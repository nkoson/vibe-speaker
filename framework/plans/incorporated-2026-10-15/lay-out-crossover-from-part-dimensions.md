---
id: lay-out-crossover-from-part-dimensions
date: 2026-10-01
project: neat-petite-amt-v4, neat-petite-dayton-astra, neat-dayton-redcatt
phase: design
confidence: medium
applies_when: Choosing where the crossover board goes in a small cabinet, or auditing interior occupancy with a generic board envelope
tags: [crossover, board, occupancy, lining, geometry]
---

## What went wrong
The geometry audit placed the crossover as a generic board envelope. The selected network's real parts needed far more footprint than that envelope offered, and the problem surfaced only when the board drawing was made after selection. The first relocation then came within about a millimetre of the binding-post lugs and ran into the wall lining, because the lining was not an audit object. Plate screws drawn at the corners fell inside a coil's footprint. Each fix also changed the terminal arrangement and the drawings. In a later release, a larger upright coil also invalidated the inherited restraint length and blocked pad access; support blocks that looked separate in plan overlapped in three dimensions, and a thick coil lead did not fit the factory pad hole. Body envelopes alone had not established an assembly sequence.

A ten-part revision had four coils for three axes on a fixed board with six screw-access circles. Hand placement left several rules broken, and a random placement search found a layout that kept every rule in only a few of fifty starts. The first such layout had two parallel coils nearly coaxial. It also put a capacitor 74 mm from the coil it bridges, because the search did not see connectivity.

## What could have helped
As soon as a network is a selection candidate, place its parts from datasheet dimensions with their tolerance: coil diameter and height in the intended orientation, capacitor body length, resistor stand-offs. Include the plate, its fasteners, the terminal lugs and the lining thickness on every lined face. Run the clash and clearance audit on part-level boxes rather than one envelope. Keep coil axes at right angles and hot parts clear of others. With more coils than axes, give each parallel pair both a minimum distance and a minimum sideways offset between axes, so that none is coaxial. When searching placements, first find one that satisfies every hard rule, then shorten the node-to-node wiring while keeping those rules satisfied. Keep the placement as data shared by the audit and the drawings, so the two cannot disagree. Board volume then becomes a real reserve figure rather than an estimate.

Include the complete restraint loop, support stack, return path and fastening tail when choosing tie lengths. Check conductor diameters against actual holes and copper islands, and plan accessible, strain-relieved connections before parts hide the solder points. Compare support solids in three dimensions and use distinct labels for mechanical supports and electrical pad addresses. A staged drawing of the bare-board soldering and later mounting can expose access assumptions that a finished layout cannot.
