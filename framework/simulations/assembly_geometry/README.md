# assembly_geometry: Shared physical assembly

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py assembly_geometry --input framework/simulations/assembly_geometry/example.json --out results --name assembly_geometry
```

`assembly` is an inline record or `{file}` with `schema_version: 1`, `objects[]` and optional `sources[]`. Lengths are metres. Each object has a stable `id`, `role` (`air`, `solid`, `porous`), `shape`, `origin_m` and Euler `rotation_deg` (x, then y, then z). Shapes are `box` (`dimensions_m`), `sphere` (`radius_m`, `subdivisions`), `cylinder` (local z axis, `radius_m`, `length_m`, `segments`) and a closed `mesh` (`vertices_m`, `triangles`). `divisions` refines box surfaces.

Sources identify `object_id`, `local_position_m` and `local_normal`. Fabricated objects can carry `fabricate: true`, `machining`, `joints` and `treatments`; those records are exported intact rather than inferred from a bounding box. The same assembly is accepted by cavity/exterior apps and by whole-speaker sections using `assembly_source`.

`cell_sizes_m` specifies independent volume refinements. Air is the union of air objects minus the union of solid objects. Porous objects are tagged material regions, not airtight displacement. Outputs contain transformed meshes/normals, topology counts, voxel-volume convergence, pairwise solid intersections, sources and fabrication records. An intersection can be an intended joint; the agent interprets it.

Mesh topology checks count open, inconsistently oriented and nonmanifold edges. Closed mesh containment uses oriented solid angles. Grid volume is approximate, so compare refinements with actual dimensions. `framework/tools/assembly_drawing.py` renders the result and exports its fabrication record. It does not invent a joint or machining allowance.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
