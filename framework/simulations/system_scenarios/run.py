#!/usr/bin/env python3
"""Replay dependency chains over shared correlated draws and explicit model scenarios."""
import copy,itertools,sys,tempfile
from pathlib import Path
import numpy as np
from scipy.special import ndtr
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,apps
NAME="system_scenarios"
VERSION="1.0"

def assign(record,path,value):
    parts=path.split('.');current=record
    for part in parts[:-1]:current=current[int(part)] if isinstance(current,list) else current[part]
    if isinstance(current,list):current[int(parts[-1])]=value
    else:current[parts[-1]]=value

def references(record,outputs):
    if isinstance(record,dict):
        return {k:(str(outputs[v[1:]]) if k=="file" and isinstance(v,str) and v.startswith('@') else references(v,outputs)) for k,v in record.items()}
    if isinstance(record,list):return [references(v,outputs) for v in record]
    return record

def compute(params,base_dir):
    variables=params.get("variables",[]);n=len(variables);draws=int(params.get("draws",0));rng=np.random.default_rng(params.get("seed",0))
    correlation=np.asarray(params.get("correlation",np.eye(n)),float).reshape(n,n)
    if n and (not np.allclose(correlation,correlation.T) or not np.allclose(np.diag(correlation),1) or np.linalg.eigvalsh(correlation).min() < -1e-10):raise cli.InputError("correlation needs a symmetric positive semidefinite unit-diagonal matrix")
    eigen,vectors=np.linalg.eigh(correlation);latent=rng.normal(size=(draws,n))@(vectors@np.diag(np.sqrt(np.maximum(eigen,0)))).T
    sampled=[]
    for sample in np.vstack([np.zeros((1,n)),latent]):
        row=[]
        for j,var in enumerate(variables):
            centre=float(var["nominal"]);spread=float(var.get("spread",0));distribution=var.get("distribution","uniform")
            if distribution=="uniform":value=centre+spread*(2*ndtr(sample[j])-1)
            elif distribution=="normal":value=centre+spread*sample[j]
            elif distribution=="lognormal":value=centre*np.exp(spread*sample[j])
            else:raise cli.InputError("distribution needs uniform, normal or lognormal")
            row.append(value)
        sampled.append(row)
    outcomes=[]
    for scenario in params.get("model_scenarios",[{"name":"nominal","overrides":{}}]):
        for draw,values in enumerate(sampled):
            steps=copy.deepcopy(params["steps"])
            for var,value in zip(variables,values):assign(steps,var["path"],float(value))
            for path,value in scenario.get("overrides",{}).items():assign(steps,path,value)
            for record in params.get("derived_ts",[]):
                ts=cli.dotted(steps,record["path"]);ts["qts"]=1/(1/ts["qes"]+1/ts["qms"])
                sd=ts["sd_cm2"]*1e-4;cms=ts["vas_l"]*.001/(cli.RHO*cli.C**2*sd*sd)
                ts["mms_g"]=1000/((2*np.pi*ts["fs_hz"])**2*cms)
            observations={};outputs={};documents={};error=None
            with tempfile.TemporaryDirectory(prefix="speaker-scenarios-") as folder:
                try:
                    for step in steps:
                        app=apps.module(step["app"]);p=references(step["parameters"],outputs)
                        result=app.compute(p,base_dir);validity=result.pop("validity",{});doc=dict(simulation=app.NAME,version=app.VERSION,status="computed",inputs=p,results=result,validity=validity)
                        path=Path(folder)/(step["id"]+'.json');cli.write_document(path,doc);outputs[step["id"]]=path;documents[step["id"]]=doc
                    for obs in params.get("observables",[]):
                        value=cli.dotted(documents[obs["step"]],obs["path"])
                        if isinstance(value,dict) and "real" in value:value=abs(cli.complex_from_record(value))
                        if value is not None:
                            a=np.asarray(value)
                            operation=obs.get("reduce","scalar")
                            value=float({"min":np.min,"max":np.max,"mean":np.mean,"rms":lambda a:np.sqrt(np.mean(abs(a)**2)),"scalar":float}[operation](a))
                        observations[obs["name"]]=value
                except (cli.InputError,ValueError,np.linalg.LinAlgError) as exc:error=str(exc)
            outcomes.append(dict(scenario=scenario["name"],draw=draw,variables=dict(zip([v["name"] for v in variables],values)),
                                 observables=observations,input_error=error))
    summaries=[]
    for scenario in params.get("model_scenarios",[{"name":"nominal"}]):
        rows=[r for r in outcomes if r["scenario"]==scenario["name"] and r["draw"]>0]
        metrics={}
        for obs in params.get("observables",[]):
            values=[r["observables"].get(obs["name"]) for r in rows]
            finite=[x for x in values if x is not None and np.isfinite(x)]
            metrics[obs["name"]]=dict(resolved=len(finite),unresolved=len(values)-len(finite),
                                      conditional_percentiles=None if not finite else np.percentile(finite,[5,50,95]))
        summaries.append(dict(scenario=scenario["name"],draws=len(rows),metrics=metrics))
    return dict(outcomes=outcomes,summary=summaries,seed=params.get("seed",0),
                validity=dict(interpretation="Model scenarios are not assigned probabilities. Percentiles condition on resolved production draws; all unresolved counts are retained. Identical draws are shared across scenarios. No design ranking is computed."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Each scenario replays its dependency chain without a cache; scalar observables and uncertainty bookkeeping are returned to the caller."]))
