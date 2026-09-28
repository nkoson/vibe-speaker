"""A crash, malformed input or failed launch cannot masquerade as an earlier computed run."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

FRAMEWORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRAMEWORK / "simulations"))
from _common import cli

spec = importlib.util.spec_from_file_location("checked_runner", FRAMEWORK / "tools/run_simulation.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def invoke(tmp_path, monkeypatch, compute, input_text="{}"):
    source = tmp_path / "params.json"
    source.write_text(input_text)
    result = tmp_path / "result.json"
    result.write_text('{"status":"computed","results":{"old":true}}')
    monkeypatch.setattr(sys, "argv", ["test", "--input", str(source), "--out", str(tmp_path), "--name", "result"])
    return result, lambda: cli.run("test", "1", compute, "test", [])


def test_unhandled_crash_removes_previous_result(tmp_path, monkeypatch):
    def crash(*args):
        raise RuntimeError("deliberate crash")
    result, run = invoke(tmp_path, monkeypatch, crash)
    with pytest.raises(RuntimeError, match="deliberate crash"):
        run()
    assert not result.exists()


def test_malformed_input_replaces_old_result_with_input_error(tmp_path, monkeypatch):
    result, run = invoke(tmp_path, monkeypatch, lambda *args: {}, "{")
    assert run() == 2
    assert json.loads(result.read_text())["status"] == "input_error"


def test_success_publishes_new_result_without_temporary_files(tmp_path, monkeypatch):
    result, run = invoke(tmp_path, monkeypatch, lambda *args: {"new": 42})
    assert run() == 0
    assert json.loads(result.read_text())["results"] == {"new": 42}
    assert {p.name for p in tmp_path.iterdir()} == {"params.json", "result.json"}


def test_same_input_and_output_does_not_delete_input(tmp_path, monkeypatch):
    source = tmp_path / "params.json"
    source.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["test", "--input", str(source), "--out", str(tmp_path), "--name", "params"])
    with pytest.raises(SystemExit):
        cli.run("test", "1", lambda *args: {}, "test", [])
    assert source.read_text() == "{}"


def test_runner_rejects_crash_with_old_computed_file(tmp_path):
    source = tmp_path / "params.json"
    source.write_text('{"acoustic":{"kind":"published_curve"}}')  # missing points: unhandled KeyError
    output = tmp_path / "source_response.json"
    output.write_text('{"status":"computed"}')
    with pytest.raises(RuntimeError, match="KeyError"):
        runner.run_simulation("source_response", source, tmp_path)
    assert not output.exists()


def test_runner_recomputes_changed_referenced_content(tmp_path):
    params = {"acoustic": {"kind": "frd_file", "file": "driver.frd"},
              "impedance": {"kind": "resistive", "r_ohm": 8}}
    source = tmp_path / "params.json"
    source.write_text(json.dumps(params))
    frd = tmp_path / "driver.frd"
    frd.write_text("100 90 0\n1000 90 0\n20000 90 0\n")
    before = runner.run_simulation("source_response", source, tmp_path)
    frd.write_text("100 96 0\n1000 96 0\n20000 96 0\n")
    after = runner.run_simulation("source_response", source, tmp_path)
    assert after["results"]["statistics"]["spl_2v83_1m_db"][0] - before["results"]["statistics"]["spl_2v83_1m_db"][0] == pytest.approx(6)
