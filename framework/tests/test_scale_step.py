"""Independent checks for source-preserving STEP scaling and installed poses."""
import sys
from pathlib import Path
import cadquery as cq
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from scale_step import build, mesh_report, wall_samples


def test_scale_rebuilds_assembly_from_scaled_parts_and_poses(tmp_path):
    source=tmp_path/'source';source.mkdir()
    shape=cq.Workplane('XY').box(100,40,20,centered=False).val()
    cq.exporters.export(shape,str(source/'part.step'))
    old=(source/'part.step').read_bytes()
    manifest=dict(parts=[dict(id='part',placements=[
        dict(origin=[100,200,300],x_dir=[1,0,0],normal=[0,0,1]),
        dict(origin=[500,200,300],x_dir=[1,0,0],normal=[0,0,1])])])
    report=build(source,manifest,tmp_path/'scaled',.08,min_wall_mm=.1)
    assert (source/'part.step').read_bytes()==old
    assert report['parts'][0]['bounds_mm']==pytest.approx([0,8,0,3.2,0,1.6],abs=1e-6)
    assert report['assembly']['bounds_mm']==pytest.approx([8,48,16,19.2,24,25.6])
    assert report['assembly']['solid_count']==2
    assert not report['parts'][0]['material_added']


def test_closed_ring_mesh_and_exact_surface_wall_samples():
    shape=cq.Workplane('XY').circle(5).circle(4).extrude(3).val()
    r=mesh_report(shape)
    assert r['open_edges']==r['nonmanifold_edges']==r['degenerate_triangles']==r['inconsistent_edges']==0
    assert r['connected_surfaces']==1
    samples=wall_samples(shape,2)
    assert min(x['thickness_mm'] for x in samples)==pytest.approx(1)


@pytest.mark.parametrize('replace',[False,True])
def test_added_material_stays_in_scaled_variant(tmp_path,replace):
    source=tmp_path/'source';source.mkdir()
    shape=cq.Workplane('XY').box(10,10,1,centered=False).val()
    cq.exporters.export(shape,str(source/'part.step'));old=(source/'part.step').read_bytes()
    manifest=dict(parts=[dict(id='part',placements=[dict(origin=[0,0,0])])])
    patches={'part':dict(operations=[dict(kind='box',size=[10,10,2],origin=[0,0,0])])}
    if replace:
        patches={'part':dict(mode='replace',solid_model=patches['part'])}
    result=build(source,manifest,tmp_path/'scaled',.08,patches,.1)
    assert result['parts'][0]['bounds_mm'][-1]==pytest.approx(.16)
    assert result['parts'][0]['material_added']
    assert (source/'part.step').read_bytes()==old


def test_refuses_output_over_sources(tmp_path):
    with pytest.raises(ValueError,match='separate'):
        build(tmp_path,{},tmp_path,.08)
