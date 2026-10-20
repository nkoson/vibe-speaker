#!/usr/bin/env python3
"""Distributed acoustic two-port network with electrodynamic drivers and radiating outlets."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,acoustics
NAME="distributed_loading"
VERSION="1.0"

def compute(params,base_dir):
    f=cli.frequency_grid(params.get("frequencies"),10,4000,600);s=2j*np.pi*f
    node_names=params["nodes"];indices={name:i for i,name in enumerate(node_names)};n=len(indices)
    if n!=len(node_names) or n<1:raise cli.InputError("acoustic nodes need unique names")
    matrix=np.zeros((len(f),n,n),complex);rhs=np.zeros((len(f),n),complex)
    for duct in params.get("ducts",[]):
        a,b=[indices[v] for v in duct["nodes"]]
        length=cli.positive(duct["length_m"],"duct.length_m")
        area=cli.positive(duct["area_m2"],"duct.area_m2")
        c=cli.positive(duct.get("speed_m_s",cli.C),"duct.speed_m_s")
        alpha=cli.positive(duct.get("attenuation_np_m",.001),"duct.attenuation_np_m",zero=True)
        gamma=alpha+s/c;zc=cli.RHO*c/area
        sh=np.sinh(gamma*length);diag=np.cosh(gamma*length)/(zc*sh);off=-1/(zc*sh)
        matrix[:,a,a]+=diag;matrix[:,b,b]+=diag;matrix[:,a,b]+=off;matrix[:,b,a]+=off
    for chamber in params.get("chambers",[]):
        a=indices[chamber["node"]];volume=cli.positive(chamber["volume_l"],"chamber.volume_l")*.001
        matrix[:,a,a]+=s*volume/(cli.RHO*cli.C**2)
        if chamber.get("leak_resistance_pa_s_m3"):
            matrix[:,a,a]+=1/cli.positive(chamber["leak_resistance_pa_s_m3"],"chamber.leak_resistance_pa_s_m3")
    outlets=[]
    for outlet in params.get("outlets",[]):
        a=indices[outlet["node"]];radius=cli.positive(outlet["radius_m"],"outlet.radius_m");area=np.pi*radius**2
        z=cli.RHO*cli.C/area*acoustics.piston_radiation_impedance(f,radius)
        z+=s*cli.RHO*float(outlet.get("end_correction_m",0))/area+float(outlet.get("resistance_pa_s_m3",0))
        matrix[:,a,a]+=1/z;outlets.append((outlet,a,z))
    drivers=[]
    for driver in params["drivers"]:
        e=acoustics.driver_elements(driver["ts"]);voltage=float(driver.get("voltage_rms",1.))
        ze=acoustics.blocked_impedance(driver["ts"],f)+float(driver.get("series_resistance_ohm",0))
        zm=acoustics.mechanical_impedance(driver["ts"],f,e)
        ya=e["sd"]**2/(zm+e["bl"]**2/ze);q0=e["sd"]*e["bl"]*voltage/(ze*zm+e["bl"]**2)
        incidence=np.zeros(n)
        for key,sign in (("front_node",1),("rear_node",-1)):
            if driver.get(key) is not None:incidence[indices[driver[key]]]+=sign
        matrix+=ya[:,None,None]*np.outer(incidence,incidence);rhs+=q0[:,None]*incidence
        drivers.append((driver,e,ze,zm,incidence,ya,q0))
    try:p=np.linalg.solve(matrix,rhs[...,None])[...,0]
    except np.linalg.LinAlgError as exc:raise cli.InputError("acoustic network has a singular frequency/domain") from exc
    emissions=[];rows=[]
    for driver,e,ze,zm,b,ya,q0 in drivers:
        q=q0-ya*(p@b);v=q/e["sd"];current=(float(driver.get("voltage_rms",1.))-e["bl"]*v)/ze
        voltage=float(driver.get("voltage_rms",1.))
        rows.append(dict(id=driver["id"],velocity_m_s=v,current_a=current,z_ohm=voltage/current,
                         excursion_peak_mm=np.sqrt(2)*abs(v/s)*1000,volume_velocity_m3_s=q))
        if driver.get("front_node") is None:emissions.append(dict(id=driver["id"],position_m=driver.get("position_m",[0,0,0]),volume_velocity_m3_s=q))
    for outlet,a,z in outlets:emissions.append(dict(id=outlet["id"],position_m=outlet.get("position_m",[0,0,0]),volume_velocity_m3_s=p[:,a]/z))
    receivers=np.asarray(params.get("observers_m",[[0,1,0]]),float)
    total=np.zeros((len(receivers),len(f)),complex)
    for emission in emissions:
        radius=np.linalg.norm(receivers-np.asarray(emission["position_m"]),axis=1)
        if np.any(radius<=0):raise cli.InputError("observer coincides with an outlet")
        emission["pressure_at_1m_pa"]=s*cli.RHO*emission["volume_velocity_m3_s"]/(2*np.pi)
        total+=emission["pressure_at_1m_pa"][None,:]*np.exp(-s[None,:]*radius[:,None]/cli.C)/radius[:,None]
    return dict(f_hz=f,node_pressure_pa=p,drivers=rows,emissions=emissions,observer_pressure_pa=total,
                relative_residual=np.max(abs((matrix@p[...,None])[...,0]-rhs),axis=1)/np.maximum(np.max(abs(rhs),axis=1),1e-30),
                validity=dict(model="Piecewise constant-area plane-wave ducts and lumped chambers/drivers. Taper/folds are segmented; porous loss and effective speed are explicit inputs. No transverse duct modes or nonlinear flow."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Acoustic/electrical loading and direct-plus-mouth output are solved together. The supplied network can describe lines, folded rear horns, vents and multiple chambers/drivers."]))
