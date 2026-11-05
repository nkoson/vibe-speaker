"""Read REW Java serialization as data, never by running Java classes or pickle."""
import hashlib
import json
import math
import re
from pathlib import Path
import numpy as np
from .core import Measurement, MeasurementError, vector


def scalar(value, default=None):
    if value is None:
        return default
    if isinstance(value, (str, bool, int, float)):
        return value
    if hasattr(value, 'value'):
        return scalar(value.value, default)
    if type(value).__name__ == 'JavaString':
        return str(value)
    return default


def field(obj, name, default=None):
    return scalar(getattr(obj, name, None), default)


def class_name(obj):
    return getattr(getattr(obj, 'classdesc', None), 'name', None)


def calibration_data(obj):
    if obj is None or getattr(obj, 'freqArray', None) is None:
        return None
    f=vector(obj.freqArray,'calibration frequency');g=vector(obj.gainArray,'calibration gain')
    ph=getattr(obj,'phaseArray',None)
    ph=np.zeros(len(f)) if ph is None else vector(ph,'calibration phase')
    if len(f)!=len(g) or len(ph)!=len(f) or np.any(f<=0) or np.any(np.diff(f)<=0):
        raise MeasurementError('invalid calibration frequency/gain/phase arrays')
    return {'frequency_hz':f.tolist(),'gain_db':g.tolist(),'phase_deg':ph.tolist(),
            'name':field(obj,'sourceName',''),'inverse_c':field(obj,'inverseCSelected',False)}


def decode_measurement(obj, provenance, index, quantity=None):
    """Structural adapter tested on REW V5.31.3; unknown structures fail explicitly."""
    values=getattr(obj,'splValues',None)
    if values is None:
        raise MeasurementError(f'measurement {index}: no supported saved magnitude array')
    values=vector(values,'saved response');n=len(values)
    if field(obj,'dataLength',n)!=n:
        raise MeasurementError(f'measurement {index}: dataLength disagrees with saved response')
    start=field(obj,'startFreq')
    if start is None:
        raise MeasurementError('missing frequency grid start')
    if field(obj,'isLogSpaced',False):
        step=field(obj,'logStep')
        if step is None or step<=1:
            raise MeasurementError('invalid log frequency step')
        f=start*np.exp(np.arange(n)*math.log(step))
    else:
        step=field(obj,'freqStep')
        if step is None or step<=0:
            raise MeasurementError('invalid linear frequency step')
        f=start+np.arange(n)*step
    irdata=getattr(obj,'irData',None);ir=getattr(irdata,'ir',None)
    # refR is the impedance sense resistor. Imported/RTA records may have no IR.
    detected='impedance' if field(obj,'refR',0)>0 else ('spl' if ir is not None else None)
    quantity=quantity or detected
    if quantity=='transfer':
        raise MeasurementError('native MDAT values are saved SPL; export a transfer response in dB for transfer import')
    if quantity=='impedance' or detected=='impedance':
        raise MeasurementError('native impedance MDAT storage is not supported; export impedance as ZMA/REW text in ohms')
    if quantity is None:
        raise MeasurementError(f'measurement {index}: specify --quantity for an imported/RTA record without an IR')
    if detected=='impedance' and quantity!='impedance':
        raise MeasurementError('impedance sense resistor is present; cannot label this as SPL')
    phase=getattr(obj,'phaseValues',None)
    samples=None;dt=None;t0=None
    if ir is not None and getattr(ir,'data',None) is not None:
        samples=vector(ir.data,'impulse samples');dt=field(ir,'T');t0=field(ir,'startTime')
        if field(ir,'n',len(samples))!=len(samples):
            raise MeasurementError('IR sample count mismatch')
    timing=field(obj,'timingReferenceMode','UNKNOWN')
    metadata={**provenance,'measurement_index':index,'reader':'rew_java_serialization_v1',
        'rew_version':f"{field(obj,'rewVersion','?')}.{field(obj,'rewSubVersion','?')}{field(obj,'versionSt','')}",
        'notes':field(obj,'measNotes',''),'quantity_detection':detected,
        'input':field(obj,'sourceFileName',''),'output':field(obj,'outputName',''),
        'excitation':field(obj,'sourceFileFormat',''),'sweep_level_dbfs':field(obj,'sweepLevel'),
        'sweep_level_text':field(obj,'sigGenLevelSt',''),'sample_rate_hz':field(obj,'sampleRate'),
        'is_rta':field(obj,'isFromRTA',False),'source_type':field(obj,'sourceType'),
        'timing_reference':timing,'timing_reference_output':field(obj,'timingRefName'),
        'timing_reference_input':field(obj,'timingRefInputName'),
        'phase_basis':'unreferenced' if timing in ('NONE','UNKNOWN') else 'timing_reference_recorded',
        'saved_smoothing_octave_fraction':field(obj,'octaveFrac'),
        'saved_valid_band_hz':[field(obj,'validStartFreq'),field(obj,'validEndFreq')],
        'spl_alignment_cumulative_db':field(obj,'alignSPLOffsetCumulative',0),
        'processing':{'mode':'saved','calibration_applied':'already in saved response; not reapplied','level_alignment_db':0},
        'has_distortion_data':getattr(obj,'distortionData',None) is not None,
        'has_rt60_data':getattr(obj,'rt60Data',None) is not None,
        'limit_cal_boost_20db':field(obj,'calDataLimitApplied',False)}
    unsupported=[];cal=[]
    for name in ['meterCal','scCal']:
        c=calibration_data(getattr(obj,name,None))
        if c:
            c['role']=name;cal.append(c)
        if field(getattr(obj,name,None),'inverseCSelected',False):
            unsupported.append('C-weighting compensation: use saved response or REW export')
    metadata['calibration_files']=[{'name':c['name'],'role':c['role']}for c in cal]
    if irdata is not None:
        for source,target in [('measurementDelay','measurement_delay_s'),('timingOffset','timing_offset_s'),
            ('cumulativeStartTimeOffset','cumulative_time_shift_s'),('cumulativeClockRateAdjust','clock_adjustment'),
            ('signalToNoisedB','snr_db'),('minPhase','minimum_phase'),('fdwEnabled','fdw_enabled')]:
            metadata[target]=field(irdata,source)
        if metadata.get('minimum_phase'):metadata['phase_basis']='reconstructed_minimum_phase'
        windows=getattr(irdata,'windows',None)
        if windows is not None:
            metadata['saved_window']={k:field(windows,k)for k in ['preImpulseDurn','postImpulseDurn','winRefTime','preType','postType']}
        offset=field(irdata,'splOffset')
        if quantity=='spl' and offset is not None:
            metadata['ir_scale_to_rms']=20e-6*10**(offset/20)/math.sqrt(2)
            metadata['ir_spl_offset_db']=offset
        if field(irdata,'invertImpulse',False) or field(ir,'inverted',False):
            unsupported.append('saved inversion flag requires REW export for re-windowing')
        if metadata.get('minimum_phase'):
            unsupported.append('minimum-phase derived record; use saved response')
    metadata['ir_processing_unsupported']=unsupported
    # Ignore a DC frequency entry, never invent a positive log-axis location for DC.
    keep=f>0
    if phase is not None:
        phase=vector(phase,'saved phase')
        if len(phase)!=n:raise MeasurementError('saved phase length mismatch')
        phase=phase[keep]
    return Measurement(field(obj,'shortDesc',f'Measurement {index}'),quantity,f[keep],values[keep],phase,
                       metadata,samples,dt,t0,cal)


def read_mdat(path, quantity=None):
    import javaobj.v2 as java
    path=Path(path);raw=path.read_bytes()
    if len(raw)>512*1024*1024:
        raise MeasurementError('MDAT exceeds the 512 MiB input limit; split the measurement set in REW')
    if not raw.startswith(b'\xac\xed\x00\x05'):
        raise MeasurementError('unsupported MDAT header; use a REW text/IR export for this format')
    try: roots=java.loads(raw)
    except Exception as exc:raise MeasurementError(f'cannot decode MDAT: {exc}') from exc
    found=[];seen=set()
    def visit(x):
        if id(x) in seen:return
        seen.add(id(x))
        if class_name(x)=='roomeqwizard.MeasData':found.append(x)
        elif isinstance(x,(list,tuple)):
            # Serialized arrays of measurements are supported; don't traverse object internals.
            for child in x:
                if not isinstance(child,(str,int,float,bool)):visit(child)
    visit(roots)
    if not found:raise MeasurementError('MDAT contains no supported roomeqwizard.MeasData records')
    provenance={'file':str(path.resolve()),'sha256':hashlib.sha256(raw).hexdigest()}
    return [decode_measurement(m,provenance,i+1,quantity)for i,m in enumerate(found)]


def read_text(path, quantity=None, phase_known=False, delimiter=None):
    """Strict single-response FRD/ZMA/REW text, including decimal commas with ';' or tabs."""
    path=Path(path);raw=path.read_bytes();lines=raw.decode('utf-8-sig').splitlines();rows=[];comments=[]
    for number,line in enumerate(lines,1):
        line=line.strip()
        if not line:continue
        if line.startswith(('*','#',';')):
            comments.append(line);continue
        sep=delimiter or (';' if ';' in line else ('\t' if '\t' in line else (',' if ',' in line else None)))
        cols=line.split(sep) if sep else line.split()
        try:
            row=[float(x.strip().replace(',','.') if sep in (';','\t') else x.strip())for x in cols]
        except ValueError as exc:
            raise MeasurementError(f'{path.name}:{number}: expected numeric Hz/magnitude[/phase] columns; headers must start with * or #') from exc
        if len(row) not in (2,3):raise MeasurementError('response text requires 2 or 3 columns; distortion/RT60 exports use their own units and are not frequency responses')
        rows.append(row)
    if not rows or len({len(r)for r in rows})!=1:raise MeasurementError('empty or inconsistent response table')
    a=np.array(rows);quantity=quantity or ('impedance' if path.suffix.lower()=='.zma' else 'spl')
    phase=a[:,2] if a.shape[1]==3 and phase_known else None
    return [Measurement(path.stem,quantity,a[:,0],a[:,1],phase,
        {'file':str(path.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'measurement_index':1,
         'comments':comments,'phase_basis':'declared_measured' if phase_known and phase is not None else 'unknown',
         'phase_column_present':a.shape[1]==3,'processing':{'mode':'text','level_alignment_db':0},
         'timing_reference':'UNKNOWN'})]


def read_result(path):
    d=json.loads(Path(path).read_text())
    if d.get('schema')!='speaker-measurement/1':raise MeasurementError('not a measurement result')
    r=d['response'];ir=d.get('impulse') or {}
    return Measurement(d['name'],d['quantity'],r['frequency_hz'],r['magnitude'],r.get('phase_deg'),d['metadata'],
                       ir.get('samples'),ir.get('sample_interval_s'),ir.get('start_time_s'),d.get('calibration',[]))


def load(path, quantity=None, phase_known=False):
    ext=Path(path).suffix.lower()
    if ext=='.mdat':return read_mdat(path,quantity)
    if ext=='.json':return [read_result(path)]
    if ext in ('.txt','.frd','.zma','.csv'):return read_text(path,quantity,phase_known)
    raise MeasurementError(f'unsupported extension {ext}; use MDAT, FRD/ZMA, response TXT/CSV or analysis JSON')
