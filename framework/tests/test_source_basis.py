"""LF pressure has one drive basis; calibration changes acoustics, not electrical/mechanical predictions."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

SIM = Path(__file__).resolve().parents[1] / "simulations"
sys.path.insert(0, str(SIM))
from _common import acoustics, cli, radiation

spec = importlib.util.spec_from_file_location("source_basis_run", SIM / "source_response/run.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def source_case(tmp_path, series_r=0.4):
    example = json.loads((SIM / "lf_box/example.json").read_text())
    f = np.geomspace(20, 3000, 200)
    ts, enc = example["driver"]["ts"], example["enclosure"]
    box = acoustics.box_response(ts, enc, f, 2.83, series_r)
    curve = dict(box, voltage_rms=2.83)
    document = {"inputs": {"drive": {"series_resistance_ohm": series_r}},
                "results": {"f_hz": f, "curves": [curve]}}
    (tmp_path / "box.json").write_text(json.dumps(cli.to_jsonable(document)))
    params = {"frequencies": {"values_hz": f.tolist()},
              "acoustic": {"kind": "lf_box", "voltage_basis": "driver_terminal",
                           "reference": {"file": "box.json", "path": "results.curves.0.cone_pressure_pa"}},
              "impedance": {"kind": "reference", "reference": {"file": "box.json", "path": "results.curves.0.z_ohm"}}}
    return params, box, acoustics.box_response(ts, enc, f, 2.83, 0), f


def test_terminal_source_matches_zero_resistance_and_known_resistor_transfer(tmp_path):
    params, lossy, bare, f = source_case(tmp_path)
    result = source.compute(params, tmp_path)
    for source_key, box_key in (("pressure_per_volt_pa", "cone_pressure_pa"),
                                ("outlet_pressure_per_volt_pa", "outlet_pressure_pa")):
        np.testing.assert_allclose(result[source_key] * 2.83, bare[box_key], rtol=1e-12)
        # Independent voltage divider: moving R out of the box into the network preserves pressure.
        transfer = bare["z_ohm"] / (bare["z_ohm"] + 0.4)
        np.testing.assert_allclose(result[source_key] * transfer * 2.83, lossy[box_key], rtol=1e-12)
    np.testing.assert_allclose(np.abs(2.83 / (result["z_ohm"] + 0.4)), lossy["current_rms_a"], rtol=1e-12)


def test_calibration_scales_cone_and_outlet_but_not_impedance_or_box(tmp_path):
    params, _, _, _ = source_case(tmp_path)
    original_file = (tmp_path / "box.json").read_bytes()
    before = source.compute(params, tmp_path)
    params["acoustic"]["level_calibration"] = {"gain_db": -2.2, "basis": "test: matched drive/band datasheet anchors"}
    after = source.compute(params, tmp_path)
    for key in ("pressure_per_volt_pa", "outlet_pressure_per_volt_pa"):
        np.testing.assert_allclose(after[key], before[key] * 10 ** (-2.2 / 20))
    np.testing.assert_array_equal(after["z_ohm"], before["z_ohm"])
    assert (tmp_path / "box.json").read_bytes() == original_file


def test_legacy_basis_is_explicit_about_embedded_loss(tmp_path):
    params, lossy, _, _ = source_case(tmp_path)
    params["acoustic"].pop("voltage_basis")
    result = source.compute(params, tmp_path)
    np.testing.assert_allclose(result["pressure_per_volt_pa"] * 2.83, lossy["cone_pressure_pa"])
    assert "do not apply" in result["pressure_basis"]


def test_calibration_requires_provenance(tmp_path):
    params, *_ = source_case(tmp_path)
    params["acoustic"]["level_calibration"] = {"gain_db": -2}
    with pytest.raises(cli.InputError, match="basis"):
        source.compute(params, tmp_path)


def test_nonfirst_curve_uses_its_own_voltage(tmp_path):
    params, *_ = source_case(tmp_path)
    path = tmp_path / "box.json"
    doc = json.loads(path.read_text())
    second = copy.deepcopy(doc["results"]["curves"][0])
    second["voltage_rms"] = 5.66
    for key in ("cone_pressure_pa", "outlet_pressure_pa"):
        for component in ("real", "imag"):
            second[key][component] = [v * 2 for v in second[key][component]]
    doc["results"]["curves"].append(second)
    path.write_text(json.dumps(doc))
    before = source.compute(params, tmp_path)
    params["acoustic"]["reference"]["path"] = "results.curves.1.cone_pressure_pa"
    after = source.compute(params, tmp_path)
    np.testing.assert_allclose(after["pressure_per_volt_pa"], before["pressure_per_volt_pa"])


def test_calibrated_outlet_reaches_coherent_sum_on_the_same_basis(tmp_path):
    params, _, bare, f = source_case(tmp_path)
    params["acoustic"]["level_calibration"] = {"gain_db": -2, "basis": "test calibration"}
    result = source.compute(params, tmp_path)
    (tmp_path / "section.json").write_text(json.dumps(cli.to_jsonable({"results": result})))
    whole = {"sections": [{"name": "lf", "source": {"file": "section.json"},
                           "position": {"x_mm": 0, "z_mm": 1000, "depth_mm": 0},
                           "rear_outlets": [{"face": "front", "voltage_rms": 1,
                                             "pressure": {"file": "section.json", "path": "results.outlet_pressure_per_volt_pa"}}]}]}
    sections = radiation.load_sections(whole, f, tmp_path)
    pressure, _ = radiation.pressure(sections, f, [[0, 3, 1]], 3)
    np.testing.assert_allclose(pressure[0] * 2.83, bare["pressure_pa"] * 10 ** (-2 / 20), rtol=1e-12)


def test_terminal_basis_rejects_a_prefiltered_source(tmp_path):
    params, *_ = source_case(tmp_path)
    path = tmp_path / "box.json"
    doc = json.loads(path.read_text())
    doc["inputs"]["terminal_transfer"] = {"file": "network.json"}
    path.write_text(json.dumps(doc))
    with pytest.raises(cli.InputError, match="without terminal_transfer"):
        source.compute(params, tmp_path)


@pytest.mark.parametrize("calibration", ["invalid", {"gain_db": float("nan"), "basis": "test"},
                                        {"gain_db": 1e10, "basis": "test"}])
def test_invalid_calibration_is_an_input_error(tmp_path, calibration):
    params, *_ = source_case(tmp_path)
    params["acoustic"]["level_calibration"] = calibration
    with pytest.raises(cli.InputError, match="level_calibration"):
        source.compute(params, tmp_path)
