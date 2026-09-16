---
id: price-the-removed-output-before-designing
date: 2026-09-15
project: forte-iii-one-woofer-20260915
phase: research
confidence: low
applies_when: A brief removes output from an earlier design (a driver, a parallel connection, cabinet volume) while adding or tightening a load, size or cost constraint
tags: [brief, feasibility, sensitivity, amplifier-load, parallel-drivers]
---

## Observation
A brief asked for a previous design's performance to be matched or beaten, with the amplifier load
returned to the reference speaker's and at most one woofer. The previous design used two 12 inch
woofers in parallel. Paralleling them had done two things at once: it gained about 6 dB of voltage
sensitivity, and it halved the impedance, taking the minimum to 1.888 ohm and the current at the
project's 18 V probe to 9.535 A. The new brief asked for the second effect to be undone while the
first was kept.

A 430-run screen over eleven single woofers, four radiators, volumes from 90 to 240 L and the real
baffle established the answer before any candidate was built: one woofer supported a system level
about 1.5 dB lower, growing the box from 110 to 170 L moved the 38 Hz output by 0.7 dB, and the most
efficient woofer in the inventory held its lowest useful frequency 4 dB quieter than the chosen one.
The delivered design matched or beat the previous one on sensitivity, both ripple bands, the seating
window and the network heat, took the impedance minimum from 1.888 to 3.237 ohm and the current from
9.535 to 5.560 A, and gave up 1.1 to 3.9 dB between 38 and 63 Hz.

## Why it mattered
The brief was not internally satisfiable, and saying so with an arithmetic derivation at the start
turned the whole run into a search for the best point on a known trade instead of a search for a way
out. The selection statement, the evaluation and the package could all name one regression and its
cause in a sentence, rather than reporting a list of missed rows.

## Advice
When a brief removes a source of output and constrains the load in the same breath, consider writing
the arithmetic down before designing anything: n drivers in parallel are 10 log10(n) decibels of
power sensitivity and 20 log10(n) of voltage sensitivity, and the same n divides the impedance. Those
are one fact with two faces, and a brief that asks to keep one and undo the other is asking for
something the inventory has to supply from elsewhere - a larger driver, a larger box, a different
loading, or a lower target.

Consider screening the removed output's replacement candidates across the whole allowed range of the
variable the brief leaves free, not just the plausible ones, so that the infeasibility claim rests on
a range rather than on a few tries. Then state the price in the units the brief used, and let the
selection be about where on the trade to sit.

## Evidence
- `framework/projects/forte-iii-one-woofer-20260915/inventory/single-woofer-screen.md`
- `framework/projects/forte-iii-one-woofer-20260915/evaluations/iteration-3.md`, selection statement
- `framework/projects/forte-iii-one-woofer-20260915/postmortem.md`, outcome table
