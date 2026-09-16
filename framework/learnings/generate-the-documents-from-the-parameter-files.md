---
id: generate-the-documents-from-the-parameter-files
date: 2026-09-14
project: forte-iii-r3
phase: documentation
confidence: low
applies_when: A buildability decision changes a part after the simulation parameter files were written
tags: [documentation, buildability, schematic, netlist, consistency]
---

## Observation
A crossover position dissipating 117 W had to become an array of twenty-four 18 ohm parts to be
buildable from stocked 10 W resistors. The array was worked out, priced and written into the parts
list in the construction document, and it was correct there. It was not written into the
`crossover_network` parameter file, so `schematic.py` and the board netlist derived from that file
went on showing a single 10 W resistor, and so did the pin-to-pin connection table. Three
documents in the same package disagreed about what to fit in five positions. The independent
evaluator named it the top delivery risk, on the ground that a builder follows the wiring table.

## Why it mattered
The wiring table and the schematic are generated artefacts; the parts list was hand-written. A
correction applied only to the hand-written half cannot reach the generated half, and the
generated half is the one a builder wires from. Writing the realized array values back into the
parameter file and rerunning the chain also changed the response slightly, because the array
resistances are not exactly the nominal ones, which is a second reason the two halves must agree.

## Advice
Consider making the simulation parameter file the single place where a part is defined, including
the parts that exist for buildability rather than for the electrical model: a resistor array, a
substituted stock value, a slot port modelled as round ducts. Where a leaf carries `part` and
`rating` fields the schematic and the connection table pick them up, so the array can be named
where it is defined. After any late correction, ask which documents are generated and which are
written, and rerun the generated ones. A useful last check before delivery is to open the wiring
table and the parts list side by side and read the five most stressed positions in both.

## Evidence
- `framework/projects/forte-iii-r3/final/crossover_connections.md` and `final/02-crossover-construction.md`
- `framework/projects/forte-iii-r3/tools/rate_resistors.py`
- `framework/projects/forte-iii-r3/postmortem.md`, reason 7
