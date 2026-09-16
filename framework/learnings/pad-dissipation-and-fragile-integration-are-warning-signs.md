---
id: pad-dissipation-and-fragile-integration-are-warning-signs
date: 2026-09-15
project: forte-iv-single-pr, forte-iii-three-way, forte-iii-performance-20260914, forte-iii-r3, forte-iii-pr-20260914, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915
phase: design
confidence: high
applies_when: A candidate reaches its level with deep pads or only at nominal depths
tags: [pads, dissipation, robustness, depth-perturbation]
---

## Observation
The selected candidate's midrange series pad dissipated about 133 W and the treble pad about 78 W at the stress drive, and its on-axis ripple rose from 5.1 dB nominal to 12.5 dB when acoustic depths were perturbed by 50 mm. Earlier candidates had even deeper pads, driven partly by the level misreading. The nominal curves looked acceptable; the stress and perturbation figures did not.

The second study found the same warning in a different branch: LF correction produced 84.19 W in a resistor string at its peak, and 111.44 W frequency-coincident total resistor heat. Splitting that string into three parts reduced individual dissipation to 28.06 W but did not reduce the cabinet's heat burden. A coaxial design's nominal 4.862 dB ripple became 15.921 dB under a +10 mm relative acoustic-depth scenario. Common-depth shifts were comparatively benign on axis but worsened the seating window to 6.53/8.74 dB.

The passive-radiator follow-up improved the symmetric positive 10 mm relative-depth ripple from 15.921 to 4.898 dB using steeper upper overlap, but common -50 mm depth still produced 10.816 dB vertical deviation. Final physical component heat was 118.275 W at 727.6 Hz under 28.3 V sine drive. The direction of crossover-order change was specific to the interference mechanism; the heat burden remained.

A third project measured what a deep pad costs in parts rather than only in watts. Matching a
111 dB horn assembly to a 94 dB system took about 19 dB in each upper section, which is 152 W of
component dissipation at the project's stress drive and, once every position was sized as an array
of the stocked part at half its nameplate, 54 resistors per speaker and two thirds of the
crossover's cost. Its depth-perturbation ripple went from 4.7 dB nominal to 29.1 dB at 50 mm.

A sixth project found the heat summary itself was wrong. A capacitor appeared to dissipate an
impossible amount, because a composite element's stress was being attributed to its last member
instead of being distributed: the whole Zobel, bank or notch was reported against one part. A nodal
solve of the same board gave the three resistor positions 71.55 W, 60.56 W and 46.98 W at 18 V, and
the exact-resistance four-body banks still needed a provisional 9.5 V ceiling to stay inside
half-rating practice.

## Why it mattered
Deep pads can reflect excess raw sensitivity or resonant voltage magnification in the preceding filter. Either can impose substantial heat and cost. Integration that holds only at nominal depths may fail with unmeasured phase and real mounting.

The single-PR revision reached 90.511 dB with ordinary internal resistors, but a resonant midrange filter still made three 6.8-ohm bodies dissipate 17.066 W each at the same 18 V sine probe. Moderate driver sensitivity and a small resistor count did not establish low dissipation. The nominal 4.621 dB seating deviation rose to 11.642 dB under a common +50 mm upper-depth scenario. Splitting a pad into ordinary 25 W parts removed a case-cooling dependency; it did not remove the resonance or validate enclosed endurance.

A fifth project found that pad depth, not pad topology, sets the heat, and that the heat therefore
moves with the system level rather than independently of it. Flooring both shunt pad resistors so that
each pad worked mainly as a series resistor did not reduce the dissipation: the loss moved into the
series resistor and the total stayed within a watt. Fitting the same design at seven system levels
moved the worst-case network dissipation from 71 W at the lowest level to 46 W at the highest,
because a louder system needs a shallower pad. A heat objective written independently of the
sensitivity objective is therefore not independent of it.

## Advice
When reading a crossover result, consider looking at the pad dissipation and the depth-perturbation ripple before admiring the nominal curve. A pad much deeper than the mismatch between driver sensitivities suggests the system level or a part choice should change. A perturbation ripple far above the nominal one suggests the crossover relies on a phase relationship that has not been measured; changing overlap width, moving a driver, or revisiting filter order may help, but the direction needs testing against the actual phase mechanism. Report both figures in the evaluation next to the nominal ones.

Include correction branches and reactive component currents in that review, and compare frequency-coincident total heat with the actual cooling arrangement. A case-cooled resistor marking does not establish enclosed-board capacity. If upper sections share a horn, consider both common and relative phase uncertainty and inspect off-axis as well as on-axis effects; rigid physical alignment does not establish equal acoustic delay. Such perturbations are sensitivity scenarios, not measured manufacturing variation.

Consider trying both wider and narrower overlap against the actual phase scenarios. This follow-up contradicts any presumption that reducing filter order will improve robustness. Inspect the seating window under common shifts as well as on-axis relative shifts, and keep case-cooled resistor ratings separate from an enclosed board thermal qualification.

Consider converting the dissipation into a part count early, not at documentation time. A position
that needs a two-figure number of stocked resistors is telling you the architecture wants a
transformer-tapped attenuator, or a less sensitive upper driver, or a louder bass section, and any
of those is a design decision rather than a bill-of-materials decision. Where the array is kept,
write it into the parameter file so the schematic and the wiring table carry it too.

When pads seem unexpectedly deep for the raw driver sensitivity, consider examining voltage on both sides of the filter and pad. Compare the same input voltage and frequency-coincident total heat before and after substitutions. Keep per-body rating, cabinet heat, parasitic inductance and measured ambient temperature as separate checks.

Consider checking a part's own dissipation rather than its group's before sizing an array from it.
Per-part `I^2 R` and power conservation across the group are both cheap to verify - the members of a
series group share its current and those of a parallel group share its voltage, and the leaf powers
sum to the group's power - and a figure that survives neither check is a reporting artefact rather
than a heat problem. `crossover_network` now distributes that stress itself.

## Evidence
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 4
- `framework/projects/forte-iii-performance-20260914/evaluations/final-audit.md`
- `framework/projects/forte-iii-performance-20260914/final/02-crossover-construction.md`
- `framework/projects/forte-iii-r3/final/02-crossover-construction.md`, the resistor array table
- `framework/projects/forte-iii-r3/postmortem.md`, reason 7
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/depth-directivity-summary.json`
- `framework/projects/forte-iv-single-pr/evaluations/leaf-stress-correction.md` and its postmortem, the misattributed group stress
- `framework/tests/test_network_leaf_stress.py`, the per-leaf distribution and the power-conservation check

