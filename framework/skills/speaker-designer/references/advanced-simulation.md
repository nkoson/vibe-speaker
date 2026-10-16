# Connect the richer models to the design

Use this procedure when geometry, listening position, unusual loading, heat or source uncertainty can change the design choice. The applications return results and numerical diagnostics. Interpretation, priorities and final selection belong to the model applying the speaker-design skills.

## Establish the prediction chain

Begin with the ordinary LF/source/network/exterior chain and a saved baseline. For each added mechanism, identify the input it replaces, the output it changes and the downstream consumers to rerun. Compare against the baseline in the common valid band. Keep the user's targets and physical drive convention unchanged during that comparison.

| Question | Application and connection | Evidence to read |
|---|---|---|
| Do the parts, air domains and braces fit? | `assembly_geometry`; share its metre-based assembly with cavity and exterior models | Volume refinement, solid intersections, transformed source normals, surface topology and fabrication records |
| Does cabinet shape alter radiation? | `exterior_bem`; prescribed surface velocities on a closed mesh; export a complex angular source | Mesh refinement, element/wavelength ratio, residual and condition number, source sphere normalization |
| Does an internal mode change the driver or outlet? | `cavity_modes` canonical terminal-volt cone/outlet/impedance outputs replace the lumped source in their supported band | Low-frequency agreement, blending ownership, no duplicate outlet or compliance, downstream crossover changes |
| Does a line, fold or chamber alter loading? | `distributed_loading`; segment the actual area/length/loss profile and place each motor and terminus | Loaded impedance, cone and outlet flow, per-motor current/excursion and coherent outlet sum |
| What does a specific room do? | `room_modal` for LF waves; `room_response` for coherent early reflections; `room_rays` for specular/diffuse energy | Source normalization, receivers, independent frequency/basis/order/ray refinements and declared wall properties |
| Do panel and air modes interact? | `coupled_cabinet`; structural/cavity modes and exterior acoustic load | Surface and modal refinement, joint stiffness/added-mass scenarios, coupled pressure and panel motion |
| Is the network more general than ladders? | `network_fit` uses `board_nodal`; actual nodes, transformers and mutual-inductance records | Numerical objective, all trial metrics, constraint margins, exact stock losses and power conservation |
| What changes with heating and excursion? | `electrothermal_network` for programme-weighted resistance feedback; `nonlinear_driver` for supplied nonlinear laws and optional port loss | Heat-balance residual, parameter-domain coverage, electrical/mechanical energy balance and spectra |
| Is the choice robust? | `system_scenarios` replays a dependency chain with correlated production draws and explicit model cases | Nominal recovery, same draws across candidates/cases, unresolved counts, conditional percentiles and observable differences |

These tools have different physical scope. Read their README contracts before constructing inputs. A well-conditioned numerical answer can still depend on uncertain material or driver parameters; compare those assumptions separately from numerical refinement.

## Source and geometry ownership

`source_response` distinguishes supplied complex phase, reconstructed minimum phase and an explicit zero-phase assumption. Its source contract records phase reference, baffle ownership and normalization. For a common-observer source, preserve the common reference rather than adding a second acoustic-depth delay. For a geometry-derived source containing cabinet diffraction, omit the separate baffle factor. Use referenced frequency bands and declared delays to preserve pressure normalization and phase during interpolation.

The assembly schema uses metres and rigid transforms. Existing cabinet/cavity/radiation inputs retain their documented coordinate conventions. Record the transform when adapting the shared geometry, and compare source locations, normals and volume totals after conversion. Shared IDs connect dimensions, materials, joints, source positions and machining records; diagrams alone do not establish those relationships.

## Compare mechanisms without counting them twice

For cavity sources, use the exported per-terminal-volt cone pressure, outlet pressure and loaded impedance together. A source blending study can retain lumped LF behavior and detailed cavity behavior higher up, with a continuous declared transition. Inspect complex pressure and impedance across that transition, not magnitude alone.

For room studies, keep the direct field, coherent reflected field and incoherent reflected energy separate. When combining early image paths with ray energy, specify a common arrival-time boundary using `max_arrival_ms` and `min_arrival_ms`; compare the time/order coverage. A modal/early-field blend calls for an explicit frequency overlap and an agreement plot. A weighted combination is a declared approximation, rather than additional independent sound to add twice.

For distributed loading, preserve each motor's electrical drive, acoustic incidence and outlet position. A line or rear horn can change both source impedance and the delayed radiated output. Compare with the lumped limit as segment lengths become short. Duct attenuation and effective sound speed describe supplied material scenarios; the app does not invent them from a brand name.

For panel radiation, distinguish the isolated-panel screening proxy from coupled exterior pressure. The coupled solver includes declared joints and attached masses; its rectangular modal basis remains a geometric approximation. Refine panel modes, cavity modes and surface panels separately. Test zero coupling as a diagnostic, then restore the actual coupling for the design comparison.

## Make a recommendation from the outputs

Numerical minima, margin signs, inferred cutoff frequencies and conservation residuals are observations. The evaluator weighs them against the brief, uncertainty and construction tradeoffs. A low fit cost does not by itself select a network, and a negative margin can describe a trade to explain rather than a software verdict about a speaker.

Keep source data separate from assumptions. Missing nonlinear curves, wall impedances or joint properties can be represented by clearly identified ranges with cited physical bounds. If a numerical experiment depends on an unsupported value, broaden or replace that assumption and report how the choice changes. Complete the design under defensible simulated scenarios without handing ordinary design decisions back to the builder.
