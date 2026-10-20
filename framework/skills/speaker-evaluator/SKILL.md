---
name: speaker-evaluator
description: Evaluate and compare simulated loudspeaker candidates from their result files - score every objective with its tolerance, compare candidates with each other and with the reference speaker, judge model risk, rank them and write concrete refinement requests for the designer. Use inside a speaker-design project after candidates have been simulated.
---

# Speaker evaluator

Compare candidates using the brief, evidence and current model contracts. The apps report physical observables, numerical minima and diagnostics. You decide how those results relate to the user's goals and which design to recommend. Treat the completed results as the canonical performance of the design. User-facing evaluations contain constructive interpretation and instructions, with no simulation-status or measurement disclaimers. Explain the audible or practical significance supported by the data, the tradeoffs, and the concrete response to a miss. Keep provenance, validation and probability qualifications in the internal evidence record. Do not substitute a score or a number dump for an engineering judgement.

Read `project.json`, the reference, each candidate's parameter/result chain and the preceding evaluation. Use `framework/templates/evaluation.md` to record values, target basis, margins and interpretations with result-file/JSON paths. Preserve a candidate's parameters during review; place proposed design changes in controlled refinement requests.

## Establish comparability

Use [simulation integrity](../speaker-design/references/simulation-integrity.md) for inherited baselines, source calibration, fixture conventions and frequency coverage. Check phase/baffle ownership, per-terminal versus input voltage, cone/outlet counting and the propagation reference. Identify extrapolated or unresolved regions before quoting their statistics.

Use [advanced simulation guidance](../speaker-designer/references/advanced-simulation.md) to read the richer models. Inspect residuals, mesh/mode/order refinement and physical parameter scenarios separately. Results outside an app's physical scope do not become stronger evidence because their numerical residual is small.

## Read the design as a whole

- Review `inventory/search-review.md` against [component research and search expansion](../speaker-design/references/component-research.md). Check coverage of every required role, reasons for exclusions, untested contenders and whether serious alternatives received suitable system fits. Request expansion for unexplained stock gaps, costly banks, constrained loading hardware or weakly supported driver pairings; do not rank a narrow inventory as if it represented the market.
- Compare central objectives first, including equal-voltage bass, sustained extension, supported level, load, size and cost where relevant. Preserve threshold/reference-band definitions and distinguish nominal labels from actual complex impedance.
- Inspect response shape and local deviations across the full requested band, with the branch contributions, listening window and directivity alongside on-axis statistics. `NBD_ON`, `SM_PIR` and related metrics retain the identity of their source curve.
- For recurring peaks/dips, use the controlled decomposition in [crossover search](../speaker-designer/references/crossover-search.md). Separate geometry, source magnitude, phase and leakage before attributing a mechanism.
- Compare protection conditions against loaded terminal transfer at the stated amplifier or listening-level reference. A maker's operating band, minimum filter and rating-test condition are different evidence. The agent interprets the applicable condition and its margin.
- Read stock identity, tolerance, physical-leaf stress and frequency-coincident heat together. Inspect power diverted through compensation separately from attenuation caused by the level budget. A low part count or low DCR is not an independent definition of quality.
- For room scenarios, compare direct pressure, reflected pressure/energy, spatial mean/spread and changes with placement, boundaries and orientation. Read image-order, modal-order and ray-count sensitivity before interpreting a narrow room feature as a speaker defect.
- For coupled cabinet or nonlinear studies, inspect field normalization, energy/conservation residuals, actual geometry and supplied parameter domains. An isolated panel proxy, a coupled exterior pressure and a time-domain spectrum answer different questions.
- For uncertainty studies, retain all-scenario denominators, unresolved cases, censoring and the distinction between production draws and model alternatives. Compare close candidates using the same assumptions and draws.

## Recommend and request refinements

Make a definite recommendation in the user's priority order, explaining the benefits, costs and important uncertainty. Distinguish a central miss from a small secondary advantage. A software optimizer's minimum, a preference prediction or a count of designer-defined thresholds does not replace this interpretation.

For each useful refinement, name the physical variable, expected mechanism, observable and controlled comparison. Request a change in drivers, geometry, loading or network according to the evidence rather than applying the same remedy to every response error. Explain whether another iteration could plausibly change the recommendation within the authorized budget.

When construction documentation is appropriate, verify that the selected realization includes exact stock, source contracts, dimensions, bank leaves and shared-phase plots. Confirm that triggered inventory expansions were performed and their affected fits replayed, or that a specific user scope/budget limit is recorded. Describe unresolved findings in terms a builder can act on, without handing routine acoustic design choices back to the user.
