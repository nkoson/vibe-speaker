---
id: measurement-and-model-limits
applies_when: Reading a simulated result for what it is worth, planning the measurements that would confirm it, or writing down what a predicted figure does and does not mean
updated: 2026-10-15
---

# What a simulated result is worth, and what measuring it would take

Nothing this framework produces is a measurement. Every curve is a linear, small-signal model
evaluated over declared priors, and the distance between that and a microphone is the subject of this
reference. It exists for two jobs: to keep predicted figures honestly labelled, and to say what the
conditions behind published or user-supplied measurement data. The default design workflow completes the speaker through simulation, research and robustness analysis; the measurement procedures below apply when interpreting such data or when the user requests that work.

## 1. Quasi-anechoic measurement is bounded by the room, not the software

**Physics.** A gated impulse response is valid only above roughly `1 / t_gate`: a 5.6 ms gate is
trustworthy above about 180 Hz, and a gate of at least 5 ms is needed for a correct response above
200 Hz. Below that the data is not merely noisy, it is absent, and must be replaced by a near-field
splice.

The gate is set by geometry. For a reflection-free time `dt` at a measuring distance `d`, the
loudspeaker and microphone must both stand at

```
h = sqrt( ((d + c dt) / 2)^2 - (d / 2)^2 )
```

above the reflecting plane — 1.08 m for a 5 ms gate at a 48 cm measuring distance. The formula
handles the floor only; side walls and ceiling need their own check, and practice is to keep at least
150 cm from the rotation centre to any wall and to absorb floor and ceiling if windows longer than
about 4 ms are wanted.

**Practice.** Window with a Tukey taper rather than a rectangle to avoid low-mid overshoot on a short
window. State the gate with every gated curve; a response quoted without its gate has an unstated
low-frequency validity limit.

## 2. The near-field splice, and the uncertainty it hides

**Physics.** With an effective radius `a` (membrane radius plus about a third of the surround width),
the near field is sampled at `d < a/20` and the far field begins beyond `r > 6a`; between them the
on-axis pressure depends on `ka` and can null, so it is unusable. The near-field level scales to the
half-space far field at distance `r` by

```
p_far / p_near = (a / 2r) * (ka/2) / sin(ka/2)     which simplifies to  a / 2r  where ka << 1
```

the simplification being safe below roughly 200 Hz for any practical membrane.

**Where the honesty is required.** Practice "often needs an extra 1 to 2 dB of scaling to make the two
curves meet". That admission is the real uncertainty of any absolute sensitivity derived through a
near-field splice, and it is why a spliced sensitivity should be quoted with a tolerance rather than
to a tenth of a decibel.

**The splice also has to carry the baffle.** A near-field measurement contains no baffle step and no
diffraction. Converting it to the finished box's free-space response means applying the step
explicitly — analytically as `p4/p2 = (1 + j f/f0) / (2 + j f/f0)` with `f0 = 34.16/d` Hz for a square
baffle of width `d` in metres (`42.70/d` for a sphere), or by simulation. A rectangular baffle is
handled by an equivalent width `d = w (h/w)^(1/3)`, which its own authors label an approximation.
Better practice when splicing for a crossover simulation is two *different* diffraction corrections —
one at the intended listening distance for the near-field part, one at the actual measurement
distance for the gated part — because the step itself is distance-dependent: a 250 mm baffle shows
only about 5 dB of step at 0.25 m against 6 dB in the far field.

## 3. Measuring for a crossover simulation

- **Timing offset is the acoustic centre.** For a measurement at distance `D` with no processing
  delay, the loopback offset is `D / 344` seconds — 2.907 ms at 1000 mm. That single number is what
  encodes the relative driver delay into the simulated sum; an error in it appears directly as a wrong
  summed response and is indistinguishable from a real offset.
- **Distance.** 1000 mm to the rotation centre is the common default and is not far field for a large
  multi-way; deep horns, long ribbons and wide baffles want at least three baffle widths, or the
  listening distance.
- **The same angular grid for every driver, subwoofer included.** Power response and directivity index
  are truncated to the smallest coverage angle common to all drivers, so one driver measured to 90
  degrees silently invalidates the whole power calculation. Full-space power needs 0 to 180 degrees
  from all of them. Ten-degree steps are the working default, five degrees inside the listening window
  where the on-axis response has dense ripple.
- **Skipping the vertical plane** for circular drivers on a tall narrow baffle costs an asserted
  "small hump under 1 dB" in power response near the diffraction peak — an order-of-magnitude bound
  from vendor documentation, not a validated tolerance.
- **Near-field capture** at 5 mm from the dust-cap centre with zero timing offset and a reduced drive
  level; ports at the vent mouth. Export at high resolution so the simulator's interpolation is not
  the limiting factor.

## 4. Distortion, and why one number will not do

A swept-sine THD measurement exposes mainly the displacement-limited low-frequency mechanisms and
collapses at higher frequencies, where a multi-tone stimulus spread across the band triggers
intermodulation and shows substantially higher distortion — which is the regime music actually
occupies. The frequency distribution of a multi-tone spectrum is also a fingerprint: distortion
concentrated near `fs` points at the suspension, intermodulation across the whole band at `Bl(x)`,
and distortion rising toward high frequencies at `Le(x)`, `Le(i)`, Doppler and cone break-up.

Excursion is measured to IEC 62458 with a two-tone stimulus, not to the older AES2-1984 current or
displacement criteria; the procedure, the distortion definitions and the four parameter-based
displacement limits are in `driver-selection.md` section 4.

For maximum-output ratings, cite the clause: IEC 60268-21 gives rated maximum input value (17.1),
rated maximum sound pressure (18.1.2b), short-term maximum SPL (18.3), long-term maximum SPL (18.4)
and multitone distortion (23). Those clause numbers reach this reference second-hand and should be
checked against the current edition before being used normatively. **No source consulted here gives
an acceptance threshold** — a distortion percentage that constitutes a pass for hi-fi, monitoring or
PA — except the broadcast monitor limits in `target-response.md`.

## 4a. Measuring heat and protection in a finished passive system

Two procedures are worth knowing because they are the only way to check the claims a linear model
cannot make.

**Voice-coil temperature through a crossover.** Coil temperature is read from the DC resistance, and
in a finished passive system the crossover blocks the usual low-frequency path to each driver. The
method is to add a low-amplitude **pilot tone** at a frequency where that driver's branch impedance
is at a minimum and the motional term is negligible — around 2 Hz for a woofer behind a low-pass,
around 3 kHz for a tweeter behind a high-pass — kept 20 to 40 dB below the programme level, and to
derive `Re` from it continuously. The pilot tone also keeps the temperature measurement alive when
the programme signal stops. Choose the frequencies from a measured impedance sweep of the actual
network, not from these examples.

**The thermal power test.** Drive IEC 60268 noise, step the level in 2 dB steps on a 30 s cycle until
the coil rise lands in the 50 to 100 K working window, and **abort on resistance rather than on
time**: 130 percent of cold `Re` corresponds to about +80 K for a copper coil. Then run on and off
phases long enough to separate the short coil time constant from the long magnet one. The parameters
this extracts, and what they predict, are in `driver-selection.md` section 5.

**Protection systems are tested the same way**, with the limiter, crossover and protection components
in circuit and displacement measured directly by laser while voltage, current and `Re` are monitored —
which is the only way to establish that a protection circuit acts before the driver's displacement
limit rather than after it.

## 4b. What the standards say, and which of them could actually be read

Most of the measurement practice this repository relies on traces back to standards that are sold
rather than published. That matters, because a figure quoted from a secondary description of a
standard is a figure nobody here has checked. This section records what was read at source and what
was not, so the distinction stays visible.

**Read at first hand: AES2-2012**, *Methods of measuring and specifying the performance of
loudspeakers for professional applications - Drive units*. Two of its clauses settle questions this
repository was answering from application notes.

**Maximum useful displacement (clause 5.5)** is defined as the peak displacement at which **neither**
the total harmonic distortion **nor** the second- or third-order modulation distortion exceeds
**10 %** in the radiated sound pressure. The measurement is a two-tone test:

```
f1 = fs                     first tone, at resonance
f2 = 8.5 fs                 second tone
amplitude ratio f1:f2 = 4:1
microphone in the near field; modulation components read at f2 +/- n f1
displacement read with a laser displacement sensor
```

Note that `8.5 fs` is the same frequency at which IEC 62458 defines the inductive displacement limit
`xL` (`driver-selection.md` section 3). The two standards are probing the same upper-frequency
behaviour, from the impedance side and from the acoustic side. The standard also notes that its
definition differs from IEC 60268-5 but that the difference is not expected to cause difficulty,
since the limiting distortion figure is only 10 %.

**Power handling (clause 6)** is an endurance test, and it is worth putting beside the accelerated
protocol already recorded in section 4a:

- **Signal**: pink noise spanning **one decade upward from the manufacturer's stated low-frequency
  limit**, bandpass filtered at 24 dB/octave with Butterworth response, **peak-to-rms ratio 4:1
  (12 dB)**. The amplifier must pass peaks at least 9 dB and preferably 12 dB above the rms voltage,
  which means an amplifier rated at 4 to 8 times the test power.
- **Procedure**: successively higher powers, **thermal equilibrium at each step (about 2 hours)**.
  Power is the square of the applied rms voltage divided by the **rated** impedance.
- **Rated power** is the power the device withstands for 2 hours **without significant permanent
  change** in acoustical, mechanical or electrical characteristics.
- **Reported alongside it**: the temperature rise of **both** the voice coil and the magnet assembly
  at the end of the test, with the measurement method stated; the maximum excursion beyond which
  permanent mechanical damage occurs, with the cause named; and the **low resonance frequency
  measured before and after** the power test.

That last item is the cheap diagnostic: `fs` shifting across a power test is direct evidence of
suspension change, and it costs one extra impedance sweep. It is also a reminder that the framework's
cold Thiele/Small parameters describe a driver that has not been played.

**The two protocols are not interchangeable.** AES2's 2-hour-per-step endurance test answers "what
power will this survive"; the Klippel-style accelerated protocol in section 4a — short steps, target
coil rise, abort at 130 % of cold `RE` — answers "how hot does the coil get and how fast". A thermal
model calibrated against one should not be validated against the other.

**Not read at source, and the consequence in each case:**

| Document | Status | Consequence here |
|---|---|---|
| ANSI/CTA-2034-A | Paywalled; not read | The spinorama **curve geometry** (group angles, ring weights) in `target-response.md` section 7 still rests on an open-source reimplementation with two flagged discrepancies. The **preference predictors** no longer do — they were read in Harman's patent. |
| IEC 60268-5 | Paywalled; not read | AES2-2012 states its tests and nomenclature are compatible with IEC 268-5 and flags where the `Xmax` definitions differ, so AES2 serves as the readable equivalent for drive units. Any figure attributed to IEC 60268-5 elsewhere is second-hand. |
| IEC 60268-21 | Paywalled; not read | No substitute obtained. |
| AES56 (polar radiation measurement) | Only the front matter is public | AES2 defers directional measurement to AES56, so the measurement geometry for directivity is a step this repository cannot check at source. |

## 5. Choosing a model, and knowing where it stops

- **Lumped elements** (what `lf_box`, `crossover_network` and `board_nodal` are) hold while every
  dimension is small compared with a wavelength. No source consulted gives the frequency or `ka` at
  which lumped box modelling stops being valid, which is a real gap: cone break-up and internal
  standing waves arrive before anyone announces them.
- **Frequency-domain wave models** (FEM, BEM, hybrid) solve the Helmholtz equation; **time-domain**
  models solve the wave equation. They are different equations, so transient and nonlinear behaviour
  cannot be recovered from a frequency-domain run. Local nonlinear effects such as vortex shedding in
  a port exist only in the time domain.
- **Ray methods** are valid only where the wavelength is much smaller than the geometry — that is
  above the loudspeaker's own scale, in room acoustics.
- **Elements per wavelength — the rule, and why the rule is not enough.** The common rule of thumb
  is **6 to 10 degrees of freedom per wavelength**. For an element of order `P` that gives a maximum
  element size

  ```
  h = c P / (10 f_max)
  ```

  so quadratic elements (`P = 2`) at `f_max = 100 Hz` in air allow `h = 0.686 m`. The error bound
  behind the rule has **two** terms, and only the first is what the rule addresses:

  ```
  error <= C1 (k h / 2P)^P  +  C2 k (k h / 2P)^(2P)
  ```

  The first term is interpolation error. The second is **numerical dispersion — the pollution
  effect** — the accumulated phase error of a wave crossing many elements, and it carries an extra
  factor of `k`. **That is why a fixed number of elements per wavelength gets worse as frequency
  rises**, and the review that states the rule says so explicitly: it "becomes less valid as the
  frequency of interest is increased". A mesh specified as "8 per wavelength" is not a constant
  accuracy specification across a decade of frequency.

  What the rule does buy, when it holds: quadratic tetrahedral and hexahedral elements at 10 degrees
  of freedom per wavelength reproduce the analytic modal frequencies of a rigid-walled rectangular
  room to within **0.002 % to 0.08 %** over the first ten modes. Numerical accuracy against the
  governing equation is not the difficulty; see the paragraph on agreement below for the one that is.

  Treat any BEM or FEM result whose mesh density and element order are unstated as unquantified.
- **Direct-sound or point-source modes**, which skip the solve entirely, omit baffle diffraction and
  enclosure reflections — exactly the effects that shape the crossover region on a real cabinet. One
  vendor lists crossover design as an intended use of such a mode; treat that as marketing
  convenience.
- **Solvers have bugs.** One published changelog records a 10 to 20 percent calculation error for
  rectangular lumped elements across four builds, and wrong surface vibration across seven earlier
  ones. Record the tool and version in the design record, and re-run anything produced on a build
  later found to be wrong.

**The quantity no source supplied: agreement.** Not one source consulted states the decibel or degree
error between a simulated and a measured response for any tool. This has now been looked for
deliberately and the result is worth recording, because the shape of the absence is informative:

- **Numerical accuracy is published and is excellent** — the sub-0.1 % figures above. A solver can be
  shown to solve its own equation correctly.
- **Agreement with measurement is described qualitatively even in the review literature.** A 2023
  review of finite-element methods for room acoustics, surveying decades of work, reports studies
  comparing predictions with measured data as finding "qualitative agreement" and "good agreement"
  without attaching a figure to either.

So the gap is not that nobody has compared simulation with measurement; it is that **the comparison
is conventionally reported without a number.** The two are different quantities and must never be
substituted for one another: a solver's 0.01 % numerical error says nothing whatever about how far
its answer sits from a microphone. Every simulated result in this repository therefore carries no
error bar from the literature, only the model's declared assumptions and its validity range.

## 6. Two effects that ambush validation

- **Temperature and phase.** A 2 degree C change produces a 180-degree phase error at 10 kHz at a 5 m
  measurement distance. High-frequency phase from a long far-field measurement is fragile in a way
  amplitude is not.
- **Heat changes the load.** Copper rises about 0.39 percent per degree C, so a 6.6 ohm voice coil at
  150 C presents about 10 ohms. Every filter corner and every L-pad shifts with it; see
  `crossover-design.md` section 12.

## 7. What this framework's models contain, and what they do not

Linear, small-signal physics with declared priors. No distortion, no compression, no port noise, no
break-up beyond source data, no full room wave/scattering model and no joint behaviour. `room_response` adds finite-order rectangular-room reflections at physical receivers; see [room simulation](room-simulation.md). `thermal_power` supplies a declared voice-coil heating scenario; it does not establish enclosure endurance or nonlinear compression. Published data digitised from a
datasheet carries reading uncertainty, and a datasheet impedance prior is a prior, not a measurement.
The applications report; they do not judge. See `simulations/README.md` for the shared limits and each
app's own `README.md` for what its model includes.

A design document labels computed performance "predicted" or "simulated" and states the drive condition and consequential assumptions. Final stock values are selected through the simulation workflow, including sensitivity to uncertain inputs. Empirical certification is separate from a complete simulation-designed construction package; see `crossover-design.md` section 10.

## 8. Source ownership and validation practice

Keep the datum of every transfer explicit. `lf_box` pressure includes its external series resistance while its exported driver impedance excludes that resistance. For driver impedance `Z` and external resistance `Rs`, a source-voltage pressure becomes driver-terminal pressure by multiplying by `(Z+Rs)/Z`. This is voltage-divider algebra. `source_response` supports `acoustic.voltage_basis: driver_terminal`; apply the physical resistance once in the downstream network. Keep raw alignment/stress runs at their declared drive and use their own mechanical limits.

An acoustic level correction is a declared calibration, not a new parameter set. Compare source and published levels at the same drive, distance, band, horn/baffle and radiation space; retain graph anchors and reading uncertainty. Where conditions support it, a published measured curve is evidence for an acoustic calibration, but it does not validate the inferred phase or adjust the electrical/thermal/mechanical model. Apply the same calibration to cone and outlet pressure. State the resulting model consistency limits before inferring maximum output.

When combining a lumped bass model with a published wideband curve, define which owns each band's level and shape. Preserve modeled bass and replace the duplicate upper rolloff instead of multiplying the same slope twice. Check actual output against the graph above the blend and the unmodified bass below it. A curve from another horn or baffle is a different mounting prior, not measured installed data.

**Validation practice, not a measurement claim.** Run actual-source level, colocated cone/outlet, placed baffle/path and known-series-resistor checks before iteration one. Verify aggregate source equivalents independently for pressure, per-motor current and excursion; a low-frequency equivalent does not establish distributed cavity behavior. Record plausible acoustic-center uncertainty separately from large sensitivity probes, including common and relative shifts where appropriate. Freeze inputs and cold-replay the dependency chain before delivery; a numerical invariant checks implementation and conventions, not agreement with a microphone.

## Sources

- AES2-2012, *AES standard for acoustics - Methods of measuring and specifying the performance of loudspeakers for professional applications - Drive units* (revision of AES2-1984), Audio Engineering Society. Clauses 5.5 and 6 read at first hand. https://parkaudio.ua/DOCz/knowledgebase/aes02-2012-f.pdf
- A. J. Prinn, "A Review of Finite Element Methods for Room Acoustics", *Acoustics* 5(2), pp. 367-395, 2023 (open access). Source of the degrees-of-freedom-per-wavelength rule, the two-term error bound, the element-size formula and the FEM-versus-analytic accuracy table. https://www.mdpi.com/2624-599X/5/2/22
- F. Ihlenburg and I. Babuska, analyses of FEM error for wave problems, cited by the above as the origin of the error bound and the pollution effect; **not read at first hand**.
- S. Marburg, "Six boundary elements per wavelength: Is that enough?", *J. Comput. Acoust.* 10(1), pp. 25-51, 2002. The standard reference for the boundary-element form of the same question; **not obtained** (paywalled).

- ARTA Labs, application note AN4, "Free-field measurements" — the near-field and far-field limits, the near-field scaling factor, the baffle-step transfer function with its corner frequencies and rectangular equivalent width, and the gate and mounting-height arithmetic. <https://artalabs.hr/AppNotes/AN4-FreeField-Rev03eng.pdf>
- ARTA Labs, *LIMP user manual* — impedance jig selection and small-signal drive levels for parameter extraction. <https://artalabs.hr/download/LIMP-user-manual.pdf>
- Saunisto, K., *VituixCAD Measurement Preparations and Guide* (with REW) — timing offset, measurement distance, angular grids, gating and window choice, the two-diffraction splice procedure and near-field capture practice. <https://kimmosaunisto.net/Software/VituixCAD/VituixCAD_Measurement_REW.pdf>
- Klippel GmbH, "Multi-tone distortion" and "Compression of fundamental components" — the THD-versus-multitone argument, the nonlinearity fingerprints, the IEC 60268-21 clause map, and the separation of thermal from nonlinear compression. <https://www.klippel.de/know-how/measurements/nonlinear-distortion/multi-tone-distortion.html>
- Klippel GmbH, Application Notes AN4, AN5, AN18 and AN28 - the IEC 62458 excursion procedure, the parameter-based displacement limits, the thermal power-test protocol with its 130-percent-`Re` abort, and the pilot-tone method for monitoring a driver's temperature through a passive crossover. <https://www.klippel.de/know-how/literature/application-notes.html>
- Klippel GmbH, Near Field Scanner product documentation — the spherical-harmonic field reconstruction as a validation reference and the temperature-versus-phase error figure. <https://www.klippel.de/products/rd-system/modules/nfs-near-field-scanner.html>
- AKABAK 3 documentation and changelog, RandTeam — the hybrid BEM/lumped partition, the direct-sound mode's omissions, the non-uniqueness failure in thin-gap geometries, and the published solver-error builds. <https://www.randteam.de/AKABAK3/Index.html>
- COMSOL, *Acoustics Module* documentation — the frequency-domain against time-domain governing equations, the ray-acoustics validity limit, acoustic-structure coupling and the thermoviscous regime. <https://www.comsol.com/acoustics-module>
- Keele, D. B., Jr., "Low-Frequency Loudspeaker Assessment by Nearfield Sound-Pressure Measurement", *Journal of the Audio Engineering Society*, vol. 22, no. 3, 1974, and Struck, C. J., Temme, S. F., "Simulated Free Field Measurements", *Journal of the Audio Engineering Society*, vol. 42, no. 6, 1994 — the primary basis of the near-field method and of gated quasi-anechoic measurement.
- IEC 60268-21, *Sound system equipment — Part 21: Acoustical (output based) measurements* — the maximum-SPL and distortion measurement definitions cited second-hand above.
- In this repository: `simulations/README.md` for the limits shared by every application, `references/driver-selection.md` section 6 for parameter-extraction uncertainty, and `references/crossover-design.md` section 10 for what no simulation settles.
