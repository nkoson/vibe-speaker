# system_scenarios: Correlated whole-chain scenarios

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py system_scenarios --input framework/simulations/system_scenarios/example.json --out results --name system_scenarios
```

`steps[]` defines ordered `{id, app, parameters}` computations. Within a later parameter document, `{file: "@earlier_id", ...}` references the fresh earlier result. Ordinary relative paths resolve against this scenario input's directory. The chain runs without a cache and temporary results are removed after observations are collected.

`variables[]` names each varied input, its dotted path into `steps`, nominal value, spread and distribution (`uniform`, `normal`, `lognormal`). Uniform spread is a half-range, normal spread a standard deviation, lognormal spread a log-space standard deviation around its nominal median. `correlation` is the latent normal correlation matrix; for non-normal marginals it is not the physical-value Pearson matrix. The matrix is checked for symmetry, unit diagonal and positive semidefiniteness.

`draws` and `seed` generate a reproducible table reused across every `model_scenarios[]` case. Each model case supplies fixed path overrides; it has no inferred probability. Draw zero is the nominal point. `derived_ts[]` names T/S record paths for recomputing Qts and Mms from the authoritative fs/Vas/Sd/Q values.

`observables[]` identifies a step, result path, name and reduction (`scalar`, `min`, `max`, `mean`, `rms`). Outputs preserve all nominal/drawn outcomes, input errors, resolved/unresolved counts and conditional production percentiles per model case. A null/censored value remains unresolved for the statistic rather than disappearing from its denominator. The app computes no ranking, target acceptance or production yield from arbitrary model scenarios.

Use the same production draw definitions for candidate comparisons, inspect domain errors and nominal recovery, and keep scenario uncertainty distinct from numerical mesh/solver refinement.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
