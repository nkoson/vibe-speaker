import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import apps, acoustics, cli

TS=dict(fs_hz=40,vas_l=40,qms=4,qes=.4,re_ohm=6,sd_cm2=220,le_mh=.5)


@pytest.mark.parametrize("kind",["sealed","vented"])
def test_chamber_network_recovers_independent_lumped_response(kind,tmp_path):
    f=np.geomspace(10,1500,100);volume=40;fb=40;ql=10;qp=20
    cb=volume*.001/(cli.RHO*cli.C**2)
    ref=fb if kind=="vented" else TS["fs_hz"]*np.sqrt(1+TS["vas_l"]/volume)
    p=dict(preset=kind,driver={"ts":TS},rear={"volume_l":volume,"ql":ql,"loss_reference_hz":ref},
           frequencies={"values_hz":f},voltage_rms=2.83)
    if kind=="vented":
        area=np.pi*.04**2;mass=1/((2*np.pi*fb)**2*cb)
        p["port"]=dict(area_m2=area,effective_length_m=mass*area/cli.RHO,resistance_pa_s_m3=2*np.pi*fb*mass/qp)
    result=apps.module("enclosure_network").compute(p,tmp_path)
    traditional=acoustics.box_response(TS,dict(type=kind,net_volume_l=volume,tuning_hz=fb,ql=ql,qp=qp,
                                             port={"diameter_mm":80}),f)
    np.testing.assert_allclose(result["drivers"][0]["z_ohm"],traditional["z_ohm"],rtol=1e-10)
    predicted=result["observer_pressure_pa"][0]*np.exp(2j*np.pi*f/cli.C)
    np.testing.assert_allclose(predicted,traditional["pressure_pa"],rtol=1e-10,atol=1e-12)


def test_pr_bandpass_and_double_reflex_outputs(tmp_path):
    module=apps.module("enclosure_network")
    common=dict(driver={"ts":TS},rear={"volume_l":40},front={"volume_l":20},
                frequencies={"values_hz":[20,40,80,160]})
    pr=module.compute(dict(common,preset="bandpass_pr",
        radiator=dict(sd_cm2=250,mmp_g=70,cmp_m_per_n=.001,rmp_ns_m=2)),tmp_path)
    assert len(pr["emissions"])==1
    assert "excursion_peak_mm" in pr["outlets"][0]
    reflex=module.compute(dict(common,preset="double_tuned_reflex",
        port=dict(area_m2=.005,effective_length_m=.2,resistance_pa_s_m3=10),
        outer_port=dict(area_m2=.005,effective_length_m=.3,resistance_pa_s_m3=10)),tmp_path)
    assert len(reflex["emissions"])==2
    assert max(reflex["relative_residual"])<1e-12


def test_added_mass_identification_recovers_physical_parameters(tmp_path):
    # Independent primitive equation; do not synthesize through production driver helpers.
    f=np.geomspace(10,2000,150);s=2j*np.pi*f
    true=dict(mms_kg=.03,cms_m_per_n=.0005,rms_ns_m=1.5,bl_tm=8,re_ohm=6,le_h=.0005)
    observations=[]
    for mass in (0,.02,.04):
        z=6+s*.0005+64/(1.5+s*(.03+mass)+1/(s*.0005))
        observations.append(dict(frequency_hz=f,real=z.real,imag=z.imag,added_mass_g=mass*1000))
    initial={k:v*1.2 for k,v in true.items()}
    p=dict(sd_cm2=220,initial=initial,bounds={k:[v*.1,v*10] for k,v in true.items()},observations=observations)
    result=apps.module("parameter_identification").compute(p,tmp_path)
    for k,v in true.items():assert result["parameters"][k]==pytest.approx(v,rel=1e-5)
    assert result["jacobian_rank"]==len(true)
    assert not {"score","acceptable","pass","fail"}&result.keys()
