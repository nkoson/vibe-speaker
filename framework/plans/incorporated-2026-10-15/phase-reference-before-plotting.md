---
id: phase-reference-before-plotting
date: 2026-10-02
project: neat-petite-amt-v3, neat-petite-dayton-astra
phase: documentation
confidence: medium
applies_when: Plotting acoustic section phase from a result that may already remove a common propagation reference
tags: [phase, plotting, provenance, validation]
---

## What went wrong
A phase plot removed the observation-distance delay a second time from section responses already expressed relative to that common distance. This introduced artificial phase wraps while leaving the section-to-section phase difference unchanged. A relative-phase check alone therefore did not reveal the plotting error. Independent review of the stored phase convention caught it before delivery; the physical simulation was unaffected.

An absolute crossing-phase objective can also conceal an ordering mismatch: one summary used LF-minus-HF while its plot used HF-minus-LF. Both had the same absolute error and the same correct acoustic sum, so a magnitude-only consistency check would not reveal the opposite signs. The issue was caught while reconciling the final figure and prose.

## What could have helped
Inspect the result's phase convention before applying any delay or normalization, and state the actual shared reference in the figure caption. Compare each plotted branch with its canonical complex response after only the declared wrapping or common transformation. A relative-phase comparison is useful as a second check, but cannot detect a common phase error applied to every branch. Independent branch shifts can conceal the integration that the plot is intended to diagnose.

Name the ordered subtraction whenever a signed relative phase is quoted, and convert signed tolerance intervals to that same order. Use an explicitly absolute value for an order-independent headline. Check the crossing marker against the plotted canonical branches as well as against the summary metric.
