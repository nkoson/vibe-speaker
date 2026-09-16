---
id: reference-sensitivity-conventions-differ
date: 2026-09-14
project: forte-iii-three-way
phase: research
confidence: low
applies_when: Turning a reference's published sensitivity into an objective
tags: [reference, sensitivity, conventions, objectives]
---

## Observation
The reference's published 99 dB sensitivity was an "average listening room" figure. An independent measurement gave 95.2 dB B-weighted. The project's modeled figure was a free-field band mean at 2.83 V normalized to 1 m. None of the three is the same quantity, yet the objectives table had to score the candidate against a number.

## Why it mattered
An objective written as "99 dB" against a free-field band mean is unreachable by construction and misleads the ranking; an objective written as "95.2 dB" hides that the manufacturer's claim was never tested. The evaluation had to carry an "unverified" row for the room figure and score the free-field figure separately.

## Advice
When the reference publishes a sensitivity, consider recording its convention explicitly (room or anechoic, weighting, band, voltage and distance) in `reference.json` and writing the objective in the convention the model can produce, with a note on how it relates to the published figure. Where an independent anechoic measurement exists, prefer it as the comparable target and keep the manufacturer's figure as context. Do not add room gain to a modeled figure to claim compliance.

## Evidence
- `framework/projects/forte-iii-three-way/README.md`, last paragraph
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, objective scoring rows for sensitivity
