# Comparable sources and revisions

Use this procedure when importing published curves, inheriting a design, changing a model convention or comparing geometry variants. These checks establish internal consistency; they do not validate a model against a real speaker.

## Identify the baseline

Identify the exact delivered realization and its dependency chain, including the physical board, sources, calibration, geometry and metric definitions. A candidate name alone may refer to an earlier exploration. Preserve the original evidence; replay the same hardware with the current code and metric basis before ranking revisions. Show copied and regenerated figures together and explain changes without silently changing the user's targets.

Reconcile supplied CAD, loose-panel drawings, assembled drawings and parts lists by revision. Decide which physical artifact governs before rejecting replacement hardware for a clearance conflict. Recheck inherited prose as well as numbers: observer height, model domain, terminal connection used to measure tuning, notch values and stress figures. A crossover change can move an input-impedance feature without changing the box tuning.

Use exact IDs for edits and dependency rebasing. Candidate-owned dependencies can move; a comparison reference must retain its identity. Clear inherited price, availability, dimensions and source fields when deriving a new part record. Compare each final leaf's value, DCR/ESR, tolerance and rating with its selected stock row and exact SKU, catching second quantization into another series. Normalize prices to one tax/customer/currency basis with vendor and date; distinguish catalogue existence, quantity-specific stock, an unquoted item and a complete total.

## Put sources on a shared basis

For each curve record drive voltage, distance, baffle/test-box dimensions and orientation, smoothing, gating and near-field splice. Search the manufacturer's separate fixture and measurement-method documents. Match the fixture row to the exact driver. Compare published level and excess rise with the driver's own T/S prediction within the lumped model's useful band.

Remove a known fixture effect only with an explicitly approximate model before applying the intended baffle. Do not add a second baffle step to a measured finite-box curve. Unknown fixtures need plausible bounding scenarios and an uncertainty statement; choosing one is not validation.

Build the complete uncalibrated source, including replacement/blending and any fixture correction, before deriving its absolute calibration. Use one declared band and statistic, rerun, and check actual output against graph anchors. An unexplained offset in numeric FRD data is not digitizing uncertainty. Apply a correction consistently to the incumbent and revisions; recheck crossing, relative phase and supported output, not only sensitivity. Pressure calibration does not rescale physical current or excursion.

## Check what changed

Trace every consumer of a supposedly overridden input before removing or relabelling it. For example, explicit radiator mass can set resonance while nominal tuning still sets leakage resistance through a loss-Q reference. Preserve the same physical loss prior during a metadata cleanup. Compare expected with observed change, including acoustic coordinates when a cabinet lip or outside envelope changes but the source does not move.

For a recess, pocket or duct outside a model's validated geometry, compare plausible model scenarios, fit where necessary under each, and report which objectives or ranking flip. Their spread is model sensitivity, not a confidence interval. Choose the realization using those scenarios, improve the model or geometry where a central objective flips, and prefer margins that survive the uncertainty when the brief permits.

Before comparing panels, cavities or alignments, locate each variant's relevant modes/resonances and extend the analysis band to cover them with margin. Extend upstream excitation data too and recheck mesh resolution. Repeated worst-case frequencies can indicate an inherited band limit. Check that a quoted mode band brackets the mode it purports to bound; an isotropic band is not automatically a bound for an orthotropic calculation. If it does not bracket, report the mismatch instead of a false construction advantage.

Record these checks in `framework/templates/simulation-audit.md`, with actual files and conditions. Use that evidence to make and document the design decision; numerical consistency and empirical accuracy are distinct.
