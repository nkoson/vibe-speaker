---
id: cabinet-construction
applies_when: Turning a loudspeaker enclosure concept into explicit joints, braces, treatment regions and buildable geometry
updated: 2026-10-15
---

# Cabinet construction as model input

Read [cabinet geometry](cabinet-geometry.md) for fit/volume, [materials and panels](cabinet-materials-and-panels.md) for mechanics and the documentation skill's [construction audit](../skills/speaker-documentation/references/construction-audit.md) for machining. Construction is a set of physical interfaces, not simply outside dimensions and wall thickness.

## Separate geometry by physical function

**Physics and model ownership.** Solid braces displace air, constrain panels and alter internal propagation. Porous fill occupies space but is not an equivalent airtight solid. A structural damping layer changes mass and loss; an acoustic lining changes internal absorption. A sealed midrange chamber changes both load and available bass air. Keep separate records for these effects and connect each to the solver that supports it. A material name does not supply frequency-dependent properties automatically.

**Construction representation.** Locate the brace matrix, outlet paths, driver chambers and treatment zones in dimensioned sections. Preserve component and panel identities across assembly views, cut lists and simulation geometry. A net-volume figure alone cannot describe where air flows or where panels are supported.

**Engineering application.** Store brace contacts, openings and treatment regions in cabinet coordinates. Reconcile net air with the union of actual solids; preserve acoustic-domain simplifications separately. A rendered 3D mesh helps detect collisions and construct solver domains, but its appearance is not an acoustic solution. Ports need their complete path, inlet/outlet geometry and local clearance, not only an equivalent tube length.

## Modes, stiffness and damping

**Physics.** Unequal dimensions can separate some coincident resonances; they do not establish low radiation or rapid decay. Stiffness moves modal frequencies; mass and loss change different terms of the mechanical response. Joint restraint, driver reaction forces and coupling between panels matter. Evaluate the complete relevant band before selecting a brace/material arrangement.

**Evidence scope.** The BBC's cabinet studies support treating stiffness, loss and coupling together; they do not establish that one wood species or thickness is always best. The current panel model uses isolated-panel approximations and a relative output proxy. A future coupled structural/acoustic solver can estimate radiation with explicit boundary conditions and convergence checks; the existing proxy is not such a solver. [BBC RD 1977/3](https://downloads.bbc.co.uk/rd/pubs/reports/1977-03.pdf)

## Make the sequence buildable

**Practice.** Plan glue/clamp access, interior treatment and crossover installation before closing the cabinet. State the order for fitting angled partitions, bracing and lining. Keep outlet openings and driver ventilation clear, and show the space needed to install or remove serviceable parts.

**Engineering judgement.** A reusable geometry record should produce loose-panel machining sheets, joint sections, installed clearances and simulation domains. Specify gasket compression and sealing faces, avoid obstructing basket vents, and account for driver motion. Compare alternative joints/materials within the tools and construction methods permitted by the brief. Retain the selected dimensions and margins in the final package instead of leaving geometry decisions for the builder.

## Sources

- H. D. Harwood and R. Mathews, [Factors in the design of loudspeaker cabinets](https://downloads.bbc.co.uk/rd/pubs/reports/1977-03.pdf), BBC RD 1977/3. Existing framework material/panel evidence; it does not prohibit more complete modern coupled models.

- [Cabinet geometry](cabinet-geometry.md). Dimensional interfaces, occupied volume and assembly clearance.
- [Cabinet materials and panels](cabinet-materials-and-panels.md). Wood Handbook material data, Leissa plate mechanics and the scope of the panel model.
