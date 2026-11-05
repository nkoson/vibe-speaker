"""Measurement invariants; synthetic serialization contains no private project data."""
import copy
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from framework.measurements.core import Measurement, MeasurementError, compare, smooth_power, windowed_response
from framework.measurements.readers import decode_measurement, read_mdat, read_text, read_result


def impulse(delay=0, amplitude=1):
    fs=48000;n=4096;x=np.zeros(n);x[1024+delay]=amplitude
    return Measurement('synthetic','spl',np.array([20.,20000.]),np.array([0.,0.]),
        metadata={'ir_scale_to_rms':1.0},samples=x,sample_interval=1/fs,start_time=-1024/fs)


def java_class(name, fields):
    from javaobj.v1.beans import JavaClass, JavaString
    c=JavaClass();c.name=name;c.serialVersionUID=1;c.flags=2
    c.fields_names=list(fields);c.fields_types=[JavaString(v)for v in fields.values()]
    return c


def array(values, signature='[F'):
    from javaobj.v1.beans import JavaArray
    a=JavaArray(java_class(signature,{}));a.extend(values);return a


def fixture_measurement(name, offset=0):
    from javaobj.v1.beans import JavaObject, JavaString
    o=JavaObject();o.classdesc=java_class('roomeqwizard.MeasData',{
        'dataLength':'I','freqStep':'D','isLogSpaced':'Z','logStep':'D','octaveFrac':'D',
        'refR':'D','rewSubVersion':'I','rewVersion':'I','startFreq':'D',
        'phaseValues':'[F','shortDesc':'Ljava/lang/String;','splValues':'[F','versionSt':'Ljava/lang/String;'})
    o.dataLength=4;o.freqStep=100.;o.isLogSpaced=True;o.logStep=2.;o.octaveFrac=0.;o.refR=0.
    o.rewVersion=5;o.rewSubVersion=31;o.startFreq=100.;o.phaseValues=array([0.,-45.,-90.,-180.])
    o.shortDesc=JavaString(name);o.splValues=array([70.+offset,71.+offset,72.+offset,73.+offset]);o.versionSt=JavaString('.3')
    return o


def test_serialized_multi_measurement_and_saved_units(tmp_path):
    import javaobj.v1 as java
    path=tmp_path/'multi.mdat';path.write_bytes(java.dumps(array([fixture_measurement('one'),fixture_measurement('two',6)],'[Lroomeqwizard.MeasData;')))
    ms=read_mdat(path,quantity='spl')
    assert [m.name for m in ms]==['one','two']
    np.testing.assert_allclose(ms[0].frequency,[100,200,400,800])
    np.testing.assert_allclose(ms[1].magnitude-ms[0].magnitude,6)
    assert ms[0].metadata['rew_version']=='5.31.3'
    assert len(ms[0].metadata['sha256'])==64
    assert ms[0].metadata['phase_basis']=='unreferenced'


def test_linear_grid_and_calibration_not_applied_to_saved():
    o=fixture_measurement('saved');o.isLogSpaced=False
    o.meterCal=SimpleNamespace(freqArray=[100,1000],gainArray=[20,20],phaseArray=[45,45])
    m=decode_measurement(o,{},1,quantity='spl')
    np.testing.assert_allclose(m.frequency,[100,200,300,400])
    np.testing.assert_allclose(m.magnitude,[70,71,72,73])
    np.testing.assert_allclose(m.phase,[0,-45,-90,-180])


def test_corrupt_and_unsupported_mdat(tmp_path):
    p=tmp_path/'bad.mdat';p.write_bytes(b'not a Java stream')
    with pytest.raises(MeasurementError,match='header'):read_mdat(p)
    p.write_bytes(b'\xac\xed\x00\x05\x73')
    with pytest.raises(MeasurementError,match='decode'):read_mdat(p)
    o=fixture_measurement('bad');o.dataLength=6
    with pytest.raises(MeasurementError,match='dataLength'):decode_measurement(o,{},1,'spl')
    o.dataLength=4;o.refR=100
    with pytest.raises(MeasurementError,match='ZMA'):decode_measurement(o,{},1)


def test_impulse_absolute_level_delay_calibration_and_padding():
    m=impulse(24,2)
    m.calibration=[{'frequency_hz':[1,24000],'gain_db':[6.020599913,6.020599913],'phase_deg':[30,30]}]
    g=windowed_response(m,1,5,kind='rectangular',fft_length=8192)
    np.testing.assert_allclose(g.magnitude,20*np.log10(1/20e-6),atol=1e-8)
    expected=np.exp(-2j*np.pi*g.frequency*.0005-1j*np.pi/6)
    np.testing.assert_allclose(g.complex_response(),expected,atol=1e-9)
    assert g.metadata['processing']['time_origin_changed'] is False
    assert g.metadata['processing']['resolution_scale_hz']==pytest.approx(1/.006)
    h=windowed_response(m,1,5,kind='rectangular')
    np.testing.assert_allclose(h.magnitude,g.magnitude[1::2],atol=1e-8)


def test_gate_excludes_reflection_without_independent_alignment():
    m=impulse();m.samples[1024+480]=.5
    short=windowed_response(m,1,3,kind='rectangular')
    long=windowed_response(m,1,15,kind='rectangular')
    assert np.ptp(short.magnitude)<1e-10
    assert np.ptp(long.magnitude)>9
    with pytest.raises(MeasurementError,match='beyond'):windowed_response(m,100,5)
    with pytest.raises(MeasurementError,match='FFT'):windowed_response(m,1,5,fft_length=100)
    with pytest.raises(MeasurementError):windowed_response(m,1,float('nan'))


def test_impulse_scaling_is_mandatory():
    m=impulse();m.metadata={}
    with pytest.raises(MeasurementError,match='scaling'):windowed_response(m,1,3)


def test_text_phase_placeholder_and_decimal_comma(tmp_path):
    p=tmp_path/'a.frd';p.write_text('* Freq SPL Phase\n100;70,0;0\n200;71,5;0\n400;72,0;0\n')
    m=read_text(p)[0];assert m.phase is None
    np.testing.assert_allclose(m.magnitude,[70,71.5,72])
    assert read_text(p,phase_known=True)[0].phase is not None
    z=tmp_path/'driver.zma';z.write_text('100 8 -20\n200 9 0\n400 10 20\n')
    m=read_text(z,phase_known=True)[0];assert m.quantity=='impedance'
    np.testing.assert_allclose(abs(m.complex_response()),[8,9,10])
    p.write_text('100 70\n100 71\n')
    with pytest.raises(MeasurementError,match='strictly'):read_text(p)
    p.write_text('* Freq Fundamental THD H2\n100 70 1 .5\n200 70 1 .5\n')
    with pytest.raises(MeasurementError,match='2 or 3'):read_text(p)


def test_sum_ratio_and_unknown_timing():
    f=np.geomspace(100,10000,100)
    a=Measurement('a','spl',f,np.full(100,70.),np.zeros(100))
    b=copy.deepcopy(a)
    with pytest.raises(MeasurementError,match='common-timing'):compare(a,b,'sum')
    result=compare(a,b,'sum','same fixed acoustic reference; mic and reference unchanged')
    np.testing.assert_allclose(result['values'],76.020599913,atol=1e-8)
    b.phase[:]=180
    assert max(compare(a,b,'sum','same reference')['values']) < -200
    b.phase[:]=0;b.magnitude[:]=76.020599913
    np.testing.assert_allclose(compare(a,b,'ratio','same reference')['values'],6.020599913)
    bounds=compare(a,b,'bounds');np.testing.assert_allclose(bounds['upper_db'],79.542425094,atol=1e-8)
    assert compare(a,b,'difference')['level_alignment_db']==0
    b.metadata={'processing':{'mode':'saved'},'saved_smoothing_octave_fraction':6}
    with pytest.raises(MeasurementError,match='unsmoothed'):compare(a,b,'sum','same reference')


def test_smoothing_preserves_constant_and_gain():
    f=np.geomspace(20,20000,1000);y=70+3*np.sin(np.log(f)*8)
    np.testing.assert_allclose(smooth_power(f,np.full(len(f),70.),12),70,atol=1e-10)
    np.testing.assert_allclose(smooth_power(f,y+6,12)-smooth_power(f,y,12),6,atol=1e-10)
    np.testing.assert_array_equal(smooth_power(f,y,0),y)
    with pytest.raises(MeasurementError):smooth_power(f,y,-1)


def test_cli_outputs_and_round_trip(tmp_path):
    source=tmp_path/'response.frd';source.write_text('100 70 -20\n1000 73 0\n10000 70 20\n')
    out=tmp_path/'analysis'
    cmd=[sys.executable,str(ROOT/'framework/tools/analyze_measurements.py'),'analyze',str(source),'--out',str(out),'--phase-known']
    p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
    index=json.loads((out/'index.json').read_text());m=read_result(out/index['measurements'][0]['file'])
    np.testing.assert_allclose(m.magnitude,[70,73,70]);assert (out/'spl-overview.png').stat().st_size>1000
    csv=next(out.glob('*.csv'));np.testing.assert_allclose(read_text(csv,phase_known=True)[0].phase,m.phase)
    p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==2
    assert 'already contains' in p.stderr


def test_optional_real_mdat_corpus():
    """Opt-in local files are regression evidence, never distributed test fixtures."""
    import os
    paths=os.environ.get('REW_TEST_FILES')
    if not paths:pytest.skip('set REW_TEST_FILES to os.pathsep-separated real MDAT files')
    for path in paths.split(os.pathsep):
        ms=read_mdat(path)
        assert ms
        for m in ms:
            assert len(m.frequency)>100
            if m.samples is not None:
                result=windowed_response(m,1,3)
                assert np.isfinite(result.magnitude).all()


def test_crossover_distinguishes_output_shortfall_from_cancellation(tmp_path):
    from framework.measurements.crossover import analyse_crossover
    f=np.geomspace(1000,6000,100)
    w=Measurement('woofer','spl',f,np.full(100,60.),np.zeros(100))
    t=Measurement('tweeter','spl',f,np.full(100,60.),np.full(100,120.))
    total=Measurement('measured sum','spl',f,np.full(100,60.))
    result=analyse_crossover(w,t,total,tmp_path,[1500,4500],common_timing='synthetic common source')
    np.testing.assert_allclose(result['coherent_sum_db'],60.,atol=1e-9)
    np.testing.assert_allclose(result['combined_minus_upper_bound_db'],-6.020599913,atol=1e-8)
    assert (tmp_path/'crossover.png').stat().st_size>1000
    assert result['level_alignment_db']==0
    t.phase=None
    result=analyse_crossover(w,t,total,tmp_path,[1500,4500])
    assert 'coherent_sum_db'not in result
    np.testing.assert_allclose(result['upper_bound_db'],66.020599913,atol=1e-8)


def test_combined_calibration_boost_limit():
    m=impulse();m.metadata['limit_cal_boost_20db']=True
    m.calibration=[{'frequency_hz':[1,24000],'gain_db':[-15,-15],'phase_deg':[0,0]}]*2
    result=windowed_response(m,1,3,kind='rectangular')
    np.testing.assert_allclose(result.magnitude,20*np.log10(1/20e-6)+20,atol=1e-8)
