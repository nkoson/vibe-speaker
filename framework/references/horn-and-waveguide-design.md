---
id: horn-and-waveguide-design
applies_when: Designing or judging a horn or waveguide - sizing a throat, a rear cavity or a mouth, predicting the band a horn will work over, or deciding whether a horn model can answer the question at all
updated: 2026-09-15
---

# Horn and waveguide design

A horn is two different problems wearing one name. **Loading** is what the horn does to the driver's
radiation impedance, and it is what Webster's horn equation was written to predict. **Directivity** is
what the mouth does to the radiated pattern, and Webster's equation cannot see it at all. The two
problems have different mathematics, different valid ranges and different failure modes, and most
confusion about horns comes from answering one with the other.

This reference covers low-frequency horn design from Thiele/Small parameters, the boundary of
Webster's equation, and the oblate-spheroidal waveguide. Horn *directivity* from mouth dimensions is
in `transducer-types.md` section 3 (Keele's constant-directivity relation); read both before designing
a horn section.

## 1. Low-frequency horn design from Thiele/Small parameters

Keele recast the classical horn equations into the Thiele/Small parameters a driver's datasheet
actually carries. The whole set below is **physics**, derived in the source, and it is the reason a
bass horn can be designed without ever measuring `Bl`, `Cms` or `Mms`.

Throughout: `fc` is the horn cutoff frequency, `ST` the throat area, `VB` the rear (back) cavity
volume, `VFC` the front cavity volume, `VD = SD xmax` the driver's peak displacement volume, `c` the
speed of sound, `rho0` the density of air. SI units throughout — **`Vas` and `VB` in cubic metres,
not litres**, in every formula on this page.

### Throat area for maximum efficiency

```
ST = 2 pi fs Qts Vas / c
```

This is the throat that makes the horn's reflected load resistance equal the driver's `RE`, which
maximises midband efficiency. The midband nominal efficiency itself is

```
eta = 2 RE RET / (RE + RET)^2        RET = ST Bl^2 / (rho0 c SD^2)
```

which peaks at **50 %** when `RET = RE`. Keele's own conclusion, credited to correspondence with
Richard Small, is that this is **not** automatically the throat you want: traditional horn design
fixes the throat area to maximise efficiency, and since many of the horn's other performance
characteristics depend heavily on throat area, that constraint "removes one valuable degree of design
freedom". Treat the equation as the efficiency-optimal point, not as the answer.

### Rear cavity volume for reactance annulling

The rear cavity's compliance is used to cancel the horn's throat mass reactance near cutoff
(Klipsch's reactance annulling). The condition is that the driver mounted in its closed rear cavity
has its lower resistance-controlled bound sitting at the horn cutoff:

```
fLS (1 + alpha) = fc = 2 fLBC          alpha = Vas / VB
```

Solved for the cavity:

```
VB = Vas / ( fc / (fs Qts) - 1 )
```

and when the box dominates the total compliance (`Vas >> VB`) this reduces to

```
VB ~= Vas fs Qts / fc        equivalently    VB = ST c / (2 pi fc) = ST lambda_c / (2 pi)
```

**The sign of the denominator is the driver-suitability test.** `VB` is finite and positive only when
`fLS < fc`, that is when `fs Qts < fc`. If `fs Qts >= fc`, the driver is not suited to a horn at that
cutoff frequency — no cavity volume will annul the reactance. This is one line of arithmetic and it
rejects unsuitable drivers before any modelling.

### The band the driver can work over

```
fHS = fs / Qts          upper bound of the resistance-controlled region
fLS = Qts fs            lower bound
fs  = sqrt(fLS fHS)
fHS / fLS = 1 / Qts^2
```

That last ratio is the single most useful number in horn driver selection: **the width of the usable
band goes as `1/Qts^2`**, so a low `Qts` (strong motor, large magnet) is what buys bandwidth. A
`Qts = 0.21` driver has a resistance-controlled region spanning `1/0.21^2 ~= 23` — about 4.5 octaves.
A `Qts = 0.45` driver spans under five. This is physics, not preference.

### High-frequency rolloff corners

Three separate mechanisms roll the response off at the top, and in practice they usually arrive in
this order:

```
1. driver moving mass       fHM  = 2 fs / Qts = 2 fHS
2. voice-coil inductance    fHVC = RE / (pi LE)
3. front cavity compliance  fHC  = 2 Qts fs (Vas / VFC)
```

giving 6 dB/octave above `fHM`, 12 above `fHVC` and 18 above `fHC`. The composite rolloff in a real
design is a combination of all three; the individual corners give the shape, not the exact curve.
**The front cavity is the one the designer controls**: `fHC` is inversely proportional to `VFC`, so
the volume trapped between the cone and the throat sets the top of the horn's passband. Keep it small
or accept the corner.

### Displacement-limited maximum acoustic output

```
PAR ~= (3 pi rho0 c^2 / 2) * ( 1 / (fs Qts Vas) ) * fc^2 VD^2

with  3 pi rho0 c^2 / 2 ~= 6.7e5   in SI units
```

Equivalently, in electromechanical form, `PAR ~= 3 pi^2 Bl^2 xp^2 fc^2 / RE`. The approximation
carries one stated assumption: for a well-designed finite exponential horn with optimum mouth size,
the low-frequency efficiency is down no more than **0.3 dB** from maximum midband efficiency at
`1.26 fc`, and `PAR` is the output available down to that frequency. Thermal limits are a separate
ceiling and are not in this equation.

### Worked example, reproduced

Keele's example is a 12-inch driver into a 50 Hz exponential horn: `fs = 45 Hz`, `Qts = 0.210`,
`Vas = 140 litres = 0.14 m^3`, `SD = 5.0e-2 m^2`, `xmax = 3.3 mm`, `VD = 1.66e-4 m^3`, `RE = 5.6 ohm`,
`LE = 3.2 mH`, `VFC = 1.1 litre`. The published results recompute exactly:

| Quantity | Formula | Result |
|---|---|---|
| `ST` | `2 pi (45)(0.21)(0.14)/343` | `2.42e-2 m^2` = 242 cm2 |
| `VB` | `140 / (50/(45 x 0.21) - 1)` | 32.6 litres |
| `fHS` | `45/0.21` | 214 Hz |
| `fLS` | `0.21 x 45` | 9.5 Hz |
| `fHM` | `2 x 214` | 430 Hz |
| `fHVC` | `5.6/(pi x 0.0032)` | 560 Hz |
| `fHC` | `2 x 9.5 x 140/1.1` | 2400 Hz |
| annulling check | `9.5 (1 + 140/32.6)` | 50 Hz = `fc` |
| `PAR` | `6.7e5 (50)^2 (1.66e-4)^2 / (45 x 0.21 x 0.14)` | 35 acoustic watts |

Every line above was recomputed here and agrees with the paper. **Note what the rear cavity does to
the design: 32.6 litres of cavity behind a 12-inch driver, plus the horn itself.** A bass horn's size
is set by this equation, and the number is usually the reason the design is abandoned.

## 2. Where Webster's horn equation stops being valid

Webster's equation assumes plane-wave propagation. Morse's condition for that assumption, applied to
an exponential horn of throat area `S0` and flare rate `m`, is

```
d/dx [ S0 e^(m x) ] << 1.0          "<<" conventionally read as < 0.1
```

Geddes, working a published example, finds this is satisfied only over roughly the first 15 to 20 cm
of a horn whose total length is 40 cm. Beyond that the equation is not reliable. He also gives a
geometric test that lands at the same place and is easier to apply: **draw a line from the centre of
the throat tangent to the wall contour; where the walls recede past that line, the wavefront would
have to diffract to stay attached to them, and Webster's equation is blind to that diffraction.**

Two consequences, both from Geddes at first hand:

- **Impedance survives the violation; pattern does not.** Acoustic impedance is an average of the
  wavefront across the guide, so Webster's equation "does an admirable job of predicting the
  impedance of a wide variety of horn contours" even outside its strict validity. Directivity is a
  detail of the wavefront and the equation cannot predict it.
- **Shape barely moves the impedance anyway.** Geddes: "virtually any shape connecting a given throat
  and mouth area will yield approximately the same impedance — within a dB or so. In the long
  wavelength region where the Horn Equation is valid, shape is simply not a significant factor, the
  waves don't see shape." This is a judgement by a specialist rather than a published measurement
  series, and it is stated here because it is decision-changing: it says a throat-impedance solver
  that distinguishes exponential from hypex from conical is computing a distinction of about 1 dB.

## 3. The oblate-spheroidal (OS) waveguide

The OS waveguide is the contour that follows the coordinate surfaces of the oblate spheroidal
coordinate system. In Cartesian terms the radius is

```
r(x) = sqrt( rt^2 + tan^2(theta0) x^2 )
```

where `rt` is the throat radius and `theta0` is **half** the included coverage angle. Kolbrek and
Geddes state the same contour independently. Geddes notes that all eleven orthogonal coordinate
systems that admit wave solutions share this one boundary shape (a catenoid), straight or of the form
above — so this curve is not one horn family among many, it is the shape that the geometry of the
wave equation picks out.

The OS waveguide has no sharp cutoff. Defining a cutoff at the frequency where throat resistance
falls to 0.2 of its asymptotic value, so that it means roughly what it means for an exponential horn:

```
fc = 0.2 c sin(theta0) / (pi rt)
```

Worked check: a 1-inch throat (`rt = 12.7 mm`) with a 60-degree included angle (`theta0 = 30 deg`)
gives `fc = 0.2 x 344 x 0.5 / (pi x 0.0127) = 862 Hz`, matching the published figure. **A low cutoff
needs a big throat or a narrow angle**, which is exactly why OS waveguides are poor at low
frequencies: like conical horns, they get very long and narrow before they load anything in the bass.

Throat impedance for the OS waveguide has no closed form and must be integrated numerically.

## 4. Higher-order modes

For a one-parameter (1P) wave to propagate in a 1P device it must be launched by a 1P source
wavefront. A dome diaphragm vibrates axially, not radially, so it is not a 1P source, and **no real
device is.** Any non-1P excitation, and any discontinuity anywhere in the throat, phase plug or
contour, generates **higher-order modes (HOMs)** — wave motion the horn equation does not predict
because Webster's solution does not contain those terms.

What is established:

- Above a frequency set by throat radius and horn angle, HOMs exist in an OS waveguide and the 1P
  assumption fails. **Neither source consulted gives that frequency as a formula**, only that it
  exists and that it is set by those two quantities. Do not invent one.
- Waveguides based on the orthogonal coordinate geometries generate the fewest HOMs of any contour
  joining the same throat and mouth apertures. That is Geddes' claim of optimality and it is the
  actual argument for the OS shape — not loading.
- Geddes reports that HOM audibility *increases* with level, the opposite of nonlinear distortion,
  and attributes perceived horn "harshness" to it. That is a designer's conclusion from his own
  listening work, not an independently verified measurement, and is labelled as such.

## 5. What this means for building a horn model

Read together, the sources above say something specific about where effort belongs, and it is not
where horn folklore puts it:

- **Computing throat impedance from the flare profile is low value.** Shape moves it by about a dB in
  the band where the model is valid, and the model is invalid where shape matters.
- **Computing the design quantities from Thiele/Small parameters is high value.** `ST`, `VB`, the
  `fs Qts < fc` suitability test, `fHS/fLS = 1/Qts^2`, the three HF corners and `PAR` are all closed
  form, all cheap, and each of them settles a decision.
- **Directivity comes from the mouth, through Keele's constant-directivity relation, not from the
  flare.** See `transducer-types.md` section 3.
- **A horn model cannot state its own accuracy above the first break-up of the driver**, and for a
  compression driver that is a measured frequency, not a simulated one (`transducer-types.md`
  section 2).

## 6. Not covered

Compression ratio and throat-cavity volume for compression drivers; horn efficiency as a function of
throat-to-mouth area ratio; the power-response tilt that horn EQ has to correct; folded-horn path
design and the frequency at which a fold begins to misbehave; multi-cell and radial horn pattern
prediction; and the HOM cutoff frequency as a formula. None of these were obtained from a source that
states them quantitatively.

## Sources

- D. B. Keele, Jr., "Low-Frequency Horn Design Using Thiele/Small Driver Parameters", AES 57th Convention, Los Angeles, May 1977, preprint 1250 (K-7), Klipsch & Associates. Read at first hand; Table I, the design example and the appendix conversions are reproduced and recomputed above.
- E. R. Geddes, "Letter to the Editor, AudioXpress" (reply to Kolbrek's horn theory series), gedlee.com. First-hand statement of Webster validity, the OS/catenoid boundary, HOMs and the shape-versus-impedance claim. http://www.gedlee.com/Papers/Horn%20Theory%20reply.pdf
- B. Kolbrek, "Horn Theory: An Introduction, Part 2", audioXpress, 2008. Source of the OS contour and cutoff equations as stated here, independently of Geddes. https://audioxpress.com/assets/upload/files/kolbrek2885.pdf
- E. R. Geddes, "Acoustic Waveguide Theory", J. Audio Eng. Soc. 37(7), pp. 554-569, 1989, and "Acoustic Waveguide Theory Revisited", JAES 41(6), pp. 452-461, 1993. Cited by both sources above as the origin of the OS waveguide solution; **not read at first hand** (AES e-library, paywalled).
- P. M. Morse and H. Feshbach, *Methods of Theoretical Physics*, McGraw-Hill, 1953. Origin of the Webster validity condition, quoted via Geddes; not read at first hand.
- P. W. Klipsch, "A Low-Frequency Horn of Small Dimensions", J. Acoust. Soc. Am. 13, pp. 137-144, Oct. 1941. Origin of reactance annulling, cited by Keele; not read at first hand.
