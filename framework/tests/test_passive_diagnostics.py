import json
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli,apps,load_diagnostics


def test_epdr_resistor_reactive_limit_and_symmetry():
    np.testing.assert_allclose(load_diagnostics.epdr(np.array([4,8,16])),[4,8,16],rtol=1e-12)
    assert load_diagnostics.epdr(np.array([8j]))[0]==pytest.approx(8/(3*np.sqrt(3)),rel=1e-12)
    z=8*np.exp(1j*np.linspace(-np.pi/2,np.pi/2,151))
    np.testing.assert_allclose(load_diagnostics.epdr(z),load_diagnostics.epdr(z.conj()))


def test_programme_power_for_resistor(tmp_path):
    board=dict(components=[dict(id="R",type="R",nodes=["in","out"],value_ohm=8)],
               sources=[dict(id="amp",plus="in",minus="0",voltage_rms=1)],
               loads=[dict(id="load",plus="out",minus="0",impedance={"kind":"resistive","r_ohm":8})])
    result=apps.module("network_diagnostics").compute(dict(network=board,programme={"voltage_rms":4}),tmp_path)
    mode=result["modes"][0]
    assert mode["components"][0]["mean_power_w"]==pytest.approx(.5)
    assert mode["loads"][0]["mean_power_w"]==pytest.approx(.5)
    assert mode["sources"][0]["input_mean_power_w"]==pytest.approx(1)


def test_group_delay_against_rc_analytical_expression(tmp_path):
    f=np.geomspace(1,100000,3000);tau=.001;h=1/(1+2j*np.pi*f*tau)*np.exp(-2j*np.pi*f*.002)
    result=apps.module("response_diagnostics").compute(dict(response={"frequency_hz":f,"real":h.real,"imag":h.imag},known_delay_s=.002),tmp_path)
    np.testing.assert_allclose(result["group_delay_s"],.002+tau/(1+(2*np.pi*f*tau)**2),rtol=2e-5)


def test_impulse_reconstruction_discrete_normalization(tmp_path):
    fs=48000;n=1024;f=np.fft.rfftfreq(n,1/fs)[1:];h=np.exp(-2j*np.pi*f*8/fs)
    result=apps.module("response_diagnostics").compute(dict(response={"frequency_hz":f,"real":h.real,"imag":h.imag},
        known_delay_s=8/fs,time_domain={"sample_rate_hz":fs,"fft_length":n,"dc_real":1}),tmp_path)["time_domain"]
    expected=np.zeros(n);expected[8]=1
    np.testing.assert_allclose(result["impulse_samples"],expected,atol=1e-12)
    assert result["step_response"][-1]==pytest.approx(1)


def test_spatial_fit_known_flat_attenuator(tmp_path):
    p=json.loads((Path(__file__).resolve().parents[1]/"simulations/network_fit/example.json").read_text())
    f=np.geomspace(30,1000,30)
    cli.write_document(tmp_path/"source.json",{"results":{"f_hz":f,"pressure_per_volt_pa":np.ones(30,complex)*cli.P0*10**(90/20)/2.83,
                                                        "directivity":{"kind":"omni"}}})
    p.pop("target");p["variables"][0].pop("stock")
    p["system"]=dict(sections=[dict(name="s",source={"file":"source.json"},position={"z_mm":1000},load_id="driver")])
    p["spatial_targets"]=[dict(curve="listening_window",target_db=90-20*np.log10(2),band_hz=[30,1000])]
    p["constraints"]=[dict(quantity="epdr_ohm",minimum=10)]
    result=apps.module("network_fit").compute(p,tmp_path)
    trial=result["trials"][result["numerical_minimum_index"]]
    assert trial["values"][0]==pytest.approx(8,rel=2e-4)
    assert trial["objective_terms"][0]["curve"]=="listening_window"


def test_ideal_transformer_ratio_reflected_load_and_power(tmp_path):
    p=dict(frequencies={"values_hz":[20,1000,20000]},components=[],
           transformers=[dict(id="T",kind="ideal",primary_nodes=["in","0"],secondary_nodes=["out","g"],turns_ratio=2)],
           sources=[dict(id="amp",plus="in",minus="0",voltage_rms=1)],
           loads=[dict(id="load",plus="out",minus="g",impedance={"kind":"resistive","r_ohm":8})])
    result=apps.module("board_nodal").compute(p,tmp_path)["modes"][0]
    np.testing.assert_allclose(result["loads"][0]["transfer"],.5)
    np.testing.assert_allclose(result["sources"][0]["input_z_ohm"],32)
    assert result["power_relative_residual"]<1e-12


def test_inductor_parasitics_match_explicit_parallel_network():
    from _common import acoustics
    f=np.geomspace(100,1000000,100)
    s=2j*np.pi*f
    z=acoustics.element_impedance(dict(type="L",value_mh=1,dcr_ohm=.2,parallel_r_ohm=1000,parallel_c_pf=500),f)
    np.testing.assert_allclose(z,1/(1/(.2+s*.001)+.001+s*500e-12))


def test_exports_preserve_curve_and_impulse_scale(tmp_path):
    import importlib.util
    from scipy.io import wavfile
    path=Path(__file__).resolve().parents[1]/"tools/export_response.py"
    spec=importlib.util.spec_from_file_location("export_response_test",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    p=tmp_path/"result.json"
    cli.write_document(p,dict(status="computed",simulation="test",version="1",
        results=dict(f_hz=[100,200],response=np.array([1,1j]),time_domain=dict(sample_rate_hz=48000,impulse_samples=[0,2,0]))))
    module.export(p,"results.response",tmp_path/"curve.csv","csv",quantity="transfer")
    data=np.loadtxt(tmp_path/"curve.csv",delimiter=",",skiprows=1)
    np.testing.assert_allclose(data[:,1]+1j*data[:,2],[1,1j])
    module.export(p,"results.time_domain.impulse_samples",tmp_path/"impulse.wav","wav")
    fs,samples=wavfile.read(tmp_path/"impulse.wav")
    assert fs==48000
    np.testing.assert_allclose(samples,[0,2,0])
    assert (tmp_path/"impulse.wav.json").exists()
