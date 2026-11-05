"""Independent circuit identities, metadata replay and advisory load evidence."""
import copy
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'simulations'))
from _common import apps, cli, electrical_load, acoustics

TS = dict(fs_hz=55, vas_l=18, qms=4.5, qes=.48, re_ohm=5.7, sd_cm2=135, le_mh=.42)
F = np.geomspace(40, 18000, 91)


def save(path, results, inputs=None):
    cli.write_document(path, dict(status='computed', inputs=inputs or {}, results=results))


def source(tmp_path, load=None):
    p = dict(name='driver', frequencies={'values_hz': F.tolist()},
             acoustic=dict(kind='bandwidth_prior', sensitivity_db_2v83_1m=90),
             impedance=load or dict(kind='resistive', r_ohm=8), directivity={'kind': 'omni'})
    result = apps.module('source_response').compute(p, tmp_path)
    save(tmp_path / 'source.json', result, p)
    return result


@pytest.mark.parametrize('kind', ['constant', 'leach', 'lr2', 'semi_inductance'])
@pytest.mark.parametrize('topology', ['series', 'lowpass', 'parallel_series'])
def test_independent_divider_and_nodal_agree_for_each_load(kind, topology, tmp_path):
    s = 2j*np.pi*F
    models = dict(constant=dict(kind='constant', le_mh=.42), leach=dict(kind='leach', k=.024, n=.64),
                  lr2=dict(kind='lr2', le_mh=.11, l2_mh=.65, r2_ohm=4.2),
                  semi_inductance=dict(kind='semi_inductance', leb_mh=.08, le_mh=.5, ke=.08, rss_ohm=15))
    independent = dict(constant=5.7+s*.00042, leach=5.7+.024*s**.64,
        lr2=5.7+s*.00011+(s*.00065*4.2)/(s*.00065+4.2),
        semi_inductance=5.7+s*.00008+1/(1/(s*.0005)+1/(.08*np.sqrt(s))+1/15))
    load = dict(kind='blocked', ts=dict(TS, inductance_model=models[kind]))
    z = independent[kind]
    zs = .27+s*.0012
    components = [dict(id='L', type='L', value_mh=1.2, dcr_ohm=.27, nodes=['in', 'out'])]
    elements = [dict(components[0], position='series')]
    if topology == 'parallel_series':
        zc = .03+1/(s*1.1e-6)
        zs = zs*zc/(zs+zc)
        c = dict(id='Cp', type='C', value_uf=1.1, esr_ohm=.03, nodes=['in', 'out'])
        components.append(c)
        elements = [dict(id='group', type='parallel', position='series', parts=[elements[0], c])]
    after = z
    if topology == 'lowpass':
        zc = .02+1/(s*8.2e-6)
        after = z*zc/(z+zc)
        c = dict(id='C', type='C', value_uf=8.2, esr_ohm=.02, nodes=['out', '0'])
        components.append(c)
        elements.append(dict(c, position='shunt'))
    expected = after/(zs+after)
    p = dict(frequencies={'values_hz': F.tolist()}, sections=[dict(name='driver', load=load, elements=elements)])
    ladder = apps.module('crossover_network').compute(p, tmp_path)
    board = apps.module('board_nodal').compute(dict(frequencies=p['frequencies'], components=components,
        sources=[dict(id='amp', plus='in', minus='0', voltage_rms=2.83)],
        loads=[dict(id='driver', plus='out', minus='0', impedance=load)]), tmp_path)
    np.testing.assert_allclose(ladder['sections'][0]['transfer'], expected, rtol=2e-12)
    np.testing.assert_allclose(board['modes'][0]['loads'][0]['transfer'], expected, rtol=2e-12)
    assert np.min(z.real) >= 0


def test_evidence_gaps_and_missing_phase_are_observations(tmp_path):
    (tmp_path/'magnitude.zma').write_text('100 6\n1000 9\n10000 20\n')
    z, record = electrical_load.resolve(dict(kind='zma_file', file='magnitude.zma'), F, tmp_path)
    assert np.all(np.isfinite(z))
    assert record['phase_basis'] == 'assumed_zero_missing_phase'
    assert record['extrapolated_points'] > 0
    assert record['observations']['missing_evidence']
    assert record['supported_band_hz'] is None
    z, record = electrical_load.resolve(dict(kind='free_air', ts=TS), F, tmp_path)
    assert record['inductance_model'] == {'kind': 'constant', 'le_mh': .42}
    assert 'legacy_constant_inductance_from_ts' in record['assumptions']
    assert not {'acceptable', 'pass', 'fail', 'qualified'} & record.keys()


def test_cold_roundtrip_preserves_load_and_separate_acoustic_contract(tmp_path):
    p = dict(driver=dict(ts=dict(TS, inductance_model=dict(kind='lr2', le_mh=.1, l2_mh=.8, r2_ohm=5)),
        electrical_load=dict(identity='fixture-driver', evidence=['synthetic primitive equations'], supported_band_hz=[80, 12000])),
        enclosure=dict(type='sealed', net_volume_l=12), frequencies={'values_hz': F.tolist()})
    box = apps.module('lf_box').compute(p, tmp_path)
    save(tmp_path/'box.json', box, p)
    src = source(tmp_path, dict(kind='reference', reference=dict(file='box.json', path='results.curves.0.z_ohm')))
    np.testing.assert_allclose(src['z_ohm'], box['curves'][0]['z_ohm'], rtol=1e-12)
    contract = src['source_contract']['electrical_load']
    assert contract['identity'] == 'fixture-driver'
    assert contract['supported_band_hz'] == [80, 12000]
    assert contract['observations']['outside_supported_band_points'] > 0
    section = dict(name='driver', source={'file': 'source.json'}, elements=[dict(id='R', type='R', position='series', value_ohm=2)])
    net = apps.module('crossover_network').compute(dict(frequencies=p['frequencies'], sections=[section]), tmp_path)
    save(tmp_path/'network.json', net)
    whole = apps.module('whole_speaker').compute(dict(frequencies=p['frequencies'], observer=dict(horizontal_angles_deg=[], vertical_angles_deg=[]),
        sections=[dict(name='driver', source={'file': 'source.json'}, position=dict(z_mm=1000),
                       transfer=dict(file='network.json', path='results.sections.0.transfer'))]), tmp_path)
    assert whole['electrical_loads'][0]['transfer_load']['identity'] == 'fixture-driver'
    assert whole['electrical_loads'][0]['source_load']['inductance_model']['kind'] == 'lr2'
    # Re-read serialized source in a fresh resolution, including an explicit load override.
    z, _, again = electrical_load.section(section, F, tmp_path)
    np.testing.assert_allclose(z, src['z_ohm'], rtol=1e-12)
    assert again['identity'] == contract['identity']
    _, _, changed = electrical_load.section(dict(section, load=dict(kind='resistive', r_ohm=4)), F, tmp_path)
    assert changed['identity'] != contract['identity']
    assert changed['transformations'][-1]['previous_identity'] == contract['identity']


def test_identification_holdout_excluded_and_circuit_residual_visible(tmp_path):
    f = np.geomspace(20, 15000, 101); s = 2j*np.pi*f
    known = dict(mms_kg=.025, cms_m_per_n=.0007, rms_ns_m=1.4, bl_tm=7, re_ohm=5.7)
    z = 5.7+s*.00042+49/(1.4+s*.025+1/(s*.0007))
    held = np.arange(1, len(f), 2)
    contaminated = z.copy(); contaminated[held] += 3+2j
    p = dict(sd_cm2=135, known=known, initial=dict(le_h=.0002), bounds=dict(le_h=[.00001,.002]),
        observations=[dict(frequency_hz=f, real=contaminated.real, imag=contaminated.imag, held_out_indices=held.tolist())],
        audit_bands=[dict(name='handover', band_hz=[800, 5000])],
        transfer_audits=[dict(name='lowpass', elements=[dict(id='L', position='series', type='L', value_mh=1.2, dcr_ohm=.3)])])
    out = apps.module('parameter_identification').compute(p, tmp_path)
    assert out['parameters']['le_h'] == pytest.approx(.00042, rel=1e-7)
    audit = out['fit_diagnostics']['observations'][0]
    fit, heldout = audit['residual_bands']
    assert fit['complex_rms_ohm'] < 1e-7
    assert heldout['complex_rms_ohm'] == pytest.approx(np.sqrt(13))
    assert np.max(abs(audit['transfer_audits'][0]['transfer_difference_db'])) > .1
    # Exported fit is directly consumable, retaining the electrical model.
    actual, contract = electrical_load.resolve(out['impedance_model'], f, tmp_path)
    np.testing.assert_allclose(actual, z, rtol=1e-8)
    assert contract['fit_band_hz'] == [20, 15000]
    assert contract['supported_band_hz'] is None


def fitter_input(tmp_path, nodal):
    source(tmp_path)
    alternative=dict(name='alternate', loads={'driver':dict(kind='resistive', r_ohm=4)}, basis='controlled electrical probe')
    if nodal:
        return dict(network=dict(frequencies={'values_hz': F.tolist()}, components=[dict(id='R',type='R',value_ohm=6,nodes=['in','out'])],
            sources=[dict(id='amp',plus='in',minus='0',voltage_rms=2.83)],
            loads=[dict(id='driver',plus='out',minus='0',impedance=dict(file='source.json',path='results.z_ohm'))]),
            variables=[dict(id='R',bounds=[1,20],stock=[dict(value_ohm=v) for v in [4,6,8]])],
            target=dict(transfers=[dict(load_id='driver',band_hz=[100,10000],db=20*np.log10(.5))]),
            load_scenarios=[alternative], max_evaluations=60)
    return dict(frequencies={'values_hz': F.tolist()},fit_frequencies={'values_hz':F.tolist()},
        sections=[dict(name='driver',source={'file':'source.json'},elements=[dict(id='R',type='R',position='series',value_ohm=6,
            fit=dict(min=1,max=20),stock=[dict(value_ohm=v) for v in [4,6,8]])])],
        system=dict(observer=dict(distance_m=1,ear_height_m=1),sections=[dict(name='driver',source={'file':'source.json'},position=dict(z_mm=1000))]),
        target=dict(spl_db=90+20*np.log10(.5),band_hz=[100,10000]), load_scenarios=[alternative],max_nfev=60)


@pytest.mark.parametrize('nodal', [False, True])
def test_fit_alternatives_change_explicit_objective_and_report_stress(tmp_path, nodal):
    p=fitter_input(tmp_path,nodal)
    app=apps.module('network_fit' if nodal else 'crossover_fit')
    nominal=app.compute(p,tmp_path)
    robust=app.compute(dict(p,load_scenario_objective={'mode':'weighted_mean'}),tmp_path)
    if nodal:
        n=nominal['trials'][nominal['numerical_minimum_index']]
        r=robust['trials'][robust['numerical_minimum_index']]
        nv,rv=n['values'][0],r['values'][0]
        for trial in robust['trials']:
            expected=np.mean([(20*np.log10(load/(load+trial['values'][0]))-20*np.log10(.5))**2 for load in [8,4]])
            assert trial['cost'] == pytest.approx(expected,abs=1e-10)
        assert r['load_scenarios'][1]['components_stress'][0]['max_power_w'] > 0
    else:
        nv=nominal['fitted_values'][0]['fitted'];rv=robust['fitted_values'][0]['fitted']
        assert robust['load_scenarios'][1]['network']['sections'][0]['components'][0]['max_dissipation_w'] > 0
        assert len(robust['quantization']['load_scenarios']) == 2
    assert nv == pytest.approx(8,rel=.01)
    assert 4 < rv < 7
    # Identical alternatives have no effect on the preferred numerical realization.
    p['load_scenarios'][0]['loads']['driver']['r_ohm']=8
    same=app.compute(dict(p,load_scenario_objective={'mode':'weighted_mean'}),tmp_path)
    value=same['trials'][same['numerical_minimum_index']]['values'][0] if nodal else same['fitted_values'][0]['fitted']
    assert value == pytest.approx(nv,rel=.01)


def test_scenario_chain_retains_evidence_after_temporary_files_removed(tmp_path):
    p=dict(steps=[dict(id='source',app='source_response',parameters=dict(
        frequencies={'values_hz':F.tolist()},acoustic=dict(kind='bandwidth_prior',sensitivity_db_2v83_1m=90),
        impedance=dict(kind='resistive',r_ohm=6,electrical_load=dict(identity='test-load')))),
        dict(id='network',app='crossover_network',parameters=dict(frequencies={'values_hz':F.tolist()},
            sections=[dict(name='driver',source={'file':'@source'},elements=[dict(id='R',type='R',position='series',value_ohm=2)])]))],
        observables=[dict(name='z',step='network',path='results.input_z_ohm',reduce='min')],retain_results=True)
    r=apps.module('system_scenarios').compute(p,tmp_path)
    outcome=r['outcomes'][0]
    assert outcome['input_error'] is None
    assert outcome['load_evidence']['network'][0]['contract']['identity']=='test-load'
    assert outcome['observables']['z']==pytest.approx(8)
    assert outcome['step_results']['network']['sections'][0]['load_contract']['identity']=='test-load'


def test_import_history_survives_wider_source_grid(tmp_path):
    (tmp_path/'magnitude.zma').write_text('100 6\n1000 9\n10000 20\n')
    out=source(tmp_path,dict(kind='zma_file',file='magnitude.zma'))
    _,contract=electrical_load.resolve(dict(file='source.json',path='results.z_ohm'),F,tmp_path)
    assert contract['phase_basis']=='assumed_zero_missing_phase'
    history=contract['transformations']
    coverage=[row for row in history if row['operation']=='sampling_coverage']
    assert coverage[0]['sampled_band_hz']==[100,10000]
    assert coverage[0]['extrapolated_points']>0
    assert coverage[-1]['extrapolated_points']==0
    assert contract['supported_band_hz'] is None


@pytest.mark.parametrize('kind', ['resistive','ribbon','resonant','free_air'])
def test_driver_classes_use_the_same_load_contract(kind,tmp_path):
    models=dict(resistive=dict(kind='resistive',r_ohm=5),ribbon=dict(kind='ribbon',r_ohm=5,parallel_l_mh=2),
        resonant=dict(kind='resonant',re_ohm=5,peak_r_ohm=12,peak_hz=750,peak_q=2,
                      inductance_model=dict(kind='lr2',le_mh=.03,l2_mh=.12,r2_ohm=2)),
        free_air=dict(kind='free_air',ts=TS))
    first=source(tmp_path,models[kind])
    z,contract=electrical_load.resolve(dict(file='source.json',path='results.z_ohm'),F,tmp_path)
    np.testing.assert_allclose(z,first['z_ohm'],rtol=1e-12)
    assert contract['model']['kind']==kind
    assert contract['supported_band_hz'] is None
    if kind=='resonant':
        assert contract['inductance_model']['kind']=='lr2'


@pytest.mark.parametrize('nodal',[False,True])
def test_alternative_acoustic_sources_follow_the_load_case(tmp_path,nodal):
    p=fitter_input(tmp_path,nodal)
    raw=json.loads((tmp_path/'source.json').read_text())
    pressure=cli.complex_from_record(raw['results']['pressure_per_volt_pa'])*2
    raw['results']['pressure_per_volt_pa']=pressure
    save(tmp_path/'louder.json',raw['results'])
    p['load_scenarios'][0]['loads']['driver']['r_ohm']=8
    p['load_scenarios'][0]['sources']={'driver':{'file':'louder.json'}}
    if nodal:
        p['system']=dict(observer=dict(distance_m=1,ear_height_m=1),sections=[dict(name='acoustic-driver',load_id='driver',
            source={'file':'source.json'},position=dict(z_mm=1000))])
    r=apps.module('network_fit' if nodal else 'crossover_fit').compute(p,tmp_path)
    cases=r['trials'][r['numerical_minimum_index']]['load_scenarios'] if nodal else r['load_scenarios']
    np.testing.assert_allclose(cases[1]['acoustic_spl_db']-cases[0]['acoustic_spl_db'],20*np.log10(2),atol=1e-10)
    assert cases[1]['load_scenario']['unmatched_source_keys']==[]


def test_fractional_limiting_cases_and_resonant_shared_law(tmp_path):
    for n in (0,1):
        z,record=electrical_load.resolve(dict(kind='blocked',ts=dict(re_ohm=6,
            inductance_model=dict(kind='leach',k=.001,n=n))),F,tmp_path)
        np.testing.assert_allclose(z,6+.001*(2j*np.pi*F)**n)
    z,record=electrical_load.resolve(dict(kind='blocked',ts=dict(re_ohm=6,
        inductance_model=dict(kind='leach',k=.1,n=1.2))),F,tmp_path)
    assert record['observations']['negative_real_points']>0
    assert np.all(np.isfinite(z))


def test_unknown_reference_identity_is_content_based(tmp_path):
    for value in [4,8]:
        save(tmp_path/f'{value}.json',dict(f_hz=F,z_ohm=np.full(len(F),value+0j)))
    _,a=electrical_load.resolve(dict(file='4.json',path='results.z_ohm'),F,tmp_path)
    _,b=electrical_load.resolve(dict(file='8.json',path='results.z_ohm'),F,tmp_path)
    assert a['identity']!=b['identity']
    assert a['phase_basis']=='unspecified_from_reference'


def test_magnitude_only_identification_reports_absent_phase_without_rejection(tmp_path):
    f=np.geomspace(30,10000,61);s=2j*np.pi*f
    z=6+s*.0005+64/(1.5+s*.03+1/(s*.0005))
    np.savetxt(tmp_path/'magnitude.zma',np.column_stack([f,abs(z)]))
    p=dict(sd_cm2=220,known=dict(mms_kg=.03,cms_m_per_n=.0005,rms_ns_m=1.5,bl_tm=8,re_ohm=6),
        initial={'le_h':.0002},bounds={'le_h':[.00001,.003]},observations=[{'file':'magnitude.zma'}],
        transfer_audits=[dict(name='series',elements=[dict(id='R',type='R',position='series',value_ohm=4)])])
    r=apps.module('parameter_identification').compute(p,tmp_path)
    assert r['parameters']['le_h']==pytest.approx(.0005,rel=1e-6)
    assert r['load_contract']['phase_basis']=='magnitude_only_fit'
    audit=r['fit_diagnostics']['observations'][0]
    assert audit['residual_bands'][0]['phase_max_error_deg'] is None
    assert 'phase absent' in audit['transfer_audits'][0]['computation']


@pytest.mark.parametrize('nodal',[False,True])
def test_worst_case_objective_and_explicit_weights(tmp_path,nodal):
    p=fitter_input(tmp_path,nodal)
    p['load_scenario_objective']={'mode':'worst_case'}
    r=apps.module('network_fit' if nodal else 'crossover_fit').compute(p,tmp_path)
    assert r['load_scenario_aggregation']['effective_mode']=='worst_case'
    if nodal:
        for trial in r['trials']:
            assert trial['cost']==max(case['cost'] for case in trial['load_scenarios'])
    else:
        # The centered minimax divider satisfies H(8)*H(4)=0.5**2.
        value=r['fitted_values'][0]['fitted']
        assert (8/(8+value))*(4/(4+value))==pytest.approx(.25,rel=.02)
    cases=electrical_load.fit_cases(p)
    assert electrical_load.combine_costs([1,4],cases,{'mode':'weighted_mean','weights':{'nominal':3,'alternate':1}})==pytest.approx(1.75)
    result=electrical_load.aggregation(cases,{'mode':'weighted_mean','weights':{'nominal':0,'alternate':0}})
    assert result['effective_mode']=='nominal'
