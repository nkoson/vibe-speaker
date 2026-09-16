"""The fit has to be able to say what an element is worth and what stock does to it."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
OUT = HARNESS / "simulations" / "examples" / "out"
SOURCE = OUT / "section_lf.json"


@pytest.fixture(scope="module")
def fitted(tmp_path_factory):
    if not SOURCE.exists():
        proc = subprocess.run([sys.executable, str(HARNESS / "simulations" / "examples" / "run_examples.py")],
                              capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
    section = dict(name="lf", polarity=1, source={"file": str(SOURCE)}, passband_hz=[40, 400], elements=[
        dict(id="L1", position="series", type="L", value_mh=2.2, dcr_ohm=0.25, fit={"min": 0.8, "max": 6.8}),
        dict(id="C1", position="shunt", type="C", value_uf=47, fit={"min": 10, "max": 150}),
        # Does nothing at any frequency: a megohm across an eight ohm driver.
        dict(id="idle", position="shunt", type="R", value_ohm=1e6)])
    params = dict(
        frequencies={"min_hz": 20, "max_hz": 20000, "points": 200},
        fit_frequencies={"min_hz": 50, "max_hz": 2000, "points": 60},
        max_nfev=40, max_objective_calls=1200,
        target={"spl_db": "auto", "band_hz": [80, 400]},
        system={"observer": {"distance_m": 3.0, "ear_height_m": 1.0}, "cabinet": {"depth_mm": 400, "floor_offset_mm": 0},
                "sections": [{"name": "lf", "source": {"file": str(SOURCE)}, "position": {"x_mm": 0, "z_mm": 380}}]},
        sections=[section],
        ablation={"max_nfev": 30},
        stock={"L": [1.0, 1.5, 2.2, 3.3, 4.7], "C": [22, 33, 47, 68, 100]})
    work = tmp_path_factory.mktemp("fit")
    (work / "params.json").write_text(json.dumps(params))
    proc = subprocess.run([sys.executable, str(HARNESS / "simulations" / "crossover_fit" / "run.py"),
                           "--input", str(work / "params.json"), "--out", str(work), "--name", "fit"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads((work / "fit.json").read_text())["results"]


def test_ablation_finds_the_element_that_does_nothing(fitted):
    trials = {t["id"]: t for t in fitted["ablation"]["trials"]}
    assert set(trials) == {"L1", "C1", "idle"}
    assert abs(trials["idle"]["delta_rms_db"]) < 1e-3
    assert fitted["ablation"]["trials"][0]["id"] == "idle"
    assert trials["L1"]["delta_rms_db"] > trials["idle"]["delta_rms_db"]
    assert trials["idle"]["parts_removed"] == 1


def test_ablation_does_not_disturb_the_fitted_values(fitted):
    values = {v["id"]: v["fitted"] for v in fitted["fitted_values"]}
    for section in fitted["fitted_sections"]:
        for element in section["elements"]:
            if element["id"] in values:
                key = "value_mh" if element["type"] == "L" else "value_uf"
                assert abs(element[key] - values[element["id"]]) < 1e-9


def test_quantization_snaps_to_stock_and_reports_the_whole_network(fitted):
    quantization = fitted["quantization"]
    stock = {"L": [1.0, 1.5, 2.2, 3.3, 4.7], "C": [22, 33, 47, 68, 100]}
    for value in quantization["values"]:
        assert value["from_stock"]
        assert value["stock_value"] in stock[value["type"]]
    assert quantization["rms_error_in_band_db"] >= 0
    assert quantization["input_z_min_ohm"] > 0
    ids = {e["id"] for section in quantization["sections"] for e in section["elements"]}
    assert ids == {"L1", "C1", "idle"}
    for section in quantization["sections"]:
        for element in section["elements"]:
            assert "fit" not in element


def test_the_fit_reports_what_the_network_loses_and_costs(fitted):
    efficiency = fitted["fitted_efficiency"]
    assert 0 < efficiency["to_drivers_fraction"] <= 1
    assert efficiency["loss_db"] >= 0
    assert efficiency["octave_bands"]
    assert fitted["fitted_parts"]["total"] == 3
