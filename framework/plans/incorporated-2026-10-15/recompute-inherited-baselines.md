---
id: recompute-inherited-baselines
date: 2026-10-02
project: neat-petite-amt-v4, neat-petite-dayton-astra, neat-dayton-redcatt
phase: validation
confidence: medium
applies_when: A project takes targets or comparison baselines from a predecessor project's figures
tags: [baseline, calibration, objectives, comparison, provenance]
---

## What went wrong
A predecessor's bass-limit and sweep-level figures were copied as comparison baselines and one target. They had been computed on a mixed basis, with calibrated pressure and uncalibrated excursion, while the new candidates were scored with that calibration removed. One candidate's headroom was understated by several decibels against the baseline, and a target moved when the baseline was recomputed. The framework already states that a level calibration changes pressure but not excursion limits. The gap was that inherited numbers were trusted rather than regenerated.

Even an exactly replayed numerical baseline can carry stale explanatory evidence. A later fixed-hardware revision inherited an audit describing a different candidate, observation prose that did not quite match the saved listener height, and a radiator-adjustment instruction tied to the old crossover's input-impedance saddle. The actual source and alignment were unchanged; copying the explanation would nevertheless have misdescribed the model or directed a builder to retune the radiator after a crossover change.

The same happened in the documents of a later crossover revision. Its chapters were adapted from the predecessor package. A notch frequency belonging to the old capacitor value and a stress figure from the old package survived the edit, beside correctly regenerated numbers; only an independent check against the result files found them.

Supporting CAD and builder PDFs can also disagree inside the same release folder. Reusing the PDF dimensions while treating a later supplied CAD file as the fixed hardware can invalidate a driver-clearance decision, even when every acoustic result replays exactly.

## What could have helped
Before iteration 1, identify the exact delivered dependency chain, not only the candidate ID: the released physical realization may differ from the earlier exploration folder carrying that ID. Rerun it through the current project's metric code and record the regenerated figures, with their basis, beside the copied ones. Treat a copied figure as provenance, not as a baseline. Where a calibration, band or definition differs, say which basis each objective uses. This does not settle which basis is physically right; it only makes the comparison consistent.

Also reconcile the inherited audit and builder instructions against that exact candidate. Check observation datums, the electrical connection used for an impedance or tuning quantity, and the physical domain used by a detailed model. Reusing fixed hardware justifies reusing its evidence with the correct scope; it does not establish that every copied explanation describes the current files. When a document is adapted from a predecessor, take every quoted figure from the current project's collected numbers, and have the finished text checked against the result files by someone who did not write it.

At the same time, establish which revision of each physical artifact governs the new build. Compare panel and grille thickness, installed datums and mounting hardware across supplied CAD, drawings and parts lists before ranking a replacement driver. A standalone part model does not necessarily encode its assembled position.
