---
name: cad-drawing
description: Create and verify dimensioned fabrication CAD drawings for loudspeaker cabinets, driver and screw-hole placement, joints, braces, ports, supports and installed hardware. Use when speaker documentation requires cabinet construction drawings or their revision; electrical circuit schematics remain with speaker-documentation.
---

# CAD drawing

Create a complete, buildable cabinet drawing set from the selected geometry. Read [cabinet CAD drawing practice](../../references/cad-drawing.md) before choosing views and dimensions. It contains the sourced drawing conventions, fabrication coverage and export checks. Use [cabinet geometry](../../references/cabinet-geometry.md) and [construction audit](../speaker-documentation/references/construction-audit.md) for physical fit and datum reconciliation.

## Establish the drawing basis

Read the selected geometry, part records, existing CAD and machining schedules. Freeze one millimetre-based feature definition with stable part and feature IDs. Reconcile local panel coordinates with assembly coordinates and identify each inside/outside face. Keep the selected acoustic geometry and circuit unchanged during a drawing-only revision. Resolve a genuine conflict in the geometry record before changing dimensions on the sheet; replay affected physics only for physical design changes.

Use an available CAD application or [the framework CAD exporter](../../tools/cad-drawings.md). Prefer actual CAD geometry and dimension entities to illustration primitives. Author reusable drawing/export logic in the framework; keep project geometry, view layouts, outputs and audit records in the project. Do not add project-specific physics solvers.

## Build the views

Use aligned orthographic elevations and plan, named cutting planes and sections, and enlarged mounting/joint details. An isometric or exploded view can explain assembly order. Include every item required to build the cabinet: panels, miters, housings, brace apertures, driver cutouts and recesses, screw holes, seal stacks, ports, cradle, boards, terminals, feet, lining and service envelopes. Each feature must have a size and location on a view or keyed schedule.

Follow the reference's sheet, line-weight, hatch, scale, title/revision-block and dimension-placement conventions. Model at 1:1; scale the views on the sheet. Use functional datums and baseline/ordinate dimensions for repeated locations. Preserve exact factory patterns and centreline symmetry. Dimensions must derive from geometry, not independently typed labels.

Show complete machining callouts: count, diameter/thread, depth, entry face, recess radius/depth and fixing pattern. Describe supplied-part jig operations explicitly where they are the selected way to locate holes. Do not draw an invented bolt circle. Dimension compressed seals and dry wood contact; keep fastening engagement and tool access visible.

## Deliver and check

Deliver vector PDF sheets and editable millimetre DXF geometry with dimensions. Include a STEP assembly when 3D occupancy/fit matters, and retain the source geometry/parameters needed to regenerate it. Put the drawings in the project's final package and update the cut list, schedules and drawing index together.

Reopen the exports and check units, extents, feature counts, solid validity, measured dimension values and datum transforms. Inspect every rendered sheet at print size, including crowded hole patterns and sections. Reconstruct the cabinet from the drawings alone, checking the complete dimension chains and hardware stackups. Record the checks and exact source revision in the project evaluation.

Use the speaker-documentation skill's analysis-and-instructions-only editorial contract. Construction notes tell the builder what to machine, locate, fit or assemble. Keep CAD implementation details and validation records out of the builder PDF. Return the sheet index, CAD artifacts and audit to speaker-documentation for inclusion in the complete design package.
