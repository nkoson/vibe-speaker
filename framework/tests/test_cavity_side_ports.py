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


def test_inner_flare_patch_is_distinct_from_throat():
    app = apps.module("cavity_modes")
    p = parameters()
    p["outlet"].update(inner_mouth_diameter_mm=70, inner_flare_outer_diameter_mm=90,
                       inner_flare_length_mm=20)
    g = app._geometry(p)
    assert g["outlet_radius"] == .02
    assert g["outlet_patch_radius"] == .035
    r = app.finite_volume_modes(g, 25, 350)
    assert np.all(np.isfinite(r["outlet"]))
    assert abs(r["outlet"][0]) == pytest.approx(1, abs=1e-7)


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


def test_rounded_aperture_area_and_edge_relief():
    app = apps.module('cavity_modes')
    # Integrate a 120 x 80, R10 opening on a 0.5 mm grid.
    x=(np.arange(600)+.5)*.0005;y=(np.arange(800)+.5)*.0005
    X,Y=np.meshgrid(x,y,indexing='ij');Z=np.full_like(X,.11)
    hole=dict(shape='rounded_rectangle',x_mm=50,y_mm=70,width_mm=120,height_mm=80,corner_radius_mm=10)
    b=dict(z_mm=100,thickness_mm=27,holes=[hole])
    solid=app.brace_solid_mask(b,X,Y,Z,np.array([.3,.4,.5]))
    assert np.count_nonzero(~solid)*.5**2 == pytest.approx(120*80-(4-np.pi)*10**2,abs=5)
    b['reliefs']=[dict(shape='rounded_rectangle',x_mm=100,y_mm=-10,width_mm=80,height_mm=35)]
    pts=np.array([[.13,.01,.11],[.13,.03,.11],[.13,.01,.15]])
    np.testing.assert_array_equal(app.brace_solid_mask(b,*pts.T,np.array([.3,.4,.5])),[False,True,False])


def test_vertical_internal_panel_open_curved_top():
    app=apps.module('cavity_modes')
    p=dict(normal_axis='y',start_mm=200,thickness_mm=27,origin_uv_mm=[50,250],size_uv_mm=[200,150],
           reliefs=[dict(x_mm=150,y_mm=390,diameter_mm=180),dict(shape='rounded_rectangle',x_mm=60,y_mm=390,width_mm=180,height_mm=10)])
    pts=np.array([[.15,.21,.28],[.15,.21,.35],[.055,.21,.38],[.15,.24,.28]])
    np.testing.assert_array_equal(app.panel_solid_mask(p,*pts.T,np.array([.3,.4,.5])),[True,False,True,False])
