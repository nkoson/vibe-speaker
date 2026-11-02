"""Branch overlap evidence for engineering review; no automatic component selection."""
from pathlib import Path
import json
import numpy as np
from .core import MeasurementError, compare, smooth_power


def analyse_crossover(woofer, tweeter, combined, out, band, smoothing=12, common_timing=None):
    if len(band)!=2 or not np.isfinite(band).all() or not 0<band[0]<band[1]:
        raise MeasurementError('invalid crossover band')
    ms=[woofer,tweeter]+([combined]if combined else [])
    if any(m.quantity!='spl'for m in ms):raise MeasurementError('crossover analysis requires SPL responses')
    lo=max(band[0],*[m.frequency[0]for m in ms]);hi=min(band[1],*[m.frequency[-1]for m in ms])
    if not 0<lo<hi:raise MeasurementError('crossover band has no common measured coverage')
    bounds=compare(woofer,tweeter,'bounds');bf=np.asarray(bounds['frequency_hz'])
    f=np.geomspace(lo,hi,1200)
    interp=lambda m:np.interp(np.log(f),np.log(m.frequency),m.magnitude)
    w=interp(woofer);t=interp(tweeter)
    # The upper bound must be formed before display smoothing.
    upper=smooth_power(bf,np.asarray(bounds['upper_db']),smoothing)
    upper=np.interp(np.log(f),np.log(bf),upper)
    sw=smooth_power(f,w,smoothing);st=smooth_power(f,t,smoothing)
    diff=sw-st;ids=np.flatnonzero(diff[:-1]*diff[1:]<0)
    crossings=[float(np.exp(np.log(f[i])+diff[i]/(diff[i]-diff[i+1])*np.log(f[i+1]/f[i])))for i in ids]
    result={'schema':'speaker-crossover-evidence/1','band_hz':[lo,hi],'smoothing_fraction':smoothing,
        'inputs':[m.metadata.get('file')for m in ms],'frequency_hz':f.tolist(),
        'woofer_db':sw.tolist(),'tweeter_db':st.tolist(),'upper_bound_db':upper.tolist(),
        'equal_level_crossings_hz':crossings,'common_timing_basis':common_timing,
        'level_alignment_db':0,'findings':[]}
    if combined:
        sc=smooth_power(f,interp(combined),smoothing);result['measured_combined_db']=sc.tolist()
        result['combined_minus_upper_bound_db']=(sc-upper).tolist()
        result['findings'].append('Compare measured sum with the maximum possible sum. A low maximum identifies insufficient branch output; a shortfall below it can indicate phase cancellation when captures share drive and geometry.')
    if common_timing:
        summed=compare(woofer,tweeter,'sum',common_timing)
        result['coherent_sum_db']=np.interp(np.log(f),np.log(summed['frequency_hz']),smooth_power(np.array(summed['frequency_hz']),np.array(summed['values']),smoothing)).tolist()
        wp=np.interp(f,woofer.frequency,np.unwrap(np.deg2rad(woofer.phase)))
        tp=np.interp(f,tweeter.frequency,np.unwrap(np.deg2rad(tweeter.phase)))
        result['relative_phase_deg']=np.rad2deg(np.angle(np.exp(1j*(tp-wp)))).tolist()
    else:
        result['findings'].append('Branch magnitudes and their upper bound remain usable for diagnosing output/overlap. No phase-aligned sum has been inferred.')
    result['findings'].append('Equal-level crossings are descriptors of the acoustic branches, not independently selected electrical filter frequencies.')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'crossover.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter
    fig,axs=plt.subplots(2,1,figsize=(11,8),layout='constrained')
    for ax in axs:
        if ax is axs[0]:
            for m,label,color in [(woofer,'Woofer','#258567'),(tweeter,'Tweeter','#cc7629')]+([(combined,'Measured combined','#176fa7')]if combined else []):
                mask=m.frequency>=m.metadata.get('processing',{}).get('right_window_scale_hz',0)
                ax.semilogx(m.frequency[mask],smooth_power(m.frequency,m.magnitude,smoothing)[mask],label=label,color=color)
            limit=max(m.metadata.get('processing',{}).get('right_window_scale_hz',0)for m in ms)
            mask=bf>=limit
            ax.semilogx(bf[mask],smooth_power(bf,np.asarray(bounds['upper_db']),smoothing)[mask],'--',label='Maximum possible sum',color='#9479a8')
        else:
            ax.semilogx(f,sw,label='Woofer',color='#258567');ax.semilogx(f,st,label='Tweeter',color='#cc7629')
            ax.semilogx(f,upper,'--',label='Maximum possible sum',color='#9479a8')
            if combined:ax.semilogx(f,result['measured_combined_db'],label='Measured combined',color='#176fa7',lw=2)
        if common_timing:ax.semilogx(f,result['coherent_sum_db'],':',label='Complex branch sum',color='#333',lw=2)
        ax.grid(True,which='both',alpha=.2);ax.set_ylabel('SPL (dB)');ax.xaxis.set_minor_formatter(NullFormatter())
    axs[0].set(xlim=(20,20000),title='Crossover evidence: branch output and summation');axs[0].legend(fontsize=9)
    ticks=[20,50,100,200,500,1000,2000,5000,10000,20000];axs[0].set_xticks(ticks,labels=[str(x)for x in ticks])
    axs[1].set(xlim=(lo,hi),xlabel='Frequency (Hz)',title='Requested crossover band; identical absolute level basis')
    ticks=sorted(set([lo,hi]+[float(x)for x in [500,1000,1500,2000,2500,3000,4000,5000,6000,8000]if lo<x<hi]))
    axs[1].set_xticks(ticks,labels=[f'{x:g}'for x in ticks])
    top=max(float(upper.max()),max(result.get('measured_combined_db',upper)))
    axs[1].set_ylim(max(sw.max(),st.max())-35,top+3)
    fig.suptitle(f'Additional 1/{smoothing:g}-octave log-power display smoothing'if smoothing else 'No additional smoothing',fontsize=11)
    fig.savefig(out/'crossover.png',dpi=170);plt.close(fig)
    return result
