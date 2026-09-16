---
id: do-not-double-count-woofer-rolloff
date: 2026-09-15
project: forte-iii-three-way, forte-iii-performance-20260914, forte-iii-r3, forte-iii-one-woofer-20260915
phase: validation
confidence: high
applies_when: Building a woofer section from lf_box plus a datasheet curve
tags: [source_response, woofer, published-curve, blend]
---

## Observation
The woofer section was first built by multiplying the `lf_box` cone pressure, which already contains the voice-coil inductance roll-off, by the manufacturer's full response curve, which contains the same roll-off. The upper woofer band fell twice as fast as the datasheet showed, which pushed the lower crossover and the woofer filter values in the wrong direction. The replacement used the modeled cone below the blend band and only the published shape relative to its midband above it.

The later performance study confirmed the mechanism and contradicted this learning's previous claim that the current `source_response` published-shape option already guarantees that split. Auditing the actual implementation showed that full multiplication remained. A project adapter preserved the bass model below 180 Hz, blended over 180–350 Hz and replaced its upper slope with the exact-variant published slope. The actual c01 hybrid/native difference at 38 Hz was only +0.022 dB, while the upper slope matched the intended graph closely. The adapter's minimum-phase correction is simulated data, not measured excess phase.

A third project met the same mechanism from the other side and found what it costs to skip the
check. The Beyma 12LX60V2's lumped cone with its published 2.1 mH inductance falls about 4 dB by
600 Hz while its datasheet response is flat to 800 Hz; the B&C 15PS100 behaves the same way. Two
candidates were first built with the woofer section taken from the lumped model alone, because no
digitized curve existed for those drivers, and their handover level was understated by 2 dB. Once
the two product-page graphs were digitized in-session and spliced in, the same parts met a
sensitivity objective and an impedance objective that the previous evaluation had judged not
jointly satisfiable.

## Why it mattered
The crossover between woofer and midrange was fitted against a woofer that did not exist; the fit compensated for a roll-off the real driver does not have.

A fourth project met the mechanism again and fixed it in the application rather than in project code.
The woofer section fell 6.13 dB from 200 to 800 Hz where the manufacturer's FRD falls 2.10 dB and the
lumped model alone falls 4.56 dB. `source_response`'s `published_shape` now takes a `mode`: the
default `multiply` is the old behaviour, and `replace` divides the model's own shape out first, so
below the blend band the box model owns the response and above it the box model owns only the level.
With `replace` the section follows the FRD within 0.7 dB from 300 to 1000 Hz, the residual being the
difference between the two curves' own blend-band reference levels.

## Advice
When a cone section combines a box model and a datasheet curve, consider which source owns each band's absolute level and slope. Preserve the box model in the bass; above the blend either replace its upper response with the calibrated published shape or remove only the duplicate slope before multiplying. Check the actual application version rather than assuming an option name implements the intended split. Compare the constructed upper slope with the datasheet and check the deep-bass difference on the actual candidate. Retain source provenance, blend assumptions and the distinction between inferred minimum phase and measured installed phase.

When no digitized curve exists for the chosen woofer, consider looking for one before concluding
the driver is not loud enough: a lumped model carrying a published inductance can understate the
handover band by 2 to 4 dB, which is the difference between meeting a sensitivity objective and
missing it. Manufacturers often publish the wideband curve as a bitmap on the product page rather
than in the datasheet PDF. Record the calibration anchors and state whether the graph's own
midband agrees with the published sensitivity; where it does not, use the shape only and let the
box model own the level.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 5
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, first correction
- `framework/simulations/source_response/README.md`, acoustic kind `lf_box`
- `framework/projects/forte-iii-performance-20260914/reference/simulation-audit.md`
- `framework/projects/forte-iii-performance-20260914/tools/hybrid_source.py`
- `framework/projects/forte-iii-performance-20260914/reference/audit/actual_c01_unity_hybrid.json`
- `framework/projects/forte-iii-r3/inventory/woofers/beyma_12lx60v2_8.json` and `bc_15ps100_8.json`, digitized curves with their anchors
- `framework/projects/forte-iii-r3/postmortem.md`, "What went right", items 4 and 5
