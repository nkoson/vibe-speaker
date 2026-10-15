# Turn the brief into discriminating simulations

Use when the brief includes qualitative sound, room use or an unfamiliar architecture. The goal is a speaker that meets the user's intent, not the highest composite score available from the apps.

## Separate intent, constraints and proxies

Record the user's words and priorities. Distinguish actual hard constraints (cabinet envelope, component budget, passive-only, load or protection condition) from preferences and designer diagnostics. Translate each preference into a testable hypothesis with an observable and a controlled design variable. If several interpretations remain plausible, compare them before asking a question that research could settle.

| Brief language | Useful simulation questions | Avoid treating as equivalent |
|---|---|---|
| Deep, substantial bass | Equal-voltage LF output, sustained cutoff, displacement/outlet limits, room/placement cases | A low threshold crossing caused by a hump, or a low `fs` alone |
| Dynamic, effortless | Supported output across bands, current/excursion/heat, compression scenarios and sensitivity/load trade | Moving mass or `Bl/Mms` as a sound-quality score |
| Coherent, natural | Branch magnitude/phase over overlap, directivity continuity, seat response, absence of broad contour discontinuities | Zero phase at one crossing or minimum electrical part count |
| Detailed without fatigue | Whole-band contour, top octave, local peaks/decay hypotheses, leakage and angular behavior | A preferred diaphragm material or capacitor brand |
| Wide listening area | Individual seat curves, spatial mean/spread, horizontal and vertical behavior, position dependence | Flat on axis or a nominal horn coverage number |
| Works near a wall | Outlet clearance, boundary interference, equal-voltage LF balance and multiple plausible rooms | Copying a free-field baffle-step shelf unchanged |
| Reference speaker character | Comparable-condition response shape, level, directivity, extension and trade table | Matching a smoothed room curve as an anechoic target |
| Simple to build | Purchasable stock, actual part bodies, machining/joint sequence, visible wiring, tolerance | A low symbol count with impractical banks or custom machining |

These are hypotheses to adapt, not default targets or pass/fail thresholds. Keep subjective attributes without an established model as interpretations, and make the concrete choice using the observables the model does support.

## Choose the architecture before optimizing values

Write a short capability map for each plausible architecture: source bands and protection, radiating geometry, loading and amplifier connection, then which app predicts each coupling. An MTM-shaped 2.5-way is not a same-band MTM; a coaxial can retain acoustic delay; a full-range driver can need equalization; a hybrid dipole needs signed rear radiation. A geometry-only loading calculator does not become a complete speaker response because it returns a plausible dimension.

Where the existing models are incomplete, use sourced reduced models and sensitivity scenarios with explicit boundaries, or improve the relevant solver during authorized framework work. Avoid interpreting the absence of a modeling feature as proof that an architecture cannot meet the brief.

## Own the selection under uncertainty

For each important unknown, state its origin, plausible range/scenarios and which objective it affects. Distinguish component production tolerances from uncertain source/fixture/phase/material models. Run central and adverse combinations; use probabilities only when their distributions are supported. A fraction of equally weighted scenarios is not a production yield estimate.

Choose the next experiment by whether it could change the ranking or close a central miss. Hold unrelated variables fixed, collect before/after evidence and check the whole response family. Prefer a design that retains its advantage across plausible conditions over a fragile nominal optimum. When there is a real trade, present the alternatives and make a recommendation in the user's priority order. Final stock and geometry choices belong to the agent; a simulation-based project need not defer them to the builder.

Use [crossover search](../../speaker-designer/references/crossover-search.md) for search mechanics, [simulation integrity](simulation-integrity.md) for source/baseline consistency, and `framework/references/room-simulation.md` for virtual listening-position studies. Stop within the agreed iteration budget with an honest selection and any residual objective misses.

## Persist the observation contract

The project template includes `priority`, `conditions` (band, curve, drive, distance, environment and units), `result_reference` and an `assumptions` ledger. A result reference names `file`, `path` and optional reduction. `framework/tools/collect_objectives.py --input project.json --out objective-observations.json` collects values and signed target differences without declaring acceptance. Record each assumption's parameter paths, source/basis, range or model alternatives and the objectives affected. Use those same paths in `system_scenarios` so the uncertainty study and the brief remain connected.
