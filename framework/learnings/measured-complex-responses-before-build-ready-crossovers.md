---
id: measured-complex-responses-before-build-ready-crossovers
date: 2026-09-14
project: forte-iii-three-way
phase: documentation
confidence: low
applies_when: Presenting crossover detail as ready to build
tags: [measurement, phase, horn, crossover, documentation]
---

## Observation
The upper drivers were modeled from magnitude-only manufacturer curves with reconstructed phase, taken on a different horn than the one specified. The crossover was fitted to that model and then documented down to part numbers and a board netlist. The fit error reported by `crossover_fit` measured agreement with the model, not with the drivers.

## Why it mattered
A reader of the package could take the crossover as final. Its integration depended on a phase relationship nobody had measured, and the perturbation study showed it was fragile.

## Advice
Consider stating in the crossover document which section models rest on measured complex data and which on priors, and labeling the crossover values as a starting point to be confirmed by measuring the mounted drivers (magnitude and phase on the actual horn and baffle) before parts are bought in quantity. A prototype measurement plan belongs in the package when priors carry the integration. The `source_response` `measured` and `frd_file` kinds exist so that measured data can replace the priors and the same chain can be rerun.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, "Would better simulation have helped?"
- `framework/projects/forte-iii-three-way/reference/prototype-measurement-plan.md`
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"
