---
id: verify-routed-contours-against-hardware
date: 2026-10-05
project: neat-petite-dayton-astra
phase: design
confidence: low
applies_when: Turning manufacturer mechanical drawings into routed driver recesses, through-cutouts or grille openings
tags: [geometry, machining, contours, radii, fit, documentation]
---

## What went wrong
A rounded tweeter faceplate was represented by its rectangular width and height in the construction drawings. The pocket and body aperture consequently had sharp corners without a routing method. A later whole-millimetre revision reconciled panel sizes, joints, datums and bounding-box occupancy, yet carried the same contour error into another finished package. The user caught it. Those checks established envelope consistency, not that the drawn profile matched the hardware or could be cut with the intended tool.

## What could have helped
Inspect the manufacturer's front, rear and section drawings before turning an envelope into a cut. Record which radii are dimensioned, which are inferred from drawing geometry, and which are chosen manufacturing allowances. An inferred vector radius is useful evidence but is not a published manufacturing tolerance.

Define the finished recess, body opening and grille contour separately. Check cutter diameter and depth, minimum corner clearance against the complete body envelope, remaining fixing lands, sealing ledges, and lead access. Distinguish finished outlines from tool-centre paths and guide-bush template dimensions. A conservative square body envelope can sometimes prove a rounded opening fits without assuming the body's own corner radius.

Make the drawing code consume these contour definitions rather than only width and height. Inspect all elevations and machining views for actual arcs, tool/radius labels and consistent installation details. Keep an actual-part scrap trial where source tolerances or wiring geometry remain unknown, alongside the geometric proof rather than in place of it.

For recessed drivers, include the compressed gasket in both the acoustic seating depth and moving clearance to the grille. In the CA18 release, a 1 mm lift still passed the nominal phase target but consumed the combined grille-clearance margin. A sealing material is therefore part of the installed geometry, not just a shopping-list accessory.

Draw the complete fastener stack before judging engagement. A rear T-nut sleeve extends into the panel: the length protruding behind the wood is not the thread engagement. In this project's 9 mm web, an M4 × 16 bolt spanned the full nominal 8 mm sleeve despite protruding only 1.8 mm behind the wood. Check the actual sleeve and bearing faces rather than extending the bolt from that protrusion alone.
