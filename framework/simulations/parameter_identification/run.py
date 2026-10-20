#!/usr/bin/env python3
"""Identify declared driver or passive-radiator parameters from complex impedance."""
import copy
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, response_data, apps
NAME="parameter_identification"
VERSION="1.0"


def ts_from_physical(values, area):
    m,c,r,bl,re=[values[k] for k in ("mms_kg","cms_m_per_n","rms_ns_m","bl_tm","re_ohm")]
    w=1/np.sqrt(m*c)
    return dict(fs_hz=w/(2*np.pi),vas_l=c*cli.RHO*cli.C**2*area**2*1000,
                qms=w*m/r,qes=w*m*re/bl**2,re_ohm=re,sd_cm2=area*1e4,
                le_mh=values.get("le_h",0)*1000)


def compute(params,base_dir):
    mode=params.get("mode","driver")
    initial=dict(params["initial"]);known=dict(params.get("known",{}))
    if set(initial)&set(known):raise cli.InputError("initial variables and known values must be disjoint")
    bounds=params["bounds"];keys=list(initial)
    if not keys:raise cli.InputError("identification needs at least one fitted parameter")
    lower=np.array([bounds[k][0] for k in keys],float)
    upper=np.array([bounds[k][1] for k in keys],float)
    x0=np.array([initial[k] for k in keys],float)
    if np.any(lower<0) or np.any(lower>=upper) or np.any(x0<lower) or np.any(x0>upper):
        raise cli.InputError("fit requires nonnegative ordered bounds containing the initial point")
    observations=[]
    for record in params["observations"]:
        if "file" in record:
            f,z,phase=response_data.read_table(cli.resolve_path(record["file"],base_dir),"impedance",record.get("phase_assumption"))
        else:
            f=np.asarray(record["frequency_hz"],float)
            z=cli.complex_from_record(record);phase="supplied"
        if len(f)<3 or z.shape!=f.shape or np.any(f<=0) or np.any(np.diff(f)<=0) or not np.all(np.isfinite(z)):
            raise cli.InputError("impedance observations need increasing finite frequency/complex arrays")
        observations.append((record,f,z,phase))
    if not observations:raise cli.InputError("observations cannot be empty")
    if mode=="driver":
        required={"mms_kg","cms_m_per_n","rms_ns_m","bl_tm","re_ohm"}
        if not required <= set(initial)|set(known):
            raise cli.InputError("driver identification needs Mms, Cms, Rms, Bl and Re initial/known values")
        loaded=any(r.get("added_mass_g",0)>0 or r.get("sealed_volume_l",0)>0 for r,_,_,_ in observations)
        if not loaded and not ({"mms_kg","bl_tm"}&set(known)):
            raise cli.InputError("a single free-air condition needs known mms_kg or bl_tm to identify absolute mechanical scale")
        area=cli.positive(params["sd_cm2"],"sd_cm2")*1e-4
    elif mode=="radiator":
        if len(params["network"].get("radiators",[]))<1:raise cli.InputError("radiator fit needs an explicit enclosure network")
    else:raise cli.InputError("mode needs driver or radiator")
    history=[]
    def predict(values,record,f):
        if mode=="radiator":
            network=copy.deepcopy(params["network"])
            radiator=next((r for r in network["radiators"] if r["id"]==params["radiator_id"]),None)
            if radiator is None:raise cli.InputError("radiator_id is absent from network")
            radiator.update(values)
            radiator["added_mass_g"]=float(record.get("added_mass_g",radiator.get("added_mass_g",0)))
            network["frequencies"]={"values_hz":f.tolist()}
            result=apps.module("enclosure_network").compute(network,base_dir)
            return next(d["z_ohm"] for d in result["drivers"] if d["id"]==params["driver_id"])
        ts=ts_from_physical(values,area)
        kind=params.get("inductance_kind","constant")
        if kind=="leach":
            ts["inductance_model"]={"kind":kind,"k":values["inductance_k"],"n":values["inductance_n"]}
        elif kind=="lr2":
            ts["inductance_model"]={"kind":kind,"le_mh":values.get("le_h",0)*1000,
                                    "l2_mh":values["l2_h"]*1000,"r2_ohm":values["r2_ohm"]}
        elif kind=="semi_inductance":
            ts["inductance_model"]=dict(kind=kind,**{k:values[k] for k in ("leb_mh","le_mh","ke","rss_ohm") if k in values})
        elif kind!="constant":raise cli.InputError("unknown inductance_kind")
        if "creep_beta" in values:
            ts["creep"]=dict(beta=values["creep_beta"],transition_hz=values.get("creep_transition_hz",1.5*ts["fs_hz"]))
        e=acoustics.driver_elements(ts);s=2j*np.pi*f
        zm=acoustics.mechanical_impedance(ts,f,e)+s*float(record.get("added_mass_g",0))*.001
        if record.get("sealed_volume_l"):
            zm+=area**2*cli.RHO*cli.C**2/(s*cli.positive(record["sealed_volume_l"],"sealed_volume_l")*.001)
        return acoustics.blocked_impedance(ts,f)+values["bl_tm"]**2/zm
    def residual(x,retain=True):
        values=dict(known,**dict(zip(keys,x)))
        out=[]
        for record,f,z,phase in observations:
            delta=predict(values,record,f)-z
            scale=np.maximum(abs(z),float(params.get("impedance_floor_ohm",1)))
            if params.get("ignore_phase"):
                delta=(abs(predict(values,record,f))-abs(z))/scale
                out.extend(delta)
            else:
                out.extend(delta.real/scale);out.extend(delta.imag/scale)
        out=np.asarray(out)
        if retain:history.append(dict(values=values,normalized_squared_residual=float(out@out)))
        return out
    fit=least_squares(residual,x0,bounds=(lower,upper),x_scale=np.maximum(abs(x0),1e-9),
                      max_nfev=int(params.get("max_evaluations",1000)),ftol=1e-12,xtol=1e-12,gtol=1e-12)
    values=dict(known,**dict(zip(keys,fit.x)))
    singular=np.linalg.svd(fit.jac*np.maximum(abs(fit.x),1e-9)[None,:],compute_uv=False)
    rank=int(np.sum(singular>singular[0]*1e-10)) if len(singular) else 0
    result=dict(parameters=values,variable_names=keys,optimizer_status=fit.message,evaluations=fit.nfev,
                normalized_squared_residual=float(fit.fun@fit.fun),jacobian_scaled_singular_values=singular,
                jacobian_rank=rank,trials=history,
                bound_distances={k:{"lower":float(v-lo),"upper":float(hi-v)} for k,v,lo,hi in zip(keys,fit.x,lower,upper)},
                observations=[dict(f_hz=f,observed_z_ohm=z,predicted_z_ohm=predict(values,r,f),phase_basis=phase)
                              for r,f,z,phase in observations])
    if mode=="driver":
        ts=ts_from_physical(values,area)
        kind=params.get("inductance_kind","constant")
        if kind=="leach":ts["inductance_model"]=dict(kind=kind,k=values["inductance_k"],n=values["inductance_n"])
        elif kind=="lr2":ts["inductance_model"]=dict(kind=kind,le_mh=values.get("le_h",0)*1000,l2_mh=values["l2_h"]*1000,r2_ohm=values["r2_ohm"])
        elif kind=="semi_inductance":ts["inductance_model"]=dict(kind=kind,**{k:values[k] for k in ("leb_mh","le_mh","ke","rss_ohm") if k in values})
        if "creep_beta" in values:ts["creep"]=dict(beta=values["creep_beta"],transition_hz=values.get("creep_transition_hz",1.5*ts["fs_hz"]))
        result["driver_ts"]=ts
    result["validity"]=dict(interpretation="Numerical parameter estimates and local identifiability diagnostics, not fit-quality ratings or empirical uncertainty. Calibration and held-out validation remain separate.")
    return result


if __name__=="__main__":
    sys.exit(cli.run(NAME,VERSION,compute,__doc__,[
        "Known mass, box volume or motor/mass information establishes mechanical scale. Measurements must share calibration and operating condition.",
        "See framework/references/driver-impedance-identification.md. No fit-quality classification is emitted."]))
