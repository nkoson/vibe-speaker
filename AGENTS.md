# Agent entry point

This repository is a loudspeaker design framework in which the agent designs, evaluates and documents while standalone Python applications compute the physics. For any request to design, continue, compare or document a loudspeaker, read and follow `framework/skills/speaker-design/SKILL.md`; it names the companion skills (`speaker-designer`, `speaker-evaluator`, `speaker-documentation`, `speaker-learnings`) and when to use them.

The same skill folders are linked from `.agents/skills/` and `.claude/skills/` so that hosts which discover skills in either location find them. Each skill is a folder with a `SKILL.md` whose frontmatter carries `name` and `description`.

Setup: `python3 framework/bootstrap.py --tests` creates `.speaker-venv` inside the repository and verifies the simulation apps. Use `.speaker-venv/bin/python` for every command afterwards. See `README.md` and `framework/README.md` for the layout, and `framework/simulations/README.md` for the simulation inventory and JSON conventions.

Rules that hold for every agent:

- The simulation apps report results; they never decide whether a design is good, blocked or viable. Judgement is the agent's and is written into the project's evaluations with the file path of every figure.
- Design projects live in `framework/projects/<slug>/` and are not committed. Source changes go through Git.
- Learnings in `framework/learnings/` are advice from earlier projects, read at the start of a project and updated from the postmortem at its end. They are not rules and are not copied into objectives.
- References in `framework/references/` are the engineering with its sources: driver selection, enclosure alignments, loadings other than sealed and vented, system architecture, transducer types, horn and waveguide design, arrays and directivity control, cabinet geometry, cabinet materials and panels, baffle and driver placement, passive radiators, passive crossover design, target response, and the limits of the models themselves. Read the one that covers the work before doing it, and cite it the way you cite a result file.
- Nothing produced here is a measurement; documents say "predicted" or "simulated".
- The final document is written for the builder, not for the framework: it carries drawings, schematics, plots and the assumptions that affect building or interpreting the speaker, and leaves application provenance, file paths and iteration history in the project folder. `framework/skills/speaker-documentation/SKILL.md` says what each document contains.
