#!/usr/bin/env python3
"""Numerical benchmark observables, with analytical references and no design ratings."""
import argparse,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli,apps,geometry

def run():
    cases=[]
    f=np.array([100.,200.]);target=np.array([141.421356]);delay=.005
    actual=cli.interp_complex(target,f,np.exp(-2j*np.pi*f*delay),delay_s=delay)
    exact=np.exp(-2j*np.pi*target*delay)
    cases.append(dict(id="delay_interpolation",reference="exp(-j 2 pi f delay)",max_complex_error=float(abs(actual-exact).max())))
    f=np.array([100.,500.]);a=.1;k=2*np.pi*f/cli.C
    exact=1j*2*np.pi*f*cli.RHO*a*a/(1+1j*k*a)*np.exp(-1j*k*(1-a))
    for level in (1,2):
        mesh=geometry.object_mesh(dict(shape="sphere",radius_m=a,subdivisions=level))
        pressure,_,residual,condition=apps.module("exterior_bem").solve(mesh,f,np.ones((len(f),len(mesh["areas"]))),[[0,1,0]])
        cases.append(dict(id="pulsating_sphere",subdivisions=level,panels=len(mesh["areas"]),frequency_hz=f,
                          relative_complex_error=abs(pressure[0]/exact-1),collocation_residual=residual,condition_number=condition,
                          reference="p(r)=j omega rho a^2 v exp(-jk(r-a))/(r(1+jka)), e^(jwt) convention"))
    root=Path(__file__).resolve().parents[1]/"simulations"
    for app in ("coupled_cabinet","nonlinear_driver","electrothermal_network","distributed_loading"):
        params=cli.load_json(root/app/"example.json");result=apps.module(app).compute(params,root/app)
        observations={key:result[key] for key in ("relative_residual","energy_balance") if key in result}
        if "iterations" in result:observations["heat_balance_temperature_residual_k"]=result["iterations"][-1]["heat_balance_temperature_residual_k"]
        cases.append(dict(id=app,reference="equation residual/energy identity, not empirical agreement",observations=observations))
    return dict(cases=cases,interpretation="Errors characterize these numerical cases and inputs only; there is no design ranking or universal real-world error estimate.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",required=True);a=p.parse_args();cli.write_document(a.out,run())
