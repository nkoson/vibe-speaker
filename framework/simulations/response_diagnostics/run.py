#!/usr/bin/env python3
"""Linear phase, group delay, impulse, step and energy-time response diagnostics."""
import sys
from pathlib import Path
import numpy as np
from scipy.signal import hilbert
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,acoustics,response_data
NAME="response_diagnostics"
VERSION="1.0"


def compute(params,base_dir):
    spec=params["response"]
    if "file" in spec:
        document=cli.load_json(cli.resolve_path(spec["file"],base_dir))
        native=np.asarray(cli.dotted(document,spec.get("frequency_path","results.f_hz")),float)
        f=cli.frequency_grid(params.get("frequencies",{"values_hz":native}))
        h=cli.curve_from_reference(dict(extrapolation="error",**spec),base_dir,f)
    else:
        f=np.asarray(spec["frequency_hz"],float);h=cli.complex_from_record(spec)
    if len(f)<3 or h.shape!=f.shape or np.any(f<=0) or np.any(np.diff(f)<=0) or not np.all(np.isfinite(h)):
        raise cli.InputError("diagnostics need at least three increasing positive frequencies and finite complex samples")
    delay=float(params.get("known_delay_s",0))
    residual=h*np.exp(2j*np.pi*f*delay)
    phase=np.unwrap(np.angle(residual))
    threshold=abs(h).max()*10**(float(params.get("phase_floor_db",-80))/20)
    valid=abs(h)>threshold
    # A finite-difference derivative uses neighboring phase samples.
    mask=valid.copy();mask[1:]&=valid[:-1];mask[:-1]&=valid[1:]
    gd=-np.gradient(phase,2*np.pi*f,edge_order=2)+delay
    gd[~mask]=np.nan
    result=dict(f_hz=f,response=h,phase_deg=np.rad2deg(phase-2*np.pi*f*delay),
                group_delay_s=gd,phase_valid=mask,phase_floor_amplitude=threshold)
    if params.get("minimum_phase"):
        m=params["minimum_phase"] if isinstance(params["minimum_phase"],dict) else {}
        minimum=acoustics.minimum_phase(f,f,acoustics.db(h),m.get("lower_rolloff_db_oct",0),m.get("upper_rolloff_db_oct",0))
        mp=np.unwrap(np.angle(minimum))
        mg=-np.gradient(mp,2*np.pi*f,edge_order=2)
        mg[~mask]=np.nan
        result.update(minimum_phase_response=minimum,minimum_group_delay_s=mg,
                      excess_phase_deg=np.rad2deg(phase-mp-2*np.pi*f*delay),excess_group_delay_s=gd-mg)
    time=params.get("time_domain")
    if time:
        fs=cli.positive(time["sample_rate_hz"],"sample_rate_hz")
        n=int(time.get("fft_length",65536))
        if n<8 or n%2:raise cli.InputError("fft_length must be even and at least eight")
        bins=np.fft.rfftfreq(n,1/fs)
        policy=time.get("extension","error")
        spectrum=np.empty(len(bins),complex)
        spectrum[1:]=response_data.resample(bins[1:],f,h,delay_s=delay,extrapolation=policy)
        if "dc_real" not in time:
            raise cli.InputError("time reconstruction requires explicit dc_real")
        spectrum[0]=float(time["dc_real"])
        padding_delay=float(time.get("delay_s",0))
        spectrum*=np.exp(-2j*np.pi*bins*padding_delay)
        imaginary_nyquist=float(spectrum[-1].imag)
        spectrum[-1]=float(time.get("nyquist_real",spectrum[-1].real))
        impulse=np.fft.irfft(spectrum,n=n)
        roundtrip=np.fft.rfft(impulse)
        result["time_domain"]=dict(time_s=np.arange(n)/fs,impulse_samples=impulse,
            impulse_density_per_s=impulse*fs,step_response=np.cumsum(impulse),
            energy_time_amplitude=abs(hilbert(impulse)),sample_rate_hz=fs,
            added_delay_s=padding_delay,period_s=n/fs,extension=policy,
            extrapolated_bins=int(np.sum((bins[1:]<f[0])|(bins[1:]>f[-1]))),
            discarded_nyquist_imaginary=imaginary_nyquist,
            max_fft_roundtrip_error=float(abs(roundtrip-spectrum).max()),
            interpretation="Band-limited periodic reconstruction; endpoint extension and delay determine wraparound and pre-ringing.")
    return result


if __name__=="__main__":
    sys.exit(cli.run(NAME,VERSION,compute,__doc__,[
        "Linear transform diagnostics preserve declared delay and endpoint assumptions; no audibility thresholds are imposed.",
        "See framework/references/measured-response-processing.md. Finite bandwidth does not identify an unmeasured transient."]))
