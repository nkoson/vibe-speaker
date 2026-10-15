---
id: trace-all-consumers-of-overridden-parameters
date: 2026-10-12
project: neat-petite-dayton-astra
phase: validation
confidence: low
applies_when: A physical parameter is supplied explicitly and appears to override another nominal model input
tags: [passive-radiator, loss, parameter-basis, replay]
---

## What went wrong
An explicit passive-radiator mass set the actual resonance, so the nominal tuning input was treated as inactive during a release cleanup. The same input still set the acoustic leakage resistance from the declared loss Q. Replacing it with the actual resonance therefore changed bass damping and the system cutoff even though the radiator mass and crossover were unchanged. Comparing the result with the expected small volume-only change exposed the unintended alteration before publication.

## What could have helped
Trace every consumer of an apparently overridden input before deleting or relabelling it. Separate an actual resonance from a loss-reference frequency, and preserve the latter when replaying the same physical prior. Compare expected and observed changes after a metadata cleanup; a larger-than-expected shift can indicate that an input still participates elsewhere in the equations. Record the reference used by a loss parameter rather than treating a plausible-looking nominal value as a harmless label.
