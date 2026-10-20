---
id: passive-network-diagnostics
applies_when: Interpreting amplifier load, component dissipation and spatial network-fitting targets
updated: 2026-10-20
---

# Passive network diagnostics and objectives

## Reactive load

For ideal class-B operation, write output voltage `Vrail sin(theta)` and positive
device current `Vrail/|Z| sin(theta-phi)`. Instantaneous device dissipation is
`Vrail²/|Z| (1-sin(theta)) sin(theta-phi)` during its conducting half-cycle.
For a resistor its maximum is `Vrail²/(4R)`. Equating maxima gives
`EPDR=|Z|/[4 max_theta((1-sin(theta))*max(sin(theta-phi),0))]`.
The implementation finds this mathematical maximum; it does not select an amplifier.
EPDR equals R for a resistor and is symmetric for conjugate loads. It describes
this ideal output-stage assumption only, not class-D heat or transistor safe area.

The formula above is an explicit derivation from instantaneous voltage times
current. Benjamin supplies the reactive-load analysis context; Howard introduces
the equivalent-resistance interpretation. The local implementation is independent.

## Programme dissipation

Ideal transformers use the lossless constraints `Vp=n Vs`, `Is=-n Ip`.
Finite transformers instead use a positive-definite coupled winding inductance
matrix. Inductor shunt R/C parasitics are ordinary explicit passive branches.
Neither ideal constraints nor parasitics infer physical coil layout or core saturation.

Normalize voltage PSD S(f) so its frequency integral is one. If a network run uses
reference voltage V0, the programme mean component power is
`(Vrms/V0)² integral(Pcomponent(f) S(f) df)`. Voltage/current RMS follow the same
integration of squared magnitudes. White and pink PSDs are 1 and 1/f before
normalization. Custom PSD represents other spectra. A spectrum alone does not
determine the peak waveform or output crest factor; a supplied crest is a scenario.

## Spatial objectives

A passive network can be evaluated against on-axis response, listening window,
early reflections, sound power and predicted in-room curves simultaneously. Their
definitions are in the target-response reference. These are energy averages across
directions, while summation of drivers at each direction is coherent.

Caller-supplied target curves, bands, weights, shape-only offsets and electrical
constraints define the numerical problem. Store each objective contribution and
signed constraint margin. Optimizer termination and a numerical extremum are not
speaker-quality decisions. A preference regression can be a caller-requested
mathematical objective, but its score does not certify a design or replace constraints.

## Sources

- E. Benjamin, “Audio Power Amplifiers for Loudspeaker Loads,” *JAES* 42(9),
  670–683, September 1994, [publisher record](https://aes.org/publications/elibrary/elibrary-page/?id=6931).
  Reactive-load output-stage context; publisher abstract inspected, not a claimed
  reproduction of inaccessible implementation details.
- K. Howard, [Heavy Load: How Loudspeakers Torture Amplifiers](https://www.stereophile.com/content/heavy-load-how-loudspeakers-torture-amplifiers),
  July 2007. Author's load-line analysis and equivalent peak dissipation resistance.
- S. E. Olive et al., [US8311232B2](https://patents.google.com/patent/US8311232B2):
  measured-response preference predictors. These coefficients do not establish the
  accuracy of simulated response inputs.
- W. M. Leach Jr., [Georgia Tech Audio Engineering](https://leachlegacy.ece.gatech.edu/ece4445/index.html),
  passive circuit and loudspeaker load analysis.
- Ngspice authors, [User's Manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf),
  passive RLC devices and controlled-source network equations. The local ideal
  transformer stamp is derived directly from the two constraints above.
