---
id: check-upper-driver-graph-calibration
date: 2026-09-14
project: forte-iii-three-way
phase: validation
confidence: low
applies_when: Digitizing manufacturer graphs for upper drivers
tags: [digitizing, published-curve, compression-driver, horn]
---

## Observation
A compression driver's published response was digitized with a graph-coordinate calibration error, so its level and shape were off until a candidate was almost frozen. The other upper-driver anchors were checked against the original graphs afterwards. The digitized curves were also taken on the manufacturer's test horn, not on the horn chosen for the design, and no phase was published.

## Why it mattered
An upper-driver level error propagates straight into pad depth, crossover point and the sensitivity comparison with the reference. It is cheap to catch at digitizing time and expensive after fitting.

## Advice
When a `published_curve` is written, consider recording two or three anchor readings (a labeled grid line, the stated sensitivity at 1 kHz, the highest point) next to the points, and confirm that `source_response` reproduces the datasheet sensitivity within the reading uncertainty. Note the horn or baffle the curve was taken on; when it differs from the chosen horn, expect the level, the low-end loading and the phase to differ and say so in the evaluation.

## Evidence
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, last paragraph
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"
