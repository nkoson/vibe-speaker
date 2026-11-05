import importlib.util, sys
from pathlib import Path
import pytest
TOOLS=Path(__file__).parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
from pcb_rails import compile_layout
from wire_assembly import route_metrics, construction_geometry

def sample():
    b={'id':'B','size_mm':[80,60,9],'holes':[], 'rails':[{'id':'P','net':'P','points':[[5,5],[5,55]],'width_mm':3,'section_mm2':1.5,'cut_length_mm':80},{'id':'N','net':'N','points':[[75,5],[75,55]],'width_mm':3,'section_mm2':1.5,'cut_length_mm':50}], 'terminals':{},'parts':[]}
    for id,y in [('R1',20),('R2',40)]:b['parts'].append({'id':id,'x':40,'y':y,'body_w':20,'body_h':8,'restraint_holes_mm':[],'leads':[{'rail':'P','points':[[30,y],[5,y]]},{'rail':'N','points':[[50,y],[75,y]]}]})
    layout={'boards':[b],'logical_components':{'R1':['P','N'],'R2':['P','N']},'harness':[]}
    circuit={'components':[{'id':id,'type':'R','nodes':[id+'A',id+'B'],'value_ohm':10} for id in ['R1','R2']],'wires':[]}
    return layout,circuit

def test_cut_length_is_electrical_length():
    layout,circuit=sample();board,rows,_=compile_layout(layout,circuit)
    copper=[r for r in rows if r['kind']=='rail']
    assert sum(r['length_mm'] for r in copper)==pytest.approx(130,abs=.002)
    assert sum(r['resistance_ohm'] for r in copper)==pytest.approx(.0175*.130/1.5)

def test_connected_pair_includes_both_leads_and_shared_path():
    layout,_=sample();report=route_metrics(layout)
    assert {r['plan_route_mm'] for r in report['connected_pairs']}=={70}
    assert report['totals']['bends']==0
    assert report['totals']['straight_runs']==2

def test_geometry_reports_crossing_for_agent_interpretation():
    layout,_=sample();layout['boards'][0]['rails'].append({'id':'X','net':'X','points':[[20,10],[20,30]],'width_mm':3,'section_mm2':1.5})
    report=construction_geometry(layout)
    assert report['lead_wire_crossings']==[{'board':'B','part':'R1','lead':1,'wire':'X'}]

def test_direct_lead_joint_joins_endpoints_without_added_wire():
    layout,circuit=sample();b=layout['boards'][0]
    b['rails'][0].update(points=[[5,30],[5,30]],kind='direct_joint',cut_length_mm=0)
    for c in b['parts']:c['leads'][0]['points'][-1]=[5,30]
    _,rows,audit=compile_layout(layout,circuit)
    assert audit['disconnected_logical_nodes']==[]
    assert route_metrics(layout)['totals']['direct_joint_count']==1
    assert route_metrics(layout)['totals']['node_wire_count']==1
    assert all(not r['id'].startswith('B-P') for r in rows)
