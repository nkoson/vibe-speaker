---
name: speaker-learnings
description: Carry knowledge between loudspeaker design projects - consult the learnings from past projects before and during a run, write the postmortem when a run ends, and distill its findings into new or updated learnings as advice. Use at the start of a speaker-design project, whenever a decision resembles a past situation, and after a project's package has been delivered or the run has stopped.
---

# Speaker learnings

Carry project experience into future designs as qualified advice. Learnings record mechanisms from prior work; references hold sourced engineering and skills hold reusable procedures. These roles help keep one project's thresholds out of another project's objectives.

## Consult

Read `framework/learnings/INDEX.md` and open findings relevant to the current decision. Record whether each applies, applies with a change, or does not apply, with a brief reason in the project log. An empty active index is valid after incorporation; historical dispositions live in `framework/plans/`.

## Record experience

At delivery or when a run ends, write the project postmortem from `framework/templates/postmortem.md`. Include the outcome against central goals, what changed the design, input/model/tooling problems and their evidence, useful refinements, and which earlier advice helped. Distinguish an unsolved search from demonstrated physical infeasibility.

For a transferable finding, update an existing learning about the same mechanism or write one using `framework/learnings/README.md`. Combine the failure and prevention across projects into `What went wrong` and `What could have helped`. Keep detailed numbers and artifacts in the source project; qualify advice where evidence differs. Confidence reflects independent corroboration, not repeated discussion.

General engineering belongs in sourced references. A demonstrated software defect belongs in source code with a relevant numerical regression check. When a finding is already integrated, record that verification rather than recreating it as unresolved advice.

## Incorporate during framework work

When framework improvement is authorized, map each active finding to its current implementation, make the change and record verification. Retire active rows after that evidence is complete, preserving the incorporation record and any requested historical originals. This is integration into the working framework, not an invitation to leave findings as disconnected study notes.

Run `.speaker-venv/bin/python -m pytest framework/tests/test_learnings.py -q` after updating learning records. Commit framework changes when requested; project folders and their postmortems stay outside Git.
