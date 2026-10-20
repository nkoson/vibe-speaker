"""Small-signal blocked impedance and viscoelastic suspension laws."""
import numpy as np
from . import cli


def blocked_impedance(ts, f):
    s = 2j*np.pi*np.asarray(f, float)
    re = cli.positive(ts.get("re_ohm"), "re_ohm")
    model = ts.get("inductance_model") or {"kind": "constant", "le_mh": ts.get("le_mh", 0)}
    kind = model["kind"]
    if kind == "constant":
        return re+s*cli.positive(model.get("le_mh", 0), "le_mh", zero=True)*1e-3
    if kind == "leach":
        k = cli.positive(model.get("k"), "inductance k", zero=True)
        n = cli.positive(model.get("n"), "inductance n", zero=True)
        if n > 1:
            raise cli.InputError("passive fractional inductance needs 0 <= n <= 1")
        return re+k*s**n
    if kind == "lr2":
        le = cli.positive(model.get("le_mh", 0), "le_mh", zero=True)*1e-3
        l2 = cli.positive(model.get("l2_mh"), "l2_mh")*1e-3
        r2 = cli.positive(model.get("r2_ohm"), "r2_ohm")
        return re+s*le+(s*l2*r2)/(s*l2+r2)
    if kind == "semi_inductance":
        leb = cli.positive(model.get("leb_mh", 0), "leb_mh", zero=True)*1e-3
        y = np.zeros_like(s)
        branches = 0
        for key, z in (("le_mh", lambda v:s*v*1e-3), ("ke", lambda v:np.sqrt(s)*v),
                       ("rss_ohm", lambda v:np.full_like(s, v))):
            if model.get(key) is not None:
                value = cli.positive(model[key], key)
                y += 1/z(value)
                branches += 1
        if not branches:
            raise cli.InputError("semi_inductance needs at least one parallel branch")
        return re+s*leb+1/y
    raise cli.InputError(f"unknown inductance model {kind}")


def mechanical_impedance(ts, f, elements):
    s = 2j*np.pi*np.asarray(f, float)
    model = ts.get("creep") or {}
    if model and model.get("kind", "log") != "log":
        raise cli.InputError("creep.kind must be log")
    beta = cli.positive(model.get("beta", 0), "creep.beta", zero=True)
    corner = cli.positive(model.get("transition_hz", 1.5*ts["fs_hz"]), "creep.transition_hz")
    c0 = cli.positive(model.get("c0_m_per_n", elements["cms"]), "creep.c0_m_per_n")
    r0 = cli.positive(model.get("r0_ns_m", elements["rms"]), "creep.r0_ns_m", zero=True)
    compliance = c0*(1+beta*np.log1p(2*np.pi*corner/s))
    return r0+s*elements["mms"]+1/(s*compliance)
