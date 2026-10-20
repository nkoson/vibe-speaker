---
id: passive-analysis
applies_when: Verifying passive simulations, importing complex data and interpreting model comparisons
updated: 2026-10-20
---

# Passive analysis and independent verification

## Evidence classes

An analytical identity verifies a mathematical limit. An independently implemented
solver comparison checks more of the numerical implementation. A measurement tests
the physical model under the measured conditions. Keep these classes separate.
An algebraic residual does not bound discretization error or empirical error.

The reference corpus in `framework/benchmarks/reference_exports` is generated without
importing the simulation implementation. Its elementary circuits use independently
specified rational transfer functions evaluated by SciPy's continuous-time system
analysis. The corpus also includes explicit analytical values. These are simulated
references, not measured data. Its manifest records equations, units, conditions and
file hashes. Changing production code must not automatically regenerate reference
values. An external result can be added only with its source, version, conditions and
evidence class retained.

## Conventions and comparison

Use complex RMS phasors with time convention `exp(+j omega t)`. An outgoing delay is
`exp(-j omega tau)`. Declare terminal voltage, pressure reference distance, radiation
space, acoustic timing reference and whether cabinet diffraction is already included.
Compare complex impedance or transfer on their common frequency domain. Do not extend
the reference silently. A pure known delay can be removed before interpolation and
restored afterwards; unknown undersampled phase cannot be recovered.

Report log-frequency-weighted RMS and maximum magnitude differences, wrapped phase
differences away from zeros, and normalized complex differences with an explicit
denominator floor. At a null the absolute complex difference is more informative than
a divergent relative percentage. A tolerance is supplied by a test author or design
agent; the simulation does not invent a loudspeaker acceptance threshold.

## Elementary reference equations

For a resistance R and shunt capacitance C, `H(s)=1/(1+sRC)`. For a series R-L branch
feeding C, `H(s)=1/(1+sRC+s²LC)`. The continuous-time impulse of the first circuit is
`exp(-t/RC)/(RC)` for nonnegative t, and group delay is
`RC/(1+(omega RC)²)`. These independently exercise phase, magnitude, frequency units
and time reconstruction.

For a moving-coil driver with mechanical impedance Zm and blocked electrical
impedance Ze, `Zin=Ze+Bl²/Zm`, `v=Bl V/(Ze Zm+Bl²)`. A sealed ideal volume contributes
`Sd² rho c²/(s Vb)` to Zm. These follow the electromechanical equivalent circuits
described by Small and Leach. A numerical network residual is a separate observable.

## Sources

- W. M. Leach Jr., Georgia Tech, [Audio Engineering course](https://leachlegacy.ece.gatech.edu/ece4445/index.html):
  author-provided infinite-baffle, closed-box and vented-box SPICE examples and circuit analysis.
- R. H. Small, “Direct-Radiator Loudspeaker System Analysis,” *JAES* 20, 383–395, 1972.
  Parameter/equivalent-circuit foundation; see the established enclosure references.
- SciPy developers, [freqresp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqresp.html)
  and [group_delay](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.group_delay.html):
  independent rational-system evaluation and the phase-derivative definition.
- NumPy developers, [DFT conventions](https://numpy.org/doc/stable/reference/routines.fft.html):
  transform signs and normalization, not an empirical acoustical validation.
