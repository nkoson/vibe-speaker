# Select the model for the architecture

Use this map before selecting drivers and loading. It describes the current applications, not the possible performance of an architecture. A missing coupling is not proof that the requested speaker cannot work. Use the available models with explicit source ownership and compare plausible assumptions when a missing effect can change selection.

| Speaker family | Available prediction | Coupling to account for in the design |
|---|---|---|
| Sealed, reflex, passive radiator | Lumped LF, network, exterior sum, LF uncertainty and linear displacement/outlet limits | Cavity modes, actual outlet location, frequency-dependent losses and physical clearances |
| Bandpass, isobaric, aperiodic | Equivalent circuits for the specified chambers and loss scenarios | Per-motor current/excursion, duct modes and material-to-resistance uncertainty |
| Cone/dome multiway and 2.5-way | Separate section sources, filters and geometry | Classify the actual passbands; front-panel symmetry alone does not establish a same-band MTM. Shared-box loading and wiring need a consistent equivalent. |
| Horn/compression driver | Horn sizing, infinite-horn loading and analytical directivity | Finite horn-mouth effects, throat/phase-plug geometry and source delay are separate from nominal coverage. |
| Rear-loaded full-range horn | Horn screens and source/network models | Account for direct cone and delayed mouth contributions coherently. A horn length alone is not an absolute system response. A single driver can still need equalization. |
| Transmission line / mass-loaded quarter-wave tube | Length and approximate mode arithmetic | The line calculator does not provide complex cone/terminus output or loaded impedance. Preserve driver offsets, folds, stuffing zones and terminus mass when choosing a supported response model. |
| Open baffle / U/H frame / passive cardioid | Dipole cancellation and displacement screens | Rear radiation has sign as well as level. A shadowed monopole is not a dipole; frame modes and rear resistance affect loading. |
| Coaxial | Separate point sections on a common axis | Coincident axes do not establish coincident acoustic centres. Cone/waveguide interaction and separate LF/HF phase still matter. |
| Arrays and large panels | Point-section summation, spacing and distance screens | Represent physical radiators and electrical groups explicitly. Evaluate actual distance sweeps rather than assigning one universal 3 dB or 6 dB spreading law. |

Read the corresponding application contract before use: `lf_box`, `cavity_modes`, `horn_design`, `horn_loading`, `transmission_line`, `open_baffle`, `whole_speaker` and `room_response` under `framework/simulations/`.

## Preserve the physical chain

- Keep one geometry record for dimensions, source positions, surface normals, chambers, braces, treatments and wiring. Translate that record into each app's documented datum; compare transformed positions, air volumes and clearances independently.
- Separate solid displacement, structural damping and porous acoustic treatment. A shaded drawing region is not necessarily an airtight solid. Unequal dimensions spread some resonances but do not establish adequate damping.
- Carry significant cavity effects into the source/impedance representation used for final scoring, with a clear replacement/blending convention. Do not apply a second compliance, baffle factor or outlet contribution already present in the source.
- For non-ladder circuits, use `board_nodal` to evaluate actual connections and feed its load transfers into the exterior sum. Its general netlist capability does not imply that `crossover_fit` searches general networks or that mutual inductance is modeled.
- Use room and seat scenarios to compare placement and directivity. Keep free-field response, the angularly weighted predicted-in-room curve and actual-position room pressure distinct.

## Inspect the input and reporting contracts

Source provenance needs an explicit phase basis. A magnitude-only input does not become measured complex data because an importer supplies zero phase; identify reconstructed or assumed phase and apply acoustic delay only once. Inspect the source grid before complex interpolation, especially for long delays. All referenced curves should cover the consuming band; held endpoints are not additional evidence.

For fitted networks, compare the selected network's own result with its reported summary. The fitter selects by combined cost, while some summary statistics can summarize a different attempt. Retain and compare the incumbent outside the fitter when a call budget is exhausted; validate realized stock and required protection separately from weighted penalties.

For orthotropic panels, distinguish the actual orientation-dependent modes from the app's isotropic restraint comparison. Do not call the latter a bound unless it brackets the relevant calculation. Check mode coverage, pressure-grid coverage and mesh refinement separately. The current volume-velocity panel proxy does not provide absolute radiated sound pressure.

These checks support a definite design choice under the model's assumptions. They do not transfer design responsibility to the builder or establish new acceptance thresholds.
