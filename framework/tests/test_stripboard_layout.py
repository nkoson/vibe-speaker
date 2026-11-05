"""Electrical and geometric invariants of the stock-strip realization tool."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
from stripboard_layout import compile_circuit, body_distance, inspect


def fixture():
    p=dict(id='R',center_mm=[10,10],reserve_mm=[4,8,5],footprint_mm=[4,8],
           body=dict(kind='box',center_mm=[10,10,3],size_mm=[4,8,4]),nodes=['P','N'],
           leads=[dict(pad=[1,2],points_mm=[[10,6,3],[5,0,-1]],solder_tail_mm=2),
                  dict(pad=[5,2],points_mm=[[10,14,3],[5,20,-1]],solder_tail_mm=2)])
    layout=dict(size_mm=[30,30,1],grid=dict(origin_mm=[0,0],pitch_mm=5),rows={'P':1,'N':5},
                parts=[p],holes=[],harness=[dict(id='amp',node='IN',pad=[1,5],resistance_ohm=.01)],copper_ohm_per_mm=.001)
    circuit=dict(components=[dict(id='R',type='R',nodes=['RA','RB'],value_ohm=10)],wires=[{'id':'obsolete'}])
    return layout,circuit


def test_segment_and_native_losses_do_not_duplicate_previous_wiring():
    layout,circuit=fixture();out,_=compile_circuit(layout,circuit,2)
    assert out['components']==circuit['components']
    assert len(out['wires'])==4
    wire={w['id']:w for w in out['wires']}
    assert wire['copper_R1_2_5']['resistance_ohm']==pytest.approx(.03)
    assert wire['lead_R_1']['resistance_ohm']==pytest.approx(.0175*(np.sqrt(77)+2)/1000/.5+.001)
    assert wire['lead_R_1']['from']=='RA' and wire['lead_R_1']['to']=='R01C02'


def test_distinct_nodes_cannot_share_an_uncut_strip():
    layout,_=fixture();layout['rows']['N']=1
    with pytest.raises(ValueError,match='distinct continuous strips'):inspect(layout)


def test_cut_harness_length_replaces_the_resistance_allowance():
    layout,circuit=fixture()
    layout['harness'][0].update(length_mm=600,section_mm2=1.5)
    out,_=compile_circuit(layout,circuit)
    assert next(w for w in out['wires'] if w['id']=='amp')['resistance_ohm']==pytest.approx(.009)


def test_route_and_pad_must_agree_in_three_dimensions():
    layout,_=fixture();layout['parts'][0]['leads'][0]['points_mm'][-1][2]=1
    with pytest.raises(ValueError,match='copper pad'):inspect(layout)


def test_insulated_route_under_a_cylinder_is_not_a_plan_overlap_collision():
    body=dict(kind='cylinder',center_mm=[0,0,8],radius_mm=5,length_mm=20,axis='Y')
    assert body_distance([[0,0,1],[0,0,8],[0,11,8]],body)==pytest.approx([2,-5,1])
