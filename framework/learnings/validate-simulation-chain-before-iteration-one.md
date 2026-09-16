---
id: validate-simulation-chain-before-iteration-one
date: 2026-09-15
project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915
phase: validation
confidence: high
applies_when: Before the first design iteration, once the source files and cabinet geometry exist
tags: [validation, rear-outlet, normalization, sanity-case]
---

## Observation
The first project ran two full design iterations on corrupted feedback. A propagation helper was silently discarding the rear passive radiator, the whole-speaker level was misread by 9.5 dB, and the woofer source counted its inductive roll-off twice. Each error was found late, by inspecting curves that looked wrong only in hindsight. Earlier networks were then re-evaluated with corrected models, but the exploration they should have provided was lost.

The later performance study ran actual-source checks before design: cone plus outlet agreed with the box within 2.84 × 10^-14 dB in the colocated case; a 100 dB source still read 100 dB at the 3 m observer; and the real rear-outlet finite-baffle effect was retained. During unfrozen c08 fitting, a project cache nevertheless reused a result after a referenced file changed because only parameter text was compared. All downstream outputs were regenerated; eight independent cold replays matched exactly.

## Why it mattered
Crossover values, pad depths and even part choices had been optimized against wrong levels and a missing bass radiator. The corrected final round had one iteration left to find a viable concept and did not.

The single-PR revision verified a parallel two-motor/shared-cavity equivalent against independent five-equation physics, checked identical physical LF transfers and applied the hybrid source correction exactly once to cone, radiator and current. Independent board and whole-system replays matched every frozen result. The cavity app still accepted only one aggregate cone location, so two location/mesh studies remained explicitly limited proxies rather than a validated two-cone field solution.

A fourth project ran the check on its own files before iteration 1 and found the published-shape
defect described in `do-not-double-count-woofer-rolloff`. Its level convention agreed to 0.0002 dB
once the source-to-ear path length was accounted for, and the 0.50 dB difference in the placed case
was that path length rather than a normalization error. The project's own run helper nevertheless
reproduced the stale-result trap in a new form: when an application crashed, the previous run's result
file was still present and was read as this run's, which is the subject of
`a-failed-run-must-not-read-the-previous-result`.

## Advice
Consider running a small validation case before counting any iteration, with the actual project files:
- A woofer-plus-outlet `whole_speaker` run with unity transfers and no other sections. Compare its low-frequency SPL with the `lf_box` curve for the same drive; they should agree within the baffle factor. If the outlet is absent, the sum will show only the cone.
- One section at a time with unity transfer, checking that the `whole_speaker` level in the section's band equals the `source_response` sensitivity plus the baffle effect. A constant offset between the two is a normalization misreading, not a propagation effect.
- The woofer section's slope above the blend band against the datasheet curve, to catch a double-counted roll-off.
Write the outcome of the check into the project log so later readers know which model version each candidate used.

If a project caches runs, consider including the contents of referenced dependencies and the model version in freshness checks. A stable parameter filename or parameter-text hash is not enough when its source files change. A cold replay of the selected chain can complement the physical invariants before freezing a candidate.

When using an aggregate driver equivalent, consider independently solving the actual electrical/mechanical coupling before fitting. Verify source pressure, physical per-motor current, excursion and the number of radiator contributions after separate wiring is introduced. An aggregate equivalence at low frequency does not establish a distributed high-frequency cavity equivalence; document that boundary separately.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reasons 3 to 6
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`
- `framework/tests/test_radiation_invariants.py` (regression test added after the rear-outlet fix)
- `framework/projects/forte-iii-performance-20260914/reference/simulation-audit.md`
- `framework/projects/forte-iii-performance-20260914/evaluations/c08-dependency-verification.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-pair-source-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
