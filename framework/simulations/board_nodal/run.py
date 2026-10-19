#!/usr/bin/env python3
"""Nodal AC solution of a physical crossover board: components, wires, input terminals and driver loads in every connection mode."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics  # noqa: E402

NAME = "board_nodal"
VERSION = "1.0"
NOTES = [
    "Complex nodal analysis with ideal voltage sources at the active input terminals; zero-ohm wires merge nodes, so their individual currents are indeterminate and finite wire resistances are needed for wire current figures.",
    "An inactive source leaves its terminals open. A floating sub-network without any fixed potential is referenced to 0 V at one node so the matrix stays solvable; it carries no current.",
    "Coil DCR and capacitor ESR default as in crossover_network when absent; ratings are echoed with the computed maxima, the comparison is yours.",
    "Tolerance draws scale each component independently by uniform spreads.",
]


class Nodes:
    def __init__(self):
        self.parent = {}

    def add(self, node):
        self.parent.setdefault(node, node)

    def root(self, node):
        self.add(node)
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def join(self, a, b):
        ra, rb = self.root(a), self.root(b)
        if ra != rb:
            self.parent[rb] = ra


def _component_z(component, f, scale=None):
    kind = component["type"]
    factor = 1.0 if not scale else float(scale.get(component["id"], 1.0))
    s = 2j * np.pi * f
    if kind == "R":
        return np.full(len(f), float(component["value_ohm"]) * factor, complex)
    if kind == "L":
        dcr = component.get("dcr_ohm")
        l_mh = float(component["value_mh"]) * factor
        return (acoustics.default_coil_dcr(l_mh) if dcr is None else float(dcr)) + s * l_mh * 1e-3
    if kind == "C":
        return float(component.get("esr_ohm", 0.01)) + 1 / (s * float(component["value_uf"]) * 1e-6 * factor)
    raise cli.InputError(f"component '{component.get('id')}' has unknown type '{kind}'")


def _load_z(load, f, base_dir):
    z = load.get("impedance")
    if isinstance(z, dict) and "file" in z:
        ref = dict(z)
        ref.setdefault("frequency_path", "results.f_hz")
        return cli.curve_from_reference(ref, base_dir, f)
    return acoustics.impedance_model(z, f)


def solve(f, components, wires, sources, loads, mode, load_z, scale=None):
    """Solve one connection mode; returns per-edge states, source currents and load transfers."""
    nodes = Nodes()
    edges = []
    for c in components:
        a, b = c["nodes"]
        nodes.add(a)
        nodes.add(b)
        edges.append((c["id"], a, b, _component_z(c, f, scale), "component"))
    for w in wires:
        nodes.add(w["from"])
        nodes.add(w["to"])
        if float(w.get("resistance_ohm", 0.0)) <= 0:
            nodes.join(w["from"], w["to"])
        else:
            edges.append((w["id"], w["from"], w["to"], np.full(len(f), float(w["resistance_ohm"]), complex), "wire"))
    for load in loads:
        nodes.add(load["plus"])
        nodes.add(load["minus"])
        edges.append((load["id"], load["plus"], load["minus"], load_z[load["id"]], "load"))
    for a, b in mode.get("links", []):
        nodes.join(a, b)
    active = mode.get("active_sources") or [s["id"] for s in sources]
    fixed = {}
    for src in sources:
        nodes.add(src["plus"])
        nodes.add(src["minus"])
        if src["id"] in active:
            v = float(src.get("voltage_rms", 1.0)) * np.exp(1j * np.deg2rad(float(src.get("phase_deg", 0.0))))
            for pin, level in ((src["plus"], v), (src["minus"], 0.0)):
                root = nodes.root(pin)
                if root in fixed and abs(fixed[root] - level) > 1e-12:
                    raise cli.InputError(f"mode '{mode.get('id')}': linked sources demand different potentials at one node")
                fixed[root] = level
    roots = {nodes.root(n) for n in nodes.parent}
    # Reference every floating connected group to 0 V at one node.
    adjacency = {r: set() for r in roots}
    for _, a, b, _, _ in edges:
        ra, rb = nodes.root(a), nodes.root(b)
        adjacency[ra].add(rb)
        adjacency[rb].add(ra)
    seen = set()
    for r in sorted(roots):
        if r in seen:
            continue
        group = []
        stack = [r]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            group.append(n)
            stack.extend(adjacency[n] - seen)
        if not any(g in fixed for g in group):
            fixed[sorted(group)[0]] = 0.0
    unknown = sorted(roots - fixed.keys())
    index = {n: i for i, n in enumerate(unknown)}
    n = len(unknown)
    matrix = np.zeros((len(f), n, n), complex)
    rhs = np.zeros((len(f), n), complex)
    # Branch impedance admits mutual inductance without changing the circuit graph.
    impedance = np.zeros((len(f), len(edges), len(edges)), complex)
    for ei, edge in enumerate(edges):
        impedance[:, ei, ei] = edge[3]
    edge_index = {edge[0]: i for i, edge in enumerate(edges)}
    coils = {c["id"]: c for c in components if c["type"] == "L"}
    applied = {}
    for cid, coil in coils.items():
        for other, coupling in coil.get("mutual_with", {}).items():
            if other not in coils or other == cid or abs(float(coupling)) >= 1:
                raise cli.InputError("mutual_with needs another coil and -1 < coupling < 1")
            pair = tuple(sorted((cid, other)))
            if pair in applied and applied[pair] != coupling:
                raise cli.InputError("conflicting mutual coupling declarations")
            applied[pair] = coupling
            l1 = float(coil["value_mh"]) * (1 if not scale else scale.get(cid,1)) * 1e-3
            l2 = float(coils[other]["value_mh"]) * (1 if not scale else scale.get(other,1)) * 1e-3
            mutual = float(coupling) * np.sqrt(l1*l2)
            impedance[:,edge_index[cid],edge_index[other]] = 2j*np.pi*f*mutual
            impedance[:,edge_index[other],edge_index[cid]] = 2j*np.pi*f*mutual
    if coils:
        ci=[edge_index[k] for k in coils]
        inductance=impedance[0][np.ix_(ci,ci)].imag/(2*np.pi*f[0])
        if np.linalg.eigvalsh(inductance).min() <= 0:
            raise cli.InputError("coupled inductance matrix is not positive definite")
    branch_y = np.linalg.inv(impedance)
    incidence = np.zeros((n,len(edges)))
    fixed_drop = np.zeros((len(f),len(edges)),complex)
    for ei,(_,a,b,_,_) in enumerate(edges):
        for pin, sign in ((a,1),(b,-1)):
            root=nodes.root(pin)
            if root in index: incidence[index[root],ei]+=sign
            else: fixed_drop[:,ei]+=sign*fixed[root]
    # Contract in stages rather than enumerating the full five-index product.
    # This is the same nodal stamp, including declared mutual inductance.
    matrix = np.einsum('ie,fej,kj->fik',incidence,branch_y,incidence,optimize=True)
    rhs = -np.einsum('ie,fej,fj->fi',incidence,branch_y,fixed_drop,optimize=True)
    if n:
        try:
            values = np.linalg.solve(matrix, rhs[..., None])[..., 0]
        except np.linalg.LinAlgError as exc:
            raise cli.InputError(f"mode '{mode.get('id')}': singular circuit (open connection or floating network)") from exc
        residual = np.max(np.abs((matrix @ values[..., None])[..., 0] - rhs), axis=1) / np.maximum(np.max(np.abs(rhs), axis=1), 1e-12)
    else:
        values = np.zeros((len(f), 0), complex)
        residual = np.zeros(len(f))

    def voltage(pin):
        root = nodes.root(pin)
        return values[:, index[root]] if root in index else np.full(len(f), fixed[root], complex)

    states = {}
    boundary = {root: np.zeros(len(f), complex) for root in fixed}
    drops = np.array([voltage(a)-voltage(b) for _,a,b,_,_ in edges]).T
    currents = (branch_y @ drops[...,None])[...,0]
    for ei, (name, a, b, z, kind) in enumerate(edges):
        drop = drops[:,ei]
        current = currents[:,ei]
        states[name] = dict(kind=kind, voltage=drop, current=current, power=np.abs(current) ** 2 * z.real)
        for pin, sign in ((a, 1), (b, -1)):
            root = nodes.root(pin)
            if root in boundary:
                boundary[root] += sign * current
    supply = sum(np.real(np.conj(current) * fixed[root]) for root, current in boundary.items())
    dissipated = sum(st["power"] for st in states.values())
    power_residual = np.abs(supply - dissipated) / np.maximum(np.abs(supply), 1e-12)
    src_rows = []
    for src in sources:
        if src["id"] not in active:
            src_rows.append(dict(id=src["id"], active=False))
            continue
        current = boundary[nodes.root(src["plus"])]
        v = float(src.get("voltage_rms", 1.0)) * np.exp(1j*np.deg2rad(float(src.get("phase_deg",0))))
        with np.errstate(divide="ignore", invalid="ignore"):
            zin = np.where(np.abs(current) > 1e-15, v / current, np.inf)
        src_rows.append(dict(id=src["id"], active=True, voltage_rms=abs(v), current_rms_a=np.abs(current), input_z_ohm=zin))
    reference_v = next((float(s.get("voltage_rms", 1.0)) for s in sources if s["id"] in active), 1.0)
    load_rows = [dict(id=load["id"], transfer=states[load["id"]]["voltage"] / reference_v, voltage_rms=np.abs(states[load["id"]]["voltage"]),
                      current_rms_a=np.abs(states[load["id"]]["current"]), power_w=states[load["id"]]["power"]) for load in loads]
    return dict(states=states, sources=src_rows, loads=load_rows, kcl_relative_residual=float(residual.max()),
                power_relative_residual=float(power_residual.max()), reference_voltage_rms=reference_v)


VALIDITY = [
    "Lumped nodal solve: valid while every part and every wire run is short compared with a wavelength. At 20 kHz that is about 17 mm per degree of phase, so the board layout, not the netlist, is the limit at the top of the band.",
    "Declared mutual inductance and finite-magnetizing-inductance transformers are modeled. Geometry does not determine coupling automatically; stray fields and nonlinear core saturation are outside this AC solve.",
    "The residuals reported are the solver's own consistency, not agreement with a measurement.",
]


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 40000.0, 600)
    components = list(cli.require(params, "components"))
    for transformer in params.get("transformers", []):
        pid,sid=transformer["id"]+":primary",transformer["id"]+":secondary"
        lp=cli.positive(transformer["primary_inductance_mh"],"primary_inductance_mh")
        ratio=cli.positive(transformer["turns_ratio"],"turns_ratio")
        components.extend([dict(id=pid,type="L",nodes=transformer["primary_nodes"],value_mh=lp,
                                dcr_ohm=transformer["primary_dcr_ohm"],mutual_with={sid:transformer["coupling"]}),
                           dict(id=sid,type="L",nodes=transformer["secondary_nodes"],value_mh=lp/ratio**2,
                                dcr_ohm=transformer["secondary_dcr_ohm"])])
    wires = params.get("wires") or []
    sources = cli.require(params, "sources")
    loads = cli.require(params, "loads")
    modes = params.get("modes") or [dict(id="all_sources", links=[], active_sources=[s["id"] for s in sources])]
    ids = [c["id"] for c in components] + [w["id"] for w in wires] + [l["id"] for l in loads]
    if len(set(ids)) != len(ids):
        raise cli.InputError("component, wire and load ids must be unique")
    load_z = {load["id"]: _load_z(load, f, base_dir) for load in loads}
    tol = params.get("tolerances") or {}
    draws = int(tol.get("draws", 0))
    rng = np.random.default_rng(int(tol.get("seed", 9919)))
    spreads = {"C": float(tol.get("C", 0.05)), "L": float(tol.get("L", 0.03)), "R": float(tol.get("R", 0.02))}
    rows = []
    for mode in modes:
        sol = solve(f, components, wires, sources, loads, mode, load_z)
        comp_rows = []
        for c in components:
            st = sol["states"][c["id"]]
            i = int(np.argmax(st["power"]))
            row = dict(id=c["id"], type=c["type"], max_voltage_rms=float(np.abs(st["voltage"]).max()), max_current_rms_a=float(np.abs(st["current"]).max()),
                       max_power_w=float(st["power"][i]), max_power_hz=float(f[i]), voltage_rms=np.abs(st["voltage"]), current_rms_a=np.abs(st["current"]), power_w=st["power"])
            if c.get("rating"):
                row["rating"] = c["rating"]
            comp_rows.append(row)
        wire_rows = [dict(id=w["id"], resistance_ohm=w.get("resistance_ohm", 0.0), max_current_rms_a=float(np.abs(sol["states"][w["id"]]["current"]).max()),
                          max_power_w=float(sol["states"][w["id"]]["power"].max())) for w in wires if float(w.get("resistance_ohm", 0.0)) > 0]
        entry = dict(id=mode.get("id"), links=mode.get("links", []), active_sources=mode.get("active_sources") or [s["id"] for s in sources],
                     sources=sol["sources"], loads=sol["loads"], components=comp_rows, wires=wire_rows,
                     kcl_relative_residual=sol["kcl_relative_residual"], power_relative_residual=sol["power_relative_residual"])
        for src in entry["sources"]:
            if src.get("active"):
                zmag = np.abs(src["input_z_ohm"])
                aud = (f >= 20) & (f <= 20000)
                src["input_z_min_ohm"] = float(np.min(zmag[aud]))
                src["input_z_min_hz"] = float(f[aud][np.argmin(zmag[aud])])
        if draws:
            samples = {load["id"]: [] for load in loads}
            for _ in range(draws):
                scale = {c["id"]: 1 + rng.uniform(-1, 1) * float(c.get("tolerance_fraction", spreads.get(c["type"], 0.0))) for c in components}
                trial = solve(f, components, wires, sources, loads, mode, load_z, scale)
                for row in trial["loads"]:
                    samples[row["id"]].append(acoustics.db(row["transfer"]))
            entry["tolerance"] = dict(draws=draws, loads=[dict(id=k, transfer_db_p5=np.percentile(v, 5, axis=0), transfer_db_p50=np.percentile(v, 50, axis=0),
                                                            transfer_db_p95=np.percentile(v, 95, axis=0)) for k, v in samples.items()])
        rows.append(entry)
    return dict(f_hz=f, modes=rows, component_count=len(components), wire_count=len(wires))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Nodal solution of a physical crossover board", NOTES, VALIDITY))
