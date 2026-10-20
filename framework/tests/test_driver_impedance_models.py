import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import acoustics, cli

TS = dict(fs_hz=40,vas_l=40,qms=4,qes=.4,re_ohm=6,sd_cm2=220,le_mh=.5)


def test_fractional_inductance_matches_magnitude_and_phase():
    f = np.geomspace(10,20000,101)
    ts = dict(TS,inductance_model={"kind":"leach","k":.03,"n":.6})
    z = acoustics.blocked_impedance(ts,f)-6
    np.testing.assert_allclose(abs(z), .03*(2*np.pi*f)**.6,rtol=1e-12)
    np.testing.assert_allclose(np.angle(z), .6*np.pi/2,atol=1e-12)


def test_extended_model_recovers_inductor_when_other_branches_open():
    f = np.geomspace(10,20000,101)
    ts = dict(TS,inductance_model={"kind":"semi_inductance","le_mh":.4,"leb_mh":.1})
    np.testing.assert_allclose(acoustics.blocked_impedance(ts,f),6+2j*np.pi*f*.0005)


def test_zero_creep_and_finite_creep_passivity():
    f = np.geomspace(.1,20000,201);e=acoustics.driver_elements(TS);s=2j*np.pi*f
    expected=e["rms"]+s*e["mms"]+1/(s*e["cms"])
    np.testing.assert_allclose(acoustics.mechanical_impedance(TS,f,e),expected)
    ts=dict(TS,creep={"beta":.2,"transition_hz":60})
    z=acoustics.mechanical_impedance(ts,f,e)
    assert np.all(z.real >= e["rms"])
    assert abs(z[0]) < abs(expected[0])


def test_box_and_free_air_share_blocked_motor(tmp_path):
    f=np.geomspace(20,2000,50)
    ts=dict(TS,inductance_model={"kind":"leach","k":.04,"n":.7},creep={"beta":.1})
    free=acoustics.impedance_model({"kind":"free_air","ts":ts},f)
    box=acoustics.box_response(ts,{"type":"sealed","net_volume_l":1e12,"ql":1e12},f)["z_ohm"]
    np.testing.assert_allclose(box,free,rtol=1e-8)


def test_fractional_active_domain_rejected():
    with pytest.raises(cli.InputError):
        acoustics.blocked_impedance(dict(TS,inductance_model={"kind":"leach","k":.1,"n":1.2}),np.array([100]))


def test_isobaric_lossy_impedance_scaling():
    from _common import bass
    f=np.geomspace(10,20000,100)
    ts=dict(TS,inductance_model={"kind":"leach","k":.03,"n":.6},
            creep={"beta":.2,"c0_m_per_n":.0005,"r0_ns_m":1.2})
    original=acoustics.impedance_model({"kind":"free_air","ts":ts},f)
    for wiring,scale in [("series",2),("parallel",.5)]:
        pair,_=bass.isobaric_pair(ts,wiring)
        np.testing.assert_allclose(acoustics.impedance_model({"kind":"free_air","ts":pair},f),original*scale)
