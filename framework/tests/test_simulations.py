"""Smoke and invariant tests for the standalone simulation applications.

Run: .speaker-venv/bin/python -m pytest framework/tests -q
The example chain is executed once into framework/simulations/examples/out.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]
OUT = HARNESS / "simulations" / "examples" / "out"


def load(name):
    return json.loads((OUT / f"{name}.json").read_text())


def test_every_example_computed(chain):
    for line in chain.splitlines():
        assert line.startswith("ok"), line


def test_result_documents_carry_identity_and_no_verdicts():
    for path in OUT.glob("*.json"):
        doc = json.loads(path.read_text())
        if "simulation" not in doc:
            continue
        assert doc["status"] == "computed"
        assert doc["simulation"] and doc["version"]
        text = json.dumps(doc["results"]).lower()
        for word in ('"pass"', '"fail"', "blocked", "viable", "acceptable", "verdict"):
            assert word not in text, f"{path.name} contains a judgement word: {word}"


def test_lf_box_physics():
    r = load("lf_box")["results"]
    stats = r["curves"][0]["statistics"]
    assert 25 < stats["cutoffs"]["f6"]["value_hz"] < 60
    assert abs(r["derived_driver"]["mms_g"] / 85.2 - 1) < .05
    z = np.array(r["curves"][0]["z_ohm"]["magnitude"])
    assert z.min() > 5.0
    assert r["vent"]["physical_length_mm"] > 0
    assert r["curves"][1]["statistics"]["max_excursion_peak_mm"] == pytest.approx(10 * stats["max_excursion_peak_mm"], rel=1e-6)


def test_crossover_network_energy_and_impedance():
    r = load("crossover_network")["results"]
    assert r["statistics"]["input_z_min_ohm"] > 0
    lf = r["sections"][0]
    mags = np.array(lf["transfer"]["magnitude_db"])
    f = np.array(r["f_hz"])
    assert mags[f < 100].max() < 3
    assert mags[f > 10000].max() < -30


def test_whole_speaker_sum_is_between_parts_and_power_sum():
    r = load("whole_speaker")["results"]
    total = np.array(r["on_axis"]["spl_db"])
    power = np.array(r["on_axis"]["power_sum_db"])
    assert np.all(total <= power + 20 * np.log10(len(r["on_axis"]["sections"])) + 1e-6)
    assert r["statistics"]["acoustic_crossings"]
    assert len(r["horizontal"]["spl_db"]) == len(r["horizontal"]["angles_deg"])


def test_crossover_fit_improves_ripple():
    r = load("crossover_fit")["results"]
    f = np.array(r["fit_f_hz"])
    band = r["band_hz"]
    inside = (f >= band[0]) & (f <= band[1])
    start = np.ptp(np.array(r["start_spl_db"])[inside])
    assert r["statistics"]["ripple_in_band_db"] < start


def test_board_nodal_matches_ladder_in_linked_mode():
    board = load("board_nodal")["results"]
    linked = board["modes"][0]
    assert linked["kcl_relative_residual"] < 1e-8
    assert linked["power_relative_residual"] < 1e-8
    iso = board["modes"][1]
    mf = next(l for l in iso["loads"] if l["id"] == "mf")
    assert max(mf["transfer"]["magnitude_db"]) < -100


def test_cavity_modes_and_convergence():
    r = load("cavity_modes")["results"]
    fine = r["bases"][-1]
    assert fine["cells"] > 1000
    assert 140 < r["bases"][-1]["modeled_air_volume_l"] < 160
    assert fine["first_modes_hz"][0] > 150
    assert r["mesh_convergence"]["first_modes_max_relative_change_percent"] < 10


def test_plate_structure_scaling():
    r = load("plate_structure")["results"]
    assert r["summary"]["min_first_mode_hz"] > 50
    for panel in r["panels"]:
        bounds = [v["peak_bound_rms_mm"] for v in panel["loss_variants"]]
        assert bounds == sorted(bounds, reverse=True)


def test_response_metrics_comparisons():
    r = load("response_metrics")["results"]
    comp = r["comparisons"][1]
    assert comp["alignment_offset_applied_to_a_db"] != 0
    assert 0 <= comp["fraction_of_band_within_db"]["3"] <= 1


def test_input_error_document(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"driver": {"ts": {"fs_hz": 35}}, "enclosure": {"type": "vented"}}))
    proc = subprocess.run([sys.executable, str(HARNESS / "simulations" / "lf_box" / "run.py"), "--input", str(bad), "--out", str(tmp_path)], capture_output=True, text=True)
    assert proc.returncode == 2
    doc = json.loads((tmp_path / "lf_box.json").read_text())
    assert doc["status"] == "input_error"


def test_tools_run(tmp_path):
    tools = HARNESS / "tools"
    proc = subprocess.run([sys.executable, str(tools / "cabinet_drawing.py"), "--input", str(tools / "example_cabinet.json"), "--out", str(tmp_path)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    cut = json.loads((tmp_path / "example_cabinet_cutlist.json").read_text())
    assert 100 < cut["chambers"][0]["net_l"] < 200
    proc = subprocess.run([sys.executable, str(tools / "schematic.py"), "--input", str(HARNESS / "simulations" / "crossover_network" / "example.json"), "--out", str(tmp_path), "--name", "demo"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    board = json.loads((tmp_path / "demo_board.json").read_text())
    assert board["components"] and board["modes"]
    connections = (tmp_path / "demo_connections.md").read_text()
    assert "Jantzen Cross-Cap" in connections
    assert "400 V" in connections
    proc = subprocess.run([sys.executable, str(tools / "build_pdf.py"), "--out", str(tmp_path / "package.pdf"), "--title", "Demo package",
                           "--md", str(tmp_path / "demo_connections.md"), "--md", str(tmp_path / "example_cabinet_cutlist.md"),
                           "--preview", str(tmp_path / "preview")], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "package.pdf").stat().st_size > 5000
    assert (tmp_path / "preview" / "page-01.png").exists()
    proc = subprocess.run([sys.executable, str(tools / "plot_curves.py"), "--out", str(tmp_path / "p.png"), "--curve",
                           f"{OUT / 'whole_speaker.json'}:results.f_hz:results.on_axis.spl_db:System"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
