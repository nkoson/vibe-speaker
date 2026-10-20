"""Cached geometric pressure basis for caller-defined spatial fitting objectives."""
import numpy as np
from . import cli, radiation, preference, acoustics


def basis(sections,f,distance,ear):
    for section in sections:
        for record in [section]+section["outlets"]:
            model=record["directivity"];kind=model["kind"]
            if kind=="measured_planes":
                from .response_data import full_sphere
                complete=full_sphere(model)
            elif kind=="complex_grid":
                complete=min(model["horizontal_deg"])<=-180 and max(model["horizontal_deg"])>=180 and min(model["vertical_deg"])<=-90 and max(model["vertical_deg"])>=90
            else:
                complete=kind in ("omni","dipole","cardioid","distributed_edge_dipole") or bool(record.get("rear"))
            if not complete:raise cli.InputError("spatial fitting requires explicitly complete source angular coverage")
    out={}
    for plane in ("H","V"):
        angles=[preference.signed(a) for p,a in preference.spin_angles() if p==plane]
        _,parts=radiation.pressure(sections,f,radiation.observation_points(distance,ear,angles,plane),
                                   distance,transfers=[np.ones(len(f),complex)]*len(sections))
        for i,a in enumerate(angles):out[(plane,a)]=parts[:,i,:]
    return out


def curves(basis,transfers,voltage,options):
    h=np.asarray(transfers)
    orbit={key:abs(np.sum(parts*h,axis=0)) for key,parts in basis.items()}
    family=preference.assemble(None,orbit,options.get("rear_wall","standard"),bool(options.get("double_90_degree_weight",False)))
    out={name:acoustics.db(family[name]*voltage/cli.P0) for name in
         ("on_axis","listening_window","early_reflections","sound_power","predicted_in_room")}
    out.update(sound_power_di=family["sound_power_di_db"],early_reflections_di=family["early_reflections_di_db"])
    return out


def regression(f,curves):
    if f.min()>100 or f.max()<16000:
        raise cli.InputError("preference objective requires coverage of 100..16000 Hz and resolved LF extension")
    a=preference.nbd(f,curves["on_axis"]);b=preference.nbd(f,curves["predicted_in_room"])
    c=preference.lfx(f,curves["sound_power"],curves["listening_window"])
    d=preference.smoothness(f,curves["predicted_in_room"])
    if c is None or c["bound"]!="resolved" or d is None or d["value"] is None:
        raise cli.InputError("preference objective has unresolved LF extension or smoothness")
    return preference.preference_score(a["value"],b["value"],c["value"],d["value"])
