# Evaluation: iteration N

Project: `<slug>`. Evaluator reading of the result documents listed per candidate. Every figure below is quoted from a simulation result file with its path; judgements are the evaluator's.

## Objectives table

| Objective | Target (tolerance) | c01 | c02 | c03 | Source path |
|---|---|---|---|---|---|
| Sensitivity 500 to 10000 Hz mean, dB | 99 (1) | 96.4 | 98.1 | 98.9 | `whole_speaker.results.statistics.mean_spl_in_sensitivity_band_db` |
| f6 sustained, Hz | 38 (3) | 36.7 | 41.2 | 35.9 | `lf_box.results.curves.0.statistics.cutoffs.f6.value_hz` |
| Impedance minimum 20 to 20000 Hz, ohm | 6.4 (0.4) | 4.3 | 6.1 | 6.6 | `crossover_network.results.statistics.input_z_min_ohm` |
| Ripple 200 to 10000 Hz, dB | 6 (1) | 4.7 | 5.9 | 7.4 | `whole_speaker.results.statistics.ripple_200_10000_db` |
| Output before first limit at 20 to 300 Hz, dB | 110 (2) | 112 | 108 | 111 | `lf_box.results.linear_scaling_to_limits` |

## Per candidate

### c01
- Strengths: ...
- Weaknesses: ... (quote the figure and the file)
- Reference comparison: RMS difference to the digitized reference curve 40 to 16000 Hz is 2.1 dB after level alignment (`response_metrics.results.comparisons.1.rms_difference_db`); the candidate is 3 dB lower at 60 to 100 Hz.
- Risks in the model: which figures rest on priors (datasheet phase, horn coverage), which on measurements.
- Refinement request: concrete changes for the designer (part, value, dimension), with the expected effect.

## Ranking and decision

1. c03: ...
2. c02: ...
3. c01: ...

Continue: yes / no. If the iteration limit is reached, the recommended candidate for the final package and the reasons.
