"""Command-line inspection, processing, plotting and comparison of measurement data."""
import argparse
import json
import re
from pathlib import Path
import numpy as np
from scipy.integrate import trapezoid
from .core import MeasurementError, compare, impulse_diagnostics, smooth_power, windowed_response
from .readers import load, read_result


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def record(m, include_ir=True):
    h=None if m.phase is None else m.complex_response()
    return {'schema':'speaker-measurement/1','name':m.name,'quantity':m.quantity,'metadata':m.metadata,
        'response':{'frequency_hz':m.frequency.tolist(),'magnitude':m.magnitude.tolist(),
                    'magnitude_unit':'ohm' if m.quantity=='impedance' else 'dB SPL' if m.quantity=='spl' else 'dB',
                    'phase_deg':None if m.phase is None else m.phase.tolist(),
                    'complex':None if h is None else {'real':h.real.tolist(),'imag':h.imag.tolist()},
                    'complex_unit':'ohm' if m.quantity=='impedance' else 'Pa RMS' if m.quantity=='spl' else 'ratio'},
        'calibration':m.calibration,
        'impulse':None if m.samples is None or not include_ir else {'samples':m.samples.tolist(),
                    'sample_interval_s':m.sample_interval,'start_time_s':m.start_time},
        'diagnostics':impulse_diagnostics(m)}


def stats(m, band, smoothing):
    lo,hi=band
    processing=m.metadata.get('processing',{})
    resolution=processing.get('right_window_scale_hz')
    effective_lo=max(lo,m.frequency[0],resolution or 0)
    effective_hi=min(hi,m.frequency[-1])
    mask=(m.frequency>=effective_lo)&(m.frequency<=effective_hi)
    if mask.sum()<3:
        return {'requested_band_hz':band,'available':False,'reason':'fewer than three supported samples in band'}
    y=m.magnitude if m.quantity=='impedance' else smooth_power(m.frequency,m.magnitude,smoothing)
    ff=m.frequency[mask];yy=y[mask]
    # Equal weight per log-frequency interval, not per FFT bin.
    x=np.log2(ff);mean=float(trapezoid(yy,x)/(x[-1]-x[0]))
    return {'requested_band_hz':band,'analysed_band_hz':[float(ff[0]),float(ff[-1])],
        'mean':mean,'minimum':float(yy.min()),'minimum_hz':float(ff[np.argmin(yy)]),
        'maximum':float(yy.max()),'maximum_hz':float(ff[np.argmax(yy)]),'peak_to_peak':float(np.ptp(yy)),
        'units':'ohm' if m.quantity=='impedance' else 'dB','display_smoothing_fraction':smoothing,
        'mean_definition':'trapezoidal mean of plotted magnitude over log2 frequency'}


def plot(measurements, path, smoothing):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    quantities={m.quantity for m in measurements}
    if len(quantities)!=1:raise MeasurementError('plot one quantity at a time; SPL and impedance do not share a magnitude axis')
    irs=[m for m in measurements if m.samples is not None]
    fig,axs=plt.subplots(3 if irs else 2,1,figsize=(11,9 if irs else 7),layout='constrained')
    names=[m.name for m in measurements]
    for i,m in enumerate(measurements):
        color=f'C{i%10}'
        label=m.name if names.count(m.name)==1 else f"{m.name} [{Path(m.metadata.get('file','')).name} #{m.metadata.get('measurement_index',i+1)}]"
        y=m.magnitude if m.quantity=='impedance' else smooth_power(m.frequency,m.magnitude,smoothing)
        limit=m.metadata.get('processing',{}).get('right_window_scale_hz',0)
        keep=m.frequency>=limit
        axs[0].semilogx(m.frequency[keep],y[keep],label=label,color=color)
        if m.phase is not None:axs[1].semilogx(m.frequency[keep],(m.phase[keep]+180)%360-180,label=label,color=color)
    unit='Impedance (ohm)' if measurements[0].quantity=='impedance' else 'SPL (dB)' if measurements[0].quantity=='spl' else 'Transfer (dB)'
    axs[0].set_ylabel(unit);axs[0].legend(fontsize=8);axs[1].set(ylabel='Phase (degrees)',ylim=(-180,180),xlabel='Frequency (Hz)')
    if all(m.phase is None for m in measurements):axs[1].text(.5,.5,'No established phase data',ha='center',transform=axs[1].transAxes)
    for ax in axs[:2]:
        ax.set_xlim(20,20000);ticks=[20,50,100,200,500,1000,2000,5000,10000,20000]
        ax.set_xticks(ticks,labels=[str(x)for x in ticks]);ax.xaxis.set_minor_formatter(NullFormatter());ax.grid(True,which='both',alpha=.2)
    if irs:
        from scipy.signal import hilbert
        for i,m in enumerate(measurements):
            if m.samples is None:continue
            t=(m.start_time+np.arange(len(m.samples))*m.sample_interval)*1000
            e=abs(hilbert(m.samples));db=20*np.log10(np.maximum(e/max(e.max(),1e-300),1e-6))
            axs[2].plot(t,db,label=m.name,color=f'C{i%10}')
        peaks=[impulse_diagnostics(m)['peak_time_s']*1000 for m in irs]
        axs[2].set(xlim=(min(peaks)-2,max(peaks)+30),ylim=(-70,3),xlabel='Saved time (ms)',ylabel='ETC (dB re own peak)')
        axs[2].grid(True,alpha=.2)
    smoothing_label='No additional smoothing' if smoothing==0 else f'Additional 1/{smoothing:g}-octave log-power smoothing (magnitude display only)'
    gate_scales=[m.metadata.get('processing',{}).get('right_window_scale_hz',0)for m in measurements]
    gate_note=f'; curves shown above each gate\'s frequency scale' if any(gate_scales) else ''
    fig.suptitle(smoothing_label+'\nAbsolute levels retained; saved time origins'+gate_note,fontsize=10)
    fig.savefig(path,dpi=160);plt.close(fig)


def analyse(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    if (out/'index.json').exists() and not args.overwrite:raise MeasurementError('output already contains an analysis; use a new folder or --overwrite')
    context=json.loads(Path(args.context).read_text()) if args.context else {}
    input_paths={Path(source).resolve()for source in args.files}
    measurements=[];index=[]
    for source in args.files:
        ms=load(source,args.quantity,args.phase_known)
        if args.select:
            if any(i<1 or i>len(ms)for i in args.select):raise MeasurementError('selected measurement index is outside the file')
            ms=[m for i,m in enumerate(ms,1)if i in args.select]
        for m in ms:
            if args.context:m.metadata['acquisition_context']=context
            if args.mode=='ir':
                if args.left_ms is None or args.right_ms is None:raise MeasurementError('--mode ir requires --left-ms and --right-ms')
                m=windowed_response(m,args.left_ms,args.right_ms,args.reference_ms,args.window,args.taper,args.fft_length)
            elif args.left_ms is not None or args.right_ms is not None:
                raise MeasurementError('window arguments require --mode ir')
            basename=f'{len(measurements)+1:03d}-'+(re.sub(r'[^A-Za-z0-9_-]+','-',m.name).strip('-')[:65] or 'measurement')
            result=record(m);result['statistics']=stats(m,args.band,args.smoothing)
            if (out/(basename+'.json')).resolve() in input_paths or (out/(basename+'.csv')).resolve() in input_paths:
                raise MeasurementError('output would overwrite an input measurement; choose a different output folder')
            write_json(out/(basename+'.json'),result)
            cols=[m.frequency,m.magnitude]
            header='frequency_hz,magnitude_'+('ohm' if m.quantity=='impedance' else 'db')
            if m.phase is not None:cols.append(m.phase);header+=',phase_deg'
            np.savetxt(out/(basename+'.csv'),np.column_stack(cols),delimiter=',',header=header,comments='# ')
            index.append({'name':m.name,'file':basename+'.json','statistics':result['statistics'],
                          'timing_reference':m.metadata.get('timing_reference'),'phase_basis':m.metadata.get('phase_basis')})
            measurements.append(m)
    if not measurements:raise MeasurementError('no measurements selected')
    for quantity in sorted({m.quantity for m in measurements}):
        plot([m for m in measurements if m.quantity==quantity],out/(quantity+'-overview.png'),args.smoothing)
    write_json(out/'index.json',{'schema':'speaker-measurement-analysis/1','measurements':index,'context':context,
        'processing':{'mode':args.mode,'smoothing_fraction':args.smoothing,'automatic_level_alignment':False,
                      'automatic_peak_alignment':False}})
    notes=['# Measurement observations','', 'Original files are unchanged. CSV/JSON contain the processing result before additional plot smoothing.', '',
        'Interpretation and diagnostic measurement choices: [measurement analysis reference](https://www.roomeqwizard.com/help/help_en-GB/html/graph_splphase.html).', '']
    for entry in index:
        notes += [f"## {entry['name']}",f"Data: `{entry['file']}`. Timing: {entry['timing_reference']}; phase basis: {entry['phase_basis']}.",
                  'Statistics: `'+json.dumps(entry['statistics'])+'`.', '']
    notes += ['## Engineering review','Explain each feature using its frequency, level, branch contribution and acquisition conditions. Separate observations from competing causes. Select a controlled next measurement that distinguishes the causes; consult framework/skills/speaker-measurements/SKILL.md.']
    (out/'observations.md').write_text('\n'.join(notes)+'\n')
    print(json.dumps({'output':str(out.resolve()),'measurements':len(measurements),'index':str(out/'index.json')}))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    inspect=sub.add_parser('inspect',help='list every measurement, acquisition metadata and available data')
    analyze=sub.add_parser('analyze',help='export preserved data, statistics and plots')
    for p in [inspect,analyze]:
        p.add_argument('files',nargs='+');p.add_argument('--quantity',choices=['spl','impedance','transfer'])
        p.add_argument('--phase-known',action='store_true',help='text phase column is real phase data, not a zero placeholder')
    analyze.add_argument('--out',required=True);analyze.add_argument('--context',help='JSON of user-confirmed acquisition conditions, retained verbatim')
    analyze.add_argument('--select',type=int,nargs='+',help='one-based indices, applied to each input file')
    analyze.add_argument('--mode',choices=['saved','ir'],default='saved');analyze.add_argument('--left-ms',type=float);analyze.add_argument('--right-ms',type=float)
    analyze.add_argument('--reference-ms',type=float,default=0);analyze.add_argument('--window',choices=['tukey','hann','rectangular'],default='tukey')
    analyze.add_argument('--taper',type=float,default=.25);analyze.add_argument('--fft-length',type=int)
    analyze.add_argument('--smoothing',type=float,default=0,help='0 retains saved smoothing; 12 adds 1/12-octave log-power display smoothing')
    analyze.add_argument('--band',type=float,nargs=2,default=[20,20000]);analyze.add_argument('--overwrite',action='store_true')
    comp=sub.add_parser('compare',help='compare two exported measurement JSON files')
    comp.add_argument('a');comp.add_argument('b');comp.add_argument('--out',required=True)
    comp.add_argument('--operation',choices=['difference','bounds','sum','ratio'],default='difference')
    comp.add_argument('--common-timing',help='explicit evidence that both records share their time reference and retained offsets')
    xo=sub.add_parser('crossover',help='analyse woofer/tweeter overlap and a measured combined response')
    xo.add_argument('--woofer',required=True);xo.add_argument('--tweeter',required=True);xo.add_argument('--combined')
    xo.add_argument('--out',required=True);xo.add_argument('--band',nargs=2,type=float,required=True)
    xo.add_argument('--smoothing',type=float,default=12);xo.add_argument('--common-timing')
    args=parser.parse_args(argv)
    try:
        if args.command=='inspect':
            records=[]
            for source in args.files:
                for m in load(source,args.quantity,args.phase_known):
                    records.append({'name':m.name,'quantity':m.quantity,'frequency_samples':len(m.frequency),
                                    'has_phase':m.phase is not None,'has_impulse':m.samples is not None,'metadata':m.metadata})
            print(json.dumps(records,indent=2,allow_nan=False))
        elif args.command=='analyze':
            if not np.isfinite(args.band).all() or not 0<args.band[0]<args.band[1]:raise MeasurementError('invalid statistics band')
            if not np.isfinite(args.smoothing) or args.smoothing<0:raise MeasurementError('smoothing must be nonnegative')
            analyse(args)
        elif args.command=='crossover':
            from .crossover import analyse_crossover
            analyse_crossover(read_result(args.woofer),read_result(args.tweeter),read_result(args.combined)if args.combined else None,
                              args.out,args.band,args.smoothing,args.common_timing)
            print(str(Path(args.out).resolve()/'crossover.json'))
        else:
            result=compare(read_result(args.a),read_result(args.b),args.operation,args.common_timing)
            result['inputs']=[str(Path(args.a).resolve()),str(Path(args.b).resolve())]
            out=Path(args.out)
            if out.resolve() in {Path(args.a).resolve(),Path(args.b).resolve()}:
                raise MeasurementError('comparison output must differ from both inputs')
            out.parent.mkdir(parents=True,exist_ok=True);write_json(out,result)
            print(str(out.resolve()))
    except (MeasurementError,OSError,ValueError,KeyError) as exc:
        parser.exit(2,f'analysis error: {exc}\n')


if __name__=='__main__':main()
