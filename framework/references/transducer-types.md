---
id: transducer-types
applies_when: Choosing or judging an upper-range transducer - a dome, a compression driver, a horn or waveguide - and setting the crossover and protection it needs
updated: 2026-09-15
---

# Transducer types above the woofer

A cone woofer's behaviour is covered by the Thiele/Small model and by the large-signal mechanisms in
`driver-selection.md`. The transducers above it are not: a dome fails differently from a cone, a
compression driver is a diaphragm plus a phase plug plus a horn and each stage has its own limit, and
a horn's pattern is set by its mouth rather than by its driver. This reference holds what is
established here about those, and says plainly what is not.

**Read the scope first, because the coverage is very uneven.** Dome and compression drivers, horn
and waveguide directivity and phase plugs are established here. Electrostatic panels are established
quantitatively in section 4b, from a textbook chapter read at first hand. Air-motion transformers
(4a), true ribbons and planar-magnetic panels (4c), coaxials (4d) and full-range drivers (4e) are
covered only as **named constraints**: what limits them, and what number is missing. For those four,
no source consulted supplies a design model, and section 5 says what the framework can and cannot do
with them. Do not infer their behaviour from the dome and compression-driver material here; they
differ in exactly the mechanisms this reference describes.

## 1. Dome tweeters and other HF drivers

**No mechanical self-protection.** Measured suspension stiffness of domes and micro-speakers shows no
progressive rise inside the working range, unlike a woofer whose suspension stiffens as it runs out
of travel. Overdrive therefore goes straight to damage rather than to audible roughness first, and
the paper's own qualitative observation is that HF overload is heard as a timbre change rather than
as the characteristic roughness of a woofer, so it is under-reported by ear. **The high-pass filter
is the excursion protection**; that is an engineering requirement, not a preference, and it is the
main reason to prefer a steeper acoustic slope on an HF section.

**Suspension, not motor, dominates the distortion.** In one measured dome, peak `Kms(x)` distortion
exceeded 40 percent of the sound-pressure peak while `Bl(x)` stayed below 15 percent and `Le(x)`
below 2 percent. Those percentages are one sample under one stimulus and are not a class
specification, but the ranking is the useful part: attack suspension asymmetry first.

**Total Q is not a constant.** A ferrofluid-cooled dome measured `Qts = 0.83` small-signal and
`Qts = 1.7` after twenty minutes of large-signal excitation, with the fluid's temperature- and
vibration-dependent losses driving most of the change. Any impedance-compensation network or
Q-dependent alignment fitted to cold parameters is detuned once the speaker is warm. Dry-gap
tweeters will not show that magnitude.

**Thermal compression.** A 51 mm-coil compression driver measured about **3 dB of thermal compression
over a 12 dB drive range** (1 V to 4 V rms), at a maximum real input power of 12 W with a coil
temperature rise under 80 K. A passive crossover cannot recover that loss, so a system sensitivity
quoted at 1 W/1 m overstates output at rated power. The figure is one device: it scales with coil
mass, gap geometry and heat path, and at domestic levels of a few hundred milliwatts it is
negligible.

**Creep.** Impregnated fabric and paper diaphragms show about 20 percent compliance increase one
decade below resonance (a synthetic diaphragm measured 2 percent). It raises the DC offset produced
by any nonlinear asymmetry and appears on no datasheet.

## 2. Compression drivers

**The lumped model stops at the first break-up.** One measured compression driver had its dome in
phase across four radii up to 6 kHz, the outer rim in anti-phase from 6 to 7.5 kHz, break-up
beginning at 5 kHz and a distinct magnitude minimum at 8.5 kHz producing a dip in the fundamental and
a matching THD peak. Those frequencies belong to that dome's diameter and material and must be
re-measured per driver. The transferable rules are that an equivalent-circuit model explains the low
end and predicts nothing above the first break-up, and that a response minimum and a distortion peak
tend to arrive together. **Choose the upper working limit from a measured response, not a simulated
one.**

**Not covered:** compression ratio and throat area, diaphragm-to-throat cavity volume and the HF
rolloff it imposes, horn efficiency and the throat-to-mouth area ratio, and the power-response tilt
that horn equalisation has to correct. These are central to compression-driver practice and no source
here supplies them.

## 3. Horn and waveguide directivity

**Physics, empirically constant.** Keele's constant-directivity mouth relation, applied to each plane
separately:

```
d = K / (theta * fc)        fc = K / (theta * d)        theta(f) = K / (d * f)  below fc
K = 1e6 inch-deg-Hz = 2.54e4 metre-deg-Hz
```

with `d` the mouth dimension in the plane considered, `theta` the coverage angle in that plane in
degrees, and `fc` the frequency below which pattern control is lost. `K` is explicitly an empirical
constant, not physics; a second source gives 25106 rather than 25400, a 1.2 percent difference that
does not matter. Scaling follows directly: one octave lower control needs double the mouth
dimension, and halving the coverage angle also needs double the mouth dimension.

**The two planes lose control at different frequencies.** A square mouth on a horn with unequal
coverage angles loses control in the narrow plane first. To make both planes let go together, the
narrower-coverage plane's mouth dimension must be larger by the ratio of the coverage angles: a
90 x 45 degree horn needs a mouth twice as tall as it is wide. Commercial horns are usually the other
way round, which produces **pattern flip** — a 12 x 6 inch mouth marketed as 90 x 45 degrees achieves
45 degrees vertically only above about 3.7 kHz, and below 2 kHz its vertical beamwidth is wider than
its horizontal.

**The design consequence.** Check the mouth dimensions against the formula before designing a
crossover point or a vertical array around a horn's nominal rating, because in the 1 to 4 kHz region
— exactly where a two-way monitor or PA box crosses over — the real directivity mismatch against a
cone driver is usually larger than the datasheet implies. This is the horn-side companion to the `ka`
question in `system-architecture.md` section 1.

**Mouth termination.** An undersized mouth reflects energy back down the horn and produces ripple.
The criterion is the dimensionless `k rm` at cutoff, for which the sources disagree — 0.93 under a
plane-wave assumption, 1.4 under a spherical-wave one — with practice quoted as 0.7 to 1 for bass
horns and at least 1 for midrange and treble horns. See `enclosure-alignments.md` section 5 for the
flare mathematics that goes with it.

**Mid-band narrowing.** Spherical-segment horns (multicellular and radial) narrow to 40 to 50 percent
of their nominal beamwidth where the wavelength becomes comparable to the segment dimensions. Keele's
constant-directivity horns removed it by doubling the included angle over the last third of the
conical section, joining the exponential throat to the conical mouth at `r = 0.95 sin(theta) / k_c`.
Both figures are reported at second hand without tolerances.

**Air nonlinearity at the throat.** Beranek's simplification for an infinite exponential horn is
`D2 [%] = 1.73e-2 * (f / fc) * It`, with `It` the throat intensity in W/m^2. It grows with `f / fc`,
so a low-cutoff horn driven hard at high frequency is the worst case; at domestic levels it is
negligible, and in high-power sound reinforcement throat pressures of 150 to 170 dB make it real.

**Not covered:** Geddes' oblate-spheroidal waveguides, higher-order modes and throat-discontinuity
diffraction — only the Keele-lineage constant-directivity theory is represented here. Also absent:
mouth roundover and flare termination geometry, diffraction-slot horns, and horn-mouth interaction
with the cabinet baffle.

## 4. Phase plugs

A compression-driver phase plug exists to make the acoustic path length from every point on the
diaphragm to the exit equal, so the exit wavefront is planar. Hughes' progressive degenerate
ellipsoidal construction does this in closed form: take the longest straight path as the target
(`phi_max = atan((H_core/2)/L)`, `r_max = L / cos(phi_max)`) and lengthen every shorter cross-section
with a tangent-line-plus-elliptical-arc segment until `F = 2(t + S) = r_max`. A curved exit wavefront
is obtained by shortening or lengthening the target path per exit height rather than by changing the
outer geometry.

Two warnings travel with it. The published paper contains two typographical errors corrected only in
its rev02 PDF — the tangent-length terms are added, not subtracted, and the arc-length correction
multiplies rather than adds — so any secondary reproduction of those equations has to be checked. And
the construction is geometric: it does not by itself predict the acoustic response, the higher-order
modes, or whether the plug loads the diaphragm correctly, and its supporting measurement is one
prototype validated to about 8 kHz. The technology is covered by US Patent 8,887,862.

## 4a. Air-motion transformers, as far as anything is established

The folded-diaphragm air-motion transformer sits between a dome and a compression driver in the
system role it plays, and the only figures this repository has for the class are manufacturer
catalogue specifications for one pro-audio range:

| Model | Power (W AES) | Sensitivity (dB, 2.83 V / 1 m) | Nominal impedance |
|---|---|---|---|
| TPL-200/H | 120 | 104 | 8 ohm |
| TPL-200/B | 120 | 101 | 8 ohm |
| TPL-150/H | 80 | 102 | 8 ohm |
| TPL-150/Black | 80 | 99 | 8 ohm |
| TPL-75 | 40 | 92 | 8 ohm |

The one usable conclusion is the sensitivity bracket: a pro AMT of this size sits around 99 to
104 dB/2.83 V/m, which is compression-driver territory and 10 to 15 dB above an ordinary dome. That
matters directly for the level budget in `crossover-design.md` section 4 — an AMT in a system whose
bass section supports 90 dB needs as much padding as a horn does.

**Everything else about the class is still unsourced here**: nominal against minimum impedance and
how the impedance behaves with frequency, whether a matching transformer is involved and what it does
to the load, the minimum crossover frequency and slope the diaphragm needs, excursion and thermal
limits, distortion mechanisms, and the directivity of a tall folded diaphragm in the vertical plane —
which is the property most likely to decide whether one belongs in a design at all.

## 4b. Electrostatic panels

The one transducer class in this section with a complete, quantitative small-signal model.

**Constant charge, not constant voltage.** The electrostatic principle only became practical for
full-range use once constant-charge polarization was understood (after about 1950). With the
diaphragm held at constant *charge* rather than constant *voltage*, the force on it becomes linear in
the signal, and the negative-stiffness instability that plagues constant-voltage designs is removed.
Any analysis that assumes a fixed polarizing voltage on the diaphragm is analysing the wrong device.

**The governing equation.** For a plane unbaffled diaphragm, neglecting diaphragm stiffness, mass and
intentional damping:

```
P = I_sig * Vpol / (2 c r d)

P      sound pressure at a large axial distance, N/m^2
I_sig  signal current fed to the plates, A
Vpol   polarizing voltage, V
c      speed of sound, m/s
r      measuring distance, m
d      diaphragm-to-plate spacing, m
```

Three things follow, and each of them inverts a cone-driver intuition:

- **Output depends on signal *current*, not voltage.** An ESL is a current-driven radiator. This is
  why its behaviour is described in terms of a drive circuit with a large series resistance rather
  than a voltage source.
- **Output is independent of diaphragm area and shape** — the equation holds "for a plane unbaffled
  diaphragm of any size or shape". Area buys maximum output and low-frequency capability, not
  sensitivity.
- **Output is frequency independent for constant current**, so the flat response is inherent rather
  than fitted. The diaphragm can be made light enough that the electric force acts effectively
  directly on the air load, which is why break-up modes can be almost eliminated and the acoustic
  performance is theoretically predictable — the opposite of the cone-driver situation in section 2.

**Sensitivity is set by `Vpol/d`, and air breakdown caps it.** The optimum, maximising attainable
diaphragm force at high frequencies, is

```
Vpol / d = 0.5 * Emax(d)
```

where `Emax` is the breakdown field intensity of air for a gap of that length, under uniform-field
conditions between smooth flat plates. `Emax` is **not** a constant: it is about **30 kV/cm at a
10 mm gap and rises towards about 60 kV/cm as the gap approaches zero.** Halving the gap therefore
does better than doubling the sensitivity, which is the physical reason ESLs use small gaps and pay
for it in maximum excursion.

**Scaling.** Doubling the linear dimensions of an ESL gives **+12 dB** of maximum output when the
limit is the available force, and **+18 dB** when the limit is the diaphragm striking the plates.

**The load an ESL presents.** It is a capacitor, so its impedance falls with frequency, and a step-up
transformer is always interposed. These are not small ratios: the transformer in one published Quad
design has a step-up ratio of about **1:290** to the whole secondary, implemented as two separate
1:122.5 transformers driving the plates rather than one centre-tapped secondary. **A passive
crossover designed against a nominal resistive load is meaningless here**, and the amplifier sees a
capacitive load at high frequencies, which is the usual cause of trouble.

**Two effects that detune a warm ESL**, both stated in the source: the diaphragm's mean voltage rises
under constant-charge operation, changing sensitivity; and the inter-plate capacitance increases when
the polarizing voltage is applied. Neither is on any datasheet.

## 4c. True ribbons and planar-magnetic panels

**Nothing quantitative was obtained.** No source consulted gives a force equation, a sensitivity
relation, a power-handling figure, an impedance model or a resonance treatment for these. What
follows is the set of constraints that were stated, so that a design does not walk into them; it is
not a model, and a candidate using one of these drivers must say so.

- **Diaphragm mass is comparable with the co-vibrating air-load mass.** That is the whole attraction —
  near-ideal coupling to air and high sensitivity — and it is also why these drivers have almost no
  mechanical reserve. No source gives the two masses as numbers for any real device.
- **A true aluminium-foil ribbon requires an impedance-matching transformer**; its bare impedance is
  a few milliohms. An air-motion transformer (AMT) does not. This is a hard crossover constraint:
  the transformer's leakage inductance and core behaviour sit between the crossover and the
  radiator, and the framework's `crossover_network` app does not model a transformer.
- **Aluminium ribbon tweeters have a relatively limited dynamic range**, and AMTs with narrow
  conductor spacing show **early onset of power compression**. The mechanism in the AMT case is
  thermal and is the same one `driver-selection.md` section 5 describes, but no thermal parameters
  are published for these drivers.
- **They are line sources, not point sources, over most of their band.** The one quantitative figure
  obtained: an AMT diaphragm **wider than about 1 inch and/or longer than about 3 inches produces
  high-frequency beaming with extremely narrow vertical coverage above roughly 8 kHz.** That is a
  single vendor-side designer's figure, not a measurement series, but it is the right order and it is
  the number to check a tall ribbon against before trusting an on-axis response.

The practical consequence for this framework is in section 5: a tall ribbon's directivity cannot be
computed by the circular-piston model the apps use, so any vertical off-axis result for one is wrong
in a way the app will not flag.

## 4d. Coaxial drivers

The attraction of a coaxial is real and is worth stating precisely: it removes the acoustic offset
between the two sections, so the off-axis phase cancellation that vertical spacing causes
(`baffle-and-driver-placement.md`, and `system-architecture.md` section 3) does not arise. It buys
that by creating a different problem.

**The low/mid cone is a horn for the high-frequency section.** Because the cone is axisymmetric, it
forms the walls of a horn within which the HF output propagates, and an axisymmetric directivity
pattern is imposed on the HF section whether or not that was wanted. Two consequences are stated:

- The imposed pattern typically has a **beamwidth that decreases with increasing frequency**, which
  is the opposite of what a constant-directivity design wants.
- **Directivity control ceases below about 2.5 kHz** in a basic coaxial arrangement, extending down
  to about **1.6 kHz** when a static waveguide is added around the HF exit. Below that frequency the
  coaxial has no pattern control and behaves like the cone alone.

**The horn moves.** The cone is also the woofer, so the "horn walls" translate with cone excursion —
in one design the clearance between the moving cone and a static waveguide is specified in the range
0.3 cm to 5 cm to prevent contact. The HF path is therefore modulated by the LF programme. No source
consulted quantifies the resulting distortion, and this is a mechanism a linear crossover simulation
cannot see, of the same family as the force-factor modulation in `driver-selection.md` section 4.

These figures come from a patent specification, which is a primary engineering document but is
written to argue for its own remedy; treat the frequencies as representative of the designs it
describes rather than as class constants.

## 4e. Full-range drivers

**No design model was obtained, and one would be hard to justify.** A full-range driver is asked to
be a piston in the bass and something else entirely at the top, and the two regimes are joined by
mechanisms the framework does not model:

- **The whizzer cone** — a small low-mass secondary cone at the voice-coil/diaphragm junction — is
  what extends the HF output. It is a separate radiator with its own break-up behaviour, driven
  through the compliance of its own joint. Nothing here predicts its response, its directivity or the
  interference between it and the main cone.
- **Directivity is the binding constraint, and it is computable.** A full-range driver's radiating
  diameter is a woofer's, so it beams at a woofer's frequencies while still being asked to reproduce
  treble. The circular-piston directivity the framework already uses gives that frequency directly
  from the cone diameter, and it should be computed and reported for any full-range candidate before
  anything else about it is discussed.
- The lumped Thiele/Small model governs the bass and **predicts nothing above the first cone
  break-up**, exactly as section 2 says for compression drivers.

A full-range design is therefore a design whose most important region is outside every model here.
That is a statement about this repository, not a verdict on the driver class.

## 5. What the framework models

`directivity` provides piston, Gaussian-horn, tabulated-beamwidth and rectangular-ribbon patterns
with their -6 dB beamwidths, so a horn's coverage can be *described* to the simulation but is not
derived from its geometry: nothing here computes a pattern from a mouth size, and nothing computes
throat impedance, horn loading or horn efficiency. `source_response` turns a published curve into a
section file with a minimum-phase reconstruction and an acoustic depth; a horn's acoustic centre is an
input you supply, not a modelled quantity, and for a deep horn it is neither the mouth nor the
diaphragm. Thermal compression, break-up and air nonlinearity are not modelled anywhere. See
`simulations/directivity/README.md` and `simulations/source_response/README.md`.

**Since `horn-and-waveguide-design.md` was added, a horn's throat area, rear cavity, usable band, HF
corners and displacement-limited output can be derived from Thiele/Small parameters**, and an OS
waveguide's contour and cutoff from its throat radius and coverage angle. Pattern from mouth size
still comes from Keele's constant-directivity relation in section 3, not from a solver.

**Where the apps will be quietly wrong.** `directivity` offers a rectangular-ribbon pattern, so a
ribbon's *shape* can be described; but for the driver classes in 4b to 4e the apps have no model of
the mechanism, and nothing in a result file will say so:

| Driver class | What the apps will do | Why it is wrong |
|---|---|---|
| Electrostatic | treat it as a resistive-ish load with a supplied curve | it is a capacitor behind a ~1:290 transformer (4b) |
| True ribbon | model the crossover into the driver's rated impedance | the transformer sits between them and is unmodelled (4c) |
| Tall ribbon / planar | apply a piston or ribbon pattern | beaming above ~8 kHz for a diaphragm over ~3 in long (4c) |
| Coaxial | treat the two sections as independent, coincident sources | the cone horn-loads the HF section and moves with programme (4d) |
| Full-range | model the piston band and extrapolate | the whizzer and break-up region is unmodelled (4e) |

For any of these, state the assumption in the candidate notes the way you would for an unpublished
dimension, and do not present an off-axis or impedance result as if the model covered the device.

## 6. Making a claim about an upper-range driver

State the driver's usable band with the evidence for each end: the break-up behaviour or measured
response for the top, the resonance and the protection the filter provides for the bottom. For a
horn, state the mouth dimensions and the `fc` per plane that Keele's relation gives, and compare that
with the crossover frequency and with the woofer's beamwidth there. Where the level budget depends on
sensitivity at power rather than at one watt, say whether thermal compression has been allowed for —
it is not in any simulated curve in this repository.

## Sources

- P. J. Baxandall, revised by J. Borwick, "Electrostatic loudspeakers", chapter 3 of *Loudspeaker and Headphone Handbook*, ed. J. Borwick. Read at first hand; source of the governing pressure equation, the constant-charge argument, the `Vpol/d = 0.5 Emax` optimum, the air breakdown curve, the 12/18 dB scaling and the Quad transformer ratio.
- I. Levitsky, "Thin-Film High-Frequency Transducers", audioXpress, parts 1 and 2. Source of the ribbon and AMT constraints in section 4c, including the ~8 kHz beaming figure for diaphragms over about 3 inches long. A designer's article, qualitative: it supplies constraints, not a model. https://audioxpress.com/article/thin-film-high-frequency-transducers-part-1-the-advantages
- US Patent 10,506,331 B2, "Coaxial loudspeaker", for the statements in section 4d about the cone acting as a horn for the HF section, the 2.5 kHz and 1.6 kHz directivity-control limits and the moving-waveguide clearance. A patent specification, written to argue for its own remedy. https://patents.google.com/patent/US10506331B2/en

- Klippel, W., "Large Signal Performance of Tweeters, Micro Speakers and Horn Drivers", application paper — thermal compression over drive range, hot `Qts`, dominant suspension nonlinearity, absence of mechanical self-protection, creep, and the compression-driver break-up case study. <https://www.klippel.de/fileadmin/klippel/Files/Know_How/Literature/Papers/Large_signal_performance_of_tweeters_05.pdf>
- Hughes, C. E., "Understanding Horn Directivity", Excelsior Audio — Keele's constant-directivity mouth relation applied per plane, the asymmetric loss of control, and the pattern-flip example against a commercial rating. <https://www.excelsior-audio.com/Publications/Understanding_Horn_Directivity.pdf>
- Hughes, C. E., "Progressive Degenerate Ellipsoidal Phase Plug", AES 139th Convention, 2015, rev02 — the equal-path-length construction, the curved-wavefront extension, and the two published errata. <https://www.excelsior-audio.com/Publications/Hughes_-_Progressive_Degenerate_Ellipsoidal_Phase_Plug_(AES139,_2015-10)_rev02.pdf>
- Kolbrek, B., "Horn Theory: An Introduction", *audioXpress* — the mouth-termination criterion and its competing optima, spherical-segment narrowing and Keele's constant-directivity fix, and Beranek's air-nonlinearity distortion term. <https://audioxpress.com/assets/upload/files/kolbrek2884.pdf>
- Keele, D. B., Jr., "What's So Sacred About Exponential Horns?", AES 51st Convention, preprint 1038, 1975, and "Optimum Horn Mouth Size", AES 46th Convention, preprint 933, 1973 — the primary sources behind the constant-directivity and mouth-size results quoted at second hand above. Neither was read for this reference.
- Beyma, AMT driver catalogue specifications - the sensitivity, power and impedance figures in section 4a. Manufacturer catalogue data for one product range; no measurement conditions beyond the stated 2.83 V / 1 m are published there. <https://www.beyma.com/productos/c/amt-driver/>
- In this repository: `references/enclosure-alignments.md` section 5 for horn flare and loading mathematics, `references/system-architecture.md` for the crossover frequency and directivity matching these drivers have to meet, `references/driver-selection.md` for the large-signal mechanisms common to all moving-coil transducers, and `simulations/directivity/README.md` for the patterns the framework can represent.
