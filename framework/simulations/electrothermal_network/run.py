#!/usr/bin/env python3
"""Self-consistent steady-state voice-coil heating under a loaded passive network."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,networks
NAME="electrothermal_network"
VERSION="1.0"

def compute(params,base_dir):
    network=params["network"];sections=network["sections"]
    f=cli.frequency_grid(network.get("frequencies"),20,20000,500)
    drive=params.get("programme",{});rms=cli.positive(drive.get("voltage_rms",2.83),"programme.voltage_rms",zero=True)
    spectrum=np.asarray(drive.get("relative_psd",1/f),float)
    if spectrum.shape!=f.shape or np.any(spectrum<0):raise cli.InputError("relative_psd needs nonnegative values on the grid")
    trap=np.trapezoid if hasattr(np,"trapezoid") else np.trapz
    integral=trap(spectrum,f)
    if not np.isfinite(integral) or integral<=0:raise cli.InputError("programme PSD needs positive finite integrated weight")
    psd=rms*rms*spectrum/integral
    ambient=float(params.get("ambient_c",20));alpha=float(params.get("copper_alpha_per_k",.00393))
    temperatures=np.full(len(sections),ambient);records=[];iterations=int(params.get("iterations",40))
    if iterations<1:raise cli.InputError("iterations needs a positive count")
    thermal=params["thermal"]
    cold=[networks.section_load(s,f,base_dir) for s in sections];elements=[networks.with_wire(s) for s in sections]
    for iteration in range(iterations):
        powers=[];rows=[];network_power=np.zeros(len(f))
        for i,(section,(z,p),parts) in enumerate(zip(sections,cold,elements)):
            re=cli.positive(section["re_ohm"],"section.re_ohm");hot_re=re*(1+alpha*(temperatures[i]-ambient))
            hot_z=z+hot_re-re;state=networks.ladder_state(f,hot_z,parts,None,1.)
            power=float(trap(abs(state["load_current"])**2*hot_re*psd,f));powers.append(power)
            network_power+=sum(leaf["dissipation_w"] for leaf in state["states"])*psd
            row=dict(name=section["name"],coil_temperature_c=float(temperatures[i]),coil_power_w=power,
                     z_ohm=hot_z,transfer=state["terminal"],pressure_per_volt_pa=None if p is None else p*z/hot_z,
                     source_contract=dict(phase_reference="intrinsic",baffle="external",normalization="driver_terminal_volt"))
            rows.append(row)
        target=ambient+np.array([powers[i]*float(thermal[s["name"]]["steady_resistance_k_w"]) for i,s in enumerate(sections)])
        records.append(dict(iteration=iteration,temperatures_c=temperatures.copy(),heat_balance_temperature_residual_k=target-temperatures))
        if iteration<iterations-1:temperatures+=float(params.get("relaxation",.5))*(target-temperatures)
    return dict(f_hz=f,sections=rows,iterations=records,programme_psd_v2_hz=psd,
                network_dissipation_w=float(trap(network_power,f)),
                validity=dict(model="Fixed-point electrical/thermal resistance coupling. Mechanical and motor parameters stay fixed; pressure correction follows unchanged mechanical response and changed terminal current. Thermal resistances and programme spectrum are supplied scenarios, not endurance ratings."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Frequency-coincident driver and component losses under a total RMS programme voltage; the final temperature-balance residual is reported without an acceptance verdict."]))
