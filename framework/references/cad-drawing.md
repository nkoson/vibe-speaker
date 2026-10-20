---
id: cad-drawing
applies_when: Creating or reviewing fabrication CAD drawings for a loudspeaker cabinet and its installed parts
updated: 2026-10-20
---

# Cabinet CAD drawing practice

A fabrication drawing communicates shape, location, material and fit. Its dimensions must let a builder reconstruct the part without measuring the picture. Assembly views explain how parts meet; detail views define machining. Use one geometric definition for the CAD model, dimensions, hole schedules and cut list.

## Engineering basis

NASA's engineering drawing manual calls for complete, unambiguous fabrication information, third-angle mechanical views, distinguishable line weights, arrow-ended dimensions and identified cutting planes. It keeps CAD geometry at full size and requires view scales to be stated. Its design-review appendix favors functional/mating datums and avoids dimension arrangements that accumulate unnecessary tolerance. These principles inform the workflow here; spacecraft-specific administrative and material rules are not adopted. [S1, printed pp. 25-38 and 107]

ISO 128-2 addresses line conventions and leaders; ISO 5457 addresses drawing-sheet size/layout; ISO 7200 addresses title-block data. ASME Y14.100 supplies the wider preparation/revision framework. The linked public publisher pages establish these scopes. The numerical style below is this repository's working convention, not a claim to reproduce inaccessible clauses. [S2-S5]

Autodesk documents baseline dimensions from a common origin and ordinate dimensions with an origin indicator. Its documentation also describes dimensions associated with geometry and dimension styles controlling units, tolerance and text placement. These support using feature-derived dimensions rather than manually typed values detached from the shape. [S6-S7]

## Sheet and annotation convention

The following are local drafting choices for cabinet work:

- Model in millimetres at 1:1. Keep physical geometry out of paper-scale coordinates.
- Use A1/A2 for an assembly overview when necessary, and A3 for machining/details. Declare sheet size, drawing number, revision, date, units, material, projection and view scale in a ruled title block. Include sheet number/total and a concise change entry.
- Prefer third-angle projection: top above front, right view to the right. Put the projection name or symbol on each sheet. Independently placed sections/details have their own name, direction and scale.
- Plot visible outlines at 0.50 mm and dimensions, leaders, centre/hidden lines at 0.25 mm. Use 0.13 mm hatching. Keep text at least 2.5 mm tall on the printed sheet; 3.0-3.5 mm is a useful ordinary annotation size. Increase sheet size or split views before shrinking type.
- Solid lines identify visible edges; short dashes identify hidden edges; long-short chains identify axes/centres; a heavier chain and arrows identify a cutting plane. Hatch cut material with thin parallel strokes. Vary adjacent-part hatch direction or spacing. Add a distinct key for porous lining.
- Keep dimensions outside contours where possible. Stagger parallel strings; put short dimensions nearest the part. Keep extension lines distinct from outlines and leave a small gap at their origins. Use real arrowheads and clear leaders for diameters/radii.
- Leave reserved bands for title/revision blocks. No geometry, text or dimensions may run into those bands or outside the border. Review at the intended print size, including monochrome output.

## Datums, dimensions and fit

Choose datums a builder can touch: a finished panel face, a long-point edge, the cabinet bottom, or a stated centreline derived from two physical edges. Name every view's origin and handedness. An inside-face view must explicitly show whether it is mirrored relative to the exterior view.

Use baseline or ordinate dimensions for driver centres, brace housings, hole groups and board mounts. Avoid forcing the builder to add unrelated chains. Give one controlling dimension for a feature; mark duplicated overview dimensions as reference. Closing dimension chains are verification arithmetic, not extra competing tolerance constraints. MIT's drawing handbook also recommends sufficient nonredundant dimensions and references chosen for the manufacturing sequence. [S11]

Each hole callout carries count, diameter/thread, through/blind depth, entry face and location. Give bolt-circle diameter plus angular pitch and clocking, or a keyed coordinate table. Locate rectangular patterns from the same datum. Define countersink angle/major diameter and counterbore diameter/depth separately from the bore. Preserve factory fractional coordinates; display precision does not authorize rounding a fixing pattern. Autodesk's hole-note documentation derives diameter, depth and thread data from the model rather than a disconnected annotation. [S12]

Use whole-millimetre wood targets where required by the project, but retain exact centreline symmetry. State the project's actual fit tolerance separately. A total assembled fit allowance is not automatically a tolerance for every panel or hole. Check the cumulative stack across mating parts. Dimension dry wood contact, compressed seals, remaining webs and thread engagement. Give hardware-dependent machining as an explicit operation: for example, locate pilots with the supplied flange used as a jig. Do not invent unavailable factory coordinates.

## Views needed for a cabinet

Choose the smallest complete set; an attractive isometric is a locator, not a replacement for machining views.

| View / record | Information it must carry |
|---|---|
| Assembly elevations and plan | Overall envelope, feet, driver centres, ports, connector, axes and view relationships |
| Longitudinal and transverse sections | Panel thickness, joints, brace locations, holes, lining, cradle, boards, installed envelopes and service clearance |
| Loose-panel drawings | Part ID/quantity/material, actual blank and long-point dimensions, local datum, cutouts, pockets, grooves, pilots and entry face |
| Driver mounting details | Aperture, recess contour/radii/depth, fixing pattern, bearing ledge, compressed seal, nut/insert and fastener stack |
| Brace details | Blank and housing engagement, each aperture and edge radius, coordinates and thickness |
| Ports | Purchased pieces, straight cut lengths, sleeve engagement, finished mouth-to-mouth length, recess, fixing operation and mouth clearance |
| Cradle/support details | Saddle arc/centre, runners, contact surfaces, screw/pilot locations and assembly order |
| Rear/underside details | Connector relief and hole pattern, board/star mounts, feet and blind fixing depths |
| Cut list and feature schedule | Matching IDs, quantities, material thickness and sheet/view references |

A section starts from a marked cutting plane in an exterior/assembly view. Match its identifier and arrow direction to the section label. Show actual material intersections and necessary visible geometry beyond the plane. Distinguish a purchased-item envelope from a machined wood profile; dimensions for both still come from the authoritative part record.

## What to take from the supplied example

The Nova-Andromeda sheet combines elevations with multiple labelled sections, dimension strings, internal bracing, installed drivers and a damping key. A common grid and title block make the large sheet navigable. The useful pattern is the relationship between views and the placement of construction information directly on them. Apply that organization to the selected speaker's own geometry. Do not copy the example's dimensions, construction or artwork. [S8]

## CAD artifacts and numerical checks

Deliver an editable millimetre DXF with named layers and native dimension entities, plus vector PDF sheets. Keep a 1:1 profile/part export distinct from paper-space layouts. A STEP assembly is useful for fit and occupancy checks; preserve named components. Retain the generating geometry/parameters because STEP transfers geometry rather than the complete parametric design history. CadQuery documents this distinction and its STEP/DXF export support. [S9]

Use a CAD application's dimension objects, or a CAD library that creates actual DIMENSION entities and their rendered geometry. Ezdxf documents both dimension construction and its rendering step. A line and a typed number are insufficient if they can disagree silently with the geometry. [S10]

Before release:

1. Reopen DXF and STEP exports. Check millimetre units, expected parts/features, positive valid solids, body bounds, hole centres/diameters and every dimension's measured value and rendered numeric label. Set the dimension length factor explicitly to one; a library's default annotation style can scale labels while leaving the geometry unchanged.
2. Compare drawing features against the selected geometry and bill of materials. Check datum transforms, mirrored panels, brace engagement, recess webs, hole ligaments and screw reach.
3. Verify paper scales using model lengths and viewport/layout scale. Keep detail scales explicit; label an unscaled illustrative view as such.
4. Render every sheet. Check overlapping text, crossed dimension strings, hidden-line clarity, section arrows, hatch boundaries and empty/obscured callouts.
5. Perform a reconstruction pass from drawings alone. Every essential feature must have a dimension, keyed schedule or a precise supplied-part jig operation.
6. Keep source/provenance and checks in the project evaluation. Builder-facing notes are concise assembly and machining instructions, following the documentation skill's canonical-results contract.

## Sources

- **S1.** NASA Goddard Space Flight Center, *Engineering Drawing Standards Manual*, X-673-64-1F, Rev. 001 (1994), sections 3.1-3.5 and Appendix A. [NASA-hosted manual](https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/NASA%20GSFC-X-673-64-1F.pdf). Relevant text inspected directly.
- **S2.** ISO, *ISO 128-2:2022, Basic conventions for lines*. [Publisher scope](https://www.iso.org/standard/83355.html).
- **S3.** ISO, *ISO 5457:1999, Sizes and layout of drawing sheets*, with 2010 amendment. [Publisher record](https://www.iso.org/standard/29017.html?browse=tc).
- **S4.** ISO, *ISO 7200:2004, Data fields in title blocks and document headers*. [Publisher scope](https://www.iso.org/standard/35446.html).
- **S5.** ASME, *Y14.100-2017, Engineering Drawing Practices*. [Publisher scope](https://www.asme.org/codes-standards/find-codes-standards/engineering-drawing-practices).
- **S6.** Autodesk, [Create baseline and chain dimensions in Fusion drawings](https://www.autodesk.com/learn/ondemand/tutorial/create-baseline-and-chain-dimensions-in-fusion-drawings). Official tutorial and transcript inspected.
- **S7.** Autodesk, [Dimensions in Drawings](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-Help/files/GUID-438F8DED-72FA-460A-AB11-FBBD84194672.htm). Official documentation inspected.
- **S8.** Humble Homemade Hifi, [Nova-Andromeda CAD sheet](https://www.humblehomemadehifi.com/library/Humble%20Homemade%20Hifi_CAD_Nova-Andromeda.pdf). User-supplied authored drawing, visually inspected; layout example rather than normative authority.
- **S9.** CadQuery authors, [Importing and Exporting Files](https://cadquery.readthedocs.io/en/latest/importexport.html). Official interchange and parametric-source documentation.
- **S10.** Ezdxf authors, [Tutorial for Linear Dimensions](https://ezdxf.readthedocs.io/en/stable/tutorials/linear_dimension.html) and [Drawing / Export Add-on](https://ezdxf.readthedocs.io/en/stable/addons/drawing.html). Official CAD-entity and rendering documentation.

- **S11.** MIT OpenCourseWare, [Design Handbook: Engineering Drawing and Sketching](https://ocw.mit.edu/courses/2-007-design-and-manufacturing-i-spring-2009/pages/related-resources/drawing_and_sketching/), Design and Manufacturing I, 2009. Dimension placement, orthographic views and section hatching.
- **S12.** Autodesk, [Hole and thread notes](https://help.autodesk.com/cloudhelp/2016/ENU/Inventor-Help/files/GUID-162B828C-D6BA-4989-AA61-C9F4516D60D7.htm). Model-derived hole-note contents.

Sources accessed 2026-10-20. No forum or social-media material was used.
