"""Versioned metre-based assembly geometry shared by acoustic and drawing apps."""
import itertools
import numpy as np
from . import cli


def transform(record):
    angles = np.deg2rad(record.get("rotation_deg", [0, 0, 0]))
    x, y, z = angles
    rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    origin = np.asarray(record.get("origin_m", [0, 0, 0]), float)
    if origin.shape != (3,) or not np.all(np.isfinite(origin)):
        raise cli.InputError("origin_m needs three finite coordinates")
    return rz @ ry @ rx, origin


def mesh_data(vertices, triangles):
    vertices, triangles = np.asarray(vertices, float), np.asarray(triangles, int)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or triangles.ndim != 2 or triangles.shape[1] != 3:
        raise cli.InputError("mesh needs vertices Nx3 and triangles Mx3")
    if np.any(~np.isfinite(vertices)) or np.any(triangles < 0) or np.any(triangles >= len(vertices)):
        raise cli.InputError("mesh contains invalid vertices or triangle indices")
    faces = vertices[triangles]
    crosses = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])
    twice = np.linalg.norm(crosses, axis=1)
    if np.any(twice <= 1e-14):
        raise cli.InputError("mesh contains degenerate triangles")
    edges = {}
    for tri in triangles:
        for a, b in zip(tri, np.roll(tri, -1)):
            key = tuple(sorted((int(a), int(b))))
            edges.setdefault(key, []).append(1 if a < b else -1)
    boundary = sum(len(v) == 1 for v in edges.values())
    nonmanifold = sum(len(v) > 2 for v in edges.values())
    inconsistent = sum(len(v) == 2 and sum(v) != 0 for v in edges.values())
    volume = np.sum(np.einsum("ij,ij->i", faces[:, 0], np.cross(faces[:, 1], faces[:, 2]))) / 6
    return dict(vertices=vertices, triangles=triangles, centres=faces.mean(axis=1),
                normals=crosses / twice[:, None], areas=twice / 2, signed_volume_m3=float(volume),
                boundary_edges=boundary, nonmanifold_edges=nonmanifold, inconsistent_edges=inconsistent,
                max_edge_m=float(max(np.linalg.norm(faces[:, i] - faces[:, j], axis=1).max() for i, j in [(0,1),(1,2),(2,0)])))


def sphere_mesh(radius, subdivisions=2):
    vertices = [np.array(v, float) for v in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]]
    triangles = [(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]
    for _ in range(subdivisions):
        cache, refined = {}, []
        def midpoint(a,b):
            key=tuple(sorted((a,b)))
            if key not in cache:
                v=vertices[a]+vertices[b]; v/=np.linalg.norm(v)
                cache[key]=len(vertices); vertices.append(v)
            return cache[key]
        for a,b,c in triangles:
            ab,bc,ca=midpoint(a,b),midpoint(b,c),midpoint(c,a)
            refined += [(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]
        triangles=refined
    return np.array(vertices)*radius, np.array(triangles)


def box_mesh(dimensions, divisions=1):
    dims=np.asarray(dimensions,float)
    if dims.shape!=(3,) or np.any(dims<=0):
        raise cli.InputError("box dimensions_m needs three positive lengths")
    vertices, triangles, ids=[],[],{}
    def index(v):
        key=tuple(np.round(v,12))
        if key not in ids: ids[key]=len(vertices); vertices.append(v)
        return ids[key]
    for axis in range(3):
        u,v=[i for i in range(3) if i!=axis]
        for side in (0,1):
            for i,j in itertools.product(range(divisions),repeat=2):
                points=[]
                for du,dv in ((0,0),(1,0),(1,1),(0,1)):
                    p=np.zeros(3);p[axis]=side*dims[axis];p[u]=(i+du)*dims[u]/divisions;p[v]=(j+dv)*dims[v]/divisions;points.append(p)
                winding=np.cross(points[1]-points[0],points[2]-points[0])[axis]
                if winding*(2*side-1)<0: points=points[::-1]
                a,b,c,d=[index(p) for p in points];triangles.extend(((a,b,c),(a,c,d)))
    return np.array(vertices),np.array(triangles)


def object_mesh(record):
    kind=record.get("shape","box")
    if kind=="box": v,t=box_mesh(record["dimensions_m"],int(record.get("divisions",1)))
    elif kind=="sphere": v,t=sphere_mesh(float(record["radius_m"]),int(record.get("subdivisions",2)))
    elif kind=="mesh": v,t=np.asarray(record["vertices_m"],float),np.asarray(record["triangles"],int)
    elif kind=="cylinder":
        n=int(record.get("segments",32)); r=float(record["radius_m"]);h=float(record["length_m"])
        if n<3 or r<=0 or h<=0: raise cli.InputError("cylinder needs positive radius/length and >=3 segments")
        a=np.arange(n)*2*np.pi/n
        v=np.vstack((np.c_[r*np.cos(a),r*np.sin(a),np.zeros(n)],np.c_[r*np.cos(a),r*np.sin(a),np.full(n,h)],[[0,0,0],[0,0,h]]))
        t=[]
        for i in range(n):
            j=(i+1)%n;t.extend(((i,j,n+j),(i,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)))
        t=np.array(t)
    else: raise cli.InputError(f"unknown geometry shape {kind}")
    rotation,origin=transform(record)
    return mesh_data(v@rotation.T+origin,t)


def contains(record, points):
    rotation,origin=transform(record); p=(np.asarray(points)-origin)@rotation
    kind=record.get("shape","box")
    if kind=="box": return np.all((p>=0)&(p<=record["dimensions_m"]),axis=-1)
    if kind=="sphere": return np.linalg.norm(p,axis=-1)<=record["radius_m"]
    if kind=="cylinder": return (np.linalg.norm(p[...,:2],axis=-1)<=record["radius_m"])&(p[...,2]>=0)&(p[...,2]<=record["length_m"])
    # Solid-angle winding test for closed oriented triangle meshes.
    mesh=mesh_data(record["vertices_m"],record["triangles"])
    if mesh["boundary_edges"] or mesh["nonmanifold_edges"] or mesh["inconsistent_edges"]:
        raise cli.InputError("solid containment needs a closed consistently oriented mesh")
    faces=mesh["vertices"][mesh["triangles"]]; result=[]
    for chunk in np.array_split(p.reshape(-1,3),max(1,int(np.ceil(p.size/3/128)))):
        a,b,c=[faces[None,:,i,:]-chunk[:,None,:] for i in range(3)]
        la,lb,lc=[np.linalg.norm(q,axis=-1) for q in (a,b,c)]
        denominator=la*lb*lc+np.sum(a*b,axis=-1)*lc+np.sum(b*c,axis=-1)*la+np.sum(c*a,axis=-1)*lb
        angle=2*np.arctan2(np.sum(a*np.cross(b,c),axis=-1),denominator)
        result.extend(np.abs(angle.sum(axis=1))>2*np.pi)
    return np.array(result).reshape(p.shape[:-1])


def air_mask(assembly, points):
    air=[o for o in assembly["objects"] if o.get("role")=="air"]
    solids=[o for o in assembly["objects"] if o.get("role","solid")=="solid"]
    mask=np.zeros(np.asarray(points).shape[:-1],bool)
    for obj in air: mask |= contains(obj,points)
    for obj in solids: mask &= ~contains(obj,points)
    return mask


def load_assembly(spec, base_dir):
    record=cli.load_json(cli.resolve_path(spec["file"],base_dir)) if "file" in spec else spec
    if record.get("schema_version",1)!=1 or not record.get("objects"):
        raise cli.InputError("assembly needs schema_version 1 and nonempty objects")
    ids=[o["id"] for o in record["objects"]]
    if len(set(ids))!=len(ids): raise cli.InputError("assembly object IDs need to be unique")
    return record
