#!/usr/bin/env python3
"""Create or refresh the project-local Python environment and verify the simulation apps.

  python3 framework/bootstrap.py            create .speaker-venv if missing, install requirements, run the example chain
  python3 framework/bootstrap.py --check    only verify the existing environment and run the example chain
  python3 framework/bootstrap.py --tests    also run the pytest suite

Uses the project-local uv in .speaker-tools/bin when present, otherwise the
standard library venv module and pip. Nothing is installed outside the repository.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".speaker-venv"
UV = ROOT / ".speaker-tools" / "bin" / "uv"
REQUIREMENTS = ROOT / "requirements.txt"


def venv_python():
    candidates = [VENV / "bin" / "python", VENV / "Scripts" / "python.exe"]
    return next((p for p in candidates if p.exists()), None)


def run(command, **kwargs):
    print("$", " ".join(str(c) for c in command))
    return subprocess.run([str(c) for c in command], check=True, **kwargs)


def create():
    if venv_python():
        return
    if UV.exists():
        run([UV, "venv", VENV, "--python", "3.12"])
    else:
        run([sys.executable, "-m", "venv", VENV])


def install():
    python = venv_python()
    if UV.exists():
        run([UV, "pip", "install", "--python", python, "-r", REQUIREMENTS])
    else:
        run([python, "-m", "pip", "install", "--upgrade", "pip"])
        run([python, "-m", "pip", "install", "-r", REQUIREMENTS])


def verify(tests):
    python = venv_python()
    run([python, "-c", "import numpy, scipy, matplotlib; print('numpy', numpy.__version__, 'scipy', scipy.__version__, 'matplotlib', matplotlib.__version__)"])
    run([python, ROOT / "framework" / "simulations" / "examples" / "run_examples.py"])
    if tests:
        run([python, "-m", "pytest", ROOT / "framework" / "tests", "-q"])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify only; do not create or install")
    parser.add_argument("--tests", action="store_true", help="run the pytest suite after the example chain")
    args = parser.parse_args()
    if not args.check:
        create()
        install()
    if not venv_python():
        raise SystemExit("no environment at .speaker-venv; run without --check to create it")
    verify(args.tests)
    print(f"ready: {venv_python()}")


if __name__ == "__main__":
    main()
