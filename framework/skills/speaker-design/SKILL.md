---
name: speaker-design
description: Run a complete passive loudspeaker design project from a plain-language brief - start the project, research the reference speaker and an extensive parts inventory, build and refine simulated design candidates with the standalone simulation apps, evaluate and compare them, pick the best within the iteration limit and produce the construction and performance documentation. Use for any request to design, continue, compare or document a loudspeaker.
---

# Speaker design

Use this skill to carry a passive loudspeaker brief through source selection, simulation, comparison and a buildable final package. The agent owns design decisions. The Python apps return physical results, numerical minima, margins and diagnostics; those quantities do not select a speaker or define the user's priorities.

Use the completed simulation outputs as the canonical performance results of the design. Analyze the speaker on that basis and make definite engineering decisions. The user already knows the workflow uses simulations: do not add simulation-versus-measurement disclaimers in conversation, documents, captions, legends or drawing notes, even once. Do not qualify every result with "predicted", "simulated", "not measured", "not production-yield data" or equivalent language.

User-facing communication contains analysis and instructions. Connect each important result to the speaker's behavior, an objective, a tradeoff, a construction choice or a listening recommendation. Constructive comments include shortcomings and the concrete response to them; they are not praise-only commentary. State meaningful operating conditions, such as voltage, distance, frequency band and room geometry. Translate an unresolved interface into a specific fitting or machining step. Keep acquisition provenance, model validation, numerical uncertainty and tool diagnostics in project records; do not turn them into boilerplate for the user. Preserve the true origin of data internally and do not invent a physical measurement session.

The apps continue to compute and report quantities only. Interpretation and design decisions belong to the agent, using the engineering references. Resolve invalid calculations before relying on them; canonical results do not make inconsistent inputs valid.

## Working context

Projects live in `framework/projects/<slug>/` and remain outside Git. `project.json` records the brief, objectives, listening geometry, iteration budget, candidate list and decisions. Inventory records, candidate parameter/result files, evaluations and final drawings preserve the evidence. A revision normally becomes a new candidate with a `parent`, leaving the released baseline available for comparison.

Use `.speaker-venv/bin/python` and `framework/tools/run_simulation.py` for project runs. Read `framework/simulations/README.md` and each selected app's contract before its first use. Keep dependency execution in order and inspect command status and fresh result identity before using a result. One app per command makes failures and provenance easier to interpret.

The companion skills cover candidate creation (`speaker-designer`), comparison (`speaker-evaluator`), builder documentation (`speaker-documentation`) and accumulated experience (`speaker-learnings`). Their procedures are guidance to adapt to the brief. Engineering sources live in `framework/references/README.md`; consult the reference covering each physical decision.

## Interpret the brief and establish a baseline

Start from `framework/templates/project.json`. Record the user's quantitative targets, qualitative priorities, physical constraints and authorized iteration budget. If no iteration count was given, three rounds of three detailed candidates is a useful starting budget, with expensive analysis focused on finalists. This is not a limit on researched parts, catalogue coverage, inexpensive screening or stock alternatives. An explicit user research/time limit still governs. Clarify only ambiguities that materially change the speaker.

Use [brief-to-experiments](references/brief-to-experiments.md) to turn qualitative goals into observable comparisons. Record each objective's band, curve, drive, units, direction, tolerance, priority and evidence. Separate user constraints from designer diagnostics. Preserve the user's targets through corrections; a missed objective is evidence to interpret rather than a reason to move the target.

Compare the objectives with similar speakers and the applicable efficiency/volume/extension tradeoffs. Explain apparent conflicts while architecture is still open. An inventory search establishes what that search found, not universal impossibility.

For inherited work or changed input conventions, use [simulation integrity](references/simulation-integrity.md): identify the delivered realization, replay its dependency chain, reconcile physical artifacts and compare the original and corrected basis. Consult matching active learnings and record how their advice applies.

## Build an evidence-backed inventory

Record reference-product quantities with source and conditions: voltage or power basis, distance, radiation environment, band, smoothing and whether the quantity was published directly or derived from a plot. Keep unknown values explicit. Circuit/construction facts, response data and subjective claims are different evidence types.

Follow [component research and search expansion](references/component-research.md) before shortlisting and whenever an inventory gap affects a design decision. Start an `inventory/search-review.md` from `framework/templates/inventory-search.md`. Cover every required component role, including drivers, horns/waveguides, passive radiators, complete or modular ports, crossover stock and other performance- or construction-critical parts. A previous project's inventory, one retailer or one familiar manufacturer is a seed, not the search boundary.

For an open major driver role, research roughly 15–25 materially distinct models across at least four manufacturers where the relevant market permits. These are starting breadth targets, not a cap, a substitute for catalogue coverage, or a reason to pad the list with duplicates. For narrower markets or user-fixed choices, record the applicable catalogue search and why the meaningful pool is smaller. Survey loading hardware and crossover catalogue families by their physical/electrical coverage, following the component-specific procedure; a driver-count target is not a useful stock-value limit.

For bass-critical briefs, use `framework/templates/feasibility.md` to compare plausible drivers, alignments and sizes before committing to upper drivers. Research upper-driver and loading alternatives in parallel with this screen so an early LF choice does not silently fix the rest of the system. Include finite-baffle/outlet output, real electrical loss, sustained extension and physical output limits. Preserve broad research records separately from the smaller simulation shortlist, with reasons and evidence for exclusions.

## Iterate through connected simulations

A candidate begins with a distinct physical idea and uses `speaker-designer` to realize it. Before fitting, the simulation and geometry audits in `framework/templates/` help establish source normalization, cone/outlet ownership, actual volume, physical fit and intended coordinate transforms.

Use the designer's [advanced simulation guide](../speaker-designer/references/advanced-simulation.md) when a richer mechanism can affect the choice. Shared assembly geometry, cavity/BEM source fields, distributed loading, room waves/reflections, structural coupling, thermal/nonlinear behavior and joint uncertainty are connected tools, not independent scores to collect.

After each round, use `speaker-evaluator` to compare current and earlier candidates with the same metric definitions and source assumptions. Separate design and review contexts when that workflow is available and appropriate; otherwise perform a fresh review pass and record the arrangement. The evaluation should propose controlled experiments addressing central misses and explain whether another round could change the recommendation.

When a model/input correction changes earlier evidence, record the cause, affected candidates, changed figures, ranking consequences and invalidated exploration. Recompute dependencies before comparing. Validation reruns are distinct from new exploration; keep the authorized budget visible.

## Select and deliver

Make a definite recommendation using the user's central priorities, realized construction and robustness evidence. Check the inventory search review: unresolved coverage gaps and triggered expansion requests need a follow-up search or an explicit user-scope/budget limitation before claiming a best available choice. Explain genuine tradeoffs and residual misses. The best numerical objective alone is not the selection. When useful iterations remain, work on a central miss before polishing construction details that would be discarded after a concept change.

For a selected construction design, use `speaker-documentation` to produce a complete PDF with source drawings and plots alongside it. Deliver final stock values, machining dimensions, wiring and useful placement guidance. If the available work does not approach the central brief, explain the closest option and alternatives honestly; respect the user's requested deliverable and budget.

Finish with a project postmortem through `speaker-learnings`, recording transferable mechanisms and implementation defects. Source changes go through Git when authorized; project-specific evidence stays in the project folder.
