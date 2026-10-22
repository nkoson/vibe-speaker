"""Declarative purchased-part solids and BRep-derived drawing projections.

Geometry only: the author supplies sourced dimensions, profiles and interfaces.
Local XY is the front face; negative Z is behind that face, as for cabinet parts.
"""
import math


def primitive(spec):
    import cadquery as cq
    kind = spec['kind']
    if kind == 'revolve':
        # XZ workplane: tuples are radius and axial Z; revolve around global Z.
        shape = cq.Workplane('XZ').polyline(spec['profile']).close().revolve(
            360, (0, 0), (0, 1)).val()
    elif kind == 'cylinder':
        shape = cq.Solid.makeCylinder(spec['radius'], spec['length'],
            cq.Vector(*spec.get('origin', [0, 0, 0])),
            cq.Vector(*spec.get('direction', [0, 0, -1])))
    elif kind == 'box':
        shape = cq.Workplane('XY').box(*spec['size'], centered=False)
        if spec.get('corner_radius'):
            shape = shape.edges('|Z').fillet(spec['corner_radius'])
        shape = shape.translate(tuple(spec.get('origin', [0, 0, 0]))).val()
    elif kind == 'extrude':
        shape = cq.Workplane('XY', origin=(0, 0, spec.get('z', 0))).polyline(
            spec['points']).close().extrude(spec['length']).val()
    elif kind == 'slot':
        shape = cq.Workplane('XY', origin=tuple(spec['origin'])).slot2D(
            spec['length'], spec['width'], spec.get('angle_deg', 0)).extrude(
            spec['depth']).val()
    elif kind == 'loft':
        wires = []
        for section in spec['sections']:
            wp = cq.Workplane('XY', origin=(0, 0, section['z']))
            if 'radius' in section:
                wire = wp.circle(section['radius']).val()
            elif 'spline_points' in section:
                wire = wp.spline(section['spline_points'], periodic=True).wire().val()
            else:
                wire = wp.polyline(section['points']).close().val()
            wires.append(wire)
        shape = cq.Solid.makeLoft(wires, ruled=spec.get('ruled', False))
    else:
        raise ValueError('unknown solid primitive: ' + kind)
    if 'rotate' in spec:
        r = spec['rotate']
        shape = shape.rotate(tuple(r['start']), tuple(r['end']), r['degrees'])
    if 'translate' in spec:
        shape = shape.translate(tuple(spec['translate']))
    return shape


def make_component(spec):
    shape = None
    for operation in spec['operations']:
        item = primitive(operation)
        action = operation.get('operation', 'union')
        if shape is None:
            if action != 'union':
                raise ValueError('first solid operation must be union')
            shape = item
        elif action == 'union':
            shape = shape.fuse(item)
        elif action == 'cut':
            shape = shape.cut(item)
        elif action == 'intersect':
            shape = shape.intersect(item)
        else:
            raise ValueError('unknown solid operation: ' + action)
    if shape is None or not shape.isValid() or shape.Volume() <= 0:
        raise ValueError('invalid component solid')
    shape = shape.clean()
    if 'expected_solids' in spec and len(shape.Solids()) != spec['expected_solids']:
        raise ValueError('component solid count differs from expected_solids')
    return shape


def projection_entities(shapes, spec):
    """Orthographic hidden-line removal with explicitly defined view axes."""
    import cadquery as cq
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
    from OCP.BRepLib import BRepLib
    algorithm = HLRBRep_Algo()
    for name in spec['parts']:
        algorithm.Add(shapes[name].wrapped)
    axes = gp_Ax2(gp_Pnt(*spec.get('origin', [0, 0, 0])),
                  gp_Dir(*spec['normal']), gp_Dir(*spec['x_dir']))
    algorithm.Projector(HLRAlgo_Projector(axes))
    algorithm.Update()
    algorithm.Hide()
    result = HLRBRep_HLRToShape(algorithm)
    groups = [('OUTLINE', result.VCompound()),
              ('OUTLINE', result.Rg1LineVCompound()),
              ('OUTLINE', result.OutLineVCompound())]
    if spec.get('hidden', False):
        groups += [('HIDDEN', result.HCompound()), ('HIDDEN', result.OutLineHCompound())]
    entities = []
    for layer, compound in groups:
        if compound.IsNull():
            continue
        BRepLib.BuildCurves3d_s(compound, 1e-7)
        for edge in cq.Shape(compound).Edges():
            if edge.Length() < 1e-6:
                continue
            if edge.geomType() == 'LINE':
                points = [edge.startPoint(), edge.endPoint()]
            else:
                points, _ = edge.sample(spec.get('deflection_mm', .05))
                # Deflection samples omit the final parameter. Include it so that
                # full circles close and adjoining arcs meet in PDF and DXF.
                points.append(edge.endPoint())
            if len(points) > 1:
                entities.append(dict(kind='polyline', points=[[p.x, p.y] for p in points],
                                     closed=False, layer=layer))
    return entities


def interface_offsets(a, b):
    """Report paired hole centre differences; caller defines the pairing/axes."""
    if len(a) != len(b):
        raise ValueError('paired mounting patterns must have equal hole counts')
    return [dict(a=list(x), b=list(y), offset_mm=math.dist(x, y)) for x, y in zip(a, b)]
