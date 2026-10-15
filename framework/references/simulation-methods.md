---
id: simulation-methods
applies_when: Selecting and connecting geometry, boundary, modal, distributed, nonlinear and uncertainty simulations
updated: 2026-10-15
---

# Numerical methods and physical contracts

The applications evaluate specified equations and return observables. Numerical domain errors describe inputs the equations cannot use; residuals, margin signs and numerical objective minima describe the computation. The design agent interprets them against the brief.

## Source and interpolation contract

Complex pressure is a transfer at an explicit voltage, distance, propagation reference and baffle basis. Magnitude-only information supports a declared phase assumption; it does not supply measured phase. Separating a known delay `exp(-j omega tau)` from the residual before interpolation preserves that delay. Interpolating magnitude and unwrapped residual phase avoids Cartesian chord attenuation, but sparse samples still cannot identify an unknown aliased delay uniquely. Referenced curves report their available band and extrapolation policy.

For an acoustic field on a reference sphere, propagation removal uses the same sign convention as the solver. The exterior app uses `e^(j omega t)` and outgoing `exp(-jkr)`. Its angular source includes the modeled cabinet field, so multiplying another cabinet baffle correction would duplicate it.

## Geometry and acoustic boundaries

`assembly_geometry` separates solids, air and porous regions. Mesh topology, rigid transforms and volume integration are geometry calculations. A surface tag describes where a material is applied; the material's frequency-dependent behavior remains an independent physical input.

`exterior_bem` uses constant-panel single-layer Neumann collocation. The normal-derivative jump and free-space Helmholtz kernel define the operator; the current centroid quadrature is low order. Compare mesh refinement and condition numbers as well as the solved residual. Boundary integral formulations and the roles of single/double-layer operators are documented by the [Bempp handbook](https://bempp.com/handbook/api/boundary_operators.html). The local implementation is independent and uses NumPy, not Bempp.

`room_modal` uses orthonormal rectangular cosine functions with the full wall-admittance overlap matrix. The weak Helmholtz boundary term is `j omega rho Y`, giving complex modal coupling rather than assuming independently damped rigid-room modes. Finite-aperture electrodynamic sources add their acoustic admittance, allowing room pressure to change current and motion. See the [pressure-acoustics equations](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.164.html) for the continuum problem; the local Galerkin discretization is verified through limiting cases.

`room_response` resolves coherent early image paths; `room_rays` estimates reflected energy in triangulated geometry. Their time partition is explicit. A frequency blend with a modal solution reports its overlap discrepancy and uses declared power weights, not a second independent copy of the direct field. The [room simulation documentation](https://pyroomacoustics.readthedocs.io/en/stable/pyroomacoustics.room.html) distinguishes image paths and later ray/scattering effects; coefficients and discretizations remain model-specific.

## Coupled cabinet and distributed loading

In `coupled_cabinet`, pressure exerts modal panel forces and panel normal acceleration drives the acoustic field. Exterior pressure also loads the panel model when feedback is enabled. This follows the reciprocal dynamic and kinematic interface conditions described in [acoustic–structure interaction](https://www.comsol.com/support/learning-center/course/modeling-speaker-drivers-in-comsol-multiphysics-202/supplement-a-equations-76561). Rectangular sine/cosine bases and low-order boundary panels approximate the geometry; joint springs and attached masses are explicit parameters. The result is predicted exterior pressure, distinct from the isolated panel-volume-velocity screening proxy.

`distributed_loading` connects plane-wave transmission sections, acoustic compliance, radiation impedance and motor equivalents. A uniform duct uses `Zc=rho c/S`, propagation constant `gamma`, and hyperbolic two-port functions. Tapered lines and folded horns are piecewise sections; motor position and outlet propagation remain explicit. Segment refinement resolves longitudinal variation but does not create transverse modes. Transmission-line and horn continuum assumptions are also described in [alternative loadings](alternative-loadings.md) and [horn and waveguide design](horn-and-waveguide-design.md).

## Electrical, thermal and nonlinear state

`board_nodal` incorporates a coupled branch impedance matrix. Mutual terms are `j omega k sqrt(L1 L2)`; finite transformers specify winding inductances, resistance and coupling. The inductance matrix's positive definiteness is an input-domain property. Network fitting evaluates the same solver, records every trial and preserves exact stock attributes. The numerical search does not select the speaker.

`electrothermal_network` integrates `I² Re` under a normalized programme spectrum and iterates the resistance/temperature relationship. `nonlinear_driver` uses a flux/current law, inductance coenergy force, position-dependent motor/restoring terms and two thermal bodies. Its optional port model has linear and quadratic pressure losses. The need for separate nonlinear motor, suspension and inductance descriptions is supported by [Klippel's large-signal discussion](https://www.klippel.de/know-how/measurements/nonlinear-distortion/separated-loudspeaker-distortion.html). No nonlinear curve is inferred from a nominal power label.

## Evidence and uncertainty

The reusable [benchmark catalogue](../benchmarks/catalog.json) connects generated fixtures to analytical identities and integration tests. `framework/tools/run_benchmarks.py` emits errors and residuals without design ratings. Those cases establish numerical behavior for their conditions; they are not universal empirical error bars.

`system_scenarios` shares correlated production draws across explicit model alternatives and replays dependencies. Its percentiles are conditional on resolved draws, with unresolved counts alongside them. Physical model scenarios and numerical refinement have separate meanings, and arbitrary scenario frequencies are not manufacturing yields. The agent makes the robustness judgement from the observable changes and the user's priorities.

## Sources

- Bempp authors, [Boundary Operators](https://bempp.com/handbook/api/boundary_operators.html), accessed 2026-10-15. Helmholtz boundary integral operators; not the local quadrature implementation.
- COMSOL, [Pressure Acoustics, Frequency Domain Equations](https://doc.comsol.com/6.3/doc/com.comsol.help.aco/aco_ug_pressure.05.164.html), accessed 2026-10-15. Continuum acoustic equations and conventions.
- COMSOL, [Supplement A: Equations](https://www.comsol.com/support/learning-center/course/modeling-speaker-drivers-in-comsol-multiphysics-202/supplement-a-equations-76561), accessed 2026-10-15. Dynamic/kinematic acoustic–structure interface conditions.
- Pyroomacoustics authors, [Room Simulation](https://pyroomacoustics.readthedocs.io/en/stable/pyroomacoustics.room.html), accessed 2026-10-15. Image and ray/scattering method scope.
- Klippel GmbH, [Separated Loudspeaker Distortion](https://www.klippel.de/know-how/measurements/nonlinear-distortion/separated-loudspeaker-distortion.html), accessed 2026-10-15. Large-signal parameter mechanisms; no endorsement of the local polynomial inputs or a universal distortion threshold.
