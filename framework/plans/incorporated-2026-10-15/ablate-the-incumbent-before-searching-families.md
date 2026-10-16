---
id: ablate-the-incumbent-before-searching-families
date: 2026-10-12
project: neat-petite-dayton-opus, neat-petite-dayton-astra, neat-dayton-redcatt
phase: design
confidence: medium
applies_when: Asked to reduce the part count or redesign the topology of an existing crossover whose drivers stay fixed
tags: [crossover, search, ablation, part-count, topology, process]
---

## What went wrong
A fixed-hardware revision asked for fewer crossover parts. Exhaustive stock-grid searches were queued for a long list of four-, five- and six-part families, and each larger search ran for many minutes to most of an hour. Only after several had finished did a one-minute check of the incumbent show the mechanism: the incumbent network with one element removed. The element that looked like a breakup trap was in fact what pulled the acoustic crossing down and turned the relative phase into alignment. Every family without an equivalent element was bound to fail, so a large share of the search time went to families that could have been ruled out first, and the queue had to be stopped and reordered.

A later revision made the opposite mistake: it carried the incumbent's multi-part functions into the starting architecture and added shaping parts until the user rejected the complexity. A user-directed build-up from zero exposed each trade more clearly. A nominal low-pass capacitor produced a resonance with the inductive driver load; resistive damping improved integration but spent input power. The resulting six-part path still missed the smoothness goal. Neither the incumbent's ablation nor that unsuccessful greedy path established a universal minimum part count.

A final-network removal test then appeared to show a redundant woofer rejection capacitor: refitting the other parts improved several axial metrics. Comparing the individual acoustic branches exposed substantially greater breakup-region leakage, which the summed-response score had rewarded rather than penalized. Conversely, two upper-band shaping parts looked partly recoverable on the narrow crossover-band score while their refitted omissions worsened the high-frequency contour or vertical response. A fixed-values removal test and a narrow refit score answered different, incomplete questions about usefulness.

## What could have helped
Before searching for smaller or different networks, ablate the incumbent: remove each element in turn, or use `crossover_fit`'s ablation pass, and read the crossing frequency, the relative phase across the overlap and the off-axis dips, not only the on-axis error. Name what each element does for this driver, then search first the families that keep that function, and give the others a short coarse screen. Estimate a search's size from its grid lengths before queuing it and order the queue by how likely each family is to survive. Ablation explains the incumbent only; a family it rules out can still be worth a quick screen when the stock grid or the drivers differ.

Establish the user's component budget before treating extra shaping as an acceptable cost. When a constructive build-up is requested, actually simulate the zero-part state and let each single addition answer a named residual. Hold prior values and sources fixed for its first comparison; record subsequent value, placement and polarity changes as separate operations. Compare every trial with omitting the proposed part, the whole relevant response band and the released design. A minimum inside one value sweep does not mean that adding that component helped. Resolve meaningful stock-range boundaries, and preserve a negative result as a finding about the tested path without claiming proof about every network within the budget.

At final selection, consider both controlled omission and refitting, and inspect each branch's unwanted-band contribution alongside the complete response, protection, phase, heat and angular behavior. A useful part need not win every axial statistic. Materialize a promising refitted omission on actual stock before claiming either redundancy or impossibility; an incomplete stock grid can hide a viable alternative, while a smooth sum can hide a rejection tradeoff. Keep the evidence for that tradeoff in the project rather than converting it into a universal minimum-part claim.
