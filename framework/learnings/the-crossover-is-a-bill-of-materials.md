---
id: the-crossover-is-a-bill-of-materials
date: 2026-09-16
project: forte-iv-single-pr
phase: design
confidence: medium
applies_when: A crossover is being designed, quantized to stock, or read after a fit
tags: [crossover, cost, parts, efficiency, compensation, inventory]
---

## Observation
The delivered three-way's crossover came to 40 physical bodies and about 829 EUR per speaker,
against about 633 EUR for the drivers and radiator it feeds: the filter cost more than the
transducers. Reading the same result files for power rather than for response showed where it went.
Pink weighted over 20 Hz to 20 kHz, 37 percent of the amplifier's real power reached the drivers and
63 percent stayed in the network, worst in the 354 to 707 Hz octave at 13 percent. Three mechanisms
produced it, and only one of them was attenuation:

- A midrange pad 5.45 dB deep, which passes 29 percent of that band's power by definition.
- A shaping notch in the woofer branch whose resistor bank took 62 W at 100 Hz against 16 W into the
  woofer at the 18 V probe.
- An impedance-compensation branch across the woofer that took 72 W at 394 Hz against 16 W into the
  woofer, while attenuating the woofer by 0.8 dB. Its own audit says why: it converted a load
  averaging 9.64 ohm across the crossover band into 3.10 ohm, so about two thirds of the branch
  current went around the driver rather than through it.

The same branch produced the 2.43 ohm impedance minimum and the resistor body that set the
provisional 9.5 V input ceiling, both at the same frequency. The stock inventory the design chose
from held 87 parts, all one premium manufacturer, so no cheaper option for any position existed to
be compared against.

## Why it mattered
Every response objective was met while most of the amplifier's output was being spent on the network,
and nothing in the chain reported that until someone asked. The evaluator had flagged the component
stress in iteration 1 and asked for the loss distribution to be redesigned rather than the resistor
count multiplied; what the final candidate did was multiply the resistor count, splitting each
position into four bodies. That halves nothing: per-body dissipation falls, total heat, cost and
board area do not. A part count of 40 and a crossover dearer than the drivers were both visible in
the parameter file all along, and neither was a number anyone was looking at.

The upstream cause was in the objectives. Sensitivity of at least 90 dB at 2.83 V with f3 below 40 Hz
in about 105 L sits close to the lossless efficiency ceiling, and was reachable only because 2.83 V
into a 4 ohm woofer is 2 W. The impedance-minimum objective of 4 ohm was meanwhile stricter than the
reference product being emulated, whose published independent measurement reads about 3.2 ohm. Two
objectives pulled against each other and against the physics, and the network paid the difference in
parts and heat.

## Advice
Consider reading what the network keeps at the same time as what it passes. `crossover_network` now
reports `efficiency` and `parts`; neither is a target and no share passes or fails, but a design
spending most of its input on its own resistors is worth noticing while the driver complement and the
topology can still change. Read the figure with the pad depths and the compensation audit beside it,
because attenuation forced by a sensitivity mismatch and current diverted around a driver look
identical in the loss number and are different findings with different fixes.

Where a compensation branch is expensive, consider whether it is earning the current it diverts.
`compensation_audit` gives the effective resistance before and after, and the ratio of the two is
roughly the share of branch current that stops reaching the driver. Fitting a lower-order filter
against the driver's complex impedance is sometimes cheaper than flattening the impedance and fitting
against a resistor; that is a comparison to run, not a rule.

Consider running `crossover_fit` with `ablation` before quantizing, so each element's worth is
measured against this design rather than assumed from its name. Nothing obliges a removal at any
delta; the value is in knowing which elements the network is leaning on.

When splitting a position into a bank looks like the answer to a stress figure, consider whether the
question was heat per body or heat at all. Splitting answers the first and leaves the second where it
was, and it multiplies cost and board area while doing so.

Consider collecting stock inventory the way drivers are collected: several series per class across
the price range, from more than one manufacturer. An inventory of one premium brand makes the cheap
option unavailable to the design by omission, and the substitution that would settle it - the cheaper
part's own tolerance, ESR and ratings in the parameter file, rerun - costs one run.

## Evidence
- `framework/projects/forte-iv-single-pr/final/02-crossover-construction.md`, the parts list, the
  cost subtotal and the resistor stress table
- `framework/projects/forte-iv-single-pr/candidates/c08/sim/physical_network.json`, `results.efficiency`,
  `results.parts`, `results.sections[].compensation_audit`, `results.sections[].insertion_loss`
- `framework/projects/forte-iv-single-pr/evaluations/iteration-1.md`, the request to redesign the loss
  distribution rather than multiply the resistor count
- `framework/projects/forte-iv-single-pr/final/04-reference-comparison.md`, the reference product's
  measured impedance minimum against this project's objective
- `framework/projects/forte-iv-single-pr/inventory/stock/`, 87 records from one manufacturer
- `framework/references/crossover-design.md` sections 7 and 8, and
  `framework/references/target-response.md` section 9
