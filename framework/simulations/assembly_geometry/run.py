#!/usr/bin/env python3
"""Shared assembly meshes, air occupancy, source transforms and fabrication records."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli, geometry
NAME="assembly_geometry"
VERSION="1.0"

def compute(params,base_dir):
    assembly=geometry.load_assembly(params.get("assembly",params),base_dir)
    rows=[]
    for obj in assembly["objects"]:
        mesh=geometry.object_mesh(obj)
        rows.append(dict(id=obj["id"],role=obj.get("role","solid"),material=obj.get("material"),
                         bounds_m=[mesh["vertices"].min(axis=0),mesh["vertices"].max(axis=0)],mesh=mesh,
                         joints=obj.get("joints",[]),treatments=obj.get("treatments",[]),machining=obj.get("machining",[])))
    lo=np.min([r["bounds_m"][0] for r in rows],axis=0); hi=np.max([r["bounds_m"][1] for r in rows],axis=0)
    volumes=[];overlaps=[]
    for h in params.get("cell_sizes_m",[.02,.01]):
        h=cli.positive(h,"cell_sizes_m")
        n=np.maximum(np.ceil((hi-lo)/h).astype(int),1)
        if np.prod(n)>2e6: raise cli.InputError("geometry grid exceeds two million cells; increase cell size")
        step=(hi-lo)/n; axes=[lo[i]+(np.arange(n[i])+.5)*step[i] for i in range(3)]
        points=np.stack(np.meshgrid(*axes,indexing="ij"),axis=-1).reshape(-1,3)
        masks=[geometry.contains(o,points) for o in assembly["objects"]]
        solids=[m for o,m in zip(assembly["objects"],masks) if o.get("role","solid")=="solid"]
        union=np.any(solids,axis=0) if solids else np.zeros(len(points),bool)
        volumes.append(dict(cell_size_m=h,actual_cell_dimensions_m=step,cells=len(points),
                            solid_union_m3=float(union.sum()*np.prod(step)),air_volume_m3=float(geometry.air_mask(assembly,points).sum()*np.prod(step))))
        if h==params.get("cell_sizes_m",[.02,.01])[-1]:
            for i in range(len(rows)):
                for j in range(i+1,len(rows)):
                    if rows[i]["role"]==rows[j]["role"]=="solid":
                        overlaps.append(dict(objects=[rows[i]["id"],rows[j]["id"]],intersection_m3=float(np.sum(masks[i]&masks[j])*np.prod(step))))
    emitters=[]
    for source in assembly.get("sources",[]):
        obj=next(o for o in assembly["objects"] if o["id"]==source["object_id"])
        rotation,origin=geometry.transform(obj)
        emitters.append(dict(source,position_m=rotation@np.asarray(source["local_position_m"])+origin,
                             normal=rotation@np.asarray(source.get("local_normal",[0,1,0]))))
    return dict(schema_version=1,objects=rows,volume_refinement=volumes,solid_intersections=overlaps,sources=emitters,
                fabrication=[dict(id=o["id"],dimensions_m=o.get("dimensions_m"),machining=o.get("machining",[]),joints=o.get("joints",[])) for o in assembly["objects"] if o.get("fabricate")],
                validity=dict(volume_basis="voxel-centre integration; compare cell-size sequence",units="metres"))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Intersections and volumes are numerical results; the caller interprets intended joints and clearances."]))
