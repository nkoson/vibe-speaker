#!/usr/bin/env python3
"""Driven rectangular-room Galerkin modes with complex wall impedance."""
import itertools,sys
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,acoustics
NAME="room_modal"
VERSION = "1.1"
WALLS=("x_min","x_max","y_min","y_max","z_min","z_max")

def basis(points,modes,dimensions):
    points=np.atleast_2d(points)
    normalization=np.sqrt(2.**np.count_nonzero(modes,axis=1)/np.prod(dimensions))
    return np.prod(np.cos(np.pi*points[:,None,:]*modes[None,:,:]/dimensions),axis=-1)*normalization

def compute(params,base_dir):
    f=cli.frequency_grid(params.get("frequencies"),20,300,281,"linear")
    dims=np.asarray(params["room"]["dimensions_m"],float)
    if dims.shape!=(3,) or np.any(dims<=0):raise cli.InputError("room dimensions need positive xyz lengths")
    order=int(params.get("mode_order",4))
    if not 1<=order<=10:raise cli.InputError("mode_order outside computational range 1..10")
    modes=np.array(list(itertools.product(range(order+1),repeat=3)))
    eigen=np.sum((np.pi*modes/dims)**2,axis=1); modal_hz=cli.C*np.sqrt(eigen)/(2*np.pi)
    receptors=np.asarray(params["receivers_m"],float);sources=params["sources"]
    positions=np.asarray([s["position_m"] for s in sources],float)
    if np.any(receptors<0) or np.any(receptors>dims) or np.any(positions<0) or np.any(positions>dims):raise cli.InputError("sources and receivers lie outside room")
    source_basis=basis(positions,modes,dims);receiver_basis=basis(receptors,modes,dims)
    for si,source in enumerate(sources):
        radius=source.get("radius_m")
        if radius:
            normal=np.asarray(source.get("normal",[0,1,0]),float);normal/=np.linalg.norm(normal)
            tangent=np.cross(normal,[1,0,0] if abs(normal[0])<.8 else [0,1,0]);tangent/=np.linalg.norm(tangent)
            bitangent=np.cross(normal,tangent);j=np.arange(int(source.get("aperture_samples",64)))
            r=float(radius)*np.sqrt((j+.5)/len(j));angle=j*np.pi*(3-np.sqrt(5))
            points=positions[si]+r[:,None]*(np.cos(angle)[:,None]*tangent+np.sin(angle)[:,None]*bitangent)
            if np.any(points<0) or np.any(points>dims):raise cli.InputError("source aperture crosses the room boundary")
            source_basis[si]=basis(points,modes,dims).mean(axis=0)
    q=np.array([cli.curve_from_reference(s["volume_velocity"],base_dir,f) if "volume_velocity" in s else np.full(len(f),float(s.get("volume_velocity_m3_s",1e-4)),complex) for s in sources])
    wallmat=[];admittance=[]
    nodes,weights=leggauss(order+2)
    walls=params["room"].get("walls",{})
    for axis in range(3):
        other=[d for d in range(3) if d!=axis]
        for side in (0,1):
            pts=[];w=[]
            for i,j in itertools.product(range(len(nodes)),repeat=2):
                p=np.zeros(3);p[axis]=side*dims[axis]
                p[other]=(np.array([nodes[i],nodes[j]])+1)*dims[other]/2
                pts.append(p);w.append(weights[i]*weights[j]*np.prod(dims[other])/4)
            phi=basis(pts,modes,dims);wallmat.append(phi.T@(np.array(w)[:,None]*phi))
            spec=walls.get(WALLS[axis*2+side],{"rigid":True})
            if spec.get("rigid"):y=np.zeros(len(f),complex)
            elif "impedance" in spec:y=1/cli.curve_from_reference(spec["impedance"],base_dir,f)
            else:
                z=complex(spec["resistance_pa_s_m"],spec.get("reactance_pa_s_m",0.))
                if z.real<0 or abs(z)==0:raise cli.InputError("wall impedance needs nonnegative resistance and nonzero magnitude")
                y=np.full(len(f),1/z)
            admittance.append(y)
    loss=float(params.get("modal_loss_factor",0.))
    pressure=[];residual=[];amplitudes=[];motor_states=[]
    for i,hz in enumerate(f):
        omega=2*np.pi*hz;k=omega/cli.C
        a=np.diag(eigen*(1+1j*loss)-k*k).astype(complex)
        for b,y in zip(wallmat,admittance):a+=1j*omega*cli.RHO*y[i]*b
        qdrive=q[:,i].copy();source_y=np.zeros(len(sources),complex);motors={}
        for si,source in enumerate(sources):
            if source.get("driver"):
                if not source.get("radius_m"):raise cli.InputError("room-loaded driver needs a finite radius_m aperture")
                e=acoustics.driver_elements(source["driver"]["ts"])
                ze=acoustics.blocked_impedance(source["driver"]["ts"],hz)
                zm=acoustics.mechanical_impedance(source["driver"]["ts"],hz,e)
                if source.get("sealed_volume_l"):
                    zm+=e["sd"]**2*cli.RHO*cli.C**2/(1j*omega*float(source["sealed_volume_l"])*.001)
                voltage=float(source.get("voltage_rms",1))
                qdrive[si]=e["sd"]*e["bl"]*voltage/(ze*zm+e["bl"]**2)
                source_y[si]=e["sd"]**2/(zm+e["bl"]**2/ze)
                motors[si]=(e,ze,voltage)
        a+=1j*omega*cli.RHO*(source_basis.T*source_y)@source_basis
        rhs=1j*omega*cli.RHO*(source_basis.T@qdrive)
        try:coeff=np.linalg.solve(a,rhs)
        except np.linalg.LinAlgError as exc:raise cli.InputError("lossless modal pole sampled exactly; supply physical loss or a different frequency") from exc
        pressure.append(receiver_basis@coeff);amplitudes.append(coeff)
        source_pressure=source_basis@coeff;actual_q=qdrive-source_y*source_pressure
        state=[]
        for si,(e,ze,voltage) in motors.items():
            velocity=actual_q[si]/e["sd"];current=(voltage-e["bl"]*velocity)/ze
            state.append(dict(source=si,volume_velocity_m3_s=actual_q[si],current_a=current,
                              excursion_peak_mm=np.sqrt(2)*abs(velocity)/omega*1000,input_impedance_ohm=voltage/current))
        motor_states.append(state)
        residual.append(np.linalg.norm(a@coeff-rhs)/max(np.linalg.norm(rhs),1e-30))
    return dict(f_hz=f,pressure_pa=np.array(pressure).T,
                receivers=[dict(position_m=point,pressure_pa=np.array(pressure)[:,i]) for i,point in enumerate(receptors)],modal_amplitudes=np.array(amplitudes),
                wall_admittance_m_pa_s=dict(zip(WALLS,admittance)),motor_states=motor_states,rigid_basis_modes_hz=modal_hz,mode_indices=modes,relative_residual=residual,
                validity=dict(basis_order=order,mode_count=len(modes),basis_max_frequency_hz=float(modal_hz.max()),
                              note="Cosine Galerkin basis with full wall admittance matrices, no diagonal damping approximation. Compare increasing orders; finite-aperture motor records include room-pressure feedback; other sources are prescribed volume velocity."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Physical receiver pressure in a driven linear room; supplied wall impedance and source volume velocity determine the result."]))
