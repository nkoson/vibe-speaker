---
id: bound-the-fit-to-values-you-can-buy
date: 2026-09-15
project: forte-iii-one-woofer-20260915
phase: design
confidence: low
applies_when: Setting the bounds of a crossover fit, or reading a fit result with values resting on their bounds
tags: [crossover-fit, bounds, stock, quantization, heat]
---

## Observation
Fit bounds were first written from the crossover frequencies the design intended: a narrow window
around each seed value, meant to hold the acoustic crossings where the driver spacing wanted them.
Across two iterations the fits returned four to six values resting on a bound every time, and each
time the response was acceptable while something else was not: one candidate put 48.1 W into a single
midrange resistor, another asked for a 20 mH shunt coil, a third for a 12 mH one. None of those
values exists in the project's stock list; the largest catalogued coil is 10 mH.

Rewriting the bounds as the range the catalogue can actually supply, and leaving the crossing
frequencies to the optimizer, produced the same on-axis response, the same 3.7 to 3.9 dB seating
window and 41 to 52 W of network dissipation instead of 68 W.

## Why it mattered
The bounds, not the topology and not the drivers, were the binding constraint for two of three
iterations. A value at a bound was read each time as "the optimizer finished", and the effort went
into the next candidate instead of into the bound.

## Advice
Consider deriving each bound from the stock list before the first fit: the smallest and largest value
of that component type the inventory holds, or the range reachable by two or three parts in series or
parallel. A bound that no catalogue value satisfies produces a design that cannot be built, and the
fit reports success either way.

Consider treating `values_at_bound` as a finding to act on in the same iteration rather than a note
in the evaluation, as `framework/references/crossover-design.md` section 9 asks. When several values sit
on bounds at once, the likely cause is the bounds; when one does, it is more often the topology.

Where a crossing frequency has to be held, consider holding it with a weight in the fit target or
with a different filter order rather than with a narrow bound on a component value, so the optimizer
can reach the same acoustic result through parts that exist.

## Evidence
- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-2.md` and `iteration-3.md`
- `framework/projects/forte-iii-one-woofer-20260915/candidates/c04/summary.json`, `c07/summary.json`, `fit_statistics.values_at_bound`
- `framework/projects/forte-iii-one-woofer-20260915/candidates/c10/voicing/90.5-buildable/summary.json`
