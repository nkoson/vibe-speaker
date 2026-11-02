---
id: measurement-analysis
applies_when: Analysing measured loudspeaker or crossover behaviour, selecting corrective changes, or planning diagnostic measurements
updated: 2026-11-02
---

# Measured speaker and crossover analysis

The purpose is to improve the speaker. Establish the acquisition basis briefly, then explain the acoustic branches, their sum, tonal balance and operating limits. The diagnostic sequences below are engineering deductions from the cited linear-system relationships and measurement methods; they are not automatic fault classifications supplied by REW.

## 1. Branch output, overlap and summation

For complex acoustic pressures W and T at one observation point, the combined response is W+T. Consequently:

```
abs(abs(W)-abs(T)) <= abs(W+T) <= abs(W)+abs(T)
abs(W+T)^2 = abs(W)^2 + abs(T)^2 + 2 abs(W) abs(T) cos(relative_phase)
```

At equal branch levels, in-phase addition gives +6.02 dB above either branch; opposite phase can cancel. Electrical filter corner, acoustic equal-level crossing and the complete overlap band are different quantities. Judge the acoustic sum, with driver response, load, polarity and acoustic offsets included. See [passive crossover principles](crossover-design.md#2-the-target-is-acoustic-not-electrical) and [REW trace arithmetic](https://www.roomeqwizard.com/help/help_en-GB/html/graph_allspl.html).

| Measured feature | Circuit/physical hypothesis | Measurement that distinguishes it | Design response supported by that result |
|---|---|---|---|
| Both branches are weak in the handover; even their maximum possible sum is low | Insufficient acoustic overlap; excessive low-pass attenuation or high-pass arriving too high | Same-drive filtered woofer, filtered tweeter and combined captures; direct woofer versus filtered woofer | Extend the deficient branch or coordinate both slopes; compute the complete sum and retain tweeter protection |
| Branch levels are adequate but combined output falls well below their upper bound | Relative phase/polarity or acoustic offset | Common-reference branch phase plus normal/reversed-tweeter combined measurements at unchanged geometry | Change polarity only if the measured sum supports it; otherwise refit filter phase/overlap or geometry |
| Broad treble shelf with otherwise good overlap | Attenuator value or tweeter sensitivity balance | Compare absolute tweeter/woofer levels and a controlled resistor change | Refit attenuation and loaded high-pass together; a series resistor is not a pure gain control |
| Woofer response rolls off much earlier through the crossover than expected | Actual driver impedance, wrong effective L/C, DCR or connection topology | Direct/filtered woofer pair; calibrated complex impedance; component value and node checks | Correct the loaded low-pass model or build, then recompute transfer, phase and sum |
| Narrow feature persists in one branch through filter changes | Driver resonance/breakup, diffraction or cabinet mechanism | Same branch at nearby axes and with one controlled filter change; impedance where relevant | Apply a targeted notch/damping or crossover change only after identifying the mechanism |
| Sum changes strongly with vertical angle | Driver spacing, acoustic offset and crossover phase produce lobing | Fixed-radius vertical measurements above/below the design axis, same drive/reference | Adjust acoustic handover/phase or spacing; assess useful listening window, not just one on-axis point |

These distinctions follow the complex-sum relation and the load-sensitive network described in [crossover design](crossover-design.md). Component selection requires actual topology and the driver's complex impedance. A microphone cannot measure electrical impedance. REW's electrical method uses a sense resistor and two interface inputs, with open/short/reference calibration. [REW impedance measurement](https://www.roomeqwizard.com/help/help_en-GB/html/impedancemeasurement.html).

## 2. Retargeting a measured branch

Use the corrected direct driver capture where available. Otherwise a filtered branch can be retargeted over a reliable band as `new = measured * H_new / H_old`, with the old and new **loaded complex electrical transfers**. Division where the old response is strongly suppressed amplifies noise; inspect that band rather than extending a useful result through a transfer zero.

Perform this transformation before time gating. Time multiplication and frequency multiplication do not commute: a window convolves spectra, while a changed crossover changes the impulse's ringing. Dividing a short-gated old-filter response by its full transfer does not recover the original driver response. Preserve the calibrated drive, shared time origin and polarity. Apply no independent gain fit. This follows the Fourier operations in [NumPy's DFT reference](https://numpy.org/doc/stable/reference/routines.fft.html) and [measured-response processing](measured-response-processing.md).

## 3. A short acquisition check

Read file metadata and previously confirmed conditions first. Verify the measurement identity, calibration file, branch/polarity, output setting, microphone axis/distance and whether older files were superseded. Equal sweep dBFS alone does not prove equal amplifier voltage; a user's confirmed unchanged output settings can establish a relative comparison without knowing absolute terminal voltage. Do not repeatedly ask for it or normalize away differences being investigated.

For UMIK-1, use 48 kHz and the microphone's serial-specific calibration. Pointing at the speaker uses the on-axis file; pointing upward uses the 90-degree file. [miniDSP UMIK setup](https://www.minidsp.com/applications/acoustic-measurements/umik-1-setup-with-rew).

REW saves multiple measurements in one MDAT. Text exports can contain zero phase placeholders. The raw IR and saved frequency response are distinct: microphone/soundcard calibration normally affects the frequency calculation, not the stored impulse, unless explicitly merged. Preserve already-calibrated saved curves; apply calibration once when recalculating from raw data. [REW file formats](https://www.roomeqwizard.com/help/help_en-GB/html/file.html), [REW impulse graph](https://www.roomeqwizard.com/help/help_en-GB/html/graph_impulse.html).

## 4. Timing for crossover analysis

An acoustic reference removes variable acquisition latency; a reference capable of high-frequency output is required. The reference path must remain the same between branch captures. A complete speaker can reference itself by selecting the same output for sweep and reference. Once its tweeter is disconnected for a woofer-only capture, that ordinary wiring no longer supplies the appropriate reference. Use a second fixed speaker, or deliberately isolated amplifier/branch routing with the tweeter protected. Do not join amplifier outputs or assume a shared-return crossover is already bi-amp ready. [REW measurement timing](https://www.roomeqwizard.com/help/help_en-GB/html/makingmeasurements.html#acousticref), [miniDSP same-output and separate-output examples](https://www.minidsp.com/applications/rew/speaker-time-alignment).

Enable `Adjust clock with acoustic ref` for separate USB input/output clocks. It adds an end reference for clock-rate correction. This does not justify independently centring each branch's impulse. Relative delay changes phase by `-360 f delay` degrees; remove only a declared common delay when presenting branch phase. A timing flag without reference geometry and retained offsets is not enough to assert common timing. [REW Analysis preferences](https://www.roomeqwizard.com/help/help_en-GB/html/analysis.html), [REW phase controls](https://www.roomeqwizard.com/help/help_en-GB/html/graph_splphase.html).

## 5. Windowing and display choices

Use the same absolute gate for related branch captures. Choose its right extent from the direct response and first relevant reflection, while allowing the crossover's own decay to remain. Compare nearby gate lengths when that changes the engineering conclusion. Frequency detail is limited on the order of inverse window duration; FFT zero padding cannot restore it. A 3 ms gate is useful around a few kilohertz, not for judging deep bass. REW's default long windows retain room contributions. [REW Analysis preferences](https://www.roomeqwizard.com/help/help_en-GB/html/analysis.html), [ARTA AN4, sections 1 and 5](https://artalabs.hr/AppNotes/AN4-FreeField-Rev03eng.pdf).

Retain unsmoothed complex data for addition and electrical retargeting; smooth the final magnitude for display. A broad shelf matters even if a narrow-band ripple statistic improves. Use little or no smoothing for bass resonances, and state the display bandwidth for crossover plots. Normalizing each branch changes the question from absolute output to shape. [REW SPL/phase graph](https://www.roomeqwizard.com/help/help_en-GB/html/graph_splphase.html).

## 6. Secondary diagnostic branches

These are targeted follow-ups when the data supports them, not substitutes for analysing the crossover.

| Evidence | Focused follow-up | Interpretation and action |
|---|---|---|
| A dip moves with mic/speaker position or changes with the reflection gate | A controlled position change; compare impulse-envelope timing | Treat geometry-dependent interference through placement/window selection rather than a large electrical boost |
| Bass behaviour cannot be separated with a short far-field gate | Cone and port/passive-radiator near-field captures at known drive; scale and combine correctly | Determine bass alignment and contributions before altering damping or tuning; include baffle correction once |
| Output rises less than a known input-voltage step | Repeat at lower/higher drive with cooldown and unchanged geometry | Quantify compression relative to the input step; inspect driver/network heating or excursion-dependent behaviour |
| THD percentage spikes where fundamental SPL is low | Inspect absolute harmonic SPL and noise at the corresponding harmonic frequencies | Distinguish low denominator/noise from increased harmonic output; choose a useful operating limit from level-dependent evidence |

Near-field merging requires source-specific area/geometry scaling and correct port/cone contributions; it is not an arbitrary visual offset. [ARTA AN4, sections 2–5](https://artalabs.hr/AppNotes/AN4-FreeField-Rev03eng.pdf). For distortion, REW records absolute harmonics and noise as well as relative figures; available harmonic orders reduce toward the measurement's upper bandwidth. Swept and stepped-sine analyses have different noise/separation behaviour. Do not generate THD from the ordinary linear impulse or sum percentages of harmonics. [REW distortion documentation](https://www.roomeqwizard.com/help/help_en-GB/html/graph_distortion.html).

For room decay, inspect frequency-dependent decay before quoting a single RT60. Domestic-room low frequencies are dominated by modes; a diffuse-field reverberation model often does not describe them. [REW RT60 documentation](https://www.roomeqwizard.com/help/help_en-GB/html/graph_rt60.html). For nonlinear mechanisms and thermal interpretation, use [Klippel's measurement literature](https://www.klippel.de/know-how/literature/application-notes.html) and [driver selection](driver-selection.md); do not infer a unique nonlinear parameter fault from one THD trace.

## Implementation provenance

The public [REW API](https://www.roomeqwizard.com/help/help/html/api.html) documents numerical response/IR exports and big-endian float arrays; it also supports headless operation on compatible builds. The offline importer instead reads serialized data using [javaobj-py3](https://github.com/tcalmant/python-javaobj), without executing the serialized Java classes. REW does not publish a stable MDAT field contract; supported structures and numerical conventions are documented in [the tool contract](../measurements/README.md) and tested separately from engineering interpretations. Unsupported schemas must produce an actionable format error rather than guessed units or calibration.

All external sources above are developer/manufacturer documentation or original engineering material. No forum or Reddit source is used.

## Sources

Consulted 2026-11-02; citations beside each procedure identify its supporting material.

- John Mulcahy, REW: [Making Measurements](https://www.roomeqwizard.com/help/help_en-GB/html/makingmeasurements.html), [Analysis Preferences](https://www.roomeqwizard.com/help/help_en-GB/html/analysis.html), [File Menu](https://www.roomeqwizard.com/help/help_en-GB/html/file.html), [API](https://www.roomeqwizard.com/help/help/html/api.html).
- John Mulcahy, REW graph documentation: [SPL and Phase](https://www.roomeqwizard.com/help/help_en-GB/html/graph_splphase.html), [All SPL](https://www.roomeqwizard.com/help/help_en-GB/html/graph_allspl.html), [Impulse](https://www.roomeqwizard.com/help/help_en-GB/html/graph_impulse.html), [Distortion](https://www.roomeqwizard.com/help/help_en-GB/html/graph_distortion.html), [RT60](https://www.roomeqwizard.com/help/help_en-GB/html/graph_rt60.html), [Impedance Measurement](https://www.roomeqwizard.com/help/help_en-GB/html/impedancemeasurement.html).
- miniDSP: [UMIK setup](https://www.minidsp.com/applications/acoustic-measurements/umik-1-setup-with-rew), [Speaker time alignment](https://www.minidsp.com/applications/rew/speaker-time-alignment).
- ARTA Labs: [Application Note 4, Loudspeaker Free-Field Response](https://artalabs.hr/AppNotes/AN4-FreeField-Rev03eng.pdf).
- NumPy developers: [DFT conventions](https://numpy.org/doc/stable/reference/routines.fft.html).
- javaobj-py3 maintainers: [parser source and documentation](https://github.com/tcalmant/python-javaobj). This is the serialization implementation source, not an acoustic authority.
