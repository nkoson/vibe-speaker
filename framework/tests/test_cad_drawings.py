"""CAD geometry and interchange checks, independent of acoustic judgement."""
import importlib.util
import math
from pathlib import Path

import cadquery as cq
import ezdxf
import pytest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'cad_drawings.py'
spec = importlib.util.spec_from_file_location('cad_drawings', TOOL)
cad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cad)


def block(**changes):
    value = dict(id='panel', width=100, height=80, thickness=20, features=[], placements=[])
    value.update(changes)
    return value


def test_cut_volumes_and_entry_faces():
    p = block(features=[
        dict(id='bore', kind='circle', center=[25, 40], diameter=10, depth='through'),
        dict(id='blind', kind='circle', center=[75, 40], diameter=20, depth=6, face='inside'),
    ])
    shape = cad.make_part(p)
    expected = 100 * 80 * 20 - math.pi * 5**2 * 20 - math.pi * 10**2 * 6
    assert shape.Volume() == pytest.approx(expected)
    assert shape.isInside(cq.Vector(75, 40, -5))
    assert not shape.isInside(cq.Vector(75, 40, -18))
    assert not shape.isInside(cq.Vector(25, 40, -10))


def test_miter_volume_and_panel_datum_transform():
    shape = cad.make_part(block(miter=True))
    # Integrate (100 - 2*z) * (80 - 2*z) through the 20 mm depth.
    assert shape.Volume() == pytest.approx(100 * 80 * 20 - 180 * 20**2 + 4 / 3 * 20**3)
    located = cad.place_part(shape, dict(origin=[100, 200, 300], x_dir=[1, 0, 0], normal=[0, -1, 0]))
    bounds = located.BoundingBox()
    assert [bounds.xmin, bounds.xmax, bounds.ymin, bounds.ymax, bounds.zmin, bounds.zmax] == pytest.approx([100, 200, 200, 220, 300, 380])


def test_countersink_is_conical_not_counterbore():
    p = block(features=[
        dict(id='bore', kind='circle', center=[50, 40], diameter=4, depth='through'),
        dict(id='head', kind='countersink', center=[50, 40], diameter=8, bore=4, depth=2),
    ])
    shape = cad.make_part(p)
    conical_extra = math.pi * 2 / 3 * (4**2 + 4*2 + 2**2) - math.pi * 2**2 * 2
    assert shape.Volume() == pytest.approx(160000 - math.pi * 2**2 * 20 - conical_extra)


def test_native_dimension_units_and_step_round_trip(tmp_path):
    manifest = dict(meta=dict(title='Test cabinet', drawing_prefix='T', revision='A', date='2026-10-20'),
                    parts=[block(placements=[dict(origin=[0, 0, 0])])], sheets=[dict(
                        id='C1', title='Machining', views=[dict(id='panel', part='panel', at=[60, 100], scale=.5,
                        entities=[dict(kind='circle', center=[50, 40], radius=5, id='hole')],
                        dimensions=[dict(p1=[0, 0], p2=[100, 0], base=[0, -20])],
                        diameters=[dict(feature='hole', location=[120, 50])])])])
    result = cad.build(manifest, tmp_path, tmp_path/'drawing.pdf')
    dxf = ezdxf.readfile(tmp_path/'dxf/C1_panel.dxf')
    assert dxf.units == 4
    assert not dxf.audit().has_errors
    assert sorted(float(d.get_measurement()) for d in dxf.modelspace().query('DIMENSION')) == pytest.approx([10, 100])
    # Dimension blocks own their labels; no duplicate hand-drawn labels remain.
    assert len(dxf.modelspace().query('TEXT')) == 0
    labels = [text for dim in result['views'][0]['dimensions'] for text in dim['rendered_text']]
    assert labels == ['100', 'Ø10']
    # DXF dimensions and circles stay full size when the PDF uses a 1:2 view.
    assert next(iter(dxf.modelspace().query('CIRCLE'))).dxf.radius == 5
    reopened = cq.importers.importStep(str(tmp_path/'step/cabinet-assembly.step')).val()
    assert reopened.Volume() == pytest.approx(160000)
    assert result['views'][0]['scale'] == .5
    assert (tmp_path/'drawing.pdf').read_bytes().startswith(b'%PDF')


def test_rejects_blind_machining_deeper_than_panel():
    with pytest.raises(ValueError, match='invalid machining depth'):
        cad.make_part(block(features=[dict(id='bad', kind='circle', center=[50,40], diameter=10, depth=21)]))


def test_aperture_roundover_keeps_the_through_bore():
    feature = dict(id='bore', kind='circle', center=[50, 40], diameter=30, depth='through')
    plain = cad.make_part(block(features=[feature]))
    rounded = cad.make_part(block(features=[dict(feature, edge_radius=3)]))
    assert rounded.isValid()
    assert rounded.Volume() < plain.Volume()
    assert rounded.isInside(cq.Vector(66, 40, -10))
    assert not rounded.isInside(cq.Vector(66, 40, -.1))
