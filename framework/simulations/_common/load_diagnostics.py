"""Passive electrical load observables under a declared ideal class-B model."""
import numpy as np
from . import cli


def epdr(z):
    """Resistance with equal peak transistor dissipation at sinusoidal rail swing.

Maximize (1-sin(theta))*sin(theta-phi) on the positive-current half cycle.
For resistance the maximum is 1/4, hence |Z|/(4*maximum).
"""
    z=np.asarray(z,complex)
    phi=np.angle(z)
    theta=np.linspace(0,2*np.pi,128,endpoint=False)[:,None]
    ph=phi.ravel()[None,:]
    power=(1-np.sin(theta))*np.maximum(np.sin(theta-ph),0)
    t=theta[:,0][np.argmax(power,axis=0)]
    for _ in range(8):
        first=np.cos(t-ph[0])-np.sin(2*t-ph[0])
        second=-np.sin(t-ph[0])-2*np.cos(2*t-ph[0])
        t-=np.divide(first,second,out=np.zeros_like(first),where=abs(second)>1e-12)
    maximum=(1-np.sin(t))*np.maximum(np.sin(t-ph[0]),0)
    result=abs(z).ravel()/(4*maximum)
    valid=np.isfinite(z.ravel())&(abs(z).ravel()>0)&(z.real.ravel()>=-1e-12)
    return np.where(valid,result,np.nan).reshape(z.shape)


def programme_weights(f,spec):
    f=np.asarray(f,float)
    kind=spec.get("spectrum","pink")
    if "relative_psd" in spec:
        psd=np.asarray(spec["relative_psd"],float)
    elif kind=="pink":
        psd=1/f
    elif kind=="white":
        psd=np.ones_like(f)
    else:
        raise cli.InputError("programme spectrum needs pink, white or supplied relative_psd")
    if psd.shape!=f.shape or np.any(psd<0) or not np.all(np.isfinite(psd)):
        raise cli.InputError("programme PSD must be a finite nonnegative curve on the network grid")
    if spec.get("band_hz"):
        lo,hi=spec["band_hz"];psd=psd*((f>=lo)&(f<=hi))
    integral=np.trapezoid(psd,f)
    if integral<=0:raise cli.InputError("programme PSD has no positive integrated power")
    return psd/integral
