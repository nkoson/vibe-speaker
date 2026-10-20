#!/usr/bin/env python3
"""Programme-integrated passive network stress and reactive amplifier-load observables."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _common import cli,apps,load_diagnostics
NAME="network_diagnostics"
VERSION="1.0"


def compute(params,base_dir):
    result=apps.module("board_nodal").compute(params["network"],base_dir)
    f=result["f_hz"];programme=params["programme"]
    voltage=cli.positive(programme["voltage_rms"],"programme.voltage_rms",zero=True)
    psd=load_diagnostics.programme_weights(f,programme)
    crest=cli.positive(programme.get("crest_factor",np.sqrt(2)),"programme.crest_factor")
    rows=[]
    for mode in result["modes"]:
        sources=[s for s in mode["sources"] if s.get("active")]
        ref=programme.get("reference_voltage_rms")
        if ref is None:
            if len(sources)!=1:raise cli.InputError("multiple-source programme needs explicit reference_voltage_rms for common scaling")
            ref=sources[0]["voltage_rms"]
        ref=cli.positive(ref,"reference_voltage_rms")
        scale=(voltage/ref)**2
        groups={}
        for name in ("components","loads"):
            groups[name]=[]
            for record in mode[name]:
                average=np.trapezoid(record["power_w"]*psd,f)*scale
                vrms=np.sqrt(np.trapezoid(record["voltage_rms"]**2*psd,f)*scale)
                irms=np.sqrt(np.trapezoid(record["current_rms_a"]**2*psd,f)*scale)
                groups[name].append(dict(id=record["id"],mean_power_w=average,voltage_rms=vrms,current_rms_a=irms,
                                        voltage_peak_with_declared_output_crest_v=crest*vrms,
                                        current_peak_with_declared_output_crest_a=crest*irms,
                                        rating=record.get("rating")))
        source_rows=[]
        for source in sources:
            z=source["input_z_ohm"]
            source_rows.append(dict(id=source["id"],epdr_ohm=load_diagnostics.epdr(z),z_ohm=z,
                                    input_mean_power_w=np.trapezoid(np.real(1/z)*psd,f)*source["voltage_rms"]**2*scale,
                                    input_current_rms_a=np.sqrt(np.trapezoid(source["current_rms_a"]**2*psd,f)*scale)))
        rows.append(dict(id=mode["id"],sources=source_rows,**groups))
    return dict(f_hz=f,normalized_psd_per_hz=psd,modes=rows,
                validity=dict(epdr_model="Ideal class-B sinusoidal output at rail swing; does not predict class-D dissipation or amplifier compatibility.",
                              crest_basis="Output crest factor is a supplied scenario, not determined from input PSD. Filtered programme peaks require waveform simulation.",
                              integration="PSD normalized over the supplied grid/band; out-of-band programme is not modeled."))


if __name__=="__main__":
    sys.exit(cli.run(NAME,VERSION,compute,__doc__,[
        "Outputs are load/stress quantities, not component sizing or amplifier acceptance decisions.",
        "See framework/references/passive-network-diagnostics.md for equations and limits."]))
