# Incorporate project learnings into the framework

Status: complete. All 28 learnings incorporated, verified and removed from the active directory. Branch: `improve/incorporate-project-learnings`.

Scope: all 28 learning files present at the start, including existing uncommitted edits and five additions. Each was overwritten with one combined failure and prevention statement before implementation. README and INDEX are infrastructure, not learning records. Project-specific thresholds do not become framework rules; simulations continue to report, and agents judge.

## Execution and verification

1. Consolidate each file across all source projects (completed).
2. Reviewed each group against skills, engineering references and available simulation/tool behavior (completed below).
3. Implemented the changes, retained existing numerical fixes and tested the missing contracts.
4. Focused checks passed; final full suite: `.speaker-venv/bin/python -m pytest framework/tests -q` → **142 passed in 16.83 s**, including every simulation example. Reviewed workflow/reference contradictions and retired-learning dependencies.
5. Recorded confirmation for each of the 28 learnings, then removed each active file and cleared INDEX. README and INDEX remain for future projects.
6. This change set is committed on the named new branch with framework source, documentation, templates, tests and this plan. Project folders remain uncommitted.

## G1 Source calibration and conventions

### Current framework review

Skills: designer sections 4–6; orchestrator reference research. References: measurement-and-model-limits, crossover-design, target-response. Simulations: source_response, lf_box, whole_speaker/radiation; tests: published_shape_modes, radiation_invariants.

### Implemented plan

Published-shape replacement and normalization invariants exist. LF sources lack explicit level calibration and a driver-terminal voltage basis; reference templates encourage assumed conditions. Add supported acoustic calibration and terminal normalization (including outlet output), preserve impedance and mechanical predictions, document legacy source-voltage behavior, add regression tests, and require early graph/basis audits.

### Learning coverage

#### whole-speaker-output-is-already-one-metre-equivalent

What went wrong: An extra distance correction was applied to output already normalized to its reference distance, corrupting reported sensitivity and fit targets.

What could have helped: Check a single unity-transfer section against its source at the declared reference distance, accounting for actual path length and baffle gain; record the convention once and apply no second normalization.

Incorporation: **confirmed**. Framework locations: simulations/whole_speaker/README.md; templates/simulation-audit.md.

Verification: Existing test_radiation_invariants.py verifies 1, 3 and 10 m equivalent pressure; the new audit requires actual-path/baffle accounting.

#### do-not-double-count-woofer-rolloff

What went wrong: Multiplying a full published response by a lumped cone response counted inductive rolloff twice; using the lumped model alone also understated the handover band. An option name was mistaken for proof that replacement was implemented.

What could have helped: Assign ownership of level and slope by band, use and verify published-shape replacement above the blend, retain modeled bass below it, and compare actual bass and upper slopes with calibrated source data. Label reconstructed phase as inferred.

Incorporation: **confirmed**. Framework locations: skills/speaker-designer/SKILL.md, Source and crossover audits; references/measurement-and-model-limits.md §8.

Verification: Existing test_published_shape_modes.py confirms replacement slope and preserved bass; source_response examples still exercise both modes.

#### check-upper-driver-graph-calibration

What went wrong: Graph calibration errors and curves measured on a different horn distorted upper-driver level, shape and the resulting crossover.

What could have helped: Record several graph anchors and reading uncertainty, verify the reproduced sensitivity, and record the test horn or baffle and phase provenance before fitting.

Incorporation: **confirmed**. Framework locations: templates/simulation-audit.md; templates/part.json source_audit; skills/speaker-designer/SKILL.md.

Verification: Reviewed anchor, uncertainty, mounting and phase fields against the original failure; template JSON parses.

#### put-the-series-resistance-in-one-place

What went wrong: A coil allowance remained in box pressure while the crossover applied the real coil DCR again. Unity-transfer validation did not expose the repeated loss.

What could have helped: Use a terminal-referenced LF source with all external series resistance represented once in the network; retain allowance runs for alignment screening only. Validate a known resistor moved between the box drive and the network, including current and outlet pressure.

Incorporation: **confirmed**. Framework locations: simulations/source_response/run.py _box_pressure; simulations/lf_box/README.md; skills/speaker-designer/SKILL.md.

Verification: test_source_basis.py proves terminal-normalized cone/outlet pressure equals zero-resistance physics and reapplying a known resistor restores pressure and RMS current; prefiltered sources are rejected.

#### decide-the-woofer-level-basis-in-the-screen

What went wrong: Disagreement between Thiele/Small-derived and published woofer levels remained unresolved through candidate ranking and required a late external rescaling adapter.

What could have helped: Compare like-for-like levels during screening, choose and record the supported basis and uncertainty before fitting, and use an explicit acoustic calibration with provenance. Preserve electrical current and excursion predictions when correcting acoustic level.

Incorporation: **confirmed**. Framework locations: simulations/source_response/run.py compute; simulations/examples/section_lf_terminal.json; templates/feasibility.md; templates/part.json.

Verification: test_source_basis.py verifies acoustic calibration of cone and outlet, unchanged impedance/raw mechanical result, required provenance, selected-curve voltage and coherent downstream summation. The new example computed successfully.

#### reference-sensitivity-conventions-differ

What went wrong: Room, weighted, per-watt and per-voltage sensitivity figures were compared as the same quantity, and cutoffs derived from digitized plots were presented as published measurements.

What could have helped: Record drive, distance, band, weighting, environment and source for each figure; score only a comparable convention, retain other claims as context, and label derived values from the first report onward.

Incorporation: **confirmed**. Framework locations: templates/reference.json; templates/project.json; templates/evaluation.md; references/target-response.md §10; skills/speaker-documentation/SKILL.md.

Verification: Reviewed explicit unknown conventions, derived labels and removal of the f3-to-f6 example; JSON templates parse and reference tests pass.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G2 Reliable simulation execution

### Current framework review

Skills: designer invocation and orchestrator corrections. References: measurement-and-model-limits. Simulations: shared cli, example runner, radiation_invariants.

### Implemented plan

CLI loads inputs before invalidating output and only handles InputError during compute, so crashes and malformed inputs leave stale computed files. Invalidate the destination before reading inputs, reject input/output aliasing, atomically publish results, add a checked reusable runner with no cache, test crashes and malformed inputs, and provide an actual-project validation template plus cold-replay practice.

### Learning coverage

#### validate-simulation-chain-before-iteration-one

What went wrong: Design iterations used missing rear radiation, inconsistent baffle factors, wrong normalization or source shape, stale dependencies, and unverified aggregate-driver equivalents. Unity checks alone missed losses introduced by the network.

What could have helped: Validate actual project sources before iteration one: colocated cone/outlet sum, placed baffle and propagation, single-section level, source slope, and a known series-resistor transfer. Independently check aggregate pressure, per-motor current and excursion; do not infer distributed cavity validity. Avoid caches or hash transitive dependencies and model code, then cold-replay the selected chain.

Incorporation: **confirmed**. Framework locations: templates/simulation-audit.md; skills/speaker-design/SKILL.md before Iterate; references/measurement-and-model-limits.md §8.

Verification: Actual-project audit now includes unity and known-resistance cases, cone/outlet and aggregate boundaries. test_radiation_invariants.py and test_source_basis.py pass; example chain uses the no-cache checked runner.

#### a-failed-run-must-not-read-the-previous-result

What went wrong: A failed subprocess left a previous computed result in place, which a helper read as the new run and used for scoring.

What could have helped: Invalidate the old output before launch, check process exit and document status, include stderr in the failure, and accept only newly written results. Deliberate caches need content-based dependency and model freshness.

Incorporation: **confirmed**. Framework locations: simulations/_common/cli.py run/write_document; tools/run_simulation.py; simulations/examples/run_examples.py.

Verification: test_run_freshness.py exercises crashes, malformed inputs, atomic publication, input/result collision, failed subprocess stderr and changed referenced file content. All example invocations succeeded.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G3 Feasibility and target setting

### Current framework review

Skills: design research ordering, designer level/placement, evaluator refinement. References: driver-selection, system-architecture, target-response, crossover-design. Simulations: lf_box, directivity, baffle_diffraction, whole_speaker pair_geometry, crossover_fit.

### Implemented plan

Physics and screening outputs exist, but broad upper inventory still precedes bass feasibility and auto targets remain easy to inherit. Make bass and replacement-output screens precede upper research; make explicit bass-supported targets and stock coverage part of the workflow; screen requested crossings with actual phase/window rather than treating spacing rules as hard window predictions. Correct unsafe objective examples and use a feasibility template.

### Learning coverage

#### screen-bass-feasibility-before-broad-upper-inventory

What went wrong: Extensive upper-driver research preceded proof that the allowed bass hardware could provide the required level, extension and excursion envelope.

What could have helped: Screen bass drivers and permitted loadings, volumes and tunings with actual baffle/outlet effects and stress limits first, then research a broad upper inventory matched to the supported level.

Incorporation: **confirmed**. Framework locations: skills/speaker-design/SKILL.md §3; templates/feasibility.md.

Verification: Reviewed research ordering: bass range and output/limits precede upper inventory. Existing LF, uncertainty, baffle and source apps pass the full suite/examples.

#### establish-the-bass-envelope-before-system-sensitivity

What went wrong: Upper-band sensitivity was chosen independently of deep-bass output; larger boxes and favorable box cutoffs were mistaken for balanced full-system performance.

What could have helped: Derive system level from the complete bass-to-midband envelope with realizable losses and limits. Compare equal-voltage fixed-frequency output, sustained cutoff and broad-band shape separately; compare shared bass hardware at equal system level.

Incorporation: **confirmed**. Framework locations: templates/feasibility.md; skills/speaker-designer/SKILL.md, Source and crossover audits; references/target-response.md §10.

Verification: Reviewed separate equal-voltage bass, sustained cutoff and broad-band shape fields and explicit bass-supported target. LF/system numerical tests pass.

#### price-the-removed-output-before-designing

What went wrong: A revision removed a parallel woofer and tightened loading while expecting its output gain to remain, without a replacement mechanism.

What could have helped: State coherent source-count voltage gain, power gain and impedance/current changes first, screen the allowed replacement range, and quantify the lost output and available tradeoffs without claiming a finite search proves universal infeasibility.

Incorporation: **confirmed**. Framework locations: references/crossover-design.md §6; skills/speaker-design/SKILL.md §3; templates/feasibility.md.

Verification: Reviewed coherent pressure versus total power/current arithmetic and scoped the finite-screen conclusion. Removed the prior universal efficiency claim; no project-specific target was imported.

#### set-the-fit-target-from-the-woofer-not-the-optimizer

What went wrong: An automatic starting-response target and unnecessary shelves, compensation and stock DCR fallbacks spent available bass level and worsened impedance. An upper-bass mean alone obscured deep-bass and parallel-driver loading tradeoffs.

What could have helped: Set an explicit target from the full bass envelope, audit passband transfer and compensation, verify exact stock loss coverage, and sweep voicing where necessary. Report voltage sensitivity alongside current and impedance; do not convert wideband sensitivity to per-watt using minimum impedance.

Incorporation: **confirmed**. Framework locations: skills/speaker-designer/SKILL.md, Source and crossover audits; simulations/crossover_fit/README.md; templates/feasibility.md.

Verification: Reviewed explicit target, full bass envelope, insertion-loss/compensation audit and exact stock DCR/fallback coverage. Existing fit and power/parts regressions pass.

#### check-source-spacing-before-a-directivity-objective

What went wrong: Window objectives and later refinement requests ignored minimum physical spacing, phase and upper-driver bandwidth, spending iterations on incompatible crossings.

What could have helped: Compute feasible spacing and crossover intervals before objectives and again before requests; use c/(2d) and c/d as screening quantities and simulate the actual angular window with relative phase. Check top-octave capability when considering coincident alternatives.

Incorporation: **confirmed**. Framework locations: references/system-architecture.md §11; references/baffle-and-driver-placement.md §3; templates/feasibility.md; skills/speaker-evaluator/SKILL.md, Interpret before attributing.

Verification: Reviewed spacing and driver-band checks at both initial screening and refinement, actual phase/window qualification, and top-octave review. Existing pair-geometry/directivity tests pass.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G4 Crossover realization and power

### Current framework review

Skills: designer crossover and evaluator loss/cost. References: crossover-design. Simulations: crossover_network, crossover_fit, board_nodal; tests: network_leaf_stress, network_efficiency_and_parts, fit_ablation_and_stock.

### Implemented plan

Leaf stress, loss, part count, stock snapping and ablation already exist. Retain and verify them. Add stock-derived bounds, DCR trade tables and pad-body screening to normal practice; remove contradictory mandatory compensation language, qualify resistive approximations, and add analytical pad/body and DCR guidance. No new optimizer or automatic design rejection is needed.

### Learning coverage

#### bound-the-fit-to-values-you-can-buy

What went wrong: Narrow seed-centered bounds trapped fits at their limits and requested unavailable coils or avoidable heat; optimizer completion was treated as engineering completion.

What could have helped: Derive bounds from stocked values or explicit feasible banks, inspect each active bound in the same iteration, constrain acoustic behavior through the target, and rerun the exact realized network with its losses.

Incorporation: **confirmed**. Framework locations: skills/speaker-designer/SKILL.md, Source and crossover audits; simulations/crossover_fit/README.md; references/crossover-design.md §9.

Verification: Reviewed stock-derived bounds and same-iteration investigation, without falsely declaring every constrained optimum wrong. test_fit_ablation_and_stock.py and test_crossover_fit_budget.py pass.

#### coil-dcr-is-a-lever-on-the-impedance-minimum

What went wrong: Treating coil DCR only as loss overlooked an available sensitivity-versus-load trade and delayed a workable stock choice.

What could have helped: Sweep actual coil values and DCR together, refit and compare impedance, sensitivity, absolute bass, ripple, cost and coil heat; missing thermal ratings remain unknown. Select from the trade rather than automatically minimizing or increasing resistance.

Incorporation: **confirmed**. Framework locations: references/crossover-design.md §13; templates/feasibility.md; skills/speaker-designer/SKILL.md.

Verification: Reviewed stock-pair DCR sweep outputs including load, fixed-frequency bass and unrated coil heat; actual network/board and insertion-loss tests pass.

#### a-pad-body-is-a-level-step

What went wrong: A broad larger-woofer study pursued resistor removal despite available level gains being smaller than the discrete pad-body thresholds, and overlooked the pad’s protection of the upper driver.

What could have helped: Calculate pad heat and body-count thresholds at the stated drive before new inventory research, compare calibrated achievable levels against them, and check driver power, bass and spacing after pad removal. Treat the resistive formula as screening and verify the loaded network.

Incorporation: **confirmed**. Framework locations: references/crossover-design.md §13; skills/speaker-designer/SKILL.md; templates/feasibility.md.

Verification: Checked resistive voltage-divider/power and integer body-count derivation, nonmonotonic heat, protection after removal and requirement for loaded-network verification. Existing leaf-stress and power-conservation regressions pass.

#### the-crossover-is-a-bill-of-materials

What went wrong: Response-focused evaluation allowed excessive compensation loss, heat, physical bodies and cost, while a premium-only inventory prevented cheaper comparisons. Splitting resistors concealed rather than reduced total loss.

What could have helped: Read efficiency, octave loss, compensation, ablation, physical part count and cost during design; stock multiple price classes and makers. Compare cheaper parts with their actual parasitics and ratings, and distinguish attenuation, diverted current, per-body heat and total cabinet heat.

Incorporation: **confirmed**. Framework locations: skills/speaker-designer/SKILL.md crossover audit; skills/speaker-evaluator/SKILL.md; templates/evaluation.md; references/crossover-design.md §§8,13; simulations/_common/networks.py.

Verification: Retained existing loss/parts/ablation behavior and verified test_network_efficiency_and_parts.py and test_fit_ablation_and_stock.py. Removed mandatory-compensation contradiction in reference, evaluator and result note; differentiated real power from current magnitude.

#### pad-dissipation-and-fragile-integration-are-warning-signs

What went wrong: Nominal curves hid deep pads, resonant voltage gain and phase-sensitive integration. Banks were mistaken for heat reduction, mounting ratings for enclosed endurance, and group stress for individual-part stress.

What could have helped: Check filter and pad voltages, per-leaf power conservation and frequency-coincident total heat at equal drive; compare measured-uncertainty and deliberate-probe phase scenarios on and off axis, including common and relative shifts. Test overlap/order changes against the mechanism and realize every bank explicitly before sizing or documenting it.

Incorporation: **confirmed**. Framework locations: skills/speaker-designer/SKILL.md, Source and crossover audits; templates/evaluation.md; references/crossover-design.md §13.

Verification: test_network_leaf_stress.py, test_network_efficiency_and_parts.py and test_whole_speaker_depth_perturbation.py pass. Reviewed per-leaf versus coincident total heat, filter voltage gain, mounting/rating limits and common/relative on/off-axis phase scenarios.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G5 Interpretation and robustness

### Current framework review

Skills: evaluator bass/robustness and designer depth studies. References: target-response, system-architecture. Simulations: whole_speaker section curves, lf_uncertainty summaries, response_metrics.

### Implemented plan

Section phase and perturbations exist. Uncertainty summaries omit unresolved cutoffs and include censored values without distinguishing them; the evaluation template uses box f6 for a system objective. Add explicit total/resolved/censored/no-pass counts and conditional percentiles, tests including all-unresolved draws, and workflow/template fields for fixed-frequency levels, threshold margins, coherent attribution and controlled voicing studies.

### Learning coverage

#### keep-system-and-box-cutoffs-separate

What went wrong: Box and system cutoffs, thresholds and reference bands were mixed; tiny level changes near a plateau or trough produced large apparent extension changes without comparable bass-output changes.

What could have helped: State scope, reference band and threshold with every cutoff, inspect bounds and curves, and quote absolute levels at fixed bass frequencies plus threshold margins. Treat differences within uncertainty as unresolved rather than robust improvements.

Incorporation: **confirmed**. Framework locations: templates/evaluation.md; references/target-response.md §§5,10; skills/speaker-evaluator/SKILL.md; skills/speaker-documentation/SKILL.md.

Verification: System-objective template now cites whole_speaker low_cutoffs, with threshold/reference/bound and absolute-bass fields. Existing response/statistics tests pass; reviewed plateau interpretation and label consistency.

#### build-a-voicing-study-when-two-objectives-trade

What went wrong: Single fits were taken as evidence that joint targets were impossible, cutoff jumps were mistaken for added bass, and unresolved cutoff draws disappeared from robustness summaries.

What could have helped: Sweep a few controlled voicings of the same hardware, recording sensitivity, fixed-frequency bass, heat, reference level and trough margin. Count unresolved outcomes explicitly in all scenario totals and target assessments; label resolved-only percentiles as conditional. Keep voicings within the candidate and identify the selected one.

Incorporation: **confirmed**. Framework locations: simulations/lf_uncertainty/run.py summarize_samples; templates/feasibility.md; skills/speaker-designer/SKILL.md; skills/speaker-evaluator/SKILL.md.

Verification: test_uncertainty_outcomes.py checks mixed and entirely unresolved cutoffs with explicit denominator and conditional percentiles. Reviewed fixed-hardware voicings, selected-point identity, trough margin and all-scenario joint-target accounting.

#### check-a-default-perturbation-against-the-thing-it-perturbs

What went wrong: A default depth shift larger than plausible physical uncertainty dominated reported fragility and obscured meaningful candidate differences.

What could have helped: Justify perturbations from acoustic-center uncertainty rather than treating a default or physical depth as a tolerance; report smaller plausible scenarios and larger sensitivity probes separately, with section and common/relative scope.

Incorporation: **confirmed**. Framework locations: references/measurement-and-model-limits.md §8; skills/speaker-designer/SKILL.md; templates/evaluation.md; simulations/lf_uncertainty/README.md.

Verification: Reviewed physical uncertainty versus probe language and section/common/relative scope; test_whole_speaker_depth_perturbation.py passes. Corrected stale uncertainty defaults table to the actual app values.

#### read-the-section-curves-before-blaming-a-driver

What went wrong: A summed hump and dip caused by residual woofer leakage and relative phase were attributed to the tweeter’s own response, prompting the wrong replacement proposal.

What could have helped: Read every contributing section’s complex pressure and relative phase at the feature, reconstruct the coherent sum and inspect depth sensitivity before attributing the defect or requesting a new driver.

Incorporation: **confirmed**. Framework locations: skills/speaker-evaluator/SKILL.md, Interpret before attributing; references/target-response.md §10; templates/evaluation.md.

Verification: Reviewed coherent complex-pressure attribution equation and phase/depth checks before replacement requests. Existing whole-speaker summation and depth tests pass; the new cone/outlet integration test also verifies complex summation.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G6 Physical geometry and construction

### Current framework review

Skills: designer cabinet and documentation construction. References: cabinet-geometry. Tools/simulations: cabinet_drawing, lf_box, cavity_modes, plate_structure.

### Implemented plan

Drawing and volume tools exist but cannot establish shaped-part interference. Keep that judgment explicit; add an early geometry audit template and practice for datums, static/moving bounds, union volumes, joints and installation reserves, and require alignment/full-chain replay after volume changes. Correct stale model descriptions rather than pretending bounding boxes establish buildability.

### Learning coverage

#### include-hardware-in-cabinet-envelope

What went wrong: Late drawings exposed brace, basket, horn, duct and board clashes, incorrect volume deductions and inconsistent depth datums. Wood size omitted projecting or moving hardware; nominal overlaps hid missing joints and installation clearance.

What could have helped: Draw front, rear and side sections when the driver set is chosen. Track wood, static and moving envelopes; flange, recess, cutout, physical and acoustic depth; internal duct length versus acoustic path; and solid-union displacement with explicit joints. Include wires, supports, fasteners, access and service spaces, inspect source drawings and clearances, then replay alignment and the fixed network after net-air changes.

Incorporation: **confirmed**. Framework locations: templates/geometry-audit.md; references/cabinet-geometry.md, Installation datums and early geometry review; skills/speaker-designer/SKILL.md §3; skills/speaker-documentation/SKILL.md.

Verification: Reviewed all original geometry mechanisms: early three views, datum and view direction, hardware/motion/access, internal/acoustic duct length, union volumes/joints, individual fasteners, installed reserves and downstream replay. Cabinet tools remain explicit about their lack of interference solving; existing geometry/tool smoke tests pass.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## G7 Selection, delivery and learning lifecycle

### Current framework review

Skills: design selection/corrections, evaluator ranking, documentation, learnings. References: measurement-and-model-limits and crossover-design. Tools/simulations: schematic, board_nodal, build_pdf; tests: schematic_netlist_ids, learnings.

### Implemented plan

Physical-leaf generation exists, but ranking and finishing do not explicitly prioritize central objectives and the learning format appends project narratives indefinitely. Add central-objective and correction accounting, defer detailed finishing when appropriate, reconcile frozen parameters with all artifacts, state prototype measurement work, adopt two-section consolidated learnings, and support an empty active index after verified incorporation.

### Learning coverage

#### a-central-objective-miss-outweighs-smoothness

What went wrong: Ranking secondary smoothness and sensitivity above a large central bass miss produced a polished package for a design that did not meet the brief.

What could have helped: Identify the brief’s central objectives before ranking, state when no candidate meets them, and distinguish closest prototype from compliant design. Use remaining exploration on the central miss and present quantified options when exhausted.

Incorporation: **confirmed**. Framework locations: templates/project.json objective_review.central_objectives; templates/evaluation.md; skills/speaker-evaluator/SKILL.md, Decide and request; skills/speaker-design/SKILL.md §5.

Verification: Reviewed central-first ranking, explicit no-candidate-meets outcome and prototype versus compliant-design wording. No scoring threshold is imposed by simulation code.

#### defer-detailed-engineering-until-the-concept-approaches-targets

What went wrong: Detailed boards, cavity/panel work and final drawings consumed effort after a decisive acoustic miss was already known.

What could have helped: Perform early mechanical feasibility checks, but reserve detailed finishing for a concept approaching central targets. If none does, use remaining budget for alternatives and deliver the unmet-objective study and options, unless the user explicitly wants construction details anyway.

Incorporation: **confirmed**. Framework locations: skills/speaker-design/SKILL.md §5; skills/speaker-evaluator/SKILL.md, Decide and request; templates/evaluation.md.

Verification: Reviewed distinction between early physical feasibility and detailed finishing, use of remaining exploration and concise unmet-objective report, preserving an explicit request for full prototype documentation.

#### generate-the-documents-from-the-parameter-files

What went wrong: Late stock substitutions and resistor banks were edited only in prose, leaving schematic, wiring, simulated response and parts list inconsistent.

What could have helped: Define every physical leaf and bank in the frozen parameter files, regenerate simulations, schematic, netlist and connection table after changes, and reconcile the parts list and stressed positions against that same realization.

Incorporation: **confirmed**. Framework locations: skills/speaker-documentation/SKILL.md, Freeze the realization before writing; templates/candidate.json crossover.parameter_file.

Verification: Reviewed parameter-first late edits and artifact reconciliation. Existing test_schematic_netlist_ids.py, test_network_leaf_stress.py and board tests pass, covering physical leaf IDs and realized connections.

#### measured-complex-responses-before-build-ready-crossovers

What went wrong: Detailed build instructions made a crossover fitted to magnitude-only priors and different test hardware appear final despite unmeasured installed phase.

What could have helped: Declare source provenance and unresolved integration assumptions, label values as prototype starting points, and include mounted-driver magnitude, phase and impedance measurement and refit steps before quantity purchasing.

Incorporation: **confirmed**. Framework locations: skills/speaker-documentation/SKILL.md, Freeze the realization before writing; references/measurement-and-model-limits.md §§7,8.

Verification: Reviewed explicit prototype status and mounted-driver magnitude/phase/impedance/tuning/refit sequence before quantity purchasing, with reconstructed phase and different test hardware disclosed.

#### validation-reruns-are-not-design-iterations

What went wrong: Correction reruns preserved the iteration counter while invalid feedback had consumed real exploration; uniform corrections and design-changing corrections were not distinguished.

What could have helped: Log corrections separately with affected candidates and ranking impact, retain corrected historical results and separate new exploration from validation. Continue within authorized limits and ask about budget only when restoring invalidated exploration would require changing those limits.

Incorporation: **confirmed**. Framework locations: skills/speaker-design/SKILL.md §4; templates/project.json corrections; templates/simulation-audit.md; skills/speaker-learnings/SKILL.md retirement workflow.

Verification: Reviewed separate correction accounting, affected candidates and ranking impact, uniform versus exploration-invalidating corrections, and authorized budget limits. Learning format tests passed with all 28 consolidated records before retirement.

Group verification: **complete**. All learning entries in this group name their implementation and completed checks. The full suite passed 142 tests, including all 25 simulation example runs. Workflow-only changes were reviewed against each consolidated failure; numerical behavior is covered by the named regression suites.

## Source evidence retained from the consolidated records

The following paths are historical project evidence, not dependencies of the framework or builder-facing output. Projects remain ignored by Git.

### whole-speaker-output-is-already-one-metre-equivalent

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 4
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Reference comparison and lineage" (c06 to c07 sensitivity 86.6 to 95.3 dB after the correction)
- `framework/simulations/whole_speaker/README.md`, "Output"

### do-not-double-count-woofer-rolloff

project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-r3, forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 5
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, first correction
- `framework/simulations/source_response/README.md`, acoustic kind `lf_box`
- `framework/projects/forte-iii-performance-20260914/reference/simulation-audit.md`
- `framework/projects/forte-iii-performance-20260914/tools/hybrid_source.py`
- `framework/projects/forte-iii-performance-20260914/reference/audit/actual_c01_unity_hybrid.json`
- `framework/projects/forte-iii-r3/inventory/woofers/beyma_12lx60v2_8.json` and `bc_15ps100_8.json`, digitized curves with their anchors
- `framework/projects/forte-iii-r3/postmortem.md`, "What went right", items 4 and 5

### check-upper-driver-graph-calibration

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, last paragraph
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"

### put-the-series-resistance-in-one-place

project: neat-petite-amt

- `framework/projects/neat-petite-amt/candidates/c07/notes.md`, section 2
- `framework/projects/neat-petite-amt/candidates/c07/sim/ws_lf_unity_r003.json` against `ws_lf_unity.json`
- `framework/simulations/_common/acoustics.py`, `box_response`, the `z_ohm` line
- `framework/projects/neat-petite-amt/project.json`, log entry CORRECTION dated 2026-09-18

### decide-the-woofer-level-basis-in-the-screen

project: neat-petite-amt

- `framework/projects/neat-petite-amt/inventory/screen.md`
- `framework/projects/neat-petite-amt/evaluations/iteration-1.md`, the c01 basis finding, and `iteration-2.md`, the basis decision
- `framework/projects/neat-petite-amt/candidates/c08/sim/derive_datasheet_basis.py`

### reference-sensitivity-conventions-differ

project: forte-iii-three-way, neat-petite-amt

- `framework/projects/forte-iii-three-way/README.md`, last paragraph
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, objective scoring rows for sensitivity
- `framework/projects/neat-petite-amt/reference/reference.json`, `published.sensitivity_db_2v83_1m` and `digitized_curves.on_axis_spl`; `project.json` log entry on the status check

### validate-simulation-chain-before-iteration-one

project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915, neat-petite-amt

- `framework/projects/forte-iii-three-way/postmortem.md`, reasons 3 to 6
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`
- `framework/tests/test_radiation_invariants.py` (regression test added after the rear-outlet fix)
- `framework/projects/forte-iii-performance-20260914/reference/simulation-audit.md`
- `framework/projects/forte-iii-performance-20260914/evaluations/c08-dependency-verification.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-pair-source-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
- `framework/projects/neat-petite-amt/reference/validation/` and `tools/compare_validation.py`

### a-failed-run-must-not-read-the-previous-result

project: forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-one-woofer-20260915/tools/lf_section.py`, the `run` helper
- `framework/projects/forte-iii-one-woofer-20260915/postmortem.md`, "What went wrong", item 4
- `framework/tests/test_crossover_fit_budget.py`, the application defect that exposed it

### screen-bass-feasibility-before-broad-upper-inventory

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/postmortem.md`, reasons 2 and 7
- `framework/projects/forte-iii-three-way/inventory/screen.md`

### establish-the-bass-envelope-before-system-sensitivity

project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-pr-20260914

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 2 and "Changes required"
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Reference comparison and lineage" (c04 to c08)
- `framework/projects/forte-iii-performance-20260914/inventory/bass-screen.md`
- `framework/projects/forte-iii-performance-20260914/evaluations/iteration-3.md`
- `framework/projects/forte-iii-performance-20260914/final/03-simulated-performance.md`
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`

### price-the-removed-output-before-designing

project: forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-one-woofer-20260915/inventory/single-woofer-screen.md`
- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-3.md`, selection statement
- `framework/projects/forte-iii-one-woofer-20260915/postmortem.md`, outcome table

### set-the-fit-target-from-the-woofer-not-the-optimizer

project: forte-iii-r3, forte-iii-single-pr-20260914

- `framework/projects/forte-iii-r3/project.json`, the log entry diagnosing 2 to 6.6 dB of avoidable insertion loss
- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, sensitivity and impedance before and after
- `framework/projects/forte-iii-r3/postmortem.md`, reasons 3 and 4
- `framework/projects/forte-iii-single-pr-20260914/candidates/c04/sim/crossover_network.params.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c07/sim/crossover_network.params.json`
- `framework/projects/forte-iii-single-pr-20260914/inventory/stock/mundorf_vs180_*.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, incomplete low-loss refinement
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/whole-tolerance-summary.json`

### check-source-spacing-before-a-directivity-objective

project: forte-iii-r3, neat-petite-amt

- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, the seating-window column across nine candidates
- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, "Why the seating window is missed"
- `framework/projects/forte-iii-r3/postmortem.md`, reason 1
- `framework/projects/neat-petite-amt/candidates/c05/notes.md`, section 5, and `evaluations/iteration-2.md`, lineage

### bound-the-fit-to-values-you-can-buy

project: forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-2.md` and `iteration-3.md`
- `framework/projects/forte-iii-one-woofer-20260915/candidates/c04/summary.json`, `c07/summary.json`, `fit_statistics.values_at_bound`
- `framework/projects/forte-iii-one-woofer-20260915/candidates/c10/voicing/90.5-buildable/summary.json`

### coil-dcr-is-a-lever-on-the-impedance-minimum

project: neat-petite-amt

- `framework/projects/neat-petite-amt/candidates/c07/candidate.json`, `crossover.dcr_voicing_table`
- `framework/projects/neat-petite-amt/candidates/c07/sim/crossover_network_dcr013.json`, `_dcr024.json`, and the parent `c05/sim/crossover_network.json`
- `framework/projects/neat-petite-amt/evaluations/iteration-2.md`, request R1, and `iteration-3.md`, the DCR table

### a-pad-body-is-a-level-step

project: neat-petite-amt

- `framework/projects/neat-petite-amt/candidates/STUDY-BRIEF-BIGGER-WOOFER.md`, the pad table
- `framework/projects/neat-petite-amt/evaluations/study-bigger-woofer-1.md` and `study-bigger-woofer-2.md`
- `framework/projects/neat-petite-amt/candidates/c13/candidate.json` (two bodies) and `c12/candidate.json` (none)
- `framework/projects/neat-petite-amt/postmortem.md`, the study addendum

### the-crossover-is-a-bill-of-materials

project: forte-iv-single-pr, neat-petite-amt

- `framework/projects/forte-iv-single-pr/final/02-crossover-construction.md`, the parts list, the
  cost subtotal and the resistor stress table
- `framework/projects/forte-iv-single-pr/candidates/c08/sim/physical_network.json`, `results.efficiency`,
  `results.parts`, `results.sections[].compensation_audit`, `results.sections[].insertion_loss`
- `framework/projects/forte-iv-single-pr/evaluations/iteration-1.md`, the request to redesign the loss
  distribution rather than multiply the resistor count
- `framework/projects/forte-iv-single-pr/final/04-reference-comparison.md`, the reference product's
  measured impedance minimum against this project's objective
- `framework/projects/forte-iv-single-pr/inventory/stock/`, 87 records from one manufacturer
- `framework/references/crossover-design.md` sections 7 and 8, and
  `framework/references/target-response.md` section 9
- `framework/projects/neat-petite-amt/inventory/stock/README.md`, `candidates/c09/notes.md` (the premium-part check) and `candidates/c07/candidate.json` `final`

### pad-dissipation-and-fragile-integration-are-warning-signs

project: forte-iv-single-pr, forte-iii-three-way, forte-iii-performance-20260914, forte-iii-r3, forte-iii-pr-20260914, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 4
- `framework/projects/forte-iii-performance-20260914/evaluations/final-audit.md`
- `framework/projects/forte-iii-performance-20260914/final/02-crossover-construction.md`
- `framework/projects/forte-iii-r3/final/02-crossover-construction.md`, the resistor array table
- `framework/projects/forte-iii-r3/postmortem.md`, reason 7
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/depth-directivity-summary.json`
- `framework/projects/forte-iv-single-pr/evaluations/leaf-stress-correction.md` and its postmortem, the misattributed group stress
- `framework/tests/test_network_leaf_stress.py`, the per-leaf distribution and the power-conservation check

### keep-system-and-box-cutoffs-separate

project: forte-iii-three-way, forte-iii-r3, forte-iii-one-woofer-20260915, neat-petite-amt

- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Bass and output interpretation"
- `framework/projects/forte-iii-three-way/postmortem.md`, "Changes required"
- `framework/simulations/lf_box/README.md` and `framework/simulations/whole_speaker/README.md`, statistics sections
- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, the voicing table and the cutoff warning
- `framework/projects/forte-iii-r3/postmortem.md`, "Outcome"
- `framework/projects/neat-petite-amt/candidates/c07/candidate.json`, `final`, and `postmortem.md` item 7

### build-a-voicing-study-when-two-objectives-trade

project: forte-iv-single-pr, forte-iii-r3, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, the candidate table and the closing paragraph
- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, the c07 and c08 voicing rows
- `framework/projects/forte-iii-r3/postmortem.md`, "What went right", item 6
- `framework/projects/forte-iii-single-pr-20260914/candidates/c08/voicing-study/summary.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/selected-voicing.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, cutoff trade and outcome
- `framework/projects/forte-iv-single-pr/evaluations/iteration-2.md` and `final-tolerance-evidence.json`, the 0.035 dB margin and the 19-of-24 scenario count

### check-a-default-perturbation-against-the-thing-it-perturbs

project: forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-one-woofer-20260915/candidates/c10/final/detail/detail-report.json`
- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-1.md`, fragility paragraph
- `framework/projects/forte-iii-one-woofer-20260915/final/03-simulated-performance.md`, depth table

### read-the-section-curves-before-blaming-a-driver

project: neat-petite-amt

- `framework/projects/neat-petite-amt/evaluations/iteration-2.md`, "key independent finding"
- `framework/projects/neat-petite-amt/candidates/c04/sim/whole_speaker.json`, `results.on_axis.sections`
- `framework/projects/neat-petite-amt/candidates/c08/sim/whole_speaker_3rd.json`, the third-order variant that removed the pair

### include-hardware-in-cabinet-envelope

project: forte-iii-performance-20260914, forte-iii-pr-20260914, forte-iii-r3, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915

- `framework/projects/forte-iii-performance-20260914/final/01-cabinet-construction.md`
- `framework/projects/forte-iii-performance-20260914/final/cabinet-drawings/geometry-audit.json`
- `framework/projects/forte-iii-performance-20260914/candidates/c08/volume-accounting.json`
- `framework/projects/forte-iii-performance-20260914/project.json`, geometry correction log
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-r3/final/cabinet_drawing.png` and `final/01-cabinet-construction.md`
- `framework/projects/forte-iii-r3/postmortem.md`, reason 2
- `framework/projects/forte-iii-single-pr-20260914/candidates/c08/detailed/solid-volume-budget.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/geometry-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, physical realization corrections
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/mechanical-layout.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-geometry-review.json`

### a-central-objective-miss-outweighs-smoothness

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 1
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, opening paragraph and objective scoring

### defer-detailed-engineering-until-the-concept-approaches-targets

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 8 and "Changes required"

### generate-the-documents-from-the-parameter-files

project: forte-iii-r3

- `framework/projects/forte-iii-r3/final/crossover_connections.md` and `final/02-crossover-construction.md`
- `framework/projects/forte-iii-r3/tools/rate_resistors.py`
- `framework/projects/forte-iii-r3/postmortem.md`, reason 7

### measured-complex-responses-before-build-ready-crossovers

project: forte-iii-three-way

- `framework/projects/forte-iii-three-way/postmortem.md`, "Would better simulation have helped?"
- `framework/projects/forte-iii-three-way/reference/prototype-measurement-plan.md`
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Integration, heat and risk"

### validation-reruns-are-not-design-iterations

project: forte-iii-three-way, neat-petite-amt

- `framework/projects/forte-iii-three-way/postmortem.md`, reason 6
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, last paragraph
- `framework/projects/neat-petite-amt/project.json`, log entry CORRECTION dated 2026-09-18, and `postmortem.md` item 1

## Verification and retirement record

On 2026-09-28, reviewed all 28 combined learning statements against the specific implementation and verification above. Every learning has been acted upon through code, workflow, reference or template changes, and existing applicable numerical fixes were regression-tested. This confirms incorporation; it does not claim future designs cannot repeat errors or that simulations have been validated against measurements.

New numerical behavior: explicit LF drive basis and acoustic calibration, coherent calibrated outlet support, stale-result invalidation and checked no-cache execution, and explicit unresolved/censored cutoff accounting. Existing source-shape, radiation, stock/ablation, component-power, depth, netlist and board checks remain passing.

Compatibility: source-voltage LF behavior and published-shape multiplication remain available for old inputs; new workflow uses driver-terminal normalization and replacement when appropriate. Terminal normalization rejects a prefiltered LF source to avoid repeating a transfer. Acoustic calibration changes pressure only. Cutoff percentiles now exclude censored observations as well as no-pass observations, label that conditional basis, and retain all outcome counts. Inputs and result paths must differ.

Learning lifecycle: active files now use two combined sections; an empty active INDEX is valid. Future incorporation records verification before removing a file. Project postmortems remain uncommitted.

Retirement completed: 28 of 28 active learning files removed after their confirmations were recorded; README and INDEX retained. No project files were staged.

Post-retirement checks: learning/reference tests **6 passed** with an empty active directory; all JSON templates parsed; no operational skill/reference/app README refers to a retired learning slug; `git diff --check` clean. Final source and template edits after the full suite were documentation/metadata only.
