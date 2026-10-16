---
id: decompose-off-axis-dips-before-attributing
date: 2026-10-02
project: neat-petite-dayton-opus, neat-dayton-redcatt
phase: evaluation
confidence: medium
applies_when: A dip or peak persists in an axial or off-axis response and its cause is about to be attributed to phase, spacing or a driver
tags: [directivity, vertical-window, dips, attribution, geometry, crossover]
---

## What went wrong
Persistent response features were easy to attribute to the nearby crossover or fixed driver spacing before checking which source actually produced them. In the off-axis case, ideal acoustic targets at the real positions gave a much shallower valley than the real network: source magnitude, phase drift and out-of-band woofer leakage supplied the rest. In the axial case, the tweeter dominated a trough and peak while the woofer was already 18 to 33 dB lower; phase alignment could recover only a small part of the deficit. At higher frequencies, woofer leakage again caused material cancellation. Treating every nearby feature as the same phase or spacing problem would have sent both searches toward the wrong remedy. Broad equalization could then suppress a peak while deepening its neighboring trough.

## What could have helped
Before naming the cause of a feature that resists the network, compute three floors at the actual positions and observer:
- ideal acoustic targets at the crossing (geometry only);
- the real section magnitudes with zero relative phase (driver response);
- the real network (phase drift and leakage).

Find the frequency and angle that set the figure, and read the section levels and relative phase there before choosing an explanation. Where one branch dominates, compare its actual magnitude with the zero-relative-phase sum before spending more effort on crossing phase. Isolate a proposed equalizer against an otherwise fixed network, then score both neighboring shoulders and the wider band. Read a valley measure beside the vertical window, because rows can lower one by broadening the other. The decomposition still rests on the section models; a breakup feature computed with a piston directivity past its validity is the least certain part of it.
