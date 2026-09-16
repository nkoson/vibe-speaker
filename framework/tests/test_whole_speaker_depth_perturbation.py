"""depth_perturbation_mm takes one figure for every section, or one per section.

A tweeter whose acoustic centre is 15 mm behind the baffle and a woofer 180 mm behind it do not have
the same plausible mounting uncertainty, and a single figure applied to both produces a number that
describes the model rather than the design.
"""
import json
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
APP = HARNESS / "simulations" / "whole_speaker" / "run.py"
EXAMPLE = HARNESS / "simulations" / "whole_speaker" / "example.json"
OUT = HARNESS / "simulations" / "examples" / "out"


def build(tmp_path, perturbation):
    params = json.loads(EXAMPLE.read_text())
    base = EXAMPLE.parent
    for section in params["sections"]:
        for key in ("source", "baffle", "transfer"):
            if isinstance(section.get(key), dict) and "file" in section[key]:
                section[key]["file"] = str((base / section[key]["file"]).resolve())
        for outlet in section.get("rear_outlets", []) or []:
            for key in ("pressure", "baffle"):
                if isinstance(outlet.get(key), dict) and "file" in outlet[key]:
                    outlet[key]["file"] = str((base / outlet[key]["file"]).resolve())
    params.setdefault("analysis", {})["depth_perturbation_mm"] = perturbation
    path = tmp_path / "params.json"
    path.write_text(json.dumps(params))
    return params, path


def run(tmp_path, perturbation, name):
    params, path = build(tmp_path, perturbation)
    proc = subprocess.run([sys.executable, str(APP), "--input", str(path), "--out", str(tmp_path), "--name", name],
                          capture_output=True, text=True)
    return params, proc, json.loads((tmp_path / f"{name}.json").read_text())


def test_one_figure_perturbs_every_section(tmp_path):
    params, proc, doc = run(tmp_path, 20, "uniform")
    assert proc.returncode == 0, proc.stderr
    rows = doc["results"]["depth_perturbations"]
    assert len(rows) == 2 * len(params["sections"])
    assert {abs(r["depth_change_mm"]) for r in rows} == {20.0}


def test_a_mapping_perturbs_each_section_by_its_own_amount(tmp_path):
    params, proc, doc = run(tmp_path, {params_section["name"]: mm for params_section, mm in
                                       zip(json.loads(EXAMPLE.read_text())["sections"], (40, 15, 0))}, "per_section")
    assert proc.returncode == 0, proc.stderr
    rows = doc["results"]["depth_perturbations"]
    by_section = {}
    for row in rows:
        by_section.setdefault(row["section"], set()).add(abs(row["depth_change_mm"]))
    names = [w["name"] for w in json.loads(EXAMPLE.read_text())["sections"]]
    assert by_section[names[0]] == {40.0}
    assert by_section[names[1]] == {15.0}
    assert names[2] not in by_section, "a section given 0 is not perturbed"


def test_each_row_carries_the_acoustic_depth_it_was_applied_to(tmp_path):
    _, proc, doc = run(tmp_path, 20, "depths")
    assert proc.returncode == 0, proc.stderr
    for row in doc["results"]["depth_perturbations"]:
        assert row["acoustic_depth_mm"] is not None


def test_an_unknown_section_name_is_an_input_error(tmp_path):
    _, proc, doc = run(tmp_path, {"not_a_section": 20}, "unknown")
    assert proc.returncode == 2, proc.stdout
    assert doc["status"] == "input_error"
    assert "not_a_section" in doc["error"]
