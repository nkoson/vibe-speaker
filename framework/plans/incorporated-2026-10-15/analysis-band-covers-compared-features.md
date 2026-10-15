---
id: analysis-band-covers-compared-features
date: 2026-10-01
project: neat-petite-amt-v4, neat-petite-dayton-opus
phase: evaluation
confidence: medium
applies_when: Comparing design variants (grain direction, bracing, materials, alignments) with a model whose frequency band is set by another run
tags: [panels, band-limit, evaluation, plate-structure, cavity]
---

## What went wrong
A panel screening inherited its upper frequency from the cavity run feeding it. One grain orientation moved the panels' first modes above that limit. Its worst-margin figures therefore came from the stiffness-controlled region below the modes, and the comparison reported a large advantage that vanished when the band was extended. The evaluation recommended changing the construction on that basis. The clue was that every variant reported its worst margin at the same frequency, a cavity peak rather than a panel mode. A later project's default detailed run again stopped below the panels' first modes and reported an excess below the modes themselves. Only the separately extended run was usable. Its reported pinned-to-clamped band also did not contain the orthotropic first mode the same run computed.

## What could have helped
Before comparing variants, list each variant's governing feature (first mode, resonance, tuning) and confirm it lies inside the analysed band with margin. Extend the feeding run when it does not, and check that the mesh still resolves the higher band. Treat identical worst-case frequencies across variants that should differ as a sign that the band, not the variable, is limiting. Make the extended band the default for a project whose panels have their first modes near the top of the standard band, rather than an optional second run. Check that a reported band brackets the mode it claims to bound before quoting it. The comparison is still a screening when the model is an upper bound.
