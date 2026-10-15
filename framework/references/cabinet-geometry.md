---
id: cabinet-geometry
applies_when: Sizing or placing anything inside or on a cabinet - drivers, horns, ports, braces, boards, terminals - and before claiming that something does or does not fit
updated: 2026-09-28
---

# Cabinet geometry: the interior is a volume

A cabinet interior is a three-dimensional space that several solid objects share. Nothing in this framework checks whether two of them occupy the same place: `framework/tools/cabinet_drawing.py` draws three elevations and subtracts litres, and it will happily draw a port tube through a brace, a woofer magnet through a partition and a crossover board through a horn. The occupancy bookkeeping is yours.

That makes "there is room" and "there is no room" claims you derive, not impressions you form from one drawing. Two mistakes make the derivation fail, and both are avoidable with arithmetic:

- **Comparing one coordinate.** Two objects at the same height on the same panel may be 300 mm apart front to back. A clash needs an overlap in all three ranges; anything less is not a clash.
- **Treating a shaped object as its bounding box.** A cone driver is not a solid block the size of its frame, and a horn is not a solid block the size of its mouth. Painting the bounding box over the interior deletes most of the space that ports, boards and wiring actually use.

## The frames the applications use

| Where | x | depth (y) | z |
|---|---|---|---|
| `cabinet_drawing.py` | mm from the left edge of the front elevation | not an input; each object's depth range is implied by what it is (see below) | mm from the cabinet bottom |
| `baffle_diffraction` inputs | mm from the baffle's left edge | not a source-position input | mm from the baffle's bottom edge |
| `whole_speaker` position inputs (also used by `crossover_fit`) | mm from the cabinet centre line, positive to the right | `depth_mm` behind the front face | mm from the cabinet bottom; the loader adds `cabinet.floor_offset_mm` |
| `directivity` | no cabinet coordinates | no cabinet coordinates | no cabinet coordinates; angles are relative to the source axis |

Convert deliberately: `x_centre = x_left - width/2`. Keep `z_bottom` in the `whole_speaker` input when using `floor_offset_mm`; its resulting physical height is `z_floor = z_bottom + floor_offset_mm`. Adding the offset to both inputs raises the source twice. See `simulations/baffle_diffraction/README.md` and `simulations/_common/radiation.py:load_sections` for the input contracts. In the cabinet spec, `rear_cutouts` are given in the same left-origin frame as the front and the tool mirrors them for the rear elevation; mirror it yourself as well and the duct appears on the wrong side of the rear elevation while the volume accounting stays unchanged, which is the kind of error nothing else will flag.

## What the cabinet spec implies in depth

With outside depth `D` and panel thickness `t`, the interior occupies depth `t` to `D - t`. Then:

- A `ports` entry `{x, z, od, length}` is a cylinder of diameter `od` centred on `(x, z)`, occupying depth `D - t - length` to `D - t`: a rear-panel duct reaching `length` millimetres forward into the box. Any object inside that cylinder is in the way; any object outside it is not, however close its height.
- A `front_cutouts` entry is a hole in the baffle. The part behind it starts at depth `t` and extends back by its own overall depth from the datasheet - the cutout says nothing about that.
- A `braces` entry at `z` is a panel across the full inside width and depth with a window cut in it, so it claims every x and every depth at that height except the window. A duct or a wire crossing that height passes through the window or through a hole you add to the brace and account for.
- A `partitions` entry at `z` is solid across the full section; nothing passes without a cutout listed on the partition.
- `lining_mm` takes that thickness off every lined surface before anything else is placed.

## The things inside are shaped

**Cone driver.** Circular flange on the baffle, then a basket that narrows quickly to a magnet assembly typically about 40 to 60 percent of the flange diameter, over an overall depth from the datasheet. Model it as a flange disc a few millimetres thick, a frustum from the cutout diameter to the magnet diameter, and a magnet cylinder. The corners of its bounding box and the annulus around the magnet are open space, and that space is where ducts, boards and wiring normally run. Datasheets publish cutout diameter, outer diameter, overall depth and displacement volume; the taper is often only in the drawing. When you have to approximate it, approximate it as the frustum above and write in the notes that you did.

**Horn or waveguide.** Mouth on the baffle, body tapering back to the throat, compression driver and its magnet behind that. It occupies the front of its chamber over its axial length, and the space beside the throat is open. A rear-panel object at the same height as the horn mouth is behind it, not inside it.

**Dome or ribbon.** A shallow body, roughly 15 to 30 mm behind the baffle for a dome, plus the magnet and any rear chamber; a ribbon's transformer sits behind the baffle too.

**Port tube.** A cylinder along its axis whose outside diameter is the bore plus twice the wall thickness of real tube stock, and wider still at a flared end. `lf_box` reports `results.vent.physical_length_mm`, already corrected for the duct ends; that is the length you place, and it grows with the square of the diameter for a given tuning, so a larger duct is a longer duct. An elbow is two cylinders and a bend, with the bend's centreline adding to the acoustic length; the framework's duct model is a straight round vent, so an elbow's tuning is an estimate you flag.

**Passive radiator.** A cone that moves. Keep the swept volume clear behind it over the peak excursion the alignment predicts, with margin, not just the static body.

**Crossover board.** A plate with components standing off it, the tallest usually a coil. It has a footprint, a height, a mounting position and a displacement, and it needs air around hot parts and spacing or right-angle orientation between coils.

**Terminal cup, hardware, damping, wiring.** A cup is a recess with a depth behind the panel. Bolts, T-nuts, feet, plinths, grille fixings and the wiring loom take space and change the outside envelope as well as the inside.

## The occupancy list

Before you place anything and before you claim that something does not fit, write a list with one row per object: name, shape, x range, depth range, z range, where each number came from, and the assumptions you made. Include the chamber's own interior as the first row. Two objects clash only when all three ranges overlap; report the overlap in millimetres when they do.

Keep the list in the candidate's `notes.md` and carry the objects that displace air into the cabinet spec, because the drawing cannot show it and the cut list cannot check it.

## Clearances, and the reason for each

- **Duct inner end to the nearest surface**, commonly held at one to two duct diameters: JBL's documents give both "one port diameter" and "about twice the port dimension", and no measured threshold was found. The reason is the constriction. Air leaving a duct of diameter `D` toward a wall at distance `h` passes through a curtain of area `π D h`, which equals the bore area at `h = D/4` and is four times it at `h = D`. A closer surface raises losses, shifts tuning away from the model and adds noise. The value is practice; the reason is geometry (`cabinet-construction.md` section 13).
- **Duct mouth on the outside** away from the floor, a wall or a grille for the same reason, and away from the listener when chuffing matters.
- **Around the magnet**, a clear path so the rear of the cone loads into the chamber rather than a trapped pocket. The `lf_box` model assumes the cone sees the box volume; a magnet pressed against a brace or a rear wall is a different acoustic problem than the one that was simulated.
- **Brace windows** large enough that the bays are acoustically one chamber, which is also what the volume accounting assumes.
- **Bay length** short enough to raise panel modes: no side bay much longer than about 300 to 400 mm is common practice for a stiff box, and `plate_structure` will tell you what the choice did.
- **Driver flanges and cutouts** not overlapping each other, the panel edges or a brace, with room for the fixings and the gasket.
- **Hot crossover parts** away from damping material, wiring and the tube walls.

## Terminals: the hole the wires leave through

A terminal is four things at once - a hole in a box that has to stay airtight, a solid object with a
depth behind the panel, a current path, and the part of the speaker an owner touches - and its
position is argued against all four.

**The hardware sets the hole, not the other way round.** A pair of five-way binding posts takes
banana plugs, spades, pins, bare wire and clips, and the pair is drilled on the 19.05 mm (3/4 inch)
centre spacing that a double banana plug needs; that spacing is a de facto convention inherited from
General Radio test equipment of the 1920s, and it decides whether an owner's existing cable fits. A
moulded cup or plate is a bigger hole with a recess behind it: one vendor's 76 mm round cup wants a
51 mm cutout, carries a gasket and stands about 4 mm proud of the panel. The professional
alternative, Neutrik's speakON, is a chassis connector with published ratings - 30 A rms continuous,
250 V ac, contact resistance at most 3 milliohms - and the manufacturer states it is not to be used
as a mains connector. Take the cutout, the depth behind the panel and the fixing pattern from the
drawing of the part you will actually buy, the same way you take a driver cutout from its datasheet.

**Polarity and market.** IEC 60268-5 carries a clause on marking terminals and controls, including
the positive terminal. The clause text is behind the standard's paywall; the practice it codifies is
not in doubt - red and a `+` mark the positive terminal, black the return - and a construction
document should state the polarity at the terminals rather than leave it to the colour of a wire. In
the European Union, equipment whose sockets accept 4 mm banana plugs ships with removable plastic
plugs blocking them, because a European mains outlet will physically accept a double banana at
roughly the same spacing. A terminal design that only works with unshrouded 4 mm sockets is
therefore not one that ships in that market: keep spade and bare-wire access.

**Where on the panel.** Placing the row low on the rear of a floorstander, so the cable drops to the
floor instead of hanging out sideways, is ergonomics and convention rather than acoustics; it is a
reasonable default and it is not a rule. What can actually veto a position is geometric, and it is
the ordinary occupancy problem: a rear passive radiator's swept volume, a rear duct's inner end and
its clearance, the crossover boards, the lining, and the brace whose rim is bonded to that panel.
Put the terminal row in the occupancy list with its depth behind the panel, including the length a
plug and a bent cable need outside the cabinet, and check the three ranges like anything else.

**What the position costs.** The lead from the terminal to the board is series resistance in that
branch and belongs in `wire_loop_ohm` rather than in an assumption that it is zero: one metre of
1.5 mm2 copper, out and back, is about 0.023 ohm, the same order as a coil's DCR. The hardware's own
current rating has to cover the branch current that `crossover_network` or `board_nodal` reports.
Route the run clear of the crossover's coils, whose spacing and orientation rules are in
`crossover-design.md`, and clear of any reserved motion envelope. The cup or plate displaces air and
goes in the displacement list below. And the hole is a leak until it is sealed: a gasket plus
sealant on a clean bore is the practice, and a terminal is the most common place to lose the seal
that a sealed or vented alignment assumed.

**A judgement, stated as one.** A hole costs the most stiffness in the middle of a large unbraced
bay, where the panel's bending is greatest, and least near a brace or a panel edge. That follows
from plate bending rather than from any measurement in this repository, and `plate_structure` treats
bays as uncut plates, so it will not show the difference.

## Volume accounting is part of geometry

Every object in the chamber subtracts from the net air volume the alignment was designed for. `cabinet_drawing.py` subtracts braces, ducts listed in `ports`, lining at its solid fraction and whatever you list in `driver_displacements`; it knows nothing about a horn body, an elbow, a board, a terminal cup or a bag of wadding, so those go in as displacement entries with their z, or the net volume is wrong. After any geometry change, rerun the cut list, and when the net volume moved, rerun `lf_box` before believing the old response.

## Making a claim about fit

A claim that something does not fit is a finding with a derivation, and the derivation has three parts: the extents of the object, the occupancy rows it would overlap with the overlap in millimetres, and the alternatives you tried. For a duct the usual alternatives are: move it on the panel; split the area into two or more smaller ducts; change diameter and accept the new length; flare it; form a slot duct from panels in a corner; bend it and flag the tuning estimate; move it to the front panel; change tuning or net volume; use a passive radiator instead. Reaching a blocking conclusion without naming which of those failed and why is a conclusion about the first idea, not about the cabinet.

Two habits protect the derivation:

- **Do not carry a finding across objects.** A brace that really does collide with something tells you about that brace. The duct at the same height is a separate derivation with its own extents, and one paragraph covering both usually means only one was computed.
- **Do not turn an unknown into a blocker.** When a dimension is not published, say which dimension, what you assumed, and what would settle it, then continue with the assumption on the record.

## What the applications do not model

`cabinet_drawing.py` draws a rectangular box with rectangular panels and does no interference checking, no depth placement of front objects, no elbows, no non-rectangular cabinets, no chamfers and no grilles. `lf_box` supports declared straight/flared round-duct geometry; bends and slots remain equivalent-geometry estimates. `cavity_modes` and `plate_structure` take the chamber as you describe it. Where your cabinet departs from those assumptions, the numbers are estimates: say so in the candidate notes and in the documentation, next to the figure they affect.

## Panel treatment, and how little is established here

Bay length and bracing are in the clearances list above because they move panel modes; what follows
is what is and is not known about damping those modes once they exist.

**Constrained-layer damping, and its mechanism.** The dissipation in a constrained-layer treatment is
transverse **shear** strain in the viscoelastic layer, which only develops when a stiff skin forces
the layer into shear instead of letting it bend freely with the panel. The stack is
panel / viscoelastic adhesive / stiff constraining skin. A free layer works by extension instead,
and works best on a thin, low-impedance panel: the BBC measured free layers bringing a 9 mm plywood
panel from `Q = 70` to 8.5-10 and a constrained felt-and-steel layer to `Q = 7`
(`cabinet-materials-and-panels.md` section 1).

**The magnitude depends on the substrate.** One finite-element study of a 0.4 x 0.3 m clamped
**steel** plate, 1 mm base with a 0.4 mm damping layer and a 0.1 mm constraining skin, found a
first-mode modal loss factor of 0.023 at full coverage and 0.024 for topology-optimised partial
coverage using 60 to 80 percent of the material. The same order of loss factor is not what the BBC
measured on wood, and KEF reports a theoretical 30 dB from damping placed between braces and walls.
Where damping does its work, and the constructions that deliver it, are in
`cabinet-construction.md` sections 3 and 4.

**Do not transfer the layer thicknesses.** The 40 percent and 10 percent thickness ratios belong to a
1 mm steel substrate. A loudspeaker wall of 18 to 25 mm MDF is twenty times thicker and several times
lower in modulus, and constrained-layer effectiveness depends on a shear parameter that scales with
layer thickness, shear modulus and bending wavelength — none of which the source sweeps. The
transferable parts are the topology (shear layer under a stiff skin) and the order of magnitude.

**Current model boundary.** `plate_structure` reports pinned-to-clamped mode bands, material/treatment priors and a relative audibility comparison when a cone reference is supplied. It does not establish absolute radiated SPL or the restraint of a particular glued joint. The available material data and their limits are recorded in `cabinet-materials-and-panels.md`; use that reference and `simulations/plate_structure/README.md` rather than interpreting a brace-spacing rule as acoustic qualification.

## Installation datums and early geometry review

**Practice.** Draw the occupied front, rear and side sections as soon as the driver set is fixed, before fitting the crossover. Use `framework/templates/geometry-audit.md`. Separate flange projection, recess depth, through-cut and overall installed body depth; the acoustic center is a separate model coordinate. Read both ends of each dimension arrow in the manufacturer's drawing.

Track wooden, static assembled and moving/service bounds separately. A passive radiator's diaphragm can project beyond a flush flange. Track duct acoustic path, wall traversal and internal protrusion separately; the tool's `ports.length` is the internal length as defined above. A slot or bent duct equivalence carries tuning uncertainty.

Include fasteners, leads, cable insulation, straps, spacers, adhesive, motor supports and sealed service spaces in the installation reserve. Check individual bolt coordinates and access against panel edges and supports; check wire entries against support grids. When detailing an object, replace its reserve rather than adding both displacements. Intersecting supports need specified joinery, and their solid union is counted once. State view direction separately from datum, especially on rear-mounted boards.

A conservative bounding overlap is a reason to inspect the actual shapes, not proof of interference; likewise a nominal box clearance does not establish fastener access or moving clearance. After a net-air correction, rerun the alignment and the complete fixed-network chain before retaining the old score.

## Sources

- Thiele, A. N., "Loudspeakers in Vented Boxes, Parts I and II", *Journal of the Audio Engineering Society*, vol. 19, nos. 5 and 6, 1971 - the alignment the duct length comes from.
- Small, R. H., "Vented-Box Loudspeaker Systems, Parts I to IV", *Journal of the Audio Engineering Society*, vol. 21, 1973 - box losses, duct end correction and the limits of the lumped model.
- Salvatti, A., Devantier, A., Button, D. J., "Maximizing Performance from Loudspeaker Ports", *Journal of the Audio Engineering Society*, vol. 50, no. 1/2, pp. 19-45, 2002 - duct area, flares, edge radii and the air speeds at which each geometry becomes audible. The convention-paper version read here does not address a duct's distance from surfaces. <https://aes2.org/publications/elibrary-page/?id=11094>
- JBL, D. Daniels, "Notes on porting", 1985, and the JBL GTO/P1000-series subwoofer owner's manual - the two- and one-diameter duct-end clearances, stated as practice without measurements. Archived copy of the notes: <http://www.cieri.net/Documenti/JBL/Documenti%20tecnici/JBL%20-%20Ports%20and%20Vents.pdf>
- Olson, H. F., "Direct Radiator Loudspeaker Enclosures", *Journal of the Audio Engineering Society*, vol. 17, no. 1, pp. 22-29, 1969 - the outside shape of the box is part of the response, not only the inside volume.
- Constrained-layer damping topology optimisation study, *Materials* (MDPI), vol. 15, no. 10, 3512, 2022 - the shear mechanism, the modal-strain-energy loss-factor method, the representative viscoelastic properties and the modal loss factors quoted above. A steel-plate finite-element study with no loudspeaker context and no measured validation; the measured wood-panel damping data are the BBC's, in `cabinet-materials-and-panels.md`. <https://doi.org/10.3390/ma15103512>
- IEC 60268-5, *Sound system equipment - Part 5: Loudspeakers*, clause 14 "Marking of terminals and controls", including the positive terminal. The clause title is from the contents page of the publicly available preview; the clause text is paywalled and has not been read here. <https://webstore.iec.ch/en/publication/1223>
- Neutrik, speakON NL4MP and NL4MPXX product documentation - 30 A rms continuous, 250 V ac, contact resistance at most 3 milliohms, and the manufacturer's statement that speakON is not to be used as an AC mains connector. Manufacturer documentation for one connector family. <https://www.neutrik.com/en/product/nl4mp>
- Wikipedia, "Banana connector" and "Binding post" - the 19.05 mm double-banana centre spacing and its General Radio origin, the connection types a five-way post accepts, the red-positive convention, and the European practice of shipping audio equipment with those sockets blocked. A tertiary source, used here only for conventions that are not published as a standard anyone can cite.
- A vendor terminal-cup listing, DIY Sound Group "Standard Round Terminal Cup" - 76 mm outside diameter, 51 mm cutout, gasket fitted, standing about 4 mm proud. One vendor's part, quoted as an example of the dimensions a cup imposes, not as a general figure. <https://www.diysoundgroup.com/speaker-accessories-136/round-terminal-cup.html>
- Dickason, V., *The Loudspeaker Design Cookbook*, 8th ed., Audio Amateur Press - construction practice: bracing, lining, duct placement, mounting and displacement accounting.
- The manufacturer's mechanical drawing of the part in hand, for every dimension that decides a fit. Nothing here replaces it.
- In this repository: the header of `framework/tools/cabinet_drawing.py` for the spec fields, `framework/simulations/lf_box/README.md` for the duct model, `framework/simulations/whole_speaker/README.md` for the placement frame.
