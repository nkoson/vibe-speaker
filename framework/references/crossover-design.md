---
id: crossover-design
applies_when: Choosing a crossover topology, fitting values, quantizing to stock, reading dissipation or impedance, or judging a crossover result
updated: 2026-09-15
---

# Passive crossover design: principles

A passive crossover is a lossy network between one amplifier and several drivers, built from parts that are not ideal, working into loads that are not resistors, and judged by an acoustic result it only partly controls. Almost every bad passive crossover comes from forgetting one of those four facts.

## 1. The load is not a resistor

Textbook filter alignments are derived for a resistive termination. A moving-coil driver is not one: voice-coil inductance lifts the impedance with frequency, the fundamental resonance puts a peak at fs, and a horn-loaded compression driver adds the horn's own loading. A filter designed against a nominal 8 ohms and then connected to a real driver does not produce the response it was designed for.

Two corrections, used together or separately:

- **Impedance compensation.** A Zobel network, a series R and C in shunt across the driver, flattens the inductive rise: `C = Le / Re^2` and `R = Re`, with `Re` the DC resistance and `Le` the voice-coil inductance. A series or parallel notch tames the resonance peak. Elliott calls impedance compensation "absolutely essential for proper behaviour of the crossover network, but sadly is not used in a great many designs".
- **Designing against the actual impedance.** `crossover_network` terminates each ladder with the driver impedance from the section's `source_response` file, and `crossover_fit` searches values with that termination in place. That is the honest route, and it is why a fit against a modelled impedance is only as good as the impedance model: a datasheet prior for a compression driver or a dome is a prior, not a measurement.

## 2. The target is acoustic, not electrical

What reaches the listener is the electrical filter, times the driver's own response and rolloff, times the baffle, summed with the other sections at their acoustic offsets. A second-order electrical filter on a driver already rolling off can give a fourth-order acoustic slope; a fourth-order electrical filter on a driver with a peak can give something with no textbook name. Design the acoustic sum: pick the electrical order as the means to it, and read the result from `whole_speaker`, not from the ladder.

The consequence for the fit: the target level and band belong to the acoustic sum, and the fit is only meaningful if the source responses fed to it are right. A wrong level or a double-counted rolloff in a source file produces a crossover that is a correct solution to the wrong problem.

## 3. Summation, phase and polarity

- **Linkwitz-Riley** targets put each section 6 dB down at the crossover frequency so that the two sum flat, which is why they are the usual starting point for a passive multi-way: LR4 and LR8 with both sections in the same polarity, LR2 with one section inverted.
- **Butterworth** targets are 3 dB down at the crossover: the even orders sum to a 3 dB bump there, and the odd orders sum flat in magnitude with the two outputs in quadrature and the phase rotating through the band.
- **Acoustic offset** between the drivers' acoustic centres adds a frequency-dependent phase difference across the overlap. It tilts the vertical lobe and can turn a designed flat sum into a comb. Move the driver, change the depth, or change the overlap; adding filter elements to fix a geometry problem usually makes a narrower version of the same problem.
- **Do not assume polarity.** Run the polarity study and keep the sign that sums best, then make the crossover file agree with it.

Constant-voltage designs (Small) sum exactly by construction but are limited to first-order slopes, which most real drivers cannot survive; the linear-phase families derived by time delay (Lipshitz and Vanderkooy) show what it costs to have both flat sum and steep slopes. Both are worth knowing as the boundaries of what a passive network can do.

## 4. The level budget is decided before the crossover

The system sensitivity of a passive speaker is set by its least sensitive section, after the baffle step and the box losses, because every other section is attenuated down to meet it. A crossover cannot make a section louder. This is the single most useful thing to work out before choosing values:

```
pad depth of a section  =  that section's in-band sensitivity  -  the system level you can support
```

A horn assembly at 110 dB/2.83 V/m in a system whose bass section supports 94 dB needs about 16 dB of attenuation, and no arrangement of resistors avoids it. When that number is large, the finding is about the driver complement, not about the network. The choices that change it are: a less sensitive upper driver or a smaller horn, a more sensitive or larger bass section, an autotransformer tap instead of resistive attenuation, accepting a lower system level, or going active. Deciding between them is design work; sizing resistors for it is not.

**L-pad.** To attenuate by `A` dB into a load `Z` while presenting `Z` to the filter, with `a = 10^(-A/20)`:

```
R_series = Z (1 - a)          R_shunt = Z a / (1 - a)
```

A series resistor alone also attenuates, but it changes the impedance the filter works into and therefore detunes it; that is why the L-pad exists. Both forms change the source impedance the driver sees, which matters for a driver whose damping depends on it, and neither is flat unless the load is flat, which is another reason for impedance compensation.

**Coil DCR is attenuation too.** A series coil of resistance `R_L` into a load `Z` costs `20 log10(R_L / Z + 1)` dB of level in the passband, which comes off that section's sensitivity before the pad is calculated.

## 5. Power, heat and what the ratings mean

The pad dissipates the difference between what the amplifier delivers to that section and what the driver takes. A 10 dB pad passes a tenth of the power to the driver and turns most of the rest into heat, in a sealed or vented box with still air and no cooling of any kind.

**The stress condition is a probe, not the operating point.** A continuous single-frequency sine at the stress voltage concentrates the whole spectrum into one branch of one section; music distributes power across the spectrum and across time, which is why power-handling standards such as IEC 60268-5 specify shaped noise with a defined crest factor rather than a sine. Parts are chosen to survive the probe with margin; the thermal design point is not the probe. Reading `results.sections[].components[].max_dissipation_w` and `results.total_component_dissipation_w` without saying which drive condition produced them turns a robustness check into a false requirement.

**A power rating is a statement about a mounting.** Every resistor datasheet gives its rated power for a stated condition: free air at a stated ambient with a derating curve above it, or a case temperature held by a heatsink of stated size, or a specified copper area on a board. Power-type chassis-mount parts routinely quote a heatsinked rating an order of magnitude above their free-air rating - a part sold as "100 W" may be rated 3.5 W in free air, the number that applies on a crossover board. Use the rating for the mounting the design actually has, then derate: sizing the worst case at about half the applicable rating is common practice, and it exists because resistance rises with temperature, wirewound resistors change value as they heat, and a hot part ages the parts and the glue around it.

**A passive loudspeaker has no thermal system.** It has a board on a panel, still air, wadding that insulates rather than cools, and panels that are poor radiators. Heatsinks, fans, thermal interfaces and forced air belong to amplifiers, not to passive crossovers, and a commercial passive design of ordinary sensitivity dissipates a few watts in its network under normal use. So when the arithmetic starts asking for a cooling assembly, or for a resistor count in the tens, that is the level budget of section 4 speaking: the fix is upstream, in the driver complement or the system level, and adding a heatsink to a loudspeaker is an answer to a question that should not have been reached. If a design is nevertheless kept with a heavy attenuator, the honest form is to write the dissipation, the mounting, the derating and the risk into the evaluation and the documentation, and to say plainly what happens at sustained level.

## 6. The load the amplifier sees

The sections sit in parallel at the terminals, so the input impedance minimum is lower than any single branch minimum. Report the minimum magnitude, the frequency it occurs at and the phase angle near it: a dip with a large phase angle is harder to drive than its magnitude suggests. Keep the minimum consistent with the nominal rating you claim: the convention behind those ratings, in IEC 60268-5, is that the impedance modulus does not fall below 80 percent of the rated value, which is about 6.4 ohms for an 8 ohm speaker and 3.2 for a 4 ohm one. Zobels, notches and pads all move it. `crossover_fit` can hold a stated minimum during the search; state it rather than discovering the dip afterwards.

**Drivers in parallel are one change with two faces.** Putting `n` identical drivers in parallel
multiplies the radiating area and divides the impedance, so at a fixed voltage the array draws `n`
times the current and produces about `20 log10(n)` dB more, while its minimum impedance falls to
`1/n` of one driver's. Two drivers are 6 dB and half the impedance; four are 12 dB and a quarter.
The efficiency, in sound power per watt, barely moves - the extra output is bought with extra
current. Series connection is the mirror image: `n` times the impedance and the same voltage
sensitivity as one driver. So a design that gains sensitivity by paralleling has not become more
efficient, and a brief that asks to keep the sensitivity while restoring the load is asking for that
output from somewhere else: a larger driver, a larger box, a different loading, or a lower target.
Report voltage sensitivity, minimum impedance and current at a stated drive together whenever an
array is proposed, and do not convert a wideband voltage sensitivity to a one-watt figure using the
array's bass minimum.

## 7. Real components

- **Coils.** DCR costs level (section 4) and damping. Air cores are linear but get heavy and resistive at large values; iron and ferrite cores give a given inductance with less wire and less DCR but saturate and distort at high level, which matters most in a woofer's series coil. Large-value coils are also physically large objects on the board.
- **Capacitors.** Tolerance dominates the response error in most networks. Give every capacitor a voltage rating checked against the voltage the network puts across it at the stress drive, which for a shunt capacitor in a resonant branch can exceed the terminal voltage.
- **Resistors.** Non-inductive types where the resistor sits in a filter branch rather than a pad. Series and parallel combinations are legitimate for reaching a value or spreading heat, but a large array is a symptom, as in section 5.
- **Layout.** Coils couple: space them and set neighbouring axes at right angles. Keep hot parts away from capacitors, wiring and damping material. Wire gauge follows the current figures from `crossover_network` or `board_nodal`, and the wiring resistance goes back into the model as `wire_loop_ohm` rather than being assumed to be zero.
- **Tolerances.** Run the tolerance draws and compare envelopes, not only nominal curves. A design that is only flat at nominal values is a design that will not be flat.

## 8. Fewer parts, and when more are justified

Each element costs money, adds a tolerance, adds a loss and adds a way to be wrong. Higher order buys steeper acoustic slopes, which protect a driver near its limits and control the overlap where directivity mismatches, and it costs phase rotation, parts and sensitivity to component values. Start from the simplest network that reaches the acoustic target and add order for a stated reason.

## 9. Before accepting a fitted network

Check, in this order, and write what you found:

1. `statistics.values_at_bound`: a value resting on a bound means the topology or the bound is wrong, not that the optimizer finished.
2. The values are plausible parts: an air-core coil of several millihenries in an upper section, a series capacitor of hundreds of microfarads on a tweeter, or a pad resistor that dissipates more than the driver it feeds points at an error upstream rather than at a part to buy.
3. Quantized to stock, with real DCR and ESR, and rerun. The quantized network is the design; the continuous one was an intermediate.
4. Pad depth per section against the sensitivity mismatch of section 4.
5. Dissipation per component at the stress drive against the rating for the actual mounting, with the drive condition stated.
6. Input impedance minimum, its frequency and the phase near it.
7. Acoustic crossings inside both drivers' published ranges, with the woofer's beamwidth near the horn's coverage at the crossing.
8. Tolerance envelope and the depth-perturbation result, before admiring the nominal curve.
9. What the fit assumed: datasheet phase, prior impedance models, no measurement. The values are a starting point for a build that will be measured, and the documentation says so.

## 10. What no simulation settles

Real impedance and real acoustic response on the real baffle, horn phase, driver-to-driver variation, thermal compression and the value shift that comes with it, port and cabinet noise. Final crossover values are set after measurement; a simulated network is a build starting point, and calling it anything else in a document is a false claim.

## 11. Compensation networks, with the numbers and the disagreements

Section 1 gives the shape of the problem; these are the values, with the caveat that almost all of
this material comes from self-published engineering sites rather than from papers, and that two
published conventions for the same network disagree with each other.

**Zobel.** The base form is `C = Le / Re^2` with the series resistor equal to `Re`. Two conventions
scale the resistor differently: `R = 1.1 Re` (Elliott) and `R = 1.25 Re` (Dickason), with
`C = Le / R^2` in both. For one worked driver those give 6.2 ohm with 23.5 uF against 7.0 ohm with
18 uF — about 13 percent apart in resistance and 25 to 30 percent in capacitance. Neither multiplier
is derived; both are empirical corrections for the fact that `Le` is frequency-dependent. `Le` itself
is usually quoted at one frequency, so the capacitance inherits that ambiguity, and a driver whose
impedance rise is semi-inductive rather than a clean single `Le` cannot be tracked by one R-C at all.
Measure the impedance curve rather than trusting a single datasheet `Le`.

**Resonance notch.** A parallel L-C-R across the driver flattens the `fs` peak, with
`RN = Re / Qes` — and `RN` is the **total**, of which the notch inductor's own DCR is a real part (in
one worked example, 1.5 ohm of a 7.75 ohm total). A capacitor formula of the form
`C = 1 / (2 pi Re f3)` circulates with `f3` left undefined; do not apply it blind. Size the notch
from the measured impedance instead: the resistance is the peak height above `Re`, and `L` and `C`
follow from the centre frequency and the width you need.

**The target the compensation has to hit.** A compensated driver should look essentially resistive —
variation under about 1 ohm, roughly 10 percent — across at least one octave either side of the
crossover, preferably one and a half to two. Compensation typically lowers a driver's effective
impedance by 20 percent or so, and it is that lowered, measured value that belongs in any component
formula, never the nominal rating on the label. Sensitivity to the load grows with filter order, so
treat compensation as mandatory at second order and above.

**L-pad.** Consistent with section 4, with `Vr = 10^(A/20)`: `Rs = Z (Vr - 1) / Vr` and
`Rp = Z / (Vr - 1)`. To audit an existing pad, `A = 20 log10( Rs / ((Z Rp) / (Z + Rp)) + 1 )`, which
reduces to `A = 20 log10((Rs + Z) / Z)` for a series resistor alone. Both forms assume the driver
really is resistive at `Z` where the pad is working, which is what the compensation above is for.

**Electrical coefficient tables, and what they are not.** Tables of the form `C = k / (Z fx)`,
`L = k' Z / fx` exist for each alignment — LR2 at 0.0796 and 0.3183 (that is `1/4pi` and `1/pi`),
2nd-order Butterworth at 0.0912 and 0.2756, first order at 0.159 (`1/2pi`). They compute the
**electrical** transfer function into a resistive load. An electrical LR4 into a real driver is not
an acoustic LR4, because the driver's own rolloff and the baffle are already part of the acoustic
branch; the tables are a starting point for a fit, not a design. The published LR4 coefficient set
could not be corroborated against a second source here.

**Three-way midrange gain error.** A midrange bounded by two crossovers picks up a passband gain error
that must be removed by level matching: about 2.08 dB at second order with reversed midrange polarity
(2.45 dB when the crossovers are only three octaves apart), 0.85 dB at third order, and 2.28 dB at
fourth order, all at a ten-to-one crossover spread. Widely spaced crossovers suffer less.

**Series topology, and the one real advantage it has.** A second-order series crossover is computed
from `C = 1 / (2 pi f (Z / sqrt(2)))` and `L = (Z / sqrt(2)) / (2 pi f)`. The property worth knowing
is confined to **first order**: a series first-order network keeps its summed response flat as the
driver impedance changes — one published demonstration moves a woofer from 6 to 10 ohms with the sum
staying flat, where the parallel equivalent visibly deviates — and it is described as the only
crossover circuit with that behaviour. At second order the difference between series and parallel
largely disappears, and the author's own listening comparison found very little audible difference.
Treat series topology as an answer to impedance variation at first order, not as a general
improvement.

**Bessel, for when transient behaviour is the priority.** A Bessel alignment has the most linear
phase of the common families, the widest and most gradual crossover region, and a gentle dip rather
than a peak in the summed response; a phase-matched Bessel pair sums within about 2 dB at second and
fourth order. To convert a Bessel design from the conventional -3 dB normalisation to the
phase-matched form at second order, multiply the low-pass corner by 1.272 and the high-pass corner by
0.786. Its cost is the shallow initial cutoff, which is exactly the protection an HF driver needs, so
it is rarely the right choice for the tweeter branch of a passive two-way.

**What to expect when it is right.** A well-executed passive network summing through the crossover
region achieves about +/-0.5 dB of ripple; a fit target tighter than that is optimising noise.

## 12. Heat, drift and what the real parts cost

- **Coil DCR against wire gauge.** At a fixed inductance, DCR scales roughly with the inverse square
  of wire diameter, and the low DCR is paid for in volume: one catalogue pair at 0.005 mH gives
  0.020 ohm in a 19 x 25 mm body with 1.60 mm wire against 0.060 ohm in a 10 x 8 mm body with
  0.80 mm wire — three times the resistance for about a tenth of the volume. Those absolute figures
  come from the very-low-inductance end of a catalogue and do not transfer to a 1 to 5 mH woofer
  coil; the scaling law does.
- **Cored coils: the saturation figure does not exist, and the manufacturer says so.** A major
  supplier's iron-core coil listings publish inductance, DCR, wire gauge and physical size and **no
  current or saturation rating at all**. Chasing that to the per-part datasheet does not help,
  because the same supplier states plainly in its own technical FAQ: *"We have not done any
  measurements for power handling and saturation points for our induction coils."* Their stated
  reasons are that such a measurement is difficult and that its result would not be conclusive enough
  to decide whether a coil suits a particular crossover position.

  **Treat that as settled rather than as a search still to be done.** The number is not withheld, it
  has not been taken. A design that needs to know where a cored coil saturates must either measure it
  or avoid the question, and the framework's part records should carry "not published" rather than a
  blank that invites an assumption.

  What *is* established about the physics, from the same supplier:

  - An air core does not saturate at all; its inductance is essentially constant over the full
    operating current range. Every saturation question is a cored-coil question.
  - **A ferrite core saturates earlier than a non-ferrite powder core**, and when it does the
    inductance loss is **instant, with a much more aggressive loss curve**. Powder cores handle
    higher power, saturate later, and fall off more softly.
  - The practice threshold they give is a **frequency**, not a current: ferromagnetic-cored inductors
    can be used for the bass and lower midrange "without any audible distortion or interference, or
    as rule of thumb for positions below 1.2 kHz". Above that, use air cores.

  Their hierarchy for air cores, best first, is foil, then Litz wire, then single wire. The 1.2 kHz
  figure is a vendor rule of thumb with no derivation attached and is recorded as such — but since it
  is the only threshold anyone published, a cored coil above 1.2 kHz is a choice that has to be
  argued for in the candidate notes.
- **Coils get hot.** A 0.66 ohm winding passing 5 A rms dissipates 16.5 W, and at 150 C its resistance
  rises to about 1 ohm and its dissipation to about 25 W. Copper's temperature coefficient is 0.39 to
  0.395 percent per degree C.
- **So does the load.** A 6.6 ohm voice coil at 150 C presents about 10 ohms, a rise of roughly half.
  Filter corner frequencies, filter Q and L-pad attenuation all move with it, which is one more reason
  to prefer an L-pad over a bare series resistor, and a reason a passive design voiced cold is not the
  same design when hot. This matters in monitoring and PA duty and is negligible at domestic level.
- **Capacitors.** Polypropylene in the signal path (dielectric constant about 1.5, strength 23 to
  25 MV/m, which is why it is physically large); polyester acceptable at lower power (2.8 to 4.5,
  16 MV/m). Electrolytics do not belong in a hi-fi crossover: their value drifts with age, and
  non-polarised crossover types have been quoted with tolerances as wide as +20/-50 percent, which at
  the low end doubles a corner frequency. Class II ceramics (X7R, Y5V and relatives) never belong in a
  signal path at all.
- **Insertion loss.** A heavily padded network with high-DCR coils has been quoted as losing "as much
  as 3 dB" overall. That is an upper bound from an author arguing for bi-amping, not a typical value;
  compute the actual loss from your own DCR and pad values, where section 4's `20 log10(R_L / Z + 1)`
  gives each series element's contribution.
- **Bi-amping.** Its power advantage over one amplifier and a passive network is bounded at 3 dB in
  theory and reported at 1 to 2 dB in practice. The real arguments for going active are directivity
  control, freedom from the thermal drift above and from impedance interaction — not headroom.
- **Power split.** For typical programme material the equal-power frequency between the low band and
  everything above it lies between 250 and 350 Hz, which is the figure to use when sizing component
  current ratings per branch.
- **Group delay.** Every common passive topology is an order of magnitude below published audibility
  thresholds at a normal crossover frequency; the phase budget is spent on acoustic-centre offset
  instead. The numbers are in `system-architecture.md` section 6.

## Sources

- Jantzen Audio technical FAQ, "Coil types and where to use them" and "P-core inductors - Ferrite and non-ferrite powder cores". First-hand manufacturer statement that power handling and saturation points are not measured for their coils, the ferrite-versus-powder saturation behaviour, the 1.2 kHz practice threshold and the air-core hierarchy. A vendor source, and the rules of thumb in it carry no derivation. https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/

- Elliott, R., "Linkwitz-Riley Crossovers - Passive", Elliott Sound Products - practical passive design: component formulas, impedance compensation, coil DCR loss, L-pads and what changes with temperature. <https://sound-au.com/lr-passive.htm>
- Linkwitz, S. H., "Active Crossover Networks for Noncoincident Drivers", *Journal of the Audio Engineering Society*, vol. 24, no. 1, pp. 2-8, 1976 - the LR alignment and the lobing that comes from driver offset. <https://aes2.org/publications/elibrary-page/?id=2649>
- Small, R. H., "Constant-Voltage Crossover Network Design", *Journal of the Audio Engineering Society*, vol. 19, no. 1, pp. 12-19, 1971 - what exact summation requires, and why it limits the slope. <https://aes2.org/publications/elibrary-page/?id=2214>
- Lipshitz, S. P., Vanderkooy, J., "A Family of Linear-Phase Crossover Networks of High Slope Derived by Time Delay", *Journal of the Audio Engineering Society*, vol. 31, no. 1/2, pp. 2-20, 1983 - the trade between flat summation, slope and phase.
- Zobel, O. J., "Theory and Design of Uniform and Composite Electric Wave-Filters", *Bell System Technical Journal*, vol. 2, no. 1, 1923 - the impedance-compensation network by its original name.
- Dickason, V., *The Loudspeaker Design Cookbook*, 8th ed., Audio Amateur Press - crossover topologies, L-pads, Zobels, notch filters and component practice in one place.
- Beranek, L. L., Mellow, T. J., *Acoustics: Sound Fields and Transducers*, Academic Press, 2012 - the electro-mechano-acoustic models the ladders terminate into.
- D'Appolito, J., *Testing Loudspeakers*, Audio Amateur Press - what has to be measured before crossover values are final.
- IEC 60268-5, *Sound system equipment - Part 5: Loudspeakers* - the signal conditions under which power ratings are defined.
- The manufacturer's datasheet of the exact part, read for the condition its rating applies to: free air with a derating curve, or a held case temperature on a heatsink.
- Elliott, R., "Impedance Compensation" and "Capacitor Characteristics" and "Bi-amping - Not Quite Magic" and "L-pad calculations", Elliott Sound Products - the Zobel and notch conventions, the resistive-bandwidth target, L-pad and audit formulas, capacitor dielectric practice and tolerance, coil and voice-coil thermal drift, insertion loss and the bi-amping bound. Self-published engineering writing, not peer reviewed; the arithmetic is checkable and the rules of thumb are labelled as such above. <https://sound-au.com/articles/z-compensation.htm>
- "Zobel Networks", True Audio - the alternative Zobel convention sized from nominal rather than measured resistance, recorded here for the disagreement it creates. <https://www.trueaudio.com/st_zobel.htm>
- Elliott, R., "Serial vs. Parallel Crossover Networks" and Rane, "A Bessel Filter Crossover, and its Relation to Others", RaneNote 147 - the series component forms and the first-order impedance-invariance property, and the Bessel family's phase, summation and normalisation figures. <https://sound-au.com/parallel-series.htm> and <https://www.ranecommercial.com/legacy/note147.html>
- Jantzen Audio air-core coil catalogue - published inductance, DCR, wire gauge and physical envelope per part, the basis of the gauge-against-DCR scaling in section 12; tolerance and current ratings are not in the catalogue and must come from the per-part datasheet. <https://www.jantzen-audio.com/product-category/air-core-wire-coil/>
- In this repository: `framework/simulations/crossover_network/README.md` and `framework/simulations/crossover_fit/README.md` for what the applications compute and report.
