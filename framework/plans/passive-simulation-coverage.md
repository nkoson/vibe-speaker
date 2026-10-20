# Passive simulation coverage

Implement on `codex/passive-simulation-coverage`, with reviewable commits after
each stage. Active DSP synthesis and hardware configuration are outside scope.
Simulations report observables, numerical objective values and signed margins;
the design agent interprets them using the engineering references.

1. Independent analytical/reference-export corpus, comparison metrics and provenance.
2. Measured polar ingestion, explicit phase/voltage/distance conventions, response
   preparation (windowed impulses, complex merging and curve arithmetic).
3. Lossy voice-coil impedance and suspension creep, measured parameter identification,
   polygonal angular diffraction and additional enclosure networks.
4. Passive-network load diagnostics and programme dissipation, spatial optimization
   objectives, and linear impulse/step/group-delay analysis.
5. Independent regression cases, complete example/test replay, reference and contract
   reconciliation.

Every new model needs a repository engineering reference citing independent primary
literature or official mathematical documentation. Neither discussion forums nor
unattributed software behavior is an engineering source. Export fixtures distinguish
analytical values, independently computed values and measurements. None establishes
universal empirical accuracy.

## Progress

- Branch created from `61a2f31`; working tree was clean.
- Existing numerical tests and shared implementations inspected.
