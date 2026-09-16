---
id: driver-selection
applies_when: Choosing a driver from its published parameters, judging whether a sensitivity or output claim is reachable, reading an Xmax or power figure, or deciding how much to trust a parameter set
updated: 2026-09-15
---

# Choosing a driver from its parameters

Almost every constraint a finished loudspeaker lives with is decided when the drivers are chosen. The
box changes the alignment; it does not change the efficiency the driver is capable of, the excursion
it has, or the output it can produce before it stops behaving linearly. This reference is the
arithmetic that turns a datasheet into those limits, and the warnings that say how much of the
datasheet to believe.

## 1. Efficiency is fixed by three parameters

**Physics.** Small's reference efficiency of a direct radiator in half space is

```
eta_0 = (4 pi^2 / c^3) * fs^3 * Vas / Qes
```

with the constant evaluating to `9.6e-7` in SI units (`Vas` in cubic metres), `9.6e-10` for `Vas` in
litres and `2.7e-8` for `Vas` in cubic feet. The litre constant carries an implicit `c = 345 m/s`;
other authoritative renderings of the same formula use 343 or 346 m/s and differ by about 2 percent,
which is the speed of sound and not a disagreement about the physics.

This is the efficiency-bandwidth-volume trade — Hofmann's Iron Law — in its quantitative form.
Efficiency rises with the **cube** of resonance frequency and only linearly with compliance volume,
so a driver that goes an octave lower at the same `Vas` and `Qes` gives up 9 dB. There are three
knobs and you may have any two: low cutoff, small box, high sensitivity.

Small's value is twice Thiele's because Thiele assumed a full-space radiation load and Small assumed
half space; the piston radiation resistance differs by exactly a factor of two between them. When
comparing a computed efficiency with a published one, establish which load the publisher assumed
before concluding anything.

**Two ceilings above it.** Keele retained the radiation-impedance terms that the standard lumped
analysis drops and found the maximum power-transfer efficiency of a direct radiator to be **25
percent**, under the nominal (`E^2/Re`-referenced) efficiency convention that direct-radiator
analysis conventionally uses. The figure is a bound and not a design formula. At low frequencies the
achievable nominal efficiency is proportional to cone diameter, and at a fixed diameter depends only
on the ratio of moving mass to air-load mass. Real reference efficiencies land of the order of one
percent.

**A refuted claim, recorded so it is not repeated.** The related assertion that the Thiele/Small
analysis "systematically misses air-load effects in box simulations" did not survive verification.
The lumped model's omission of radiation impedance bounds a maximum-efficiency question; it does not
invalidate box simulation.

## 2. Total Q sets the shape of the bass, numerically

For the second-order high-pass `G(s) = s^2 Ts^2 / (s^2 Ts^2 + s Ts / Qt + 1)`, peaking depends on `Qt`
alone and is exactly `Qt / sqrt(1 - 1/(4 Qt^2))`:

| `Qt` | passband peak | `f3 / fc` |
|---|---|---|
| 0.5 (critical damping) | none | 1.554 |
| 0.707 (Butterworth, maximally flat) | 0.0 dB | 1.000 |
| 1.0 | 1.25 dB | 0.786 |
| 1.4 | 3.5 dB | 0.709 |
| 2.0 | 6.3 dB | 0.674 |

Every increase in peaking buys bandwidth: `Qt = 2` reaches a third of an octave lower than
Butterworth and pays 6.3 dB of hump for it. That trade is the one being made whenever a sealed
alignment is described as "extended" or "tight", and the numbers above are what the words are worth.

## 3. Excursion decides the output, and the arithmetic is closed

**Physics.** Peak displacement volume is `VD = SD * xmax` with `xmax` the peak linear displacement.
Small's displacement-limited acoustic power rating is

```
P_AR = (4 pi^3 rho0 / c) * fs^4 * VD^2 / (kx^2 |X(jw)|max^2)
```

with `4 pi^3 rho0 / c = 0.42` in SI units. For the vented box this reduces to a form that is far
more useful in practice:

```
P_AR = kP * f3^4 * VD^2       watts acoustic, into 2 pi
P_ER = (kP / k_eta) * f3 * VD^2 / VB
```

Small recommends `kP = 3.0` for normal programme material regardless of alignment. Read the
qualification with the number: his own figures show `kP` spanning roughly 0.3 to 5 across the
C4/B4/QB3 families and between passband-limited and wideband drive, the rating assumes programme
that does not drive the system hard below cutoff, and it is vulnerable to subsonic content.

**A worked example to calibrate intuition.** A 12-inch driver with an effective radius of 0.12 m,
+/-4 mm peak displacement (`VD = 0.18 dm^3`), `fs = 50 Hz` in a Butterworth sealed alignment at
`QT = 0.71` gives `P_AR = 0.086 W` acoustic, which is 101.4 dB at 1 m in half space, from `P_ER = 5 W`
electrical at `eta_0 = 1.7 %`. Small himself calls those conservative and suggests 10 W and 0.17 W
are more realistic with an amplifier of 30 Hz power bandwidth. The lesson is the order of magnitude:
a fraction of a watt of acoustic power is a loud loudspeaker, and displacement, not amplifier power,
is what runs out first in the bass.

## 4. What Xmax means, and why two datasheets disagree

This is the single least trustworthy number on a datasheet, and the standard that most datasheets
still quote is the one its own critics describe as giving "multiple or infinite values".

**AES2-1984** defines Xmax as the peak displacement at which motor linearity deviates by 10 percent,
measured in free air at `fs`, by either percent distortion of the input current or percent deviation
of displacement against current, with the manufacturer required to state the method. Klippel's four
objections are worth repeating exactly: it gives no clear definition, it gives multiple or infinite
values, it considers suspension nonlinearity only, and it fails at assessing motor linearity. For one
simulated driver with a 5 mm coil height the current-THD criterion gives about 0.6 mm, the
displacement-THD criterion never reaches 10 percent at all, and the pressure-THD criterion yields
three simultaneous answers at 1.5, 8 and 13.5 mm. Always cite this as the **1984** standard.

**IEC 62458 replaces it with two workable definitions.** The performance-based one: the peak
displacement at which either the total harmonic distortion `dt` or the `n`-th order modulation
distortion (`n = 2` or 3) first exceeds 10 percent in the radiated pressure, in free air, under two
tones at `f1 = fs` and `f2 = 8.5 fs` with amplitude ratio 4:1, where

```
dt = sqrt( P(2f1)^2 + P(3f1)^2 + ... + P(Kf1)^2 ) / Pt * 100 %
d2 = [ P(f2 - f1) + P(f2 + f1) ] / P(f2) * 100 %
d3 = [ P(f2 - 2f1) + P(f2 + 2f1) ] / P(f2) * 100 %
```

and Xmax is the peak displacement at the lowest drive voltage where any of the three reaches 10
percent (`Xmax = 1.4 * Xrms` from the measured fundamental).

**The parameter-based limits are the more useful form for design**, because each one names the
mechanism that binds:

| Limit | Criterion | Threshold | Corresponds to |
|---|---|---|---|
| `xBl` | `Bl(x)` falls to `Bl_min` of its rest value | **82 %** | about 10 % total modulation distortion |
| `xC` | `Cms(x)` falls to `C_min` of its rest value | **75 %** | about 10 % total harmonic distortion |
| `xL` | blocked impedance `ZE(x, f2)` deviates from rest | **10 %** at `f2 = 8.5 fs` | about 10 % intermodulation distortion |
| `xD` | Doppler distortion `d2` | **10 %** at `f2 = 8.5 fs` | Doppler nonlinearity |

**Read the worked example, because it inverts the usual assumption.** For one driver Klippel
publishes `xBl = 2.63 mm`, `xC = 4.28 mm`, `xL = 2.28 mm` and `xD = 15.9 mm`: the binding limit is
**voice-coil inductance**, not the suspension and not the coil overhang, and the Doppler limit is
almost seven times larger than the real one. A design that sizes excursion against a geometric
`XLIN = L - H` or against a suspension-derived figure can therefore be distorting badly at a fraction
of the excursion it was allowed.

Measured 10-percent-distortion excursion has been found to differ from the manufacturer's geometric
figure by roughly a factor of two **in both directions** — reported pairs include 12.8 mm claimed
against 6.8 mm measured, and 4.0 mm claimed against 6.6 mm measured. The direction is not
predictable, so the defensible response is to name the standard the figure came from and treat the
value as uncertain, not to apply a derating factor.

**Which distortion order appears first also diagnoses the limit**: third-order components dominating
indicates symmetrical limiting set by coil length, second-order components indicate coil offset or an
asymmetric suspension.

## 5. What the linear model leaves out

Every model in this framework is linear and small-signal. The mechanisms it omits are these, and
they are the reason a simulated maximum output is a ceiling rather than a prediction.

- **Force factor `Bl(x)`.** Falls with excursion as the coil leaves the gap. Voice-coil geometry sets
  the character of the limiting: an equal-length coil (coil height equal to gap height) limits softly
  and early, an overhung coil stays clean longer and then produces higher-order harmonics of larger
  amplitude once the coil is half out. Klippel's worked pair — 30 percent THD against 5 percent at the
  same excitation, converging at half the coil height — is one simulated motor pair and must not be
  quoted as a class specification.
- **Suspension stiffness `Kms(x)`.** In dome tweeters this, not the motor, is the dominant distortion
  generator. HF drivers also show no progressive stiffness rise inside their working range, so they
  have no mechanical self-protection: excursion protection has to come from the high-pass filter.
- **Inductance `Le(x)`.** Produces a reluctance force proportional to the square of current times the
  local slope of `Le(x)`. Because the squaring acts on a broadband current, this mechanism generates
  distortion across the whole audio band, unlike `Bl(x)` and `Kms(x)` which multiply displacement and
  therefore fade at high frequency.
- **Compression, of two separable kinds.** Thermal compression from voice-coil heating has time
  constants of seconds (coil) to minutes (magnet and frame); nonlinear compression is instantaneous.
  A single measurement duration cannot separate them, which is why the standards specify both
  short-term and long-term tests. Total Q is not a constant under power either: a ferrofluid-cooled
  dome measured `Qts` rising from 0.83 to 1.7 after twenty minutes of large-signal excitation, so an
  impedance-compensation network fitted to cold parameters is detuned when the speaker is warm.
- **Creep.** Impregnated fabric and paper diaphragms lose about 20 percent of their stiffness one
  decade below resonance, which no datasheet reports.

**Not all bass distortion is equal.** Suspension nonlinearity `Kms(x)` produces distortion that is
comparatively benign, because it acts on the bass signal itself. Force-factor nonlinearity `Bl(x)` is
different in kind: it **amplitude-modulates the entire signal**, so a woofer's bass excursion
modulates whatever midrange it is also reproducing. Force-factor modulation of 50 percent is
described as "not unusual in compact, long-stroke units". A related geometric effect: an effective
piston area that varies with excursion — one published example moves between 105 and 55 cm2 — is
directly a 6 dB sensitivity change with displacement. Doppler distortion, by contrast, has been
reported as **much less audible than an equivalent amount of amplitude modulation**, which is
consistent with this repository's own finding that the Doppler-driven crossover-frequency argument
did not survive verification.

**Shorting rings do not fix `Le(x)` in the bass.** A copper ring or cap has too much resistance to
counteract low-frequency flux changes, so position-dependent inductance stays uncorrected below
roughly 1 kHz — which is the band where the excursion that drives it actually occurs.

**The thermal model, when the question is output at power.** Voice-coil heating is a two-body lumped
system: with `P_Re = i_rms^2 Re` dissipated in the coil,

```
dT_v(ss) = (Rtv + Rtm) P_Re          dT_m(ss) = Rtm P_Re
tau_v = Rtv Ctv   (coil, short)      tau_m = Rtm Ctm   (magnet and frame, long)
```

with the extracted capacitances checkable against material mass — `m_copper [g] = 2.7 Ctv` and
`m_steel [g] = 2 Ctm`, both for `C` in Ws/K. The model neglects convection cooling, eddy-current
heating of the pole pieces and any distribution of heat within each body. The standard test drives
IEC 60268 noise to a coil rise of 50 to 100 K, steps level in 2 dB steps on a 30 s cycle, and aborts
when the coil resistance reaches **130 percent of cold `Re`, which corresponds to about +80 K**.

**Practice.** Design the linear model with margin rather than to the edge, keep the stress-drive
excursion inside the **binding** displacement limit rather than inside a geometric Xmax, and say in
the documentation that compression and nonlinearity are not modelled at all.

## 6. How much to trust a parameter set

- **Small-signal drive.** Impedance measurements intended for parameter extraction are made at about
  0.1 to 0.2 V across the driver. Higher drive contaminates the result with the nonlinearities above.
- **Vas by added volume (verified).** `Vas = VT * [(fCT * QECT) / (fS * QES) - 1]`, with `VT` the net
  internal volume of an **unlined**, sealed test box and `fCT`, `QECT` remeasured with the driver in
  it. Unlined because absorbing material changes the box compliance; sealed because leaks change it
  too. Small's own check is `sqrt(f1 f2) = fs`.
- **Mms by added mass, two incompatible equations.** The constant-`Bl` form is
  `Mms = Madded / (fS QEM / (fM QES) - 1)`; the AES2-2012 constant-compliance form is
  `Mms = Madded / (fS^2 / fM^2 - 1)`. They give different answers because compliance drifts with
  displacement and with creep. Report which was used rather than substituting silently.
- **Do not extract Qms and Qes from an impedance sweep alone.** The widely reproduced
  `Qms = fs sqrt(r0) / (f2 - f1)` chain attributed to Small was put to adversarial verification and
  **refuted**; it is not in the source it is usually credited to. Use a method whose provenance you
  can state.
- **Mounting changes the answer.** IEC 60268-5 specifies a 135 x 165 cm baffle, AES2-2012 an unbaffled
  clamped driver. The air load on a large baffle is twice the free-air value, which moves `Mms` and
  `Vas`.
- **Expect 20 to 30 percent spread** on measured `Vas` and `Mms` between methods, before considering
  sample-to-sample variation, temperature or burn-in state. That figure is quoted without a sample
  size and should be read as an order-of-magnitude warning, but it is the justification for treating
  a datasheet parameter set as a distribution rather than a number.

**What the framework does.** `lf_box` takes the parameter set at face value; `lf_uncertainty` exists
precisely because the parameter set is uncertain, and a Monte Carlo over `Vas`, `Qts` and `fs` spread
of this size is the honest way to present a bass claim. Run it whenever an alignment sits near an
edge that matters. See `simulations/lf_box/README.md` and `simulations/lf_uncertainty/README.md`.

## 7. Making a driver-choice claim

Name, for each candidate driver: the parameter set and where it came from, the reference efficiency
the formula in section 1 gives, the `Qt` the intended box implies and the peaking from section 2, the
displacement-limited output from section 3 at the target `f3`, the Xmax figure **with the standard it
was measured to**, and what the linear model is not telling you. A sensitivity target that the
efficiency law cannot support is a finding about the driver complement, and no box or network
recovers it.

## Sources

- Small, R. H., "Direct-Radiator Loudspeaker System Analysis", *Journal of the Audio Engineering Society*, vol. 20, no. 5, pp. 383-395, 1972 — the reference-efficiency formula and its constants, the `Qt` peaking family, the displacement-limited power ratings, and the added-volume `Vas` method. <https://diyaudioprojects.com/Technical/Papers/Direct-Radiator-Loudspeaker-System-Analysis.pdf>
- Small, R. H., "Vented-Box Loudspeaker Systems, Part II: Large-Signal Analysis", *Journal of the Audio Engineering Society*, vol. 21, no. 6, 1973 — the vented displacement-limited ratings and the `kP = 3.0` programme constant with its qualifications.
- Keele, D. B., Jr., "Maximum Efficiency of Direct-Radiator Loudspeakers", AES 91st Convention, preprint 3193, 1991 — the 25 percent power-transfer ceiling and the diameter and mass-ratio dependence. <https://dbkeele.com/23-maximum-efficiency-of-direct-radiator-loudspeakers/>
- Klippel, W., "Assessment of Voice Coil Peak Displacement Xmax", AES convention paper — the demonstration that the AES2-1984 criterion yields inconsistent values for the same driver. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Literature/Papers/Assessment_of_Voice_coil_peak_displacement_XMAX_02.pdf>
- Klippel, W., "Loudspeaker Nonlinearities — Causes, Parameters, Symptoms", companion to *Journal of the Audio Engineering Society*, vol. 54, no. 10, pp. 907-939, 2006 — `Bl(x)`, `Kms(x)`, `Le(x)`, the reluctance force and the voice-coil geometry trade. <https://www.klippel.de/fileadmin/_migrated/content_uploads/Loudspeaker_Nonlinearities%E2%80%93Causes_Parameters_Symptoms_01.pdf>
- Klippel, W., "Large Signal Performance of Tweeters, Micro Speakers and Horn Drivers", application paper — HF-driver thermal compression, hot `Qts`, dominant suspension nonlinearity and suspension creep. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Literature/Papers/Large_signal_performance_of_tweeters_05.pdf>
- ARTA Labs, *LIMP user manual* and application note AN7, "Estimation of Linear Displacement with STEPS" — small-signal drive level, the two added-mass equations, method spread, IEC and AES mounting, and the IEC PAS 62458 and AES2-1984 Xmax definitions with measured-versus-claimed disagreements. <https://artalabs.hr/download/LIMP-user-manual.pdf>
- Klippel GmbH, Application Note AN4, "Measurement of peak displacement Xmax (performance-based method)" - the IEC 62458 two-tone procedure with the `dt`, `d2` and `d3` definitions, and the four stated defects of AES2-1984. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Application_Notes/AN_04_Peak_Displacement_Xmax.pdf>
- Klippel GmbH, Application Note AN5, "Displacement limits due to driver nonlinearities" - the `xBl`, `xC`, `xL` and `xD` limits with their IEC 62458 thresholds and the worked example in which inductance binds. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Application_Notes/AN_05_Displacement_Limits.pdf>
- Klippel GmbH, Application Note AN18, "Thermal parameter measurement" - the two-body thermal circuit, its steady-state and time-constant equations, the equivalent-mass checks and the power-test protocol. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Application_Notes/AN_18_Measurement_of_Linear_Thermal_Parameters.pdf>
- PURIFI ApS, "Some speaker problems that needed solving", technical note, 2021 - force-factor modulation magnitudes, the `Sd(x)` sensitivity effect, the relative audibility of Doppler against amplitude modulation, and the low-frequency limit of shorting rings. Manufacturer technical writing, not peer reviewed. <https://purifi-audio.com/blog/tech-notes-1/some-speaker-problems-that-needed-solving-1>
- IEC 62458, *Sound system equipment - Electroacoustical transducers - Measurement of large signal parameters* - the standard the displacement limits and the two-tone Xmax procedure are defined in; cited here through the application notes above rather than read at source.
- IEC 60268-5, *Sound system equipment — Part 5: Loudspeakers*; AES2-2012, *AES standard for acoustics — Methods of measuring and specifying the performance of loudspeakers for professional applications* — the mounting, drive and rating conventions the figures above have to be read against.
- In this repository: `simulations/lf_box/README.md` for the alignment model that consumes these parameters, `simulations/lf_uncertainty/README.md` for the tolerance sweep, and `references/enclosure-alignments.md` for what the box then does with them.
