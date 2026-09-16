"""A passive-radiator alignment that would need negative added mass is an input error, not a curve.

Mass can only be added to a radiator, so the bare part's own in-box resonance is the highest tuning it
can reach in a given volume. Before the fix the response was computed from the negative mass and only
the sign of required_added_mass_g revealed that the alignment could not be built.
"""
import json
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
APP = HARNESS / "simulations" / "lf_box" / "run.py"
sys.path.insert(0, str(HARNESS / "simulations"))
from _common import acoustics  # noqa: E402

RADIATOR = {"fp_hz": 22.4, "vap_l": 155.3, "mmp_g": 300.0, "qmp": 6.74, "sd_cm2": 804.3}
DRIVER = {"fs_hz": 19.5, "vas_l": 212.0, "qms": 3.02, "qes": 0.5, "re_ohm": 3.0, "sd_cm2": 829.6, "le_mh": 0.92}


def params(tuning_hz, **enclosure):
    return {"driver": {"ts": DRIVER},
            "enclosure": {"type": "passive_radiator", "net_volume_l": 100.0, "tuning_hz": tuning_hz,
                          "radiator": RADIATOR, **enclosure},
            "frequencies": {"min_hz": 20, "max_hz": 200, "points": 40}}


def run(tmp_path, doc, name):
    path = tmp_path / f"{name}.params.json"
    path.write_text(json.dumps(doc))
    proc = subprocess.run([sys.executable, str(APP), "--input", str(path), "--out", str(tmp_path), "--name", name],
                          capture_output=True, text=True)
    return proc, json.loads((tmp_path / f"{name}.json").read_text())


def test_the_reachable_tuning_ceiling_is_reported():
    mass = acoustics.pr_added_mass(100.0, 30.0, RADIATOR)
    assert mass["realizable"] is True
    assert mass["required_added_mass_g"] > 0
    # asking for the ceiling itself needs no added mass
    ceiling = acoustics.pr_added_mass(100.0, mass["maximum_tuning_hz"], RADIATOR)
    assert abs(ceiling["required_added_mass_g"]) < 1e-6


def test_total_mass_and_required_mass_agree():
    mass = acoustics.pr_added_mass(100.0, 30.0, RADIATOR)
    assert mass["total_moving_mass_g"] == RADIATOR["mmp_g"] + mass["required_added_mass_g"]


def test_an_unreachable_tuning_is_refused(tmp_path):
    above = acoustics.pr_added_mass(100.0, 30.0, RADIATOR)["maximum_tuning_hz"] + 5.0
    proc, doc = run(tmp_path, params(above), "too_high")
    assert proc.returncode == 2, proc.stdout
    assert doc["status"] == "input_error"
    assert "added radiator mass" in doc["error"]
    assert "reaches at most" in doc["error"]


def test_a_reachable_tuning_still_computes(tmp_path):
    proc, doc = run(tmp_path, params(30.0), "ok")
    assert proc.returncode == 0, proc.stderr
    assert doc["status"] == "computed"
    radiator = doc["results"]["radiator"]
    assert radiator["realizable"] is True
    assert radiator["added_mass_used_g"] > 0
    assert abs(radiator["actual_tuning_hz"] - 30.0) < 1e-6


def test_an_explicit_zero_added_mass_is_accepted_and_reports_what_it_gives(tmp_path):
    above = acoustics.pr_added_mass(100.0, 30.0, RADIATOR)["maximum_tuning_hz"] + 5.0
    proc, doc = run(tmp_path, params(above, added_mass_g=0), "bare")
    assert proc.returncode == 0, proc.stderr
    radiator = doc["results"]["radiator"]
    assert radiator["added_mass_used_g"] == 0
    assert abs(radiator["actual_tuning_hz"] - radiator["maximum_tuning_hz"]) < 1e-6


def test_an_explicit_negative_added_mass_is_refused(tmp_path):
    proc, doc = run(tmp_path, params(30.0, added_mass_g=-20), "negative")
    assert proc.returncode == 2
    assert doc["status"] == "input_error"
