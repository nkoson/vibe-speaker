---
id: calibrate-after-source-shaping
date: 2026-10-06
project: neat-petite-dayton-astra
phase: validation
confidence: low
applies_when: Combining a lumped bass model with published response shaping and an absolute level calibration
tags: [source-response, normalization, calibration, phase, baseline, validation]
---

## What went wrong
A project helper calculated its calibration gain from a raw bass response, then applied that gain to a source whose published-response replacement had already performed a different normalization. The calibration used a mean over one band; the replacement used medians over another. The completed source therefore retained an unintended level offset from the published curve, even though the metadata claimed a level match.

The error affected both the incumbent and replacement-driver models. Correcting only the replacements would have left an inconsistent comparison. Correcting the incumbent also moved the acoustic crossing and its phase difference because only the woofer branch changed level; the unchanged physical crossover no longer met its earlier nominal phase claim.

## What could have helped
Construct the complete uncalibrated source first, including replacement, blending and any declared fixture correction. Calculate the absolute calibration against that completed source using one stated band and statistic. Then rerun it and compare the actual output with the published anchors, rather than validating only the gain formula or intermediate raw curve. A numeric FRD should not acquire an unexplained offset labelled as digitizing uncertainty.

When an inherited baseline is affected, preserve its original results and the user's requested targets, create a consistently corrected same-hardware comparator, and disclose both. Check the changed crossing frequency and relative phase as well as sensitivity and bass level. Keep pressure calibration separate from current and excursion when evaluating physical output limits; correcting an input convention does not establish measured accuracy.
