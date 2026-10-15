---
id: cabinet-construction
applies_when: Turning an enclosure concept into a buildable cabinet - bracing, damping, joints, adhesives, fasteners and driver mounting, lining and fill, sealing, separate chambers, ports and outside details as built, materials as built, floor coupling, assembly sequence, verification and workshop safety
updated: 2026-10-15
---

# Cabinet construction

A loudspeaker cabinet is a set of physical interfaces, not an outside size and a wall thickness. This reference covers how the box is built and what each construction choice does to the sound. The neighbouring references cover the rest: [cabinet geometry](cabinet-geometry.md) for fit, occupancy, terminals and volume accounting; [materials and panels](cabinet-materials-and-panels.md) for elastic and damping data, plate frequencies and the BBC audibility criterion; [baffle and driver placement](baffle-and-driver-placement.md) for edge diffraction; [enclosure alignments](enclosure-alignments.md) for the volume and tuning the box must deliver. The documentation skill's [construction audit](../skills/speaker-documentation/references/construction-audit.md) covers machining drawings.

**Read these five findings first, because each one overturns a common rule.**

- **Stiffness moves a resonance; damping and coupling set its level.** A stiff brace raised a wall resonance by an octave in KEF's simulation without lowering it relative to the driver. A university simulation of a commercial cabinet, checked against accelerometer measurements, found its internal support radiated more than no support at all, and the BBC's double-thickness cabinet radiated more than the thin one (section 3).
- **The driver drives the walls through its frame, and the internal pressure drives them too.** Neither path is negligible in general. The driver-to-baffle joint is a design element, not a fixing detail (sections 2 and 7).
- **Joints, fillets and glue coverage are structural parameters.** Glue modelled over 70 % of a joint lowered a B&W panel section's first mode from 474 to 409 Hz. Fillets of the wrong timber species made a BBC panel peak 9 dB louder and audible (section 5).
- **Leakage is usually the largest loss in a real box.** Small measured leakage `QL` of 5 to 20 even in well-built boxes, and some of the leaks were in the drivers themselves (section 10).
- **Wall lining treats the midrange, not the bass, and fill adds less volume than folklore says.** Thirty millimetres of mineral wool did almost nothing at a 40 Hz box resonance and heavily damped the 213 Hz first mode. The thermodynamic ceiling on the compliance gain from fill is 40 %, and Small judged practical gains "probably never more than about 25 %" (section 9).

## 1. What a cabinet has to do

| Job | What goes wrong when it fails | Section |
|---|---|---|
| Hold the net air volume the alignment assumed | Leaks, displaced volume, wrong fill gain, panels acting as springs | 2, 9, 10; [geometry](cabinet-geometry.md) |
| Keep the walls from radiating audibly | Panel and baffle modes driven by the motor reaction and the internal pressure | 2 to 5 |
| Stop interior sound coming back out | Standing waves and rear reflections returning through the cone and the port | 8, 9 |
| Hold every driver rigidly, sealed and serviceable | Baffle–driver resonance, frame warp and rub, leaks, stripped fixings | 7, 12 |
| Keep separate chambers separate | Woofer pressure driving a midrange or tweeter | 11 |
| Make the port behave as modelled | Noise, compression, pipe resonances, tuning error | 13 |
| Present the outside shape the diffraction prediction assumed | Grille frames, proud flanges, edges | 14 |
| Keep its coupling to the floor predictable | Rigid-body modes on feet and spikes | 15 |
| Survive moisture, temperature, handling and service | Joint failure, warping, short-grain breakage, heat-softened glue | 6, 16 |
| Be buildable in the stated order, and safely | Unreachable joints, closed-in faults, dust exposure | 19, 20 |

## 2. What drives the walls

**Physics.** Two forces excite the cabinet. The motor pushes the voice coil with `F = Bl i` and pushes the magnet and frame back with the same force, which the frame passes into the baffle. Above the driver's resonance the suspension contributes little, and B&W measured the frame force on a free-hanging 10 inch driver to within ±0.5 dB of `Bl i` from 10 Hz to 1 kHz. The cone also compresses the box air, `Δp = γ P0 ΔV / V`, which pushes every panel outward at once.

**Worked numbers (derived here).** `Bl = 7 T·m` at 2.83 V into 6 Ω gives 3.3 N on the frame. A 220 cm² cone moving 1 mm in a 20 L box gives 156 Pa inside, which is 28 N on a 0.18 m² panel. At 5 mm the internal pressure is 780 Pa peak.

**Which path dominates depends on the cabinet.** Four studies disagree in a way that is informative:

- **KEF LS50**, a small box with thick walls (manufacturer FEA/BEA): wall output driven by internal pressure was "almost 40 dB" below the diaphragm. Wall output driven by the reaction force peaked about 7 to 11 dB below it (figure readings).
- **B&W 800 Diamond** (manufacturer coupled FEM): the pressure path radiated 10 to 20 dB less power than the mechanical path, except near coincidence peaks.
- **Pioneer** (Jones, preliminary report): decoupling the driver from the baffle cut panel acceleration by more than 20 dB, "This confirms that the dominant excitation source is mechanical."
- **ISVR** (Alavi and Holland, laser vibrometer on an 18 mm plywood cabinet): the back panel vibrated about as much as the front because of the internal pressure.

So neither path can be dropped. Thin walls, large panels and vented boxes give the pressure path more weight. Do not write "the reaction force always dominates" or "panels are driven by the box pressure".

**Rigid-body motion.** At low frequencies the whole cabinet moves against the cone's moving mass and radiates as a dipole (KEF). For a free 15 kg cabinet the 3.3 N force above gives 0.56 µm at 100 Hz, about 58 dB below the motion of a 20 g cone (derived here). Jones's measured free-magnet ratio of 40.2 dB for 1 kg against 10 g confirms the mass-ratio rule. On real supports the mount resonance governs instead (section 15).

**Panels are part of the alignment.** Below its first resonance a panel is a spring in parallel with the box air. The BBC requires vented-box panels stiff enough "that the resonance frequency is not affected to any great extent" and that they do not radiate "appreciably in antiphase with the sound output from the vent". The volume compliance of one pinned 300 × 600 mm panel, relative to a 20 L box, is about 2.4 % for 18 mm MDF, 1.1 % for 18 mm birch plywood and 8.4 % for 9 mm birch plywood (Navier series, derived here). The panels' compliances add, so a box of thin panels shifts the alignment measurably, while thick panels add a few per cent at most. In a closed box the panel mass, the air spring and the cone mass also form a coupled mode, 172 Hz in Luan's test rig with a PVC panel.

**Cabinet radiation is not negligible.** Bastyr and Capone found by laser scanning and BEM that a cabinet's "radiation efficiency is many times greater than that of the drivers", so a small wall velocity still matters near the cabinet's lower resonances. B&W cites their result as cabinet output "comparable with that of the main drive units in the frequency range 100-300Hz" for a floorstander. Alavi and Holland found the cabinet's on-axis contribution added peaks of about 1 dB and dips of up to 4 dB between 400 and 1100 Hz. Skrodzka and Sęk called front-panel vibration negligible, but they compared velocities rather than radiated pressure and their readings sat within 5 dB of the noise floor.

## 3. Bracing

### 3.1 What a brace does

**Physics, stated by the BBC.** "The resonance frequencies for a given panel can be raised by fixing struts along the surface of the panel and this effectively increases the stiffness without significantly increasing the mass." A stiff rod joining the centres of two opposite panels suppresses their fundamental, because the internal pressure pushes both outward at the same moment. The axial stiffness of a 20 mm hardwood dowel 300 mm long is about `1.3e7 N/m`, roughly ten times the centre-point stiffness of a pinned 300 × 600 mm panel of 18 mm MDF (derived here, with an assumed `E = 12 GPa` for the dowel). A rod helps against the pressure-driven mode. Against a reaction-force-driven mode it also couples the two panels together.

### 3.2 A brace works only if it forces a nodal line

**Physics.** A rib adds bending stiffness through its second moment of area, `I = w d³ / 12` about its own axis plus a parallel-axis term for its offset from the panel. A strip set on edge, with its depth `d` in the bending direction, is `(d/w)²` stiffer than the same strip laid flat: 6.0 times for 18 × 44 mm and 6.9 times for 19 × 50 mm. Doubling both dimensions multiplies `I` by 16.

**Simulated (online magazine, secondary).** Waratuke's finite-element study of a pinned 1016 × 457 mm panel of 19 mm MDF gave a first mode of 114 Hz unbraced (recomputed here: 114.7 Hz). Braces of 2 × 3/4 inch raised it only to 158, 208, 223 and 274 Hz for 1, 3, 4 and 9 braces. Braces of 4 × 1 1/2 inch raised it to 177, 341, 384 and 475 Hz. The shallow braces could not force a node, so the panel kept vibrating as one plate. Nine identical, evenly spaced deep braces produced a cluster of six modes between 475 and 496 Hz. The model has no air, no joint compliance and no radiation metric, so it shows frequencies, not audibility.

**Consequence.** `plate_structure` treats every brace line as an ideal support and every bay as a separate plate. That is optimistic when the braces are shallow or loosely glued. Check that the brace section is deep enough before trusting the bay frequencies, or give `coupled_cabinet` an explicit edge stiffness.

### 3.3 When braces stop acting together

**Physics (Luan, DTU/Bang & Olufsen).** A rib-stiffened panel behaves as one stiffened plate only while half the bending wavelength in the panel is longer than the rib spacing. Above that, "half a bending wavelength in the base plate becomes comparable to – or smaller than – the stiffener spacing", and the bays between ribs vibrate separately. Half the bending wavelength, derived here:

| Frequency | 18 mm MDF (3.59 GPa, 750 kg/m³) | 18 mm birch plywood (8 GPa, 720 kg/m³) |
|---|---|---|
| 100 Hz | 433 mm | 534 mm |
| 200 Hz | 306 mm | 378 mm |
| 500 Hz | 193 mm | 239 mm |
| 1 kHz | 137 mm | 169 mm |

Braces 200 to 300 mm apart therefore stop acting as global stiffening somewhere between 200 and 500 Hz, which is the band where the BBC criterion tightens fastest. The coincidence frequency, above which the panel's bending waves radiate efficiently, is about 1.6 kHz for 18 mm MDF and 1.0 kHz for 18 mm plywood (standard plate theory, not taken from a source read here).

### 3.4 Stiffer is not quieter

- **KEF (manufacturer FEA/BEA):** an X-brace behind the LS50 driver raised the lowest wall resonance from about 700 Hz to about 1.5 kHz, "while the resonance was raised to a higher frequency, its amplitude was not reduced relative to the driver. Indeed the frequency is raised towards the ear's most sensitive region."
- **Bastyr and Capone (measured, abstract read):** comparing a cabinet with and without its bracing, "stiffer cabinets with lower amplitude wall vibrations do not always radiate less sound."
- **Aalborg University with DALI (master's thesis, FEA checked against accelerometer measurements):** the cabinet's existing internal support gave a higher peak equivalent radiated power than no support at all, 90.5 against 87.6 dB. Moving the same support cut it by 3.3 dB. Bringing two eigenfrequencies closer together raised the summed response.
- **BBC:** the 18 mm cabinet radiated more than the 9 mm one, because its `Q` was higher ([materials and panels](cabinet-materials-and-panels.md) section 4).

**Consequence.** Brace for a stated band and pair the bracing with damping. Judge a bracing scheme by radiated output relative to the driver, never by first-mode frequency alone. The BBC criterion is flat at about −30 dB from 400 Hz to 10 kHz, so no frequency exists above which a resonance is automatically safe. The ESP claim that resonances above about 1.5 kHz have "no energy available" is a judgement. It ignores the woofer or midrange frame that keeps driving the baffle above its crossover, and the tweeter on the same baffle.

### 3.5 Layout

- **Unequal bays.** Spacing braces so that no two bays share a size is widely advised ("each braced section should be a different size from any other", ESP). No measurement of it was found. The indirect support is simulation: identical evenly spaced braces clustered their modes (Waratuke), and close eigenfrequencies summed (Aalborg). Label it judgement.
- **Symmetry planes.** "A brace positioned centrally on the plane of symmetry cannot buckle: in effect the symmetry adds stiffness to the brace" (KEF, manufacturer judgement with no data).
- **Matrix bracing.** B&W's FE-driven redesign of a floorstander into a plywood matrix with steel brackets predicted 10 to 20 dB less cabinet acoustic power in the most significant band. The same paper found its FE model over-predicted measured mode frequencies by 10 to 20 %, which is the measured accuracy to expect from an FE model of a real wooden cabinet.
- **Brace windows** must keep the bays acoustically one chamber, and every brace goes into the occupancy list and the volume accounting ([cabinet geometry](cabinet-geometry.md)).

### 3.6 Bracing at the driver

- **The baffle with the driver's mass forms a resonance.** In the BBC LS5/8 the baffle's compliance with the drivers' mass resonated "at about 60 Hz, with a Q factor of about 10". Two horizontal hardwood battens, one above and one below the woofer, removed it. The BBC's general remedy is to make the baffle "only slightly wider than the diameter of the unit, thus ensuring a very high panel stiffness".
- **Frame resonance.** If a driver's frame arms are curved, "the magnet mass resonates with this stiffness at mid audio frequencies with a very high Q". The BBC's only practicable damper was "a strong brace across the cabinet just behind the magnet together with a piece of dense felt compressed between the magnet and the brace; however, large forces are communicated to the panels." A magnet brace turns the rear panel into a reaction-force path. State that trade-off when you specify one.
- **Not quantified anywhere found:** how much stiffness a doubled baffle adds, and how much a driver cutout removes.

## 4. Damping and coupling

The measured loss factors of named treatments are in [materials and panels](cabinet-materials-and-panels.md) section 1. This section covers where damping does its work and which constructions deliver it.

**Where damping works (BBC, measured on a damped beam).** On a 50 cm beam clamped at both ends with three layers of damping, removing 30 % of the material from the ends raised `Q` only from 9 to 11.7. The BBC extrapolate that about half the area of a panel can be left bare at the edges. A cut through all layers at mid-span raised `Q` from 11.7 to 20, while a cut through the top layer alone did nothing measurable. **Practice that follows:** put the damping in the middle of each bay and keep it continuous there. Applying the same reasoning to a braced bay, treating each brace as a clamped edge, is a judgement.

**A free layer also works, on a thin panel.** The BBC's free layers reached `Q` of 8.5 to 10 on 9 mm plywood (three layers of Bostik; one layer of Aquaplas) through extensional damping. The BBC states that "such a lossy layer will have the maximum effect on a system having relatively low mechanical impedance, which implies a fairly thin panel". A constrained layer, with a stiff skin forcing the viscoelastic layer into shear, did best (`Q = 7`). Both work on a thin panel. On a thick panel the same treatment buys less, and the BBC's thick-walled cabinet would have needed "much thicker, and therefore more expensive, damping material" ([materials and panels](cabinet-materials-and-panels.md) section 4).

**Damped bracing (manufacturer claim).** KEF put material of "high mechanical resistance and low stiffness" between the brace and the walls, baffle and driver. It reports "a theoretical reduction in cabinet vibration of about 30dB which is approximately 20dB greater than could be expected with conventional damping material directly attached to the panels". Its single-point laser decay plots of three rear panels show the mechanism at work. A budget chipboard box had a 250 Hz resonance at 47 dB still visible after 50 ms. The LS3/5A had resonances at 300 to 400 Hz at 38 dB, gone within 30 ms. The LS50 showed tails of about 23 dB. These are a simulation and single-point manufacturer measurements against other makers' products, with uncalibrated levels. The mechanism, shear in a layer between a stiff brace and a wall, is the same one the BBC measured.

**The lossy thin-wall approach, stated by its originators.** The BBC damped thin panels deliberately. The LS5/8 used 12 mm birch plywood with self-adhesive bitumen pads "to a thickness approximately equal to that of the wood itself" on every panel except the baffle. The baffle's problem was the driver-mass resonance of section 3.6, not a free panel mode. Stiff-and-heavy and thin-and-lossy are both documented strategies. Choose by computing both against the criterion, not by allegiance.

**Constructions without data.** Patents describe double-wall cabinets with a viscoelastic layer between two MDF skins (Sony, US 5,949,033) and braces split by a damping layer in shear (Stiles, US 7,270,215). Neither gives acoustic data. They show the constructions exist, not that they work.

**Loose coupling is not a specification.** A licensee-built BBC LS3/6 radiated less from its panels because its back-panel battens were loose. The BBC called that "an effective if unconventional method of achieving the same end as damping, but is somewhat difficult to specify!" Do not rely on looseness. It varies from cabinet to cabinet and rattles.

**Decay time.** A resonance decays 30 dB in about `1.1 Q / f` seconds: a 250 Hz panel mode with `Q = 50` takes about 220 ms, and with `Q = 10` about 44 ms.

## 5. Joints

**Glue makes a joint stiff; fasteners do not (Wood Handbook).** "These adhesive joints are much stiffer than mechanically fastened joints, resulting in stiffer panels." Tunay and Tankut found furniture-case rigidity "comes mainly from the gluing of the joining surfaces" (abstract only). Treat screws and nails as clamps for the glue joint, not as the joint (judgement).

**Joints are structural parameters (measured and calibrated).**

- **B&W:** an eigen-analysis of a small panel section gave first modes of 474 Hz with a perfectly rigid joint and 409 Hz once the glue joint was modelled, a drop of 14 %. The glue bead covered only 70 % of the groove sides. A dovetail joint lowered the modes by 2.7 to 5 %.
- **BBC LS3/5A:** Parana pine fillets of "insufficient mechanical impedance" let a chassis resonance colour the sound. Beech fillets lowered the 350 Hz peak by 9 dB, to inaudibility. Because balsa is botanically a hardwood, "it is therefore meaningless merely to call for 'hardwood' fillets."
- **BBC LS3/6:** loose battens changed the panel-output curves and lowered the coupling between panels (section 4).

**Practice that follows.** Specify the fillet and batten species, not "hardwood". Glue every fillet and brace along its full length, and inspect each one before the box is closed. No measurement of the rotational stiffness of loudspeaker joints was found. Keep the pinned-to-clamped band of [materials and panels](cabinet-materials-and-panels.md) section 2 rather than a single edge condition, and give `coupled_cabinet` explicit edge springs when the joint matters.

**Strength is not what limits the joint (worked check, judgement).** A 220 cm² cone at 9 mm excursion in a sealed 20 L box gives 1.4 kPa peak inside, about 120 N per metre of edge on a 0.30 × 0.40 m panel. An 18 mm MDF butt joint that fails in the board's internal bond (0.55 MPa minimum, Medite datasheet) carries about 9.9 kN/m, roughly 80 times more. This ignores resonant amplification, fatigue, drops and transport. Choose joints for stiffness, airtightness, alignment during glue-up and moisture behaviour.

**Joint geometry (Wood Handbook, written for solid wood).**

- Edge-grain to edge-grain bonds "can be as strong as the wood".
- End-grain butt joints "reach only about 25% of the tensile strength of the wood parallel-to-grain", even with special techniques.
- A plain end-to-edge-grain joint cannot carry appreciable load and needs interlocking surfaces. Its moisture movement produces "large internal stresses".
- Tongue-and-groove and other shaped joints "typically do not produce higher strength". Their value is that parts "can be quickly aligned in clamps". Extending that to rebates, housings, biscuits and loose tenons in a sheet-material box is a judgement, but a consistent one: they locate panels.

**Sheet materials.** Particleboard and MDF have dense faces and a weak core. Measured MDF faces are 1.4 to 1.75 times as dense as the core (Dettmer and Smith across five mills; Tor). An edge joint or an edge screw lands in the weakest material. The BBC: "care is necessary in joining the edges to form a cabinet because of the lower density of the inner core." Plywood's cross-banding lets fasteners go "very near the edges" (Wood Handbook).

**Mitres.** A bare mitre is an end-grain joint. In tests of 16 mm MDF and particleboard frame corners glued with PVA, two 8 mm dowels gave the highest bending capacity. A 3 mm plywood spline gave 92 to 98 % of that, and one dowel about 68 % (Derikvand and Eckelman, five specimens per configuration). These are in-plane furniture frames, not box corners, so the numbers transfer only as a ranking.

**Removable panels.** "Compared to a glued joint, the rigidity of a removable panel is somewhat reduced, the mechanical losses are increased and there is some degree of decoupling of the panel from the rest of the cabinet" (KEF). A removable panel is also a leak path: give it a continuous gasket, fasteners close enough to compress it evenly, and threaded inserts for repeated removal (sections 7 and 10).

## 6. Adhesives

**Families (Wood Handbook Table 10-1).**

| Adhesive | Good at | Watch for |
|---|---|---|
| PVA, including aliphatic "yellow" glues | High dry strength, easy use | Low heat and moisture resistance; "joints yield under continued stress" |
| Cross-linkable PVA | Better heat and moisture resistance | Still thermoplastic in most products; check the heat data |
| Polyurethane, one-part | High dry and wet strength; gap-filling | Moisture-curing; isocyanate sensitiser while uncured |
| Epoxy | Bonds wood, metal, glass and plastics; gap-filling; low clamp pressure | Mixed by the user; amine hardeners are skin sensitisers |
| Elastomeric construction adhesive | Bridges gaps up to 6.5 mm | Strength develops over weeks; lower dry strength |
| Contact cement | Instant bond | Much lower strength; creeps under static load |
| Hot melt | Quick handling strength | Low strength; edge-banding use |
| Hide glue | Strong when dry; reversible | Not water resistant |

**Bonding conditions (Wood Handbook).**

- Bond wood at 6 to 14 % moisture content, and keep the difference between mating parts below about 5 % (2 % for dense species).
- Clamp at about 0.7 MPa for low-density wood, up to 1.7 MPa for the densest. An 18 × 400 mm glue face at 0.7 MPa needs 5.0 kN of clamp force, so a box joint needs several clamps or cauls.
- The strongest gluelines for rigid adhesives are 0.08 to 0.15 mm thick. Most wood adhesives do not fill gaps.
- Composite panel surfaces bond poorly. "Lightly sanding with 320-grit sandpaper to cut through the inactivated surface often improves adhesion", and "the internal strength of composites often limits the strength of adhesive bonds."

**Time windows (manufacturer data).** Titebond Original allows 4 to 6 minutes open and 10 to 15 minutes total assembly at 21 °C and 50 % RH. Titebond III allows 8 to 10 and 20 to 25 minutes. Higher temperatures shorten every window. A box with several simultaneous glue lines has to be dry-fitted, and glued in a planned order or in sub-assemblies, inside those windows.

**Wait before flushing.** Water from the glue swells the wood at the joint, and a joint flushed too early later sinks. The Wood Handbook conditions the assembly "for 24 h at 70 °C, 4 days at 50 °C, or 7 days at room temperature before surfacing", and notes that sunken bondlines "become very conspicuous under a high-gloss finish".

**Durability classes.** EN 204 classifies thermoplastic adhesives for non-structural wood use by lap-shear strength after conditioning sequences. From accredited test certificates, D3 requires more than 10, 2 and 8 N/mm² after sequences 1, 3 and 4, and D4 requires at least 10, 4 and 4 N/mm² after sequences 1, 3 and 5. The standard itself was not read, and heat resistance is a separate test (EN 14257, "WATT 91"). A D-class is a moisture rating of a product, not a joint design value.

**Heat.** Titebond's own data (ASTM D905 shear on hard maple) show Original keeping 1600 of 3600 psi (44 %) after a night at 66 °C, and Titebond III keeping 800 of 4000 psi (20 %), with 0 to 10 % wood failure. The Wood Handbook says joints with common adhesives last "indefinitely" below about 15 % wood moisture content at comfortable temperatures, but "some adhesives deteriorate when exposed ... to temperatures greater than 38 °C". **Judgement:** near a plate amplifier, a hot crossover resistor or a sunlit window, use an adhesive whose heat data cover the case, or a thermoset.

**Labels.** "Conforms to ASTM D-4236" is the US art-material health-labelling practice (16 CFR 1500.14), not a strength rating. Strength is ASTM D905. Water resistance is ANSI/HPVA Type I/II or an EN 204 D-class.

**Health.** "Diisocyanates are sensitizers that are capable of causing occupational asthma", and "amine hardeners in some epoxy adhesives are strong skin sensitizers". Solvent vapour can accumulate inside a closed cabinet: "when used in small, unventilated spaces, the solvent can accumulate in the air and cause an explosion if ignited" (Wood Handbook). Follow the product's safety data sheet.

## 7. Fasteners and driver mounting

### 7.1 Screws in sheet materials

**Measured relation (Wood Handbook Eq. 8-12).** Ultimate screw withdrawal from fibreboard and particleboard is `P = K D^0.5 (L − D/3)^1.25 G²`, with `D` the shank diameter and `L` the threaded embedment in mm, `G` the board's specific gravity and `P` in N. For fibreboard `K = 57.3` into the face and `44.3` into the edge, so edge withdrawal is about 77 % of face. A #8 screw (4.17 mm) with 15.9 mm embedment in MDF of `G = 0.72` gives 1718 N face and 1328 N edge (recomputed). Measured edge-to-face ratios: 0.74 to 0.80 across eight mills (Wood Handbook Table 12-6), 0.81 to 1.07 across five (Dettmer and Smith; one mill's edge beat its face), and a manufacturer's guaranteed minimum of 0.60 (Medite).

**The edge's real problems are splitting, stripping and corners.** For a #10 screw in 18 mm MDF, Tor measured stripping torque of 1.2 to 2.7 N·m in the edge against 2.9 to 5.4 N·m in the face. With the best pilot hole (3.2 mm, 93 % of the minor diameter) the edge's stripping-to-seating ratio was only 2.1 to 2.2. Fibreboard splits at edges far more readily than particleboard or plywood. Weyerhaeuser recommends parallel-thread screws made for composite panels rather than wood screws, and a pilot of "at least 90% of the root diameter" for the full screw length. It keeps face screws at least 25 mm and edge screws at least 76 mm from corners. **Judgement:** set a power driver's clutch low and finish edge screws by hand.

### 7.2 Threaded inserts and T-nuts

Drivers come out for service. A wood screw driven again into the same MDF hole works against the low stripping torque of section 7.1, while a machine screw into an insert or T-nut does not re-cut the thread (judgement). The European Technical Assessment ETA-12/0481 for one insert family gives characteristic withdrawal `F = f D l` with `f = 5 N/mm²` "for plywood or MDF". An M5 insert (10 mm outer diameter, 14 mm embedment) comes out at about 700 N and an M6 (12 × 18 mm) at about 1080 N. The ETA's own list of permitted panels names plywood but not MDF, so treat the MDF figure as indicative. Capacity is also limited by bolt-head pull-through and the insert's tension capacity. No non-forum source with T-nut pull-out data in MDF was found.

### 7.3 Tightening

"Screws should be tightened just enough to seal the gasket firmly to the front panel." Over-tightening "forces the frame out of alignment ... just enough to cause the voice coil to rub against the pole pieces" (JBL construction manual). One driver manufacturer specifies 1.6 N·m for its own drivers, tightened in a cross sequence (Dynaudio, read through a page summary only). No source on re-tightening after the wood or gasket creeps was found. Take the torque and sequence from the driver's datasheet where it gives them.

### 7.4 Rigid or decoupled mounting

- **Measured (Jones, Pioneer, preliminary).** A 5 inch driver in a 15 mm MDF box mounted on elastomer grommets cut back and side panel acceleration by more than 20 dB. "Diaphragm motion is minimally affected by de-coupling the drive unit from the cabinet." A sighted mono listening test preferred the decoupled version. One driver, single-point measurements and sighted listening make this preliminary.
- **Where it works (KEF).** "Decoupling provides effective vibration control for midrange drivers, but is not readily achievable for drivers covering the low-frequency range. The very soft materials required would not provide adequate support for the driver." The physics behind that: a compliant mount and the driver mass form a resonance, and isolation works only well above it.
- **Partial decoupling in practice.** The BBC LS3/5A applied PVC edging to the woofer chassis "so as to decouple it somewhat from the front panel". B&W found its soft chassis gasket "responsible for the lower measured frequency of most baffle modes". A gasket is a structural element, not only a seal.

### 7.5 Force cancelling

**Physics.** Two identical drivers rigidly tied together and driven with the same signal put equal and opposite reaction forces on the cabinet, so the net force is only their mismatch. A 1 % force mismatch leaves −40 dB, 5 % leaves −26 dB, 10 % −20 dB, and 5° of phase mismatch −21 dB (derived here). KEF calls it "the most effective technique" for reaction-force radiation, but no measurement of the residual was found. Two drivers mounted on separate flexible panels still drive each panel locally unless the drivers are tied together, which is why KEF says "rigidly coupled".

## 8. Inside the box: standing waves

**The lumped model ends at the first internal mode.** "The electrical analogy ... holds good only at low frequencies below the first internal standing-wave mode" (BBC LS5/8). Leach puts the plane-wave approximation's limit at a box depth below λ/7. Axial modes between parallel walls a distance `L` apart sit at `n c / 2L`:

| Internal dimension | 150 mm | 200 mm | 300 mm | 400 mm | 600 mm | 900 mm |
|---|---|---|---|---|---|---|
| First axial mode | 1150 Hz | 862 Hz | 575 Hz | 431 Hz | 288 Hz | 192 Hz |

**How box modes get out.**

- **They load the cone.** Near a cavity resonance the impedance behind the diaphragm rises and its velocity falls, so the outside response gets a notch. A patent describes measured nulls from cavity modes in a small enclosure (Mitel, US 7,461,718).
- **They push back through the cone.** In the piston band, sound returning from inside moves the whole cone, and the cone radiates that motion forward. The isolation is set by moving mass per area, `20 log10 |1 + j ω m'' / 2ρc|` with `m'' = Mms / Sd`. A 5 inch midrange of 5 g and 85 cm² gives only 8 dB at 500 Hz and 13 dB at 1 kHz. A 6.5 inch woofer of 15 g and 137 cm² gives 13 and 19 dB, and an 8 inch woofer of 30 g and 220 cm² gives 15 and 21 dB (derived here, ignoring the motor's electrical damping). An unabsorbed rear reflection therefore comes back out only 10 to 20 dB below the direct sound in the midrange, enough for a ripple of roughly ±1 to ±3 dB. Linkwitz states the same consequence qualitatively. No peer-reviewed measurement of it was found.
- **They leak out of the port.** The port's inner end samples the local box pressure, so the port radiates the midrange modes as well (section 13).

**Proportions separate modes; they do not remove them.** Manufacturer practice avoids equal or integer-multiple dimensions and extreme ratios. JBL: "no dimension should be more than three times any other dimension." Leach cites the ratio sets 0.8:1.0:1.25 and 0.6:1.0:1.6. Every closed cavity has modes whatever its shape. Splayed walls change their frequencies and shapes, and ESP's guidance is that "acoustic damping material is still needed, no matter how irregular the interior volume." Compute a non-rectangular cavity with the `cavity_modes` finite-volume basis instead of trusting a rule.

**Position matters.** A source excites a mode in proportion to the mode's pressure at the source. Augspurger showed in damped pipes that mounting the driver at one fifth of the pipe length attenuated the fourth harmonic better than other geometric changes. The fractions are for pipes; the principle carries over to boxes.

**Judge stored energy in time as well as in level.** The BBC found an audible coloration near 1.5 kHz that chopped-tone tests resolved into three resonances with `Q` of order 500, about 40 dB below the steady state. These were "irregularities of no more than 0.1 dB on the axial curve". They were cone resonances, not box modes. The lesson is that a smoothed magnitude response does not show everything that matters.

## 9. Lining and fill

### 9.1 Wall lining is a midrange absorber

**Physics.** A porous layer on a rigid wall absorbs where the particle velocity is high, which is away from the wall. "Absorbers need to be about a minimum of a tenth of a wavelength thick to significantly absorb incident sound, and about a quarter of a wavelength to absorb all sound" (NASA TM-2011-216995). A quarter wavelength is 858 mm at 100 Hz, 172 mm at 500 Hz and 86 mm at 1 kHz. Normal-incidence absorption coefficients from the Delany–Bazley model on a rigid backing (derived here):

| Layer | Flow resistivity | 213 Hz | 500 Hz | 1 kHz | 2 kHz |
|---|---|---|---|---|---|
| 25 mm | 5000 Pa·s/m² | 0.05 | 0.15 | 0.31 | 0.57 |
| 25 mm | 10000 Pa·s/m² | 0.03 | 0.16 | 0.39 | 0.74 |
| 50 mm | 5000 Pa·s/m² | 0.12 | 0.39 | 0.74 | 0.94 |
| 50 mm | 10000 Pa·s/m² | 0.13 | 0.50 | 0.89 | 0.99 |

The model is valid only for `0.01 < ρ0 f / σ < 1` (Jiménez et al.). Below that range it gives non-physical values, which is why the table starts at 213 Hz.

**Measured and practised.**

- **BBC LS5/8:** "By using a 30mm layer of low-density mineral wool, almost no damping is obtained at the cabinet resonant frequency (40 Hz), whereas the first mode (213 Hz) is heavily damped." The 213 Hz damping is stronger than the normal-incidence table predicts. Oblique and grazing incidence along the lined walls probably contribute (judgement); the report does not separate the mechanisms.
- **One surface may stay bare.** "At least two reflecting surfaces are required to support standing waves" (BBC), so the LS5/8 left its baffle bare for service access. JBL arranges its lining "so that a padded wall faces an unpadded wall", over at least half the interior surface.
- **BBC LS3/5A:** the 5 L box is lined with polyurethane foam on every surface except the front, 25 mm on top and bottom and 16 mm on sides and back. Its modes are high enough for that thickness. ESP reports a larger box whose foam lining did nothing for its lower modes.
- **IEC 60268-5 measuring enclosure:** it must be airtight and lined to "remove standing waves", with 50 mm of glass wool at 20 kg/m³ in the informative examples.

### 9.2 Volume fill

- **Attenuation per metre.** Bradbury's measurements, seen only as figures redrawn on ESP, show tens of dB per metre through fibrous fill in the 100 Hz to 1 kHz band, rising with frequency and packing density. At equal density, finer fibres attenuate more than twice as much at higher frequencies. A rear reflection that crosses the box and back, 0.5 to 0.8 m, through moderate fill loses some 15 to 40 dB on that path, against a few dB in a bare box (derived here).
- **Materials are alike at matched density (Augspurger, built and measured pipes).** "For roughly equivalent damping, the packing densities of these two materials must differ by a factor of 2 or more." In a 0.61 m pipe, equivalent fills were polyester at 29 g/L, fibreglass at 14.5 g/L and a microfibre at 10.5 g/L. Polyester batches from different makers need not match. "Probably the most important is consistency." Specify the material and its density, then check the result by measurement.
- **Measured flow resistivity of real fills:** about 4300 Pa·s/m² for polyester fibre at 30 kg/m³ (SAPEM 2011) and 2300 Pa·s/m² for a light glass wool (Lafarge et al.). Lighter loudspeaker fills will be lower still. Give `cavity_modes` a measured or datasheet value, not a generic one.

### 9.3 What fill does to the bass

**Physics with measurements.** Fill that exchanges heat with the air moves the compression from adiabatic toward isothermal. That raises the apparent volume by at most the ratio of specific heats, 40 %. Leach's model gives 31 % for uncompressed fibreglass (recomputed: 1.306). His published correction puts the upper limit of isothermal behaviour for that fill at 257 Hz, not 6.4 kHz, so the gain varies across a woofer's band. Lafarge et al. measured a light glass wool's transition near 200 Hz. Small, who measured systems: "The maximum theoretical increase in compliance is 40%, but using practical materials the actual increase is probably never more than about 25%." Fill also adds moving mass, "from negligible proportions to as much as 20%", and loss: unfilled systems have `QMC` of about 5 to 10, filled ones 2 to 5. Small gives the measurement method for a real box (his Eq. 53, from the closed-box resonance and `Q` with and without fill). A JBL owner's manual tells installers who leave out 25 mm of wall lining to make the box 10 % larger (manufacturer rule of thumb).

**Placement.** Losses from fill "can be substantial, especially if the filling material is relatively dense and is allowed to be quite close to the driver where the air particle velocity and displacement are highest" (Small). In a vented box, wall linings bring the absorption `QA` to 30 to 80 against 100 or more unlined. An unobstructed vent has `QP` of 50 to 100, which grille cloth or lining over it lowers "considerably", though "with reasonable care in design" not below 20 (Small). Fasten fill "so as not to be drawn toward the port by the air flow", and leave it out near the port end if necessary (JBL). Keeping fill off the cone and away from vented pole pieces is judgement; no source quantifies it.

**Fixing.** Bag mineral wool to keep fibres in. The BBC used 100-gauge polyethylene bags, which did "not significantly effect the absorption coefficient" from 40 Hz to 3 kHz. A nonwoven facing with paint tripled a polyester sample's flow resistance and changed its absorption (SAPEM 2011), so a facing is not automatically transparent. Attach linings with glue spots, tacks or staples (JBL). Damping materials must be "very well bonded to the interior of the treated panels so it cannot move, rattle or fall off" (ESP). A 1965 magazine design that used long-fibre wool told builders to mothproof it.

## 10. Airtightness, leaks and rattles

**Leakage is usually the largest loss (Small, measured).** "Leakage losses are usually the most significant, giving QL values of between 5 and 20." "Some of the more serious leaks were traced to the drivers. These leaks were caused by imperfect gasket seals and/or by leakage of air through a porous dust cap and past the voice coil." The `lf_box` default `QL = 10` sits in that range; a real box's figure is measured, not assumed.

**A leak scales as the cube of the gap.** A slit's flow resistance is `R = 12 μ L / (w h³)`. For a 100 mm long seam through 18 mm of panel in a 20 L box tuned to 40 Hz, `QL` is about 1400 at a 0.1 mm gap, 175 at 0.2 mm, 52 at 0.3 mm and 11 at 0.5 mm (derived here; laminar model). One unglued half-millimetre seam is enough to produce a typical measured `QL`.

**Leaks also make noise.** "An accumulation of small air leaks can affect performance significantly and they can introduce objectionable whistles or hisses" (JBL). The BBC sealed the LS3/5A "so as to prevent air leaks which could give rise to extraneous noises resulting from the high sound pressures produced inside the cabinet; even screw holes are made air tight."

**Where leaks are.** Glue joints, the driver flange gasket, porous dust caps, terminal cups and plates, wire holes ("make sure that the wires fit snugly in the holes, otherwise a 'whistling' or 'hissing' sound may occur", JBL), the port tube's fit in its hole, screw holes, removable panels, and passages between chambers. JBL's automotive manual seals every interior joint with caulk.

**How production finds them.** Klippel's air-leak detection drives a sine tone below the system resonance, high enough to force air through the leaks. It detects the leak noise by demodulation, because the noise is turbulent and "amplitude-modulated" by the sound pressure. For vented systems "it is recommended to seal the port during ALD measurement ... make sure that port sealing itself is not leaking." "Leak noise mainly contains high frequency components which are shadowed by any obstacle", so large objects need several microphones, or a microphone scanned over the surface. A leaky dust cap shows up as a changed `Qms`. **A builder's adaptation (judgement, not a published procedure):** plug the port, play a sine below the box resonance at a level the driver tolerates, and listen or place a microphone along every seam, the flange, the terminal and the wire passes. Do it before the last panel is glued, and again before finishing.

**Rattles.** Klippel separates "deterministic (strictly periodic) Rub&Buzz distortion as caused by hard limiting or loose wires" from "impulsive distortion which happens sporadically (e.g. caused by loose particles)". "All internal wiring has to be secured properly to prevent rattling as well, because it can be very difficult to correct after the box is sealed up" (ESP). The BBC stopped the LS3/5A crossover board resonating "by means of a thick felt pad, placed between the board and the unit". Board placement and fixing are in [crossover assembly](crossover-assembly.md).

## 11. Separate chambers

**Practice (BBC LS5/5).** The midrange's rear was "confined in a small enclosure" to avoid interaction "with the cabinet vent resonance". "It is necessary to enclose the rear to prevent it acting as a vent at low frequencies."

**Why (derived here).** The 780 Pa that an 8 inch woofer makes at 5 mm in 20 L puts 6.6 N on an 85 cm² midrange cone sharing that air. That is a static excursion of 3 to 8 mm for an assumed suspension compliance of 0.5 to 1.2 mm/N, at bass frequencies, at or beyond the midrange's `Xmax`.

**Seal the wire passes between chambers.** A hole through an 18 mm partition into a rigid 2 L midrange chamber forms a Helmholtz low-pass. Its corner is about 23 Hz for a 3 mm hole, 43 Hz for 6 mm and 67 Hz for 10 mm (derived here). Below that corner the midrange chamber follows the woofer chamber's pressure, which is exactly where woofer excursion is largest.

**The chamber has its own modes.** A midrange chamber 150 to 300 mm deep has its first axial mode at 575 to 1150 Hz, inside the midrange band, and a light midrange cone passes that sound back out only about 8 to 15 dB down (section 8). Line or fill it. Tapered "tube" midrange chambers are documented here only through bass-pipe measurements (Augspurger) and manufacturers' descriptions. Model them before relying on the shape.

**Open-back drivers.** Any tweeter, ribbon or midrange whose rear opens into the woofer chamber is driven by that chamber's pressure. Give it a sealed rear chamber, or confirm that its own back is sealed.

## 12. The driver cutout and what is behind the driver

**Rear chamfer (one designer's measurements).** Gravesen measured a 4.5 inch class driver flush-mounted in a 44 mm baffle, a 22 mm baffle and a 22 mm baffle with a 45° rear chamfer. The responses differed by about 1 dB between 300 Hz and 1.5 kHz, with no visible change in cumulative spectral decay, step response or distortion. A 5 inch class driver in a deep 48 mm straight hole showed a dip and peak of about ±2 dB between 600 Hz and 1 kHz, which a 45° chamfer removed. Another designer chamfers every baffle opening "for smooth airflow" (Zaph Audio). No driver manufacturer's mounting instruction on rear chamfers was found. **Physics, unquantified:** a deep narrow hole behind the cone adds air mass and a short duct with its own resonance, so the effect grows with baffle thickness relative to the opening and with small drivers whose frame windows are small. **Judgement:** chamfer or relieve the rear of the cutout when the baffle is thick relative to the driver, keep the screw lands and the frame's support intact, and do not treat a 45° angle as a rule.

**Structural cost.** Material removed around the cutout is removed from the reaction-force path into the baffle. No measurement of that loss was found; see the judgement on holes in [cabinet geometry](cabinet-geometry.md).

**Clearance behind the magnet and pole vent.** No source gives a figure. **Geometry:** air leaving a vent of diameter `D` toward a wall at distance `h` passes through a curtain of area `π D h`. That equals the vent's own area at `h = D/4`, and is four times it at `h = D`. Treat `h ≥ D/2` to `D` as a judgement grounded in that arithmetic, not as a published rule.

## 13. Ports as built objects

**Edges and flares (Salvatti, Devantier and Button, JBL/Infinity, measured).**

- "A well rounded entrance (radius = 0.2 x diameter) yields a very low 5% loss, while a sharp entrance asymptotically reaches 50% loss." Their design rule "requires all port edges to have a blend radius of at least 20% of the minimum diameter", which `lf_box` checks as `edge_radius_mm`.
- A normalised flare rate near 0.5 is the best compromise across levels. Maximally radiused ports are best at low level but compress and shift tuning at high level.
- "Roughening the port walls generally does not appear to be beneficial in the normal operating range."
- They report Backman's finding that "forcing the air to make any kind of turn will cause turbulence to occur at lower levels". That bears on elbows, and on a duct end that discharges against a nearby surface.

**Flare accuracy is a build tolerance (Bezzola, Samsung, conference paper with blind listening tests).** Optimally flared ports could be played "1 to 3 dB louder than slightly under- or over-flared ports, and 10 to 16 dB louder than straight unflared ports" before port noise became audible. "For ports with nominal Dc of 60 mm, a 2-mm (3.3%) change in central diameter results in performance hits of 0.8 to 3 dB." Drawings must carry the flare profile and its tolerance, not only "flared".

**Pipe resonances.** A port tube is open at both ends, so its first longitudinal resonance is near `c / 2L` plus end corrections: about 1.3 kHz for 100 mm × 50 mm, 710 Hz for 200 × 70 mm and 480 Hz for 300 × 100 mm (derived here). "When the port eigenfrequencies get excited by flow separation and vortex shedding, they are very audible to the human ear, because they are outside the spectral masking bandwidth of the nominal port operating frequencies" (Bezzola). KEF markets a flexible port wall to radiate this energy (patent US 9,143,847; no data published). Two things excite a pipe resonance. The box pressure at that frequency is one, and the crossover and the lining reduce it. Vortex shedding at high port velocity is the other, and neither reduces it; generous edge radii and a correct flare delay it.

**Construction practice (JBL).**

- "Port material can be anything rigid, e.g. cardboard carpet tube." The construction manual accepts cardboard with a wall thicker than 1/16 inch (1.6 mm).
- Using the box walls as sides of a slot duct "will cause an alteration in the expected tuning", so leave length adjustment possible after assembly.
- Several small tubes tune lower than one tube of the same total area.
- "The tube or tunnel must fit snugly into its receptacle on the baffle panel so that no air leakage occurs around its outer edge."
- Measure the actual tuning at the impedance minimum between the two peaks.

**End clearance.** JBL documents give both "about twice the port dimension" (a 1985 engineering note) and "one port diameter" (an automotive manual). No measured threshold was found. The curtain-area arithmetic of section 12 is the reason behind the practice, and [cabinet geometry](cabinet-geometry.md) holds the occupancy rule.

## 14. Outside details that diffract

The edge physics, the baffle step and driver-to-edge distances are in [baffle and driver placement](baffle-and-driver-placement.md). This section covers the built details that add diffraction sources of their own.

**What sets the size.** An edge diffracts in proportion to how much sound reaches it. Holland's model scales the whole diffracted field by the piston's directivity at 90°, with each edge element re-radiating with inverted polarity (the paper notes no experimental verification yet). KEF's simulation shows the consequence on a 20 cm cube. A 25 mm piston gives a peak and dip about 6 to 7 dB apart with the first dip near 3 kHz, while a 160 mm piston is smooth above 2 kHz. A dome on a flat baffle "fully 'illuminates' the edges" (manufacturer). So any discontinuity near a tweeter matters far more than the same discontinuity near a woofer. A discontinuity at distance `r` from the source gives its first peak near `c / 2r` and its first dip near `c / r`.

**Shape at large scale (Olson, measured).** With a small source, the outside shape alone changed the axial response by more than 10 dB. A 2 × 3 ft box with the source off centre still rippled about ±3 dB between 300 Hz and 4 kHz. The same family with 152 mm, 45° bevels on three sides of the front stayed within about ±1 dB (figure readings). Olson's remedy is "eliminating all sharp boundaries on the front portion of the enclosure" and "making the distances from the mechanism to the diffracting edges varied". His bevel was about an eighth of a wavelength at 280 Hz. On a real two-way with a 295 × 180 mm baffle, mounting it flush in a 3 m baffle showed edge effects of "almost 3dB" between 1 and 4 kHz (Howard, *Stereophile*, measured).

**Edge radius and chamfers as built.** A radius acts only above about `c / 8r`:

| Radius | 6 mm | 12 mm | 19 mm | 25 mm | 50 mm | 150 mm |
|---|---|---|---|---|---|---|
| Acts above about | 7.1 kHz | 3.6 kHz | 2.3 kHz | 1.7 kHz | 860 Hz | 290 Hz |

"The radius necessary to have a real benefit is very large, at least 50 mm or more. Smaller radii have very little effect, and only at very high frequencies. Most manufacturers have utilized radii on the order of 6 mm or less" (Sony patent US 5,731,555, the inventor's view). One practitioner agrees that small roundovers "do help, but are of limited benefit" (Ralph). This independently supports Linkwitz's one-eighth-wavelength rule in the placement reference. No measured or BEM comparison of several radii on one cabinet was found, so the rule is agreed judgement backed by physics, not a measured threshold. **Consequence for construction:** a router roundover is for handling and appearance. An acoustically useful radius is a design dimension. It needs solid material at least as deep as the radius at the corner (laminated blocks or solid timber at the edges; one practitioner notes that baffle thickness limits the edge geometry), and it changes the effective baffle width, the cut list and `baffle_diffraction`'s `edge_radius_mm`.

**Flush mounting and proud flanges (practitioner measurements).**

- **Round tweeter faceplates.** A 100 mm round tweeter faceplate standing 3.2 mm proud gave about +2.5 dB near 3.5 kHz and −2.5 dB near 7 kHz against flush mounting (Zaph Audio, on-axis). Those frequencies are what an equal-distance circular edge 50 mm from the dome predicts. "Never, ever surface mount a 4" flange tweeter."
- **Small flanges and woofers.** A 2 inch square flange gave only about −1.5 dB near 8 kHz, and a surface-mounted woofer flange was "not so bad".
- **Recess depth.** In an automotive tweeter recess, a finite-element model found 2 mm of extra depth raised the response by about 1 dB at 4.5 kHz, which the thesis attributes to the recess acting like a small horn (Chalmers MSc thesis, validated against anechoic measurement to about 1 dB below 6 kHz). That evidence is for a cavity, not a flat baffle.
- **Other details.** KEF made its woofers "as low profile as possible" and moved its ports to the rear partly "to minimise the diffraction" (manufacturer). Grille-frame mounts and screw heads are named as diffraction sources in the Sony patent, but no magnitudes were found for them, for trim rings, logos and controls, or for the gap between a flange and its recess.
- **Practice:** flush-mount tweeters and any round faceplate near them. Machine the recess to the faceplate's measured depth plus the compressed gasket (construction audit). Keep fasteners, trim and fittings away from the tweeter (judgement).

**Waveguides and the baffle.** KEF's "Shadow Flare", a shallow waveguide that "smoothly blends the Uni-Q driver into the baffle", took the tweeter's plotted ripple from about ±2 dB to about ±0.5 dB (manufacturer; whether measured or simulated is not stated). Make a waveguide's mouth flush with the baffle and blend it in without a step. Waveguide design itself is in [horn and waveguide design](horn-and-waveguide-design.md).

**Felt around the tweeter.**

- **Thick wool felt (measured).** Half-inch wool felt on one stepped baffle changed the tweeter-axis response by "±3dB or more" (Ralph, *audioXpress*, on-axis only, no listening test). His placement rules are judgement: a strip between the tweeter and the next driver, no round opening centred on the tweeter, and nothing closer than about 38 mm to the tweeter centre.
- **Thin pads (patent counter-view).** The Sony patent counters that typical pads under 6 mm "are only effective at higher frequencies (above 5 kHz)". The tenth-wavelength rule of section 9.1 is consistent with both views: about 5.7 kHz for 6 mm and 2.7 kHz for 12.7 mm.
- **Gaps.** No attenuation data at grazing incidence, which is how sound crosses a baffle, was found. Acoustic Research measured edge and baffle reflections and presented a suppression technique (Kates, *JAES* 1979; abstract only).

**Grilles.**

- **Frames.** A 12 mm MDF grille frame close to the tweeter cut a notch of about 11 dB near 6.4 kHz (Audioholics, measured). Thin frames and perforated grilles changed the response by roughly ±1 to 4 dB, mostly above 4 kHz (*Stereophile* and NRC/SoundStage! measurements, read off published plots). A frame is an edge source like any other. Keep it thin, with rounded or chamfered inner edges, flush to the baffle and as far from the tweeter as the design allows (judgement grounded in the edge physics above).
- **Perforated sheet (physics).** A perforated sheet acts as a limp mass of air in its holes, `m = ρ0 (t + 0.8 d) / σ` for thickness `t`, hole diameter `d` and open fraction `σ` (Elliott, Holland and Newell; the same end correction as Schultz's perforated-metal data). It is a first-order low-pass with `f−3dB = 2 ρ0 c / (2π m)`, and what it does not transmit it reflects back toward the baffle, which adds comb filtering. Normal-incidence estimates, derived here: 23 % open, 3.2 mm holes, 1 mm sheet, −3 dB at 7.1 kHz and about −5 dB at 10 kHz; 46 % open, 2 mm holes, 1 mm sheet, −3 dB at 19 kHz and about −1 dB at 10 kHz; 60 % open, 2 mm holes, 0.8 mm sheet, about −0.6 dB at 10 kHz. A dome a few millimetres behind a grille is in the near field, so treat these as orders of magnitude. The one peer-reviewed grille study found (Kılıçkaya and Erol, abstract only) recommends a grille "as thin as possible, considering mechanical strength" with an openness of "50% or higher".
- **Cloth.** No measured insertion loss of loudspeaker grille cloth was found. Toole describes grille cloth as so open "that you can easily see through" it, which implies low flow resistance and low loss, but gives no numbers.
- **Grille on or off is a design decision.** Dynaudio tunes its loudspeakers "without the grille on" (manufacturer). One Paradigm model measured flatter with its grille fitted, and removing it added a peak of almost 5 dB just below 4 kHz: "Do not listen to this speaker with its grille removed" (*Stereophile*). State which condition the crossover is voiced for, predict in that condition, and put the grille's fixing (magnets, pins, a frame) in the drawings.

**Audibility is not settled.**

- Toole excludes on-axis diffraction artefacts from the directivity index because they "can have no consequential effects in real listening circumstances".
- Peaks are "far more audible than equivalent valleys or dips" (Bücklein, abstract).
- Comb filtering from a perforated screen in front of a loudspeaker was "at worst, barely audible" in ABX tests with 20 subjects (Elliott, Holland and Newell).
- A delayed copy arriving from the same direction colours the sound most (Moulin and Corteel, sound-reinforcement tests). Edge sources arrive from almost the same direction as the driver; applying that result to edges is an inference.
- Acoustic Research's reported listening improvements from its baffle absorber are known only second-hand.

No grille on/off listening test was found. Predict these details, keep them tidy and say what they do; do not claim an audible benefit.

## 15. Floor, stands and feet

**Spikes are springs (B&W, measured).** On its spikes a B&W floorstander showed rigid-body acceleration peaks below 90 Hz, the spikes "acting like springs". Left and right side measurements "differ by up to 15dB" below 100 Hz, because the 1 mm spherical spike tips did not make a consistent contact with the floor.

**Isolation against rigid coupling (one controlled study, reported by a magazine).** Katz measured a pair of floorstanding loudspeakers on a suspended wooden floor, on isolators and on hard-oak blocks of the same form. With isolators the cabinet base vibrated about 20 dB more near 200 Hz and about 8 dB less at 1 kHz. The floor vibrated 5 to 8 dB less, but more below about 60 Hz. At the listening position the differences "were modest and inconsistent between the L and R loudspeakers." The AES paper itself was not read.

**Physics.** A cabinet on any support is a mass on a spring. Well above the mount resonance the cabinet is mass-controlled and passes little force to the floor. A rigid mount adds the floor's mass and stiffness to the cabinet's, so the cabinet moves less and the floor moves more. Katz's data fit both halves. "Draining energy" into the floor is not a separate mechanism. KEF suggests "a high mass stand, preferably sand filled" to control rigid-body motion (manufacturer judgement).

**Doppler from baffle motion is tiny.** One micrometre of baffle motion modulating a 10 kHz tone gives sidebands near −81 dB, and 10 µm about −61 dB (derived here). A claim that baffle vibration audibly modulates the tweeter needs its own measurement.

## 16. Materials as built

The elastic and damping data are in [materials and panels](cabinet-materials-and-panels.md). These are the properties that matter at the bench.

**MDF (manufacturer datasheet and measured).**

- **Datasheet minima (Medite Premier, EN test methods):** thickness ±0.15 mm; moisture content 5 to 9 %; 24-hour thickness swell at most 9 %; dimensional movement 0.30 % in length and width; internal bond at least 0.55 N/mm²; screw holding at least 1000 N face and 600 N edge.
- **Moisture-resistant grades** swell less in water (at most 7 %), but their length and width movement is the same 0.30 %.
- **Wax** "has practically no effect on water vapor sorption or dimensional changes associated with changes in humidity" (Wood Handbook).
- **Measured across five mills:** linear expansion of 0.16 to 0.27 % from 50 to 90 % RH; none met the recommended internal bond (Dettmer and Smith).
- **Conditioning:** "should be conditioned to the final environment for two to three days before cutting" (Medite); unitised panels can take up to 7 days to acclimate (Weyerhaeuser).

**Birch plywood (Handbook of Finnish Plywood).**

- **Thickness:** nominal 18 mm is 17.1 to 18.7 mm under EN 315 (17.1 to 18.1 from Finnish mills), so cut housings and rebates to measured stock.
- **Density:** about 680 kg/m³.
- **Movement:** in-plane 0.015 % per 1 % change in moisture content, and 0.3 to 0.4 % per 1 % in thickness.
- **Glue:** phenolic, to EN 314-2 class 3.
- **Voids:** "plywood can be ordered with a solid core and face veneers" where voids matter (Wood Handbook).

Hot-pressed panels sit at a lower equilibrium moisture content than solid wood at the same humidity; the Wood Handbook recommends conditioning them at 30 to 40 % RH for interior use.

**Formaldehyde.** US TSCA Title VI limits are 0.05 ppm for hardwood plywood, 0.11 ppm for MDF, 0.13 ppm for thin MDF and 0.09 ppm for particleboard. European E1 board releases less than 0.1 ppm (HSE). The test methods differ, so do not compare the numbers directly. Cured phenol-formaldehyde, the exterior plywood glue, releases no detectable formaldehyde (Wood Handbook).

**Solid wood moves.** Within 6 to 14 % moisture content, `ΔD = D C (M_final − M_initial)` with the tangential coefficient for flat-sawn width and the radial one for quarter-sawn (Wood Handbook Eq. 13-3, Table 13-5).

- **Worked example (recomputed):** a 300 mm white oak panel going from 6 to 11 % moisture content moves 5.64 mm flat-sawn and 2.91 mm quarter-sawn. At 21 °C, 30 % RH gives about 6.2 % equilibrium moisture content and 65 % RH about 12.0 %, so the same flat-sawn panel moves about 6.5 mm across that range.
- **Comparison:** about 0.5 to 0.9 mm for MDF and 0.2 mm for birch plywood of the same width.
- **Variability:** individual boards scatter with a coefficient of variation of about 15 %. Within a timber type the BBC measured a factor of four in elastic modulus, "a variation of 12 dB in height of a resonance peak".

**Solid-wood construction rules (Wood Handbook).** Large solid panels must be "free to move across the grain", and mitred trim should be "glued and splined". Short grain fails across the fibres: white oak's modulus of rupture is about 19 times its tensile strength perpendicular to the grain. Decide the grain direction, the joint type (long grain or end grain), the captured panels' float gaps and any short-grain lips together, and size the gaps from the movement calculation rather than copying another design.

**Balanced construction and finishes.**

- "Warping in overlaid panels is almost always caused by differences in shrinkage or swelling from one side of the panel to the other" (Wu, LSU AgCenter). Veneer both faces with matching material, and finish both faces.
- "Finishes cannot change the EMC of wood; they only slow down the rate of water entering and leaving the wood" (Wood Handbook). Panel edges contain end grain and are "especially vulnerable to absorption of water", so seal them.
- MDF edges are more porous than faces. Sand, seal or fill them, then prime and topcoat (Medite, Weyerhaeuser).
- No measurement of a finish's effect on cabinet sound was found. A 0.1 mm film adds about 0.9 % mass per coated face to 18 mm MDF (derived here). The finish's job is moisture and appearance; do not claim an acoustic effect for it.

## 17. How much is enough: audibility

**The cabinet-specific criterion** is the BBC's, reproduced with its limits in [materials and panels](cabinet-materials-and-panels.md) section 3: about −13 dB relative to the direct sound at 100 Hz, falling to about −30 dB at 400 Hz and flat to 10 kHz. It remains the only published acceptance threshold found. ESP's author, who built an accelerometer for testing cabinets, wrote: "I haven't been able to determine what level may become audible in its own right." The BBC report also states that audibility "is related to its decay period", with timber's most audible resonances "towards the lower end of the band". That sits uneasily with the criterion's leniency at low frequency. The criterion is the empirical result to use.

**General resonance thresholds (secondary summary of Fryer and of Toole and Olive).** For a resonance added in parallel with the signal, which is how a panel radiates, the threshold in pink noise is lowest at `Q = 1`, "a value from -29dB to -23dB", and rises about 3 dB per doubling of `Q`. "Resonances with Q>50 are more audible with transient signals while resonances with Q<10 are more audible with continuous complex signals." Toole's later summary: "it is the spectral bump that is the most reliable indicator of audibility", and early reflections lower the thresholds. A study of 63 to 500 Hz (Olive et al. 1997, seen only through Fazenda et al.) reportedly found pink-noise thresholds falling as `Q` rises, the opposite trend. Record both; the original papers are paywalled and were not read.

**Consequence.** A broad, low-`Q` panel output around −25 dB relative to the direct sound can be audible. That is consistent with the BBC's −30 dB midband line. Lowering `Q` with damping lowers the panel's peak level but broadens it, and a broad resonance is detected at a lower level than a narrow one. Judge treatment against the criterion, not against `Q` alone (judgement).

## 18. Checking the built cabinet

Everything this framework produces is predicted. These are the methods the sources use to measure a built cabinet, so the construction document can say what a builder's verification would involve.

- **BBC pressure-gradient method.** A figure-of-eight microphone about 25 mm from the panel centre with its null toward the cone, with the proximity bass rise compensated, compared against the criterion. "The test is therefore most rigorous for the frequencies where the phase variation across the panels is fairly small."
- **Accelerometers.** Stereophile tapes a PVDF film accelerometer to a panel and reads a cumulative spectral decay in relative levels, cross-checked against wrinkles in the impedance curve. Researchers use low-mass accelerometers (0.65 g and 0.75 g in the studies above). Sensor mass limits use on light structures, and one central point shows only the low-order modes. "It's not trivial to assess performances of a cabinet in terms of radiated sound solely by looking at the vibration pattern because of complex phase relationships" (B&W).
- **Laser vibrometry with BEM or reciprocity** gives each panel's pressure at a listening point. The scan spacing must be at most half the shorter of the bending and acoustic wavelengths (Alavi and Holland).
- **Pressing a panel with a finger** is neither a damping treatment nor a test of one. An inference that damping layers do nothing because finger pressure did not move a measured peak is not supported (section 21).
- **Bass parameters.** Measure the actual port tuning at the impedance minimum, the fill's effect with Small's with-and-without method, and `QL` from the impedance. Run a leak test (section 10).

## 19. Making the sequence buildable

**Practice, in order, with the reason for each step.**

1. **Condition the materials and measure them.** Condition sheet goods in the room they will live in (section 16). Build solid wood at the moisture content it will see in service: for interior use the Wood Handbook recommends 8 % (pieces 6 to 10 %) for most of the United States, 6 % for the dry southwest and 11 % for damp coastal areas. Translate that to the local climate with its humidity-to-moisture table. Measure the actual sheet thickness and cut every housing and rebate to it. Keep one batch per cabinet (judgement).
2. **Machine every panel against its own datum**, with the loose-panel IDs and drawings of the construction audit. A driver cutout, its rebate depth (including the compressed gasket) and its rear relief are all machined before assembly.
3. **Dry-fit the whole box.** Check the glue-up order against the adhesive's open time, the clamp force and the clamp access. Check squareness by diagonals: for a 400 × 300 mm frame, 0.1° out of square shows as 0.84 mm difference between diagonals (derived here). Equal diagonals prove a rectangle only if opposite sides are equal and the frame is not twisted.
4. **Glue braces, fillets and partitions along their full length** and inspect them before the next panel hides them. Plan how angled partitions, braces and lining go in before the box closes.
5. **Seal from the inside** every joint, wire pass, terminal and port fit, and every passage between chambers.
6. **Fix everything that could rattle.** Tie the wiring down, bond or bag the lining, keep fill off the cone and the port ends, and mount the crossover board so it cannot resonate (the BBC used a thick felt pad) in a place that leaves service access.
7. **Leak-test and listen for rattles** before the last panel is glued, and again before finishing (section 10).
8. **Wait before flushing joints** (7 days at room temperature for water-based glue), then finish all faces and seal the edges.
9. **Mount the drivers** on their gaskets into inserts or T-nuts, tightened in a cross pattern just enough to seal, with the driver's specified torque where one is published.
10. **Keep service access.** Provide a removable panel or reach through a driver opening to the crossover and terminals, and show the space needed to remove each serviceable part.

**Engineering judgement.** One geometry record should produce the loose-panel machining sheets, the joint sections, the installed clearances and the simulation domains (`assembly_geometry`). Specify gasket compression and sealing faces. Keep driver basket vents unobstructed and allow for driver motion. Compare alternative joints and materials only within the tools and methods the brief permits. Put the selected dimensions and margins in the package instead of leaving geometry decisions to the builder.

## 20. Workshop safety and handling

**Wood dust (UK HSE WIS23).**

- All wood dust can cause asthma, dermatitis and irritation, and hardwood dust can cause nasal cancer.
- The GB workplace limits are 3 mg/m³ for hardwood and 5 mg/m³ for softwood (8-hour averages). For mixtures the hardwood limit applies, and exposure must be reduced as low as reasonably practicable even below the limit.
- The highest exposures come from sawing, routing, sanding, blowing dust with compressed air and dry sweeping.
- **Controls:** local exhaust extraction; respiratory protection with an assigned protection factor of at least 20 ("often described as FFP3"), fit-tested; and cleaning with at least an M-class vacuum. "Nuisance dust masks do not filter out wood particles and hence provide no protection against wood dust."

**Classification and other limits.**

- "Wood dust is known to be a human carcinogen" (US National Toxicology Program), with the strongest evidence for nasal and sinus adenocarcinoma.
- NIOSH recommends 1 mg/m³. The EU hardwood limit is 2 mg/m³ from 2023 (Directive 2017/2398).

**MDF (HSE, archived guidance).** Machining MDF produces "a mixture of softwood dust and hardwood dust (if it is present)", plus formaldehyde. Where hardwood is present, the hardwood limit applies to the whole mixture. The formaldehyde limit is 2.5 mg/m³ (2 ppm), and in E1 board free formaldehyde is "thought to be insignificant". "Do not use nuisance dust masks, FFP1 or FFP2."

**Adhesives** are covered in section 6.

**Lifting (HSE INDG143).** The risk filter for a load held close to the body between knuckle and elbow height is 25 kg for men and 16 kg for women, and lower at other heights and reaches. "The Manual Handling Regulations do not set specific weight limits, so the guidelines are not 'safe limits'." A shell of 18 mm MDF measuring 250 × 400 × 300 mm outside already weighs about 6.8 kg before drivers, bracing and damping (derived here at 720 kg/m³). Compute the finished mass and say in the documents how the cabinet is lifted.

## 21. Claims checked and not supported

Recorded so that they are not reintroduced from the same popular sources.

- **"Stiffer is always better; push every resonance above X Hz."** Contradicted by KEF, Bastyr and Capone, the Aalborg/DALI study and the BBC thick-wall cabinet (section 3.4). A threshold such as "above 1.5 kHz no energy is available" is a judgement.
- **"Damping layers or mass on the panels do nothing; only bracing works."** Contradicted by the BBC's measured loss factors (`Q` 70 to 7), its beam data and KEF's damped bracing (section 4).
- **"Panels are driven mainly by the box pressure"**, and the reverse. Neither is general (section 2).
- **"Cabinet radiation is negligible."** Contradicted by Bastyr and Capone, B&W and Alavi and Holland. The supporting study was limited by its noise floor (section 2).
- **"Use hardwood fillets."** Meaningless as a specification; the species changed a panel peak by 9 dB (section 5).
- **"A shaped joint is stronger because it has more glue area."** The Wood Handbook says it typically is not; its value is alignment (section 5).
- **"Screws in MDF edges hold nothing."** Edge withdrawal is 60 to 107 % of face in the data found. The real limits are splitting, stripping torque and corner distance (section 7.1).
- **"Moisture-resistant MDF does not move."** It swells less in water but moves the same 0.30 % with humidity (section 16).
- **"Finishing stops wood movement" and "the finish changes the sound."** Finishes only slow moisture exchange, and no acoustic evidence was found (section 16).
- **"Fill makes the box act 20 to 40 % larger."** 40 % is the ceiling. Small judged practical gains at no more than about 25 %, and the gain is frequency dependent (section 9.3).
- **"Non-parallel walls eliminate standing waves."** They change the modes; damping is still needed (section 8).
- **"Line the walls and the box modes are handled."** Thin linings do little below a few hundred hertz (section 9.1).
- **"A small leak does not matter."** One unglued half-millimetre seam gives a typical measured `QL`, and leaks whistle (section 10).
- **"Always chamfer the cutout at 45°."** The only measurements show about 1 dB in typical cases and more for deep holes (section 12).
- **"Port ends must be exactly one diameter from a wall."** JBL's own documents give one and two diameters, and no threshold was measured (section 13).
- **"Dimpled or roughened port walls reduce noise."** Not beneficial in the normal range (section 13).
- **"A 19 mm roundover fixes baffle diffraction."** It acts only above about 2.3 kHz, while the first edge peak and dip of a typical bookshelf baffle sit around 1 to 3 kHz. Olson's successful bevels were 152 mm (section 14).
- **"Perforated metal grilles are transparent."** Only when thin and at least about 50 % open; a 23 % open sheet loses about 5 dB at 10 kHz by the mass model (section 14).
- **"Always listen with the grille off."** It depends on whether the speaker was voiced with it (section 14).
- **"Felt around the tweeter cures diffraction"**, and **"diffraction ripple is inaudible"**. Neither is established; thin felt acts only at high frequencies, and the listening evidence is indirect (section 14).
- **"Spikes drain energy into the floor."** Spikes are springs, and coupling makes the floor move more (section 15).
- **"Decoupling a driver smears transients."** The one measurement found shows unchanged cone motion and more than 20 dB less panel vibration (section 7.4).
- **"Conforms to ASTM D-4236" means a strong glue.** It is a health-labelling statement (section 6).

## 22. What the framework models

- **`assembly_geometry`** records solids, air regions, porous regions and fabrication data (joints, machining, treatments) in one coordinate frame. It reports intersections; it does not judge a joint or infer a machining allowance.
- **`plate_structure`** screens isolated bays as simply supported plates, with brace lines as ideal supports and rigid joints. It has no joint compliance, no fluid coupling and no apertures. A shallow brace (section 3.2), a braced panel below the global-to-local transition (section 3.3) and a partly glued joint (section 5) all make it optimistic.
- **`coupled_cabinet`** couples panels, cavity and exterior with declared edge rotational springs and attached masses. Use it when joint restraint, the driver's mass on the baffle or the panel–air coupling decides a choice. It does not model apertures, multilayer shear or arbitrary brace compliance. A real wooden cabinet's measured modes sat 10 to 20 % below a careful FE model in B&W's study, so treat the frequencies as a band.
- **`cavity_modes`** models lining as a damping admittance on a rigidly backed layer (Miki's model, from its flow resistivity), plus brace windows and port tubes in the finite-volume basis. Miki's model is stated valid for `0.01 < f / σ < 1` (Jiménez et al.), close to the Delany–Bazley range of section 9.1: above 100 Hz at `σ = 10000` and above about 40 Hz at 4000. The app states that it "is not a model of bulk stuffing filling the box". Neither app models the compliance gain from volume fill: enter the net volume you are claiming in `lf_box`, and say in the notes what fill gain is assumed.
- **`lf_box`** takes `QL` and `QP` as inputs and reports the `QL`/`QA`/`QP` split against Small's measured ranges, port velocity against Reynolds-number and 10 m/s limits, flare geometry and the 0.2 `Dmin` edge radius. It does not predict leak noise, port pipe resonances in a vented box, or turbulence from bends and nearby surfaces.
- **`baffle_diffraction`** gives a rectangular baffle's step and edge ripple with the piston's beaming toward the edges, an edge radius that acts above `c / 8r`, and an optional recessed-tweeter carrier. It has no proud flange, grille frame, grille sheet, felt or waveguide blend.
- **`exterior_bem`** computes whatever the closed mesh contains. A recess, a flange step or a grille frame counts only if it is meshed; "a feature absent from the mesh is absent from the computation."
- **Nothing in the framework** models glue strength, wood movement, fastener capacity, rattles, rear-chamfer effects, grille transmission, felt or floor coupling. Those are judged from this reference and stated in the candidate notes.

## 23. Not covered

No non-forum source was found for these, so a decision on any of them needs a stated assumption:

- the rotational stiffness of glued loudspeaker joints;
- a measured comparison of brace types, or of regular against irregular spacing;
- the stiffness of a doubled baffle and the stiffness removed by a cutout;
- T-nut pull-out in MDF, and re-tightening after creep;
- driver manufacturers' instructions on rear chamfers and on clearance behind the magnet;
- measured box-level compliance gain against fill type and density, and measured interior sound radiated through cones against fill;
- a measured port-end clearance threshold;
- the residual vibration of opposed drivers;
- biscuit, loose-tenon and connector strength in MDF corners;
- the effect of finishes on cabinet sound;
- engineering data on non-wood cabinet materials as built;
- a measured or BEM comparison of edge radii and chamfers on one cabinet;
- the insertion loss of grille cloth, and a grille on/off listening test;
- the effect of a gap between a flange and its recess, of screw heads and trim on the baffle, and of felt at grazing incidence.

The paywalled primary papers behind several secondary statements were not read: Toole and Olive 1988, Olive et al. 1997, Bradbury 1976, Iverson 1973, Tappan 1962, Putland 1998, Kates 1979, and the full texts of Bastyr and Capone 2003 and Kılıçkaya and Erol 2026.

## Sources

Research papers, theses and broadcaster reports

- H. D. Harwood and R. Mathews, "Factors in the design of loudspeaker cabinets", BBC Research Department Report RD 1977/3, 1977. Sections 2, 3, 4, 9 and 10, Tables 5 and 6. <https://downloads.bbc.co.uk/rd/pubs/reports/1977-03.pdf>
- H. D. Harwood, M. E. Whatton and R. W. Mills, "The design of the miniature monitoring loudspeaker type LS3/5A", BBC RD 1976/29, 1976. Cabinet, lining, sealing and crossover-board practice. <https://downloads.bbc.co.uk/rd/pubs/reports/1976-29.pdf>
- C. D. Mathers, "Design of the high-level studio monitoring loudspeaker type LS5/8", BBC RD 1979/22, 1979. Section 4: lining, bitumen damping, the baffle–driver resonance and its battens. <https://downloads.bbc.co.uk/rd/pubs/reports/1979-22.pdf>
- H. D. Harwood and S. A. Hughes, "The design of studio monitoring loudspeakers types LS5/5 and LS5/6", BBC RD 1967/57, 1967. The midrange sub-enclosure and the chopped-tone resonances. <https://downloads.bbc.co.uk/rd/pubs/reports/1967-57.pdf>
- Y. Luan, *Modeling structural acoustic properties of loudspeaker cabinets*, PhD thesis, Technical University of Denmark with Bang & Olufsen, 2011, including Luan, Ohlrich and Jacobsen, *Journal of Sound and Vibration*, 2011. Rib-stiffened plates, the half-wavelength limit, source and receiver mobility. <https://backend.orbit.dtu.dk/ws/files/6437287/Yu%20Luan.pdf>
- M. Cobianchi and M. Rousseau (B&W Group), "Predicting the Acoustic Power Radiation from Loudspeaker Cabinets: a Numerically Efficient Approach", AES 139th Convention, Paper 9367, 2015. The reaction force, glue joints, the matrix redesign, FE accuracy, spikes. Copy hosted by S. Linkwitz: <https://www.linkwitzlab.com/Cabinet%20radiation-17925.pdf>
- M. Cobianchi and M. Rousseau, "Modelling the Sound Radiation by Loudspeaker Cabinets", COMSOL Conference, Cambridge, 2014. <https://uk.comsol.com/paper/download/199487/cobianchi_paper.pdf>
- H. Alavi and K. R. Holland, "Investigation of loudspeaker cabinet vibration using reciprocity", *Proceedings of the Institute of Acoustics* 31(4), 2009, pp. 177-187. Read in an archived copy of the IOA proceedings.
- A. K. Johansen and O. K. H. Olsen, *Simulation-driven design of loudspeaker cabinet using optimization algorithms for finite element models*, MSc thesis, Aalborg University with DALI A/S, 2023. A master's thesis; FE checked against accelerometer measurements. <https://projekter.aau.dk/projekter/files/538307413/Simulation_driven_design_of_loudspeaker_cabinet_using_optimization_algorithms_for_finite_element_models.pdf>
- K. J. Bastyr and D. E. Capone, "On the acoustic radiation from a loudspeaker's cabinet", *Journal of the Audio Engineering Society* 51(4), 2003, pp. 234-243. Abstract only. <https://pure.psu.edu/en/publications/on-the-acoustic-radiation-from-a-loudspeakers-cabinet/>
- E. B. Skrodzka and A. P. Sęk, "Vibration patterns of the front panel of the loudspeaker system: measurement conditions and results", *Journal of the Acoustical Society of Japan (E)* 19(4), 1998. <https://www.jstage.jst.go.jp/article/ast1980/19/4/19_4_249/_pdf>
- A. Jones (Pioneer), "Loudspeaker Driver De-Coupling: a Preliminary report", undated industry report hosted by S. Linkwitz. Preliminary; one driver. <https://www.linkwitzlab.com/Driver%20Decoupling.doc>
- F. E. Toole, "The Measurement and Calibration of Sound Reproducing Systems", *Journal of the Audio Engineering Society* 63(7/8), 2015. <https://linkwitzlab.com/Toole-Room%20calibration.pdf>
- I. Mateljan, H. Weber and A. Doric, "Detection of audible resonances", 3rd Congress of the Alps Adria Acoustics Association, Graz, 2007. A secondary summary of P. A. Fryer and of F. E. Toole and S. E. Olive, *JAES* 36(3), 1988. <https://www.artalabs.hr/papers/im-aaaa2007.pdf>
- B. M. Fazenda, M. Stephenson and A. Goldberg, "Perceptual thresholds for the effects of room modes as a function of modal decay", *Journal of the Acoustical Society of America*, 2015. Author's copy; used only for its summary of Olive et al., *JAES* 45(3), 1997. <https://eprints.hud.ac.uk/id/eprint/24317/1/FazendaStephensonGoldberg-PerceptualThresholdsModalDecay.pdf>
- R. H. Small, "Closed-Box Loudspeaker Systems, Part I: Analysis", *Journal of the Audio Engineering Society* 20(10), 1972. Section 7, enclosure filling.
- R. H. Small, "Vented-Box Loudspeaker Systems, Part I: Small-Signal Analysis", *Journal of the Audio Engineering Society* 21(5), 1973. Section 3, enclosure losses.
- W. M. Leach Jr., "Electroacoustic-analogous circuit models for filled enclosures", *Journal of the Audio Engineering Society* 37(7/8), 1989, with the author's correction. <https://leachlegacy.ece.gatech.edu/papers/Filling.pdf>
- D. Lafarge, P. Lemarinier, J. F. Allard and V. Tarnow, "Dynamic compressibility of air in porous structures at audible frequencies", *Journal of the Acoustical Society of America* 102(4), 1997. <https://backend.orbit.dtu.dk/ws/files/5335549/Tarnow.pdf>
- G. L. Augspurger, "Loudspeakers on damped pipes", *Journal of the Audio Engineering Society* 48(5), 2000. Fill materials at matched density, driver position, tapered pipes.
- A. Salvatti, A. Devantier and D. J. Button, "Maximizing performance from loudspeaker ports", *Journal of the Audio Engineering Society* 50(1/2), 2002. The convention-paper version was read. <https://jahonen.kapsi.fi/Audio/Papers/AES_PortPaper.pdf>
- A. Bezzola, "Optimal bass reflex loudspeaker port design", COMSOL Conference, Boston, 2019. A conference paper with blind listening tests. <https://www.comsol.com/paper/download/679311/bezzola_paper.pdf>
- M. A. Kuczmarski and J. C. Johnston, *Acoustic Absorption in Porous Materials*, NASA/TM-2011-216995, 2011. <https://ntrs.nasa.gov/api/citations/20110011143/downloads/20110011143.pdf>
- N. Jiménez, V. Romero-García and J.-P. Groby, "Perfect absorption of sound by rigidly-backed high-porous materials", *Acta Acustica united with Acustica* 104, 2018. The Delany–Bazley and Miki models and their validity range. <https://perso.univ-lemans.fr/~vromero/ewExternalFiles/2018AAA.pdf>
- R. Bartolini, D. Borelli and C. Schenone, "Flow resistance and sound absorption of polyester fibre material with different coatings", SAPEM 2011, abstract. <https://sapem2011.matelys.com/Abstracts/S2/S2_11.pdf>
- J. Dettmer and G. D. Smith, "Comparing properties of North American manufactured particleboard and medium density fiberboard, Part II", *BioResources* 10(3), 2015. MDF density profiles, screw withdrawal, swell and expansion.
- O. Tor, "Effects of pilot hole diameter on screw-driving torques in medium density fiberboard", *CERNE* 25(1), 2019. <https://www.redalyc.org/journal/744/74460212007/74460212007.pdf>
- M. Derikvand and C. A. Eckelman, "Bending moment capacity of L-shaped mitered frame joints constructed of MDF and particleboard", *BioResources* 10(3), 2015.
- M. Tunay and N. Tankut, "Effect of various factors on the rigidity of furniture cases", *African Journal of Biotechnology* 8(20), 2009. Abstract only.
- Q. Wu, "Warp in Overlaid Furniture Panels", *Louisiana Agriculture*, LSU AgCenter, 1999. An extension article reporting a model.
- H. F. Olson, "Direct Radiator Loudspeaker Enclosures", *Audio Engineering*, November 1951, pp. 34-38 and 59-64 (reprinted *JAES* 17(1), 1969). The measured effect of cabinet shape and of 152 mm bevels. <https://www.worldradiohistory.com/Archive-All-Audio/Archive-Audio/50s/Audio-1951-Nov.pdf>
- K. R. Holland, "A simple model of cabinet edge diffraction", *Proceedings of the Institute of Acoustics* 32(5), 2010. <https://www.ioa.org.uk/system/files/proceedings/kr_holland_a_simple_model_of_cabinet_edge_diffraction.pdf>
- D. Elliott, K. Holland and P. Newell, "The audibility of comb-filtering due to perforated cinema screens", *Proceedings of the Institute of Acoustics* 36(3), 2014. The perforated-sheet mass model and an ABX test. <https://www.ioa.org.uk/system/files/proceedings/d_elliott_k_holland_p_newell_the_audibility_of_comb-filtering_due_to_perforated_cinema_screens.pdf>
- A. B. Kılıçkaya and H. Erol, "On the effect of the grille on the acoustic frequency response of a tweeter loudspeaker", *Noise Control Engineering Journal* 74(1), 2026, doi:10.3397/1/37745. Abstract only.
- R. Haddad, *Application of CAE techniques in solving tweeter installation issues*, MSc thesis, Chalmers University of Technology with Volvo Cars, 2018. Recess depth and grilles in automotive tweeter mounts. <https://publications.lib.chalmers.se/records/fulltext/255605/255605.pdf>
- J. M. Kates, "Loudspeaker Cabinet Reflection Effects", *Journal of the Audio Engineering Society* 27(5), 1979. Abstract only. <https://www.aes.org/e-lib/browse.cfm?elib=3202>
- R. Bücklein, "The Audibility of Frequency Response Irregularities", *Journal of the Audio Engineering Society* 29(3), 1981. Abstract only.
- S. Moulin and E. Corteel, "Spectral and spatial perceptions of comb-filtering for sound reinforcement applications", AES 152nd Convention, Paper 10551, 2022. <https://www.l-acoustics.com/wp-content/uploads/2022/07/AES152_Moulin-22-comb-filtering-HF.pdf>

Standards, regulations and government handbooks

- Forest Products Laboratory, *Wood Handbook: Wood as an Engineering Material*, FPL-GTR-282, USDA Forest Service, 2021. Chapters 4 (moisture), 8 (fastenings), 10 (adhesives), 11 (composites), 12 (composite properties), 13 (drying and dimensional change) and 16 (finishing), read in the Treesearch copies at `https://research.fs.usda.gov/download/treesearch/<id>.pdf` (ids 62243, 62253, 62250, 62258, 62260, 62261, 62269).
- IEC 60268-5:2003+A1:2007, *Sound system equipment - Part 5: Loudspeakers*, clause 11 and Annexes A and B, read in the national adoption PS IEC 60268-5/2014. <https://psqca.com.pk/cs/newitems2021/electronics/28-PS%20IEC%2060268-5-2014_FINAL.pdf>
- EN 204, durability classes for non-structural thermoplastic wood adhesives. The requirements were read on accredited test certificates (EPH Dresden PT-23-08-16-01; ift Rosenheim 16-001452-PR01) published by the adhesive maker Kiilto; the standard was not read.
- ETA-Danmark, European Technical Assessment ETA-12/0481, RAMPA threaded inserts, 2021. <https://www.rampa.com/media/35/3f/9c/1671462200/ETA120481%20HB%20RAMPA%20r3%202020_22_03_2021.pdf>
- US 40 CFR 770.10, formaldehyde emission standards for composite wood products. <https://www.law.cornell.edu/cfr/text/40/770.10>
- US 16 CFR 1500.14, including the ASTM D-4236 art-material labelling requirement. <https://www.law.cornell.edu/cfr/text/16/1500.14>
- Health and Safety Executive, "Wood dust: Controlling the risks", WIS23, 2022. <https://www.hse.gov.uk/pubns/wis23.pdf>
- Health and Safety Executive, "Frequently Asked Questions - MDF", 2021, archived copy (withdrawn from hse.gov.uk). <https://web.archive.org/web/2023id_/https://www.hse.gov.uk/woodworking/faq-mdf.htm>
- Health and Safety Executive, "Manual handling at work: A brief guide", INDG143, 2020. <https://www.hse.gov.uk/pubns/indg143.pdf>
- National Toxicology Program, *Report on Carcinogens*, 15th edition, "Wood Dust". <https://ntp.niehs.nih.gov/ntp/roc/content/profiles/wooddust.pdf>
- NIOSH Pocket Guide to Chemical Hazards, "Wood dust". <https://www.cdc.gov/niosh/npg/npgd0667.html>

Manufacturer engineering documents and data (claims are labelled as such where used)

- M. Dodd (KEF), *LS50 White Paper*, 2012. The excitation paths, the X-brace result, damped bracing, decoupling and force cancelling. <https://web.archive.org/web/2013id_/http://www.kefamerica.com/july12/LS50%20White%20Paper.pdf>
- KEF, *The Reference* information sheet, 2019. <https://assets.kef.com/pdf_doc/REF/REF_Info_sheet_EN_Artwork_20190227_v2.pdf>
- JBL Technical Service Department, *Loudspeaker Enclosure Construction Manual*, Publication CF802. Lining, proportions, leaks, driver tightening, port fit. Archived copy: <https://www.cieri.net/Documenti/JBL/Documenti%20tecnici/JBL%20-%20Loudspeaker%20Enclosure%20Construction%20Manual%20(Publication%20CF802).pdf>
- D. Daniels (JBL), "Notes on porting", 1985. <http://www.cieri.net/Documenti/JBL/Documenti%20tecnici/JBL%20-%20Ports%20and%20Vents.pdf>
- JBL, GTO/P1000-series subwoofer owner's manual. <https://support.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw70170d85/pdfs/P1000_OM_EN.pdf>
- Klippel GmbH, "ALD - Air Leak Detection" and "ALS - Air Leak Stethoscope" manuals. <https://klippel.de/manuals/frequencyresponse-distortion/ald/ald.html>
- Finnish Forest Industries Federation, *Handbook of Finnish Plywood*, 2002. <https://koskisen.fi/wp-content/uploads/materials/Handbook-of-Finnish-Plywood.pdf>
- Medite Europe, Medite Premier and Medite MR technical datasheets, V4/15.
- Weyerhaeuser, Super-Refined MDF2 tip sheets (edge fastening, edge finishing, proper care prior to use), 2016.
- Franklin International, Titebond Original and Titebond III product data, ASTM D905 results.
- Dynaudio, "Special Forty drivers mounting torque" FAQ. Read through a page summary only. <https://dynaudio.com/faq/special-forty-drivers-mounting-torque>
- KEF, *The Reference* R&D white paper, section 4.1.4 "Cabinet diffraction". Driver directivity and edge illumination, low-profile drivers, rear ports, the Shadow Flare. <https://assets.kef.com/pdf_doc/REF/REF-White-Paper-201219-LR.pdf>
- D. P. Anagnos (Sony), US 5,731,555, "Loudspeaker enclosure having a low reflection/low diffraction baffle", 1998. Background read in full: edge radius, felt pads, front-baffle discontinuities. <https://patents.google.com/patent/US5731555A/en>
- O. Jørgensen, "What are the advantages of speaker grilles?", Dynaudio Magazine, 2023. Read through a page summary only. <https://dynaudio.com/magazine/2023/july/grilles-ask-the-expert>
- F. E. Toole, "Loudspeakers and Rooms - Working Together", Harman/Infinity technical paper. Grille cloth as an absorber. Archived copy: <http://www.cieri.net/Documenti/Infinity/Documenti%20tecnici/Infinity%20-%20Loudspeakers%20and%20Rooms%20-%20Working%20Together%20(Floyd%20E.%20Toole).pdf>
- Patents read through page summaries only, cited for the constructions they describe and not for performance: D. P. Anagnos (Sony), US 5,949,033; E. Stiles, US 7,270,215; M. A. Dodd (GP Acoustics), US 9,143,847; S. Dedieu and P. Moquin (Mitel), US 7,461,718.

Secondary: engineers' sites and magazines, labelled where used

- D. Waratuke, "Loudspeaker Cabinet Bracing: A Detailed Look on Do's and Dont's", Audioholics, 2012. A finite-element study in an online magazine. <https://www.audioholics.com/loudspeaker-design/detailed-look-proper-loudspeaker-cabinet-bracing>
- R. Elliott, "Audio Accelerometer For Speaker Box Testing", ESP Project 181, 2018, and "Loudspeaker enclosure design guidelines", Elliott Sound Products. <https://sound-au.com/project181.htm>, <https://sound-au.com/articles/enclosures.htm>
- R. C. White, ed. R. Elliott, "Volume filling a reflex box", Elliott Sound Products, 2007. Amateur measurements and Bradbury's figures redrawn. <https://sound-au.com/articles/boxstuff.htm>
- S. Linkwitz, "Frontiers", page 2, section N. <https://www.linkwitzlab.com/frontiers_2.htm>
- J. Atkinson, BBC LS3/5a (Harbeth) measurements, *Stereophile*, 1993, and J. Austin, "Bob Katz on Loudspeaker Isolation", *Stereophile*, 2020, the latter reporting B. Katz, AES 149th Convention Paper 10405, 2020. Read through archived copies.
- A. R. Bailey, "A non-resonant loudspeaker enclosure design", *Wireless World*, 1965.
- T. Gravesen, "The importance of chamfering driver holes", troelsgravesen.dk. A designer's single-driver measurements. <http://www.troelsgravesen.dk/chamfer.htm>
- J. Krutke, Zaph Audio small driver tests, and "Surface mounting woofers and tweeters", 2005. A designer's own measurements. <https://www.zaphaudio.com/smalltest>, <https://www.zaphaudio.com/mtg-surface.html>
- D. Ralph, "Diffraction Doesn't Have to Be a Problem", *audioXpress*, 2005, and "SB Acoustics 2-Way: Diffraction and the Off-Axis", 2009, hosted on Zaph Audio. One practitioner. <https://audioxpress.com/article/Diffraction-Doesn-t-Have-to-Be-a-Problem>
- K. Howard, "Cutting Corners", *Stereophile*, 2004. A two-way measured with and without a large baffle extension. Read through an archived copy.
- J. Atkinson, Paradigm Reference Active/20 and Atlantic Technology AT-1 measurements, *Stereophile*; SoundStage!, Krell LAT-2 measurements (NRC), 2002; J. Larson, "Speaker Grilles On Or Off: Which Way Sounds Better?", Audioholics, 2019. Grille on/off measurements read off published plots. <https://www.audioholics.com/loudspeaker-design/grilles>
