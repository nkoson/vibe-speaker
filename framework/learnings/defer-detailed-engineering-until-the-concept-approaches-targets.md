---
id: defer-detailed-engineering-until-the-concept-approaches-targets
date: 2026-09-14
project: forte-iii-three-way
phase: selection
confidence: low
applies_when: Deciding when to start boards, drawings and structural studies
tags: [effort, sequencing, finalist, documentation]
---

## Observation
After the central performance miss was known, the project still produced a detailed board netlist, cabinet drawings, cavity and panel studies and a full documentation package for the selected candidate. That work improved electrical consistency and the documents; it did not change the acoustic outcome.

## Why it mattered
Effort that could have gone into another acoustic concept went into finishing a design that had already failed the brief. The package looked complete, which made the miss easier to overlook.

## Advice
Consider gating the detailed apps (`cavity_modes` FVM, `plate_structure`, `board_nodal`, drawings) on a candidate that approaches the core targets, and spending remaining budget on alternatives while it does not. When the budget is exhausted without such a candidate, a shorter package that states the miss and the options is more useful than a complete one that documents the wrong speaker. Detailed engineering is cheap to add later; a lost iteration is not.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 8 and "Changes required"
