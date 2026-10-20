#!/usr/bin/env python3
"""Energy-consistent electromechanical driver with explicit nonlinear and thermal curves."""
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.polynomial import polyval,polyder
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,acoustics
NAME="nonlinear_driver"
VERSION="1.0"

def compute(params,base_dir):
    ts=params["driver"]["ts"]
    if ts.get("inductance_model") or ts.get("creep"):
        raise cli.InputError("frequency-dependent small-signal laws require memory states; this nonlinear solver needs its explicit time-domain laws")
    e=acoustics.driver_elements(params["driver"]["ts"]);law=params.get("nonlinear",{})
    bl=law.get("bl_x",[e["bl"]]);stiff=law.get("stiffness_x",[1/e["cms"]])
    lx=law.get("inductance_x",[max(e["le"],1e-6)]);li=law.get("inductance_i_factor",[1.])
    dbl=polyder(bl);dlx=polyder(lx);dli=polyder(li)
    resistance=law.get("mechanical_resistance_v",[e["rms"]])
    thermal=params.get("thermal",{});ambient=float(thermal.get("ambient_c",20.));alpha=float(thermal.get("copper_alpha_per_k",.00393))
    rvc=cli.positive(thermal.get("coil_to_magnet_k_w",2.),"coil_to_magnet_k_w")
    rma=cli.positive(thermal.get("magnet_to_air_k_w",3.),"magnet_to_air_k_w")
    cv=cli.positive(thermal.get("coil_heat_capacity_j_k",10.),"coil_heat_capacity_j_k")
    cm=cli.positive(thermal.get("magnet_heat_capacity_j_k",100.),"magnet_heat_capacity_j_k")
    tones=params.get("drive",{}).get("tones",[{"frequency_hz":100.,"voltage_rms":1.}])
    duration=cli.positive(params.get("duration_s",.2),"duration_s");rate=cli.positive(params.get("sample_rate_hz",20000.),"sample_rate_hz")
    if any(float(t["frequency_hz"])>=rate/2 for t in tones):raise cli.InputError("drive tones exceed Nyquist")
    time=np.arange(int(duration*rate)+1)/rate
    box_l=params.get("sealed_volume_l")
    box_k=0 if box_l is None else cli.RHO*cli.C**2*e["sd"]**2/(cli.positive(box_l,"sealed_volume_l")*.001)
    vent=params.get("vented")
    cab=0 if not vent else cli.positive(vent["volume_l"],"vented.volume_l")*.001/(cli.RHO*cli.C**2)
    area=1 if not vent else cli.positive(vent["port_area_m2"],"port_area_m2")
    port_mass=1 if not vent else cli.RHO*cli.positive(vent["effective_port_length_m"],"effective_port_length_m")/area
    port_r=0 if not vent else cli.positive(vent.get("port_resistance_pa_s_m3",0),"port_resistance_pa_s_m3",zero=True)
    port_nl=0 if not vent else cli.positive(vent.get("quadratic_loss_pa_s2_m6",0),"quadratic_loss_pa_s2_m6",zero=True)
    leak=0 if not vent or not vent.get("leak_resistance_pa_s_m3") else 1/cli.positive(vent["leak_resistance_pa_s_m3"],"leak_resistance_pa_s_m3")
    if vent and box_l is not None:raise cli.InputError("choose sealed_volume_l or vented")
    def voltage(t):return sum(np.sqrt(2)*float(tone["voltage_rms"])*np.sin(2*np.pi*float(tone["frequency_hz"])*t+np.deg2rad(float(tone.get("phase_deg",0)))) for tone in tones)
    def derivative(t,y):
        x,v,i,tc,tm,pbox,qport=y
        Lx=polyval(x,lx);Li=polyval(i,li);Ldiff=Lx*(Li+i*polyval(i,dli))
        Re=e["re"]*(1+alpha*(tc-ambient));Rms=polyval(v,resistance)
        if Ldiff<=0 or Re<=0 or Rms<0:raise cli.InputError("nonlinear differential inductance/resistance leaves its physical domain")
        force_factor=polyval(x,bl)
        coenergy_gradient=polyval(x,dlx)*sum(coef*i**(n+2)/(n+2) for n,coef in enumerate(li))
        di=(voltage(t)-Re*i-force_factor*v-i*Li*polyval(x,dlx)*v)/Ldiff
        dv=(force_factor*i+coenergy_gradient-polyval(x,stiff)*x-box_k*x-Rms*v+e["sd"]*pbox)/e["mms"]
        heat=Re*i*i;exchange=(tc-tm)/rvc
        dp=0 if not vent else (-e["sd"]*v-qport-leak*pbox)/cab
        dq=0 if not vent else (pbox-port_r*qport-port_nl*abs(qport)*qport)/port_mass
        return [v,dv,di,(heat-exchange)/cv,(exchange-(tm-ambient)/rma)/cm,dp,dq]
    sol=solve_ivp(derivative,[0,time[-1]],[0,0,0,ambient,ambient,0,0],t_eval=time,method="Radau",
                  rtol=float(params.get("rtol",1e-7)),atol=1e-10,max_step=1/(max(float(t["frequency_hz"]) for t in tones)*20))
    if not sol.success:raise cli.InputError(sol.message)
    x,v,i,tc,tm,pbox,qport=sol.y;u=voltage(time);Re=e["re"]*(1+alpha*(tc-ambient))
    acceleration=np.array([derivative(t,y)[1] for t,y in zip(time,sol.y.T)])
    port_acceleration=np.array([derivative(t,y)[6] for t,y in zip(time,sol.y.T)])
    pressure=cli.RHO*(e["sd"]*acceleration+port_acceleration)/(2*np.pi)
    window=np.hanning(len(time));spectrum=np.fft.rfft(pressure*window)*2/window.sum();freq=np.fft.rfftfreq(len(time),1/rate)
    spring=sum(coef*x**(n+2)/(n+2) for n,coef in enumerate(stiff))+.5*box_k*x*x
    # Magnetic energy = i*lambda - coenergy for a nonlinear flux/current law.
    magnetic=polyval(x,lx)*sum(coef*(n+1)*i**(n+2)/(n+2) for n,coef in enumerate(li))
    stored=.5*e["mms"]*v*v+spring+magnetic+cv*(tc-ambient)+cm*(tm-ambient)+.5*cab*pbox*pbox+.5*(port_mass if vent else 0)*qport*qport
    losses=polyval(v,resistance)*v*v+(tm-ambient)/rma+(port_r+port_nl*abs(qport))*qport*qport+leak*pbox*pbox
    work=np.trapezoid(u*i-losses,time) if hasattr(np,"trapezoid") else np.trapz(u*i-losses,time)
    domains={}
    for key,values in (("x_m",x),("current_a",i)):
        band=law.get(key+"_domain")
        domains[key]=dict(min=float(values.min()),max=float(values.max()),declared_domain=band,
                          samples_outside=0 if band is None else int(np.sum((values<band[0])|(values>band[1]))))
    return dict(derived_driver=e, effective_thermal=dict(ambient_c=ambient,copper_alpha_per_k=alpha,coil_to_magnet_k_w=rvc,magnet_to_air_k_w=rma,coil_heat_capacity_j_k=cv,magnet_heat_capacity_j_k=cm),
                effective_nonlinear=dict(bl_x=bl,stiffness_x=stiff,inductance_x=lx,inductance_i_factor=li,mechanical_resistance_v=resistance),
                time_s=time,displacement_m=x,velocity_m_s=v,current_a=i,voltage_v=u,coil_temperature_c=tc,
                magnet_temperature_c=tm,box_pressure_pa=pbox,port_volume_velocity_m3_s=qport,port_velocity_m_s=qport/area,pressure_at_1m_pa=pressure,spectrum_f_hz=freq,spectrum_pressure_peak_pa=spectrum,
                energy_balance=dict(net_input_minus_dissipated_j=float(work),stored_change_j=float(stored[-1]-stored[0]),residual_j=float(work-stored[-1]+stored[0])),
                parameter_domains=domains,drive_crest_factor=float(np.max(abs(u))/np.sqrt(np.mean(u*u))),
                validity=dict(model="Polynomial force factor, secant stiffness, flux/current inductance and velocity resistance; two-body heating; sealed compliance or vented chamber/port with declared quadratic flow loss. Curves are supplied priors with SI-unit polynomial coefficients. No implicit motor data inferred from wattage."))

if __name__=="__main__":sys.exit(cli.run(NAME,VERSION,compute,__doc__,["Time-domain state and spectrum results; transient startup and supplied nonlinear/thermal parameters are part of every scenario."]))
