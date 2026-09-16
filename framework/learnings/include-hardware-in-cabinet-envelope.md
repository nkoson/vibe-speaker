---
id: include-hardware-in-cabinet-envelope
date: 2026-09-15
project: forte-iii-performance-20260914, forte-iii-pr-20260914, forte-iii-r3, forte-iii-single-pr-20260914, forte-iii-one-woofer-20260915
phase: design
confidence: high
applies_when: Freezing a compact cabinet layout with deep drivers, large flanges, internal supports or rear outlets
tags: [geometry, datums, envelope, displacement]
---

## Observation
The compact performance study initially scored wooden cabinet dimensions without fully accounting for flange projections. A separate-horn candidate intersected an upper brace. The selected prototype needed a 16 mm woofer recess, a counted 18 mm backing ring, recessed terminals and explicit motor support. The ring then left only 1.5 mm to the upper brace and 2.5 mm to the side walls. A 201.068 mm rear duct includes the 18 mm wall, so its internal protrusion is 183.068 mm; treating both lengths as equal over-counted displacement and misrepresented clearance. An acoustic-depth sign suggestion was also reversed before being caught during review.

A third study found side-mounted crossover boards intersected front-rear struts until the boards moved downward. Its SS15-PR drawing also showed a 25 mm diaphragm projection beyond a flush flange: a 510 mm wooden box became approximately 535 mm static assembled depth. Nominal rings and board bodies did not by themselves close lead, fastener and moving-envelope checks.

A third project drew the elevation only after the acoustic work was finished and found two
conflicts at once: window braces passing straight through a 168 mm deep woofer basket and a 233 mm
deep midrange horn body, and two 299 mm port tubes specified for a 317 mm cavity that the horn
already filled to 233 mm. Both are visible in seconds on a front elevation and a side section. The
fix cost a full rebuild of the finalist: new alignment volume, new port geometry as a bottom slot,
and reruns of the cavity, panel, board and plot chain.

A single-PR layout exposed two more datum and installation issues. The flush horn plus driver
extended 308 mm inward, not the initially assumed 300 mm. Cover wire entries also coincided
with support posts until checked as physical objects. A 3.500 L board reserve was too tight
for realistic wiring and supports; increasing it to 3.650 L retained unperforated loaded
boards, changed net air from 98.586564 L to 98.436564 L, and required a fixed-network replay
with 128.059 g added PR mass. The correction was small acoustically but necessary mechanically.

## Why it mattered
Nominal volume, outside size, physical fit and propagation delay depended on different datums. Fixing one without updating the others could preserve an attractive score for a cabinet that would not assemble or would violate its size constraint.

The single-PR revision needed six explicit half-laps to turn intersecting brace boxes into buildable joints, rotated PR fasteners to retain edge distance, and a rectangular PR backing plate instead of an oversized round ring. Reading both ends of the SS15 drawing gave surface-mounted static/moving depths of 415/450 mm for 380 mm rear wood. A 1.85 L installed electrical reserve included insulated cable, fasteners and spacers; the final 108.330 L air volume was replayed through the full network. Clearance boxes were screening envelopes, not solid driver geometry.

A fifth project drew the cabinet three iterations after the driver set was fixed and found the net
volume was 96.575 L, not the 101 L every candidate had been built on. The deductions that made the
difference were ordinary: 6.0 L of assumed woofer body, 3.5 L of assumed radiator body, 5.8 L for the
outside of the sealed midrange chamber, 2.2 L of boards and wiring, 3.7 L of lining solids. It cost
one rebuild of the finalist rather than the comparison between candidates, and only because that
driver's Vas was large enough for the alignment to be insensitive to 4 L.

## Advice
For a tight layout, consider defining one coordinate system and recording both external hardware bounds and internal cavity displacement before freezing geometry. Distinguish through-cut, flange, recess, physical depth and acoustic center. Track each outlet's total acoustic path separately from the part inside the chamber. A simple conservative bounding-box and clearance check may expose conflicts early; actual profiles, fastener access and motor-shell contact still need physical verification. Avoid counting a hardware reserve twice when a board or support is detailed later.

Consider tracking wood dimensions, static hardware bounds and moving clearance separately. A total depth arrow may begin on a diaphragm dome rather than a flange; verify both ends against the primary drawing. Check board-to-brace positions after physical component orientation is finalized.

Consider drawing the cabinet as soon as the driver set is fixed, before the crossover work, and
reading the drawing rather than only the numbers. A brace plane crossing a driver body and a duct
longer than the cavity are obvious on an elevation and expensive to find after a crossover has
been fitted. Where a driver body leaves no band of the front panel free for a full brace, a shelf
brace glued to the sides and the rear only will clear it; where no straight duct fits, a slot port
formed by a shelf in the dead space under the woofer may, at the cost of an area-and-length
equivalence, which leaves the tuning to be confirmed by measurement on the finished box.

Consider counting insulated wire, straps, spacers, adhesive and sealed service cavities in the
installation reserve, alongside component bodies. Check wire entries against the support grid
and fasteners. When a realistic installation slightly changes net air, a revised alignment
and complete fixed-network replay can be preferable to weakening a loaded support merely
to preserve a provisional volume allowance. Keep document coordinates in one declared datum,
with any conversion from centered source coordinates explicit.

When support boxes intersect, consider specifying the actual joinery and counting their solid union rather than dismissing the overlap as intentional. Check circular flange bolt positions individually against an inset panel's edges. Distinguish the view direction from the coordinate datum on board drawings; a rear-mounted board drawn from the front is not a rear view.

## Evidence
- `framework/projects/forte-iii-performance-20260914/final/01-cabinet-construction.md`
- `framework/projects/forte-iii-performance-20260914/final/cabinet-drawings/geometry-audit.json`
- `framework/projects/forte-iii-performance-20260914/candidates/c08/volume-accounting.json`
- `framework/projects/forte-iii-performance-20260914/project.json`, geometry correction log
- `framework/projects/forte-iii-pr-20260914/postmortem.md`
- `framework/projects/forte-iii-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-r3/final/cabinet_drawing.png` and `final/01-cabinet-construction.md`
- `framework/projects/forte-iii-r3/postmortem.md`, reason 2
- `framework/projects/forte-iii-single-pr-20260914/candidates/c08/detailed/solid-volume-budget.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/geometry-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/final-audit.json`
- `framework/projects/forte-iii-single-pr-20260914/postmortem.md`, physical realization corrections
- `framework/projects/forte-iii-single-pr-20260914/candidates/c18/detailed-revision2/mechanical-layout.json`
- `framework/projects/forte-iii-single-pr-20260914/evaluations/c18-revision2-geometry-review.json`
