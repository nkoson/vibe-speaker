---
id: whole-speaker-output-is-already-one-metre-equivalent
date: 2026-09-14
project: forte-iii-three-way
phase: validation
confidence: low
applies_when: Reading or fitting to whole_speaker SPL figures
tags: [normalization, sensitivity, crossover-fit]
---

## Observation
`whole_speaker` and `crossover_fit` normalize pressure to the reference distance so that the SPL reads like a 1 m figure at the stated drive. The project added a further 3 m to 1 m correction of 9.54 dB on top, both when reading sensitivity and when setting fit targets. Networks were padded to hit a target that was already 9.5 dB too low; sensitivities of 81 to 86 dB were reported for systems that modeled at 95 dB.

## Why it mattered
Two rounds of crossover values were shaped by the wrong level. Once the interpretation was corrected, the same drivers reached the sensitivity objective with far shallower pads.

## Advice
Before quoting a system sensitivity or writing a fit target, check the level convention against a section file: run one section alone with unity transfer and confirm that the `whole_speaker` band mean equals the `source_response` sensitivity plus the baffle effect. Treat any constant offset as an interpretation problem to resolve, not as a correction to apply. Write the convention once in the project README so every later evaluation quotes it.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 4
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Reference comparison and lineage" (c06 to c07 sensitivity 86.6 to 95.3 dB after the correction)
- `framework/simulations/whole_speaker/README.md`, "Output"
