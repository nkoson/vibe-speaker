"""Compare Hz,real,imag CSV exports over their shared band; report differences only."""
import argparse
import hashlib
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import cli, comparison


def compare_files(actual, reference):
    a = np.loadtxt(actual, delimiter=",", skiprows=1)
    r = np.loadtxt(reference, delimiter=",", skiprows=1)
    for table in (a, r):
        if table.ndim != 2 or table.shape[1] != 3 or np.any(np.diff(table[:, 0]) <= 0):
            raise cli.InputError("export needs sorted unique frequency_hz,real,imag columns")
    inside = (a[:, 0] >= r[0, 0]) & (a[:, 0] <= r[-1, 0])
    f = a[inside, 0]
    result = comparison.compare(f, a[inside, 1]+1j*a[inside, 2],
                                cli.interp_complex(f, r[:, 0], r[:, 1]+1j*r[:, 2]))
    result["provenance"] = {name: dict(file=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
                            for name, path in (("actual", actual), ("reference", reference))}
    result["excluded_actual_points"] = int((~inside).sum())
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    cli.write_document(args.out, compare_files(args.actual, args.reference))
