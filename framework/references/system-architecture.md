---
id: system-architecture
applies_when: Deciding how many sections a design needs, where the crossover frequencies go, how much acoustic offset the geometry implies, and what directivity the section boundaries have to deliver
updated: 2026-09-15
---

# How many sections, and where the crossovers go

Two-way, three-way or four-way is not a style choice. It follows from how far up each driver can be
used before its pattern collapses, how far down the next one can be used before it runs out of
excursion or gets too close to its own resonance, and how close together the two can physically be
mounted. Those three constraints decide the crossover frequencies, and the crossover frequencies
decide the section count. A layout drawn first and justified afterwards reappears later as a vertical
window figure nobody can explain.

## 1. The ceiling on each driver: `ka`

**Physics.** For a rigid circular piston in a baffle, the far-field pattern depends only on the
dimensionless product `ka = 2 pi f a / c` with `a` the piston radius. Directivity narrows
monotonically as `ka` rises: near `ka = 1` the radiation is still broad, and at `ka` much greater
than 1 the main lobe is confined to roughly +/-20 degrees with side lobes that radiate **in opposite
acoustic phase** to the main lobe. That phase reversal is the reason to take the ceiling seriously —
crossing a driver over above it does not merely lose level off axis, it inverts the off-axis
contribution and destroys the summation the crossover was designed for.

**Three criteria, which do not agree.** The sources offer:

- `ka < 5` as a typical upper limit per driver, that is `f_max = 5 c / (2 pi a)`. One commercial
  four-way holds `ka = 5.5` at every section boundary — 30 cm woofer to 2 kHz, 12 cm mid to 5 kHz,
  6 cm tweeter to 10 kHz, 3 cm super-tweeter to 20 kHz, each halving of diameter roughly doubling the
  crossover frequency.
- "One wavelength equals the cone diameter", `f_max = c / d`, which for a 150 mm driver gives about
  2.3 kHz.
- About one decade (roughly 3.2 octaves) of passband per driver.

For a 150 mm driver these give roughly 4.7 kHz, 2.3 kHz and a bandwidth rather than a frequency. The
`c / d` heuristic is about an octave more conservative than `ka = 5`, and none of the three has a
stated criterion behind it — not a beamwidth, not a directivity index, not a distortion figure.
Choose one, say which you chose, and check the result against a computed pattern rather than trusting
the rule of thumb.

**Use the radiating radius, not the frame.** `a` is the piston-equivalent radius from `Sd`, which sits
between the cone neck and the frame. And the whole family assumes pistonic behaviour: above break-up
the pattern is not a piston's at all, so the ceiling has to be checked against the driver's measured
response, not only against its diameter.

## 2. The floor on the driver above

The upper driver's lower limit is set by its own resonance, its excursion and the protection the
filter gives it. HF drivers have no mechanical self-protection — their suspensions show no
progressive stiffness rise inside the working range — so the high-pass is the excursion limit; see
`driver-selection.md` section 5. One fetched source gives a floor of 2.5 times `fs` for a
first-order network, with nothing stated for higher orders, and the commonly cited "two to three
times `fs`" rule has **no numeric source here**. Treat the margin as a judgement you state and
defend, not as a rule this reference supplies.

## 3. Where the two can be mounted, and what that costs

**Physics.** Two sources separated by `d1`, radiating the same signal, produce a total phase
difference at an off-axis angle `alpha` of

```
delta_phi = phi_H - phi_L + 360 deg * (d1 / lambda) * sin(alpha)
```

which adds at multiples of 360 degrees and cancels at odd multiples of 180. Linkwitz's design bound
is `d1 / lambda < 1` at the crossover frequency, that is `fc < c / d1`; above it the pattern breaks
into multiple beams. A 10-inch woofer beside a 4-inch tweeter cannot be mounted closer than about
7 inches centre to centre, which puts `d1 / lambda = 1` at 1.7 kHz.

**`d1 / lambda < 1` is an upper bound, not a target.** At exactly one wavelength the pattern is
already badly compromised. Linkwitz tabulates the vertical behaviour at that spacing, at the
crossover frequency, with no depth offset:

| Alignment | level each | relative phase | main lobe | peak | cancellations |
|---|---|---|---|---|---|
| Constant voltage (1st order) | 0 dB | 120 deg | -20 deg | +6 dB | +10 deg, -56 deg |
| 3rd-order Butterworth (allpass) | -3 dB | 90 deg | -15 deg | +3 dB | +15 deg, -49 deg |
| 2nd-order Butterworth | -3 dB | 0 deg | 0 deg | +3 dB | +/-30 deg |

The message is the relative-phase column: an alignment whose branches are mutually in phase keeps the
main lobe on the design axis, and one whose branches are not tilts it toward the lagging driver. The
companion rule — the frequency `c / (2 d)` above which a pair can null at all — is in
`baffle-and-driver-placement.md` section 3, and should be computed for every adjacent pair before a
crossover frequency is chosen.

## 4. Linkwitz's three conditions

A crossover pair that preserves the pattern through the transition has to satisfy all three
simultaneously, stated on the **acoustic** responses and not on the electrical filter:

1. zero phase difference between the two branches at `fc`, or the pattern tilts;
2. each branch exactly -6 dB at `fc`, so the sum is unity with no peak or dip;
3. a frequency-independent phase difference — equal group delay — so the pattern stays symmetrical
   above and below `fc`.

A cascade of two identical Butterworth sections (Linkwitz-Riley) is the realisation that meets all
three. Condition 1 presumes the acoustic centres are at the same depth or have been aligned, which
section 5 is about, and all three presume the driver's own rolloff, the baffle step and the
diffraction are inside the branch response being shaped. An electrical LR4 network into a real driver
does not produce an acoustic LR4 sum.

## 5. Acoustic-centre offset is the dominant phase error

**Physics.** A depth offset `d2` between two acoustic centres separated vertically by `d1` tilts the
main lobe by `beta = arctan(d2 / d1)`. A 3-inch offset with a 7-inch spacing is a 23-degree tilt.
Correcting it electrically needs a pure delay `t = d2 / c`, which for 3 inches is about 240
microseconds.

**Why this matters more in a passive design than in an active one.** A first-order allpass stage can
supply only about `1 / (10 fc)` of usable delay if its pole is kept at or above `3 fc`, so 240
microseconds at a 1.7 kHz crossover needs four cascaded stages. A passive network cannot generally
supply that at all. In a passive design the offset is therefore handled **mechanically** — a stepped
or sloped baffle, a recessed tweeter, an asymmetric crossover order — or accepted as lobe tilt and
stated.

**Scale.** Typical flat-baffle offsets are quoted at 25 to 50 mm, that is 70 to 145 microseconds. A
pure delay's phase error grows linearly with frequency: 145 microseconds is half a period at
3450 Hz, so 180 degrees there, 90 degrees an octave below. Two equal sources with that offset are
already 3 dB down an octave below their first null, so a crossover placed comfortably under the null
frequency is not automatically safe.

## 6. Group delay: a budget, with a caveat about its source

Published minimum audible group delay, attributed to Blauert and Laws, is about 3.2 ms at 500 Hz,
2 ms at 1 kHz, **1 ms at 2 kHz (the worst case)**, 1.5 ms at 4 kHz and 2 ms at 8 kHz. Against that,
the group delay of common topologies at a 1.59 kHz crossover is 100 microseconds (first order),
200 (LR2), 240 (2nd-order Butterworth), 480 (LR4) and under 1 microsecond (first-order subtractive) —
every one of them an order of magnitude or so below the threshold.

**Two cautions.** These thresholds reach this reference through a secondary citation, and a more
recent implementation notes that its group-delay audibility curve is a confidence limit only over
500-4000 Hz and extrapolated outside it. And filter group delay scales roughly as `1 / fc`, so an LR4
at 300 Hz is around 2.5 ms and can approach the low-frequency thresholds — recompute, do not reuse
the table.

**The design consequence is the ranking, not the numbers.** Crossover topology is not where a passive
design's phase budget is spent; acoustic-centre offset is. Spend the effort there.

## 7. Directivity across the boundary

The point of matching sections at the crossover is that the pattern should not step. A directivity
index with a step or a dip at a crossover frequency is the signature of two drivers whose coverage
did not match there — a driver-size and spacing problem, not a filter problem.

The only hard numeric envelopes available here come from the broadcast monitor standards, and they
disagree with each other:

- **ITU-R BS.1116-3**: directivity index between 6 and 12 dB over 500 Hz to 10 kHz, rising smoothly.
- **EBU Tech 3276**: between 4 and 12 dB over 250 Hz to 16 kHz, radiation maximum on the main axis at
  all frequencies.
- Both: off-axis response within 3 dB of on-axis anywhere inside +/-10 degrees, and within 4 dB at
  +/-30 degrees horizontally, in third-octave bands.

Neither defines the integration method for the directivity index, which materially changes the value,
and the 12 dB ceiling excludes typical constant-directivity PA horns from qualifying as reference
monitors. Use them as the design window for a monitor, cite which document, and see
`target-response.md` for the preference-model view of the same question.

## 8. Claims this reference will not support

Four assertions in this area were put to independent adversarial checks and **refuted**; they are
recorded here so they are not reintroduced:

- that a symmetric arrangement (a pair of drivers flanking a central tweeter) eliminates vertical
  lobing error *independently of the interdriver phase relationship*, and that it removes the
  off-axis nulls an offset two-driver layout produces even when the branches are not in phase. The
  geometry makes the vertical pattern symmetric about the design axis; it does not make the crossover
  phase irrelevant;
- that crossover filters which are in phase with each other leave the system radiation pattern and
  directivity index unchanged;
- that a coaxial arrangement needs no interdriver delay correction.

A fifth, that the overlap band between adjacent drivers should not exceed two octaves, survived but
with **low confidence**: it is asserted as practice with no derivation or measurement, in a paper
about a digital FIR crossover, so it transfers to passive design only with that caveat attached.

## 9. What the framework computes

`directivity` gives piston, horn, ribbon and tabulated patterns and their -6 dB beamwidths, which is
where the `ka` question is answered numerically for a chosen radius. `whole_speaker` sums the sections
at their positions and depths, so lobe tilt, the vertical window and the path differences between
pairs are in its output; `results.path_differences` reports each pair in millimetres and
microseconds. Nothing computes the section count, the crossover frequency or the `ka` ceiling for
you, and nothing here produces a directivity index, so a DI claim against section 7 cannot currently
be made from these results — say so rather than implying one. See `simulations/directivity/README.md`
and `simulations/whole_speaker/README.md`.

## 10. Making an architecture claim

Before the first crossover frequency is chosen, write down for each driver: its piston-equivalent
radius and the frequency its chosen `ka` ceiling implies, the floor set by its resonance and
excursion, the smallest achievable centre-to-centre spacing to its neighbour and both the
`c / d1` and `c / (2 d)` frequencies that follow, and the acoustic depth offset the mounting implies
with the lobe tilt it produces. The section count is what is left when those intervals have to cover
the band. A design that cannot cover the band with the sections it has is a finding about the driver
complement, and the crossover will not repair it.

## Sources

- Linkwitz, S. H., "Active Crossover Networks for Noncoincident Drivers", *Journal of the Audio Engineering Society*, vol. 24, no. 1, pp. 2-8, 1976 — the three crossover conditions, the two-source interference geometry, the `d1 / lambda < 1` bound, the lobe/peak/null table and the acoustic-offset tilt and delay budget. <https://www.linkwitzlab.com/JAES/jaes_papers76.htm>
- Russell, D. A., "Radiation from a Baffled Circular Piston", Pennsylvania State University Acoustics — the `ka` parameterisation, the narrowing of the pattern with `ka`, the opposite-phase side lobes and the constant-`ka` section-boundary example. <https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html>
- Blauert, J., and Laws, P., "Group Delay Distortions in Electroacoustical Systems", *Journal of the Acoustical Society of America*, vol. 63, no. 5, pp. 1478-1483, 1978 — the audibility thresholds quoted in section 6, which reach this reference through a secondary citation and were not read at source.
- Elliott, R., "Phase, Time and Distortion in Loudspeakers", Elliott Sound Products — the crossover group-delay table, the acoustic-offset scale and the comb-filter consequence. <https://sound-au.com/ptd.htm>
- ITU-R BS.1116-3, *Methods for the subjective assessment of small impairments in audio systems*, 2015, and EBU Tech 3276, *Listening conditions for the assessment of sound programme material* — the directivity-index windows and the off-axis tolerances in section 7, including their disagreement. <https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1116-3-201502-I!!PDF-E.pdf> and <https://tech.ebu.ch/docs/tech/tech3276.pdf>
- D'Appolito, J. A., "A Geometric Approach to Eliminating Lobing Error in Multiway Loudspeakers", AES 74th Convention, preprint 2000, 1983 — the symmetric arrangement, cited here together with the section 8 finding that its phase-independence claim did not survive verification. <https://aes2.org/publications/elibrary-page/?id=11762>
- In this repository: `references/baffle-and-driver-placement.md` for spacing, edge distance and room boundaries, `references/crossover-design.md` for realising these targets in a network, `references/target-response.md` for judging the resulting family of curves, and `simulations/directivity/README.md` for the patterns the `ka` decision should be checked against.
