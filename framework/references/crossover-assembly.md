---
id: crossover-assembly
applies_when: Realizing a passive circuit as physical boards, shared copper rails, component banks and serviceable assemblies
updated: 2026-10-21
---

# Crossover realization and assembly

Read [crossover design](crossover-design.md) for circuit physics and the documentation skill's [construction audit](../skills/speaker-documentation/references/construction-audit.md) for the drawing audit. The agent chooses construction from the evidence below; applications return connectivity, electrical quantities and geometry.

## Default construction: prototype PCB with shared rails

Unless the user explicitly requests another construction method, build the passive crossover on soldered prototyping circuit boards. Use the board's common copper rails, or join its isolated lands into clearly identified common-node rails, so component leads connect directly to their shared nodes with as few insulated jumpers as practical. Wooden planks, solderless breadboards and individual flying-wire junctions are not the default. Cabinet plywood can support PCB stand-offs; it is not the circuit board.

Choose a board that fits the actual bodies, lead diameters, copper requirements and mechanical restraints. Mundorf's manufacturer catalogue documents universal boards with approximately 10 by 10 mm isolated copper areas, components attached on the copper side, and leads soldered directly to the lands. It also lists copper reinforcement strips, including 1 by 5 mm. This is one suitable construction family, not a mandatory brand. Ordinary fine-pitch stripboard may need more adaptation: Roth RE200-LF, for example, has 1 mm holes, 35 micrometre copper and no plated-through holes. Do not force a large inductor lead into an undersized hole or credit an unreinforced thin track with an arbitrary current rating. [Mundorf catalogue, MConstruct Multiboard](https://www.audiohobby.eu/files/Mundorf_Hifi%2BStudio_catalog-2013.pdf), [Roth RE200-LF](https://www.roth-elektronik.com/product/RE200-LF)

Draw the actual copper connectivity. A row of separate pads becomes a rail only through specified retained copper, solder bridges or added conductor. Identify every isolation cut, retained bridge, rail splice, crossover link and external terminal. If stock artwork is not dimensioned, give a registration/receiving procedure and machine isolation from the selected layout datum; never invent a manufacturer's grid pitch. Include unconnected copper islands in the review because a strip laid across them can unintentionally join another node. Inspect both sides where copper is present on both faces.

Place shared-node rails first, then fit the components and restraints around them. Use several modules when that gives accessible joints and adequate cooling. Minimize jumpers after satisfying current, thermal, magnetic and mechanical requirements. Report separate counts for native component leads, added copper rail pieces, solder bridges, insulated board jumpers and inter-board/harness conductors. Renaming a lead extension a rail does not eliminate a connection.

## Preserve electrical identity

Total resistance in a resonant correction branch includes the resistor, winding and connections: `Rtotal = Radded + DCR + Rwire`. For a specified total, `Radded = Rtotal - DCR - Rwire`, when nonnegative. Capacitors add only when their endpoints really share the same two nodes. Preserve all physical leaves for current and heat accounting. Use the selected coil variant's DCR and dimensions together; an unpublished saturation current is not supplied by a core-material label. [Crossover design](crossover-design.md), [Jantzen coil guidance](https://jantzen-audio.com/faq/coil-types-and-where-to-use-them/)

Model copper paths by their actual length and section, using `R = rho L/A`, and contacts separately. A distributed shared rail carries the sum of the branch currents at each segment: use segment currents and `I²R`, not the current of one conveniently small branch. Include component leads, module links and driver cable. A resistance-only connection model does not automatically include lead inductance or copper temperature rise. Compare the realized network with the selected circuit and rerun dependent results when its losses change. Do not change selected electrical values merely to simplify the drawing.

Audit connectivity by collapsing only intended copper/links into circuit nodes and comparing every component endpoint against the authoritative netlist. Then inspect the physical view: graph equivalence alone does not detect an unshown copper bridge, a mounting screw across rails, inadequate lead reach or a wire drawn through a component body.

## Coil placement and nearby metal

Inductors interact through mutual inductance, `M = k sqrt(L1 L2)`. Separate their magnetic axes and use perpendicular axes for nearby coils where practical. Do not stack coils coaxially. There is no universal separation distance that makes all crossover coils independent: Coilcraft identifies orientation, distance, waveform, current and frequency as relevant. More than three coils cannot all have pairwise perpendicular axes. Record axis and body position for every coil, place unavoidable parallel coils farther apart, and evaluate declared coupling scenarios when that could affect the response. [Coilcraft FAQ, spacing and board layout](https://www.coilcraft.com/en-us/faq/)

Keep broad copper planes, metal straps, steel fixings and cabinet hardware away from unshielded coils unless their influence is accounted for. Route rails around the coil footprint rather than deliberately creating a conducting loop under it. Nearby conductors can alter losses and inductance; the magnitude depends on the particular geometry and frequency. Coilcraft's EMC discussion explains the mechanisms in an RF/switching context; its numerical layout heuristics are not universal audio-crossover acceptance limits. [Coilcraft EMC application note](https://www.coilcraft.com/ko-kr/resources/application-notes/fundamentals-of-electromagnetic-compliance/)

Use nonconductive coil restraints where possible. Never complete a conducting turn through a toroidal core and back around its outside with a bolt, bracket and chassis. Talema explicitly warns against the analogous closed centre-bolt/chassis loop in toroidal transformer mounting; the shorted-turn mechanism, rather than a transformer-specific power rating, is the applicable principle. [Talema open-style toroidal transformer installation](https://talema.com/products/toroidal-transformers-open-style/)

## Heat and component separation

Select power-resistor ratings using the actual installation, frequency-coincident dissipation and duty. A resistor's nameplate watts do not establish its surface temperature inside a cabinet. Keep hot resistors elevated above the PCB, with airflow around their bodies and clearance from film capacitors, adhesive, cable insulation and acoustic lining. Specify the chosen stand-off height and clearances as design dimensions; do not invent universal temperature-safe distances. Vishay explains the role of ambient air, mounting and terminal heat paths, while Ohmite's PC58 illustrates purpose-built PCB stand-offs. [Vishay thermal management](https://www.vishay.com/docs/30380/terminalderating.pdf), [Ohmite PC58](https://www.ohmite.com/res-pc58/)

A chassis-mount resistor may require a specified heatsink to achieve its headline rating; use its free-air rating if that heatsink is absent. Aluminum casing alone is not a heatsink installation. [Vishay RH/NH datasheet](https://www.vishay.com/docs/30201/rhnh.pdf)

Film-capacitor heating depends on solder exposure, lead length, nearby heat sources and mounting. Pre-tin heavy rails before installing heat-sensitive parts, use a tip capable of transferring heat promptly, and follow the selected component's soldering specification. Form leads with support at the body so bending force does not reach the termination. TDK's temperatures and times apply to its specified products and processes; they must not be silently transferred to another brand. [TDK film-capacitor mounting guidelines](https://www.tdk-electronics.tdk.com/download/187698/e7a5bd016c4f22e100e5e54231c7de6f/pdf-mountingguidelines.pdf)

## Mechanical support and service

Support heavy coils and large capacitors by their bodies, independently of solder joints. Use appropriately rated ties or clamps and compatible resilient pads; leave the solder lands accessible. Provide nearby PCB stand-offs so tightening restraints or cabinet vibration does not bend a large unsupported board. Do not use component leads as mounting brackets. Mundorf describes resilient bonding and screwed clamps for larger capacitors; KEMET explains how board flex and relative body motion stress terminations. [Mundorf elastic bonding](https://www.mundorf.com/en/technologies/elastic-bonding), [KEMET mounting discussion](https://www.kemet.com/en/us/technical-resources/aar80-advantages.html)

Show complete restraint loops, holes, washers, screw lengths and access. Keep mounting holes and metal washers clear of live copper; remove copper around holes where needed. Nylon hardware still needs mechanical strength and temperature suitability. Do not pull ties across a hot resistor, damage winding insulation, or close a metal strap around a coil. Adhesive supplements a specified mechanical restraint when mass and service conditions require it; an unspecified blob of glue is not a fastening design.

Fix and strain-relieve the input and driver harness before it reaches solder joints. Route associated outgoing and return conductors together where practical to reduce loop area, keep them clear of cone travel and port mouths, and prevent rattles against panels. Identify both ends of every module link and driver lead. Provide removable, accessible modules with sufficient service allowance; never bury a joint behind a part that must be destroyed to inspect it.

## Assembly and inspection sequence

1. Verify stock board construction and part dimensions; mark the copper-side datum and module identity. Cut and deburr the substrate, drill fixing/restraint holes and clear copper around them.
2. Make the documented isolation cuts. Check rail continuity and separation before fitting parts; after coils are installed, a legitimate winding can look like a short on a continuity buzzer.
3. Fit/pre-tin the shared rails and their splices. Check every node against the copper map, including unused islands and both board faces.
4. Install stand-offs, body pads and restraints, then the components. Preserve the shown coil axes and resistor elevation. Solder without tension on leads; trim tails and remove conductive debris.
5. Fit module links and strain-relieved harnesses. Verify component identity, endpoint labels, polarity and joint access against the master wiring view. Check driver-disconnected resistance against the circuit's expected low-resistance paths; do not demand isolation across a coil.
6. Install the boards with specified fasteners and lining clearances. Reconcile the parts list, conductor cut list, board volume and electrical model before releasing the construction package.

All external sources accessed 2026-10-21. Manufacturer process examples support the stated mechanisms; project dimensions and mounting choices remain the designer's engineering decisions. Local solver contracts: [board_nodal](../simulations/board_nodal/README.md), [crossover_network](../simulations/crossover_network/README.md).
