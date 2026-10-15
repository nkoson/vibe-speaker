# Incorporation of October project learnings

Date: 2026-10-15. Status: complete. All 18 findings incorporated, verified and retired from the active index.

Scope: all 18 untracked learning files and the modified learning index present when this work began. Their two-section format was already consolidated across projects; no project numbers were promoted into general requirements. The original files are preserved in `incorporated-2026-10-15/` as historical evidence, outside the active learning workflow.

## Review and implementation

Existing source calibration, terminal-voltage normalization, fresh replay, ablation, tolerance and stock facilities were inspected rather than claimed as new. Reviewed `source_response/run.py`, `crossover_fit/run.py`, `plate_structure/run.py`, `_common/bass.py`, schematic/plot tooling, current designer/evaluator/documentation skills, simulation/geometry audits and measurement/model-limit guidance. Remaining code limitations are expressly retained as limitations: nearest-value snapping is not a coupled stock search; local least squares does not guarantee an incumbent score; an isotropic panel band does not necessarily bracket an orthotropic mode. No numerical model was changed in this incorporation commit.

The procedures are progressively disclosed from existing skills:

- **integrity**: [Comparable sources and revisions](../skills/speaker-design/references/simulation-integrity.md), routed from orchestrator, designer, evaluator and documentation.
- **crossover**: [Search and diagnose a realized crossover](../skills/speaker-designer/references/crossover-search.md), routed from designer and evaluator.
- **construction**: [From model to buildable drawings](../skills/speaker-documentation/references/construction-audit.md), routed from designer and documentation.
- Applicable evidence fields added to `templates/simulation-audit.md` and `templates/geometry-audit.md`.

## Per-learning disposition

Each row was checked against the entire original learning, including later-project qualifications. The implementation column is the completed change; the linked original preserves its failure mechanism, confidence and source projects. Verification means workflow/content review, not empirical validation of loudspeaker physics.

| Original finding | Procedure | Completed incorporation and verification |
|---|---|---|
| [ablate-the-incumbent-before-searching-families](incorporated-2026-10-15/ablate-the-incumbent-before-searching-families.md) | crossover | Controlled omission before family search; zero-part path and full-band refit comparisons; reviewed against original and available tool behavior. |
| [analysis-band-covers-compared-features](incorporated-2026-10-15/analysis-band-covers-compared-features.md) | integrity | Extend upstream band/mesh; check each governing mode and claimed bracket; reviewed against original and available tool behavior. |
| [audit-board-drawings-against-circuit-nodes](incorporated-2026-10-15/audit-board-drawings-against-circuit-nodes.md) | construction | Circuit/copper/holes/visible-wire audit; solderless contacts and actual assembly; reviewed against original and available tool behavior. |
| [bound-unvalidated-geometry-models](incorporated-2026-10-15/bound-unvalidated-geometry-models.md) | integrity | Compare plausible model scenarios and objective/ranking reversals; reviewed against original and available tool behavior. |
| [calibrate-after-source-shaping](incorporated-2026-10-15/calibrate-after-source-shaping.md) | integrity | Calibrate the completed source and rerun actual graph anchors; reviewed against original and available tool behavior. |
| [check-protection-on-realized-transfer](incorporated-2026-10-15/check-protection-on-realized-transfer.md) | crossover | Qualify maker condition; test loaded terminal voltage, absolute and normalized; reviewed against original and available tool behavior. |
| [decompose-off-axis-dips-before-attributing](incorporated-2026-10-15/decompose-off-axis-dips-before-attributing.md) | crossover | Geometry, aligned real magnitudes and actual complex-sum counterfactuals; reviewed against original and available tool behavior. |
| [exact-identity-in-candidate-revisions](incorporated-2026-10-15/exact-identity-in-candidate-revisions.md) | integrity + construction | Stable IDs/SKUs, price basis, dependency roles, panel/local/installed datums; reviewed against original and available tool behavior. |
| [extend-stock-grids-before-searching](incorporated-2026-10-15/extend-stock-grids-before-searching.md) | crossover | Catalogue endpoints and gaps; jointly realize interacting values with exact losses; reviewed against original and available tool behavior. |
| [grain-direction-follows-the-joints](incorporated-2026-10-15/grain-direction-follows-the-joints.md) | construction | Joint/grain/seasonal float and short-grain features considered together; reviewed against original and available tool behavior. |
| [lay-out-crossover-from-part-dimensions](incorporated-2026-10-15/lay-out-crossover-from-part-dimensions.md) | construction | Part-level bodies, wiring, coils, restraints, supports and assembly access; reviewed against original and available tool behavior. |
| [phase-reference-before-plotting](incorporated-2026-10-15/phase-reference-before-plotting.md) | construction | Canonical branch phase, common delay once and ordered relative phase; reviewed against original and available tool behavior. |
| [put-datasheet-curves-on-one-baffle-basis](incorporated-2026-10-15/put-datasheet-curves-on-one-baffle-basis.md) | integrity | Fixture documents, approximate de-embedding, shared basis and uncertainty; reviewed against original and available tool behavior. |
| [recompute-inherited-baselines](incorporated-2026-10-15/recompute-inherited-baselines.md) | integrity | Released dependency replay, original/corrected comparison and governing CAD; reviewed against original and available tool behavior. |
| [score-what-a-response-target-trades-away](incorporated-2026-10-15/score-what-a-response-target-trades-away.md) | crossover | Whole relevant band, actual user priorities, contrasting score cases, all-row reranking; reviewed against original and available tool behavior. |
| [seed-global-fits-with-the-incumbent](incorporated-2026-10-15/seed-global-fits-with-the-incumbent.md) | crossover | Known/perturbed starts, best-point retention and nonsmooth solver diagnosis; reviewed against original and available tool behavior. |
| [trace-all-consumers-of-overridden-parameters](incorporated-2026-10-15/trace-all-consumers-of-overridden-parameters.md) | integrity | Trace loss-reference consumers and expected versus observed physical changes; reviewed against original and available tool behavior. |
| [verify-routed-contours-against-hardware](incorporated-2026-10-15/verify-routed-contours-against-hardware.md) | construction | Actual arcs/tooling, gasket position, moving clearance and full fastener stacks; reviewed against original and available tool behavior. |

## Verification

- All five skill entrypoints passed the skill-creator frontmatter/scaffold validator.
- Original learnings retain their complete source text and provenance in the historical archive.
- Full framework suite: `142 passed in 17.20s` (`.speaker-venv/bin/python -m pytest framework/tests -q`).
- Post-retirement learning/reference tests and local skill/plan links checked before commit.

This is workflow incorporation. It does not claim the simulation defects or missing automation identified by these checks have all been implemented; current application limits and interpretation checks are documented in the designer skill's model-coverage procedure.
