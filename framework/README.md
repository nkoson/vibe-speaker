# Loudspeaker design framework (LLM-driven)

A passive loudspeaker design workflow in which the language model designs, judges and documents, and small standalone Python applications compute the physics.

```
framework/
  README.md                  this file
  bootstrap.py               creates .speaker-venv from ../requirements.txt and verifies the apps
  skills/                    the design process as skills for the agent
    speaker-design/          orchestrator: project lifecycle, research, iteration, selection
    speaker-designer/        how to build and refine a candidate with the simulations
    speaker-evaluator/       how to score, compare and send candidates back for refinement
    speaker-documentation/   how to write the final construction and performance documents
    speaker-learnings/       consult past learnings, write the postmortem, distill new learnings
  learnings/                 one advice file per learning from past projects, with INDEX.md
  references/                engineering principles with their sources: cabinet geometry and materials,
                             baffle and driver placement, passive radiators, alternative loadings, horn
                             and waveguide design, arrays, target response, crossover design
  simulations/               standalone simulation apps, one folder each, documented next to the code
    README.md                inventory, conventions and data flow
    _common/                 shared physics and JSON plumbing
    examples/                a runnable example chain (outputs land in examples/out, ignored by git)
  tools/                     plotting, cabinet drawing and cut list, schematic and board netlist, PDF assembly
  templates/                 JSON and Markdown templates for project files
  tests/                     pytest suite that runs the example chain and checks invariants
  projects/                  design projects created by the skills (ignored by git)
```

## How the pieces fit

1. The user describes a speaker and a reference product. The `speaker-design` skill creates `framework/projects/<slug>/` with the brief, the iteration limit and the tolerances the user cares about.
2. The agent researches the reference and a broad inventory covering every required component role: drivers, horns/waveguides, passive radiators, complete/modular ports, crossover stock and other critical parts. The [component research procedure](skills/speaker-design/references/component-research.md) separates catalogue discovery from simulation shortlists, records coverage/exclusions, and requires search expansion when gaps or impractical banks constrain a design. Each project keeps exact part records and an `inventory/search-review.md`; detailed candidate limits do not cap the researched pool.
3. Following `speaker-designer`, the agent builds candidates: it writes parameter files, runs the simulation apps, reads the result documents and iterates on alignment, cabinet, crossover and placement.
4. Following `speaker-evaluator`, the agent scores every candidate from the result documents against the brief, the reference and the other candidates, and writes refinement requests.
5. Design and evaluation alternate until the iteration limit is reached. The best candidate is selected with a written justification.
6. Following `speaker-documentation`, the agent produces the construction package as one PDF (with its Markdown sources and images kept beside it): cabinet drawings and cut list, crossover schematic, connection table and parts list, performance plots with practical engineering interpretation, and a two-sided comparison with the reference.

7. Every run ends with a postmortem in the project folder; its transferable findings are distilled into `framework/learnings/` as advice that the next project reads at its start.

The skills point into `framework/references/` at the decisions the engineering governs, and into `framework/learnings/` at the decisions where earlier projects went wrong. A reference states what is true of loudspeakers and cites where it is written down; a learning states what happened in one project. Neither is enforced by code and neither supplies a project's objectives.

Simulations report; the model decides. No Python code in this folder marks a result as blocked, failed or viable, and no learning is enforced by code.

## Running

`python3 framework/bootstrap.py --tests` creates `.speaker-venv` in the repository root, installs numpy, scipy, matplotlib, reportlab, pypdfium2 and pytest, runs the example chain and the tests. Then use `.speaker-venv/bin/python` for everything.

```
.speaker-venv/bin/python framework/simulations/examples/run_examples.py
.speaker-venv/bin/python -m pytest framework/tests -q
```

The skills are linked into `.claude/skills/` for Claude Code and `.agents/skills/` for other agent hosts; `AGENTS.md` at the repository root is the generic entry point.

Incorporated project findings are tracked in [the improvement plan](plans/incorporate-learnings-2026-09-28.md). `learnings/` may have no active records after verified incorporation; its index and authoring format remain for future findings.

Simulation-only design is the default: the agent owns final stock values and construction choices, using sourced inputs and robustness studies. Room-aware work uses [room_response](simulations/room_response/README.md) for 3D rectangular-room reflection and seating scenarios. The [architecture and model coverage procedure](skills/speaker-designer/references/model-coverage.md) connects the available simulations; [cabinet construction](references/cabinet-construction.md) and [crossover assembly](references/crossover-assembly.md) cover physical realization. The [October incorporation record](plans/incorporate-learnings-2026-10-15.md) records the integrated project findings.

The advanced chain includes shared assembly geometry, exterior boundary acoustics, driven room modes, triangulated reflected-energy transport, coupled cabinet radiation, distributed loading, general-network fitting, nonlinear/electrothermal states and correlated scenario replay. See [simulation methods](references/simulation-methods.md) and the designer's [connection guide](skills/speaker-designer/references/advanced-simulation.md). [Generated benchmarks](benchmarks/catalog.json) report equation errors and residuals; design decisions stay with the agent.
