import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from carrier_templates import audit, export
from pcb_rails import compile_layout
from wire_assembly import route_metrics
from test_wire_assembly import sample


def test_through_carrier_length_is_used_in_electrical_netlist():
    layout, circuit = sample()
    layout['boards'][0]['parts'][0]['leads'][0]['length_mm'] = 57
    _, rows, _ = compile_layout(layout, circuit)
    lead = next(r for r in rows if r['id'] == 'R1-lead-1')
    assert lead['length_mm'] == 57
    assert lead['resistance_ohm'] == pytest.approx(.0175 * .057 / .5 + .0005)
    report=route_metrics(layout)['totals']
    assert report['native_lead_route_mm']==132
    assert report['internal_conductor_path_mm']==232


def test_carrier_hole_audit_rejects_overlapping_passages():
    b = {'id': 'B', 'size_mm': [220, 390, 5], 'parts': [{}],
         'drill_holes': [dict(id='1', kind='lead', center=[30,30], diameter=3.5),
                         dict(id='2', kind='lead', center=[32,30], diameter=3.5)]}
    with pytest.raises(ValueError, match='ligament'):
        audit({'boards': [b]})


def test_carrier_exports_real_millimetre_geometry_and_print_sizes(tmp_path):
    from pypdf import PdfReader
    import ezdxf
    b = {'id': 'B', 'size_mm': [220, 390, 5], 'holes': [], 'rails': [], 'terminals': {},
         'parts': [dict(id='R', type='R', x=50, y=50, body_w=20, body_h=10,
                       leads=[dict(hole=[30,50],under_points=[[30,50],[20,50]],points=[[40,50],[20,50]],rail='A',length_mm=30),
                              dict(hole=[70,50],under_points=[[70,50],[80,50]],points=[[60,50],[80,50]],rail='B',length_mm=30)])],
         'drill_holes': [dict(id='1', kind='lead', center=[30,50], diameter=3.5),
                         dict(id='2', kind='lead', center=[70,50], diameter=3.5)]}
    export({'boards':[b], 'revision':'T'}, tmp_path)
    doc=ezdxf.readfile(tmp_path/'B-drilling.dxf')
    assert doc.units==4
    assert sorted((e.dxf.center.x,e.dxf.center.y,e.dxf.radius) for e in doc.modelspace().query('CIRCLE'))==[(30,50,1.75),(70,50,1.75)]
    pdf=PdfReader(tmp_path/'drilling-templates-A3.pdf')
    assert float(pdf.pages[0].mediabox.width)*25.4/72==pytest.approx(297,abs=.01)
    assert float(pdf.pages[0].mediabox.height)*25.4/72==pytest.approx(420,abs=.01)
    rectangles=[args for args,op in pdf.pages[0].get_contents().operations if op==b're']
    assert any(abs(float(r[2])*25.4/72-220)<.01 and abs(float(r[3])*25.4/72-390)<.01 for r in rectangles)
    assert len(PdfReader(tmp_path/'drilling-templates-A4-tiled.pdf').pages)==4
