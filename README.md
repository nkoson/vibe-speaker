# Passive loudspeaker design framework

An agent-driven workflow for designing passive loudspeakers. The language model researches, designs, evaluates and documents; small standalone Python applications compute the physics and return JSON. No Python code decides whether a design is good, blocked or viable.

Everything lives in [`framework/`](framework/README.md).

## Quick start

Open this folder in Claude Code and describe the speaker you want, for example:

> Design a passive three-way speaker that approaches the published performance of the Klipsch Forte IV. Similar size, three iterations. Research the reference and a broad parts inventory first.

The `speaker-design` skill (linked in `.claude/skills/` and `.agents/skills/`; `AGENTS.md` is the entry point for other agent hosts) creates a project under `framework/projects/`, researches the reference and the parts, builds and refines simulated candidates with the apps in `framework/simulations/`, evaluates them, picks the best within the iteration limit and writes the documentation package.

## Install

```
python3 framework/bootstrap.py --tests
```

This creates `.speaker-venv/` inside the repository (with the project-local uv in `.speaker-tools/` when present, otherwise the standard venv module), installs `requirements.txt` (numpy, scipy, matplotlib, reportlab, pypdfium2, pytest), runs every simulation example and the test suite. Afterwards use `.speaker-venv/bin/python` for every command; `python3 framework/bootstrap.py --check` re-verifies without installing.

```
.speaker-venv/bin/python framework/simulations/examples/run_examples.py   # run every simulation example
.speaker-venv/bin/python -m pytest framework/tests -q                     # test suite
```

## What is in `framework/`

| Path | Purpose |
|---|---|
| `framework/skills/speaker-design/` | Orchestrator skill: project lifecycle, research, iteration, selection |
| `framework/skills/speaker-designer/` | How to build and refine a candidate with the simulations |
| `framework/skills/speaker-evaluator/` | How to score, compare and request refinements |
| `framework/skills/speaker-documentation/` | How to write cabinet, crossover, performance and reference-comparison documents |
| `framework/skills/speaker-learnings/` | Consult past learnings, write the postmortem, distill new learnings |
| `framework/learnings/` | Advice from past projects, one file per learning, indexed |
| `framework/simulations/` | Eighteen standalone simulation apps, each with `run.py`, `README.md` and `example.json`; see its [README](framework/simulations/README.md) for the inventory |
| `framework/tools/` | Plotting, cabinet drawing and cut list, crossover schematic and board netlist, PDF assembly of the final package |
| `framework/templates/` | Project, reference, part, candidate and evaluation templates |
| `framework/tests/` | pytest suite running the example chain |
| `framework/bootstrap.py` | Creates the local environment and verifies the apps |
| `framework/projects/` | Design projects (ignored by git) |

## Simulations

All models are linear and small-signal with declared assumptions, and every result document carries the model notes. They cover the lumped bass alignment (sealed, vented, passive radiator) and its tolerance spread, per-section acoustic and electrical source models from datasheets or measurements, source directivity, finite-baffle diffraction, loaded passive crossover ladders and their fitting to a target, the physical board as a netlist in every connection mode, the coherent whole-speaker response on and off axis with floor image and polarity studies, the internal cavity acoustics with lining and braces, panel vibration, and descriptive response statistics with reference comparison.

The applications output results only. Thresholds are parameters; interpretation is the agent's job and is written into the project's evaluations with the file path of every figure.

## Scope and limits

Nothing produced here is a measurement. Digitized datasheet curves carry reading uncertainty, horn and tweeter phase is reconstructed, and distortion, compression, port noise, breakup beyond published data, room effects and thermal behaviour are not simulated. A first-build package from this framework is a starting point that a builder verifies by measuring drivers, tuning and the crossover.

## License

See `LICENSE`.
