#!/usr/bin/env python3
"""Lumped acoustic chamber networks with vents, passive radiators and individual motors."""
import copy
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics
NAME="enclosure_network"
VERSION="1.0"


def preset(params):
    """Expand named geometry into explicit node incidences; no alignment selection."""
    p=copy.deepcopy(params)
    kind=p.pop("preset",None)
    if kind is None:
        return p
    d=dict(p["driver"],id="driver",front_node=None,rear_node="rear")
    d.setdefault("voltage_rms",p.get("voltage_rms",2.83))
    if kind=="infinite_baffle":
        d["rear_node"]=None
        return dict(p,chambers=[],drivers=[d])
    rear=dict(p["rear"],id="rear")
    chambers=[rear];vents=[];radiators=[]
    if kind in ("vented","double_tuned_reflex"):
        port=dict(p["port"],id="vent",nodes=["rear",None])
        if kind=="double_tuned_reflex":
            chambers.append(dict(p["front"],id="front"))
            port["nodes"]=["rear","front"]
            vents.append(dict(p["outer_port"],id="outer_vent",nodes=["front",None]))
        vents.append(port)
    elif kind in ("bandpass","bandpass_pr"):
        d["front_node"]="front"
        chambers.append(dict(p["front"],id="front"))
        if kind=="bandpass":
            vents.append(dict(p["port"],id="front_vent",nodes=["front",None]))
        else:
            radiators.append(dict(p["radiator"],id="front_radiator",nodes=["front",None]))
        if p.get("rear_port"):
            vents.append(dict(p["rear_port"],id="rear_vent",nodes=["rear",None]))
        if p.get("coupling_port"):
            vents.append(dict(p["coupling_port"],id="coupling",nodes=["rear","front"]))
    elif kind=="passive_radiator":
        radiators.append(dict(p["radiator"],id="radiator",nodes=["rear",None]))
    elif kind!="sealed":
        raise cli.InputError("unknown enclosure preset")
    return dict(p,chambers=chambers,drivers=[d],vents=vents,radiators=radiators)


def compute(params,base_dir):
    p=preset(params)
    f=cli.frequency_grid(p.get("frequencies"),10,2000,400);s=2j*np.pi*f
    chambers=p.get("chambers",[]);names=[r["id"] for r in chambers]
    if len(set(names))!=len(names):
        raise cli.InputError("chamber identifiers must be unique")
    n=len(names);indices={name:i for i,name in enumerate(names)}
    matrix=np.zeros((len(f),n,n),complex);rhs=np.zeros((len(f),n),complex)
    def incidence(nodes):
        if len(nodes)!=2 or nodes[0]==nodes[1]:
            raise cli.InputError("branch needs two different chamber/ambient nodes")
        b=np.zeros(n)
        for node,sign in zip(nodes,[1,-1]):
            if node is not None:
                if node not in indices:raise cli.InputError(f"unknown acoustic node {node}")
                b[indices[node]]+=sign
        return b
    for c in chambers:
        i=indices[c["id"]]
        cab=cli.positive(c["volume_l"],"chamber.volume_l")*.001/(cli.RHO*cli.C**2)
        za=1/(s*cab)
        if c.get("qa") is not None:
            ref=cli.positive(c.get("loss_reference_hz"),"chamber.loss_reference_hz")
            za+=1/(2*np.pi*ref*cab*cli.positive(c["qa"],"chamber.qa"))
        matrix[:,i,i]+=1/za
        if c.get("leak_resistance_pa_s_m3") is not None:
            matrix[:,i,i]+=1/cli.positive(c["leak_resistance_pa_s_m3"],"leak resistance")
        if c.get("ql") is not None:
            ref=cli.positive(c.get("loss_reference_hz"),"chamber.loss_reference_hz")
            matrix[:,i,i]+=2*np.pi*ref*cab/cli.positive(c["ql"],"chamber.ql")
    branches=[]
    for kind,records in (("vent",p.get("vents",[])),("radiator",p.get("radiators",[]))):
        for record in records:
            b=incidence(record["nodes"])
            count=cli.positive(record.get("count",1),"branch.count")
            if int(count)!=count:raise cli.InputError("branch.count must be an integer")
            if kind=="vent":
                area=cli.positive(record["area_m2"],"vent.area_m2")
                length=cli.positive(record["effective_length_m"],"vent.effective_length_m")
                mass=cli.RHO*length/area
                resistance=cli.positive(record.get("resistance_pa_s_m3",0),"vent resistance",zero=True)
                z=(s*mass+resistance)/count
                data=dict(area_m2=area,plane_wave_frequency_scale_hz=cli.C/(4*length))
            else:
                area=cli.positive(record["sd_cm2"],"radiator.sd_cm2")*1e-4
                mass=cli.positive(record["mmp_g"],"radiator.mmp_g")*.001
                mass+=cli.positive(record.get("added_mass_g",0),"radiator.added_mass_g",zero=True)*.001
                compliance=cli.positive(record["cmp_m_per_n"],"radiator.cmp_m_per_n")
                resistance=cli.positive(record.get("rmp_ns_m",0),"radiator.rmp_ns_m",zero=True)
                z=(s*mass+resistance+1/(s*compliance))/(area**2*count)
                data=dict(area_m2=area)
            matrix+=np.outer(b,b)[None,:,:]/z[:,None,None]
            branches.append((record,kind,b,z,count,data))
    motors=[]
    for d in p["drivers"]:
        e=acoustics.driver_elements(d["ts"])
        ze=acoustics.blocked_impedance(d["ts"],f)+cli.positive(d.get("series_resistance_ohm",0),"series resistance",zero=True)
        zm=acoustics.mechanical_impedance(d["ts"],f,e)+s*cli.positive(d.get("extra_mass_g",0),"extra_mass_g",zero=True)*.001
        b=np.zeros(n) if d.get("front_node") is None and d.get("rear_node") is None else incidence([d.get("front_node"),d.get("rear_node")])
        voltage=float(d.get("voltage_rms",2.83))*np.exp(1j*np.deg2rad(float(d.get("phase_deg",0))))
        ya=e["sd"]**2/(zm+e["bl"]**2/ze)
        q0=e["sd"]*e["bl"]*voltage/(ze*zm+e["bl"]**2)
        matrix+=ya[:,None,None]*np.outer(b,b)
        rhs+=q0[:,None]*b
        motors.append((d,e,ze,zm,b,ya,q0,voltage))
    if n:
        try:pressure=np.linalg.solve(matrix,rhs[...,None])[...,0]
        except np.linalg.LinAlgError as exc:raise cli.InputError("singular chamber network") from exc
        residual=np.max(abs((matrix@pressure[...,None])[...,0]-rhs),axis=1)/np.maximum(np.max(abs(rhs),axis=1),1e-30)
    else:
        pressure=np.zeros((len(f),0),complex);residual=np.zeros(len(f))
    driver_rows=[];outlet_rows=[];emissions=[]
    for d,e,ze,zm,b,ya,q0,voltage in motors:
        q=q0-ya*(pressure@b);v=q/e["sd"];current=(voltage-e["bl"]*v)/ze
        driver_rows.append(dict(id=d["id"],voltage_v=voltage,current_a=current,
                               z_ohm=np.divide(voltage,current,out=np.full_like(current,np.nan),where=abs(current)>1e-30)-float(d.get("series_resistance_ohm",0)),
                               excursion_peak_mm=np.sqrt(2)*abs(v/s)*1000,
                               velocity_m_s=v,acceleration_rms_m_s2=abs(s*v),
                               reaction_force_peak_n=np.sqrt(2)*abs(s*v)*(e["mms"]+d.get("extra_mass_g",0)*.001),
                               copper_loss_w=abs(current)**2*e["re"]))
        if d.get("front_node") is None:
            emissions.append(dict(id=d["id"],flow=q,position_m=d.get("position_m",[0,0,0])))
        elif d.get("rear_node") is None:
            emissions.append(dict(id=d["id"],flow=-q,position_m=d.get("position_m",[0,0,0])))
    for record,kind,b,z,count,data in branches:
        q=(pressure@b)/z
        velocity=q/(count*data["area_m2"])
        row=dict(id=record["id"],kind=kind,volume_velocity_m3_s=q,velocity_peak_m_s=np.sqrt(2)*abs(velocity),**data)
        if kind=="radiator":
            row["excursion_peak_mm"]=np.sqrt(2)*abs(velocity/s)*1000
            row["reaction_force_peak_n"]=np.sqrt(2)*abs(s*velocity)*(record["mmp_g"]+record.get("added_mass_g",0))*.001*count
        outlet_rows.append(row)
        if None in record["nodes"]:
            sign=1 if record["nodes"][1] is None else -1
            emissions.append(dict(id=record["id"],flow=q*sign,position_m=record.get("position_m",[0,0,0])))
    solid={"half":2*np.pi,"full":4*np.pi}.get(p.get("space","half"))
    if solid is None:raise cli.InputError("space needs half or full")
    observers=np.asarray(p.get("observers_m",[[0,1,0]]),float)
    total=np.zeros((len(observers),len(f)),complex)
    for emission in emissions:
        r=np.linalg.norm(observers-np.asarray(emission["position_m"]),axis=1)
        if np.any(r<=0):raise cli.InputError("observer coincides with emission")
        emission["pressure_at_1m_pa"]=s*cli.RHO*emission["flow"]/solid
        total+=emission["pressure_at_1m_pa"][None,:]*np.exp(-s[None,:]*r[:,None]/cli.C)/r[:,None]
    return dict(f_hz=f,expanded_network=p,chamber_pressure_pa=pressure,drivers=driver_rows,
                outlets=outlet_rows,emissions=emissions,observer_pressure_pa=total,
                relative_residual=residual,
                validity=dict(model="Lumped small-signal chambers, acoustic masses and radiator suspensions. No transverse modes, mutual outlet radiation or flow noise."))


if __name__=="__main__":
    sys.exit(cli.run(NAME,VERSION,compute,__doc__,[
        "Explicit incidences determine the enclosure topology. Geometry and model parameters do not select an alignment.",
        "See framework/references/passive-enclosure-networks.md for equivalent circuits and limitations."]))
