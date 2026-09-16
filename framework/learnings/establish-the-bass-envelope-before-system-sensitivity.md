---
id: establish-the-bass-envelope-before-system-sensitivity
date: 2026-09-14
project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-pr-20260914
phase: design
confidence: high
applies_when: Choosing the system level and the upper drivers for a bass-critical brief
tags: [bass, sensitivity, system-level, tradeoff]
---

## Observation
The same 12 inch woofer and passive radiator assembly appeared in two candidates. In the first the system was padded down to about 81 dB and the system f3 was about 30 Hz; in the second the upper section ran at about 95 dB and the system f3 moved to about 112 Hz. The bass section had not changed; the level the rest of the system was set to had. Lower radiator tuning could not close a level gap of that size.

A second study surveyed 63 bass alignments and moved to a 15-inch driver. The final finite-baffle passive system still settled near 90.5 dB, with f3 43.4 Hz and a 7.26 dB rise from 38 to 100 Hz. A prior fixed-trap experiment recovered deep output while creating a trough that pushed sustained f3 to about 240 Hz. A favorable box alignment or a lower reference-band level was not sufficient to establish full-band balance.

The passive-radiator follow-up grew the wooden envelope from 150.716 to 323.850 L. Sensitivity improved from 90.508 to 93.271 dB and 38 Hz output gained 2.561 dB at equal voltage, but system f3 worsened from 43.436 to 45.890 Hz and full-band ripple rose from 9.150 to 9.921 dB. Larger volume gave real absolute bass output without establishing a better normalized cutoff or balance.

## Why it mattered
The brief asked for both the reference's sensitivity and its bass extension in a similar volume. Pursuing the sensitivity in the upper bands, independently of what the bass section could deliver at that level, produced a speaker that met neither in a useful section: the selected candidate had a smooth midband and almost no bass relative to it.

## Advice
Consider deriving the system level from the bass section rather than the other way round: the level at which the bass reaches the target extension within its excursion and outlet limits is the level to pad the upper sections to. If that level is far below the brief's sensitivity, the honest options are more or larger bass drivers, a larger box, a different loading, or telling the user which of the two objectives has to give. Making the upper section louder does not add bass; it only moves the system cutoff up. When two candidates share a bass assembly, compare their bass at equal system level before reading their cutoffs.

Consider evaluating the complete bass-to-midband shape with finite-baffle/outlet propagation and realizable passive DCR, alongside absolute levels at the brief's lower limit and in the upper bass. A hump can make a cutoff look more favorable, while a notch can break the sustained passband. Narrow midband ripple and catalog sensitivity do not capture those mechanisms. Expensive low-loss parts may reduce copper loss but cannot create the missing deep-bass voltage sensitivity.

Consider retaining equal-voltage deep-bass output, sustained cutoff and broad-band ripple as separate comparisons when cabinet volume or system level changes. Improvement in one is not evidence that the others improved.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 2 and "Changes required"
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Reference comparison and lineage" (c04 to c08)
- `framework/projects/forte-iii-performance-20260914/inventory/bass-screen.md`
- `framework/projects/forte-iii-performance-20260914/evaluations/iteration-3.md`
- `framework/projects/forte-iii-performance-20260914/final/03-simulated-performance.md`
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`
