"""Penalties must constrain the actual acoustic/terminal quantities, not LC products."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'simulations'))
from _common import apps, cli

def test_relative_constraint_removes_absolute_calibration():
    mod=apps.module('crossover_fit');f=np.array([40.,100.,500.,1000.])
    spec=[dict(quantity='acoustic_relative_db',band_hz=[40,100],reference_band_hz=[500,1000],minimum=-3,weight=2)]
    r,d=mod.constraint_penalties(spec,f,np.array([84.,89.,90.,92.]),[],np.empty((0,4)))
    rr,dd=mod.constraint_penalties(spec,f,np.array([104.,109.,110.,112.]),[],np.empty((0,4)))
    assert r.tolist()==[8.,0.]
    assert np.array_equal(r,rr) and d==dd
    assert d[0]['margins']==[-4.]

def test_handover_penalty_fits_known_resistive_divider(tmp_path):
    for name,level in [('lf',90),('hf',100)]:
        source={'name':name,'frequencies':{'min_hz':20,'max_hz':20000,'points':80},
                'acoustic':{'kind':'bandwidth_prior','sensitivity_db_2v83_1m':level},
                'impedance':{'kind':'resistive','r_ohm':8},'directivity':{'kind':'omni'}}
        cli.write_document(tmp_path/(name+'.json'),{'results':apps.module('source_response').compute(source,tmp_path)})
    sections=[{'name':'lf','source':{'file':'lf.json'},'elements':[]},
              {'name':'hf','source':{'file':'hf.json'},'elements':[{'id':'pad','type':'R','position':'series','value_ohm':1,'fit':{'min':.1,'max':80}}]}]
    p={'sections':sections,'frequencies':{'min_hz':100,'max_hz':10000,'points':80},
       'fit_frequencies':{'min_hz':500,'max_hz':2000,'points':40},'max_nfev':60,
       'system':{'observer':{'distance_m':1,'ear_height_m':1},'sections':[
           {'name':s['name'],'source':s['source'],'position':{'x_mm':0,'z_mm':1000}} for s in sections]},
       'target':{'spl_db':100,'band_hz':[500,2000],'vertical_angles_deg':[0],
                 'constraints':[{'quantity':'section_difference_db','section_indices':[0,1],
                                 'band_hz':[500,2000],'minimum':0,'maximum':0,'weight':100}]}}
    r=apps.module('crossover_fit').compute(p,tmp_path)
    value=r['fitted_values'][0]['fitted']
    assert value==pytest.approx(8*(10**.5-1),rel=.01)
    assert max(abs(x) for x in r['constraint_diagnostics'][0]['margins'])<.01

def test_terminal_voltage_uses_declared_stress_drive():
    f=np.array([100.,200.,1000.]);t=np.array([.01,.1,.5])
    r,d=apps.module('crossover_fit').constraint_penalties(
        [{'quantity':'terminal_voltage_rms','section_index':0,'band_hz':[100,200],
          'drive_voltage_rms':20,'maximum':1,'weight':1}],f,np.zeros(3),[t],np.zeros((1,3)))
    assert r.tolist()==[0.,1.]
    assert d[0]['margins']==[-1.]
