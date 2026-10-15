#!/usr/bin/env python3
"""Coupled rectangular cavity, vibrating panel modes and exterior boundary radiation."""
import itertools,sys
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,apps,geometry
NAME="coupled_cabinet"
VERSION="1.0"

def compute(params,base_dir):
    f=cli.frequency_grid(params.get("frequencies"),50,1500,40)
    cabinet=params["cabinet"];dims=np.asarray(cabinet["dimensions_m"],float)
    mesh=geometry.object_mesh(dict(shape="box",dimensions_m=dims,divisions=int(params.get("surface_divisions",3))))
    centres,normals,areas=mesh["centres"],mesh["normals"],mesh["areas"]
    order=int(params.get("panel_mode_order",2));aorder=int(params.get("acoustic_mode_order",2))
    pairs=list(itertools.product(range(1,order+1),repeat=2));npanel=len(pairs)*6
    shapes=np.zeros((len(areas),npanel));m=np.zeros((npanel,npanel));stiff=np.zeros_like(m);loss=np.zeros_like(m);descriptions=[]
    plate=apps.module("plate_structure")
    for axis in range(3):
        u,v=[i for i in range(3) if i!=axis];a,b=dims[[u,v]]
        for side in (0,1):
            face=axis*2+side;name=("x_min","x_max","y_min","y_max","z_min","z_max")[face]
            material=dict(cabinet["material"],**cabinet.get("panels",{}).get(name,{}))
            t=cli.positive(material["thickness_m"],"thickness_m");rho=cli.positive(material["density_kg_m3"],"density_kg_m3")
            modes=plate.plate_modes(a,b,t,material["youngs_modulus_pa"],rho,material.get("poisson_ratio",.3),order,material.get("orthotropic"))
            selected=np.flatnonzero(normals[:,axis]*(2*side-1)>.9)
            sl=slice(face*len(pairs),(face+1)*len(pairs))
            mn=modes["indices"]
            values=np.sin(np.pi*centres[selected,u,None]*mn[None,:,0]/a)*np.sin(np.pi*centres[selected,v,None]*mn[None,:,1]/b)
            shapes[selected,sl]=values
            mass=rho*t*a*b/4
            m[sl,sl]=np.eye(len(pairs))*mass
            stiff[sl,sl]=np.diag(mass*modes["omega"]**2)
            # Rotational edge restraint: integrate mode slopes along each edge.
            for edge,krot in material.get("edge_rotational_stiffness",{}).items():
                along=np.linspace(0,1,101);weights=np.ones(101);weights[[0,-1]]=.5
                if edge in ("u_min","u_max"):
                    slope=(mn[:,0]*np.pi/a)[:,None]*np.sin(np.pi*mn[:,1,None]*along)
                    if edge=="u_max":slope*=(-1.)**mn[:,0,None]
                    measure=b/100
                elif edge in ("v_min","v_max"):
                    slope=(mn[:,1]*np.pi/b)[:,None]*np.sin(np.pi*mn[:,0,None]*along)
                    if edge=="v_max":slope*=(-1.)**mn[:,1,None]
                    measure=a/100
                else:raise cli.InputError("unknown edge restraint")
                stiff[sl,sl]+=float(krot)*measure*(slope*weights)@slope.T
            for added in material.get("added_masses",[]):
                x,y=added["position_m"]
                phi=np.sin(np.pi*mn[:,0]*x/a)*np.sin(np.pi*mn[:,1]*y/b)
                m[sl,sl]+=float(added["mass_kg"])*np.outer(phi,phi)
            loss[sl,sl]=stiff[sl,sl]*float(material.get("loss_factor",.03))
            descriptions.extend(dict(panel=name,indices=indices.tolist(),uncoupled_hz=float(hz)) for indices,hz in zip(mn,modes["frequency_hz"]))
    modal=apps.module("room_modal")
    modes=np.array(list(itertools.product(range(aorder+1),repeat=3)))
    eigen=np.sum((np.pi*modes/dims)**2,axis=1)
    phi=modal.basis(centres,modes,dims)
    coupling=phi.T@(areas[:,None]*shapes)
    source=params["source"];source_phi=modal.basis([source["position_m"]],modes,dims)[0]
    q=cli.curve_from_reference(source["volume_velocity"],base_dir,f) if "volume_velocity" in source else np.full(len(f),float(source.get("volume_velocity_m3_s",1e-4)))
    observations=np.asarray(params.get("observers_m",[[.5,1.,.5]]),float)
    pressure=[];displacements=[];surface_velocity=[];residual=[]
    vector=centres[:,None,:]-centres[None,:,:];r=np.linalg.norm(vector,axis=-1);np.fill_diagonal(r,1.)
    mu=np.einsum('ijk,ik->ij',vector,normals)/r
    external=bool(params.get("exterior_feedback",True));factor=float(params.get("coupling_scale",1.))
    for i,hz in enumerate(f):
        w=2*np.pi*hz;k=w/cli.C
        d=stiff-w*w*m+1j*loss
        if external:
            normal=-(1j*k+1/r)*np.exp(-1j*k*r)/(4*np.pi*r)*mu*areas[None,:];np.fill_diagonal(normal,-.5)
            single=np.exp(-1j*k*r)/(4*np.pi*r)*areas[None,:]
            radius=np.sqrt(areas/np.pi);np.fill_diagonal(single,(1-np.exp(-1j*k*radius))/(2j*k))
            z=(-1j*w*cli.RHO)*single@np.linalg.solve(normal,shapes)
            d+=1j*w*factor*(shapes.T*areas)@z
        acoustic=np.diag(eigen*(1+1j*float(params.get("acoustic_loss_factor",.02)))-k*k)
        matrix=np.block([[d,-factor*coupling.T],[-factor*cli.RHO*w*w*coupling,acoustic]])
        rhs=np.r_[np.zeros(npanel,complex),1j*w*cli.RHO*q[i]*source_phi]
        coefficients=np.linalg.solve(matrix,rhs);motion=coefficients[:npanel];velocity=1j*w*shapes@motion
        out,_,_,_=apps.module("exterior_bem").solve(mesh,np.array([hz]),velocity[None,:],observations)
        pressure.append(out[:,0]);displacements.append(motion);surface_velocity.append(velocity)
        residual.append(np.linalg.norm(matrix@coefficients-rhs)/max(np.linalg.norm(rhs),1e-30))
    return dict(f_hz=f,mechanical_modes_hz=np.sqrt(np.maximum(eigh(stiff,m,eigvals_only=True),0))/(2*np.pi),panel_modes=descriptions,panel_displacement_m=np.array(displacements),
                surface_velocity_m_s=np.array(surface_velocity),surface=mesh,exterior_pressure_pa=np.array(pressure).T,
                acoustic_rigid_modes_hz=cli.C*np.sqrt(eigen)/(2*np.pi),coupling_matrix=coupling,
                relative_residual=residual,validity=dict(model="Thin rectangular sine-panel modes with rotational springs/added masses, cosine cavity modes, and constant-panel exterior collocation. Surface and both modal orders are independent convergence variables. Input source is prescribed volume velocity."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Acoustic pressure loads the panels; panel acceleration drives the cavity; exterior acoustic load can feed back into panel motion. Results carry no audibility or construction verdict."]))
