"""Panel modes, material data and the one published audibility criterion for panel radiation.

Three things live here, all from primary documents. Leissa's frequency parameters for a rectangular
plate held between pinned and clamped edges, so a panel mode can be placed as a band; the BBC's
measured material and damping-treatment data, so a panel can be computed from a material name; and
the BBC's measured perceptibility criterion, so a panel output can be judged relative to the direct
sound. Nothing here converts panel motion into an absolute SPL - the BBC established that it cannot
be done from the panels alone, because the panels, the driver and the enclosed air are coupled and
the coupling sets the level.
"""
import math

import numpy as np

from .cli import InputError

# Leissa's lambda for the fundamental of a rectangular plate, against the aspect ratio a/b with a
# the SHORTER side. K = 0 is simply supported (pinned, free to rotate), K = infinity fully clamped.
# The pinned column is exact - lambda = pi^2 (1 + (a/b)^2) - and every tabulated value reproduces it,
# which is what fixes the normalisation used here.
LEISSA_CLAMPED = [(1.0, 35.99), (0.9, 32.67), (0.8, 29.08), (0.6, 25.90), (0.4, 23.65), (0.2, 22.64)]
LEISSA_ASPECT_RANGE = (0.2, 1.0)

# Higher modes of a clamped square plate, same normalisation (Leissa Table 4.27). The pair at 131.6
# and 132.3 is why "the panel resonance" is a simplification above the first mode or two.
CLAMPED_SQUARE_MODES = [35.99, 73.41, 108.3, 131.6, 132.3, 165.2]

# BBC RD 1977/3 Tables 1 and 2, with the Wood Handbook's static-bending moduli for the panel products
# the BBC did not measure. E is at 250 Hz where the BBC measured it, which is representative of
# low-frequency cabinet panel modes; E itself varies 10 to 20 percent across 62.5 Hz to 6 kHz.
MATERIALS = {
    "birch_ply_9mm": dict(label="9 mm birch 7-ply", density_kg_m3=720.0, e_pa=7.97e9, e_along_pa=12.0e9,
                          e_across_pa=5.3e9, max_q=67.0, orthotropic=True, thickness_mm=9.0,
                          source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "birch_ply_17mm": dict(label="17 mm birch 13-ply", density_kg_m3=735.0, e_pa=7.10e9, e_along_pa=7.3e9,
                           e_across_pa=6.9e9, max_q=54.0, orthotropic=True, thickness_mm=17.0,
                           source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "mahogany_ply_10mm": dict(label="10 mm mahogany 5-ply, along outer grain", density_kg_m3=610.0, e_pa=7.9e9,
                              max_q=97.0, orthotropic=True, thickness_mm=10.0,
                              source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "blockboard_12mm": dict(label="12 mm birch-faced blockboard, along", density_kg_m3=535.0, e_pa=7.4e9,
                            max_q=68.0, thickness_mm=12.0,
                            source="BBC RD 1977/3 Tables 1 and 2; blockboard's E varies most with frequency"),
    "chipboard_16mm": dict(label="16 mm 3-layer chipboard", density_kg_m3=600.0, e_pa=1.95e9, max_q=50.0,
                           thickness_mm=16.0, source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "chipboard_18mm": dict(label="18 mm 3-layer chipboard", density_kg_m3=610.0, e_pa=2.2e9, max_q=45.0,
                           thickness_mm=18.0, source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "hardboard_10mm": dict(label="10 mm hardboard (Duopanel)", density_kg_m3=990.0, e_pa=4.8e9, max_q=51.0,
                           thickness_mm=10.0, source="BBC RD 1977/3 Tables 1 and 2, E at 250 Hz"),
    "oak_along_grain": dict(label="oak, along the grain", density_kg_m3=630.0, e_pa=14.7e9, max_q=96.0,
                           source="BBC RD 1977/3 Tables 1 and 2; across the grain E is 0.97 GPa, a factor of 15"),
    "oak_across_grain": dict(label="oak, across the grain", density_kg_m3=585.0, e_pa=0.97e9, max_q=50.0,
                             source="BBC RD 1977/3 Tables 1 and 2"),
    "beech_along_grain": dict(label="beech, along the grain", density_kg_m3=680.0, e_pa=14.6e9, max_q=125.0,
                              source="BBC RD 1977/3 Tables 1 and 2; Q = 125 rings for a long time"),
    "deal_along_grain": dict(label="deal, along the grain", density_kg_m3=570.0, e_pa=14.2e9, max_q=120.0,
                             source="BBC RD 1977/3 Tables 1 and 2"),
    "grp_random_50": dict(label="GRP, 50 % random fibres", density_kg_m3=1550.0, e_pa=10.3e9, max_q=47.0,
                          source="BBC RD 1977/3 Tables 1 and 2; best figure of merit in the table"),
    "carbon_honeycomb": dict(label="carbon fibre / honeycomb sandwich", density_kg_m3=255.0, e_pa=12.5e9, max_q=170.0,
                             source="BBC RD 1977/3 Tables 1 and 2; worst figure of merit in the table despite the "
                                    "highest stiffness-to-weight - stiffness without loss moves a resonance, it does "
                                    "not remove it"),
    "mdf": dict(label="medium-density fibreboard", density_kg_m3=800.0, e_pa=3.59e9, max_q=None,
                source="Wood Handbook FPL-GTR-282 Table 12-1, static bending; the least stiff panel product in that "
                       "table and about half the modulus of plywood. No BBC loss-factor measurement exists for it"),
    "particleboard": dict(label="particleboard", density_kg_m3=700.0, e_pa=3.45e9, max_q=None,
                          source="Wood Handbook FPL-GTR-282 Table 12-1, static bending, mid-range of 2.76 to 4.14 GPa"),
    "osb": dict(label="oriented strandboard", density_kg_m3=650.0, e_pa=5.35e9, max_q=None,
                source="Wood Handbook FPL-GTR-282 Table 12-1, static bending, mid-range of 4.41 to 6.28 GPa"),
}

# BBC RD 1977/3 Table 4, measured on a 9 mm birch 7-ply substrate: the wood-panel constrained-layer
# data that is otherwise hard to find. eta = 1/Q at the panel fundamental.
TREATMENTS = {
    "none": dict(label="nothing", q=70.0, thickness_mm=0.0),
    "mutacell_1": dict(label="1 layer Mutacell with Thixofix", q=59.0, thickness_mm=1.65),
    "mutacell_2": dict(label="2 layers Mutacell", q=35.0, thickness_mm=3.3),
    "mutacell_4": dict(label="4 layers Mutacell", q=27.0, thickness_mm=6.6),
    "roofing_felt_1": dict(label="1 layer roofing felt with Thixofix", q=47.0, thickness_mm=2.35),
    "bostik_1": dict(label="1 layer Bostik self-adhesive", q=24.0, thickness_mm=1.82),
    "bostik_2": dict(label="2 layers Bostik", q=12.0, thickness_mm=3.64),
    "bostik_3": dict(label="3 layers Bostik", q=8.5, thickness_mm=5.45),
    "aquaplas_1": dict(label="1 layer Aquaplas with Thixofix", q=10.0, thickness_mm=2.9),
    "mutacell_steel": dict(label="1 layer Mutacell + steel constraining layer + Thixofix", q=20.0, thickness_mm=2.2),
    "roofing_felt_2_steel": dict(label="2 layers roofing felt + steel constraining layer + Thixofix", q=7.0,
                                 thickness_mm=7.15),
    "celotex_1": dict(label="1 layer Celotex insulation board + Thixofix", q=39.0, thickness_mm=12.0),
}

TREATMENT_CAVEAT = ("BBC RD 1977/3 Table 4, measured on a 9 mm birch 7-ply substrate. Damping depends on the mechanical "
                    "impedance of the substrate, so these Q figures are not absolute: THE RANK ORDER ALWAYS TRANSFERS "
                    "AND THE ABSOLUTE VALUES DO NOT. A constrained layer beats a free layer - the best in the table is "
                    "two layers of felt under a steel constraining layer, eta = 0.143, ten times the bare panel and twice "
                    "what the same felt gives unconstrained - because the stiff outer layer forces the viscoelastic layer "
                    "into shear rather than extension.")

# BBC RD 1977/3 Figure 12: panel output relative to the direct axial response, above the line audible.
CRITERION_POINTS = ((100.0, -13.0), (400.0, -30.0), (10000.0, -30.0))
CRITERION_LIMITS = [
    "Scatter is about +/- 1 dB about the mean curve, with a small overlap between the audible and inaudible "
    "populations, so allow a safety margin below the line.",
    "IT HAS NO THEORETICAL BACKING WHATSOEVER. The BBC say so in those words and add that there is no obvious reason "
    "the curve should slope downwards; a curve rising with frequency would be easier to justify on directivity grounds.",
    "It is a 1977 result on 1977 programme material, measured with a pressure-gradient microphone placed so the cone's "
    "radiation falls in its null.",
    "For this empirical comparison curve, a panel "
    "resonance at 150 Hz corresponds to about 18 dB on this interpolation and one at 1 kHz needs 30 dB.",
]


def material(spec):
    """Resolve a material: a name from the table, explicit values, or a name with values overriding it."""
    spec = dict(spec or {})
    name = spec.pop("name", None)
    resolved = {}
    if name:
        key = str(name).lower()
        if key not in MATERIALS:
            raise InputError(f"unknown material name '{name}'; the table holds {sorted(MATERIALS)}")
        row = MATERIALS[key]
        resolved = dict(name=key, label=row["label"], density_kg_m3=row["density_kg_m3"],
                        youngs_modulus_pa=row["e_pa"], source=row["source"], tabulated=dict(row))
        # several of the BBC's materials are a board of a stated thickness, and that thickness is
        # part of the material's identity rather than a separate choice; an explicit value overrides
        if row.get("thickness_mm"):
            resolved["thickness_mm"] = row["thickness_mm"]
        if row.get("orthotropic"):
            resolved["orthotropy_note"] = (
                "this material is orthotropic and the plate theory applied to it is isotropic. E here is the geometric "
                "mean of the along- and across-grain moduli where both were measured. The error of that substitution is "
                "not established by any source consulted.")
    for key in ("density_kg_m3", "youngs_modulus_pa", "thickness_mm", "poisson_ratio"):
        if spec.get(key) is not None:
            resolved[key] = float(spec[key])
            resolved.setdefault("overridden", []).append(key)
    for key in ("orthotropic", "loss_factors"):
        if spec.get(key) is not None:
            resolved[key] = spec[key]
    if not resolved.get("density_kg_m3") or not resolved.get("youngs_modulus_pa"):
        raise InputError("material needs a name from the table or both density_kg_m3 and youngs_modulus_pa")
    # the BBC tabulate the figure of merit per grain direction, so it is computed from the along-grain
    # modulus where one was measured; that is what reproduces their published column
    tabulated = resolved.get("tabulated") or {}
    resolved["figure_of_merit_si"] = figure_of_merit(tabulated.get("e_along_pa") or resolved["youngs_modulus_pa"],
                                                     resolved["density_kg_m3"], tabulated.get("max_q"))
    return resolved


def figure_of_merit(e_pa, density, q):
    """The BBC's own figure of merit sqrt(E rho) / Q, higher is better, in SI.

    The report's column is headed x1e-5 while its digits are the SI value times 1e-6; the misprint is
    flagged rather than silently corrected, and what transfers is the ranking, which reproduces
    exactly - GRP best, carbon-fibre honeycomb worst, solid timber poor because Q runs to 120.
    """
    if not q:
        return None
    return dict(value=math.sqrt(float(e_pa) * float(density)) / float(q),
                bbc_tabulated_equivalent=math.sqrt(float(e_pa) * float(density)) / float(q) * 1e-6,
                note="sqrt(E rho) / Q in SI. Higher is better. Stiffness alone is not the objective: it moves a "
                     "resonance up in frequency and, if Q rises with it, into the part of the audibility curve that is "
                     "least forgiving.")


def treatment(name):
    """One damping treatment as a loss factor, with eta per millimetre, because thickness is the cost."""
    key = str(name).lower()
    if key not in TREATMENTS:
        raise InputError(f"unknown damping treatment '{name}'; the table holds {sorted(TREATMENTS)}")
    row = TREATMENTS[key]
    eta = 1 / row["q"]
    bare = 1 / TREATMENTS["none"]["q"]
    return dict(name=key, label=row["label"], q=row["q"], loss_factor=eta, thickness_mm=row["thickness_mm"],
                loss_factor_per_mm=(eta - bare) / row["thickness_mm"] if row["thickness_mm"] else None,
                gain_over_bare_panel=eta / bare, bare_panel_loss_factor=bare, caveat=TREATMENT_CAVEAT)


def treatment_ranking():
    """Every treatment ranked by loss factor gained per millimetre of thickness added."""
    rows = [treatment(name) for name in TREATMENTS if name != "none"]
    rows.sort(key=lambda r: -(r["loss_factor_per_mm"] or 0.0))
    return [dict(name=r["name"], label=r["label"], loss_factor=r["loss_factor"], thickness_mm=r["thickness_mm"],
                 loss_factor_per_mm=r["loss_factor_per_mm"]) for r in rows]


def lambda_pinned(aspect):
    """Exact: lambda = pi^2 (1 + (a/b)^2) for a simply supported rectangular plate, a the shorter side."""
    return math.pi ** 2 * (1 + float(aspect) ** 2)


def lambda_clamped(aspect):
    """Leissa's clamped values interpolated against a/b, with the extrapolation flagged rather than hidden."""
    aspect = float(aspect)
    table = sorted(LEISSA_CLAMPED)
    x = [row[0] for row in table]
    y = [row[1] for row in table]
    value = float(np.interp(aspect, x, y))
    inside = LEISSA_ASPECT_RANGE[0] <= aspect <= LEISSA_ASPECT_RANGE[1]
    return value, inside


def mode_band(a_m, b_m, thickness_m, e_pa, density, nu=0.3):
    """The fundamental of a rectangular panel as a BAND between pinned and clamped edges.

        f = lambda / (2 pi a^2) sqrt(D / rho_s)      D = E h^3 / (12 (1 - nu^2))      rho_s = rho h

    The edge condition alone moves the fundamental by a factor of 1.8 to 2.2 - nearly an octave - and
    a real glued joint is neither pinned nor clamped. A single computed number here is false precision,
    so this returns both bounds and refuses to nominate one.
    """
    a, b = float(min(a_m, b_m)), float(max(a_m, b_m))
    if min(a, thickness_m, e_pa, density) <= 0 or not 0 <= nu < 0.5:
        raise InputError("a panel mode band needs positive dimensions and material values with 0 <= nu < 0.5")
    rigidity = e_pa * thickness_m ** 3 / (12 * (1 - nu ** 2))
    surface_density = density * thickness_m
    speed = math.sqrt(rigidity / surface_density)
    aspect = a / b
    pinned = lambda_pinned(aspect)
    clamped, inside = lambda_clamped(aspect)
    scale = 1 / (2 * math.pi * a * a)
    return dict(shorter_side_m=a, longer_side_m=b, aspect_ratio=aspect,
                flexural_rigidity_nm=rigidity, surface_density_kg_m2=surface_density,
                lambda_pinned=pinned, lambda_clamped=clamped,
                lambda_ratio=clamped / pinned,
                aspect_inside_leissa_table=bool(inside),
                pinned_hz=pinned * scale * speed, clamped_hz=clamped * scale * speed,
                band_hz=[pinned * scale * speed, clamped * scale * speed],
                band_octaves=math.log2(clamped / pinned),
                boundary_condition_basis="the edge condition alone moves this frequency by a factor of 1.8 to 2.2. A glued "
                                     "butt joint into a thin panel is much nearer pinned than clamped, a thick panel "
                                     "into a rebate with a glue block is nearer clamped, and neither is either. The band compares these idealized restraints rather than certifying a real joint.",
                optimistic_at_the_bottom="worked on the BBC's own LS3/6 cabinet this bracket gives 196 to 393 Hz for the "
                                         "side panel, and the BBC's measurement of that cabinet peaks near 150 Hz - "
                                         "below even the pinned bound - because a real panel carries the driver's "
                                         "reaction mass and sits on joints with real compliance. Use the band to know "
                                         "which octave to worry about, never as a notch frequency.",
                clamped_source="Leissa Table 4.30 interpolated against a/b; the clamped square value 35.99 is Leissa's "
                               "accurate figure and Galin's closed form gives exactly 36." if inside else
                               "EXTRAPOLATED: a/b lies outside Leissa's tabulated 0.2 to 1.0 and the clamped bound is "
                               "held at the nearest tabulated value.")


def audibility_criterion_db(f):
    """The BBC perceptibility criterion in dB relative to the direct axial response; above it, audible.

    About -13 dB at 100 Hz, falling linearly on a log-frequency axis to about -30 dB at roughly
    400 Hz, then flat at -30 dB to 10 kHz.
    """
    f = np.atleast_1d(np.asarray(f, float))
    low, mid, high = CRITERION_POINTS
    out = np.interp(np.log(f), [math.log(low[0]), math.log(mid[0]), math.log(high[0])],
                    [low[1], mid[1], high[1]])
    return out


def criterion_extrapolated(f):
    """Where the criterion is being read outside the band the BBC actually plotted."""
    f = np.atleast_1d(np.asarray(f, float))
    return (f < CRITERION_POINTS[0][0]) | (f > CRITERION_POINTS[-1][0])


def criterion_record(f):
    return dict(f_hz=np.asarray(f, float), criterion_db=audibility_criterion_db(f),
                extrapolated=criterion_extrapolated(f),
                shape="about -13 dB at 100 Hz, falling linearly on a log-frequency axis to about -30 dB at roughly "
                      "400 Hz, then flat at about -30 dB from 400 Hz to 10 kHz. Panel output ABOVE this line was "
                      "audible in the BBC's listening tests; below it, inaudible.",
                scatter_db=1.0, limits=list(CRITERION_LIMITS),
                source="BBC RD 1977/3 Figure 12")
