"""Electrical load resolution and evidence. Diagnostics describe, never accept/reject."""
import copy
import hashlib
import json
import numpy as np
from . import cli, acoustics


CONTRACT_VERSION = 1
INTERPRETATION = "Electrical evidence and numerical observations for agent interpretation; no fit-quality or design acceptance decision."


def identity(model):
    return hashlib.sha256(json.dumps(cli.to_jsonable(model), sort_keys=True).encode()).hexdigest()


def describe(model, f, metadata=None):
    """Record what was supplied, without inferring a support band from an evaluation grid."""
    model = copy.deepcopy(model)
    embedded = model.pop("electrical_load", model.pop("contract", {})) or {}
    metadata = dict(embedded, **(metadata or {}))
    kind = model.get("kind", "unspecified")
    ts = model.get("ts", model if kind in ("blocked", "resonant") else {})
    inductance = ts.get("inductance_model")
    assumptions = []
    if ts and not inductance:
        inductance = dict(kind="constant", le_mh=ts.get("le_mh", 0))
        assumptions.append("legacy_constant_inductance_from_ts")
    record = dict(contract_version=CONTRACT_VERSION, identity=identity(model),
                  model=model, inductance_model=inductance,
                  impedance_scope="blocked" if kind == "blocked" else "terminal",
                  units="ohm", evidence=[], supported_band_hz=None,
                  phase_basis="analytical_model" if kind not in ("curve", "reference", "zma_file") else "unspecified",
                  alternatives=[], transformations=[], assumptions=assumptions)
    record.update(copy.deepcopy(metadata))
    # An identity for the supplied realization, distinct from caller's reference identity.
    record["model_identity"] = identity(model)
    return observe(record, f)


def observe(record, f, z=None):
    record = copy.deepcopy(record)
    f = np.asarray(f, float)
    band = record.get("supported_band_hz")
    observations = dict(requested_band_hz=[float(f.min()), float(f.max())],
                        missing_evidence=not bool(record.get("evidence")),
                        support_band_stated=band is not None,
                        phase_basis=record.get("phase_basis", "unspecified"),
                        outside_supported_band_points=None if band is None else int(np.count_nonzero((f < band[0]) | (f > band[1]))))
    if z is not None:
        z = np.asarray(z, complex)
        observations.update(negative_real_points=int(np.count_nonzero(z.real < 0)),
                            nonfinite_points=int(np.count_nonzero(~np.isfinite(z))),
                            minimum_real_ohm=float(np.nanmin(z.real)))
    record["observations"] = observations
    record["interpretation"] = INTERPRETATION
    return record


def from_document(document, path, f):
    """Find metadata beside a curve, with a root fallback for older LF producers."""
    parent = cli.dotted(document, path.rsplit(".", 1)[0])
    record = None
    if isinstance(parent, dict):
        record = parent.get("load_contract") or parent.get("source_contract", {}).get("electrical_load")
    root = document.get("results", {})
    record = record or root.get("load_contract") or root.get("source_contract", {}).get("electrical_load")
    if record:
        return observe(record, f)
    inputs = document.get("inputs", {})
    model = inputs.get("impedance")
    if not model and inputs.get("driver", {}).get("ts"):
        model = dict(kind=inputs.get("enclosure", {}).get("type", "free_air"),
                     ts=inputs["driver"]["ts"], enclosure=inputs.get("enclosure", {}))
    record = describe(model or dict(kind="referenced_curve"), f)
    if model is None:
        record.update(identity=None, model_identity=None, phase_basis="unspecified_from_reference")
    record["assumptions"].append("upstream_electrical_contract_absent")
    return record


def resolve(spec, f, base_dir, metadata=None):
    """Resolve all supported inline/file forms to (complex impedance, evidence)."""
    spec = copy.deepcopy(spec)
    kind = spec.get("kind")
    ref = spec.get("reference") if kind == "reference" else spec if "file" in spec and kind != "zma_file" else None
    if ref is not None:
        ref = dict(ref)
        ref.setdefault("frequency_path", "results.f_hz")
        ref.setdefault("path", "results.z_ohm")
        doc = cli.load_json(cli.resolve_path(ref["file"], base_dir))
        z = cli.curve_from_reference(ref, base_dir, f)
        record = from_document(doc, ref["path"], f)
        if record.get("identity") is None:
            record["identity"] = identity(dict(f_hz=cli.dotted(doc,ref["frequency_path"]), curve=cli.dotted(doc,ref["path"])))
        source_f = np.asarray(cli.dotted(doc, ref["frequency_path"]), float)
        record["transformations"].append(dict(operation="curve_reference", file=ref["file"], path=ref["path"],
                                              interpolation=ref.get("interpolation", "polar"), extrapolation=ref.get("extrapolation", "hold")))
    elif kind == "zma_file":
        table = np.loadtxt(cli.resolve_path(spec["file"], base_dir), comments=["#", "*", ";"], ndmin=2)
        source_f = table[:, 0]
        phase = np.deg2rad(table[:, 2]) if table.shape[1] > 2 else np.zeros(len(table))
        z = cli.interp_complex(f, source_f, table[:, 1] * np.exp(1j * phase))
        record = describe(spec, f)
        record["identity"] = identity(dict(f_hz=source_f, magnitude=table[:, 1], phase=phase))
        record["phase_basis"] = "supplied" if table.shape[1] > 2 else "assumed_zero_missing_phase"
        record["transformations"].append(dict(operation="zma_import", file=spec["file"], phase_operation=record["phase_basis"], extrapolation="hold"))
    else:
        z = acoustics.impedance_model(spec, f)
        record = describe(spec, f)
        source_f = np.asarray(spec["frequency_hz"], float) if kind == "curve" else None
        if kind == "curve":
            record["phase_basis"] = "supplied_complex"
            record["transformations"].append(dict(operation="curve_interpolation", interpolation="cartesian_log_frequency", extrapolation="hold"))
    supplied = dict(spec.get("electrical_load", spec.get("contract", {})) or {}, **(metadata or {}))
    record.update(copy.deepcopy(supplied))
    if source_f is not None:
        record["sampled_band_hz"] = [float(source_f.min()), float(source_f.max())]
        record["extrapolated_points"] = int(np.count_nonzero((f < source_f.min()) | (f > source_f.max())))
        record["transformations"].append(dict(operation="sampling_coverage",
            sampled_band_hz=record["sampled_band_hz"], requested_band_hz=[float(np.min(f)),float(np.max(f))],
            extrapolated_points=record["extrapolated_points"]))
    return z, observe(record, f, z)


def section(section, f, base_dir):
    pressure = None
    record = None
    z = None
    if section.get("source"):
        ref = dict(section["source"])
        ref.setdefault("frequency_path", "results.f_hz")
        z, record = resolve(dict(ref, path=ref.get("impedance_path", "results.z_ohm")), f, base_dir)
        try:
            pressure = cli.curve_from_reference(dict(ref, path=ref.get("pressure_path", "results.pressure_per_volt_pa")), base_dir, f)
        except cli.InputError:
            pass  # Electrical-only sources have no acoustic curve.
    if section.get("load"):
        previous = record
        z, record = resolve(section["load"], f, base_dir)
        if previous:
            record["transformations"].append(dict(operation="explicit_load_override", previous_identity=previous.get("identity"),
                                                  acoustic_pressure="retained_from_source"))
    if z is None:
        raise cli.InputError(f"section '{section.get('name')}' has no computable load")
    if section.get("electrical_load"):
        record.update(copy.deepcopy(section["electrical_load"]))
    return z, pressure, observe(record, f, z)


def fit_cases(params):
    """Same alternative-load interface for ladder and nodal fitting. No probabilities."""
    cases = [dict(name="nominal", loads={}, sources={}, weight=1.)] + copy.deepcopy(params.get("load_scenarios", []))
    for index, case in enumerate(cases):
        case.setdefault("name", f"alternative_{index}")
    return cases


def case_inputs(sections, system, case, nodal=False):
    sections = copy.deepcopy(sections)
    system = copy.deepcopy(system)
    used = []
    source_keys = set()
    for i, section in enumerate(sections):
        key = section.get("id") if nodal else section.get("name", str(i))
        if key in case.get("loads", {}):
            section["impedance" if nodal else "load"] = copy.deepcopy(case["loads"][key])
            used.append(key)
        if not nodal and key in case.get("sources", {}):
            source_keys.add(key)
            section["source"] = copy.deepcopy(case["sources"][key])
            if key not in case.get("loads", {}):
                section.pop("load", None)
    if system:
        for section in system["sections"]:
            key = section.get("load_id") if nodal else section.get("name")
            if key in case.get("sources", {}):
                source_keys.add(key)
                section["source"] = copy.deepcopy(case["sources"][key])
    return sections, system, dict(changed_loads=used,
        unmatched_load_keys=sorted(set(case.get("loads", {}))-set(used)),
        unmatched_source_keys=sorted(set(case.get("sources", {}))-source_keys),
        acoustic_basis="replacement_sources_supplied" if case.get("sources") else "unchanged_acoustic_sources_electrical_sensitivity_probe",
        physical_consistency_basis=case.get("basis"), probability=None)


def combine_residuals(residuals, cases, spec=None):
    """Caller-selected aggregation; default preserves the nominal objective."""
    spec = spec or {}
    mode = spec.get("mode", "nominal")
    if mode == "worst_case":
        return residuals[int(np.argmax([np.mean(r*r) for r in residuals]))]
    if mode == "weighted_mean":
        weights = np.asarray([spec.get("weights", {}).get(c["name"], c.get("weight", 1.)) for c in cases], float)
        weights = np.maximum(weights, 0)
        if weights.sum() > 0:
            return np.concatenate([r * np.sqrt(w/weights.sum()) for r,w in zip(residuals,weights)])
    return residuals[0]


def combine_costs(costs, cases, spec=None):
    spec = spec or {}
    if spec.get("mode") == "worst_case":
        return float(max(costs))
    if spec.get("mode") == "weighted_mean":
        weights = np.maximum([spec.get("weights", {}).get(c["name"], c.get("weight", 1.)) for c in cases], 0)
        if weights.sum() > 0:
            return float(np.average(costs, weights=weights))
    return float(costs[0])


def inventory(result):
    """Retain evidence before temporary scenario outputs disappear."""
    rows=[]
    def visit(value, path):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in ("load_contract","electrical_load") and isinstance(item,dict) and "contract_version" in item:
                    rows.append(dict(path=path+"."+key,contract=copy.deepcopy(item)))
                else:
                    visit(item,path+"."+key)
        elif isinstance(value,list):
            for index,item in enumerate(value):visit(item,path+"."+str(index))
    visit(result,"results")
    return rows


def aggregation(cases, spec=None):
    spec = spec or {}
    requested = spec.get("mode", "nominal")
    supplied = [spec.get("weights", {}).get(c["name"], c.get("weight", 1.)) for c in cases]
    weights = np.maximum(supplied, 0)
    effective = requested if requested in ("nominal", "weighted_mean", "worst_case") else "nominal"
    if effective == "weighted_mean" and weights.sum() == 0:
        effective = "nominal"
    return dict(requested_mode=requested, effective_mode=effective,
                supplied_weights=dict(zip([c["name"] for c in cases], supplied)),
                nonnegative_weights=dict(zip([c["name"] for c in cases], weights.tolist())),
                probability_basis=None)
