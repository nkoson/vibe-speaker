---
id: set-the-fit-target-from-the-woofer-not-the-optimizer
date: 2026-09-14
project: forte-iii-r3, forte-iii-single-pr-20260914
phase: design
confidence: medium
applies_when: Running crossover_fit, or reading a system sensitivity that came out lower than the drivers suggest
tags: [crossover-fit, sensitivity, insertion-loss, zobel, baffle-step]
---

## Observation
Three first-iteration candidates were fitted with `target.spl_db` set to `auto`, which is the mean
of the starting response in the fit band. Each settled 2 to 6.6 dB below what its own woofer could
hold: the woofers' free-field band means from 180 Hz to the crossover were 95.61, 94.26 and
100.61 dB, and the system sensitivities came out at 92.90, 92.26 and 94.01 dB. The optimizer was
not wrong; it was flattening the response around wherever the starting ladder happened to sit.

Two defaults in the ladder contributed. A baffle-step shelf, a series inductor with a parallel
resistor, adds series resistance that a driver whose own falling response already cancels the step
does not need; in one candidate the fitted shelf resistor and three coil DCRs together took
3.2 dB. A Zobel sized by the textbook rule, capacitance equal to Le divided by R squared, has
under 10 ohm of reactance at 140 Hz on a 4.5 mH voice coil, so instead of flattening the load near
the crossover it loaded the amplifier in the bass: every candidate before the fix had an input
impedance minimum between 2.6 and 3.5 ohm, and after sizing the Zobel capacitor from the crossover
frequency instead, 4.1 to 5.1 ohm.

A compact single-PR study found that a requested low-loss refinement still retained high-DCR
fallbacks for coil values absent from the stock inventory. Exact low-loss records at six
plausible LF values were added before the final round. This fixed inconsistent loss assumptions,
but did not establish Forte-level sensitivity with the required bass extension: the final
system was 88.340 dB with a sustained 35.008 Hz f3. A plausible upper-bass target alone had
not established the complete 38-300 Hz envelope.

## Why it mattered
The first iteration was scored against a system level that had no engineering justification, and
its evaluation concluded that the sensitivity objective and the impedance objective could not be
met together in that inventory. Once the losses were removed and the target was set explicitly,
both were met at once by the same parts.

The single-PR revision used two parallel RSS315HF-4 cones in one chamber to reach 90.511 dB with 34.298 Hz sustained system f3. The physical minimum impedance became 1.888 ohms. This was a successful voltage-sensitivity/bass trade within that brief, not evidence of improved one-watt efficiency or equally easy amplifier loading. A 24-draw stock-tolerance screen kept sensitivity above 90 dB, but one f3 result exceeded the strict bass target.

## Advice
Consider computing the level the woofer can actually hold before fitting: take the woofer section's
pressure, apply its baffle factor, and average from the bottom of its passband to the crossover.
Subtract a small allowance for coil and wiring resistance and hand that number to
`crossover_fit` as an explicit target rather than letting it choose. Then check what the network
gives away: read the woofer branch's transfer in the passband, and if it is more than about a
decibel below unity, look for series resistance that is not buying anything. A baffle-step shelf
is only needed when the driver's own response does not already fall across the step. Sizing a
Zobel's capacitor from the crossover frequency rather than from the driver's inductance keeps the
flattening where the filter needs it and stops the network loading the amplifier two octaves
lower. Quantize woofer coils to the lowest DCR the stock list offers at that value, not to a
default gauge.

Consider checking exact stock coverage across the likely LF coil values before fitting and
reporting every fallback after quantization. An instruction to use low-loss coils does not
ensure that a sparse inventory can supply them. When deep extension is central, inspect the
absolute response across the whole bass band and a fixed-LF voicing sweep before accepting
the upper-bass mean as the system target. Failed fits from incomplete stock or poor seeds do
not by themselves establish physical infeasibility.

For parallel woofers, consider reporting voltage sensitivity, amplifier current and minimum impedance together. The minimum bass impedance is not the appropriate divisor for converting a wideband unweighted voltage sensitivity into one-watt sensitivity. Once joint targets are nominally met, check small component and acoustic-reference changes before treating a narrow cutoff margin as robust.

## Evidence
- `framework/projects/forte-iii-r3/project.json`, the log entry diagnosing 2 to 6.6 dB of avoidable insertion loss
- `framework/projects/forte-iii-r3/evaluations/all-candidate-figures.json`, sensitivity and impedance before and after
- `framework/projects/forte-iii-r3/postmortem.md`, reasons 3 and 4
- `framework/projects/forte-iii-single-pr-20260914/candidates/c04/sim/crossover_network.params.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c07/sim/crossover_network.params.json`
- `framework/projects/forte-iii-single-pr-20260914/inventory/stock/mundorf_vs180_*.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, incomplete low-loss refinement
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-physical-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/whole-tolerance-summary.json`
