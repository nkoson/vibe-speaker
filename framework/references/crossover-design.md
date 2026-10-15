---
id: crossover-design
applies_when: Choosing a crossover topology, fitting values, quantizing to stock, reading dissipation or impedance, or judging a crossover result
updated: 2026-10-15
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

The system sensitivity of a passive speaker is set by its least sensitive section, after the baffle step and the box losses, because every other section is attenuated down to meet it. A passive network cannot supply net real power gain, although reactive voltage magnification can raise a driver’s terminal voltage locally; inspect that gain and its stress before treating it as usable broad-band level. This is the single most useful thing to work out before choosing values:

```
pad depth of a section  =  that section's in-band sensitivity  -  the system level you can support
```

A horn assembly at 110 dB/2.83 V/m in a system whose bass section supports 94 dB needs about 16 dB of attenuation, and no arrangement of resistors avoids it. When that number is large, the finding is about the driver complement, not about the network. The choices that change it are: a less sensitive upper driver or a smaller horn, a more sensitive or larger bass section, an autotransformer tap instead of resistive attenuation, revising the required bass/level balance, or going active. Deciding between them is design work; sizing resistors for it is not.

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
These are coherent on-axis pressure gains for identical equally driven sources where their phases align, not a universal sound-power efficiency law. At equal total electrical power the coherent pressure gain is `10 log10(n)` dB; actual efficiency and directivity also depend on mutual loading, geometry and enclosure. Series connection gives `n` times the impedance and approximately the voltage sensitivity of one under those same assumptions. A voltage-sensitivity gain alone does not establish better efficiency or an equally easy amplifier load. A brief that keeps the gain while restoring the load needs a replacement mechanism: different drivers, volume, loading or target.
Report voltage sensitivity, minimum impedance and current at a stated drive together whenever an
array is proposed, and do not convert a wideband voltage sensitivity to a one-watt figure using the
array's bass minimum.

## 7. Real components

- **Coils.** DCR costs level (section 4) and damping. Air cores are linear but get heavy and resistive at large values; iron and ferrite cores give a given inductance with less wire and less DCR but saturate and distort at high level, which matters most in a woofer's series coil. Large-value coils are also physically large objects on the board.
- **Capacitors.** Tolerance dominates the response error in most networks. Give every capacitor a voltage rating checked against the voltage the network puts across it at the stress drive, which for a shunt capacitor in a resonant branch can exceed the terminal voltage.
- **Capacitor dielectrics, with the published numbers.** A metallized-polypropylene crossover capacitor is specified around ±5 percent, 400 V DC and 250 V AC, with dielectric absorption below 0.5 percent and self-inductance under 15 nH; its ESR is described as "extremely low" and **is not given a figure**, which is why a model needs an explicit ESR prior and has to say it is one. A bipolar aluminium electrolytic built for the same job is specified at **±20 percent** capacitance, `tan δ` at most 0.10 at 1 kHz and 0.15 at 5 kHz, 50 V rated, −40 to +85 °C, with an allowable continuous current from about 0.2 A rms at 1 µF to 1.0 A rms at 47 µF. Those are limits rather than typical values, and `ESR = tan δ / (2 π f C)` turns the loss figure into the number the ladder uses: at 1 kHz that allows about 1.6 ohm for a 10 µF part and 0.34 ohm for a 47 µF one, against the hundredths of an ohm a film part is assumed to have. The three differences that a model can see are therefore tolerance, ESR and the voltage and current ratings — and in a woofer branch the ratings, not the sound, are usually what rules a part out.
- **Choosing between two parts that do the same job.** The cheaper, generally available part is the default. A costlier one earns its place by showing an advantage in a quantity the design actually uses: a tolerance that visibly narrows the envelope of the tolerance draws, an ESR that changes a level or a Q the fit depends on, a voltage or current rating the stress run demands, a DCR that buys back level, a size that fits. The way to settle it is to put each candidate's own figures into the parameter file — `tolerance_fraction`, `esr_ohm`, `dcr_ohm`, `rating` — and rerun: if the cheap part's envelope and ratings are adequate, the expensive one has demonstrated nothing the model can see, and that is what the notes should say. Claims that survive outside the model exist, but no source consulted here establishes an audible difference between dielectrics in a crossover position at crossover values, and the published distortion measurements of capacitor dielectrics were made at small values and small signals, which does not transfer to a hundred microfarads across a woofer. Availability is a selection criterion in its own right: a catalogue that marks a series "not recommended for new designs" has answered the question before the engineering does.
- **Resistors.** Non-inductive types where the resistor sits in a filter branch rather than a pad. Series and parallel combinations are legitimate for reaching a value or spreading heat, but a large array is a symptom, as in section 5.
- **Layout.** Coils couple: space them and set neighbouring axes at right angles. Keep hot parts away from capacitors, wiring and damping material. Wire gauge follows the current figures from `crossover_network` or `board_nodal`, and the wiring resistance goes back into the model as `wire_loop_ohm` rather than being assumed to be zero.
- **Tolerances.** Run the tolerance draws and compare envelopes, not only nominal curves. A design that is only flat at nominal values is a design that will not be flat.

## 8. Fewer parts, and when more are justified

Each element costs money, adds a tolerance, adds a loss and adds a way to be wrong. Higher order buys steeper acoustic slopes, which protect a driver near its limits and control the overlap where directivity mismatches, and it costs phase rotation, parts and sensitivity to component values. Start from the simplest network that reaches the acoustic target and add order for a stated reason.

**What each kind of element costs, as arithmetic.** These follow from the circuit and are not preferences:

- A matched resistive L-pad of `A` dB passes `10^(-A/10)` of its input power to the driver and turns the rest into heat: half at 3 dB, a quarter at 6 dB, a tenth at 10 dB. Section 4 sets `A`, so the heat is the level budget's number, not the pad's.
- A compensation branch of resistance `R` across a driver whose impedance magnitude is `|Z|` carries `|Z| / R` times the driver's current where the branch is resistive, but its real-power ratio is `(1/R) / Re(1/Z)`, not generally the current-magnitude ratio. For resistive loads only, the ratios coincide. A 12 ohm shunt across a resistive 24 ohm driver makes 8 ohms total and dissipates twice the driver power. **Compensation diverts current**; its effect on driver voltage depends on the upstream filter and source impedance. The cost lands on the amplifier as a lower input impedance, on the resistor as heat, and on the build as parts.
- A notch changes current and voltage throughout its branch. Calculate its resistor heat from the loaded circuit; notch depth alone does not determine dissipation.
- A coil's DCR costs `20 log10(R_L / Z + 1)` dB of level, which is section 4's arithmetic seen from the other side: the cheap cored coil that halves DCR is buying level back, and the large air-core coil that avoids saturation is spending it.

Money and board area concentrate in the large reactive values — a woofer branch's coils and capacitors — and a position built as a bank multiplies both. `crossover_network` reports the physical part count, and `parts.sections[]` says where it went.

**Measure what an element is worth rather than arguing about it.** `crossover_fit`'s ablation pass removes one element — a series element shorted, a shunt element opened, which is what leaving it out of the build does — and refits every remaining free value before scoring, so `delta_rms_db` is what the rest of the network cannot recover without that part. It answers the question in this design, against this target, on axis. It does not answer what the element does for impedance, stress, off-axis behaviour or tolerance robustness, so read `input_z_min_ohm` beside it and rerun `crossover_network` and `whole_speaker` on any variant worth taking seriously. **There is no delta at which an element should be removed.** A part that buys 0.2 dB is worth keeping in one design and not in another, and that is a judgement to make and record, not a rule to apply.

**What share of the power the network keeps** is reported by `crossover_network`'s `efficiency` block, pink weighted. It is a reading and not a target. The same figure arises from two unlike causes — attenuation a sensitivity mismatch forces, and current a compensation branch diverts — so it means nothing without the pad depths of section 4 and the compensation audit of section 11 beside it. What it is good for is noticing early that most of the amplifier's output is being spent on something other than the drivers, which is a question about the driver complement and the topology while both can still change.

**A judgement, stated as one.** When the loss, the part count or the cost looks wrong, the order worth trying is: the level budget first, because pad depth follows from the driver complement and the system level and nothing downstream can undo it; then whether compensation is earning its diverted current, since fitting a lower-order filter against the driver's complex impedance is sometimes cheaper than flattening the impedance and fitting against a resistor; then the shaping elements, by ablation; and only then the parts themselves. This ordering is reasoning from the arithmetic above rather than a published procedure.

## 9. Before accepting a fitted network

Check, in this order, and write what you found:

1. `statistics.values_at_bound`: a value resting on a bound needs investigation of the stock range, target and topology; it can also be a legitimate constrained optimum.
2. The values are plausible parts: an air-core coil of several millihenries in an upper section, a series capacitor of hundreds of microfarads on a tweeter, or a pad resistor that dissipates more than the driver it feeds points at an error upstream rather than at a part to buy.
3. Quantized to stock, with real DCR and ESR, and rerun. The quantized network is the design; the continuous one was an intermediate.
4. Pad depth per section against the sensitivity mismatch of section 4.
5. Dissipation per component at the stress drive against the rating for the actual mounting, with the drive condition stated.
6. Input impedance minimum, its frequency and the phase near it.
6a. What the network keeps and what it costs to buy: `efficiency.loss_db` with the pad depths and the compensation audit that explain it, and `parts.total` with where the bodies went. Then the ablation report, if the topology is still open: an element nothing recovers from losing is settled, an element the rest of the network absorbs is a decision to make and write down.
7. Acoustic crossings inside both drivers' published ranges, with the woofer's beamwidth near the horn's coverage at the crossing.
8. Tolerance envelope and the depth-perturbation result, before admiring the nominal curve.
9. What the fit assumed: datasheet phase, prior impedance models, no measurement. Select final stock values using the declared source basis and robustness studies, and document their predicted performance.

## 10. Model scope and final design values

Source impedance, installed acoustic phase, sample variation, thermal drift, port noise and cabinet vibration carry different levels of model uncertainty. A completed simulation design can specify final construction values: qualify its performance as predicted and select those values using plausible source, geometry, loss and tolerance scenarios. An empirical performance certification is a different claim. Measurement is an optional additional evidence source, not a prerequisite for completing this framework's design work.

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
Prefer published complex impedance curves where available; otherwise bracket plausible frequency-dependent load models rather than treating a single datasheet `Le` as exact.

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
formula, never the nominal rating on the label. Sensitivity to the load can grow with filter order. Compensation is one option; fitting directly into the actual complex load is another. Compare acoustic response, input impedance, real power and robustness before adding a branch. Filter order alone does not require compensation.

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
  has not been taken. Use a published current-dependent model where available, or select a suitable air-core alternative when uncertainty about saturation is decisive. The framework's part records should carry "not published" rather than a
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
- **Capacitors.** Select dielectric and construction by actual tolerance, ESR, AC current/voltage,
  temperature, lifetime, volume and cost, as in section 7. The earlier blanket ban on bipolar
  electrolytics conflicted with the crossover-specific manufacturer data already cited there and is
  withdrawn. Film parts can offer tighter tolerance and lower loss; a suitable bipolar electrolytic
  remains an option, particularly for a large shunt value, if its actual specifications and the
  sensitivity study support it. Neither a premium label nor an unspecified class-wide tolerance
  establishes suitability. Voltage-dependent Class II ceramics need a bias-dependent model before
  they can be treated as a constant capacitor.
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

## 13. Pad bodies and coil resistance as design variables

**Circuit derivation, resistive screening only.** A series pad `R` feeding a resistive driver `Re` at rms voltage `V` dissipates `P_R = V^2 R / (R + Re)^2`, while driver power is `P_driver = V^2 Re / (R + Re)^2` and attenuation is `20 log10((R + Re)/Re)`. For `N` equal bodies realizing the same total resistance with equal sharing, each dissipates `P_R/N`; the count needed at an allowed per-body dissipation `P_allowed` is `ceil(P_R/P_allowed)`. The count changes at discrete crossings of `P_R = N P_allowed`. Heat is not monotonic over every possible `R`: it peaks at `R = Re`. Removing attenuation can increase driver stress, so check both powers. A matched L-pad has a different power-sharing relation (section 8).

**Practice.** Before pursuing a louder driver to remove resistor bodies, compare attainable, calibrated level gains with those count crossings. Then verify the actual complex loaded network, including filter voltage magnification, mounting derating and upper-driver limits. This calculation screens a proposal; it does not replace `crossover_network` leaf stress or qualify enclosed endurance.

**Coil DCR is a trade, not an optimization direction.** In a simple low-frequency series path, `Zin = Zdriver + Rwire + DCR`; a shunt capacitor or compensation branch changes that relation. More DCR can raise a low impedance minimum while spending voltage and heat (`I_rms^2 DCR`). Compare actual stock inductance/DCR pairs after refitting, recording minimum impedance, fixed-frequency bass, sensitivity, ripple, cost and coil heat. Neither the lowest DCR nor the highest load magnitude is automatically the right choice. An absent current or thermal rating remains unknown.

For series/parallel banks, compute leaf powers from each leaf's voltage/current and sum at the same frequency. Summing unrelated per-part maxima overstates simultaneous heat, while assigning a whole bank's power to one leaf overstates that leaf's stress. `crossover_network` reports physical leaves and conservation is checked against `board_nodal`; changing a bank requires regenerating both the model and construction artifacts.

## 14. Driver impedance and physical realization

Mixed nominal driver impedances can be useful in a passive level budget; compare voltage sensitivity
and complete loaded input impedance rather than matching nominal labels. A no-series-resistor
network is an option, not a quality target. For a resistive prototype at fixed corner, capacitor
values scale as `1/R` and inductor values as `R`; actual cost and package size need inventory data.
Electrical crossings and acoustic crossings are different observables: the latter include driver response, baffle effects and propagation. Compare the complete acoustic branches and amplifier load when choosing driver impedances.

Physical realization is covered by [crossover assembly](crossover-assembly.md); unmodeled sonic
preferences are not numeric advantages in the model.

## Sources

- Jantzen Audio technical FAQ, "Coil types and where to use them" and "P-core inductors - Ferrite and non-ferrite powder cores". First-hand manufacturer statement that power handling and saturation points are not measured for their coils, the ferrite-versus-powder saturation behaviour, the 1.2 kHz practice threshold and the air-core hierarchy. A vendor source, and the rules of thumb in it carry no derivation. https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/

- Elliott, R., "Linkwitz-Riley Crossovers - Passive", Elliott Sound Products - practical passive design: component formulas, impedance compensation, coil DCR loss, L-pads and what changes with temperature. <https://sound-au.com/lr-passive.htm>
- Linkwitz, S. H., "Active Crossover Networks for Noncoincident Drivers", *Journal of the Audio Engineering Society*, vol. 24, no. 1, pp. 2-8, 1976 - the LR alignment and the lobing that comes from driver offset. <https://aes2.org/publications/elibrary-page/?id=2649>
- Small, R. H., "Constant-Voltage Crossover Network Design", *Journal of the Audio Engineering Society*, vol. 19, no. 1, pp. 12-19, 1971 - what exact summation requires, and why it limits the slope. <https://aes2.org/publications/elibrary-page/?id=2214>
- Lipshitz, S. P., Vanderkooy, J., "A Family of Linear-Phase Crossover Networks of High Slope Derived by Time Delay", *Journal of the Audio Engineering Society*, vol. 31, no. 1/2, pp. 2-20, 1983 - the trade between flat summation, slope and phase.
- Zobel, O. J., "Theory and Design of Uniform and Composite Electric Wave-Filters", *Bell System Technical Journal*, vol. 2, no. 1, 1923 - the impedance-compensation network by its original name.
- Dickason, V., *The Loudspeaker Design Cookbook*, 8th ed., Audio Amateur Press - crossover topologies, L-pads, Zobels, notch filters and component practice in one place.
- Beranek, L. L., Mellow, T. J., *Acoustics: Sound Fields and Transducers*, Academic Press, 2012 - the electro-mechano-acoustic models the ladders terminate into.
- D'Appolito, J., *Testing Loudspeakers*, Audio Amateur Press - methods for optional empirical characterization.
- IEC 60268-5, *Sound system equipment - Part 5: Loudspeakers* - the signal conditions under which power ratings are defined.
- The manufacturer's datasheet of the exact part, read for the condition its rating applies to: free air with a derating curve, or a held case temperature on a heatsink.
- Nichicon, *Aluminum Electrolytic Capacitors UDB series*, catalogue CAT.8100M - a bipolarized electrolytic "designed specifically for crossover networks in Hi-Fi sound systems": +/-20 percent at 1 kHz, tan delta at most 0.10 at 1 kHz and 0.15 at 5 kHz, 50 V rated, -40 to +85 C, and the allowable continuous current table quoted in section 7. The catalogue also marks the series "scheduled to be discontinued, not recommended for new designs", which is where the availability point comes from. Manufacturer datasheet read at first hand. <https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-udb.pdf>
- Jantzen Audio, *Standard Z-Cap* product datasheet - a metallized polypropylene crossover capacitor: 400 V DC / 250 V AC, +/-5 percent, dielectric absorption below 0.5 percent, self-inductance under 15 nH, and ESR given as "extremely low" with no figure, which is the gap the model's explicit ESR prior fills. Manufacturer datasheet.
- Bateman, C., "Capacitor Sound" series, *Electronics World*, 2002-2003 - measured distortion of capacitor dielectrics. Cited in section 7 only for what it does **not** establish here: the measurements are of small capacitance values at small signal levels in electronics, not of crossover-scale parts across a driver, and no source consulted extends them to that case. Abstract and article summaries read; the full series was not.
- Benjamin, E., "Audio Power Amplifiers for Loudspeaker Loads", *Journal of the Audio Engineering Society*, vol. 42, no. 9, p. 670, 1994 - the analysis behind equivalent peak dissipation resistance, which is why a load's phase angle makes it harder to drive than its modulus alone says. Abstract read; the body was not, so section 6 quotes no figure from it.
- Elliott, R., "Impedance Compensation" and "Capacitor Characteristics" and "Bi-amping - Not Quite Magic" and "L-pad calculations", Elliott Sound Products - the Zobel and notch conventions, the resistive-bandwidth target, L-pad and audit formulas, capacitor dielectric practice and tolerance, coil and voice-coil thermal drift, insertion loss and the bi-amping bound. Self-published engineering writing, not peer reviewed; the arithmetic is checkable and the rules of thumb are labelled as such above. <https://sound-au.com/articles/z-compensation.htm>
- "Zobel Networks", True Audio - the alternative Zobel convention sized from nominal rather than measured resistance, recorded here for the disagreement it creates. <https://www.trueaudio.com/st_zobel.htm>
- Elliott, R., "Serial vs. Parallel Crossover Networks" and Rane, "A Bessel Filter Crossover, and its Relation to Others", RaneNote 147 - the series component forms and the first-order impedance-invariance property, and the Bessel family's phase, summation and normalisation figures. <https://sound-au.com/parallel-series.htm> and <https://www.ranecommercial.com/legacy/note147.html>
- Jantzen Audio air-core coil catalogue - published inductance, DCR, wire gauge and physical envelope per part, the basis of the gauge-against-DCR scaling in section 12; tolerance and current ratings are not in the catalogue and must come from the per-part datasheet. <https://www.jantzen-audio.com/product-category/air-core-wire-coil/>
- In this repository: `framework/simulations/crossover_network/README.md` and `framework/simulations/crossover_fit/README.md` for what the applications compute and report.
