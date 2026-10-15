---
id: alternative-loadings
applies_when: Considering a loading other than sealed, vented or passive-radiator - bandpass, isobaric, aperiodic or cardioid - or judging a claim made for one of them
updated: 2026-09-15
---

# Loadings other than sealed and vented

`enclosure-alignments.md` covers sealed and vented boxes, where the alignment mathematics is settled
and the alignment tables are Small's. This reference covers the loadings that get proposed next. Each
section says what is established, what is derived here from established definitions, and what nobody
has published a usable number for.

**The common thread: none of these loadings makes a driver bigger.** Every one of them redistributes
something — bandwidth for gain, volume for sensitivity, output for pattern control. Where a section
below gives the exchange rate, that rate is the point of the loading, and a design that claims the
benefit without paying the price has an error in it.

## 1. Bandpass boxes

### The topology and what it buys

A fourth-order bandpass box is a Helmholtz resonator placed in front of a conventional sealed box.
The driver radiates into the front chamber only; **all output leaves through the front port.** The
sealed rear chamber gives the high-pass, the front Helmholtz resonator gives the low-pass, and the
"order" of a bandpass box is the sum of the two.

The defining property is that **bandwidth and gain are exchangeable.** Narrowing the passband raises
the midband level, because the same displacement-limited volume velocity is concentrated into fewer
octaves. This is characteristic of every bandpass topology and it is the only reason to build one.
It is also the honest description of the "extra output" such boxes are sold on: the output is not
created, it is moved out of the band that was given up.

### Component values from an equivalent circuit

The model is the standard lumped-element one, with the same acoustic-domain analogy used for vented
boxes: current is volume velocity, voltage is pressure. For a front chamber of volume `VBF`, tuned to
`fBF`, with chamber loss quality factor `QLF`:

```
CABF  = VBF / (rho0 c^2)                 front chamber acoustic compliance
LMAPF = 1 / ( (2 pi fBF)^2 CABF )        front port acoustic mass
RALF  = QLF / (2 pi fBF CABF)            front chamber leakage loss
```

with the same three lines applied to the rear chamber, and driver losses entered as in the vented-box
model. Worked check against the published example (`VBF = 40 litres`, `fBF = 30 Hz`, `QLF = 10`,
`rho0 = 1.20`, `c = 343.68`):

```
CABF  = 0.040 / (1.20 x 343.68^2)            = 2.822e-7     (published 2.8220e-7)
LMAPF = 1 / ((2 pi x 30)^2 x 2.822e-7)       = 99.73        (published 99.730)
RALF  = 10 / (2 pi x 30 x 2.822e-7)          = 1.880e5      (published 1.87993e5)
```

All three reproduce. The same method extends to the sixth-order bandpass (two external ports, or one
internal and one external), the eighth-order (three chambers), the fourth-order with a passive
radiator in place of the rear seal, and the two-chamber double-driver box.

### The failure mode that is not optional

**The acoustic low-pass stops working, and the box then leaks everything above it out of the port.**
The front chamber acts as a low-pass only while the port behaves as a lumped mass. A port is a tube
open at both ends, so on its end-corrected length `L_eff = L_physical + 0.732 d`:

```
f_lumped_limit    ~= c / (4 L_eff)    the lumped model under-states the port flow by 3.9 dB here
f_port_resonance  ~= c / (2 L_eff)    first pipe resonance: port output peaks
```

At the quarter-wave point the exact tube passes `kL / sin kL = pi / 2` times the flow the lumped mass
predicts, and the error grows from there to the half-wave resonance, where the port radiates the
out-of-band energy straight through. The chamber's compliance lifts the resonance only slightly,
because a port tuned well below its pipe frequency sees the chamber as nearly an open end. The
published simulations, comparing a lumped-mass port model against the same port modelled as a
transmission line terminated in its radiation impedance, make the conclusion flat: **an electrical
low-pass filter is in practice mandatory on a bandpass box.** A design that relies on the enclosure
alone for its low-pass is relying on a model that has stopped being true.

**A claim checked and corrected.** The source states that "the first port resonance frequency is
just at" the frequency where the wavelength is four times the port's physical length. That is the
resonance of a tube closed at one end. A distributed-tube calculation of a port on its chamber,
repeated in `framework/tests/test_source_round_two.py`, puts the first output peak at `c / (2 L_eff)`
for chambers of 20 to 80 L; `c / (4 L)` on the physical length was off by nearly a factor of two.
The quarter-wave figure survives only as the point where the lumped model starts to fail.

This also constrains geometry: a long port pushes both frequencies down into the region the box was
supposed to filter. A bandpass box with a long, narrow port is the worst case, and that is exactly
what a low tuning in a small chamber asks for.

### Status

The equivalent-circuit derivations above come from a self-published technical paper by the author of
a widely used enclosure-modelling program. The arithmetic was checked here and the method is the
standard lumped-element analysis already used for vented boxes in `enclosure-alignments.md`, so the
*mechanics* can be relied on. **No bandpass alignment tables — the equivalent of Small's `B4`, `QB3`
and `BL4` families — were obtained from any source.** Bandpass design here therefore means solving
the circuit for a chosen geometry and reading the result, not looking up an alignment. Say that in
the candidate notes rather than implying a tabulated alignment was used.

## 2. Isobaric (compound) loading

Two identical drivers are mechanically coupled in tandem, cone to cone or cone to magnet, with a
small sealed volume of air between them, so they move as one. Only one diaphragm radiates into the
enclosure.

**Derived here from the Thiele/Small definitions in `driver-selection.md`**, for the coupled pair
treated as a single driver. Both suspensions resist the same displacement, so stiffnesses add and
`Cms` halves; both moving masses move together, so `Mms` doubles:

```
Mms' = 2 Mms          Cms' = Cms / 2          SD' = SD

fs'  = 1 / (2 pi sqrt(Mms' Cms')) = 1 / (2 pi sqrt(Mms Cms)) = fs     unchanged
Vas' = rho0 c^2 SD'^2 Cms' = Vas / 2                                  halved
VD'  = SD' xmax = VD                                                  unchanged
```

`Qts` is unchanged for both series and parallel wiring. In series, `RE' = 2 RE` and the force per unit
current doubles so `Bl' = 2 Bl`, and `Qes' = (RE'/Bl'^2) sqrt(Mms'/Cms') = (2 RE / 4 Bl^2) x 2 sqrt(Mms/Cms) = Qes`.
In parallel, `RE' = RE/2` and `Bl' = Bl`, giving the same result. Reference efficiency follows:

```
eta0' = 9.6e-10 fs'^3 Vas' / Qes' = eta0 / 2        i.e. 3 dB lower
```

So the exchange rate for isobaric loading is:

| Quantity | Change |
|---|---|
| Box volume for a given alignment | **halved** |
| `fs`, `Qts`, alignment family, `f3/fs` | unchanged |
| Reference efficiency | **-3 dB** |
| Thermal power handling | doubled |
| Displacement-limited output `VD` | unchanged |
| Drivers, cost, mass | doubled |

Because efficiency drops 3 dB and power handling doubles, **the maximum output is the same as one
driver** — you have bought box volume with money and amplifier power, nothing else. The claim that
isobaric loading gives lower distortion is plausible (the two motors' asymmetries partially cancel
when mounted face to face) but **no measurement supporting it was obtained**, so do not carry it into
a candidate as a benefit.

This derivation is checkable arithmetic from definitions already established in this repository. It
is **not** quoted from a primary source, and no source consulted here states the isobaric parameter
transformation at first hand. Treat it as a derivation to be re-checked, not as a citation.

## 3. Aperiodic loading

An aperiodic enclosure vents the box through a **damped** port — a vent packed or covered with
resistive material, sometimes called an acoustic resistor. In the equivalent circuit this is simply
the vent branch with a series acoustic resistance `RAV` added to the vent mass `LMAV`.

That single change spans the two familiar loadings and the physics is unambiguous at the limits:

```
RAV -> infinity   the vent branch carries no volume velocity        -> sealed box
RAV -> 0          the vent branch is a pure Helmholtz resonator     -> vented box
```

An aperiodic vent is therefore a continuously variable position between sealed and vented, and its
purpose is to damp the system resonance so that a smaller box reaches an acceptable `Qtc` than a
sealed box of the same volume would. That much follows from the circuit and can be simulated with the
machinery already in place.

**What is not established here:** the rolloff slope of a practical aperiodic box (claims of 18
dB/octave were found but not in any source that derives them), any alignment table, the relationship
between stuffing density or vent-covering material and `RAV` in SI units, and whether the vent's
resistance is usefully constant with frequency and level. Without a value for `RAV` the model has a
free parameter and cannot predict anything; it can only explore. Say so.

## 4. Cardioid and gradient loading

### The pattern

A cardioid is the first-order gradient pattern: the sum of a monopole and a dipole of equal far-field
strength. The directional function is

```
D(theta) = 1 + cos(theta)          normalised:  rho(theta) = 0.5 + 0.5 cos(theta)
```

giving unity forward, `-6 dB` at 90 degrees and a null at 180 degrees. Olson's gradient loudspeaker
(1973) is the general case: "a loudspeaker consisting of two or more loudspeakers separated in space
and operating with a difference in phase", and by varying the ratio of the monopole and dipole terms
the same arrangement produces omnidirectional, dipole or cardioid patterns.

### The practical realisation and its two limits

The usual implementation is two sources separated by `d` along the axis, the rear one inverted in
polarity and delayed by `d/c`, so that at the rear the two arrivals are equal and opposite. This
works over a band bounded at both ends, and both bounds are physics:

- **Upper limit — spacing.** The rear cancellation depends on the two arrivals being in anti-phase.
  As `d` approaches `lambda/2` that ceases to hold and the pattern breaks up. This is the same
  spacing criterion that governs any two-source array; see `arrays-and-directivity-control.md`
  section 1.
- **Lower limit — gradient efficiency.** A first-order gradient source's output falls at 6 dB/octave
  relative to a monopole of the same volume velocity as frequency drops, because the pattern is
  produced by a path-length difference that shrinks with wavelength. Holding the cardioid down in
  frequency costs 6 dB of drive per octave, paid in excursion and power.

Between them, the practical usable passband of a cardioid arrangement is reported as **2 to 2.5
octaves**. That figure comes from a patent specification, not from a measurement series, and is
flagged accordingly — but the two limits that produce it are sound, and any cardioid design that
claims a wider band should be asked which of them it escaped.

### Status

The pattern equation and the gradient principle are physics. The delay-and-invert realisation is
standard practice. **No source consulted gives the cardioid arrangement's alignment mathematics** —
how box tuning, vent resistance and delay interact when the rear source is a resistive vent rather
than a second driver, which is how most passive cardioid cabinets are actually built. That
combination is unmodelled here.

## 5. Not covered at all

Transmission lines are in `enclosure-alignments.md` section 5. Beyond that: horn loading is in
`horn-and-waveguide-design.md`. Nothing here covers tapped horns, the "ABC" box beyond its
appearance in the equivalent-circuit source, band-pass alignment tables, active or motional-feedback
loading, or any loading whose behaviour depends on a nonlinear or level-dependent element.

## Sources

- J. Ahonen, "Electroacoustic modelling of the subwoofer enclosures", Linearteam technical paper, 6 July 2007. Source of the bandpass equivalent circuits, component-value method and the port-resonance caution; worked example recomputed and verified here. Its quarter-wave statement of the first port resonance was checked and corrected to the half-wave one (section on the failure mode). **Self-published** by the author of enclosure models for the WinISD Pro program; the method is the standard lumped-element analysis, the arithmetic was checked, and it is flagged as self-published rather than peer-reviewed. http://jahonen.kapsi.fi/Audio/Papers/enclosuremodelling.pdf
- R. H. Small, "Direct-Radiator Loudspeaker System Analysis", J. Audio Eng. Soc. 20, pp. 383-395, June 1972, and the vented-box series. The parameter definitions the isobaric derivation in section 2 is built on; already established in `driver-selection.md` and `enclosure-alignments.md`.
- H. F. Olson, gradient loudspeaker work (1973), for the definition of a gradient loudspeaker and the first-order pattern family. Known through secondary description; **not read at first hand**.
- US Patent 10893345, "Compact speaker system with controlled directivity", for the reported 2 to 2.5 octave practical passband of a cardioid arrangement. A patent specification, not a measurement series. https://patents.google.com/patent/US10893345
- E. R. Geddes, "Introduction to Bandpass Loudspeaker Enclosures", J. Audio Eng. Soc. 37(5), May 1989. The standard reference for bandpass alignment; **not obtained** (AES e-library, paywalled). Its absence is why section 1 has no alignment tables.
