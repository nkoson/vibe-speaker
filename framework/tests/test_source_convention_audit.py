import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import apps, cli


def test_reference_processing_matches_inline_gain_delay_and_polarity(tmp_path):
    f = np.array([100., 200., 400.])
    p = np.array([1+2j, 2-1j, .4+.3j])
    cli.write_document(tmp_path/"curve.json", {"results": {"f_hz": f, "p": p}})
    inline = dict(frequency_hz=f, real=p.real, imag=p.imag)
    reference = dict(reference=dict(file="curve.json", path="results.p"))
    kwargs = dict(gain_db=3, scale=.25, polarity=-1, delay_s=.00013)
    module = apps.module("response_prepare")
    expected = p*.25*10**(3/20)*-1*np.exp(-2j*np.pi*f*.00013)
    for record in (inline, reference):
        actual = module.compute(dict(operation="sum", frequencies={"values_hz": f},
                                     responses=[dict(record, **kwargs)]), tmp_path)["response"]
        np.testing.assert_allclose(actual, expected, atol=1e-12)


@pytest.mark.parametrize("space,solid_angle", [("full", 4*np.pi), ("half", 2*np.pi)])
@pytest.mark.parametrize("phase", ["absolute", "intrinsic"])
def test_flow_pressure_conversion_matches_green_function(tmp_path, space, solid_angle, phase):
    f = np.array([30., 100., 250.])
    q = np.array([1e-4, 2e-4j, -3e-4])
    params = dict(operation="volume_velocity_to_pressure", frequencies={"values_hz": f},
                  responses=[dict(frequency_hz=f, real=q.real, imag=q.imag)],
                  distance_m=2, radiation_space=space, phase_reference=phase)
    module = apps.module("response_prepare")
    result = module.compute(params, tmp_path)
    expected = 1j*2*np.pi*f*cli.RHO*q/(solid_angle*2)
    if phase == "absolute":
        expected *= np.exp(-2j*np.pi*f*2/cli.C)
    np.testing.assert_allclose(result["response"], expected)
    params.update(operation="pressure_to_volume_velocity",
                  responses=[dict(frequency_hz=f, real=expected.real, imag=expected.imag)])
    np.testing.assert_allclose(module.compute(params, tmp_path)["response"], q)


def test_bem_patch_flow_is_preserved_across_meshes(tmp_path):
    module = apps.module("exterior_bem")
    for n in (2, 3):
        params = dict(frequencies={"values_hz": [40]},
                      surface=dict(shape="box", dimensions_m=[1, 1, 1], divisions=n),
                      drive=dict(patches=[dict(disk=dict(centre_m=[.5, 1, .5],
                           normal=[0, 1, 0], radius_m=.4), volume_velocity_m3_s=.001)]),
                      observers_m=[[.5, 3, .5]])
        result = module.compute(params, tmp_path)
        patch = result["drive_patches"][0]
        np.testing.assert_allclose(patch["volume_velocity_m3_s"], .001)
        assert patch["selected_area_m2"] > 0
        assert np.all(np.asarray(result["surface"]["normals"])[patch["triangles"], 1] > .99)
        params["drive"]["patches"][0]["disk"]["centre_m"] = [2, 1, 2]
        with pytest.raises(cli.InputError, match="no triangles"):
            module.compute(params, tmp_path)


def test_fixture_magnitude_removed_before_relative_shape_normalization(tmp_path):
    import copy
    f = np.geomspace(20, 20000, 120)
    # Independently construct a one-pole shelf fixture and an intrinsic magnitude.
    fixture = (1j*f/200+1)/(1j*f/200+2)
    intrinsic_db = 94-10*np.log10(1+(f/3000)**2)
    measured_db = intrinsic_db+20*np.log10(abs(fixture))
    cli.write_document(tmp_path/"base.json", {"results": {"f_hz": f, "p": np.ones(len(f), complex)}})
    cli.write_document(tmp_path/"fixture.json", {"results": {"f_hz": f, "p": fixture}})
    p = dict(frequencies={"values_hz": f}, impedance={"kind": "resistive", "r_ohm": 8},
             acoustic=dict(kind="lf_box", reference={"file": "base.json", "path": "results.p"},
                           voltage_rms=1, blend_band_hz=[150, 300],
                           published_shape=dict(mode="replace", points=np.c_[f, intrinsic_db].tolist())))
    module = apps.module("source_response")
    expected = module.compute(p, tmp_path)["pressure_per_volt_pa"]
    observed = copy.deepcopy(p)
    observed["acoustic"]["published_shape"].update(
        points=np.c_[f, measured_db].tolist(),
        fixture_response={"file": "fixture.json", "path": "results.p"})
    np.testing.assert_allclose(module.compute(observed, tmp_path)["pressure_per_volt_pa"], expected, atol=1e-11)
    # Scaling the fixture by a constant cannot identify source sensitivity.
    cli.write_document(tmp_path/"fixture.json", {"results": {"f_hz": f, "p": fixture*2}})
    np.testing.assert_allclose(module.compute(observed, tmp_path)["pressure_per_volt_pa"], expected, atol=1e-11)
