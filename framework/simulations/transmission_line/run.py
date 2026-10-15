#!/usr/bin/env python3
"""Tapered quarter-wave line length, its modes and the driver offset that suppresses the three-quarter-wave one."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics  # noqa: E402

NAME = "transmission_line"
VERSION = "1.1"
NOTES = [
    "Length from the taper-factor table: L = SF c / (4 fb). Never use L = c / (4 fb) for a tapered line; the taper factor spans 0.62 to 1.42 across the published taper ratios and the untapered value is only the SF = 1 case.",
    "Stuffing slows propagation: a measured 342 m/s falls to about 319 m/s, an asymptote reached by about 0.6 lb/ft^3, so a stuffed line tunes lower than an unstuffed length calculation predicts. Both lengths are reported.",
    "Equal-volume comparisons depend on taper, driver position, stuffing, terminus load and cutoff definition; compare complete responses rather than treating one published comparison as a universal rule.",
    "This is length and mode arithmetic only. There is no line response, no stuffing loss model, no terminus radiation and no driver in it; lf_box does not model a transmission line at all.",
    "All of it rests on one self-published modelling site, and the advantages claimed for the loading are asserted without numbers.",
]
VALIDITY = [
    "A tuning-length calculation, not a response. Nothing here predicts the level, the ripple or the group delay of the line.",
    "The taper-factor table is an interpolation over nine published points from one self-published source; taper ratios outside 0.1 to 10 are extrapolation and are reported as such.",
    "The stuffed speed of sound is one measured figure for one material at one density. A different fibre at a different packing gives a different number, and nothing here predicts which.",
]

# Taper factor against taper ratio TR = S_terminus / S_throat, as published.
TAPER_TABLE = [(0.1, 0.62), (0.2, 0.71), (0.33, 0.80), (0.5, 0.87), (1.0, 1.00),
               (2.0, 1.14), (3.0, 1.22), (5.0, 1.32), (10.0, 1.42)]

UNSTUFFED_C = 342.0
STUFFED_C = 319.0


def taper_factor(ratio):
    ratios = np.array([r for r, _ in TAPER_TABLE])
    factors = np.array([s for _, s in TAPER_TABLE])
    return float(np.interp(np.log(ratio), np.log(ratios), factors)), bool(ratios[0] <= ratio <= ratios[-1])


def compute(params, base_dir):
    line = cli.require(params, "line")
    fb = cli.positive(line.get("tuning_hz"), "line.tuning_hz")
    throat = cli.positive(line.get("throat_area_cm2"), "line.throat_area_cm2") * 1e-4
    terminus = cli.positive(line.get("terminus_area_cm2"), "line.terminus_area_cm2") * 1e-4
    ratio = terminus / throat
    factor, inside = taper_factor(ratio)
    speeds = dict(unstuffed=float(line.get("unstuffed_speed_m_s", UNSTUFFED_C)),
                  stuffed=float(line.get("stuffed_speed_m_s", STUFFED_C)),
                  model_constant=acoustics.C)
    lengths = {name: factor * speed / (4 * fb) for name, speed in speeds.items()}

    # The taper factor is exactly the difference between the line's geometric quarter-wave frequency
    # and what it actually tunes to, so the two have to be reported apart or the length looks wrong.
    modes = dict(
        tuned_fundamental_hz=fb,
        odd_harmonic_estimate_hz=[(2 * n - 1) * fb for n in range(1, 5)],
        geometric_quarter_wave_hz={name: speeds[name] / (4 * length) for name, length in lengths.items()},
        note="the tuned fundamental is the design target the taper factor was applied to reach; the geometric quarter-wave "
             "frequency is what an untapered line of the same length would give, and the ratio between them is SF. The odd "
             "harmonics are the uniform-line spacing applied to a tapered line, which is an estimate: a taper moves the "
             "higher modes off exact odd multiples, which is part of why it is used.")

    # A volume-velocity source couples to pressure cos((2n-1) pi x/(2L)).
    # Its first pressure node is x/L = 1/(2n-1), not a velocity node.
    offsets = []
    for n in (2, 3):
        fraction = 1.0 / (2 * n - 1)
        if fraction < 1.0:
            offsets.append(dict(suppresses_mode=f"{2 * n - 1}/4 wave", fraction_from_closed_end=fraction,
                                fraction_from_terminus=1 - fraction,
                                distance_from_closed_end_mm={name: fraction * length * 1000 for name, length in lengths.items()}))

    volumes = {name: (throat + terminus) / 2 * length * 1000 for name, length in lengths.items()}
    results = dict(
        tuning_hz=fb, taper=dict(ratio_terminus_over_throat=ratio, factor=factor, inside_published_range=inside,
                                 table=[dict(taper_ratio=r, factor=s) for r, s in TAPER_TABLE],
                                 note="SF from the published table by log interpolation; outside 0.1 to 10 this is extrapolation"),
        speeds_m_s=speeds,
        lengths_m=lengths, lengths_mm={name: length * 1000 for name, length in lengths.items()},
        untapered_length_m=speeds["unstuffed"] / (4 * fb),
        line_volume_l=volumes,
        modes=modes,
        driver_offset=dict(options=offsets,
                           note="the source says to offset the driver along the line to suppress the three-quarter-wave mode "
                                "without stating where; the fractions above are pressure nodes for volume-velocity excitation, derived from "
                                "the closed-open geometry. Taper the line as well, so residual standing waves move up to where "
                                "fibre damping works."),
        comparison=dict(
            basis="The equal-volume/equal-tuning comparison from the cited source is a case-dependent observation, not an alignment law.",
            observables=["absolute bass output", "sustained cutoff", "cone excursion", "terminus velocity", "ripple"],
            method="compare distributed_loading against lf_box with equal volume, drive, losses and cutoff definition"),
        validity=dict(statements=list(VALIDITY), taper_ratio_inside_published_range=inside,
                      stuffed_asymptote_density_lb_ft3=0.6))
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Tapered quarter-wave line length, modes and driver offset", NOTES, VALIDITY))
