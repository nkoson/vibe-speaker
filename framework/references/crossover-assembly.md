---
id: crossover-assembly
applies_when: Realizing a passive circuit as physical boards, shared copper rails, component banks and serviceable assemblies
updated: 2026-10-21
---

# Crossover realization and assembly

Read [crossover design](crossover-design.md) for circuit physics and the documentation skill's [construction audit](../skills/speaker-documentation/references/construction-audit.md) for the drawing audit. The agent chooses construction from the evidence below; applications return connectivity, electrical quantities and geometry.

## Select the construction and optimize placement

Use one serviceable assembly per driver. Choose an available solderable prototyping board with an existing copper pattern, or an insulating plastic/wooden carrier with ordinary electrical wire and suitable stock terminals. Record the selected board or terminal part numbers, dimensions, connection pattern, conductor range and assembly operations. The platform should accommodate the chosen parts using routine cutting, drilling, lead forming, soldering or connector installation. Stock availability and practical assembly are inputs to the design.

A common rail means an electrical node shared by several parts. It can be an existing PCB track, a stocked terminal bridge, or an ordinary wire running from one component lead to the next. Evaluate the entire connection route regardless of whether it is called a rail, jumper, lead extension or harness.

Lay out the circuit in this order:

1. Extract the shared-node graph. Mark the series chains, parallel component groups, input/return and driver connections. Include each physical leaf of a component bank.
2. Sketch those groups before assigning final body coordinates. A parallel bank naturally fits between two straight node lines; a series chain fits end-to-end. Place a shunt branch near the node from which it leaves the main path. Orient component bodies and accessible lead ends to support these connections.
3. Place the actual body envelopes, restraints and hot-part clearances on the selected stock board/carrier. Keep neighboring coil axes distinct where practical. Let these constraints guide modest rearrangement of the electrical sketch.
4. Draw every wire and native lead. Review multiple plausible placements for the crowded connected groups. Compare total conductor length, number of straight runs, direction changes, crossings, solder/terminal joints and service access. The agent chooses the practical tradeoff from these quantities.
5. Trace every node and series path with the circuit beside the physical view. Inspect avoidable detours: a short electrical chain should remain visibly grouped, and a parallel branch should meet its shared nodes directly. Resolve body collisions and lead-reach problems by moving/orienting parts while keeping the circuit intact.
6. Walk through the complete build from the shopping list, including tools, wire preparation, insulation, restraint and installation. Finalize the drawings after this review, then recompute electrical losses and displacement.

The connection graph, routing measures and geometry checks are reported quantities. Quality judgement remains with the agent. Route simplicity is assessed together with magnetic separation, cooling and mechanical support; a low jumper count by itself is insufficient.

Manufacturer construction examples help select an appropriate platform. Mundorf describes surface soldering of crossover parts onto universal-board lands. Roth RE200-LF specifies 1 mm holes and 35 micrometre copper, so its lead fit and current paths require attention for large parts. Select an existing pattern that suits the components and their currents. [Mundorf catalogue, MConstruct Multiboard](https://www.audiohobby.eu/files/Mundorf_Hifi%2BStudio_catalog-2013.pdf), [Roth RE200-LF](https://www.roth-elektronik.com/product/RE200-LF)

## Preserve electrical identity

Total resistance in a resonant correction branch includes the resistor, winding and connections: `Rtotal = Radded + DCR + Rwire`. For a specified total, `Radded = Rtotal - DCR - Rwire`, when nonnegative. Capacitors add only when their endpoints really share the same two nodes. Preserve all physical leaves for current and heat accounting. Use the selected coil variant's DCR and dimensions together; an unpublished saturation current is not supplied by a core-material label. [Crossover design](crossover-design.md), [Jantzen coil guidance](https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/)

Model wire and copper paths by their actual length and section, using `R = rho L/A`, and contacts separately. A distributed shared rail carries the sum of the branch currents at each segment: use segment currents and `I²R`, not the current of one conveniently small branch. Include component leads, module links and driver cable. A resistance-only connection model does not automatically include lead inductance or copper temperature rise. Compare the realized network with the selected circuit and rerun dependent results when its losses change. Do not change selected electrical values merely to simplify the drawing.

Audit connectivity by collapsing only intended copper/links into circuit nodes and comparing every component endpoint against the authoritative netlist. Then inspect the physical view: graph equivalence alone does not detect an unshown copper bridge, a mounting screw across rails, inadequate lead reach or a wire drawn through a component body.

## Coil placement and nearby metal

Inductors interact through mutual inductance, `M = k sqrt(L1 L2)`. Separate their magnetic axes and use perpendicular axes for nearby coils where practical. Do not stack coils coaxially. There is no universal separation distance that makes all crossover coils independent: Coilcraft identifies orientation, distance, waveform, current and frequency as relevant. More than three coils cannot all have pairwise perpendicular axes. Record axis and body position for every coil, place unavoidable parallel coils farther apart, and evaluate declared coupling scenarios when that could affect the response. [Coilcraft FAQ, spacing and board layout](https://www.coilcraft.com/en-us/faq/)

Keep broad copper planes, metal straps, steel fixings and cabinet hardware away from unshielded coils unless their influence is accounted for. Route rails around the coil footprint rather than deliberately creating a conducting loop under it. Nearby conductors can alter losses and inductance; the magnitude depends on the particular geometry and frequency. Coilcraft's EMC discussion explains the mechanisms in an RF/switching context; its numerical layout heuristics are not universal audio-crossover acceptance limits. [Coilcraft EMC application note](https://www.coilcraft.com/ko-kr/resources/application-notes/fundamentals-of-electromagnetic-compliance/)

Use nonconductive coil restraints where possible. Never complete a conducting turn through a toroidal core and back around its outside with a bolt, bracket and chassis. Talema explicitly warns against the analogous closed centre-bolt/chassis loop in toroidal transformer mounting; the shorted-turn mechanism, rather than a transformer-specific power rating, is the applicable principle. [Talema open-style toroidal transformer installation](https://talema.com/products/toroidal-transformers-open-style/)

## Heat and component separation

Select power-resistor ratings using the actual installation, frequency-coincident dissipation and duty. A resistor's nameplate watts do not establish its surface temperature inside a cabinet. Keep hot resistors elevated above the PCB, with airflow around their bodies and clearance from film capacitors, adhesive, cable insulation and acoustic lining. Specify the chosen stand-off height and clearances as design dimensions; do not invent universal temperature-safe distances. Vishay explains the role of ambient air, mounting and terminal heat paths, while Ohmite's PC58 illustrates purpose-built PCB stand-offs. [Vishay thermal management](https://www.vishay.com/docs/30380/terminalderating.pdf), [Ohmite PC58](https://www.ohmite.com/res-pc58/)

A chassis-mount resistor may require a specified heatsink to achieve its headline rating; use its free-air rating if that heatsink is absent. Aluminum casing alone is not a heatsink installation. [Vishay RH/NH datasheet](https://www.vishay.com/docs/30201/rhnh.pdf)

Film-capacitor heating depends on solder exposure, lead length, nearby heat sources and mounting. Prepare and tin wire ends before joining heat-sensitive parts, use a tip capable of transferring heat promptly, and follow the selected component's soldering specification. Form leads with support at the body so bending force does not reach the termination. TDK's temperatures and times apply to its specified products and processes; they must not be silently transferred to another brand. [TDK film-capacitor mounting guidelines](https://www.tdk-electronics.tdk.com/download/187698/e7a5bd016c4f22e100e5e54231c7de6f/pdf-mountingguidelines.pdf)

## Mechanical support and service

Support heavy coils and large capacitors by their bodies, independently of solder joints. Use appropriately rated ties or clamps and compatible resilient pads; leave the solder lands accessible. Provide nearby board supports so tightening restraints or cabinet vibration does not bend a large unsupported board. Do not use component leads as mounting brackets. Mundorf describes resilient bonding and screwed clamps for larger capacitors; KEMET explains how board flex and relative body motion stress terminations. [Mundorf elastic bonding](https://www.mundorf.com/en/technologies/elastic-bonding), [KEMET mounting discussion](https://www.kemet.com/en/us/technical-resources/aar80-advantages.html)

Show complete restraint loops, holes, washers, screw lengths and access. Keep mounting holes and metal washers clear of live copper; remove copper around holes where needed. Nylon hardware still needs mechanical strength and temperature suitability. Do not pull ties across a hot resistor, damage winding insulation, or close a metal strap around a coil. Adhesive supplements a specified mechanical restraint when mass and service conditions require it; an unspecified blob of glue is not a fastening design.

Fix and strain-relieve the input and driver harness before it reaches solder joints. Route associated outgoing and return conductors together where practical to reduce loop area, keep them clear of cone travel and port mouths, and prevent rattles against panels. Identify both ends of every module link and driver lead. Provide removable, accessible modules with sufficient service allowance; never bury a joint behind a part that must be destroyed to inspect it.

## Assembly and inspection sequence

1. Verify the selected board/carrier and part dimensions; mark the component-side datum and assembly identity. Cut and drill the specified mounting and restraint features.
2. Prepare the selected connection system, including any specified breaks in existing prototype-board tracks. Check distinct nodes before fitting parts; after coils are installed, a legitimate winding can look like a short on a continuity buzzer.
3. Prepare the specified shared-node wires or stock bridges. Check every connection against the physical wiring map.
4. Install stand-offs, body pads and restraints, then the components. Preserve the shown coil axes and resistor elevation. Solder without tension on leads; trim tails and remove conductive debris.
5. Fit module links and strain-relieved harnesses. Verify component identity, endpoint labels, polarity and joint access against the master wiring view. Check driver-disconnected resistance against the circuit's expected low-resistance paths; do not demand isolation across a coil.
6. Install the boards with specified fasteners and lining clearances. Reconcile the parts list, conductor cut list, board volume and electrical model before releasing the construction package.

## Sources

Citations appear beside the construction mechanisms they support. The principal manufacturer publications are:

- Mundorf, [HiFi and Studio catalogue, MConstruct Multiboard](https://www.audiohobby.eu/files/Mundorf_Hifi%2BStudio_catalog-2013.pdf): universal prototype-board component assembly.
- Coilcraft, [FAQ: spacing and board layout](https://www.coilcraft.com/en-us/faq/): magnetic interaction and orientation.
- TDK, [Film capacitor mounting guidelines](https://www.tdk-electronics.tdk.com/download/187698/e7a5bd016c4f22e100e5e54231c7de6f/pdf-mountingguidelines.pdf): heat exposure and mechanical handling.
- Vishay, [Thermal management](https://www.vishay.com/docs/30380/terminalderating.pdf): mounting-dependent resistor heat removal.

All external sources accessed 2026-10-21. Manufacturer process examples support the stated mechanisms; project dimensions and mounting choices remain the designer's engineering decisions. Local solver contracts: [board_nodal](../simulations/board_nodal/README.md), [crossover_network](../simulations/crossover_network/README.md).


## Ordinary wiring and stock supports

Choose wire by conductor section, insulation temperature, termination compatibility and physical flexibility. LAPP publishes its OELFLEX HEAT180 SiF single-core silicone wire in1.5 mm2, including construction and temperature data. The insulation supports routing near crossover components while the layout maintains resistor clearance. Select the actual ordering variant and include its outside diameter in the placement review. [LAPP SiF](https://products.lappgroup.com/online-catalogue/power-and-control-cables/expanded-ambient-temperatures/silicone-single-cores/oelflex-heat-180-sif.html)

Straight soldered connections can use heat-shrink sleeves; a multiway junction can use a suitable self-fusing insulating wrap, with adjoining wires separately restrained. 3M's Scotch70 is a silicone self-fusing electrical tape rated for180 C service; follow its application instructions for overlap and tension. [3M Scotch70](https://www.3m.com/3M/en_US/p/d/v000060542/)

For elevated resistor bodies, Quick-Ohm lists stocked KER8-4.2X15 steatite sleeves,15 mm high with8 mm outside diameter. Its published package quantity is100; record fitted quantity and purchasing quantity separately. Their placement and lacing remain design choices. [Quick-Ohm KER8-4.2X15](https://www.quick-ohm.de/abstandsrohr-keramik-laenge-15mm/ker8-4.2x15)
