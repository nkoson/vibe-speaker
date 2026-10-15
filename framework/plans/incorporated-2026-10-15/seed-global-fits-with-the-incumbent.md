---
id: seed-global-fits-with-the-incumbent
date: 2026-10-13
project: neat-dayton-redcatt
phase: design
confidence: low
applies_when: Fitting crossover values with an objective that contains hinge, threshold or crossing-detection terms
tags: [crossover, fitting, optimizer, search, convergence]
---

## What went wrong
A composite crossover objective had one-sided hinge penalties and a crossing frequency detected from the branch levels, so it was not smooth in the values. A gradient-based least-squares fit stopped on its step tolerance after about twenty evaluations and returned a worse score than its start. A derivative-free line search did the same. Had the first batch run with that fitter, its rankings would have reflected where each fit happened to stall, not what each topology can do. The switch to a global optimizer, made before the batch, cost roughly thirty times more evaluations per fit.

## What could have helped
Before a batch, fit one known network from its own values and from a perturbed start, and confirm that the fitter reaches the known score and does not return anything worse than its start. For non-smooth objectives, use a population-based global optimizer whose initial population contains the incumbent or parent values, so that a fit cannot lose ground. Run more than one seed on the leading candidates. Keep smooth surrogate terms where the brief allows: a soft hinge or a continuous phase measure instead of a detected crossing makes local polishing usable again.
