import json
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli, apps, acoustics


def polar_fixture(tmp_path):
    f = np.geomspace(20, 20000, 100)
    entries = []
    for plane in ("H", "V"):
        for angle in (-180, -90, 0, 90, 180):
            p = (1+.5*np.cos(np.deg2rad(angle)))*np.exp(-2j*np.pi*f*2/cli.C)
            path = tmp_path/f"{plane}{angle}.frd"
            np.savetxt(path, np.c_[f, acoustics.db(p/cli.P0), np.rad2deg(np.unwrap(np.angle(p)))])
            entries.append(dict(file=str(path), plane=plane, angle_deg=angle))
    return dict(responses=entries, distance_m=2, voltage_rms=2, phase_reference="absolute",
                frequencies={"values_hz": f.tolist()})


def test_polar_normalization_full_coverage_and_planes(tmp_path):
    p = polar_fixture(tmp_path)
    result = apps.module("polar_import").compute(p, tmp_path)
    np.testing.assert_allclose(result["pressure_per_volt_pa"], 1.5, atol=1e-12)
    assert result["coverage"]["full_sphere"]
    d = acoustics.directivity(result["directivity"], np.array([100, 1000]), np.pi, 0)
    np.testing.assert_allclose(d, 1/3, atol=1e-12)
    cli.write_document(tmp_path/"polar.json", {"results": result})
    src = apps.module("source_response").compute(dict(frequencies=p["frequencies"],
             acoustic={"kind":"simulation","reference":{"file":"polar.json"}},
             impedance={"kind":"resistive","r_ohm":8}), tmp_path)
    assert src["directivity"]["kind"] == "measured_planes"
    assert src["source_contract"]["baffle"] == "included"


def test_missing_polar_coverage_is_not_invented(tmp_path):
    p = polar_fixture(tmp_path)
    p["responses"] = [r for r in p["responses"] if abs(r["angle_deg"]) < 180]
    result = apps.module("polar_import").compute(p, tmp_path)
    assert not result["coverage"]["full_sphere"]
    with pytest.raises(cli.InputError):
        acoustics.directivity(result["directivity"], 100, np.pi, 0)


def test_measured_planes_keep_signed_nulls(tmp_path):
    p = polar_fixture(tmp_path)
    result = apps.module("polar_import").compute(p, tmp_path)
    d = result["directivity"]
    for name in ("horizontal", "vertical"):
        d[name]["real"][:] = np.cos(np.deg2rad(d[name]["angles_deg"]))[:,None]
        d[name]["imag"][:] = 0
    np.testing.assert_allclose(acoustics.directivity(d, 100, np.array([0,np.pi/2,np.pi]), 0), [1,0,-1], atol=1e-12)


def test_delayed_impulse_fft_and_reference(tmp_path):
    samples = np.zeros(64); samples[7] = 2
    p = dict(operation="ir_to_fr", impulse={"samples":samples,"sample_rate_hz":48000,"reference_time_s":7/48000})
    result = apps.module("response_prepare").compute(p, tmp_path)
    np.testing.assert_allclose(result["response"], 2, atol=1e-12)
    assert result["dc"] == 2


def test_overlap_fit_recovers_known_gain_and_delay(tmp_path):
    f = np.geomspace(50, 2000, 100)
    low = .5*np.exp(2j*np.pi*f*.0002)
    p = dict(operation="merge", frequencies={"values_hz":f},
             responses=[dict(frequency_hz=f,real=low.real,imag=low.imag),
                        dict(frequency_hz=f,real=np.ones(100),imag=np.zeros(100))],
             blend_band_hz=[100,1000],match_overlap=True)
    result = apps.module("response_prepare").compute(p,tmp_path)
    assert result["overlap_fit"]["gain_db"] == pytest.approx(20*np.log10(2),abs=1e-6)
    assert result["overlap_fit"]["delay_s"] == pytest.approx(.0002,abs=1e-9)
    np.testing.assert_allclose(result["response"], 1, atol=1e-6)


def test_digitized_log_axes(tmp_path):
    result = apps.module("response_prepare").compute(dict(operation="digitize",
       pixel_points=[[0,0],[50,50],[100,100]],
       axes={"x_pixels":[0,100],"frequency_hz":[10,1000],"y_pixels":[0,100],"values":[100,0]}),tmp_path)
    np.testing.assert_allclose(result["f_hz"],[10,100,1000])
    np.testing.assert_allclose(result["values"],[100,50,0])


def test_sided_window_preserves_impulse_at_reference(tmp_path):
    samples=np.zeros(100);samples[20]=1
    result=apps.module("response_prepare").compute(dict(operation="ir_to_fr",
        impulse=dict(samples=samples,sample_rate_hz=1000,reference_time_s=.02),
        window=dict(left_s=.01,right_s=.05,left_kind="hann",right_kind="blackman")),tmp_path)
    np.testing.assert_allclose(result["response"],1,atol=1e-12)


def test_duplicate_physical_rear_measurements_are_checked(tmp_path):
    p=polar_fixture(tmp_path)
    path=Path(p["responses"][0]["file"])
    data=np.loadtxt(path);data[:,1]+=1;np.savetxt(path,data)
    with pytest.raises(cli.InputError,match="180-degree"):
        apps.module("polar_import").compute(p,tmp_path)
