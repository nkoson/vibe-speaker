#!/usr/bin/env python3
"""Numerical fitting and joint stock trials for general passive nodal networks."""
import copy,itertools,sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, differential_evolution, NonlinearConstraint
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,apps,radiation,acoustics,networks
NAME="network_fit"
VERSION="1.0"

class EvaluationBudgetExceeded(Exception):
    """Stop numerical work while retaining evaluated trials."""


def compute(params,base_dir):
    board=copy.deepcopy(params["network"]);board["tolerances"]={"draws":0}
    f=cli.frequency_grid(board.get("frequencies"),20,20000,300)
    variables=params["variables"];components={c["id"]:c for c in board["components"]}
    keys=[v.get("key",{"R":"value_ohm","L":"value_mh","C":"value_uf"}[components[v["id"]]["type"]]) for v in variables]
    x0=np.log([components[v["id"]][key] for v,key in zip(variables,keys)])
    bounds=[tuple(np.log(v["bounds"])) for v in variables]
    if any(lo>=hi or not lo<=x<=hi for (lo,hi),x in zip(bounds,x0)):raise cli.InputError("fit start lies outside positive ordered bounds")
    target=params.get("target",{});trials=[];budget=int(params.get("max_evaluations",200));cache={}
    system=params.get("system");sources=radiation.load_sections(system,f,base_dir) if system else None
    angles=target.get("vertical_angles_deg",[0.]);observer=(system or {}).get("observer",{})
    distance=float(observer.get("distance_m",3));ear=float(observer.get("ear_height_m",1))
    def evaluate(x,stock=False):
        key=tuple(x) if not stock else None
        if key is not None and key in cache:return cache[key]
        if len(trials)>=budget:raise EvaluationBudgetExceeded
        for v,k,value in zip(variables,keys,np.exp(x)):components[v["id"]][k]=float(value)
        result=apps.module("board_nodal").compute(board,base_dir)
        mode=result["modes"][int(params.get("mode_index",0))];loads={r["id"]:r for r in mode["loads"]}
        residual=[]
        for spec in target.get("transfers",[]):
            sel=(f>=spec["band_hz"][0])&(f<=spec["band_hz"][1]);db=acoustics.db(loads[spec["load_id"]]["transfer"])
            residual.extend(((db[sel]-float(spec["db"]))*float(spec.get("weight",1))).tolist())
        acoustic=None
        if sources:
            transfers=[loads[s["load_id"]]["transfer"] for s in system["sections"]]
            p,_=radiation.pressure(sources,f,radiation.observation_points(distance,ear,angles,"V"),distance,transfers)
            acoustic=acoustics.db(p*float(params.get("input_voltage_rms",2.83))/cli.P0)
            band=target.get("band_hz",[f[0],f[-1]]);sel=(f>=band[0])&(f<=band[1])
            residual.extend((acoustic[:,sel]-float(target["spl_db"])).ravel().tolist())
        if not residual:raise cli.InputError("network fit needs transfer targets or an acoustic target")
        margins=[]
        for condition in params.get("constraints",[]):
            band=condition.get("band_hz",[f[0],f[-1]]);sel=(f>=band[0])&(f<=band[1])
            quantity=condition["quantity"]
            if quantity=="input_impedance_ohm":curve=abs(next(s for s in mode["sources"] if s.get("active"))["input_z_ohm"])
            elif quantity=="terminal_voltage_rms":curve=loads[condition["load_id"]]["voltage_rms"]
            elif quantity=="component_power_w":curve=next(c for c in mode["components"] if c["id"]==condition["component_id"])["power_w"]
            else:raise cli.InputError(f"unknown fit quantity {quantity}")
            if "minimum" in condition:margins.append(float(np.min(curve[sel])-condition["minimum"]))
            if "maximum" in condition:margins.append(float(condition["maximum"]-np.max(curve[sel])))
        row=dict(index=len(trials),cost=float(np.mean(np.array(residual)**2)),constraint_margins=margins,
                 values=np.exp(x).tolist(),components=copy.deepcopy(board["components"]),acoustic_spl_db=acoustic,
                 input_z_min_ohm=float(min(abs(s["input_z_ohm"]).min() for s in mode["sources"] if s.get("active"))),
                 inventory_cost=networks.inventory_cost(board["components"]),
                 stock_realization=stock)
        trials.append(row)
        if key is not None:cache[key]=row
        return row
    evaluate(x0)
    status="evaluation budget exhausted"
    try:
        constraints=[dict(type="ineq",fun=lambda x:np.array(evaluate(x)["constraint_margins"]))] if params.get("constraints") else []
        if params.get("optimizer", "slsqp") == "differential_evolution":
            rng=np.random.default_rng(params.get("seed",0))
            population=rng.uniform(np.array(bounds)[:,0],np.array(bounds)[:,1],size=(max(5,int(params.get("population",15))*len(x0)),len(x0)))
            population[0]=x0
            domain=NonlinearConstraint(lambda x:np.array(evaluate(x)["constraint_margins"]),0,np.inf) if params.get("constraints") else ()
            optimum=differential_evolution(lambda x:evaluate(x)["cost"],bounds,init=population,seed=params.get("seed",0),
                                           maxiter=int(params.get("max_iterations",100)),polish=False,constraints=domain)
        elif params.get("optimizer", "slsqp") == "slsqp":
            optimum=minimize(lambda x:evaluate(x)["cost"],x0,method="SLSQP",bounds=bounds,constraints=constraints,
                             options={"maxiter":int(params.get("max_iterations",100)),"ftol":1e-9})
        else:raise cli.InputError("optimizer needs slsqp or differential_evolution")
        status=str(optimum.message)
    except EvaluationBudgetExceeded:pass
    # Numerical domain membership is reported separately from design judgement.
    constrained=[r for r in trials if all(m>=-1e-9 for m in r["constraint_margins"])]
    numerical=min(constrained or trials,key=lambda r:r["cost"])
    stock=[]
    if any(v.get("stock") for v in variables):
        choices=[]
        for v,key,value in zip(variables,keys,numerical["values"]):
            choices.append(v.get("stock") or [{key:value}])
        stock_budget=int(params.get("max_stock_trials",256));budget+=stock_budget
        for combination in itertools.islice(itertools.product(*choices),stock_budget):
            for v,record in zip(variables,combination):
                if any(k in record for k in ("id","nodes","type")):raise cli.InputError("stock records use sku; circuit identity/type/nodes stay fixed")
                components[v["id"]].update(record)
            values=np.log([components[v["id"]][key] for v,key in zip(variables,keys)])
            stock.append(evaluate(values,True))
    continuous_minimum_index=numerical["index"]
    constrained=[r for r in trials if all(m>=-1e-9 for m in r["constraint_margins"])]
    numerical=min(constrained or trials,key=lambda r:r["cost"])
    return dict(f_hz=f,continuous_minimum_index=continuous_minimum_index,trials=trials,stock_trials=[r["index"] for r in stock],
                numerical_minimum_index=numerical["index"],optimizer_status=status,
                numerical_domain_count=len(constrained),
                validity=dict(objective="Declared numeric targets/constraints; trial metrics do not choose a speaker or prescribe acceptance. Stock trials preserve SKU, losses, rating and price fields supplied together."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Uses board_nodal for every trial, including mutual inductance and transformer records. All evaluated trials and constraint margins are returned for model interpretation."]))
