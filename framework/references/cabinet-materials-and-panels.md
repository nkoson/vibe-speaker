---
id: cabinet-materials-and-panels
applies_when: Choosing a cabinet material or wall thickness, predicting or judging a panel resonance, specifying damping treatment, or deciding whether panel radiation will be audible
updated: 2026-10-15
---

# Cabinet materials and panel radiation

`cabinet-geometry.md` sizes a box. This reference is about what the box is made of: the elastic and
damping properties of the candidate materials, where a panel's modes will land, how much damping a
treatment actually buys, and the one published criterion for whether the resulting radiation is
audible.

**Read the conclusion first, because it inverts a common assumption.** The BBC's measurement
programme found that a cabinet of **double** wall thickness radiated *more* from its panels than the
standard thin-wall cabinet of the same external dimensions, because the thicker panel's `Q` was
higher. Thickness is not a damping strategy. The material's loss factor and the applied damping are
the strategy, and the two must be chosen together.

## 1. Material properties

### Elastic modulus and density

Two independent sources, measured for different purposes. Use them together: the Wood Handbook is
the statistically grounded engineering reference, the BBC data is the only set measured *as a
function of frequency across the audio band*, which is what a panel-mode calculation needs.

**Wood Handbook (static bending, Table 12-1).** Specific gravity and modulus of elasticity:

| Material | Specific gravity | MOE (GPa) | MOR (MPa) |
|---|---|---|---|
| Hardboard | 0.9-1.0 | 3.10-5.52 | 31.0-56.5 |
| Medium-density fibreboard (MDF) | 0.7-0.9 | 3.59 | 35.9 |
| Particleboard | 0.6-0.8 | 2.76-4.14 | 15.2-24.1 |
| Oriented strandboard | 0.5-0.8 | 4.41-6.28 | 21.8-34.7 |
| Plywood | 0.4-0.6 | 6.96-8.55 | 33.7-42.6 |
| White oak (clear) | 0.68 | 12.27 | 104.8 |
| Douglas-fir, coastal (clear) | 0.48 | 13.44 | 85.5 |

**This table places MDF below plywood in stiffness, but some hardboard and particleboard values are lower still.** Its attraction is uniformity and machinability, not stiffness.

**BBC measured data (Tables 1 and 2), density in g/cm3, `E` in GPa at 250 Hz, `Q` the maximum
measured quality factor, and `sqrt(E rho)/Q` the BBC's own figure of merit — higher is better:**

| Material | rho | Max `Q` | `E` @250 Hz | `sqrt(E rho)/Q` x1e-5 |
|---|---|---|---|---|
| 9 mm birch 7-ply, along outer grain | 0.72 | 67 | 12.0 | 0.044 |
| 9 mm birch 7-ply, across outer grain | 0.72 | 63 | 5.3 | 0.031 |
| 17 mm birch 13-ply, along | 0.74 | 54 | 7.3 | 0.043 |
| 17 mm birch 13-ply, across | 0.73 | 54 | 6.9 | 0.042 |
| 10 mm mahogany 5-ply, along | 0.61 | 97 | 7.9 | 0.023 |
| 12 mm birch-faced blockboard, along | 0.535 | 68 | 7.4 | 0.029 |
| 16 mm 3-layer chipboard (0.600 density) | 0.60 | 50 | 1.95 | 0.021 |
| 18 mm 3-layer chipboard (0.600 density) | 0.61 | 45 | 2.2 | 0.026 |
| Hardboard (10 mm Duopanel) | 0.99 | 51 | 4.8 | 0.043 |
| Oak, along the grain | 0.63 | 96 | 14.7 | 0.032 |
| Oak, across the grain | 0.585 | 50 | 0.97 | 0.015 |
| Beech, along the grain | 0.68 | 125 | 14.6 | 0.025 |
| Deal, along the grain | 0.57 | 120 | 14.2 | 0.024 |
| GRP, 50 % random fibres | 1.55 | 47 | 10.3 | 0.085 |
| Carbon fibre / honeycomb sandwich | 0.255 | 170 | 12.5 | 0.009 |

Read four things off this table:

- **Solid timber needs explicit anisotropy and variability assumptions.** Oak's modulus is 14.7 GPa along the
  grain and 0.97 across it — a factor of 15 — and its `Q` runs to 96. Beech and deal reach `Q = 125`
  and `Q = 120`. A resonance with `Q = 120` rings for a long time. The BBC's conclusion is explicit:
  "plain timber is an unreliable material because of its variability and its inherent anisotropy."
  This matters even for fillets: replacing Parana pine fillets with beech in an LS3/5A changed the
  coupling between panels enough to drop a 350 Hz panel peak by **9 dB**, taking it from clearly
  audible ("honky", worst on speech) to inaudible.
- **Plywood is preferred over chipboard**, per the BBC, because it comes in more thicknesses and has
  fewer resonant modes for a given configuration — not because of a damping advantage.
- **Carbon-fibre honeycomb is a trap.** It has the highest modulus-to-weight in the table and the
  *worst* figure of merit, because `Q = 170`. Stiffness without loss moves the resonance, it does not
  remove it.
- **`E` varies with frequency**, by roughly 10-20 % over 62.5 Hz to 6 kHz for most panel products,
  and much more for blockboard. The 250 Hz value is tabulated above because that is representative of
  low-frequency cabinet panel modes. The BBC fit `E(f)` as `A - B f + C` per material (their Table 3)
  if a frequency-dependent value is needed.

*Unit note:* the BBC's Table 1 header prints `E x 10^-9` in `N/cm2` while Table 2 prints `N/m2`.
Only `N/m2` is dimensionally sane (oak along the grain at 14.7 GPa sits beside the Wood Handbook's
12.27 GPa for white oak), and both tables are read as GPa here. The discrepancy is a misprint in the
report, flagged rather than silently corrected.

### Damping loss factor

Loss factor is `eta = 1/Q`. The BBC measured treatments applied to a **9 mm birch 7-ply substrate**,
which is the wood-panel constrained-layer data that is otherwise hard to find:

| Treatment | `Q` at fundamental | `eta` fundamental | Damping thickness |
|---|---|---|---|
| Nothing | 70 | 0.0142 | - |
| 1 layer Mutacell with Thixofix | 59 | 0.0170 | 1.65 mm |
| 2 layers Mutacell | 35 | 0.0286 | 3.3 mm |
| 4 layers Mutacell | 27 | 0.0370 | 6.6 mm |
| 1 layer roofing felt with Thixofix | 47 | 0.0213 | 2.35 mm |
| 1 layer Bostik self-adhesive | 24 | 0.0417 | 1.82 mm |
| 2 layers Bostik | 12 | 0.0833 | 3.64 mm |
| 3 layers Bostik | 8.5 | 0.1176 | 5.45 mm |
| 1 layer Aquaplas with Thixofix | 10 | 0.1000 | 2.9 mm |
| 1 layer Mutacell + steel + Thixofix | 20 | 0.0500 | 2.2 mm |
| **2 layers roofing felt + steel + Thixofix** | **7** | **0.1428** | 7.15 mm |
| 1 layer Celotex insulation board + Thixofix | 39 | 0.0256 | 12.0 mm |

The pattern is the engineering, not the brand names (which are 1977 products):

- **An untreated 9 mm plywood panel has `eta = 0.014`.** That is the number any claim about "well
  braced" or "inert" cabinets has to beat.
- **A constrained layer beats a free layer.** The best result in the table, `eta = 0.143`, is two
  layers of felt with a **steel constraining layer** on top — a tenfold increase in loss factor over
  the bare panel, and twice what the same felt achieves unconstrained. The mechanism is that the
  stiff outer layer forces the viscoelastic layer into shear rather than extension.
- **Damping efficiency is per unit thickness, and thickness is the cost.** Celotex at 12 mm buys
  `eta = 0.026`; Aquaplas at 2.9 mm buys `eta = 0.100`. Rank by `eta` per millimetre, not by `eta`.
- The BBC caution: these `Q` figures are **not absolute**, because damping depends on the mechanical
  impedance of the substrate, so they hold for a panel of about this size, thickness and material.
  **Neither the absolute values nor an invariant rank order is established for arbitrary substrates, temperatures and bond conditions.** Use the reported ranking as evidence for comparable specimens.

## 2. Where a panel's modes will land

A flat rectangular panel of uniform thickness has natural frequencies

```
f = lambda / (2 pi a^2) * sqrt( D / rho_s )

D     = E h^3 / (12 (1 - nu^2))     flexural rigidity, N m
rho_s = rho h                        mass per unit area, kg/m^2
a                                    the SHORTER panel dimension, m
lambda                               dimensionless frequency parameter, from the table below
```

`lambda` depends on the aspect ratio `a/b` and — decisively — on how the edges are held. Leissa's
tabulated values for a rectangular plate elastically restrained against rotation on all four edges,
where `K = 0` is simply supported (pinned, free to rotate) and `K = infinity` is fully clamped:

| `a/b` | `lambda`, simply supported | `lambda`, clamped | ratio |
|---|---|---|---|
| 1.0 | 19.74 | 35.99 | 1.82 |
| 0.9 | 17.86 | 32.67 | 1.83 |
| 0.8 | 16.19 | 29.08 | 1.80 |
| 0.6 | 13.42 | 25.90 | 1.93 |
| 0.4 | 11.45 | 23.65 | 2.07 |
| 0.2 | 10.26 | 22.64 | 2.21 |

The simply-supported column is exact and checkable: for a square plate `lambda = 2 pi^2 = 19.739`,
and for any ratio `lambda = pi^2 (1 + (a/b)^2)`. Every value in that column reproduces that identity,
which confirms the normalisation used here (`a` = shorter side). The clamped square value 35.99 is
Leissa's accurate figure; Galin's closed-form approximation gives exactly 36.

**The headline is the ratio column. The edge condition alone moves the fundamental by a factor of
1.8 to 2.2 — nearly an octave.** A glued butt joint into a thin panel is much nearer pinned than
clamped; a thick panel into a rebate with a glue block is nearer clamped; neither is either. This is
why a single computed panel-mode frequency is not a prediction. **Compute the pinned and clamped
values and report the band between them.** Anything narrower is false precision.

Higher modes for a clamped square plate, same normalisation, from Leissa's Table 4.27: 35.99, 73.41,
108.3, 131.6, 132.3, 165.2. Note the two nearly coincident modes at 131.6 and 132.3 — panel modes
crowd quickly, so "the panel resonance" is a simplification above the first one or two.

### Worked example, with its own reality check

The BBC's LS3/6 cabinet is 63 x 30 x 30 cm in 9 mm birch plywood. Take the 63 x 30 cm side panel:
`a = 0.30 m`, `b = 0.63 m`, `a/b = 0.48`, so `lambda ~= 12.2` pinned and `~= 24.5` clamped by
interpolation. Birch ply is orthotropic (12.0 GPa along the outer grain, 5.3 GPa across), so take the
geometric mean `E = 8.0 GPa`; `rho = 720 kg/m3`, `h = 9 mm`, `nu = 0.3`.

```
rho_s = 720 x 0.009 = 6.48 kg/m^2
D     = 8.0e9 x (0.009)^3 / (12 x 0.91) = 534 N m
sqrt(D / rho_s) = 9.08
f_pinned  = 12.2 / (2 pi x 0.09) x 9.08 = 196 Hz
f_clamped = 24.5 / (2 pi x 0.09) x 9.08 = 393 Hz
```

The BBC's own measurement of that cabinet shows the dominant side-panel output near **150 Hz** —
below even the pinned bound. So the bracket is useful and it is also optimistic at the bottom: a real
panel carries the driver's reaction mass and sits on joints with real compliance, both of which push
the frequency down. **Use the bracket to know which octave to worry about, and never as a figure to
design a notch around.**

An orthotropic panel does not have one `E`, and isotropic plate theory applied to plywood is an
approximation whose error is not established by any source here. Say so when you use it.

## 3. From panel vibration to audibility

**The isolated-panel model does not establish absolute radiated SPL.** The BBC stated the limit of its analytical treatment: "it is not possible to calculate the output resulting from the complex coupling of all the
panels and loudspeaker unit together, so some form of overall test is required." The panels, the
driver and the enclosed air are coupled, and the coupling is what sets the radiated level. That limits the present `plate_structure` relative-panel proxy; it is not a prohibition on a future coupled structural/acoustic model with explicit geometry, boundary conditions and verification.

What exists instead is a measured audibility criterion. The BBC assembled it from listening tests on
real cabinets, plotting panel output level relative to the direct axial response against frequency,
and marking which resonances were heard:

```
Criterion for perceptibility of panel resonance (BBC RD 1977/3, Fig. 12)

  about -13 dB at 100 Hz, falling linearly (on a log-frequency axis) to
  about -30 dB at roughly 400 Hz, then
  flat at about -30 dB from 400 Hz to 10 kHz.

  Panel output ABOVE this line was audible; below it, inaudible.
```

Its stated limits, which travel with it:

- **Scatter is about +/- 1 dB** about the mean curve, with a small overlap between the audible and
  inaudible populations. Allow a safety margin below the line.
- **It has no theoretical backing whatsoever.** The BBC say so in those words, and add that there is
  no obvious reason the curve should slope downwards — a curve rising with frequency would be easier
  to justify on directivity grounds. It is an empirical fit to their own listening data and
  exceptions may exist.
- It is a 1977 result on 1977 programme material, measured with a pressure-gradient microphone placed
  so the cone's radiation falls in its null.

Even so it is the only published quantitative threshold obtained here, and it is decision-changing:
it says a panel resonance at 150 Hz has to be **13 dB** below the direct sound to be inaudible, while
one at 1 kHz needs **30 dB**. Low-frequency panel resonances get much more latitude than intuition
suggests, and midband ones get much less.

## 4. What this settles about wall thickness

The BBC built two cabinets of identical external dimensions, one in standard 9 mm birch ply and one
in 18 mm, and measured both with and without the standard damping treatment. Results:

- **Undamped, both failed the criterion**, and the **thick-walled cabinet radiated more** than the
  thin-walled one. The stated reason is that its `Q` was higher. The BBC note this has been confirmed
  in other similar experiments.
- **With the standard damping applied, the thin-walled cabinet met the criterion and the thick-walled
  one did not.** Listening tests agreed with the measurements in both cases.
- Their conclusion: the thick-walled cabinet "is more expensive in plywood and in damping material,
  and is of course unnecessarily heavy ... It has no advantages and is clearly an inferior design."

The transferable engineering is not "thin walls are better". It is that **wall thickness moves a
resonance up in frequency and raises its `Q`, and the criterion gets 17 dB stricter as you move from
100 Hz to 400 Hz.** Moving a panel mode from 150 Hz to 300 Hz while raising its `Q` moves it into the
part of the audibility curve that is least forgiving. If thickness is increased, the damping must be
increased with it, and the BBC's thick cabinet would have needed "much thicker, and therefore more
expensive, damping material" to comply.

## 5. Not covered

Bracing: no source here quantifies what a brace does to `lambda`, and a brace changes both the
effective panel dimensions and the edge condition, so neither the aspect-ratio table nor the pinned/
clamped bracket can be applied to a braced panel without an assumption that is stated. Curved and
non-rectangular panels. Joint stiffness as a number. Cabinet wall transmission loss as distinct from
panel resonance. The audibility of panel radiation under programme material other than the BBC's.

## Sources

- Z. Cai, C. A. Senalik and R. J. Ross, "Mechanical Properties of Wood-Based Composite Materials", Chapter 12 of *Wood Handbook - Wood as an Engineering Material*, General Technical Report FPL-GTR-282, USDA Forest Products Laboratory, 2021. Table 12-1 read at first hand. https://www.fpl.fs.usda.gov/documnts/fplgtr/fplgtr282/chapter_12_fpl_gtr282.pdf
- H. D. Harwood and R. Mathews, "Factors in the design of loudspeaker cabinets", BBC Research Department Report BBC RD 1977/3, January 1977. Tables 1, 2 and 4, Figure 12 and the conclusions read at first hand. https://downloads.bbc.co.uk/rd/pubs/reports/1977-03.pdf
- A. W. Leissa, *Vibration of Plates*, NASA SP-160, 1969. Tables 4.26, 4.27 and 4.30 read at first hand; the simply-supported column independently verified against the closed form. https://ntrs.nasa.gov/api/citations/19700009156/downloads/19700009156.pdf
- ASTM D1037 (fibre- and particle-based panels) and ASTM D3043 (structural panels), cited by the Wood Handbook as the procedures behind its MOE figures; not read at first hand.
- J. E. Ruzieka, *Structural Damping*, Pergamon Press, 1960, section 3 p. 63, cited by the BBC report as the basis for the extension-mode versus shear-mode damping distinction; not read at first hand.
