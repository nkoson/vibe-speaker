"""Explicitly regenerate independent mathematical exports; never run during tests.

No production simulation imports are permitted here.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy import signal


def generate(destination=None):
    root = Path(destination or Path(__file__).with_name("reference_exports"))
    root.mkdir(parents=True, exist_ok=True)
    f = np.geomspace(10, 40000, 241)
    cases = []
    for name, numerator, denominator, parameters in [
        ("rc_lowpass", [1], [8 * 20e-6, 1], {"resistance_ohm": 8, "capacitance_f": 20e-6}),
        ("rlc_lowpass", [1], [.001 * 20e-6, 8 * 20e-6, 1],
         {"resistance_ohm": 8, "inductance_h": .001, "capacitance_f": 20e-6}),
    ]:
        _, h = signal.freqresp(signal.TransferFunction(numerator, denominator), w=2*np.pi*f)
        path = root / (name + ".csv")
        np.savetxt(path, np.c_[f, h.real, h.imag], delimiter=",",
                   header="frequency_hz,real,imag", comments="", fmt="%.17g")
        cases.append(dict(id=name, file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          evidence_class="independent_numerical", quantity="voltage_transfer",
                          units="V/V", parameters=parameters, numerator=numerator, denominator=denominator,
                          conditions={"phasor": "exp(+jwt)", "source_voltage_rms": 1},
                          source="scipy.signal.freqresp continuous-time rational system"))
    # The exact two-source sum deliberately does not use a propagation helper.
    angle = np.array([-60, -30, 0, 30, 60])
    h = 2 * np.cos(2*np.pi*f[None, :]/343 * .1 * np.sin(np.deg2rad(angle[:, None])))
    path = root / "two_sources.csv"
    np.savetxt(path, np.c_[np.repeat(angle, len(f)), np.tile(f, len(angle)), h.ravel()],
               delimiter=",", header="angle_deg,frequency_hz,real", comments="", fmt="%.17g")
    cases.append(dict(id="two_sources", file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      evidence_class="analytical", quantity="normalized_pressure", units="1",
                      conditions={"spacing_m": .2, "speed_of_sound_m_s": 343, "distance": "far field"},
                      source="2 cos(k d sin(theta)/2), coherent identical monopoles"))
    manifest = dict(schema_version=1, generator="generate_reference_exports.py",
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    engine={"name": "SciPy", "version": scipy.__version__},
                    interpretation="Simulated mathematical references; no empirical accuracy claim.", cases=cases)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    generate()
