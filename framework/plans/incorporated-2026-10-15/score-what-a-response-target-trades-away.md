---
id: score-what-a-response-target-trades-away
date: 2026-10-02
project: neat-petite-amt-v4, neat-petite-amt-v5, neat-petite-dayton-astra, neat-petite-dayton-opus, neat-dayton-redcatt
phase: design
confidence: medium
applies_when: Searching, fitting or ranking crossover values against a target - a narrow response feature such as dip depth or crossing phase, or a composite closeness score against a reference design
tags: [crossover, search, ranking, response-quality, spinorama, dips, phase, voicing]
---

## What went wrong
Searches and rankings optimized what they scored and spent what they did not. In one project a revision scored an in-phase crossing and shallow dips. The networks that won turned the dip into a broad presence-region hump, and the predicted in-room smoothness fell. That surfaced only when spinorama ran on the finalists, after an iteration had carried them.

In a later project, many woofers were each ranked by a composite closeness-to-a-reference penalty, which was revised four times while the batch ran. Without f3 the search traded bass extension for sensitivity. Without a bass-balance term it bought f6 with a several-dB hump. With a near-hard balance limit over too narrow a band it left sensitivity unused and missed humps just above that band. Without the sweep level, output was never weighed.

The penalty had been validated only on the reference design's own network. There every shortfall is zero, so the check could not show any of this. Each discovery forced a re-rank or a rerun of the whole batch.

A fixed-hardware crossover revision also exposed a judgment problem after the numbers were available: an initial selection gave the diagnostic vertical window and a small narrow-band-deviation advantage more weight than the user's general phase, on-axis smoothness and reference-contour priorities. The modeled in-room curve then separated the close alternatives and changed the choice before construction freeze. Agent-defined working tolerances had helped comparison, but counting their misses could not substitute for interpreting the actual qualitative brief.

In another fixed-hardware revision the brief asked for a reference product's tonal shape, scored as an octave-scale RMS difference against its digitized curve. The trade table was first drawn only from the best-ranked rows, which all share one voicing, so it could not show what a closer shape would cost. Drawn from every row, it showed the price: window dip, narrow-band deviation and predicted preference. That price ran mostly through the in-room slope term, because the reference's rising treble flattens the predicted in-room tilt.

A later part-count revision scored narrow-band deviation, which ends at 12 kHz, and weighted the top octave lightly. Its leading networks bought smoothness below 12 kHz with a 4 dB rise above 14 kHz, and this was seen only when the curves were plotted. The same score treated woofer break-up suppression as a soft term, so backward elimination removed the break-up notch. Once both were fixed the ranking changed. The eventual winner had been in the very first batch, but ranked low under the old score and coarse snapping; it surfaced only when a later batch happened to re-fit it.

## What could have helped
Score each target's counterpart in the same search: peaks beside dips, deviation from a fitted trend over the crossover band, and the listening-window and in-room curves, not only the on-axis curve. Put every objective the comparison is judged on into the score, including bass balance over the whole region a hump can occupy, extension and output. Weight them so that no term silently acts as a hard constraint.

Before a batch, check the score on two or three cases that differ from the reference, for example a more sensitive, a less extended and a higher-impedance driver, and look at what the top rows give up. Validate any library computation against one app run.

Report the main trade as a table or curve, such as bass lift against f6 and sensitivity, so the user sees what each target costs. Check that the score covers the whole band the brief speaks about, including the top octave above the narrow-band band limit. Hold safety-type objectives such as break-up suppression and driver protection as hard floors.

Freeze the score before the batch runs, and record any later change with the rows it re-ranks. After a change to the score or to the stock snapping, re-score or re-fit every earlier candidate, not only the previous leaders. A preference score from modelled curves remains a ranking aid and does not settle the trade. Draw a trade table from every scored row, not from the top of the ranking. For a reference-shape target, sweep the one part that sets the voicing (often the pad) and put predicted preference, narrow-band deviation and dips beside the shape figure.

Before announcing a final leader, compare the close candidates on the full relevant response family and the same component-tolerance assumptions. Keep a user priority distinct from a diagnostic threshold introduced by the designer. Differences of fractions of a degree or tiny graph residuals may be less informative than their source uncertainty; show the competing improvements and costs, and record an evidence-based selection revision rather than silently moving targets.
