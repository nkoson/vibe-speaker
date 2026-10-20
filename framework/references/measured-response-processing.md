---
id: measured-response-processing
applies_when: Importing polar data, processing impulses or merging complex acoustic responses
updated: 2026-10-20
---

# Measured response preparation

## Canonical source

Pressure is an RMS complex transfer per driver-terminal volt, normalized to 1 m.
For a spherical outgoing field `p(r)=A exp(-jkr)/r`, normalization multiplies pressure
by r/V and removes only the declared propagation delay. Acoustic position must not
be encoded both in the imported phase and in the subsequent propagation calculation.
`polar_import` can remove absolute propagation, or the remaining path difference
after a common reference delay was removed. Acquisition latency is separate.

Two-column magnitudes cannot establish acoustic timing. Minimum-phase reconstruction
and assumed zero phase must remain labelled assumptions. File hashes, common data
band, gate and angular coverage accompany imported sources. Missing directions are
not automatically zero or mirrored.

The H and V inputs are great circles around the forward +y direction. For diagonal
directions this implementation blends the complex H/V values at the same polar
angle with weights proportional to squared lateral/vertical direction components.
This is a declared interpolation assumption, not a unique reconstruction theorem.
It preserves both measured planes and signed cancellations. Axial symmetry and
mirror symmetry require explicit caller declarations. Direct full-grid input is
preferable when independently measured diagonal data is available.

## Windowing and linear transforms

Multiplication by a time window convolves the frequency response with the window's
transform. Zero padding adds frequency samples, not information or low-frequency
resolution. Record window lengths and phase reference. A real impulse uses a
Hermitian spectrum. For sampled convolution coefficients, `H=rfft(h)`; a continuous
impulse-density convention instead introduces the sampling interval. Do not mix them.

Group delay is `-d arg(H)/d omega`. Phase derivatives near response zeros are
ill-conditioned and should be masked using an explicitly reported threshold.
Minimum/excess phase depends on the magnitude extension outside the measured band.

## Near/far merging

For a circular piston of radius a, low-frequency near-surface pressure scales to
half-space far-field pressure at r approximately by `a/(2r)` (Keele). This assumes
uniform piston velocity, small ka, a near microphone and an appropriate baffle.
Scale each cone/outlet separately and sum complex pressure, with common drive and
timing. Apply finite-cabinet corrections exactly once. Overlap matching is an explicit
calibration estimate; report the fitted gain/delay and residual instead of hiding it.

## Compact-source flow convention

With `exp(j omega t)` time dependence, a compact full-space volume velocity Q
produces `p(r)=j omega rho Q exp(-jkr)/(4 pi r)`. An infinite rigid-plane image
doubles forward pressure for the same Q, replacing 4 pi with 2 pi. This is the
low-ka far-field limit of a baffled piston, not a finite-cabinet correction.
The framework's explicit pressure/flow conversions retain or remove propagation
according to the declared phase reference. A source calibrated acoustically may
be converted to an equivalent room excitation, but its inferred Q cannot certify
actual diaphragm displacement or port speed. Gain, polarity and added delay apply
equally to file-referenced and inline curves.

When a published magnitude was acquired on a known finite fixture, remove its
modeled magnitude before extracting the driver's relative shape, then apply the
intended cabinet correction once. The two geometries and observation distances
need not match. With magnitude-only data this remains a minimum-phase reconstruction,
not recovery of measured timing. An unknown fixture must remain a named hypothesis;
simply assuming an infinite baffle does not establish its identity. The relative
shape normalization also means that this operation cannot identify absolute level.

A multiplicative correction may be withdrawn over a declared band using
`low * exp(w * (log(abs(high/low)) + j unwrap(arg(high/low))))`, with a stated
log-frequency weight w. This is geometric interpolation of magnitude with a
continuous relative-phase branch. It preserves both endpoint responses but is
not the coherent sum of two sources. Nulls make its logarithm singular. The
choice between this interpolation and linear complex-pressure merging is a
modeling assumption, not an accuracy improvement inferred by the processor.

## Sources

- COMSOL, [Acoustics Module User's Guide, Monopole Point Source](https://doc.comsol.com/5.4/doc/com.comsol.help.aco/AcousticsModuleUsersGuide.pdf),
  p. 112, flow-source strength `S=j omega rho Q/(4 pi)`.
- COMSOL, [Baffled Piston Radiation](https://doc.comsol.com/6.3/doc/com.comsol.help.models.aco.baffled_piston_radiation/baffled_piston_radiation.html),
  Rayleigh integral and baffled-piston far-field comparison.
- ARTA Labs, [Application Note 4: Free-field measurements](https://artalabs.hr/AppNotes/AN4-FreeField-Rev03eng.pdf),
  finite-baffle and observation-distance corrections when merging response data.

- D. B. Keele Jr., “Low-Frequency Loudspeaker Assessment by Nearfield Sound-Pressure
  Measurement,” *JAES*, April 1974; [author's publication archive](https://dbkeele.com/technical-papers-2/).
  Near-field/far-field scaling and its piston assumptions.
- NumPy developers, [Discrete Fourier Transform](https://numpy.org/doc/stable/reference/routines.fft.html).
  Transform signs, normalization and real/Hermitian spectra.
- SciPy developers, [window functions](https://docs.scipy.org/doc/scipy/reference/signal.windows.html)
  and [group delay](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.group_delay.html).
  Implemented window definitions and phase differentiation.
- J. O. Smith III, *Introduction to Digital Filters with Audio Applications*, 2007,
  [Numerical Computation of Group Delay](https://ccrma.stanford.edu/~jos/fp/Numerical_Computation_Group_Delay.html).
