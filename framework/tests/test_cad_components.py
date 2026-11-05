"""Mounting geometry, transformed drawings and printable solid connectivity."""
import sys
from pathlib import Path
import math
import pytest
import cadquery as cq
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cad_components import make_component, projection_entities, interface_offsets
from cad_drawings import make_part, place_part


def test_radial_slot_preserves_flange_and_passes_screw():
    shape = make_component({'operations': [
        dict(kind='revolve', profile=[[20,0],[40,0],[40,-6],[20,-6]]),
        dict(kind='slot', origin=[30,0,1], length=9.5, width=7.4,
             depth=-8, operation='cut'),
    ]})
    area = (9.5-7.4)*7.4 + math.pi*3.7**2
    assert shape.Volume() == pytest.approx(math.pi*(40**2-20**2)*6 - area*6)
    assert len(shape.Solids()) == 1
    assert not shape.isInside(cq.Vector(30,0,-3))
    assert shape.isInside(cq.Vector(30,5,-3))


def test_hollow_transition_and_blind_mounting_pilot():
    shape = make_part(dict(solid_model={'operations': [
        dict(kind='loft', sections=[dict(z=0,radius=30),dict(z=-40,radius=12)]),
        dict(kind='cylinder', radius=5, length=42, origin=[0,0,1], operation='cut'),
        dict(kind='cylinder', radius=2.5, length=8, origin=[20,0,0], operation='cut'),
    ]}))
    assert len(shape.Solids()) == 1
    assert not shape.isInside(cq.Vector(0,0,-20))
    assert not shape.isInside(cq.Vector(20,0,-7))
    assert shape.isInside(cq.Vector(20,0,-9))
    placed = place_part(shape,dict(origin=[100,13,200],x_dir=[1,0,0],normal=[0,-1,0]))
    bb = placed.BoundingBox()
    assert [bb.ymin,bb.ymax] == pytest.approx([13,53], abs=1e-5)


def test_projection_uses_named_frame_and_physical_dimensions():
    s = cq.Workplane('XY').box(20,10,4,centered=False).val()
    result = projection_entities({'s':s},dict(parts=['s'],origin=[0,0,0],normal=[0,0,1],x_dir=[1,0,0]))
    points = [p for e in result for p in e['points']]
    assert max(p[0] for p in points)-min(p[0] for p in points) == pytest.approx(20)
    assert max(p[1] for p in points)-min(p[1] for p in points) == pytest.approx(10)
    assert {e['layer'] for e in result} == {'OUTLINE'}
    report = interface_offsets([[50.8,0],[0,50.8]], [[51,0],[0,51]])
    assert [v['offset_mm'] for v in report] == pytest.approx([.2,.2])
    with pytest.raises(ValueError):
        interface_offsets([],[[0,0]])


def test_projected_circular_edges_close():
    shape = cq.Solid.makeCylinder(20, 5)
    result = projection_entities({'ring':shape}, dict(parts=['ring'],
        origin=[0,0,0], normal=[0,0,1], x_dir=[1,0,0]))
    curves = [e['points'] for e in result if len(e['points'])>4]
    assert curves
    for points in curves:
        assert points[0] == pytest.approx(points[-1], abs=1e-6)


def test_component_requires_requested_printable_solid_count():
    with pytest.raises(ValueError, match='solid count'):
        make_component(dict(expected_solids=1, operations=[
            dict(kind='box', size=[5,5,5]),
            dict(kind='box', size=[5,5,5], origin=[20,0,0]),
        ]))


def test_periodic_loft_step_round_trip(tmp_path):
    from cad_drawings import export_solids
    sections=[]
    for z,r in [(0,20),(-10,16),(-30,8)]:
        sections.append(dict(z=z, spline_points=[
            [r*math.cos(i*math.pi/8), .7*r*math.sin(i*math.pi/8)] for i in range(16)]))
    spec=dict(meta=dict(drawing_prefix='T'),parts=[dict(id='flare',
        solid_model=dict(expected_solids=1,operations=[
            dict(kind='loft',sections=sections,ruled=True),
            dict(kind='cylinder',radius=3,length=32,origin=[0,0,1],operation='cut')]),
        placements=[dict(origin=[0,0,0])])])
    shapes,report=export_solids(spec,tmp_path)
    assert report[0]['solid_count']==1
    assert report[0]['volume_integration_tolerance']==1e-5
    assert abs(report[0]['step_volume_difference_mm3'])<report[0]['volume_mm3']*1e-6
    assert not shapes['flare'].isInside(cq.Vector(0,0,-15))


def test_primitive_scaling_precedes_print_orientation():
    from cad_components import primitive
    shape=primitive(dict(kind='box',size=[20,10,4],origin=[0,0,-4],scale=.1,
        rotate=dict(start=[0,0,0],end=[1,0,0],degrees=180)))
    bb=shape.BoundingBox()
    assert [bb.xlen,bb.ylen,bb.zlen,bb.zmin]==pytest.approx([2,1,.4,0],abs=1e-6)
    with pytest.raises(ValueError,match='positive'):
        primitive(dict(kind='cylinder',radius=1,length=2,scale=0))


def test_filling_internal_voids_preserves_open_bores():
    shell_ops=[dict(kind='box',size=[10,10,10]),
               dict(kind='box',size=[6,6,6],origin=[2,2,2],operation='cut')]
    hollow=make_component(dict(operations=shell_ops))
    filled=make_component(dict(operations=shell_ops,fill_internal_voids=True))
    assert len(hollow.Shells())==2 and len(filled.Shells())==1
    assert filled.Volume()==pytest.approx(1000)
    open_ops=[dict(kind='box',size=[10,10,10]),
              dict(kind='cylinder',radius=2,length=12,origin=[5,5,11],operation='cut')]
    open_part=make_component(dict(operations=open_ops,fill_internal_voids=True))
    assert not open_part.isInside(cq.Vector(5,5,5))
    assert open_part.Volume()==pytest.approx(1000-math.pi*4*10)
