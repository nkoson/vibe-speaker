#!/usr/bin/env python3
"""Offline measurement CLI. Bootstrap/re-enter the repository environment if needed."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    python = ROOT / '.speaker-venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    probe = 'import numpy, scipy, matplotlib, javaobj.v2'
    ready = python.exists() and subprocess.run(
        [str(python), '-c', probe], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL).returncode == 0
    if not ready:
        subprocess.run([sys.executable, str(ROOT / 'framework/bootstrap.py'), '--install-only'], check=True)
    if Path(sys.prefix).resolve() != (ROOT / '.speaker-venv').resolve():
        os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.path.insert(0, str(ROOT))
    from framework.measurements.cli import main as cli_main
    cli_main()


if __name__ == '__main__':
    main()
