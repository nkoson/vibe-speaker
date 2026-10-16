import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import apps


def parameters():
    return dict(cavity=dict(width_mm=300, depth_mm=400, height_mm=500),
                driver=dict(ts=dict(sd_cm2=100), position=dict(x_mm=150, z_mm=350)),
                outlet=dict(type="port", inner_diameter_mm=40, outer_diameter_mm=44,
                            length_mm=100, internal_length_mm=80,
                            positions=[dict(face="left", y_mm=200, z_mm=100),
                                       dict(face="right", y_mm=200, z_mm=100)]))


def test_opposed_side_port_geometry_and_odd_mode_cancellation():
    app = apps.module("cavity_modes")
    g = app._geometry(parameters())
    np.testing.assert_allclose(g["patches"], [[.08, .2, .1], [.22, .2, .1]])
    assert g["patch_axes"] == [0, 0]
    assert g["patch_signs"] == [1, -1]
    modes = app.rectangular_modes(g, 800)
    odd_x = np.all(modes["indices"] == [1, 0, 0], axis=1)
    assert np.count_nonzero(odd_x) == 1
    assert abs(modes["outlet"][odd_x][0]) < 1e-12
    assert modes["outlet"][0] == pytest.approx(1)


def test_circular_aperture_solid_union_and_bounds():
    app = apps.module("cavity_modes")
    brace = dict(z_mm=100, thickness_mm=27,
                 holes=[dict(x_mm=100, y_mm=150, diameter_mm=80)])
    pts = np.array([[.1, .15, .11], [.2, .15, .11], [.2, .15, .14]])
    mask = app.brace_solid_mask(brace, *pts.T, np.array([.3, .4, .5]))
    np.testing.assert_array_equal(mask, [False, True, False])
    brace["holes"][0]["diameter_mm"] = 500
    with pytest.raises(ValueError, match="beyond"):
        app.brace_solid_mask(brace, *pts.T, np.array([.3, .4, .5]))


@pytest.mark.parametrize("face", ["left", "right", "front", "rear"])
def test_fvm_patch_is_on_fluid_side_of_duct_end(face):
    app = apps.module("cavity_modes")
    p = parameters()
    p["outlet"]["positions"] = [dict(face=face, x_mm=150, y_mm=200, z_mm=100)]
    g = app._geometry(p)
    modes = app.finite_volume_modes(g, 25, 350)
    assert np.all(np.isfinite(modes["outlet"]))
    assert abs(modes["outlet"][0]) == pytest.approx(1, abs=1e-7)
    assert modes["modeled_air_volume_l"] < 60
