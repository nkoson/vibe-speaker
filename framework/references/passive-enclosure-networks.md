---
id: passive-enclosure-networks
applies_when: Simulating multiple chambers, double-tuned reflex or passive-radiator bandpass systems
updated: 2026-10-20
---

# Passive enclosure networks

Each chamber has acoustic compliance `Ca=V/(rho c²)`. A short vent contributes
`Za=Ra+s rho Leff/S`; a passive diaphragm contributes
`Za=(Rm+sM+1/(sCm))/Sd²`. For n identical parallel outlets, divide this
impedance by n; individual velocity is total flow divided by n*Sd.
Effective port length already includes end corrections; do not add them twice.

A chamber's absorption resistance is in series with its compliance. Leakage is
a separate shunt resistance. Optional Qa specifies `Ra=1/(omega_ref Ca Qa)`;
Ql specifies `Rl=Ql/(omega_ref Ca)`. The reference frequency is supplied, not
silently changed when the topology changes. These loss parameters need measurement
or uncertainty scenarios; geometry alone does not identify them.

For a motor incidence vector b (front +1, rear -1), its acoustic Norton source is
`q0=Sd Bl V/(Ze Zm+Bl²)` with admittance `Ya=Sd²/(Zm+Bl²/Ze)`.
Add `Ya b b^T` to the chamber matrix and `q0 b` to the source vector. The
solved flow is `q=q0-Ya b^T p`. This is an algebraic elimination of the
electromechanical equations, not a new empirical model.

Named presets expand to explicit networks: direct radiator with one sealed/vented/PR
chamber, reflex chambers linked by a port, and a bandpass motor between chambers
whose output is a vent or passive diaphragm. Optional rear and coupling ports cover
parallel and series-tuned bandpass layouts. Presets specify topology only.

The simulator outputs each motor's current, impedance, displacement, acceleration
and reaction-force magnitude, plus individual outlet flows and coherent propagated
pressure. Reaction force uses the supplied moving mass; it is not cabinet vibration.
Frequency-dependent inductance/creep are supported in the same linear solve.

This model does not include pipe standing waves, acoustic mutual radiation,
nonlinear compression or aerodynamic noise. Use distributed loading and cavity
models for appropriate wave effects; agreement with a lumped limit is verification,
not a reason to extend that limit.

## Sources

- W. M. Leach Jr., [Georgia Tech audio engineering](https://leachlegacy.ece.gatech.edu/ece4445/index.html),
  author-published loudspeaker equivalent circuits and SPICE examples.
- R. H. Small, “Direct-Radiator Loudspeaker System Analysis,” *JAES* 20, 383–395,
  1972; “Vented-Box Loudspeaker Systems,” *JAES*, 1973. Constitutive laws and loss parameters.
- J. Candy and C. Futtrup, [Box Theory](https://speakerbench.com/doc/box_theory.html).
  Distinction between compliance/absorption, port mass/loss and distributed wave models.
- E. R. Geddes, “Introduction to Bandpass Loudspeaker Enclosures,” *JAES* 37(5),
  1989. Background topology reference; no unpublished alignment table is inferred.
