---
id: check-source-spacing-before-a-directivity-objective
date: 2026-09-14
project: forte-iii-r3
phase: research
confidence: low
applies_when: Writing a listening-window, off-axis or directivity objective for a multi-way with separated drivers
tags: [objectives, directivity, geometry, spacing, feasibility]
---

## Observation
A seating-window objective of 4 dB maximum deviation over plus or minus 10 degrees was written into
the brief's objectives before any geometry existed. Nine candidates were then built and the figure
ranged from 3.98 to 19.75 dB; only the three that used a coaxial compression driver, where the
midrange and treble share one horn mouth, reached the goal, and every one of those missed the
20 kHz objective instead because no coaxial driver in the inventory held its top octave. In the
selected design the woofer sits 390 mm below the midrange horn and the treble horn 180 mm above
it, and 180 mm is the minimum the two horn mouths allow: a 240 mm tall midrange horn and a 120 mm
tall treble horn cannot have their centres closer than 180 mm. Both acoustic crossings, at 955 Hz
and 3331 Hz, are well above the frequencies where those spacings stay inside half a wavelength,
which are 440 Hz and 950 Hz.

## Why it mattered
The objective was unreachable by construction for every architecture the inventory allowed, and
that was not visible until the candidates existed. Effort went into chasing it, and the final
package has to explain a missed objective that was never achievable rather than a design
shortcoming. The reference speaker has the same three-source geometry and its own published
measurement describes the crossover suckout deepening off axis, so it would very likely miss the
same goal.

## Advice
Before writing a window or off-axis objective, consider computing the crossover frequencies the
architecture forces and the source spacings the parts allow, and comparing the wavelength with
twice the spacing. Two sources separated by d interfere inside a narrow window once the wavelength
falls below roughly 2d; the smallest spacing a pair of horns allows is half the taller mouth plus
half the shorter one. If every crossover the inventory supports sits above c divided by twice that
spacing, the objective is a statement about geometry rather than about design quality. It may be
better to drop it, to write it at the value the architecture can reach, or to keep it and say in
the brief that meeting it requires a coincident-source device. Where a coaxial driver is the only
section to meet it, check its top octave first: sharing a horn mouth and holding 20 kHz are different
problems and one inventory may not offer both.

## Evidence
- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, the seating-window column across nine candidates
- `framework/projects/forte-iii-r3/final/05-objectives-and-findings.md`, "Why the seating window is missed"
- `framework/projects/forte-iii-r3/postmortem.md`, reason 1
