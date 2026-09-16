---
id: keep-system-and-box-cutoffs-separate
date: 2026-09-15
project: forte-iii-three-way, forte-iii-r3, forte-iii-one-woofer-20260915
phase: evaluation
confidence: high
applies_when: Comparing bass extension between candidates or with a box-only figure
tags: [cutoff, f3, f6, reference-band, statistics]
---

## Observation
The sustained cutoff statistics depend on the reference level they are measured against. `lf_box` measures against the woofer's own 150 to 300 Hz mean; `whole_speaker` measures against the system's mean, which includes the upper sections' level. A box that read f6 of 37 Hz alone read a system f3 of 112 Hz once the rest of the system ran 14 dB louder. One candidate's system f3 of 376 Hz was a sustained-threshold artefact of a depressed low midband, not a physical high-pass. And a reference-like f6 was at risk of being quoted as an f3.

A later project met the other half of the same problem: a cutoff that is stable in name but not in
value. Its selected design sloped gently through the cutoff region rather than turning a corner,
and rebuilding it at four system levels moved the sustained f6 between 54.5 and 73.8 Hz while the
absolute output at 38 Hz stayed inside half a decibel. Two consecutive rebuilds of the same
voicing, differing only by resistor values quantized to real stock, moved it by 0.2 Hz across a
tolerance boundary. The figure was reported as sitting on its boundary rather than as met.

## Why it mattered
Mixing box-only and system cutoffs, or f6 and f3, made candidates look closer to or further from the target than they were, and hid the real mechanism (system level) behind a frequency figure.

A third project measured how far the figure moves. The same hardware and the same crossover topology
fitted at seven system levels moved the sustained f3 from 35.98 to 39.48 Hz while the absolute output
at 38 Hz varied by 0.17 dB, and at the top of the axis f3 jumped to 136 Hz because a mid-bass band
crossed the moving threshold. The cutoff followed the reference level almost entirely; the bass did
not change.

## Advice
Consider quoting every cutoff with its source app, its reference band and its threshold, and comparing like with like: box-only cutoffs to judge the alignment, system cutoffs to judge the speaker. When a system cutoff looks implausible, look at the curve; the `bound` flag and the shape will show whether a shelf or a dip caused it. Keep f3, f6 and f10 labeled as what they are; a row that matches the reference only after relabeling one as another is not a match.

Consider treating a sustained cutoff as a summary of the levels rather than as a measurement of
the speaker. On a gently sloping response a threshold crossing moves several hertz for a few
tenths of a decibel of shape change, so a design that clears a cutoff tolerance by less than a
hertz has not been shown to clear it. Where that happens, quoting the level at three or four fixed
frequencies says more than the cutoff does, and rebuilding once to see how far the figure moves is
a cheap way to find out whether it is a discriminator at all.

## Evidence
- `framework/projects/forte-iii-three-way/evaluations/iteration-3.md`, "Bass and output interpretation"
- `framework/projects/forte-iii-three-way/postmortem.md`, "Changes required"
- `framework/simulations/lf_box/README.md` and `framework/simulations/whole_speaker/README.md`, statistics sections
- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, the voicing table and the cutoff warning
- `framework/projects/forte-iii-r3/postmortem.md`, "Outcome"
