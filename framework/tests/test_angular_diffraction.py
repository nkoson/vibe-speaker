import sys
from pathlib import Path
import numpy as np
from scipy.special import j0
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import diffraction, cli, apps, radiation


def circle(count):
    a=np.linspace(0,2*np.pi,count,endpoint=False)
    return dict(kind="distributed_edge_dipole",vertices_mm=np.c_[300*np.cos(a),300*np.sin(a)].tolist(),
                source_mm=[0,0],subdivisions=1)


def test_polygon_converges_to_independent_circular_dipole_formula():
    f=np.geomspace(10,3000,50)[None,:];angles=np.deg2rad(np.array([0,30,60,90,120,180]))[:,None]
    mu=np.cos(angles);k=2*np.pi*f/cli.C
    expected=(1+mu)/2-mu/2*np.exp(-1j*k*.3)*j0(k*.3*np.sin(angles))
    errors=[]
    for n in [32,128,512]:
        actual=diffraction.evaluate(circle(n),f,angles,0)
        errors.append(np.max(abs(actual-expected)))
    assert errors[2]<errors[1]<errors[0]
    assert errors[2]<1e-3


def test_open_baffle_null_and_rear_sign():
    model=dict(circle(128),open_baffle=True)
    values=diffraction.evaluate(model,100,np.deg2rad([0,90,180]),0)
    assert abs(values[1])<1e-12
    assert values[2]==pytest.approx(-values[0])


def test_angular_model_is_applied_once_in_system(tmp_path):
    f=np.geomspace(20,2000,50)
    p=dict(frequencies={"values_hz":f},baffle={"width_mm":300,"height_mm":500},
           sources=[{"name":"driver","x_mm":150,"z_mm":250,"model":"distributed_edge_dipole"}],far_field=True)
    result=apps.module("baffle_diffraction").compute(p,tmp_path)
    cli.write_document(tmp_path/"baffle.json",{"results":result})
    cli.write_document(tmp_path/"source.json",{"results":{"f_hz":f,"pressure_per_volt_pa":np.ones(len(f),complex),"directivity":{"kind":"omni"}}})
    sections=radiation.load_sections(dict(sections=[dict(name="s",source={"file":"source.json"},
            position={"z_mm":0},baffle={"file":"baffle.json","path":"results.sources.0.baffle_factor"})]),f,tmp_path)
    pressure,_=radiation.pressure(sections,f,[[0,3,0]],3)
    np.testing.assert_allclose(pressure[0],result["sources"][0]["baffle_factor"])
    assert sections[0]["directivity"]["kind"]=="distributed_edge_dipole"
