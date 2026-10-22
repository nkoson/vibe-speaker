# Cabinet CAD drawing tool

`cad_drawings.py` exports fabrication PDF sheets, editable full-size DXF views with native dimensions, and named STEP parts/assemblies from a millimetre JSON manifest. The agent selects the design, features, view layout and construction notes. The tool builds geometry and verifies interchange; it supplies no acoustic judgement.

Use the [CAD drawing skill](../skills/cad-drawing/SKILL.md) and [engineering drawing reference](../references/cad-drawing.md) when authoring the manifest. Put project inputs/exports under the project's `final/cad/`; keep the tool itself in the framework.

```sh
.speaker-venv/bin/python framework/tools/cad_drawings.py \
  --input framework/projects/PROJECT/final/cad/cabinet-drawing.json \
  --out framework/projects/PROJECT/final/cad \
  --pdf framework/projects/PROJECT/final/cabinet-sheets.pdf
```

## Manifest

- `meta`: `title`, `drawing_prefix`, `revision`, `date`; optional `projection`, `tolerance_note`, `change`.
- `parts`: stable `id`, `width`, `height`, `thickness`, `features`, `placements`. Local XY is the outside face at Z0; material extends to negative Z. `miter: true` makes four 45-degree long-point edges. A circular blank instead uses `outline: "circle"`, `center`, `diameter`.
- Each placement supplies `origin`, `x_dir`, `normal`. Local Y follows the resulting right-handed plane. Use explicit transforms for reversed rear/left/underside views.
- Features have `id`, `kind`, `depth` (millimetres or `"through"`), `face` (`outside` or `inside`). Circles use `center`, `diameter`; rectangular cuts use `xy`, `size`, optional corner `radius`. A through circle or closed rounded rectangle can specify `edge_radius` for a roundover on both rims. Countersinks use `kind: "countersink"`, `diameter`, `bore`, `depth`; these form cones, not cylindrical counterbores. Edge holes use a local 3D `position` and inward unit `direction`.
- `profile_entities` can describe a nonrectangular drawing perimeter; associated cut features marked `in_profile: true` remain in the solid but are omitted from the ordinary 2D feature loop. Keep this perimeter consistent with the boolean cuts and verify it visually and geometrically.
- `sheets`: stable `id`, `title`, `paper` (`A1`, `A2`, `A3`), `views`, `notes`, `tables`. Sheet positions and text heights are paper millimetres. Each view uses model coordinates; `at` is its paper placement, `origin` its model-coordinate offset and `scale` its uniform plot scale.
- A view can name a `part`, optional selected `features` and visible `face`; or provide `entities`. Section views supply `section: {origin, x_dir, normal, parts}`. Named installed instances use `part-id@0`, `part-id@1`, etc.; sections are cut from their actual BRep solids.
- Entities: `line` (`points`), `polyline` (`points`, `closed`), `rect` (`xy`, `size`, optional `radius`), `circle` (`center`, `radius`), `arc` (`center`, `radius`, degree `start`/`end`), `hatch` (`loops`, `angle`). Layers: `OUTLINE`, `HIDDEN`, `CENTER`, `CUT`, `DIM`, `HATCH`, `ENVELOPE`, `LINING`.
- Linear `dimensions` use `p1`, `p2`, `base`, `angle` (0 or 90), optional `reference`. `diameters` refer to a circle/arc `feature` ID and give `location`, optional leader `angle`, `prefix`, `suffix`. Numeric values derive from the geometry. `leaders` and `texts` carry construction notes in model coordinates.
- Sheet `notes` use `at`, `text`, `width`, optional `height`. `tables` use `at`, `headers`, `rows`, column `widths`, optional `row_height`, `text_height`. Reserve enough row height for wrapped cells.

## Output and checks

Each DXF is a 1:1 model-space view with mm units, named layers and rendered DIMENSION entities. It is not a paper-size PDF clone. Use geometry layers to prepare toolpaths; dimensions, section hatches and envelopes are annotations. Paper scaling is applied only to the PDF and recorded per view in `cad-audit.json`.

STEP files include named individual part solids and an assembly. Source JSON preserves the feature definitions and transforms. The export checks solid validity/positive volume, STEP round-trip volume, DXF structure and every exported dimension's measured value and rendered numeric label (with a unit length factor). Exact circular/arc DXF contours retain their native analytic geometry; BRep section contours are sampled to 0.05 mm deflection for drawing.

These checks do not replace the agent's reconstruction, datum, feature-count, fastener-stack and rendered-page review. Add imported hardware geometry or accurate clearance envelopes where required by the design. Supplied-part jig operations belong in the machining notes; omit invented mounting coordinates.

A view may supply `flared_duct` to draw a recognisable assembled or exploded port section: bore/mouth/flange diameters, wall/flange/sleeve thicknesses, three piece lengths, sleeve length and optional exploded gap, all in mm. The profiles preserve the declared purchased flare convention; cut lengths apply to straight-tail cuts.

Optional top-level `air_domain` (`origin_mm`, `size_mm`) reports each installed part's actual intrusion into the internal air box. Features marked `role: air_aperture` produce aperture areas, pairwise root ligaments and clearance to the shaped part boundary. These are geometry outputs for the agent's evaluation.

Set `inspect_intersections: true` to report installed-part pairs with positive overlap volume. The report gives part IDs and overlap volumes; the agent distinguishes intentional joints from collisions and decides how to revise the design.

## Datasheet-derived installed components

A part may supply `solid_model: {operations: [...]}` in place of panel dimensions.
The shared `cad_components.py` geometry builder supports `revolve` (closed radius/Z
profile), `cylinder`, `box`, `extrude` (XY polygon), `slot` and `loft` (ordered Z
sections with a circle radius or XY polygon). Operations are `union`, `cut` or
`intersect`; the first is a union. Optional rotation and translation apply before
combining. See `primitive()` for the explicit fields. Local XY is the front face,
with negative Z behind it. Existing part placements put the resulting component
into the cabinet assembly. Optional RGB `color` distinguishes purchased parts.

Keep published dimensions, traced profile coordinates and chosen printable
features in the project's source-basis record. Preserve mounting slots, clocking,
thread specifications and seating faces. A printed tapping bore is a fabrication
choice, not the geometry of a manufactured internal thread. Author the hole
interfaces separately from the cabinet pattern and compare them after applying
the assembly transforms; copying cabinet holes alone does not verify a factory
pattern. `interface_offsets()` reports paired centre offsets without judging fit.

A view with `projection: {parts, origin, normal, x_dir, hidden}` draws visible
BRep edges using orthographic hidden-line removal. Parts use the same names as
sections. `hidden` defaults to false; set it deliberately for through-body views.
Curved drawing edges are sampled at 0.05 mm deflection; STEP keeps BRep geometry.
Add native dimension entities and keyed mounting schedules to these projections.
Sections, projections and STEP now share the solid geometry. Reopen each STEP,
check solid count/connectivity, interfaces and installed collisions, and inspect
the new PDF views. Preserve the manufacturer's displacement value in acoustic
models: the printable mockup's solid material volume is a different quantity.

Loft sections may use periodic `spline_points` instead of polygon `points` when
the section is smooth. `solid_model.expected_solids` checks the intended connected
piece count. Complex component exports use adaptive mass integration (1e-5) and
report their STEP round-trip volume difference, with a 1e-6 relative interchange
threshold. Analytic cabinet parts retain the 1e-8 threshold. All exported solids
must remain valid and preserve their solid count. Drawings use the reopened STEP
geometry, avoiding in-memory seam tolerances that can omit section contours.

## Scaled STEP mockups

Use `scale_step.py` to create a separate scale set from the individual STEP files
and their installed placements in the CAD manifest. It scales part coordinates
and assembly translations together, rebuilds the named assembly from the output
parts, and leaves source files untouched.

```sh
.speaker-venv/bin/python framework/tools/scale_step.py \
  --source-dir PROJECT/final/cad/step \
  --manifest PROJECT/final/cad/cabinet-drawing.json \
  --out PROJECT/final/cad/scale-8-percent --scale 0.08 --min-wall-mm 0.1 \
  --patches PROJECT/final/cad/scale-8-percent/minimum-wall-patches.json
```

The optional patches file maps part IDs to either a `solid_model` operation
record for added material, or `{mode: "replace", solid_model: {...}}` for a
reconstructed variant. Dimensions in this record are in source millimetres;
scaling follows construction. Keep printable corrections in that variant and
check its original interfaces and exterior bounds. Use a reconstructed section
when coplanar Boolean additions create disconnected slivers.

The minimum-wall argument records the design requirement; it does not invent
geometry changes. Review thin membranes, steep flares, recess floors and fixing
lands at the output scale. `wall_samples()` reports exact-surface inward-normal
chords with face IDs and positions for targeted refinement. Use meridian/section
geometry for continuous wall bounds where possible, and distinguish wall stock
from tapered edge tips or an intentional assembly joint. The tool verifies STEP
solid validity/count, scale bounds and triangulated edge incidence, winding and
collapsed triangles. `scale-audit.json` retains source/output hashes and poses.
