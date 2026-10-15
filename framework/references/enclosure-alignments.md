---
id: enclosure-alignments
applies_when: Choosing or solving a bass alignment, sizing a vent, judging a port speed or a tuning claim, or considering a loading other than sealed and vented
updated: 2026-09-15
---

# Bass alignments and the loadings that produce them

The box is where a driver's parameters become a response. This reference holds the alignment
mathematics for the two loadings the framework simulates, the vent design that a vented alignment is
only half of, and what is and is not known here about the loadings it does not simulate. Passive
radiators have their own reference; the driver parameters that feed all of this have theirs.

## 1. The vented alignment is solved, not looked up

**Physics.** For target fourth-order coefficients `a1, a2, a3` and a chosen enclosure loss `QL`,
Small's lossy alignment recipe is a closed procedure:

```
c1 = a1 QL          c2 = a3 QL
solve   r^4 - c1 r^3 + c2 r - 1 = 0    for the physical positive real root r
h = r^2
f3 / fS = sqrt(h) * (f3 / f0)
alpha   = a2 h - h^2 - 1 - (1 / QL^2) (a3 sqrt(h) QL - 1)
QT      = h QL / (a3 sqrt(h) QL - 1)
```

with `alpha = Vas / VB` the compliance ratio and `h = fB / fS` the tuning ratio. As `QL` tends to
infinity these reduce to Thiele's lossless forms `h = a3 / a1`, `alpha = a2 h - h^2 - 1` and
`QT = 1 / sqrt(a1 a3)`.

Prototype coefficients:

| Alignment | `a1` | `a2` | `a3` | `f3 / f0` |
|---|---|---|---|---|
| B4 (Butterworth) | 2.6131 | 3.4142 | 2.6131 | 1.0000 |
| BL4 (Bessel) | 3.20108 | 4.39155 | 3.12394 | 1.5143 |
| QB3 | `sqrt(2 a2)` | free, `> 2 + sqrt(2)` | `(a2^2 + 2) / (2 a1)` | from the family |

The quartic has several positive real roots — at `QL = 7` they are 0.0548, 1.0000 and 18.237 — and
only the one near unity is physical. Small's own wording ("the positive real root") is loose; a
solver has to pick deliberately.

**Why this matters more than a table.** A table of alignments is a table at one `QL`. Losses move
every number in it, and the recipe above is how a design gets the tuning, the volume and the required
`QT` that its actual losses imply rather than the ones a lossless table promised.

## 2. Losses, and where the `QL = 7` default comes from

**Physics, with measured values.** Small separates the three loss mechanisms and combines them at
`fB` as `1/QB = 1/QL + 1/QA + 1/QP`:

- **Vent losses** `QP`: 50 to 100 unobstructed, and "with reasonable care in design" need not fall
  below 20 even when obstructed by grille cloth or lining.
- **Absorption losses** `QA`: 100 or more in an unlined enclosure, 30 to 80 with typical wall lining,
  lower still with very thick lining or damping partitions.
- **Leakage losses** `QL`: 5 to 20, and dominant.

All three can be lumped into one frequency-invariant leakage resistance whose `QL` equals the total
measured `QB`. Small is explicit that this is a measurement-equivalent fit rather than a physical
claim: vent losses rise with frequency and absorption losses fall with it, and both show up in the
measurement as apparent leakage.

**Practice, with its reason.** Measured `QB` in real cabinets clustered at 5 to 10, which is why
`QL = 7` is the usual design default — it is Small's own mid-range alignment chart, not an outside
convention. The figure comes from 1973 measurements of then-current commercial cabinets, so it is
measured practice of that era rather than physics.

## 3. The ceiling on a vented box

**Physics.** The lossless efficiency-bandwidth-volume limit is

```
eta_0(max) = 3.9e-6 * f3^3 * VB          (f3 in Hz, VB in m^3)
```

occurring near a compliance ratio `alpha = 0.6`. Any real box of a given `VB` and `f3` must fall
below it. Fifty litres at `f3 = 40 Hz` gives 1.25 percent, about a 93 dB/2.83 V/m ceiling — and Small
notes that typical real systems land 2 to 3 dB (40 to 50 percent) below the limit because of driver
mechanical losses, finite `QL` and non-optimal alignments.

This is the number to compute **before** promising a sensitivity at a given extension in a given
cabinet size. It settles that argument in one line, and it is the vented-box counterpart of the
efficiency law in `driver-selection.md` section 1.

## 4. The vent is half the alignment

**Physics.** Small derived a minimum vent area by limiting peak vent velocity at maximum rated
programme power to 4.5 percent of the speed of sound:

```
SV >= 0.8 * fB * VD        (SV in m^2, fB in Hz, VD in m^3)
dV >= sqrt(fB * VD)        (circular vent, dV in metres)
```

accurate within +/-10 percent across the whole C4-B4-QB3 range. Small states it "should be regarded
as a general guide only, not as a rigid rule", because vent noise also depends on edge geometry and
because the annoyance is subjective. The underlying experimental limit is about 5 percent of the
speed of sound *provided the vent is smooth and the edges are rounded with a reasonable radius* —
the proviso is part of the number.

**What actually sets the onset of trouble.** The JBL/Infinity port study found that compression
correlates with Reynolds number rather than with any single geometry: three deliberately different
subwoofers, differing in port shape, count, area, box volume and tuning, produced nearly identical
compression curves, all degrading near `Re = 50,000` and reaching a wall by about 100,000. These are empirical indicators for the tested designs and conditions, not universal noise/compression acceptance limits; oscillatory displacement, edge shape and flare also affect the result. The
legacy practice of limiting port velocity to about 10 m/s is corroborated by hot-wire measurement of
the jet-formation transition.

**Carry both thresholds; they are not interchangeable.** Since `Re = rho v D / mu`, 10 m/s is
`Re ~ 67,000` only in a 100 mm port. In a 50 mm port, 10 m/s is only `Re ~ 33,000`, while
`Re = 50,000` needs about 15 m/s. Small ports tolerate higher velocity than the flat 10 m/s rule
implies, and large ports less.

**Flares, quantitatively.** Define the normalised flare rate `NFR = port_length / (2 * flare_radius)`.
Then

```
f = (c / 2 pi) sqrt( Aeff / (Leff VB) )     with   Aeff = (1 + 0.576 NFR) Amin,   Leff = Lact + Dmin
```

where `Amin` and `Dmin` are the **throat** area and diameter, not the mouth — the conventional
mouth-radius end correction overestimates the reactive air mass. The fit has `r^2 = 0.98` and
predicted tuning within 2 percent for the six test ports and within 5 percent for other profiles.

`NFR ~ 0.5` is the best single flare rate across level: near 1.0 gives the lowest distortion at low
SPL, near 0.5 at moderate SPL, near 0 at very high SPL — and the high-SPL recommendation still
assumes the edge radius below. Every port measured showed about 10 dB of compression at tuning at
40 V drive, and the straight port started about 2 dB lower in output than any flared one.

**Edge radius is not cosmetic.** Every port edge should carry a blend radius of at least 20 percent of
the minimum diameter. This is the textbook entrance-loss coefficient: `K ~ 0.05` for `r/D >= 0.2`
against `K = 0.5` for a square edge. Both ends count, because an audio signal is oscillating and
therefore both ends are entrances.

**What the framework does.** `lf_box` reports `max_port_air_speed_peak_ms` and
`results.vent.physical_length_mm` for a straight round duct with an end correction. It does not model
flares, bends or slots, does not compute a Reynolds number, and does not model port compression or
noise at all. A flared or bent duct's tuning is an estimate to flag, and a port-speed figure is a
linear prediction — the 10 dB of compression measured at high drive is not in it.

## 5. Loadings the framework does not simulate

Everything in this section is thinner than the material above: it comes from single sources, mostly
secondary or self-published, and none of it was adversarially verified. It is here so that a decision
to use one of these loadings starts from the right equations and the right doubts, not so that a
design can be committed from this page.

**Horn loading.** For an exponential flare `S = St e^(m x)`, the throat impedance is
`zA = (rho0 c / St) [ sqrt(1 - m^2/(4 k^2)) + j m / (2k) ]`, with cutoff at `m = 2k`, that is
`fc = m c / (4 pi)`. Below `fc` the throat resistance of the infinite horn is zero and the horn stops
loading the diaphragm — an idealisation that a real finite horn softens, but the design consequence
(place `fc` safely below the passband) stands. The hyperbolic-exponential family
`S = St [cosh(x/x0) + T sinh(x/x0)]^2`, `x0 = c / (2 pi fc)`, gives the exponential at `T = 1` and the
conical as `T` grows; `0.5 < T < 1` is the useful range when loading is the goal. A conical flare
loads far worse: in the one worked comparison available, the exponential horn reached 80 percent of
its asymptotic throat resistance at 270 Hz where the conical horn needed about 1200 Hz.

Mouth size is set by the dimensionless `k rm` at cutoff, and the sources disagree: `k rm = 0.93`
under a plane-wave assumption against 1.4 under a spherical-wave assumption, a factor of 1.5 in mouth
radius and 2.3 in area. Practice quoted is `k rm` of 0.7 to 1 for bass horns and `>= 1` for midrange
and treble horns. **Keele's Thiele/Small horn design equations — throat area, rear cavity volume,
bandwidth and maximum acoustic output from `fs`, `Qts`, `Vas`, `Sd` — were not obtained**; the paper
is paywalled. Treat horn bass loading as unsupported here beyond the flare mathematics above.

**Transmission line / quarter wave.** Never use `L = c / (4 fb)` for a tapered line. Scale by the
taper factor `SF` against taper ratio `TR = S_terminus / S_throat`: 0.1 -> 0.62, 0.2 -> 0.71,
0.33 -> 0.80, 0.5 -> 0.87, 1.0 -> 1.00, 2.0 -> 1.14, 3.0 -> 1.22, 5.0 -> 1.32, 10.0 -> 1.42.
Stuffing slows propagation: measured 342 m/s unstuffed falling to about 319 m/s, an asymptote reached
by about 0.6 lb/ft^3, so a stuffed line tunes lower than an unstuffed length calculation predicts.
The same source's own conclusion is the important one: **at equal volume and equal tuning a
transmission line gives no deeper bass than a reflex box**; choose it for cone-displacement control
and low terminus velocity, offset the driver along the line to suppress the three-quarter-wave mode,
and taper it so residual standing waves move up to where fibre damping works. All of this rests on
one self-published modelling site, and its advantages are asserted without numbers.

**Open baffle and dipole.** Output falls at 6 dB/octave below the equivalence frequency
`f = 0.17 v / D`, where `D` is the front-to-back acoustic path, so a 0.5 m path puts it near 117 Hz.
Excursion rises at 18 dB/octave rather than the monopole's 12, so one octave lower at constant SPL
costs **eight times** the volume displacement — the dominant fact in dipole woofer sizing. The
pattern is `cos(theta)` with nulls at +/-90 degrees, about 1 dB down at 30, 3 dB at 45 and 6 dB at
60 degrees, and a dipole radiates about 4.8 dB less power than a monopole for the same on-axis SPL.
An H-frame or U-frame cavity resonates at `F = 0.25 v / L` with `L` the cavity depth, which caps the
usable band; no source here states how far below it to cross.

**Not covered at all.** Bandpass enclosures of any order, isobaric or compound loading, aperiodic and
resistively vented boxes, cardioid and other controlled-directivity hybrids, and folded, back-loaded
or tapped horns. Nothing in this repository has researched them, and nothing in `lf_box` models them.
Do not infer their behaviour from the sections above.

## 6. What the framework models

`lf_box` covers sealed, vented and passive-radiator loadings as lumped systems at a stated drive
voltage, reporting cutoffs, excursion, port speed and voltage-to-limit scaling. There is no
transmission-line model, no horn loading, no bandpass and no dipole. `lf_uncertainty` sweeps the
lumped model over parameter and build tolerance. Nothing models nonlinearity, port compression,
thermal behaviour or the box's own mechanical noise. See `simulations/lf_box/README.md` and
`simulations/lf_uncertainty/README.md`.

## 7. Making an alignment claim

State the loading, the net volume the alignment assumes and the objects subtracted to reach it, the
tuning and the `QL` it was solved at, the resulting `QT` against the driver's actual `Qts`, the
efficiency against the section 3 ceiling, and the excursion and port speed at the project's stress
drive with the drive condition named. An alignment quoted without its `QL` and its net volume is not
reproducible, and an alignment whose vent fails section 4 is a design that will be audible before it
is measurable.

## Sources

- Small, R. H., "Vented-Box Loudspeaker Systems, Parts I to IV", *Journal of the Audio Engineering Society*, vol. 21, nos. 5-8, 1973 — the lossy alignment recipe and its prototype coefficients, the loss decomposition and measured `QP`/`QA`/`QL` ranges, the efficiency limit, and the minimum vent-area rule with its 4.5-percent-of-`c` derivation. <https://sdlabo.jp/archives/Vented_Box_Loudspeaker%20Systems_Part_1-4.pdf>
- Thiele, A. N., "Loudspeakers in Vented Boxes, Parts I and II", *Journal of the Audio Engineering Society*, vol. 19, nos. 5 and 6, 1971 — the lossless alignment families the lossy recipe reduces to.
- Salvatti, A., Button, D. J., Devantier, A., "Maximizing Performance from Loudspeaker Ports", *Journal of the Audio Engineering Society*, vol. 50, no. 1/2, pp. 19-45, 2002 — the Reynolds-number compression result, the normalised flare rate and its tuning fit, the flare-rate optimum against level, and the 0.2-diameter edge-radius rule. <http://jahonen.kapsi.fi/Audio/Papers/AES_PortPaper.pdf>
- Kolbrek, B., "Horn Theory: An Introduction", *audioXpress* — exponential, hypex, conical and tractrix flare mathematics, the `k rm` mouth criterion and its two competing optima, and the air-nonlinearity distortion term. <https://audioxpress.com/assets/upload/files/kolbrek2884.pdf>
- Keele, D. B., Jr., "Low-Frequency Horn Design Using Thiele/Small Driver Parameters", AES 57th Convention, preprint 1250, 1977 — named here as the retrieval target for horn design from driver parameters; the equations were **not** obtained and nothing in this reference stands on them. <https://dbkeele.com/11-low-frequency-horn-design-using-thiele-small-driver-parameters/>
- Augspurger, G. L., quarter-wave modelling as published at quarter-wave.com — the taper-factor length table, stuffing density practice, the measured speed-of-sound reduction in stuffed lines, and the equal-volume comparison with a reflex box. Self-published, not peer reviewed. <http://www.quarter-wave.com/TLs/TL_Theory.html>
- Linkwitz, S., "Models and modelling of dipole loudspeakers" — the dipole equivalence frequency, the 18 dB/octave excursion law, the `cos(theta)` pattern and the H-frame cavity resonance. <https://www.linkwitzlab.com/models.htm>
- In this repository: `simulations/lf_box/README.md` for the loadings actually modelled and the duct model's limits, `references/passive-radiators.md` for radiator sizing and tuning, `references/driver-selection.md` for the parameters and displacement limits these alignments consume, and `references/cabinet-geometry.md` for turning a net volume into a buildable box.
