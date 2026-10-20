"""Distributed edge dipoles on a convex planar polygon (exp(+jwt))."""
import numpy as np
from . import cli
from scipy.special import j1


def prepare(vertices_mm, source_mm, subdivisions):
    vertices=np.asarray(vertices_mm,float)*.001
    source=np.asarray(source_mm,float)*.001
    if vertices.ndim!=2 or vertices.shape[1]!=2 or len(vertices)<3 or source.shape!=(2,) or not np.all(np.isfinite(vertices)):
        raise cli.InputError("baffle needs finite x,z polygon vertices and source coordinates")
    edges=np.roll(vertices,-1,axis=0)-vertices
    cross=lambda a,b:a[...,0]*b[...,1]-a[...,1]*b[...,0]
    turn=cross(edges,np.roll(edges,-1,axis=0))
    nonzero=turn[abs(turn)>1e-14]
    if len(nonzero)==0 or np.any(nonzero*nonzero[0]<0) or np.any(np.linalg.norm(edges,axis=1)<=0):
        raise cli.InputError("angular baffle requires a nondegenerate convex polygon")
    if np.any(cross(edges,source-vertices)*nonzero[0]<=0):
        raise cli.InputError("source must be strictly inside the convex baffle")
    count=int(subdivisions)
    if count<1:raise cli.InputError("edge subdivisions must be positive")
    points=[];weights=[]
    for a,b in zip(vertices,np.roll(vertices,-1,axis=0)):
        q=a+np.linspace(0,1,count+1)[:,None]*(b-a)
        left=q[:-1]-source;right=q[1:]-source
        weights.extend(abs(np.arctan2(cross(left,right),np.sum(left*right,axis=1))))
        points.extend((left+right)/2)
    weights=np.asarray(weights)/(2*np.pi)
    if not np.isclose(weights.sum(),1,atol=1e-8):
        raise cli.InputError("polygon does not enclose source exactly once")
    return np.asarray(points),weights


def piston(ka):
    return np.divide(2*j1(ka),ka,out=np.ones_like(ka),where=abs(ka)>1e-12)


def evaluate(model,f,h,v):
    f,h,v=np.broadcast_arrays(f,h,v)
    points,weights=prepare(model["vertices_mm"],model["source_mm"],model.get("subdivisions",24))
    x=np.sin(h)*np.cos(v);z=np.sin(v);mu=np.cos(h)*np.cos(v)
    k=2*np.pi*f/cli.C
    radius=float(model.get("radius_mm",0))*.001
    width=float(model.get("radiator_width_mm",0))*.001
    height=float(model.get("radiator_height_mm",0))*.001
    direct=piston(k*radius*np.sqrt(np.maximum(0,1-mu**2)))
    if width or height:
        direct=np.sinc(k*width*x/(2*np.pi))*np.sinc(k*height*z/(2*np.pi))
    distance=model.get("observer_distance_m")
    edge_sum=np.zeros(f.shape,complex)
    for point,weight in zip(points,weights):
        length=np.linalg.norm(point)
        projection=x*point[0]+z*point[1]
        if distance is None:
            extra=length-projection;spread=1
        else:
            r=cli.positive(distance,"observer_distance_m")
            rp=np.sqrt(r*r+length*length-2*r*projection)
            if np.any(rp<=0):raise cli.InputError("observer lies on baffle edge")
            extra=length+rp-r;spread=r/rp
        edge_pattern=piston(k*radius)
        if width or height:
            edge_pattern=np.sinc(k*width*point[0]/length/(2*np.pi))*np.sinc(k*height*point[1]/length/(2*np.pi))
        edge_sum+=weight*spread*edge_pattern*np.exp(-1j*k*extra)
    edge_radius=float(model.get("edge_radius_mm",0))*.001
    if edge_radius:
        edge_sum/=1+1j*f/(cli.C/(8*edge_radius))
    if model.get("open_baffle"):
        return mu*(direct-edge_sum)
    return (1+mu)*direct/2-mu*edge_sum/2
