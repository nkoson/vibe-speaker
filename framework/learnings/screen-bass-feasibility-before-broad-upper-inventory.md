---
id: screen-bass-feasibility-before-broad-upper-inventory
date: 2026-09-14
project: forte-iii-three-way
phase: research
confidence: low
applies_when: Deciding how much inventory to research before designing
tags: [inventory, bass, feasibility, research-order]
---

## Observation
The project researched 34 acoustic parts across six roles before any combination was shown to reach the brief's bass level and extension in the permitted volume. The bass screen ran 18 vented cases, but it did not establish the absolute output, extension and excursion envelope that the upper drivers would later have to match. The architecture and the achievable system sensitivity were decided by the upper section instead.

## Why it mattered
The upper inventory was broad and the bass section was under-explored. When the bass turned out to be the limiting section, there was little left in the iteration budget to explore alternatives such as a different woofer size, a second woofer or a different loading.

## Advice
For a brief where bass extension or output is central, consider establishing the bass envelope first: for each candidate woofer and loading in the allowed volume, the absolute level the bass section can hold down to the target extension at the stress drive, and what limits it (`lf_box` `linear_scaling_to_limits`, `lf_uncertainty` for spread). That envelope tells you the system sensitivity the upper section should be padded to, and whether one woofer is enough. Research upper drivers to match that level rather than the reference's headline figure. Breadth in the upper inventory is worth less than depth in the section that decides feasibility.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reasons 2 and 7
- `framework/projects/forte-iii-three-way/inventory/screen.md`
