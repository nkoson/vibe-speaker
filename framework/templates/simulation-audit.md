# Actual-project simulation audit

Record inputs, result paths/JSON fields, model revision, drive, grid, expected relationship, observed error and interpretation for each applicable check. Mark an inapplicable check with the reason. These are numerical/input-consistency checks, not agreement with measurement.

| Check | Expected relationship and conditions | Evidence and interpretation |
|---|---|---|
| Single section at unity transfer | Source level plus declared baffle and reference/actual-distance ratio; no second 1 m correction | |
| Colocated cone plus outlet | Same box sum and drive, consistent radiation space, no duplicate outlet | |
| Actual placement | Explain finite-baffle, rear factor and path-length changes against the colocated case | |
| Published shape | Calibrated graph anchors and upper slope; deep-bass level preserved through the blend | |
| Level basis | Compare parameter-derived and published levels at the same band, voltage, distance and space; name chosen basis and uncertainty | |
| Known series resistor | Move resistance from box drive to network; pressure (cone and outlet), current and excursion agree under the same drive | |
| Aggregate drivers | Independent coupling calculation: total pressure, physical per-motor current/excursion, actual radiator count; state cavity-model limitation | |
| Cold replay | Rerun dependencies in order without cache, compare frozen results; record code revision and any changed input | |
| Inherited baseline | Identify released realization and artifact revisions; regenerate figures on current basis without changing targets | |
| Fixture and final calibration | Record test geometry/splice; calibrate after source shaping; verify completed source against anchors | |
| Parameter consumers | Trace apparently overridden inputs and loss references; explain expected versus observed change | |
| Scenario and band coverage | Carry plausible geometry models; include every compared resonance with adequate upstream data and mesh | |
| Realized stock and protection | Exact SKU/value/loss/rating; loaded terminal transfer on final grid with explicit voltage reference | |
| Search and ranking | Known-start fit retained; score tested on contrasting cases; changed scores applied to all affected candidates | |

Graph calibration record: source URL/document, variant, test horn/baffle, two or more axes/curve anchors, reading uncertainty, phase provenance. Acoustic calibration records the gain and its derivation; it does not rescale current or excursion.

Correction log: cause; affected candidates; original and corrected evidence; ranking impact; exploration invalidated; budget treatment. Use new exploration IDs only for actual design exploration, not validation reruns.
