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
- Features have `id`, `kind`, `depth` (millimetres or `"through"`), `face` (`outside` or `inside`). Circles use `center`, `diameter`; rectangular cuts use `xy`, `size`, optional corner `radius`. A through circle can specify `edge_radius` for a roundover on both rims. Countersinks use `kind: "countersink"`, `diameter`, `bore`, `depth`; these form cones, not cylindrical counterbores. Edge holes use a local 3D `position` and inward unit `direction`.
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
