# From model to buildable drawings

Use while placing the selected network and preparing construction drawings, before the cabinet and board are frozen. A correct volume or netlist does not establish manufacturability. Keep the audit in the project and put the resulting dimensions, wiring and receiving checks in the builder package.

## Cabinet and machining

Give every loose panel an ID, actual blank dimensions and a local machining datum. Separate loose-panel coordinates from assembled elevations. Use exploded views and sections through real joints to show which broad face covers which cut edge; walk through assembly from cut blanks. Route every clearance finding into the audit, including warnings from helper scripts.

Keep machining dimensions, purchased hardware, mounting planes, compressed gaskets, motion envelopes and acoustic reference planes distinct. Resolve mating fits to single-millimetre targets and reconcile groove seating, thickness clearance and panel float independently. Dimension dry wood contact without adhesive allowances. Show gasket/tape installed compression and any separate rigid stop in each seating stack. Preserve factory fixing patterns using dimensioned symmetry/bolt circles; an instruction to transfer a pattern is not a substitute for showing its geometry. Regenerate geometry-dependent simulations as well as labels. Label an assumed installation envelope separately from a manufacturer's dimension.

Inspect factory front, rear and section drawings before converting width/height into a routed contour. Define recess, body aperture and grille separately, with corner radii identified as published, inferred or chosen allowance. Check cutter diameter/depth, fixing lands, sealing ledges, body clearance and lead access; distinguish finished outlines, cutter-centre paths and guide-bush templates. Generate actual arcs from these definitions and inspect every machining view. Use an actual-part scrap fit where tolerances are unknown, alongside the geometric checks.

Include gasket compression in seating depth and grille travel clearance. Draw the complete fastening stack: bearing faces, washer/gasket, panel web, insert or T-nut sleeve and screw. Thread engagement is overlap with the threaded sleeve, not just protrusion behind the wood. Key every hole to a visible dimension or on-sheet coordinate schedule, including diameter, depth, count and reference face. Inspect whether a CAD modeler can reconstruct all panels, joints, recesses, grooves, supports and mounting interfaces from the drawings alone; prose and unannotated vector outlines do not close a missing dimension.

For solid wood, reconsider grain, joints and panel float together whenever any changes. Identify long/end-grain glue faces, movement directions, species/climate-dependent movement allowance and short-grain lips. A panel resonance advantage does not establish joint integrity; cite wood data for allowances rather than copying a prior project's gap.

## Real parts and assembly access

Place the exact coils, capacitors, resistors and terminals using sourced dimensions and orientation, rather than a generic board reserve. Include body and lead tolerances, hot-part stand-offs, fasteners and screw access, binding-post lugs, lining and installed wiring. Replace the reserve with actual displacement without counting both. Treat coil separation/orientation as a coupling precaution; more than three coils cannot all have mutually perpendicular axes. Separate unavoidable parallel coils and avoid coaxial placement; no universal spacing certifies negligible coupling.

Check support solids in three dimensions, the complete tie loop and fastening tail, hole/lead diameters, pad access and mounting sequence. Use one placement dataset for audit and drawings. Find a physically feasible arrangement first, then shorten wiring by placing node connectors near the parts they join. Fix only geometry that matters electrically or mechanically; freezing every part can force avoidable crossings.

## Circuit, copper and visible wiring

Audit every component/driver endpoint against the authoritative circuit. Group only actual copper and specified links; review old bridges whenever a rail changes role. Distinguish physical pad addresses from rail aliases, and audit five-hole clips, split rails and numbering against the actual board. Check holes and restraints against active copper, neighboring holes and remaining ligaments. Mirrored copper views retain terminal IDs and declare their datum; distinguish board-edge trim dimensions from grid origins.

Inspect rendered symbols in both drawing directions for wires through component bodies or capacitor gaps. Graph equivalence does not catch visual bypasses or drilled copper. Provide driver-disconnected continuity checks that distinguish legitimate low-resistance coil paths from accidental input shorts. The finished board still needs inspection and testing.

For a build-by-picture package, provide one master physical view showing every lead, adapter, wire and external connection, with actual connector entry faces, consistent end labels and unambiguous crossings/junctions. Placement and abstract node views are supporting material, not substitutes. Count every added conductor, including extensions and reinforcement, not only inter-node jumpers. Check native lead reach and cut length including insertion and bends. Use a large vector sheet if a page makes wiring illegible; reduce unnecessary crossings before merely enlarging the page.

For solderless prototypes, check the exact connector's accepted conductor range, current rating and each contact interface. Keep unknown supplied lead diameters as receiving checks. A no-solder requirement includes amplifier/driver connections; use suitable factory leads or mechanical adapters. Compare the fixture and permanent board with identical components, polarity, sources and net air, sweeping declared contact/wire resistance. Equal topology is not equal response or equal current capability. The solver models only the resistances actually supplied.

## Figures and inherited prose

Take plotted phase from canonical complex section responses. Inspect their common propagation reference before removing delay; do not remove it twice. Compare each plotted branch against its stored response after only declared wrapping/common transformation, because relative phase alone misses a common error. Name the order of signed phase subtraction and convert signed tolerance intervals to match; check crossing markers against the actual plotted branches.

Regenerate quoted values from the frozen realization and reconcile old text, CAD, schematic, parts list and current results. A second reader or a fresh review pass should check the finished package against evidence without relying on the narrative that produced it. Keep a missing dimension or rating visible rather than filling it with a plausible inherited value.
