#!/usr/bin/env python3
"""Scale a STEP part set and rebuild its named assembly from the same parts.

Optional material additions are supplied as source-unit CAD operations. Geometry
checks report quantities; the author selects printable thickness and fit changes.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np

from cad_components import make_component
from cad_drawings import place_part


def mesh_report(shape, chord_mm=.005, angle_rad=.15):
    vertices, triangles = shape.tessellate(chord_mm, angle_rad)
    vertices = np.array([v.toTuple() for v in vertices])
    vertices, remap = np.unique(np.round(vertices, 7), axis=0, return_inverse=True)
    triangles = remap[np.asarray(triangles)]
    a, b, c = [vertices[triangles[:, i]] for i in range(3)]
    degenerate = int((np.linalg.norm(np.cross(b-a, c-a), axis=1) < 1e-12).sum())
    edges = {}
    for i, triangle in enumerate(triangles):
        for u, v in zip(triangle, np.roll(triangle, -1)):
            edges.setdefault(tuple(sorted((int(u), int(v)))), []).append((i, int(u), int(v)))
    neighbors = [[] for _ in triangles]
    for uses in edges.values():
        if len(uses) == 2:
            a_id, b_id = uses[0][0], uses[1][0]
            neighbors[a_id].append(b_id)
            neighbors[b_id].append(a_id)
    seen = set()
    components = 0
    for start in range(len(triangles)):
        if start in seen:
            continue
        components += 1
        stack = [start]
        while stack:
            i = stack.pop()
            if i not in seen:
                seen.add(i)
                stack.extend(neighbors[i])
    return dict(vertices=len(vertices), triangles=len(triangles),
                degenerate_triangles=degenerate,
                open_edges=sum(len(e) == 1 for e in edges.values()),
                nonmanifold_edges=sum(len(e) > 2 for e in edges.values()),
                inconsistent_edges=sum(len(e) == 2 and e[0][1:] == e[1][1:] for e in edges.values()),
                connected_surfaces=components,
                signed_volume_mm3=float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum()/6),
                chord_mm=chord_mm, angle_rad=angle_rad)


def wall_samples(shape, samples=5, face_indices=None):
    """Exact-surface inward-normal chord samples, including locations for review.

    Samples near edges can describe taper or a fixing land rather than wall stock.
    This is a sampling diagnostic, not a global minimum-thickness certificate.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.BRepClass import BRepClass_FaceClassifier
    from OCP.BRepTools import BRepTools
    from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
    from OCP.TopAbs import TopAbs_IN, TopAbs_REVERSED
    from OCP.gp import gp_Pnt2d, gp_Dir, gp_Lin
    intersector = IntCurvesFace_ShapeIntersector()
    intersector.Load(shape.wrapped, 1e-7)
    ray_length = shape.BoundingBox().DiagonalLength*2
    records = []
    for index, face in enumerate(shape.Faces()):
        if face_indices is not None and index not in face_indices:
            continue
        surface = BRepAdaptor_Surface(face.wrapped)
        u0, u1, v0, v1 = BRepTools.UVBounds_s(face.wrapped)
        for fu in (np.arange(samples)+.5)/samples:
            for fv in (np.arange(samples)+.5)/samples:
                u, v = u0+(u1-u0)*fu, v0+(v1-v0)*fv
                if BRepClass_FaceClassifier(face.wrapped, gp_Pnt2d(u,v), 1e-7).State() != TopAbs_IN:
                    continue
                props = BRepLProp_SLProps(surface, u, v, 1, 1e-9)
                if not props.IsNormalDefined():
                    continue
                p, n = props.Value(), props.Normal()
                sign = 1 if face.wrapped.Orientation() == TopAbs_REVERSED else -1
                direction = gp_Dir(sign*n.X(), sign*n.Y(), sign*n.Z())
                intersector.Perform(gp_Lin(p, direction), 1e-6, ray_length)
                distances = [intersector.WParameter(i) for i in range(1, intersector.NbPnt()+1)
                             if intersector.WParameter(i) > 1e-6]
                if distances:
                    records.append(dict(face=index, surface=face.geomType(),
                                        position_mm=[p.X(),p.Y(),p.Z()],
                                        thickness_mm=min(distances)))
    return sorted(records, key=lambda r:r['thickness_mm'])


def bounds(shape):
    b = shape.BoundingBox()
    return [getattr(b, k) for k in ('xmin','xmax','ymin','ymax','zmin','zmax')]


def build(source_dir, manifest, output_dir, scale, patches=None, min_wall_mm=None):
    source_dir, output_dir = Path(source_dir).resolve(), Path(output_dir).resolve()
    if source_dir == output_dir or scale <= 0:
        raise ValueError('use a separate output directory and a positive scale')
    output_dir.mkdir(parents=True, exist_ok=True)
    patches = patches or {}
    parts = {p['id']:p for p in manifest['parts']}
    files = sorted(p for p in source_dir.glob('*.step') if p.stem != 'cabinet-assembly')
    if {p.stem for p in files} != set(parts):
        raise ValueError('manifest and individual STEP part IDs differ')
    assembly = cq.Assembly(name='scaled-cabinet')
    report = dict(scale=scale, units='mm', requested_minimum_wall_mm=min_wall_mm, parts=[], instances=[])
    for path in files:
        original = cq.importers.importStep(str(path)).val()
        shape = original
        if path.stem in patches:
            patch = patches[path.stem]
            if patch.get('mode') == 'replace':
                shape = make_component(patch['solid_model'])
            else:
                shape = shape.fuse(make_component(patch)).clean()
        scaled = shape.scale(scale)
        target = output_dir/path.name
        cq.exporters.export(scaled, str(target))
        reopened = cq.importers.importStep(str(target)).val()
        if not reopened.isValid() or len(reopened.Solids()) != len(original.Solids()):
            raise ValueError('invalid scaled solid: '+path.name)
        if not np.allclose(bounds(reopened), np.asarray(bounds(shape))*scale, atol=1e-6):
            raise ValueError('scaled STEP bounds mismatch: '+path.name)
        mesh = mesh_report(reopened)
        if any(mesh[k] for k in ('degenerate_triangles','open_edges','nonmanifold_edges','inconsistent_edges')):
            raise ValueError('invalid triangulation: '+path.name)
        entry = dict(id=path.stem, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                     bounds_mm=bounds(reopened), solid_count=len(reopened.Solids()), mesh=mesh,
                     material_added=path.stem in patches)
        report['parts'].append(entry)
        for index, placement in enumerate(parts[path.stem].get('placements', [])):
            pose = dict(placement, origin=(np.asarray(placement['origin'])*scale).tolist())
            placed = place_part(reopened, pose)
            assembly.add(placed, name=f'{path.stem}_{index}',
                         color=cq.Color(*parts[path.stem].get('color',[.77,.68,.52])))
            report['instances'].append(dict(part=path.stem, index=index, placement=pose))
        print(path.name, 'exported', flush=True)
    target = output_dir/'cabinet-assembly.step'
    assembly.export(str(target))
    reopened = cq.importers.importStep(str(target)).val()
    if not reopened.isValid() or len(reopened.Solids()) != len(report['instances']):
        raise ValueError('scaled assembly topology mismatch')
    report['assembly'] = dict(solid_count=len(reopened.Solids()), bounds_mm=bounds(reopened),
                             sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (output_dir/'scale-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--scale', type=float, required=True)
    parser.add_argument('--min-wall-mm', type=float)
    parser.add_argument('--patches')
    args = parser.parse_args()
    build(args.source_dir, json.loads(Path(args.manifest).read_text()), args.out, args.scale,
          json.loads(Path(args.patches).read_text()) if args.patches else None, args.min_wall_mm)
