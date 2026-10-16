#!/usr/bin/env python3
"""Run one simulation without a cache and accept only its newly computed result."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

SIMULATIONS = Path(__file__).resolve().parents[1] / "simulations"


def run_simulation(app, input_path, out_dir, name=None):
    script = SIMULATIONS / app / "run.py"
    if Path(app).name != app or not script.is_file():
        raise ValueError(f"unknown simulation: {app}")
    name = name or app
    if Path(name).name != name or name in (".", ".."):
        raise ValueError("result name must be a file stem")
    input_path = Path(input_path).resolve()
    out_dir = Path(out_dir).resolve()
    output = out_dir / f"{name}.json"
    if output.resolve() == input_path:
        raise ValueError("input and result paths must differ")
    out_dir.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    proc = subprocess.run(
        [sys.executable, str(script), "--input", str(input_path), "--out", str(out_dir), "--name", name],
        capture_output=True, text=True,
    )
    if proc.returncode:
        raise RuntimeError(f"{app} exited {proc.returncode}\n{proc.stderr}\n{proc.stdout}")
    if not output.is_file():
        raise RuntimeError(f"{app} exited successfully without writing {output}")
    document = json.loads(output.read_text())
    if document.get("status") != "computed" or document.get("simulation") != app:
        raise RuntimeError(f"{app} did not produce its computed result: {document.get('error', document.get('status'))}")
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--name")
    args = parser.parse_args()
    try:
        run_simulation(args.app, args.input, args.out, args.name)
    except (ValueError, RuntimeError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(Path(args.out) / f"{args.name or args.app}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
