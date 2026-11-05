# Woofer load models and crossover validation

Status: implemented. The user-authorized implementation treats all application/tool diagnostics as data for the calling agent. Numerical tests verify code behavior; applications do not impose evidence qualification, fit-quality verdicts or design acceptance rules.

## Purpose

Prevent a passive crossover from being selected because an inadequately specified driver impedance creates an unrealistically useful response feature. Improve source preparation, model propagation, optimization, numerical validation and agent decisions. Do not implement this by adding disclaimers, measurement-confirmation boilerplate, or weaker claims to builder documents.

## Failure mechanism and scope

A passive network's transfer depends on the driver's complex impedance. An inadequately supported constant-inductance load can create an apparent recovery, shelf or other useful feature that changes substantially under a supported lossy load. An optimizer can exploit that feature even when the network solver is numerically correct.

Separate solver correctness from load adequacy: compare independent circuit solutions for the same explicit load, then hold the crossover fixed while varying the supported load models. A transfer discrepancy alone does not uniquely identify the driver's impedance. Keep acquisition details, original captures, supersession records and case-specific numerical comparisons in their project records.

The implementation applies to every driver-load consumer, including woofer, midrange and high-frequency branches, imported complex curves, analytical loads and fitted models. No project identity, driver SKU, crossover topology, component value or handover frequency may determine application behavior.

## General implementation architecture

1. **Shared load contract.** Define a versioned electrical-load record with model kind and parameters or complex-curve reference, units, stable source identity, evidence references, supported frequency band, phase basis and declared alternatives. Distinguish blocked electrical impedance from complete terminal impedance, including mechanical/enclosure loading. Keep electrical support separate from acoustic support. Extend the existing source contract rather than creating competing metadata in each app.
2. **One resolution path.** Resolve inline models and referenced curves through shared code used by source preparation, ladder and nodal networks, fitters and scenario chains. Return complex impedance together with its contract and transformation history. Preserve identity through serialization and explicit overrides; check requested frequency coverage and make extrapolation explicit. Do not silently supply zero phase or replace missing model metadata with a broadband support claim.
3. **Reuse existing physics and fitting.** Build on `_common/driver_models.py`, `parameter_identification` and `system_scenarios`. Constant, Leach, LR2 and semi-inductance laws already exist. Extend their contracts and diagnostics where needed; do not replace one universal default with another. A supported imported complex curve need not be forced through a parametric fit.
4. **Separate compatibility from evidence.** Preserve legacy numerical replay and bass-only calculations with their original assumptions recorded. Missing evidence remains missing. Source preparation reports supplied and missing metadata, phase assumptions and frequency coverage without raising evidence-validation errors; solvers return those facts for the agent to interpret. The agent evaluates adequacy against the project's objectives.
5. **Shared scenario evaluation.** Give both fitters the same declared load-alternative interface and per-scenario metrics. Keep model alternatives separate from production tolerance draws, with no inferred probabilities. Any worst-case objective, scenario weights or numerical constraints must be explicit caller inputs. Recompute dependent acoustic and electrical results consistently when a changed physical parameter affects both; identify electrical-only sensitivity probes as such.
6. **General regression suite.** Cover different driver classes, load representations, circuit topologies and frequency ranges. Include both a case where supported load alternatives change the preferred circuit and one where the original circuit remains suitable. Set solver tolerances from numerical accuracy and design error budgets from supplied objectives, never from a single case's observed attenuation.

## Implementation sequence

1. Preserve minimal failure-mechanism fixtures and explicit acceptance metrics before changing code. Include an explicit constant-inductance load, an independently solved network, a controlled transfer comparison and a physically supported lossy-load example. Keep full project recordings out of source control; add only appropriately scoped numerical fixtures needed for regressions, retaining their actual provenance.
2. Audit every consumer of the driver impedance. Distinguish bass-alignment use from crossover-band use. Expose each crossover source's electrical model, stated frequency band, parameter/source basis and reference identity. Preserve missing fields as unknown. Report a single datasheet `le_mh` as a constant-inductance assumption without implying broadband evidence. Keep constant inductance available for explicitly justified cases and analytical tests.
3. When a parametric model is needed, route source preparation through the existing `parameter_identification` models: constant, Leach, LR2 or semi-inductance, selected from the available electrical data and behavior. Prefer complex impedance with magnitude and phase; preserve supported imported curves directly when appropriate. Where data do not uniquely determine parameters, preserve the admissible family and resolve materially different crossover outcomes through additional source research or a circuit insensitive to that ambiguity. Do not install a fixed fractional exponent as a universal replacement default.
4. Propagate the selected electrical model and its identity through `lf_box`, `source_response`, `crossover_network`, `board_nodal`, `crossover_fit`, `network_fit`, `whole_speaker` and applicable scenario chains. Replaying a downstream source must not silently restore an ideal-inductance default. Apply acoustic fixture/baffle corrections and electrical losses exactly once.
5. Include supported driver-load parameter and model variations in crossover fitting and ranking, separately from capacitor/coil production tolerances. Report nominal and alternate branch transfers, acoustic overlap, summed response, impedance, phase, leakage and component stress. The agent interprets whether load sensitivity changes the merits of a circuit against the brief. Apps report quantities; selection remains the agent's engineering judgment.
6. Add a source-comparison/fit audit that records frequency-band residuals, parameter bounds, identifiability, held-out-frequency performance and the effect of the residual on crossover behavior. Let the agent supply any numerical error budget from the project's acoustic objectives; retain it as context without enforcing an acceptance threshold. A good scalar fit score must not hide an error concentrated in the handover region.
7. Update skill routing at the affected decisions, then run behavioral reviews across the regression cases. Reviews must change decisions when the evidence warrants a change and retain supported decisions in insensitive cases; wording changes alone do not complete this work.

## Intended files and responsibilities

- `simulations/_common/driver_models.py`: explicit model selection and preservation; retain correct analytical behavior.
- Shared source/load resolution and contract code, including `_common/acoustics.py`, `_common/networks.py` and the `board_nodal` load boundary: consistent metadata, coverage, override and replay handling.
- `simulations/parameter_identification/`: model fitting and residual/identifiability diagnostics; extend only where the reproduction exposes a concrete gap.
- `simulations/source_response/`, `crossover_fit/`, `network_fit/`, `system_scenarios/`: complete load propagation and scenario-aware fitting/evidence.
- `skills/speaker-designer/SKILL.md`: establish the supported broadband electrical load before fitting; inspect controlled model alternatives when they affect the chosen network.
- `skills/speaker-evaluator/SKILL.md`: compare branch transfers, available acoustic overlap and load sensitivity before ranking or release.
- `skills/speaker-design/SKILL.md` and `templates/simulation-audit.md`: guide interpretation of source/load evidence and replay during selection.
- `skills/speaker-documentation/SKILL.md`: consume the agent-selected realization and provide definite construction instructions. Add no disclaimer-based escape route.
- Relevant engineering references: explain the impedance mechanism with primary sources. Keep project-specific numbers in the reproduction and project record.

## Numerical and behavioral verification

- Independent RLC voltage-divider and nodal results agree for the same explicit complex load.
- Fractional and rational lossy models agree with independent evaluations of the documented equations, including phase and limiting cases. Negative real impedance is reported as a quantity, not a passivity-validation error. Existing published-source references remain the engineering basis.
- Fitted models are evaluated at frequencies excluded from fitting; tests distinguish interpolation from identification.
- Round-trip/replay tests preserve the same complex impedance across every consumer and serialization boundary.
- A source derived solely from a datasheet inductance value reports that assumption, with absent support and provenance left unknown.
- Imported curves, fitted models and explicit analytical loads preserve their support bands and phase basis; missing phase and out-of-band requests are handled explicitly.
- Multiple driver classes and ladder/nodal topologies exercise the same contracts without project-specific branches or constants.
- A candidate whose apparent advantage disappears under supported load alternatives is not selected solely by its nominal score.
- Existing constant-load analytical cases and legitimate bass-only workflows continue working.
- A fresh review can diagnose the reproduction from source data and computed outputs without being told the desired answer.

## Completion criteria

The regression cases are resolved through supported model preparation/selection and robust crossover evaluation; numerical and behavioral checks pass across different drivers and networks; the altered application contracts and skills agree; a cold replay retains each selected load through the full chain. Builder-facing deliverables continue to contain engineering results and definite instructions, without simulation-status caveats or requests to confirm an otherwise unsupported design.

## Implementation record

- Shared resolver and versioned evidence: `simulations/_common/electrical_load.py`; integrated source, LF, cavity, enclosure, distributed, ladder/nodal, electrothermal, fitter and whole-speaker boundaries. Schematic netlists retain custom impedance paths and metadata.
- Both fitters accept declared `load_scenarios` and caller-selected objective aggregation. Full scenario curves and stress remain available; production tolerances retain their separate interface.
- Identification adds held-out frequencies/observations, band residuals, parameter alternatives and observed-versus-fitted circuit effects. Mechanical-scale ambiguity, absent phase and absent calibration provenance are observations rather than evidence-validation failures.
- `system_scenarios` retains per-step load evidence after temporary files disappear and optionally retains complete results.
- Contracts and interpretation guidance: `simulations/electrical-loads.md`, affected app READMEs, design/designer/evaluator/documentation skills, simulation-audit template and impedance reference.
- Regression coverage: `tests/test_electrical_load_contract.py`, existing impedance, identification, source-basis, fit, replay and simulation tests. Fixtures use synthetic primitive equations and unrelated load/circuit values; no project recordings or project-specific conditions were added.

Behavioral interpretation: the controlled divider cases make a nominally suitable resistance less attractive when the declared alternate load is included in the objective. Both fitters expose that change and the per-case circuit consequences. An identical alternate load leaves the preference unchanged. The agent can therefore retain an insensitive choice or reconsider a load-sensitive one using the returned data; neither app makes that engineering decision. Held-out contamination remains visible without shifting parameters fitted to the other samples. This distinguishes a useful diagnostic from an automatic validation gate.

Verification: `.speaker-venv/bin/python -m pytest framework/tests -q` completed with **321 passed**. The suite regenerates the standalone example chain. `git diff --check` reported no whitespace errors.
