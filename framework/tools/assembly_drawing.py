#!/usr/bin/env python3
"""Render assembly_geometry meshes and export their shared fabrication records."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def draw(document,folder):
    r=document["results"];folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    fig=plt.figure(figsize=(10,8));ax=fig.add_subplot(projection="3d")
    colors={"air":"#5eabdb","solid":"#a78b68","porous":"#84ae75"};vertices=[]
    for index,obj in enumerate(r["objects"]):
        mesh=obj["mesh"];v=np.asarray(mesh["vertices"]);t=np.asarray(mesh["triangles"]);vertices.extend(v)
        ax.add_collection3d(Poly3DCollection(v[t],facecolor=colors.get(obj["role"],"gray"),edgecolor="0.3",linewidth=.25,alpha=.08 if obj["role"]=="air" else .45))
        ax.text2D(.02,.96-index*.04,f"{obj['id']}: {obj['role']}",transform=ax.transAxes,fontsize=8)
    v=np.array(vertices);lo=v.min(axis=0);hi=v.max(axis=0)
    ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(lo[2],hi[2]),xlabel="x (m)",ylabel="y (m)",zlabel="z (m)",title="Shared assembly geometry: blue air, brown solids, green porous treatment")
    ax.set_box_aspect(hi-lo);fig.tight_layout();fig.savefig(folder/"assembly.png",dpi=160);fig.savefig(folder/"assembly.svg");plt.close(fig)
    (folder/"fabrication.json").write_text(json.dumps(r["fabrication"],indent=2)+'\n')

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--input",required=True);parser.add_argument("--out",required=True);args=parser.parse_args()
    draw(json.loads(Path(args.input).read_text()),args.out)
