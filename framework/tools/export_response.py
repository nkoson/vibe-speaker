"""Export a computed complex curve or discrete impulse with a provenance sidecar."""
import argparse
import hashlib
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli


def export(input_path,path,output_path,format,frequency_path="results.f_hz",
           sample_rate_path="results.time_domain.sample_rate_hz",quantity="pressure"):
    document=cli.load_json(input_path)
    if document.get("status")!="computed":
        raise cli.InputError("export requires a computed simulation document")
    value=cli.dotted(document,path)
    output=Path(output_path)
    if format=="wav":
        samples=np.asarray(value,float)
        rate=float(cli.dotted(document,sample_rate_path))
        if rate!=int(rate) or samples.ndim!=1 or not np.all(np.isfinite(samples)):
            raise cli.InputError("WAV export needs finite discrete impulse samples and integer sample rate")
        wavfile.write(output,int(rate),samples.astype(np.float32))
        convention="float32 discrete impulse coefficients; no peak normalization"
    else:
        f=np.asarray(cli.dotted(document,frequency_path),float)
        z=cli.complex_from_record(value)
        if z.shape!=f.shape:raise cli.InputError("export curve and frequency shapes differ")
        if format=="csv":
            data=np.c_[f,z.real,z.imag];header="frequency_hz,real,imag";delimiter=","
        else:
            if format=="zma":
                magnitude=abs(z)
            elif format=="frd":
                magnitude=20*np.log10(np.maximum(abs(z)/(cli.P0 if quantity=="pressure" else 1),1e-30))
            else:raise cli.InputError("format needs csv, frd, zma or wav")
            data=np.c_[f,magnitude,np.rad2deg(np.unwrap(np.angle(z)))]
            header="Hz magnitude phase_deg";delimiter=" "
        np.savetxt(output,data,delimiter=delimiter,header=header,comments="" if format=="csv" else "# ",fmt="%.17g")
        convention=f"{quantity}; exp(+jwt); supplied normalization retained"
    metadata=dict(input_file=str(input_path),input_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
                  simulation=document["simulation"],version=document["version"],path=path,format=format,
                  convention=convention,source_contract=document.get("results",{}).get("source_contract"),
                  output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    cli.write_document(str(output)+".json",metadata)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True);parser.add_argument("--path",required=True)
    parser.add_argument("--out",required=True);parser.add_argument("--format",choices=["csv","frd","zma","wav"],required=True)
    parser.add_argument("--quantity",choices=["pressure","transfer","impedance"],default="pressure")
    parser.add_argument("--frequency-path",default="results.f_hz")
    parser.add_argument("--sample-rate-path",default="results.time_domain.sample_rate_hz")
    args=parser.parse_args()
    export(args.input,args.path,args.out,args.format,args.frequency_path,args.sample_rate_path,args.quantity)
