---
id: target-response
applies_when: Setting the target a crossover is fitted to, or judging whether a predicted response is a good one
updated: 2026-09-15
---

# What a good frequency response looks like

A loudspeaker is not judged by one curve, and it is not judged by the peak-to-peak spread of that
curve over a wide band. The published research on listener preference says what the family of curves
should look like and, more usefully, says which kinds of deviation cost a lot and which cost almost
nothing. A design fitted against the wrong statistic can be optimal in that statistic and still be a
poor loudspeaker.

## 1. The shape that is preferred

Toole's review of the literature states the pattern that consistently scored well in controlled
listening: a smooth, flat, wide-band axial frequency response, combined with similarly well-behaved
off-axis responses, up to and including the sound power. Three separate requirements are hiding in
that sentence:

1. **The direct sound is flat.** The on-axis and listening-window curves should be flat, not merely
   smooth, because that is what reaches the listener first and dominates timbre.
2. **The off-axis family is smooth and falls gently.** Off-axis curves should tilt gently downwards
   and should keep the same shape as each other. What is fatal is not that the speaker gets quieter
   off axis, but that it changes shape off axis, because the reflected energy then arrives with a
   different spectrum from the direct sound.
3. **The transition between the two regions is not free.** In rooms, the loudspeaker and the room
   interact differently above and below a transition region around 300 Hz. Below it the room's modes
   dominate; above it what matters is the direct sound and the reflections, which is where the
   directivity requirement comes from.

## 2. Which deviations cost, and how much

Olive built a regression model that predicts double-blind preference ratings from anechoic
measurements. Its variables are the useful part, because each one isolates a different kind of
deviation. In the generalized model fitted over seventy loudspeakers:

```
Preference = 12.69 - 2.49 NBD_ON - 2.99 NBD_PIR - 4.31 LFX + 2.32 SM_PIR
```

- **NBD, narrow band deviation** — the mean absolute deviation *within* each half-octave band. It
  measures wiggle at the scale of a half octave and is blind to a slow trend across the spectrum.
  The two NBD terms together carry about half the model.
- **SM, smoothness** — the `r^2` goodness of fit of a regression line through the curve from 100 Hz
  to 16 kHz. It rewards a response that follows *a* smooth trend. A gently sloping straight line
  scores as well as a flat one; a curve with a hump and a dip does not, even if its two ends match.
- **LFX, low-frequency extension** — the logarithm of the first frequency below 300 Hz at which the
  **sound power** curve is 6 dB below its reference level. It carries about 30 % of the model on its
  own, the single largest contribution.

The signs are the message. Every deviation term is negative and the smoothness term is positive, so
the model rewards a response that is *both* free of local wiggle and describable by one smooth trend,
and it rewards bass extension heavily.

**What follows for a design.** A broad, gentle tilt of a decibel or two across the spectrum is
cheap. A narrow peak or dip, a step at a crossover, or a bump-and-dip pair across an octave is
expensive. A peak-to-peak ripple figure computed over a decade cannot tell those apart: a 3 dB slow
tilt and a 3 dB narrow notch produce the same number and are not remotely the same defect.

## 3. Resonances, and why Q matters

Toole and Olive measured the audibility of resonances against frequency, Q, level, delay and
programme material. The result that matters here is that audibility is not a function of amplitude
alone: for the same peak height, resonances of medium and low Q are easier to hear than high-Q ones,
and the presence of reflections in a room *lowers* the detection thresholds for medium- and low-Q
resonances rather than masking them.

So a broad 2 dB hump spanning an octave is a more serious defect than a narrow 2 dB spike, and
listening in a room makes it more audible, not less. This is the perceptual reason behind the
metric in section 2: it is the half-octave-scale deviation that gets penalized.

## 4. The family of curves, and their names

ANSI/CTA-2034 defines the measurement set the preference work is built on, so its names are worth
using consistently: a set of anechoic responses on horizontal and vertical orbits at ten-degree
increments, from which are derived the **on-axis** response, the **listening window** (an average
over a small range of horizontal and vertical angles), the **early reflections** curve, the **sound
power**, the **directivity index** as the difference between the listening window and the sound
power, and the **predicted in-room response** as a weighted sum of direct and reflected energy.

A directivity index that rises smoothly with frequency is the signature of a well-behaved design.
A directivity index with steps or dips in it says the pattern changes abruptly somewhere, which is
almost always a crossover where the two drivers' coverage did not match — a spacing and driver-size
problem, not a filter problem. See `baffle-and-driver-placement.md` section 3.

## 5. What the framework computes, and how it maps

The applications here do not produce a spinorama, a directivity index or a predicted in-room
response, and no learning or objective should claim one. What they do produce maps onto the above as
follows.

- `whole_speaker` gives the on-axis curve, horizontal and vertical families at the angles you ask
  for, and window statistics over a stated angular window. A listening-window-like figure can be
  approximated by averaging its horizontal and vertical curves over the window angles; an early
  reflections or sound power estimate cannot, because the orbit is incomplete. Say which it is.
- `response_metrics` reports, per band, the mean, the ripple, the **standard deviation** and the
  **slope**, plus octave-band means and the band held within a tolerance. The standard deviation
  over a narrow band is the closest available relative of NBD, and the slope with the deviation about
  it is the closest relative of SM. Both are more informative than the ripple figure and neither is
  currently the thing most projects quote.
- Sustained cutoffs from `whole_speaker` are measured on the on-axis curve against a chosen reference
  band. LFX is defined on the **sound power** curve at **-6 dB**. An on-axis f3 is therefore not
  LFX, is usually the more flattering of the two, and should not be compared with published figures
  as if it were. See `keep-system-and-box-cutoffs-separate` in `framework/learnings` for how much a
  cutoff moves for a small change of reference level.

## 6. Setting the target for a fit

`crossover_fit` takes a target level and a band. What the sections above imply for that choice:

- **Fit to a level, not to a shape, unless the shape is justified.** A flat target for the direct
  sound is what the research supports. A deliberately tilted target is a decision to make explicitly
  and to write down with its reason, not something to arrive at by weighting.
- **Weight the bands by what a deviation there costs**, and remember that the fit sees only the
  on-axis sum unless you give it angles. `target.vertical_angles_deg` exists so that the fit is not
  optimizing a curve that only one microphone position will ever see.
- **Judge the result on the family, not the fit residual.** A low in-band RMS error with a step in
  the vertical map at the crossover is a worse loudspeaker than a slightly worse residual without
  one.
- **Check the shape of what is left.** Read the slope and the deviation about it across the whole
  band, and look for local features at the crossovers, at the baffle step and at the box tuning.
  Those three are where a three-way's curve shape usually goes wrong, and all three are decided
  before the network is fitted.

## 7. The CTA-2034-A chain, when you need the numbers rather than the names

Section 4 gives the names; this is how each curve is actually computed, for when a result has to be
comparable with published spinorama data.

**Two different levels of confidence apply inside this section, and they must not be conflated.**

- The **curve-assembly geometry** — which angles go in which group, and the sound-power ring weights —
  comes from one open-source reimplementation of the standard, not from the standard text.
  ANSI/CTA-2034-A remains paywalled and has not been read here. Two of the reimplementation's details
  are known to differ from the literal standard and are flagged below. Verify against the standard
  before publishing a figure as a CTA-2034-A result.
- The **four preference predictors and the regression that combines them** are no longer in that
  position. They have been read at first hand in Harman's own patent specification (US 8,311,232 B2,
  Olive, "Method for predicting loudspeaker preference"), which states the definitions, the bands and
  the coefficients. The patent's definitions and its generalized-model equation agree exactly with
  what section 2 and this section already said, so those statements are now confirmed against a
  primary source rather than resting on a reimplementation.

- **Listening window** — an RMS spatial average, in the pressure domain and not in decibels, of nine
  positions: horizontal +/-10, +/-20, +/-30 degrees and vertical on-axis, +10, -10 degrees, with the
  on-axis point counted once.
- **Early reflections**, five fixed groups: floor bounce (vertical -20, -30, -40), ceiling bounce
  (vertical +40, +50, +60), front wall (horizontal on-axis and +/-10 to +/-30), side wall (horizontal
  +/-40 to +/-80 in ten-degree steps), rear wall (horizontal +/-90 to +/-170 plus 180). **The rear-wall
  set is a known discrepancy**: the literal standard specifies only +/-90 and 180 degrees. Early
  reflections, the in-room curve and the early-reflections DI all differ between tools because of it.
- **Sound power** — an area-weighted RMS over the full 70-point spin (36 horizontal plus 34 vertical,
  the duplicated on-axis and 180-degree points dropped), each ring weighted by the solid angle it
  represents. The relative ring weights run 0.0304 on axis, 0.2378 at 10 degrees, then 0.4501, 0.6227,
  0.7535, 0.8479, 0.9131, 0.9554, 0.9791 and 0.9867 at 90 degrees. The 90-degree ring carries about
  **32 times** the weight of the on-axis point, which is the quantitative reason on-axis flatness
  barely moves sound power. The implementation doubles the 90-degree weight as a correction that is
  not obviously in the standard — a second flagged discrepancy.
- **Predicted in-room response** — an energy sum, weights applied to squared pressure:
  `PIR = 0.12 * LW^2 + 0.44 * ER^2 + 0.44 * SP^2`. Eighty-eight percent of it is off-axis behaviour,
  which is why a ragged power response cannot be repaired by on-axis equalisation, and why two of the
  four preference terms are effectively directivity measurements.
- **Directivity indices** — `SPDI = LW - SP` and `ERDI = LW - total ER`, in dB.

The four predictors in the section 2 equation, with their bands:

- **NBD** — the average over half-octave bands of the mean absolute deviation within each band,
  100 Hz to 12 kHz, ten log-spaced samples per band. A monotonic tilt costs almost nothing; a 1 dB
  wiggle inside one half-octave costs directly.
- **SM** — the `r^2` of a straight-line fit of level against log frequency, 100 Hz to 16 kHz. Because
  the line is allowed to slope, SM polices scatter and not tilt, and a design with a large total tilt
  can score well; it is the weakest and most easily gamed of the four.
- **LFX** — `log10` of the first frequency below 300 Hz at which the **sound power** curve falls 6 dB
  below the listening-window mean taken over 300 Hz to 10 kHz, defaulting to `log10(300)` if no such
  point exists. One octave of extension is worth `4.31 * log10(2) = 1.30` preference points. It
  carries no penalty for Q, group delay or distortion, so it rewards a boomy high-Q alignment exactly
  as much as a clean one — never use LFX alone as a bass objective.
- **LFQ, low-frequency quality** — the mean absolute deviation of the listening-window curve between
  LFX and 300 Hz. It is computed but carries zero weight in the published generalized regression.
- **AAD, absolute average deviation** — the mean absolute deviation from the mean level between
  200 and 400 Hz, over 1/20-octave bands from 100 Hz to 16 kHz. It appears in the patent's earlier
  model form (as ADDON) and not in the generalized four-term model; it is recorded here so that an
  older published score using AAD can be recognised for what it is rather than mistaken for NBD.

Two further details from the patent that matter when implementing this:

- **NBD, SM and AAD are each defined over any of the seven curves** — ON, LW, ER, PIR, SP, ERDI and
  SPDI — while **LFX and LFQ are defined on the sound power curve only**. A metric is meaningless
  without the curve it was computed from, so always report it as `NBD_ON`, `SM_PIR` and so on, never
  bare.
- The relative contributions of the four terms in the generalized model are **NBD_ON 31.5 %,
  LFX 30.5 %, NBD_PIR 20.5 %, SM_PIR 17.5 %**. On-axis wiggle and bass extension together carry
  nearly two thirds of the score.

A "with subwoofer" score substitutes a fixed extension for the speaker's own LFX; the constant is
contested between 14.5 Hz and 20 Hz, a difference of 0.60 points, so state which was used.

## 8. Acceptance envelopes from the broadcast standards

Where the preference model gives a ranking, the broadcast monitor standards give pass/fail numbers.
They are the only hard acceptance envelope this repository has a source for, they apply to a reference
monitor rather than to a consumer or PA design, and the two documents disagree in two places.

- **On-axis amplitude**: inside a 4 dB total tolerance band from 40 Hz to 16 kHz, third-octave bands,
  pink noise. Units in a stereo or multichannel set matched within 1.0 dB over at least 250 Hz to
  2 kHz.
- **Off axis**: within 3 dB of on-axis anywhere inside +/-10 degrees, within 4 dB at +/-30 degrees
  horizontally. No vertical limit is imposed at +/-30 degrees, so a design can comply and still have a
  severe vertical crossover null.
- **Directivity index**: 6 to 12 dB over 500 Hz to 10 kHz (ITU-R BS.1116-3) or 4 to 12 dB over 250 Hz
  to 16 kHz (EBU Tech 3276), rising smoothly, with the radiation maximum on the main axis at every
  frequency. **The two documents disagree**; neither defines the integration method, which changes
  the value.
- **Distortion**: driven at a constant voltage giving 90 dB SPL averaged over 250 Hz to 2 kHz at 1 m,
  no harmonic component above 3 percent from 40 to 250 Hz, or above 1 percent from 250 Hz to 16 kHz.
  Per component, not total, and referenced to the band-average level rather than to the local
  fundamental.
- **Stored energy**: after a sinusoidal burst at frequency `f`, on-axis pressure falls to `1/e` within
  `2.5 / f` seconds (EBU) or `5 / f` seconds (ITU) — **a factor-of-two disagreement**; cite the
  document you are testing against.
- **Dynamic range**: at least 108 dB at 1 m sustained for ten minutes on programme-simulating noise
  with no damage and no protection circuit engaging, and self-noise at or below 10 dB(A).

Third-octave smoothing hides narrow resonances and diffraction ripple, so a design that passes these
bands is not automatically smooth at the resolution the NBD metric in section 7 uses. The two views
are complementary: the standards bound the worst case, the preference model ranks what is left.

**Reaching a level at all.** The amplifier arithmetic that goes with a target SPL is
`dBW = Lreq - Lsens + 20 log10(D2 / Dref) + HR`, with at least 3 dB of headroom, and it assumes the
driver is not already in thermal or excursion compression at that power — which, per
`driver-selection.md` section 5, is exactly where a passive system's real ceiling lives.

## Sources

- S. E. Olive, "Method for predicting loudspeaker preference", US Patent 8,311,232 B2, Harman International. The preference-model definitions, bands and regression coefficients read at first hand; the patent form of the two 2004 AES papers, which are themselves paywalled. https://patents.google.com/patent/US8311232B2/en

- Toole, F. E., "Loudspeakers and Rooms for Sound Reproduction — A Scientific Review", *Journal of the Audio Engineering Society*, vol. 54, no. 6, pp. 451-476, 2006 — the preferred pattern, the transition region near 300 Hz, and the role of reflections. <https://aes2.org/publications/elibrary-page/?id=13686>
- Toole, F. E., and Olive, S. E., "The Modification of Timbre by Resonances: Perception and Measurement", *Journal of the Audio Engineering Society*, vol. 36, no. 3, pp. 122-142, 1988 — audibility of resonances against Q, level and programme, and the effect of reflections on the thresholds. <https://aes2.org/publications/elibrary-page/?id=5163>
- Olive, S. E., "A Multiple Regression Model for Predicting Loudspeaker Preference Using Objective Measurements: Part I — Listening Test Results", AES 116th Convention, preprint 6113, 2004; "Part II — Development of the Model", AES 117th Convention, preprint 6190, 2004. <https://aes2.org/publications/elibrary-page/?id=12847>
- Olive, S. E., "Method for predicting loudspeaker preference", US Patent 8,311,232 B2, 2012 — the model equations, the variable definitions and their relative contributions, in a publicly readable form. <https://patents.google.com/patent/US8311232B2/en>
- ANSI/CTA-2034-A, *Standard Method of Measurement for In-Home Loudspeakers*, Consumer Technology Association, 2015 (revised as ANSI/CTA-2034-B, 2024) — the definitions of the listening window, early reflections, sound power, directivity index and predicted in-room response. <https://webstore.ansi.org/standards/cea/cea20342015ansi>
- Devantier, A., "Characterizing the Amplitude Response of Loudspeaker Systems", AES 113th Convention, preprint 5638, 2002 — the measurement set the standard is built on.
- Aubert, P., *spinorama* - an open-source reimplementation of the CTA-2034-A curve computations and the Olive predictors, the source of every computational detail in section 7 including the two flagged discrepancies against the standard text. <https://github.com/pierreaubert/spinorama>
- EBU Tech 3276, *Listening conditions for the assessment of sound programme material: monophonic and two-channel stereophonic*, European Broadcasting Union - the monitor acceptance envelope in section 8. <https://tech.ebu.ch/docs/tech/tech3276.pdf>
- ITU-R BS.1116-3, *Methods for the subjective assessment of small impairments in audio systems*, International Telecommunication Union, 2015 - the same envelope with its two disagreements, plus the listening-room requirements. <https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1116-3-201502-I!!PDF-E.pdf>
- In this repository: `simulations/whole_speaker/README.md` for the angle sets and window statistics, `simulations/response_metrics/README.md` for the slope, deviation and band statistics, and `simulations/crossover_fit/README.md` for the target and weighting inputs.
