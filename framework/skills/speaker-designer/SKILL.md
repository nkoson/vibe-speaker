---
name: speaker-designer
description: Build or refine one simulated passive loudspeaker candidate - choose parts from the project inventory, set the bass alignment and cabinet, place the drivers, design and fit the passive crossover, and run the standalone simulation apps so the candidate folder holds every parameter and result file. Use inside a speaker-design project when creating or improving a candidate.
---

# Speaker designer

Build one candidate from the project brief, inventory, reference and latest evaluation. Record its physical idea, choices, sources and parameter/result files. Simulation results support your engineering judgement; they do not choose parts, approve a design or substitute their defaults for the brief.

## Choose the physical model

Read `framework/references/README.md` for the relevant engineering and [model coverage](references/model-coverage.md) for the available application chain. Use [advanced simulations](references/advanced-simulation.md) for exact inputs, coupling ownership and refinement studies. Read each app's README before its first use and run it with `.speaker-venv/bin/python framework/tools/run_simulation.py`.

Start with the simplest physical model that resolves the decision, then add detail where it can change the choice. Distinguish the user's architecture constraints from convenient defaults. Electrical order, brace spacing, material choice, attenuation and resistor count are design variables whose effects can be compared; their acceptability follows from this brief and the physical evidence.

## Prepare a candidate

Read the project's inventory search review and [component research procedure](../speaker-design/references/component-research.md). The inventory is expandable: request or perform a targeted search when fit, loading, cost or physical realization exposes a gap. A candidate's selected parts are not a restriction on alternatives for the next comparison.

1. Populate `candidate.json` from the template, including parent, design intent and chosen parts.
2. Establish the LF envelope with `lf_box` and appropriate loss/volume/tuning scenarios. Inspect driver parameter basis, efficiency/extension trade, sustained cutoffs, current, excursion and outlet limits at the actual drive. For lines, folded horns or chamber networks, use `distributed_loading` to retain the motor load and separate radiating paths.
3. Define cabinet geometry before fitting. Use `assembly_geometry` and `framework/templates/geometry-audit.md` for shared IDs, solids, air domains, joints, treatment zones, source normals and installed clearances. Reconcile actual net volume with the alignment. Consult `framework/references/cabinet-construction.md` and [construction audit](../speaker-documentation/references/construction-audit.md) for machining and assembly.

   For a reflex design, compare complete stock ports and modular assemblies: a separate outer flange/flare, a straight tube cut to length, and an inner flare. A tube with an integral flare can be shortened at its unflared end; otherwise fit a separate flare at the cabinet end as well as the room end. Recess the outer flange when flush mounting is specified. Include commercially available elbows or bent tubes when a straight duct cannot fit with adequate mouth clearance; account for bend geometry and flow/loading uncertainty. An off-the-shelf-port requirement can be met with purchased modular parts and a custom-cut tube. Select the port/alignment and resolve its physical installation before constructing and fitting the passive crossover; then verify the complete system with that selected loading.
4. Build each source with explicit pressure/voltage, phase and baffle conventions. Use [simulation integrity](../speaker-design/references/simulation-integrity.md) and the simulation-audit template. Apply external resistance once; pair cone and outlet from the same model and normalization. For important cavity or shape effects, use canonical `cavity_modes` or `exterior_bem` outputs through `source_response` or directly as source references.
5. Check driver bandwidth, published protection conditions, beamwidth, source spacing, acoustic depths and likely listening angles together. The spacing formulas are diagnostic screens; the complex section sum describes the actual modeled window.

## Fit and realize the network

Use `framework/references/crossover-design.md` and [crossover search](references/crossover-search.md). Establish the system level from the complete LF envelope. Choose a topology for named response/load/protection needs and compare credible alternatives rather than inheriting parts without examining their function.

`crossover_fit` handles ladders and returns continuous and joint-stock numerical trials. `network_fit` uses `board_nodal` for general netlists and explicit numerical constraints, including terminal exposure, load and component power. Targets and constraint values come from the brief and sourced physical conditions. The returned minima and margin signs are evidence for your selection, not a design verdict.

Test known and perturbed starts, preserve the incumbent, examine active bounds and inventory gaps, and inspect all evaluated stock combinations when a sparse series matters. Before freezing a bank, search single-body and nearby-stock alternatives and refit them as needed under the component research procedure. Count actual bodies, cost and installation size during selection. Keep losses, SKU, dimensions and ratings attached to the actual selected values. A response score that omits the top octave, branch leakage or a competing bass/level objective can hide a material trade.

Run the realized network through `crossover_network` or `board_nodal` with tolerances and the relevant drive. Read frequency-coincident power, physical-leaf stress, terminal transfer and complex input load. For mutual coils or transformers, use explicit coupling parameters and compare plausible coupling scenarios; a drawing does not determine coupling automatically. Use `framework/references/crossover-assembly.md` to connect the circuit to the physical board.

## Evaluate the complete response

Run `whole_speaker` with each radiator, outlet, source location, baffle convention and realized transfer. Inspect individual branches, coherent sum, polarity and acoustic-depth scenarios before attributing a feature. A directivity discontinuity can depend on driver pattern, geometry and crossover overlap; controlled comparisons distinguish them.

Use `response_metrics` on the actual objective curves and bands. When directivity and room balance matter, use `spinorama` with full angular fields or declared priors and inspect per-emitter coverage. Its angularly weighted predicted-in-room curve is distinct from a specific room pressure calculation.

For room-dependent briefs, compare `room_modal`, `room_response` and `room_rays` over a listening region as described in the advanced guide. For cabinet radiation, compare isolated-panel screening with `coupled_cabinet` where the interaction affects the choice. For level-dependent behavior, use `electrothermal_network` and `nonlinear_driver` with sourced parameters or explicit ranges. Numerical refinement and physical uncertainty are separate studies.

Use `system_scenarios` to replay the dependency chain with correlated production variation and explicit model alternatives. Read nominal recovery, unresolved cases and conditional statistics. Prefer choices whose useful advantages survive plausible assumptions; a percentage of arbitrary scenarios is not a production yield.

## Freeze and record

Record the final physical parts, wiring/polarity, geometry, source contracts, all result dependencies, cost completeness and the figures that motivated the selection. Cold-replay the chosen chain. A refinement normally becomes a new candidate, with changed variables isolated for its first comparison and dependent results regenerated. Keep remaining limitations specific to their effect on this design, and deliver definite values under the chosen assumptions.
