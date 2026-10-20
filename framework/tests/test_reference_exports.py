"""Production solvers versus frozen independently evaluated circuits."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import apps, comparison

ROOT = Path(__file__).resolve().parents[1] / "benchmarks/reference_exports"


def test_reference_hashes_and_no_production_imports():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for case in manifest["cases"]:
        assert hashlib.sha256((ROOT / case["file"]).read_bytes()).hexdigest() == case["sha256"]
    generator = (ROOT.parent / "generate_reference_exports.py").read_text()
    assert "_common" not in generator


@pytest.mark.parametrize("name", ["rc_lowpass", "rlc_lowpass"])
def test_board_against_independent_rational_export(name, tmp_path):
    data = np.loadtxt(ROOT / (name + ".csv"), delimiter=",", skiprows=1)
    components = [{"id": "R", "type": "R", "nodes": ["in", "mid"], "value_ohm": 8},
                  {"id": "C", "type": "C", "nodes": ["out", "0"], "value_uf": 20, "esr_ohm": 0}]
    if name.startswith("rlc"):
        components.append({"id": "L", "type": "L", "nodes": ["mid", "out"], "value_mh": 1, "dcr_ohm": 0})
        wires = []
    else:
        wires = [{"id": "link", "from": "mid", "to": "out", "resistance_ohm": 0}]
    params = dict(frequencies={"values_hz": data[:, 0].tolist()}, components=components, wires=wires,
                  sources=[dict(id="source", plus="in", minus="0", voltage_rms=1)],
                  loads=[dict(id="probe", plus="out", minus="0", impedance={"kind": "resistive", "r_ohm": 1e15})])
    result = apps.module("board_nodal").compute(params, tmp_path)["modes"][0]
    np.testing.assert_allclose(result["loads"][0]["transfer"], data[:, 1]+1j*data[:, 2],
                               rtol=1e-10, atol=1e-12)


def test_comparison_reports_errors_without_verdicts():
    f = np.geomspace(10, 1000, 100)
    result = comparison.compare(f, np.ones(100)*2j, np.ones(100))
    assert result["rms_magnitude_difference_db"] == pytest.approx(20*np.log10(2))
    np.testing.assert_allclose(result["phase_difference_deg"], 90)
    assert not {"pass", "fail", "acceptable", "recommended"} & result.keys()
