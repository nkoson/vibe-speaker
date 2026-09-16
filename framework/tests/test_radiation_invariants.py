"""Physical amplitude/phase invariants for exterior propagation."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import radiation, acoustics


def section(f, pressure=1.0):
    return dict(name="test", pressure=np.full(len(f), pressure, complex),
                baffle=np.ones(len(f), complex), transfer=np.ones(len(f), complex),
                centre=np.array([0., 0., 1.]), directivity={"kind": "omni"},
                tilt_rad=0., outlets=[])


def test_reference_distance_preserves_one_metre_equivalent_pressure():
    f = np.array([30., 1000.])
    for distance in [1., 3., 10.]:
        pressure, _ = radiation.pressure([section(f)], f, [[0., distance, 1.]], distance)
        np.testing.assert_allclose(pressure, [[1., 1.]], atol=1e-12)


@pytest.mark.parametrize("reflection", [None, 0.7])
def test_rear_outlet_matches_monopole_distance_phase_and_floor_image(reflection):
    f = np.array([20., 40., 100.])
    source = section(f, pressure=0.)
    source["outlets"] = [dict(pressure=np.ones(len(f), complex),
                              baffle=np.full(len(f), .5, complex), face="rear",
                              centre=np.array([0., -.33, 1.]),
                              directivity={"kind": "omni"})]
    pressure, _ = radiation.pressure([source], f, [[0., 3., 1.]], 3., floor_reflection=reflection)
    def expected(distance):
        return .5 * 3. / distance * np.exp(-2j * np.pi * f / acoustics.C * (distance - 3.))
    reference = expected(3.33)
    if reflection:
        reference += reflection * expected(np.hypot(3.33, 2.))
    np.testing.assert_allclose(pressure[0], reference, atol=1e-12)
