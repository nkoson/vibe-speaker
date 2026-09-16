---
id: a-failed-run-must-not-read-the-previous-result
date: 2026-09-15
project: forte-iii-one-woofer-20260915
phase: validation
confidence: low
applies_when: Writing or reusing project code that runs the simulation applications in a loop
tags: [tooling, project-code, stale-results, failure-handling]
---

## Observation
A project helper ran each application as a subprocess and then read `<name>.json` from the output
folder, accepting it when its `status` field said `computed`. When `crossover_fit` crashed, the file
from the previous run of the same candidate was still there, still said `computed`, and was read as
this run's result. The helper reported fitted values that did not correspond to the parameter file it
had just written, and the candidate was scored on them.

It was noticed only because one fitted value sat outside the bound that the freshly written parameter
file declared - a check that happened to be in the summary for another reason. The crash itself was a
real defect in the application, and fixing the helper is what made it visible.

## Why it mattered
A silent substitution of one run's result for another's is indistinguishable from a design that did
not respond to a change. Two candidates were rebuilt before the cause was found.

## Advice
Consider deleting the result file before launching the application, and treating a missing result as
an error rather than a reason to read whatever is there. Consider checking the subprocess return code
as well as the document's own status field, and putting the application's stderr into the exception,
because an application that exits non-zero has usually already written the reason.

Where a project caches results deliberately, the freshness check belongs on the inputs and the model
version as `validate-simulation-chain-before-iteration-one` describes; this is the simpler failure,
where nothing was cached on purpose and the file system did the caching.

## Evidence
- `framework/projects/forte-iii-one-woofer-20260915/tools/lf_section.py`, the `run` helper
- `framework/projects/forte-iii-one-woofer-20260915/postmortem.md`, "What went wrong", item 4
- `framework/tests/test_crossover_fit_budget.py`, the application defect that exposed it
