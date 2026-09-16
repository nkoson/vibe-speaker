---
id: check-a-default-perturbation-against-the-thing-it-perturbs
date: 2026-09-15
project: forte-iii-one-woofer-20260915
phase: evaluation
confidence: low
applies_when: Reading a robustness or sensitivity figure produced by an application's default perturbation
tags: [robustness, depth-perturbation, defaults, interpretation]
---

## Observation
`whole_speaker` perturbs every section's acoustic depth by one `depth_perturbation_mm`, and the value
used throughout three iterations was the application's 50 mm default. It produced ripple figures from
12 to 43 dB on candidates whose nominal ripple was about 3 dB, and every evaluation reported the
integration as fragile.

The finalist's midrange acoustic centre sits 45 mm behind the baffle and its tweeter 15 mm, so a
-50 mm shift places both in front of the baffle. Rerunning at 10, 15 and 25 mm gave the figures that
describe a real mounting uncertainty: 2.9 dB nominal, 3.4 dB at 10 mm, 4.3 dB at 15 mm and 7.3 dB at
25 mm, all on the midrange, which is still the sensitive section but by a margin a builder can act on.

## Why it mattered
The 50 mm figures were true statements about the model and useless statements about the design. They
were reported in two evaluations as a weakness of each candidate, and they could not discriminate
between candidates because every candidate failed them equally.

## Advice
Before quoting a perturbation result, consider comparing the perturbation with the quantity it
perturbs. A depth shift larger than the driver's own acoustic depth, a tolerance wider than the part's
catalogue tolerance, or a volume change larger than the displacement being estimated is a sensitivity
probe: it shows how steeply the model degrades, not what the design will do.

Where the application applies one figure to every section and the sections differ by an order of magnitude,
consider running two or three values and reporting the one that matches the physical uncertainty,
with the default kept beside it and labelled as a probe.

## Evidence
- `framework/projects/forte-iii-one-woofer-20260915/candidates/c10/final/detail/detail-report.json`
- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-1.md`, fragility paragraph
- `framework/projects/forte-iii-one-woofer-20260915/final/03-simulated-performance.md`, depth table
