---
id: room-simulation
applies_when: Predicting loudspeaker behavior at actual listening positions with walls, reflections and uncertain room geometry
updated: 2026-10-15
---

# Room simulation and virtual observations

A computational receiver can sample pressure, phase and spatial variation without asking the user to measure a speaker. The useful question is which physical effects the simulation resolves. Preserve free-field design quality and evaluate placement/room interaction as another set of objectives and scenarios.

## Available models

| Model | What it adds | What remains outside it |
|---|---|---|
| `whole_speaker` | Coherent section sum and optional floor image | Other room boundaries, scattering and modes |
| `room_response` | Rectangular 3D geometry, finite specular reflection orders, speaker orientation, multiple receivers and complex boundary-interference curves | Converged modal bass, diffuse late field, furniture, cabinet scattering, wall motion |

The image method represents specular paths by mirrored geometry. Allen and Berkley's rectangular-room formulation is the basis for this class of model. A finite-order sum truncates the reverberant response; it does not inherit the accuracy of an infinite ideal-room solution. [Allen and Berkley, 1979](https://www.trueaudio.com/array/downloads/Image%20Method-Allen%20and%20Berkley%201978.pdf)

Pyroomacoustics demonstrates the broader architecture: explicit sources/receivers, image paths and a hybrid ray method for later reflections/scattering. Its documentation also distinguishes pressure reflection from energy absorption and warns that a Sabine-derived setting need not yield the requested decay time. This supports keeping boundary assumptions and numerical convergence visible; it does not supply this repository's error bar. [Room simulation documentation](https://pyroomacoustics.readthedocs.io/en/stable/pyroomacoustics.room.html)

## Engineering use

**Room known.** Use its dimensions, source placement, toe-in and listener region. Assign wall coefficients with their basis, then compare plausible alternatives for uncertain surfaces. Model the selected driver/outlet positions and loaded network, not an omnidirectional replacement for the whole speaker. Evaluate a region around the main seat so one narrow cancellation does not dominate the design.

**Room unknown.** Declare representative dimensions and placement ranges appropriate to the brief, and select designs whose advantages survive them. These are scenario studies, not forecasts of a particular home. Keep broad voicing and directivity priorities separate from a single room's narrow comb structure. Do not flatten every simulated room dip with a passive crossover: compare source movement, listener movement and direct sound first.

**Simulation outputs.** Compare direct and reflected pressure, equal-voltage bass, seat energy mean and spread, and arrival geometry. Coherent multiple-speaker input is a distinct signal condition from independent stereo. The CTA-style predicted-in-room curve in `spinorama` is an angular weighting estimate, not this particular room's pressure response; keep their names and interpretations separate.

**Convergence.** Refine reflection order, frequency spacing and, for future wave models, mesh size independently. Boundary scenarios are physical uncertainty; numerical refinement tests discretization/truncation. Do not silently convert either spread into a statistical confidence interval. A rigid rectangular box has reference modal frequencies `f = c/2 sqrt((nx/Lx)^2 + (ny/Ly)^2 + (nz/Lz)^2)`; reproducing them is a useful future wave-solver test but does not establish modal amplitudes or losses in a furnished room.

**Design responsibility.** Use these observations to choose geometry, placement ranges, directivity and network margins. Finish the construction design under explicit assumptions rather than replacing a hard decision with a generic instruction to measure. A model limitation is a reason to improve the relevant calculation or choose a less sensitive design, not to imply that a final simulated design is impossible.

## Sources

- J. B. Allen and D. A. Berkley, [Image method for efficiently simulating small-room acoustics](https://www.trueaudio.com/array/downloads/Image%20Method-Allen%20and%20Berkley%201978.pdf), JASA 65(4), 943–950, 1979. Primary paper, mirrored copy.
- R. Scheibler, E. Bezzam and I. Dokmanić, [Pyroomacoustics: A Python package for audio room simulations and array processing algorithms](https://arxiv.org/abs/1710.04196), 2017/ICASSP 2018. Source/receiver and simulation architecture.
- Pyroomacoustics authors, [Room Simulation documentation](https://pyroomacoustics.readthedocs.io/en/stable/pyroomacoustics.room.html), accessed 2026-10-15. Image/ray distinction and boundary conventions. No external package is required by the current local implementation.
- Local contract: [room_response](../simulations/room_response/README.md). The image-receiver formula, normalization and tests there define this implementation.
