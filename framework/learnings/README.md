# Learnings from past projects

One active file per unresolved learning, combining all source projects into one mechanism. A learning is advice, not a new objective or a software acceptance threshold. Each body states only what went wrong and what could have helped prevent it; project evidence belongs in the source postmortems, and incorporation evidence belongs in the framework improvement plan.

`INDEX.md` lists each active learning once by phase and situation. An empty index is valid after the framework has incorporated all active findings. Consult matching files through `speaker-learnings` and record applicability in the project's log.

## File format

```markdown
---
id: short-kebab-case-slug
date: YYYY-MM-DD
project: source-project, another-source-project
phase: validation | research | design | evaluation | selection | documentation | process
confidence: low | medium | high
applies_when: one sentence naming the situation
tags: [comma, separated, words]
---

## What went wrong
One combined failure mechanism and consequence across the source projects.

## What could have helped
Concrete prevention options or checks, including limitations or contradictory evidence.
```

The id equals the filename stem. Confidence reflects independent evidence, not repetition in one project. Do not copy one brief's thresholds into advice.

## Consolidate and incorporate

When new evidence matches an existing mechanism, rewrite its two sections as one combined learning and update the project list. Do not append a second project narrative. Combine contradictions into qualified advice; omit success narratives unless they explain how the failure could have been prevented.

During authorized framework improvement work, group the active findings in a plan, inspect current skills, references and simulations, and record the concrete fix for each learning. General engineering belongs in sourced references, process changes in skills/templates, and demonstrated software defects in code with meaningful regression checks. Existing fixes may satisfy part of a learning, but verify them and close any workflow gaps.

Remove a learning only after its plan entry names the incorporated changes and completed verification, then remove its INDEX row. Keep the plan as the record of disposition. Preserve README and INDEX so future postmortems can add new unresolved learnings. This process does not authorize unrelated source changes during an ordinary design project.
