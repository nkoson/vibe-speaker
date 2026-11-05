import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).parents[1]/'simulations'))
from _common import apps


def mesh():
    return [np.array([0,.11,.3]),np.array([0,.07,.2]),np.array([0,.13,.4])],np.ones((2,2,2),bool)


def test_default_lining_recovers_five_wall_area():
    app=apps.module('cavity_modes');edges,fluid=mesh()
    b,areas=app.lining_boundary_area(edges,fluid,{})
    assert b.sum()==pytest.approx(2*.2*.4+.3*.4+2*.3*.2)
    assert areas['front']==0
    assert areas['rear']==pytest.approx(.12)


def test_subcell_patch_has_exact_area_and_modal_location():
    app=apps.module('cavity_modes');edges,fluid=mesh()
    b,areas=app.lining_boundary_area(edges,fluid,{'patches':[{'face':'rear','bounds_mm':[[20,210],[50,270]]}]})
    assert b.sum()==pytest.approx(.19*.22)
    assert areas['rear']==pytest.approx(.0418)
    # The rear four cell faces contain the partial rectangles; front faces get zero.
    a=b.reshape(fluid.shape)
    np.testing.assert_allclose(a[:,0,:],0)
    np.testing.assert_allclose(a[:,1,:],[[.09*.08,.09*.14],[.10*.08,.10*.14]])


def test_empty_coverage_and_obstructed_wall_cells():
    app=apps.module('cavity_modes');edges,fluid=mesh()
    b,_=app.lining_boundary_area(edges,fluid,{'patches':[]});assert b.sum()==0
    fluid[0,-1,0]=False
    b,areas=app.lining_boundary_area(edges,fluid,{'patches':[{'face':'rear','bounds_mm':[[0,300],[0,400]]}]})
    assert areas['rear']==pytest.approx(.12-.11*.13)


def test_overlapping_or_outside_patches_are_rejected():
    app=apps.module('cavity_modes');edges,fluid=mesh()
    p={'face':'rear','bounds_mm':[[0,100],[0,100]]}
    with pytest.raises(ValueError,match='overlap'):app.lining_boundary_area(edges,fluid,{'patches':[p,p]})
    with pytest.raises(ValueError,match='outside'):app.lining_boundary_area(edges,fluid,{'patches':[{'face':'top','bounds_mm':[[0,301],[0,100]]}]})
