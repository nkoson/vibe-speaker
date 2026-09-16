---
name: speaker-design
description: Run a complete passive loudspeaker design project from a plain-language brief - start the project, research the reference speaker and an extensive parts inventory, build and refine simulated design candidates with the standalone simulation apps, evaluate and compare them, pick the best within the iteration limit and produce the construction and performance documentation. Use for any request to design, continue, compare or document a loudspeaker.
---

# Speaker design (orchestrator)

You are the designer, the evaluator and the technical writer. The Python programs in `framework/simulations/` compute physics and return JSON; they never decide whether a result is good. Every judgement, every threshold and every selection is yours, made from the numbers in the result files and written down with the file path that supports it.

Companion skills: `speaker-designer` (how to build a candidate), `speaker-evaluator` (how to score and compare), `speaker-documentation` (how to write the final package), `speaker-learnings` (what past projects learned, and how to leave a postmortem and learnings behind). `framework/references/` holds the engineering the judgements rest on, each with its sources: `framework/references/cabinet-geometry.md` for the interior and what fits, `framework/references/baffle-and-driver-placement.md` for the baffle, the driver positions and the crossover frequencies the spacing has to survive, `framework/references/passive-radiators.md` for sizing, tuning and mounting a radiator, `framework/references/target-response.md` for what a good response curve is and which deviations cost, and `framework/references/crossover-design.md` for the network, `framework/references/driver-selection.md` for what a driver's parameters allow, `framework/references/enclosure-alignments.md` for the bass alignment and the vent, `framework/references/system-architecture.md` for the section count and the crossover frequencies, `framework/references/transducer-types.md` for domes, compression drivers and horns, `framework/references/measurement-and-model-limits.md` for what a predicted figure is worth, `framework/references/alternative-loadings.md` before proposing a bandpass, isobaric, aperiodic or cardioid box, `framework/references/horn-and-waveguide-design.md` before sizing a horn throat, cavity or mouth, `framework/references/arrays-and-directivity-control.md` before arraying two sources in the same band, and `framework/references/cabinet-materials-and-panels.md` before choosing a cabinet material, a wall thickness or a damping treatment. Read the one that covers the work at hand, and see `framework/references/README.md` for how a reference differs from a learning. Read `framework/simulations/README.md` once per session for the app inventory and JSON conventions; read the `README.md` inside an app's folder before the first time you run it.

Interpreter: `.speaker-venv/bin/python` at the repository root (numpy, scipy, matplotlib present). Run one app per shell command, never chained.

## Project layout

Every project lives in `framework/projects/<slug>/`:

```
project.json          brief, objectives with tolerances, limits, listening geometry, state and log
reference/            reference.json (template: framework/templates/reference.json) and research notes
inventory/            one JSON per part (template: framework/templates/part.json), grouped in woofers/, midranges/, tweeters/, horns/, radiators/, stock/
candidates/cNN/       candidate.json, sim/ (parameter and result files), notes.md
evaluations/          iteration-N.md (template: framework/templates/evaluation.md)
final/                the documentation package of the selected candidate
```

`project.json` is the single source of truth for phase, iteration counter, candidate list and decisions. Append one line to its `log` for every decision with the date.

## 1. Start a new project

1. Create the folder and `project.json` from `framework/templates/project.json`. Fill the brief from the user's words: reference product, size and budget limits, what must not change, and the iteration limit. Default limits when the user gives none: 3 iterations, 3 candidates per iteration, 1 finalist for detailed cavity and panel analysis.
2. Write the objectives as target, tolerance, direction and basis. Take them from the reference research when the user asked to approach a reference; otherwise from the brief. Objectives are optimization targets you judge with the tolerance; never edit a target to make a candidate look better. A missed objective is a finding to report.

   **Say what each objective looks like against comparable speakers, before iteration 1.** Work from `framework/references/target-response.md` section 9. For each objective write, in `basis` or beside it, what the reference product measures for the same statistic and what speakers of this size and class measure, and whether the objective sits inside that range, at its edge or beyond it. Then say which objectives pull against each other, with the arithmetic: sensitivity, extension and volume are bound by the efficiency law, a sensitivity figure quoted per volt moves about 3 dB with the nominal impedance, and an impedance minimum is moved by every Zobel, notch and pad the level budget will force. **This changes no objective and blocks nothing.** The brief is the user's; a target beyond the class may be exactly the point of the design. What it does is put the comparison and the conflict on the page while the driver complement is still open, instead of leaving them to be discovered as a missed objective in the last evaluation. Where an objective is beyond what the class reaches, say what it will likely cost - parts, heat, size or level - and let the user decide with that in front of them.
3. Do not ask the user routine questions. Ask only when different answers lead to materially different speakers (for example: floor standing or stand mounted, passive radiator allowed or not, budget class).
4. Follow `speaker-learnings` to consult `framework/learnings/INDEX.md`: open the learnings whose situation matches this project, decide for each whether it applies, and log the decision. They are advice from earlier projects, not requirements; do not copy their figures into the objectives.

Resume: if the user names an existing project, read its `project.json`, its latest evaluation and the candidate files, then continue from `state.phase`. Never overwrite a candidate folder; refinements are new candidates with a `parent`.

## 2. Research the reference

Use web search and fetch. Save `reference/reference.json` with every published quantity, its condition and source, digitized on-axis response and impedance points when a plot is available (state the reading uncertainty), dimensions, mass, driver complement and crossover frequencies, and a short `design_reading`: which properties to match (sensitivity, extension, directivity character, load) and which not to copy. Keep the notes factual; the user will read them in the final comparison.

## 3. Research an extensive inventory

Aim wide before you go deep: for each role (woofer, midrange or compression driver, horn or waveguide, tweeter, passive radiator when relevant) collect at least six to ten candidates from at least three manufacturers, from primary documentation (manufacturer datasheets and pages) with a current price and vendor where you can find one. Save each as `inventory/<class>/<id>.json` using the part template: Thiele/Small data, sensitivity, impedance, frequency range, digitized published response when the datasheet has a plot, mechanical data (cutout, depth, displacement, mass), a directivity model for horns and tweeters, and an impedance model for compression drivers, domes and ribbons. Record missing data as `null`, never invent it.

**Crossover stock is inventory too, and one brand is not an inventory.** Collect capacitor, coil and resistor series the same way as drivers: several options for every class of part the design will need, spanning the price range that class is actually sold in, from more than one manufacturer, each with its published tolerance, DCR or ESR, voltage, power and current ratings, physical size, price and availability. A generally available, affordable part is the default and a costlier one has to earn the difference in something the model can see - `framework/references/crossover-design.md` section 7 says which quantities those are and how to settle it with the tolerance draws and the stress run. So the inventory has to contain the cheap option for a position before the design can prefer it, and an inventory of one premium series is a decision made by omission. Where a class only exists at one price - a large air-core coil, say - record that, because it tells the designer where the money will go. Note the stock values each series is sold in: `crossover_fit` snaps to those lists, and a value the grid cannot reach is a topology finding rather than a rounding detail.

Screen the inventory with the fast apps before designing: `lf_box` for every woofer in two or three plausible volumes and tunings; `directivity` for the horn and tweeter candidates at the intended crossovers; `source_response` statistics for sensitivities. Write `inventory/screen.md` with what you learned and which combinations you will take into iteration 1, and why.

## 4. Iterate

Each iteration:

1. Designer phase (`speaker-designer`): create `candidates_per_iteration` candidates. In iteration 1 make them genuinely different (different woofer, alignment or upper assembly), not three tunings of one idea. From iteration 2 on, at least one candidate answers each refinement request of the last evaluation, and one may still be exploratory.
2. Evaluator phase (`speaker-evaluator`): score all candidates of this and previous iterations from their result files, compare with the reference and with each other, and write `evaluations/iteration-N.md` with a ranking and concrete refinement requests.
3. Update `project.json`: iteration counter, candidate list with a one-line verdict each, and the log.

Role separation: when subagents are available, run the designer and the evaluator as separate subagents with the corresponding skill and the project path, so that the evaluation is not written by the same context that made the design choices. Without subagents, do the roles sequentially and note that in the log. The orchestrator never edits a candidate to improve its score.

Detailed analysis (`cavity_modes` with the FVM basis, `plate_structure`, `lf_uncertainty`, `board_nodal`) is run for the finalists of the last iteration, and earlier if an evaluation asks for it to decide between candidates.

Stop when the iteration counter reaches the limit, or earlier when the evaluator states that the remaining requests cannot change the ranking. Do not spend an iteration chasing the last tenth of a decibel.

When a model or input error is discovered mid-project, log it as a correction with the candidates it affects, rerun those candidates, and consult the process learnings before deciding how it counts against the iteration budget.

## 5. Select and document

Select the best candidate from the last evaluation's ranking; the selection statement names the missed objectives with their margins and the model assumptions that carry the most risk. Then follow `speaker-documentation` to produce `final/`, whose deliverable is the PDF `final/<slug>-design-package.pdf` with its Markdown sources and images beside it. Deliver to the user: the PDF path, a short standalone summary of the selected design, the missed objectives, and what a builder must verify by measurement.

The PDF is written for the builder: drawings, schematic, plots, parts and the assumptions that change what a builder does, with the framework's own provenance left in the project folder. `speaker-documentation` states what each document carries and what the tools do not draw on their own; treat those requirements as documentation quality rather than as further design objectives.

## 6. Postmortem and learnings

Every run ends with `speaker-learnings`: write `postmortem.md` in the project folder (also when the run stops early or the brief was not met), then distill the findings that a future project could act on into `framework/learnings/` as advice, updating existing learnings where the mechanism is already covered. This step is part of the run, not optional follow-up; the next project starts by reading what this one wrote.

## Rules that do not bend

- Never present simulated figures as measurements; the documents say "predicted" or "simulated".
- Never invent driver data or prices; a missing number stays `null` and is listed as an open item.
- Never silently narrow the brief. If a constraint cannot be met by any inventory part, say so in the evaluation and let the user decide whether to relax it.
- Run every simulation as its own command and keep both the parameter file and the result file in the candidate's `sim/` folder so every figure in a document can be traced to a file.
- Do not modify the Python applications during a project to make a result look different. If an app has a bug, fix it, rerun every affected candidate, and log it.
- A claim that something cannot be built or cannot be fitted is a finding with a derivation behind it: the dimensions, what they conflict with, and the alternatives tried. State it that section or do not state it.
- Design the loudspeaker that was asked for. Cooling assemblies, thermal management and other hardware that no passive loudspeaker contains are a sign that an earlier choice was wrong; go back to that choice.
