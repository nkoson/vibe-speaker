---
id: crossover-assembly
applies_when: Realizing a passive circuit as physical boards, wiring, component banks and serviceable assemblies
updated: 2026-10-15
---

# Crossover realization and assembly

Read [crossover design](crossover-design.md) for the electrical network and the documentation skill's [construction audit](../skills/speaker-documentation/references/construction-audit.md) for drawings. This reference distinguishes modeled electrical effects from construction practice.

## Electrical identity survives assembly

**Circuit physics.** Total resistance in a resonant correction branch includes the inductor winding, resistor and wiring. If a specified total is `Rtotal`, the added resistor is `Rtotal - DCR - Rwire`, provided that is nonnegative. Retaining the same nominal resistor while substituting a different coil changes damping. A nominal capacitor bank is a sum only when its elements are genuinely in parallel; preserve actual nodes and physical leaves for stress analysis. These relationships follow from series impedance and parallel admittance; see [crossover design](crossover-design.md).

**Manufacturer evidence.** Inductance and wire gauge alone do not determine DCR; winding geometry also matters. Use the selected variant's resistance and dimensions together. A vendor's unpublished saturation current stays unknown and is not supplied by an air-core/iron-core label. [Jantzen coil guidance](https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/)

**Design application.** Recompute the realized circuit after substitutions and test tolerances, current and dissipation with the actual mounting conditions. Match the design's numerical values and quantities to purchasable parts, including banks, wire and terminal resistance. Select a robust realization in simulation; routine measurement requests are not a substitute for this work.

## Physical layout is a separate engineering problem

**Assembly practice.** Provide mechanical restraint, an insulating support and installation clearance for every part. Point-to-point wiring and a copper board are alternative implementations of the same circuit; choose between them using actual lead reach, current, mass and service access.

**Engineering judgement.** Choose board construction to suit lead size, part mass, temperature, access and service. Heavy coils need mechanical support independent of solder joints. Locate hot resistors with adequate clearance from vulnerable bodies and supports. Use actual material/component temperature ratings; a nominal wattage does not determine surface temperature or enclosed operating life. Include the complete restraint and installation sequence in the layout.

**Coupled-inductor physics.** Two coils can have mutual inductance `M = k sqrt(L1 L2)`, adding `j omega M` cross terms whose signs depend on orientation. Distance and orthogonal axes are practical coupling reductions, not a universal guarantee. The present ladder and board solvers have no mutual-inductance element. Keep coil geometry explicit, choose separation conservatively, and identify a coupled-network extension when the design decision depends on this effect. Do not simulate zero coupling and claim the layout proved it.

**Wiring physics.** Lead and contact resistance change loaded transfer and heat. Longer runs can also add inductance; a resistance-only board model does not include that effect automatically. Compare candidate wire lengths/resistances and preserve topology, polarity and terminal identity in each assembly drawing. A separate external enclosure can buy room and access while adding wiring and a physical enclosure to the bill of materials.

## Document the implementation

Generate circuit, parts list and physical wiring from the same selected realization. Check copper islands, retained bridges, mounting holes, component lead reach and driver polarity independently of circuit solving. A legible master wiring view remains necessary for a build-by-picture request. Numerical equivalence of ideal ladders and the board verifies modeled wiring, not every unmodeled physical effect.

## Sources

- Jantzen Audio, [Coil types and where to use them](https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/), accessed 2026-10-15. Per-variant DCR and limits of published ratings; vendor sound-quality hierarchy is not adopted.
- [Crossover design](crossover-design.md), sections 11–13. Compensation, winding resistance and physical-bank power accounting, with their engineering sources.
- Local implementation: [board_nodal](../simulations/board_nodal/README.md) and [crossover_network](../simulations/crossover_network/README.md). Current uncoupled electrical model contracts.
