#!/usr/bin/env python3
"""Collect objective observations and numerical differences without design verdicts."""
import argparse,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"simulations"))
from _common import cli

def collect(project,base_dir):
    rows=[]
    for objective in project.get("objectives",[]):
        source=objective.get("result_reference");value=None;error=None
        if source:
            try:
                raw=cli.file_reference(source,base_dir)
                if isinstance(raw,dict) and "real" in raw:raw=abs(cli.complex_from_record(raw))
                operation=source.get("reduce","scalar")
                if raw is not None:value=float({"scalar":float,"min":np.min,"max":np.max,"mean":np.mean,"rms":lambda x:np.sqrt(np.mean(np.abs(x)**2))}[operation](raw))
            except (cli.InputError,ValueError,TypeError) as exc:error=str(exc)
        target=objective.get("target");tolerance=objective.get("tolerance")
        rows.append(dict(name=objective["name"],value=value,target=target,tolerance=tolerance,
                         value_minus_target=None if value is None or target is None else value-target,
                         direction=objective.get("direction"),priority=objective.get("priority"),
                         conditions=objective.get("conditions"),result_reference=source,input_error=error))
    return dict(objectives=rows,assumptions=project.get("assumptions",[]),
                interpretation="Observations and signed differences only; the agent interprets priorities, tolerances and design tradeoffs.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    cli.write_document(a.out,collect(cli.load_json(a.input),Path(a.input).resolve().parent))
