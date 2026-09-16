---
name: speaker-learnings
description: Carry knowledge between loudspeaker design projects - consult the learnings from past projects before and during a run, write the postmortem when a run ends, and distill its findings into new or updated learnings as advice. Use at the start of a speaker-design project, whenever a decision resembles a past situation, and after a project's package has been delivered or the run has stopped.
---

# Speaker learnings

Past projects leave two things behind: a `postmortem.md` in the project folder and one file per distilled learning in `framework/learnings/`. A learning is advice with evidence, never a rule. The simulation apps and the other skills do not enforce learnings; you read them, decide whether they apply to the project in front of you, and record what you did with them.

## Consult (start of a project and at decisions)

1. Read `framework/learnings/INDEX.md`. Open every learning whose `applies_when` matches the current project or the decision at hand. At the start of a project that is usually the validation, research and process phases; during iterations the design, evaluation and selection phases; before the package the documentation phase.
2. For each learning you open, decide: applies as written, applies with a change, or does not apply here, and why. Write that in the project's `project.json` log as one line per learning, for example `considered validate-simulation-chain-before-iteration-one: ran the woofer-plus-outlet case, agreement within 0.3 dB`.
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

1. Check `framework/learnings/INDEX.md` for an existing learning about the same mechanism. If one exists, update it: add this project to `project`, raise `confidence` if the project confirmed it, and refine the advice. If the project contradicted it, rewrite it and say why.
2. Otherwise write a new file following `framework/learnings/README.md`: frontmatter, observation with figures, why it mattered, advice phrased as options and checks, evidence paths. One mechanism per file. Name the file by the mechanism, not by the project.
3. Add or update the line in `INDEX.md` with its phase and `applies_when`.
4. Do not turn a finding into code: the simulation apps report and the skills advise. If a finding was a software bug, the fix and its regression test belong in `framework/`, and the learning records how it was noticed so the next project can notice similar ones.
5. Leave out findings that were specific to this brief or this reference and would not recur.
6. When a finding is not project experience but general engineering that the framework failed to state - a principle, a formula, what a rating means - it belongs in `framework/references/` instead, or in an existing reference that is silent or wrong on the point. Follow `framework/references/README.md`: sources named, practice labelled as practice, no figures from this brief.

Run `python -m pytest framework/tests/test_learnings.py -q` to confirm the files are well formed, then commit the learnings together with the postmortem's project if the user has asked for commits.

## Keep it honest

- A learning from one project has `confidence: low`; it becomes stronger only when another project confirms it.
- Prefer fewer, sharper learnings. If the index grows past what a reader can scan in a minute, merge.
- Never paste a learning's text into a project document as if it were a finding of that project.
