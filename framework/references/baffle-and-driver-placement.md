---
id: baffle-and-driver-placement
applies_when: Choosing the baffle size, deciding where each driver sits on it, setting the crossover frequencies that the spacing has to survive, or judging an off-axis result
updated: 2026-09-15
---

# The baffle and where the drivers sit on it

A driver's position is part of the acoustic design. The panel it is mounted on decides how much of its
output goes forward, its distance to each edge decides the diffraction ripple, its distance to the
next driver decides what happens off axis through the crossover, and its distance to the room's
boundaries decides what the bass does. None of that is cosmetic and none of it can be fixed by the
crossover afterwards: a network can change a section's level and slope, it cannot change where the sound
comes from.

## 1. What the baffle itself does

**Physics.** At low frequencies a cabinet is small compared with the wavelength and the driver
radiates into full space. As frequency rises the front panel becomes an effective barrier and the
same driver radiates into half space. The transition is worth 6 dB and it is called the baffle step.

Allison measured where the transition completes on a real cabinet and stated the rule in the simplest
possible form: a front panel whose minimum dimension is half a wavelength is an effective 2 pi baffle
for the driver at that frequency and above. For a panel of minimum dimension `W`, that frequency is
`c / (2W)` — about 380 Hz for a 450 mm panel, about 690 Hz for a 250 mm one. Below it the driver is
progressively losing the baffle's support; an octave or so below it, the driver is in full space.

**What the framework does.** `baffle_diffraction` computes the complex factor and reports
`relative_to_2pi_db`, where 0 dB is full baffle support and -6 dB is none, plus a `shelf_corner_hz`
for the width. The corner and the frequency at which the panel is fully effective are not the same
point: the corner is near the middle of the transition and full support arrives roughly an octave
higher. Read the curve, not the single number. See `simulations/baffle_diffraction/README.md`.

Section 6 collects the numeric versions of this transition, the compensation network and the ripple
that rides on top of it.

**Consequence for the level budget.** A section whose passband straddles the step has a 6 dB slope
built into it before any filter is applied. Either the driver's own rising response absorbs it, or
the crossover pays for it with a shelf, which costs sensitivity and dissipates the difference. This
is the same arithmetic as the level budget in `crossover-design.md` section 4, and it is why the
baffle width belongs to the level budget and not only to the cabinet drawing.

## 2. Distance from the driver to each edge

**Physics.** Each baffle edge re-radiates a delayed, partly inverted copy of the driver's output.
The delay is the driver-to-edge distance. Contributions from edges at the same distance arrive
together and reinforce; contributions from edges at different distances arrive spread out and partly
cancel each other. Olson showed the effect of the cabinet's outside shape experimentally and
Vanderkooy gave the edge-source theory that computes it.

**Consequence.** A source centred on a circular baffle is the worst case, because every edge is at
the same distance: Linkwitz reports an on-axis pressure increase of up to 10 dB for that geometry.
A rectangular baffle is already better because the distances differ with direction, and an
off-centre position on a rectangle is better still. The gain is in the flatness of the ripple, not
in its absence.

**Practice, with its reason.** Give each driver a different distance to the nearest edges, and avoid
making two of those distances equal. The usual compromise is to keep every driver on the vertical
centre line, which keeps the horizontal polar response symmetrical, and to accept that the left and
right edges are then equidistant; the vertical distances differ anyway because the drivers sit at
different heights. Moving a driver off the centre line buys smoother diffraction at the cost of an
asymmetrical horizontal pattern. Which matters more is a judgement, and it depends on the driver:
the effect is strongest where the driver is still omnidirectional, so it matters most for a tweeter
and hardly at all for a woofer crossed below the step.

**Edge treatment.** Rounding or chamfering an edge only diffuses the re-radiation when the radius is
an appreciable part of a wavelength. Linkwitz puts the threshold at a radius greater than one eighth
of a wavelength, which makes a 12 mm radius effective only above roughly 3.5 kHz; below that it is
cosmetic. A large radius or a genuine taper is a real acoustic device; a router pass is not.

**A judgement, labelled as one.** Linkwitz's own conclusion is that outside the baffle step region
there is no evidence that even strong diffraction ripple has significant audible consequences.
Treat diffraction as something to keep tidy, not as the thing to optimize at the expense of driver
spacing or the step itself.

## 3. Distance from one driver to the next

**Physics.** Two sources radiating the same signal from points separated by `d` interfere. At an
angle `theta` from the perpendicular bisector of the line joining them, the path difference is
`d sin(theta)`. A complete cancellation requires a path difference of half a wavelength, so a full
null can exist only where `d >= lambda / 2`. Below that the pair still tilts and narrows its lobe,
but it cannot null.

That gives the number to compute before choosing a crossover frequency, not after: with a
centre-to-centre spacing `d`, the frequency above which the pair can null in its plane is
`c / (2d)`. A 300 mm spacing can null above about 570 Hz; a 150 mm spacing above about 1140 Hz.
The smallest spacing two round drivers allow is half of one frame diameter plus half of the other,
plus clearance, so the spacing is set by the driver choice before it is set by the layout.

**Two things make it worse than that bare number.** An acoustic offset between the drivers' centres
adds a frequency-dependent phase difference across the overlap, which tilts the lobe off the design
axis. And the pair keeps interfering above the crossover for as long as both drivers still
contribute, so a shallow acoustic slope widens the damaged band while a steep one narrows it. The
overlap width is part of the spacing decision.

**Symmetry as a partial way out.** D'Appolito's symmetrical arrangement — two identical drivers of
one section placed symmetrically above and below the other section's driver — makes the vertical
pattern symmetrical about the design axis, so the main lobe does not tilt toward the lagging driver.
It does **not** make the crossover's phase behaviour irrelevant: the stronger claim, that such an
arrangement eliminates lobing error and removes the off-axis nulls independently of the interdriver
phase relationship, was put to independent adversarial checks and did not survive them. See
`system-architecture.md` section 8 for that finding and the others in the same cluster. Symmetry also
does not remove the interference itself, and it costs a second driver and its amplifier load; see the
parallel-driver note in `crossover-design.md` section 6.

**What the framework does.** `whole_speaker` places each section at its `x_mm`, `z_mm` and `depth_mm` and
sums coherently with directivity, so the vertical map and the window statistics already contain this
effect; `results.path_differences` reports the acoustic path difference between each pair in
millimetres and microseconds. Nothing computes the spacing rule for you. Compute `c / (2d)` for each
adjacent pair and compare it with the intended crossover before fitting, because a crossover chosen
first will simply be reported as a poor vertical window afterwards.

## 4. Where the array sits relative to the room

**Physics, measured.** Allison measured the power output of a small source against its distance `x`
to a single reflecting boundary, in wavelengths. The gain is about +2.5 dB at `x = 0.1 lambda`, falls
to 0 dB at `x = lambda / 4`, is *below* the free-space value between `lambda / 4` and `lambda / 2`
with a minimum near -1 dB, and is negligible above `lambda / 2`. A boundary has little effect beyond
`0.75 lambda`. The same arithmetic applies to each of the three nearest boundaries.

**The saddle, and the rule that avoids it.** The dip appears because the boundary stops providing
half-space support before the cabinet's own panel starts providing it. Allison's rule follows
directly: the woofer's distance to the boundary must not exceed half the minimum dimension of the
panel it is mounted on, so that the panel takes over before the boundary lets go. A woofer placed
low on a tall front panel, on a cabinet standing on the floor, satisfies this for the floor and fails
it for the side walls, which is usually the right trade.

**The case that is actively bad.** Allison also measured what happens when the panel carrying the
driver faces a nearby boundary: the space between the panel and the wall acts as a conical horn and
loads the driver, producing a large peak in power output. Turning the cabinet so that a *side* faces
the wall gave essentially the true half-space response. So a driver or a radiator on a panel that
will face a wall is a placement decision with a measured penalty, not a neutral choice.

**Midranges are not exempt.** Allison's figure for keeping a midrange clear of a boundary
intersection is a distance of at least `0.75 lambda` at the crossover frequency. Lowering the woofer
crossover to keep the woofer out of trouble pushes the midrange into it.

**Practice.** Put the tweeter near seated ear height, because the vertical window is narrowest where
the drivers are closest together in wavelengths and the listener's height is the one variable the
designer does not control. State the assumed ear height and listening distance with every off-axis
figure.

**What the framework does.** `whole_speaker` takes `observer.ear_height_m` and `distance_m` and can add
a single coherent floor image through its `floor` block; it has no walls, no ceiling and no room. A
free-field result is therefore an incomplete statement about bass, and adding room gain to a modelled
curve to meet an objective is not allowed — see `reference-sensitivity-conventions-differ` in
`framework/learnings`.

## 5. Making a placement claim

A placement is a derivation, like a fit claim in `cabinet-geometry.md`. Before freezing a layout,
write down, for each driver: its frame and cutout diameter, its centre height, its distance to the
nearest two baffle edges, the centre-to-centre spacing to each neighbour and the `c / (2d)` frequency
that spacing implies, its acoustic depth, and its distance to the floor. Then name the crossover
frequencies and say which of those numbers each one has to live with. A layout that was drawn first
and justified afterwards usually shows up as a vertical window figure nobody can explain.

## 6. Numbers for the step, its compensation and the ripple

**Two formulas for the same corner, and they disagree.** Allison's rule in section 1 puts full
half-space support at `c / (2W)` — 380 Hz for a 450 mm panel. A widely used empirical fit puts the
-3 dB point of the step at `f = 115 / W` with `W` in metres (equivalently `380 / W` with `W` in feet),
which is 256 Hz for the same panel; that fit is anchored to a single measured point, Olson's 24-inch
sphere at about 190 Hz. The two are not in conflict so much as they name different points on a
transition that spans roughly a decade. Use whichever you state, and read the computed curve rather
than either number.

**Compensation network.** A first-order shelving network — an inductor `L1` shunted by `R1`, feeding
the driver `R2` — gives the full 6 dB with `R1 = R2 = R`, and `L1 [mH] = W [m] * R [ohm] / 1.021`.
For a 250 mm baffle into 4 ohms that is about 0.98 mH. Note that this network's own corner
(`R / (2 pi L1)`, about 650 Hz for that example) is not the `115 / W` frequency (460 Hz): the two
formulas define the step differently, so simulate the network against the computed baffle response
before cutting parts. Full compensation costs 6 dB of system sensitivity above the step, which goes
into the level budget of `crossover-design.md` section 4.

**Compensating on axis tilts everything else.** The step is 6 dB on axis and zero at 90 degrees off
axis, because it exists only where radiation contracts from full to half space. A network that
flattens the on-axis curve therefore tilts the off-axis and power response the other way.

**How much to apply, as practice rather than physics.** The full 6 dB belongs to a speaker in free
space. In a normal room the walls restore part of the low-frequency support, and the practice figure
is that the realised step is unlikely to exceed about **3 dB** — so a fixed network built for the
full 6 dB will usually over-correct, and designs that expect to be voiced in a room commonly make the
compensation adjustable rather than fixed. This is a rule of thumb from a self-published source, with
no room survey behind it; treat the amount as a voicing decision to state, with the free-space and
in-room endpoints known.

**Ripple magnitudes, from simulation.** A driver centred on a 300 mm square baffle peaks at almost
+9 dB near 1 kHz before settling to the +6 dB asymptote — about 3 dB of overshoot above the step —
and an asymmetric driver offset reduces the residual to about 1.5 dB after compensation. A thin
circular disc, the worst case of section 2, reaches up to +10 dB: a 1.5-inch tweeter on a 3-inch disc
peaks at 4.5 kHz and at odd multiples of it, with nulls at the even multiples. All of these are
simulated examples at one geometry each, not measurements, and they scale with baffle dimension.

**Where the baffle stops mattering.** Square baffles of 3, 6 and 12 inches give essentially the same
response above about 6 kHz, and above roughly 14 kHz baffle size has no effect at all. Read that as
"overall width no longer sets the response", not as "diffraction has stopped": local geometry close to
the tweeter — a sub-baffle, a faceplate edge, a surround step — still matters well above 6 kHz.

**The step depends on measurement distance.** A 250 mm baffle shows only about 5 dB of step at a
0.25 m microphone distance against 6 dB in the far field. A correction derived from a close
measurement therefore under-compensates what a listener at 3 m hears, and a quoted step magnitude
without its distance is incomplete.

**What the framework does, and what is not known about it.** `baffle_diffraction` computes a finite-
baffle shelf and an edge-diffraction factor per source position. No source consulted gives a measured
validation of any baffle-diffraction simulator against a real cabinet, so the ripple magnitudes above
and the ones the application reports carry no published error bar. Treat them as the right shape and
the right order of magnitude, and do not voice a design against ripple detail that no measurement has
confirmed.

## Sources

- Allison, R. F., "The Influence of Room Boundaries on Loudspeaker Power Output", *Journal of the Audio Engineering Society*, vol. 22, no. 5, pp. 314-320, 1974 — the boundary curves, the saddle, the half-panel-dimension rule, the panel-facing-a-wall case and the 0.75 lambda midrange figure. <https://aes2.org/publications/elibrary-page/?id=2760>
- Olson, H. F., "Direct Radiator Loudspeaker Enclosures", *Journal of the Audio Engineering Society*, vol. 17, no. 1, pp. 22-29, 1969 — the measured effect of cabinet outside shape on response.
- Vanderkooy, J., "A Simple Theory of Cabinet Edge Diffraction", *Journal of the Audio Engineering Society*, vol. 39, no. 12, pp. 923-933, 1991 — the edge-source theory the diffraction model rests on. <https://aes2.org/publications/elibrary-page/?id=5952>
- Linkwitz, S., "Diffraction from baffle edges" — magnitudes, the circular-baffle worst case, the one-eighth-wavelength rounding threshold, and the author's judgement on audibility. <https://www.linkwitzlab.com/diffraction.htm>
- D'Appolito, J. A., "A Geometric Approach to Eliminating Lobing Error in Multiway Loudspeakers", AES 74th Convention, preprint 2000, 1983 — the symmetrical arrangement. <https://aes2.org/publications/elibrary-page/?id=11762>
- Elliott, R., "Baffle Step Compensation", Elliott Sound Products - the `115 / W` step frequency in both unit systems and the practice figure that the step realised in a normal room is unlikely to exceed 3 dB. <https://sound-au.com/bafflestep.htm>
- "Diffraction and Baffle Step", True Audio - the `115 / W` step fit, its anchoring to Olson's sphere measurement, and the shelving-network component formula. <https://www.trueaudio.com/st_diff1.htm>
- Tolvan Data, *The Edge* documentation - the image-source diffraction formulation, the simulated ripple magnitudes for square and offset geometries, and the measurement-distance dependence of the step. <https://www.tolvan.com/edge/help.htm>
- Toole, F. E., *Sound Reproduction: The Acoustics and Psychoacoustics of Loudspeakers and Rooms*, 3rd ed., Routledge, 2017 — the standing treatment of directivity, reflections and listening geometry.
- In this repository: `simulations/baffle_diffraction/README.md` for the input contract and what the factor contains, `simulations/whole_speaker/README.md` for the placement frame and the window and path-difference statistics, and `references/cabinet-geometry.md` for the coordinate systems and the fit derivation those positions also have to satisfy.
