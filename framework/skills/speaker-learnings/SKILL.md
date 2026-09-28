---
name: speaker-learnings
description: Carry knowledge between loudspeaker design projects - consult the learnings from past projects before and during a run, write the postmortem when a run ends, and distill its findings into new or updated learnings as advice. Use at the start of a speaker-design project, whenever a decision resembles a past situation, and after a project's package has been delivered or the run has stopped.
---

# Speaker learnings

Past projects leave two things behind: a `postmortem.md` in the project folder and one file per distilled learning in `framework/learnings/`. A learning is advice with evidence, never a rule. The simulation apps and the other skills do not enforce learnings; you read them, decide whether they apply to the project in front of you, and record what you did with them.

## Consult (start of a project and at decisions)

1. Read `framework/learnings/INDEX.md`. An empty active index is valid: incorporated findings live in the framework and their disposition is recorded in `framework/plans/`. Open every learning whose `applies_when` matches the current project or the decision at hand. At the start of a project that is usually the validation, research and process phases; during iterations the design, evaluation and selection phases; before the package the documentation phase.
2. For each learning you open, decide: applies as written, applies with a change, or does not apply here, and why. Write that in the project's `project.json` log as one line per learning, for example `considered <learning-id>: ran the proposed check on the actual sources; recorded result and interpretation`.
3. Do not copy a learning's figures or thresholds into the project's objectives. Its mechanism may apply; its numbers belonged to another brief.
4. When a learning turns out to be wrong for a good reason in this project, note that in the log; it feeds the postmortem.

The designer and evaluator skills point here at the moments where past projects went wrong; the pointer is a reminder to read, not an instruction to comply.

## Postmortem (end of a run)

Write `framework/projects/<slug>/postmortem.md` from `framework/templates/postmortem.md` after the package is delivered, or when the run stops early for any reason. Do it while the files are fresh, and before any celebration of the package. Cover:

- Outcome against the brief's central objectives, with the figures and their file paths.
- What went wrong and what went right, as mechanisms: model errors, input errors, ordering of work, selection reasoning, research gaps, tooling gaps. Give each its evidence.
- Whether more or better simulation would have changed the outcome, and whether the brief is shown to be infeasible or only unsolved by this process.
- What a future attempt should do differently, as advice.
- Which existing learnings were consulted, which helped, which did not apply, which were wrong.
- Tooling defects found and whether they were fixed in `framework/` (link the commit or test).

Be as hard on the process as the facts allow. A postmortem that only praises the package is worthless to the next project.

## Distill (after the postmortem)

For each finding in the postmortem that a future project could act on:

1. Check `framework/learnings/INDEX.md` for an existing learning about the same mechanism. If one exists, rewrite it as one combined learning: add this project to `project`, adjust `confidence` to the evidence, and combine the failure and prevention across projects. Resolve contradictory evidence in qualified advice rather than appending another narrative.
2. Otherwise write a new file following `framework/learnings/README.md`: frontmatter and exactly two body sections, `What went wrong` and `What could have helped`. Combine consequence with the failure and phrase prevention as options/checks. Keep detailed figures and evidence in the source project postmortem. One mechanism per file. Name the file by the mechanism, not by the project.
3. Add or update the line in `INDEX.md` with its phase and `applies_when`.
4. Do not encode project-specific judgments or thresholds as software rules: the simulation apps report and the agent judges. Software defects belong in `framework/` with regression checks. During authorized framework improvement work, incorporate process findings into skills/templates and engineering into sourced references, using the retirement procedure below. If a finding is already incorporated, record verification in the postmortem rather than recreating an active learning; if it recurred, name the remaining gap.
5. Leave out findings that were specific to this brief or this reference and would not recur.
6. When a finding is not project experience but general engineering that the framework failed to state - a principle, a formula, what a rating means - it belongs in `framework/references/` instead, or in an existing reference that is silent or wrong on the point. Follow `framework/references/README.md`: sources named, practice labelled as practice, no figures from this brief.

Run `.speaker-venv/bin/python -m pytest framework/tests/test_learnings.py -q` to confirm the files are well formed, then commit framework changes if the user asked for commits. Project folders and their postmortems remain uncommitted as required by AGENTS.md.

## Retire incorporated findings during framework improvement

When the user authorizes incorporating learnings, first consolidate each active file into the two-section format and create a grouped plan under `framework/plans/`. For every learning record the current skill/reference/simulation review, planned change, implementation location and completed verification. Verify existing fixes rather than claiming they are new. Only then delete each incorporated learning and its index row. Preserve README, INDEX and the plan, and allow the active directory to be empty. A plan marked pending is not incorporation evidence.

## Keep it honest

- A learning from one project has `confidence: low`; it becomes stronger only when another project confirms it.
- Prefer fewer, sharper learnings. If the index grows past what a reader can scan in a minute, merge.
- Never paste a learning's text into a project document as if it were a finding of that project.
