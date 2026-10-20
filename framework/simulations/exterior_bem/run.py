#!/usr/bin/env python3
"""Constant-panel exterior Helmholtz single-layer Neumann boundary collocation."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli, geometry
NAME="exterior_bem"
VERSION="1.1"

def solve(mesh,f,velocity,observers):
    centres,normals,areas=mesh["centres"],mesh["normals"],mesh["areas"]
    vector=centres[:,None,:]-centres[None,:,:];r=np.linalg.norm(vector,axis=-1)
    np.fill_diagonal(r,1.)
    mu=np.einsum('ijk,ik->ij',vector,normals)/r
    target=np.asarray(observers,float); vtarget=target[:,None,:]-centres[None,:,:]
    distances=np.linalg.norm(vtarget,axis=-1)
    if np.any(distances<1e-9):raise cli.InputError("observers are on a collocation centre")
    pressure=[];densities=[];residual=[];condition=[]
    for index,hz in enumerate(f):
        omega=2*np.pi*hz;k=omega/cli.C
        kernel=-(1j*k+1/r)*np.exp(-1j*k*r)/(4*np.pi*r)*mu*areas[None,:]
        np.fill_diagonal(kernel,-.5)
        rhs=-1j*omega*cli.RHO*velocity[index]
        sigma=np.linalg.solve(kernel,rhs)
        p=(np.exp(-1j*k*distances)/(4*np.pi*distances)*areas[None,:])@sigma
        pressure.append(p);densities.append(sigma)
        residual.append(np.linalg.norm(kernel@sigma-rhs)/max(np.linalg.norm(rhs),1e-30))
        condition.append(np.linalg.cond(kernel))
    return np.array(pressure).T,np.array(densities),residual,condition

def compute(params,base_dir):
    f=cli.frequency_grid(params.get("frequencies"),50,2000,40)
    surface=params["surface"]
    if "assembly" in surface:
        assembly=geometry.load_assembly(surface["assembly"],base_dir)
        surface=next(o for o in assembly["objects"] if o["id"]==surface["object_id"])
    mesh=geometry.object_mesh(surface)
    if mesh["boundary_edges"] or mesh["nonmanifold_edges"] or mesh["inconsistent_edges"] or mesh["signed_volume_m3"]<=0:
        raise cli.InputError("exterior surface needs a closed outward-oriented manifold")
    drive=params.get("drive",{});voltage=cli.positive(drive.get("voltage_rms",1.),"drive.voltage_rms")
    velocity=np.full((len(f),len(mesh["areas"])),complex(drive.get("normal_velocity_m_s",0.)),complex)
    patch_records=[]
    for patch in drive.get("patches",[]):
        indices=patch.get("triangles",list(range(len(mesh["areas"]))))
        if "disk" in patch:
            if "triangles" in patch:
                raise cli.InputError("a patch uses disk or triangle indices, not both")
            disk=patch["disk"];centre=np.asarray(disk["centre_m"],float);normal=np.asarray(disk["normal"],float)
            if centre.shape!=(3,) or normal.shape!=(3,) or not np.all(np.isfinite(centre)) or not np.all(np.isfinite(normal)) or np.linalg.norm(normal)==0:
                raise cli.InputError("disk needs finite centre and nonzero normal vectors")
            normal=normal/np.linalg.norm(normal)
            radius=cli.positive(disk["radius_m"],"disk.radius_m")
            delta=mesh["centres"]-centre
            axial=delta@normal
            radial=np.linalg.norm(delta-axial[:,None]*normal,axis=1)
            indices=np.flatnonzero((abs(axial)<float(disk.get("plane_tolerance_m",1e-8)))&
                                  (radial<=radius)&(mesh["normals"]@normal>.99)).tolist()
        if not indices:
            raise cli.InputError("patch selects no triangles; refine the mesh")
        area=float(np.sum(mesh["areas"][indices]))
        if "volume_velocity_m3_s" in patch or "volume_velocity" in patch:
            if "velocity" in patch or "normal_velocity_m_s" in patch:
                raise cli.InputError("patch supplies volume velocity or normal velocity, not both")
            q=cli.curve_from_reference(patch["volume_velocity"],base_dir,f) if "volume_velocity" in patch else np.full(len(f),float(patch["volume_velocity_m3_s"]))
            values=q/area
        else:
            values=cli.curve_from_reference(patch["velocity"],base_dir,f) if isinstance(patch.get("velocity"),dict) else np.full(len(f),float(patch.get("normal_velocity_m_s",0.)))
        velocity[:,indices]=values[:,None]
        patch_records.append(dict(triangles=indices,selected_area_m2=area,volume_velocity_m3_s=values*area))
    observers=params.get("observers_m")
    angular=params.get("angular_grid")
    if angular:
        radius=cli.positive(angular.get("radius_m",1.),"angular_grid.radius_m")
        h=np.deg2rad(angular["horizontal_deg"]);v=np.deg2rad(angular["vertical_deg"])
        observers=[[radius*np.cos(el)*np.sin(az),radius*np.cos(el)*np.cos(az),radius*np.sin(el)] for el in v for az in h]
    if not observers:raise cli.InputError("give observers_m or angular_grid")
    pressure,density,residual,condition=solve(mesh,f,velocity,observers)
    result=dict(f_hz=f,observers_m=observers,pressure_pa=pressure,surface_density=density,
                collocation_relative_residual=residual,condition_number=condition,drive_patches=patch_records,
                surface=mesh,source_contract=dict(phase_reference="intrinsic",baffle="included",pressure_reference_m=1.),
                validity=dict(max_element_size_m=mesh["max_edge_m"],elements_per_wavelength=cli.C/f/mesh["max_edge_m"],
                              model="constant triangle centroid quadrature with exterior normal-derivative jump; interior resonances can affect conditioning; refine geometry and frequency independently"))
    if angular:
        # Remove reference-sphere propagation, retaining source/shape phase.
        intrinsic=pressure*radius*np.exp(2j*np.pi*f*radius/cli.C)[None,:]/voltage
        hv=intrinsic.reshape(len(v),len(h),len(f))
        vi=int(np.argmin(abs(v)));hi=int(np.argmin(abs(h)));axis=hv[vi,hi]
        if np.any((abs(axis)<=1e-20)&(np.max(abs(hv),axis=(0,1))>1e-20)):
            raise cli.InputError("angular source normalization is singular at an on-axis null")
        result.update(pressure_per_volt_pa=axis, directivity=dict(kind="complex_grid",frequency_hz=f,
            horizontal_deg=angular["horizontal_deg"],vertical_deg=angular["vertical_deg"],
            real=np.real(hv/np.where(abs(axis)>1e-20,axis,1)),imag=np.imag(hv/np.where(abs(axis)>1e-20,axis,1))))
    return result

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Geometry-derived exterior pressure; linear homogeneous fluid and prescribed surface velocity. No design verdict is computed."]))
