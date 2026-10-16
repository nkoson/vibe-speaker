"""Fresh simulation evidence shared by every test module that reads example results."""
import subprocess
import sys
from pathlib import Path
import pytest
HARNESS=Path(__file__).resolve().parents[1]

@pytest.fixture(scope="session", autouse=True)
def chain():
    proc = subprocess.run([sys.executable, str(HARNESS / "simulations" / "examples" / "run_examples.py")], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout
