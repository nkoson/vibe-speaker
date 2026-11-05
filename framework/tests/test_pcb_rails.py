import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('pcb_rails',Path(__file__).parents[1]/'tools/pcb_rails.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    return {'boards':[{'id':'B','size_mm':[80,60,1.6],'rails':[{'id':'P','net':'P','points':[[5,5],[5,55]],'section_mm2':5,'width_mm':5},{'id':'N','net':'N','points':[[75,5],[75,55]],'section_mm2':5,'width_mm':5}], 'holes':[], 'terminals':{}, 'parts':[{'id':i,'x':40,'y':y,'body_w':20,'body_h':8,'restraint_holes_mm':[],'leads':[{'rail':'P','points':[[30,y],[5,y]]},{'rail':'N','points':[[50,y],[75,y]]}]} for i,y in [('R1',20),('R2',40)]]}], 'logical_components':{'R1':['P','N'],'R2':['P','N']},'harness':[]}, {'components':[{'id':i,'type':'R','nodes':[i+'A',i+'B'],'value_ohm':10} for i in ['R1','R2']], 'wires':[]}

def test_shared_rail_splits_at_taps_and_conserves_length():
    layout,circuit=fixture();board,rows,audit=m.compile_layout(layout,circuit)
    assert audit['shorted_logical_nodes']==audit['disconnected_logical_nodes']==[]
    assert sum(r['length_mm'] for r in rows if r['kind']=='rail')==100
    assert len([r for r in rows if r['kind']=='rail'])==6
    assert all(w['resistance_ohm']>0 for w in board['wires'])

def test_disconnected_same_name_rail_is_not_implicitly_joined():
    layout,circuit=fixture();b=layout['boards'][0]
    b['rails'].append({'id':'P2','net':'P','points':[[10,5],[10,55]],'section_mm2':5,'width_mm':5})
    b['parts'][1]['leads'][0]={'rail':'P2','points':[[30,40],[10,40]]}
    _,_,audit=m.compile_layout(layout,circuit)
    assert audit['disconnected_logical_nodes'][0]['net']=='P'

def test_invalid_tap_rejected():
    import pytest
    layout,circuit=fixture();layout['boards'][0]['parts'][0]['leads'][0]['points'][-1]=[6,20]
    with pytest.raises(ValueError,match='outside'):m.compile_layout(layout,circuit)
