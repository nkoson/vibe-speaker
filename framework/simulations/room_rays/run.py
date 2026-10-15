#!/usr/bin/env python3
"""Seeded specular/diffuse energy transport in closed triangulated rooms."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,geometry,acoustics
NAME="room_rays"
VERSION="1.0"

def intersections(origin,direction,faces):
    e1=faces[:,1]-faces[:,0];e2=faces[:,2]-faces[:,0]
    h=np.cross(direction,e2);det=np.sum(e1*h,axis=1)
    inv=np.divide(1.,det,out=np.zeros_like(det),where=abs(det)>1e-12)
    s=origin-faces[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1)
    v=inv*(q@direction);t=inv*np.sum(e2*q,axis=1)
    valid=(abs(det)>1e-12)&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-7)
    values=np.where(valid,t,np.inf);index=int(np.argmin(values))
    return index,float(values[index])

def compute(params,base_dir):
    f=cli.frequency_grid(params.get("frequencies",{"values_hz":[125,500,2000]}))
    mesh=geometry.object_mesh(params["room_surface"])
    if mesh["boundary_edges"] or mesh["nonmanifold_edges"] or mesh["inconsistent_edges"] or mesh["signed_volume_m3"]<=0:raise cli.InputError("ray room needs a closed outward-oriented triangle mesh")
    faces=mesh["vertices"][mesh["triangles"]];normals=mesh["normals"]
    origin=np.asarray(params["source_position_m"],float);receivers=np.asarray(params["receivers_m"],float)
    if not np.all(geometry.contains(params["room_surface"],np.vstack([origin,receivers]))):raise cli.InputError("sources and receivers need to be inside the room surface")
    radius=cli.positive(params.get("receiver_radius_m",.2),"receiver_radius_m")
    count=int(params.get("rays",2000));bounces=int(params.get("max_bounces",20));seed=int(params.get("seed",0))
    dt=cli.positive(params.get("time_step_ms",2.),"time_step_ms")/1000;duration=cli.positive(params.get("duration_ms",500.),"duration_ms")/1000
    start=float(params.get("min_arrival_ms",0))/1000
    bins=int(np.ceil(duration/dt));energy=np.zeros((len(receivers),len(f),bins))
    if count<1 or bounces<0:raise cli.InputError("positive ray count and nonnegative bounce count needed")
    p=cli.curve_from_reference(params["source_pressure"],base_dir,f) if "source_pressure" in params else np.full(len(f),float(params.get("pressure_at_1m_pa",1.)))
    absorption=np.full((len(faces),len(f)),float(params.get("energy_absorption",.2)))
    scatter=np.full(len(faces),float(params.get("scattering",.1)))
    for material in params.get("surface_materials",[]):
        ids=material["triangles"];absorption[ids]=np.broadcast_to(material["energy_absorption"],(len(ids),len(f)))
        scatter[ids]=float(material.get("scattering",.1))
    if np.any((absorption<0)|(absorption>1)) or np.any((scatter<0)|(scatter>1)):raise cli.InputError("energy absorption/scattering outside [0,1]")
    forward=np.asarray(params.get("source_normal",[0,1,0]),float)
    if forward.shape!=(3,) or np.linalg.norm(forward)==0:raise cli.InputError("source_normal needs a nonzero 3D vector")
    forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1] if abs(forward[2])<.99 else [0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    def pattern(vector):
        vector=np.atleast_2d(vector);axial=vector@forward;lateral=vector@right;vertical=vector@up
        h=np.arctan2(lateral,axial);v=np.arctan2(vertical,np.hypot(lateral,axial))
        return acoustics.directivity(params.get("directivity",{"kind":"omni"}),f[None,:],h[:,None],v[:,None])
    rng=np.random.default_rng(seed);escaped=0;absorbed=np.zeros(len(f));remaining=np.zeros(len(f));launched=np.zeros(len(f))
    for ray in range(count):
        z=1-2*(ray+.5)/count;angle=ray*np.pi*(3-np.sqrt(5));direction=np.array([np.sqrt(1-z*z)*np.cos(angle),np.sqrt(1-z*z)*np.sin(angle),z])
        power=4*np.pi*abs(p)**2*abs(pattern(direction)[0])**2/(cli.RHO*cli.C*count);launched+=power;position=origin.copy();length=0.
        for bounce in range(bounces+1):
            face,distance=intersections(position,direction,faces)
            if not np.isfinite(distance):escaped+=1;break
            if bounce:
                rel=receivers-position;along=rel@direction;perp=np.sum(rel*rel,axis=1)-along*along
                for ri in np.flatnonzero((along>0)&(along<distance)&(perp<radius*radius)):
                    time=(length+along[ri])/cli.C
                    if start<=time<duration:
                        energy[ri,:,int(time/dt)]+=power/(np.pi*radius*radius)*cli.RHO*cli.C
            length+=distance
            if length/cli.C>=duration:break
            position+=distance*direction
            absorbed+=power*absorption[face];power*=1-absorption[face]
            normal=normals[face]
            if rng.random()<scatter[face]:
                inward=-normal;tangent=np.cross(inward,[1,0,0] if abs(inward[0])<.8 else [0,1,0]);tangent/=np.linalg.norm(tangent)
                bitangent=np.cross(inward,tangent);u,v=rng.random(2);phi=2*np.pi*v
                direction=np.sqrt(u)*(np.cos(phi)*tangent+np.sin(phi)*bitangent)+np.sqrt(1-u)*inward
            else:direction-=2*np.dot(direction,normal)*normal
            position+=direction*1e-7
        remaining+=power
    distance=np.linalg.norm(receivers-origin,axis=1)
    if np.any(distance<=0):raise cli.InputError("receiver coincides with source")
    direct=pattern(receivers-origin)*p[None,:]*np.exp(-2j*np.pi*f[None,:]*distance[:,None]/cli.C)/distance[:,None]
    return dict(f_hz=f,receivers=[dict(position_m=point,reflected_mean_square_pa2=energy[i].sum(axis=-1),direct_pressure_pa=direct[i]) for i,point in enumerate(receivers)],time_s=(np.arange(bins)+.5)*dt,reflected_pressure_squared_bins=energy,
                reflected_mean_square_pa2=energy.sum(axis=-1),direct_pressure_pa=direct,
                transport=dict(rays=count,seed=seed,escaped_rays=escaped,absorbed_power_w=absorbed,remaining_power_w=remaining,launched_power_w=launched),
                validity=dict(min_arrival_ms=start*1000,receiver_radius_m=radius,
                              model="Energy estimator for spherical receiver cross sections, declared directional source and finite specular/diffuse paths. Reflections are incoherent; compare ray count, seed, receiver radius and bounce/time limits. No LF wave interference."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["General triangle-room reflected energy. Direct sound is returned separately so an explicitly time-partitioned image/ray combination can avoid duplicate paths."]))
