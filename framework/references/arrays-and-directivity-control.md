---
id: arrays-and-directivity-control
applies_when: Arraying more than one source of the same passband - a line array, a column, a stacked pair or an MTM - or judging a claim about coupling, splay, coverage or throw
updated: 2026-09-15
---

# Arrays and directivity control

`baffle-and-driver-placement.md` governs the spacing between drivers that cross over to each other.
This reference governs the other case: **several sources reproducing the same band**, which is what a
line array, a column, a stacked subwoofer pair and the two woofers of an MTM all are. The controlling
physics is the same at every scale, and the criteria below are as binding on a 300 mm MTM as on a
5 m touring array — only the frequencies change.

**The one sentence that matters:** two sources reproducing the same band do not become one source
because they are close together. They become one source when the criteria in section 1 are met, and
they comb when they are not.

## 1. The five WST criteria for arrayability

Urban, Heil and Bauman derived, from a Fresnel analysis of the radiated field, the conditions under
which an array of discrete sources successfully approximates a continuous line source. These are
**physics with a derivation**, and they are stated as pass/fail conditions.

**Flat array — criterion 1 OR criterion 2 must hold, AND criterion 3 must hold:**

1. The sum of the individual **flat radiating areas covers more than 80 %** of the vertical frame of
   the array (the target radiating area);

   *or*

2. The **spacing between acoustic centres is smaller than `lambda/2`** at the highest operating
   frequency;

   *and*

3. The **deviation from a flat wavefront is less than `lambda/4`** at the highest operating
   frequency — 5 mm at 16 kHz.

**Curved array — the same three, plus:**

4. For cylindrical coverage over a given audience geometry, the product of **enclosure tilt angle and
   throw distance, `alpha d`, is constant**;

5. The maximum vertical cabinet size is bounded by

   ```
   STEP <= 2 d_min / (3 F_max ARF)
   ```

   where `ARF` is the Active Radiating Factor, `d_min` the closest listening distance and `F_max` the
   highest operating frequency.

### Why criteria 1 and 2 are stated as alternatives, and why waveguides exist

This is the part that transfers directly to ordinary loudspeaker design.

Criterion 2 is unsatisfiable at high frequencies with real hardware: `lambda/2` at 16 kHz is about
**10.7 mm**, and no two drivers have acoustic centres that close. So criterion 1 has to carry the
array — the radiating surfaces have to nearly fill the frame.

But criterion 1 is also unsatisfiable with circular sources. `ARF` is the fraction of the frame that
actually radiates, and for **touching circular sources the average `ARF` is `pi/4 = 78.5 %`** — which
is below the 80 % threshold before any gap, mounting flange or cabinet wall is allowed for. The
paper's own conclusion: it is therefore impossible to satisfy the first criterion with circular
sources, and this is precisely what the waveguide is for. A waveguide converts a small circular
driver into a tall, nearly rectangular radiating aperture that can fill the frame.

**So the existence of horn-loaded HF sections in arrays is not about efficiency or pattern control
first — it is about being able to satisfy criterion 1 at all.** Note also that the paper reports an
optimum number of sources of five for a simple array, citing Keele's work on Bessel arrays.

### Application at domestic scale

Criterion 2 is the same constraint that `system-architecture.md` states as `d1/lambda` at the
crossover frequency, arrived at independently. For an MTM with woofers 180 mm apart acoustic centre
to acoustic centre, criterion 2 holds up to `c/(2 x 0.180) = 953 Hz`. Above that, the two woofers are
no longer a single source and the vertical pattern develops the nulls that the `c/(2d)` formula
predicts. **That is the number that should set the crossover frequency**, and it is available before
any fitting is done.

## 2. Near field, far field and how level falls with distance

A line source of height `H` radiates into two spatially distinct regions with **different distance
laws**:

- **Near field:** SPL falls **3 dB per doubling of distance** (cylindrical propagation).
- **Far field:** SPL falls **6 dB per doubling of distance** (spherical propagation).

The border between them is

```
d_B = (3 F H^2 / 2) * sqrt( 1 - ( 1 / (3 F H) )^2 )

F   frequency in kHz
H   height of the line source in metres
d_B border distance in metres
```

Worked check against the paper's example: a flat continuous line source of `H = 5.4 m` at `F = 2 kHz`
gives `d_B = (3 x 2 x 29.16 / 2) x sqrt(1 - (1/32.4)^2) = 87.4 m`, matching the published figure of
88 m. Three consequences the authors draw from the formula, all reproduced by it:

1. **There is no near field below `F = 1/(3H)`** — the root goes imaginary. A 4 m array radiates in
   far-field mode immediately for frequencies below about 80 Hz. **An array does not control its own
   bass**, no matter how tall.
2. Above `1/(3H)`, near-field extent is approximately **linear in frequency**.
3. Dependence on array height is **quadratic**, not linear. Doubling the height quadruples the near
   field.

Polar plots and directivity figures are **meaningless inside the near field** — they describe a
far-field property. Any directivity claim has to say at what distance it was measured and whether
that distance is beyond `d_B` at the frequency in question.

## 3. Practical consequences for coverage

From the same source and its worked design example:

- **Level taper is a design target, not a defect.** Listeners further from the stage should be
  *quieter*: a maximum front-to-back loss of about 6 dB is described as very good, and the worked
  example achieves 7 dB between 4 m and 20 m by choosing tilt angles and per-cabinet gains.
- Criterion 4 (`alpha d` constant) is what produces that: cabinets aimed at distant listeners get
  small splay angles, cabinets covering near listeners get large ones, and the product stays fixed.
- **An abrupt change in splay between a far-field section and a near-field section leaves a region of
  low SPL and poor intelligibility** between them. Splay should progress smoothly.
- Atmospheric absorption is humidity dependent and acts on the longest throws at the highest
  frequencies; it is not a correction that can be applied once for a whole audience.

## 4. What is not established here

No source consulted gives: a quantitative intelligibility metric (STI, %ALcons or C50) related to
array geometry; critical distance as a function of room absorption and array directivity; the
prediction error of any array-modelling software against measurement; splay-angle optimisation as an
algorithm rather than as the `alpha d` rule; or any treatment of horizontal arraying. Coupling of
subwoofers into end-fire or gradient arrangements is touched on in `alternative-loadings.md`
section 4 and is otherwise not covered.

## Sources

- M. Urban, C. Heil and P. Bauman, "Wavefront Sculpture Technology", J. Audio Eng. Soc. 51(10), pp. 912-932, October 2003, L-ACOUSTICS. Read at first hand; the five criteria, the `ARF` result and the near-field border formula are taken from it and the border formula was recomputed against the paper's own example. http://www.l-acoustics.com/wp-content/uploads/2026/04/Wavefront_Sculpture_Technology_jaes.pdf
- C. Heil and M. Urban, "Sound Fields Radiated by Multiple Sound Source Arrays", AES 92nd Convention, May 1992, preprint 3269. The earlier derivation the 2003 paper rests on; **not read at first hand**.
- D. B. Keele, Jr., "Effective Performance of Bessel Arrays", J. Audio Eng. Soc. 38, pp. 723-748, October 1990. Cited by the above as the source of the optimum-five-sources result; **not read at first hand**.
- D. L. Smith, "Discrete-Element Line Arrays - Their Modeling and Optimization", J. Audio Eng. Soc. 45, pp. 949-964, November 1997. Cited as an alternative treatment; **not read at first hand**.
- C. Demard, "Acoustic coupling and directivity control", Revue Scientifique des Ingenieurs Industriels no. 34, 2020. A secondary account that restates criteria 1-3 in design form and supplied the worked coverage example; used as a cross-check on the primary paper. https://luck.synhera.be/bitstream/handle/123456789/398/ISILF20p39pierrard.pdf
