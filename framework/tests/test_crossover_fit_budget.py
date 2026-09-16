"""crossover_fit must report an exhausted objective-call budget, not crash on it."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "simulations" / "crossover_fit" / "run.py"
EXAMPLE = ROOT / "simulations" / "crossover_fit" / "example.json"


def test_polarity_trials_survive_a_budget_that_runs_out(tmp_path):
    params = json.loads(EXAMPLE.read_text())
    params["polarity_trials"] = 4
    params["max_objective_calls"] = 6          # gone during the first trial
    params["max_nfev"] = 50
    source = EXAMPLE.parent
    for section in params.get("sections", []):
        if isinstance(section.get("source"), dict) and "file" in section["source"]:
            section["source"]["file"] = str((source / section["source"]["file"]).resolve())
    for section in params.get("system", {}).get("sections", []):
        for key in ("source", "baffle"):
            if isinstance(section.get(key), dict) and "file" in section[key]:
                section[key]["file"] = str((source / section[key]["file"]).resolve())
    pfile = tmp_path / "params.json"
    pfile.write_text(json.dumps(params))
    proc = subprocess.run([sys.executable, str(APP), "--input", str(pfile), "--out", str(tmp_path), "--name", "fit"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr[-2000:]
    doc = json.loads((tmp_path / "fit.json").read_text())
    assert doc["status"] == "computed"
    attempts = doc["results"]["attempts"]
    assert len(attempts) == 4
    assert any("budget exhausted" in a["status"] for a in attempts)
