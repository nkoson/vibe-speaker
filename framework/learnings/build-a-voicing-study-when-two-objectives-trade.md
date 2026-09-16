---
id: build-a-voicing-study-when-two-objectives-trade
date: 2026-09-15
project: forte-iv-single-pr, forte-iii-r3, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915
phase: selection
confidence: high
applies_when: Two objectives pull against each other along one axis and no single candidate satisfies both
tags: [selection, voicing, sensitivity, bass, tradeoff, user-decision]
---

## Observation
Sensitivity and bass cutoff traded against each other along a single axis: the system level the
crossover is fitted to. Rather than argue the trade, the same design was built at four system
levels and the numbers were read off. On one bass section, 3.7 dB of sensitivity bought 25 Hz of
system f6, almost linearly: 90.72 dB with f6 41.7 Hz, 94.38 dB with 57.9 Hz, 95.58 dB with
66.0 Hz. One point on that line met both objectives at once, and it was not the point either
extreme suggested. A second, earlier study on a different upper section gave the same slope,
which is what made the relationship trustworthy rather than a single coincidence.

A single-PR study confirmed the value of holding LF hardware fixed while varying upper
attenuation, but not a generally linear cutoff relationship. Sensitivity changed from
88.873 dB to 88.342 dB while sustained system f3 jumped from 49.340 Hz to 35.021 Hz.
The absolute LF response did not change: a shallow trough near 50 Hz crossed the moving
-3 dB reference threshold. The final physical realization gave 88.340 dB and 35.008 Hz.

A later project found the same intermediate trough deciding the sustained cutoff again, and by a
margin too small to be a design difference: c06 cleared the threshold near 300 Hz by 0.035 dB while
c04 sat 0.038 dB below it. The selected candidate reached 90.547 dB and 37.640 Hz nominally, but
only 19 of 24 joint tolerance scenarios met both targets and two of them had no sustained pass at
all - which the cutoff percentiles had quietly dropped rather than counted.

## Why it mattered
The first evaluation of the project had concluded that the two objectives were not jointly
satisfiable in that inventory and asked for a decision the brief had not given. Building the axis
answered the question without asking, and the resulting package can show the user two neighbouring
designs rather than one design and an argument.

A third project built a seven-point axis and found two things that no single candidate showed. The
absolute output at the brief's lowest frequency varied by 0.17 dB across the whole axis while the
sustained cutoff moved 3.5 Hz, so the apparent bass cost of voicing higher was entirely a change of
reference level. And the network's worst-case dissipation fell from 71 to 46 W as the system got
louder, because the upper pads got shallower, which made a heat objective and a sensitivity objective
two readings of one variable rather than two constraints.

## Advice
When an evaluation says two objectives cannot both be met, consider whether they trade along one
controllable variable before treating it as a decision for the user. If they do, building the same
design at three or four points on that variable is usually cheaper than another architecture, and
it turns the disagreement into a table. Keep the points as voicings of one candidate rather than as
separate candidates so the iteration count still measures design exploration; name the selected
point explicitly in the package and keep the neighbouring ones in the project so a reader can see
what the choice cost. Where no point meets both, the study is still the right thing to hand the
user, because it prices the constraint they would have to relax.

Consider recording absolute bass SPL, the cutoff reference band and the threshold margin at
intermediate troughs beside each voicing. A large sustained-cutoff change can result from a
small reference-level change; it does not imply added bass output or a robust linear trade.
If the requested construction document excludes design history, retain the comparison study
in project evidence and document only the selected hardware and its limitations.

Consider counting an unresolved cutoff as a failed scenario rather than excluding it from the
percentiles. A draw with no sustained pass is the worst outcome in the sweep, and dropping it
reports the robustness of the scenarios that happened to resolve. Where a margin at an intermediate
trough decides the ranking, say so with the margin: a few hundredths of a decibel between two
candidates is a tie to be broken on something else.

## Evidence
- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, the candidate table and the closing paragraph
- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, the c07 and c08 voicing rows
- `framework/projects/forte-iii-r3/postmortem.md`, "What went right", item 6
- `framework/projects/forte-iii-single-pr-20260914/candidates/c08/voicing-study/summary.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/selected-voicing.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, cutoff trade and outcome
- `framework/projects/forte-iv-single-pr/evaluations/iteration-2.md` and `final-tolerance-evidence.json`, the 0.035 dB margin and the 19-of-24 scenario count

