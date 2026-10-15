---
id: extend-stock-grids-before-searching
date: 2026-10-02
project: neat-petite-amt-v4, neat-petite-amt-v5, neat-petite-dayton-astra, neat-dayton-redcatt
phase: design
confidence: medium
applies_when: Searching or snapping crossover values over stock-part lists, especially for a new driver whose impedance or breakup differs from the one the lists were built for
tags: [crossover, inventory, stock, search, grid]
---

## What went wrong
Part lists built for one design bounded the search for the next, and the bound looked like a design limit. In one project a capacitor list that began at a round value kept an exhaustive search away from the value that tuned a trap. A resistor list missing one value forced a premium part into the selected network, and a list built from a first search omitted the value a fit needed, so the realization silently snapped away from it.

In a later project that compared many woofers, the coil list ended where a 4 ohm design had needed it. The 8 ohm and less sensitive woofers wanted larger coils. The capacitor list started above the value that would trap one woofer's breakup, so an evaluator's request to trap it was never actually tested in that iteration. Shunt-capacitor and tweeter-coil grids were similarly short. Each was found only because a best row sat on a grid edge or an evaluator asked, and each cost a rerun.

An inherited heavier-wire table was subsequently treated as if its last entry were the supplier's product limit. Checking the manufacturer catalogue and current retailer pages established larger coils with different winding shapes and DCRs. The omitted options did not automatically win the new comparison, but their absence could no longer be used as evidence that a lower-loss alternative did not exist.

A grid can also be dense on paper and sparse where the fit lands. In a fixed-hardware revision the woofer coil's heavy-wire series had no value between two widely spaced stock inductances. A continuous fit chose a value inside that gap. Snapping each value to its nearest stock neighbour turned a good fit into a poor one, because the bass balance hinged on that one coil, and neighbour descent from the snapped point could not recover. A whole elimination batch had to be discarded.

## What could have helped
Before a stock-grid search, derive each list's range from what the topology can want for this driver. Examples:
- the series coil for its impedance and the baffle step it shelves;
- the trap or notch values for its breakup frequency with the largest coil in the grid;
- the pad for its level.

Extend each list to the full range the series is sold in, with price and loss data. Treat any best row on a grid edge as a grid finding and extend the grid before judging the design. Compare every realized value with its fitted value, and confirm the list covers the series around it before a realization may snap to it. Where a value exists only in a costlier series, check whether the cheap series carries it before accepting the premium part.

Where a series is sparse near the values a fit can choose, either hold that part at a stocked value during the continuous fit, or snap all parts together. One way to snap together is to enumerate every combination of the stock values just below and above each fitted value, then descend from the best few. Snapping one value at a time to its nearest neighbour hides the interaction.

Keep catalogue existence, actual supplier stock and unverified price as separate fields. Different SKUs at the same inductance and wire gauge can have different DCR, diameter, height and mass. Carry the chosen SKU's electrical and physical data together; do not invent a price or mix one variant's low resistance with another's smaller package. Preserve the old inventory record when extending a new study so frozen designs remain traceable.
