# Learnings from past projects

One file per learning, distilled from project postmortems. A learning is advice with its evidence, not a rule: it says what happened in a past project, why it mattered, and what to consider next time. Every project decides for itself whether the advice applies; nothing in the simulation apps or the skills enforces a learning.

`INDEX.md` lists every learning on one line with its phase and the situation it applies to. Read the index at the start of a project and open the files whose situation matches; record in the project's `project.json` log which learnings were considered and what was done with them. Learnings are written by the `speaker-learnings` skill after a project's postmortem.

## File format

```
---
id: short-kebab-case-slug            (equals the file name without .md)
date: YYYY-MM-DD                     (when the learning was written)
project: <slug of the source project, or several separated by commas>
phase: validation | research | design | evaluation | selection | documentation | process
confidence: low | medium | high      (low: one project; raise it when another project confirms it)
applies_when: one sentence naming the situation in which to read this
tags: [comma, separated, words]
---

## Observation
What happened, with the figures that showed it.

## Why it mattered
The consequence for the project's outcome.

## Advice
What to consider next time, phrased as options and checks, not as commands.

## Evidence
Paths inside the source project (framework/projects/<slug>/...) or files in the repository.
```

## Writing a learning

- One idea per file. Merge into an existing file when it already covers the idea; raise `confidence` and add the project to `project`.
- Keep the observation factual and the advice conditional. Write "consider", "check", "expect", not "always" or "never".
- Do not copy a project's thresholds or targets into advice; they belong to that brief. Describe the mechanism instead.
- Do not restate what the simulation READMEs already say about how an app works; a learning is about how a project went wrong or right, and how it was noticed.
- Delete or rewrite a learning that a later project shows to be wrong; say so in the file rather than leaving a contradiction.
