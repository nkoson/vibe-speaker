# Component research and search expansion

Use before shortlisting parts, when inheriting an inventory, and when a fit, price, geometry or availability problem could be caused by that inventory. The aim is broad, relevant market coverage followed by justified screening. It is not exhaustive simulation of every catalogue entry.

## Establish coverage before selecting

Create `inventory/search-review.md` using `framework/templates/inventory-search.md`. List every role the allowed architectures require, its user constraints, the useful parameter range and the manufacturers/catalogue families searched. Include specialist distributors and regional suppliers as well as familiar shops. Use current manufacturer catalogues/datasheets for identity and technical ranges, and supplier listings for exact purchasable variants, price and availability. Search results and retailer category pages are discovery aids, not evidence that no other part exists.

Search by functional requirements and parameter ranges as well as known brand/model names. Inspect relevant neighbouring markets, such as home audio, studio and professional sound, when their parts meet the brief; a retail category is not an acoustic compatibility test. Remembered or cached parts need current catalogue verification before they govern selection.

Keep the researched pool separate from the screened and simulated pools. Preserve rejected and unresolved entries with a reason and source or simulation evidence. Multiple shops selling one SKU do not broaden the model pool; impedance variants and related models count separately only when they change the design. Record such relationships instead of inflating counts. Do not silently drop a promising part because an FRD file, price or stock field is missing: seek the missing evidence, use a justified bounded model, or explicitly retain it as unresolved. Do not invent data or treat a discontinued part as normally purchasable.

The main skill gives initial driver breadth targets. Count alone does not close research: cover materially different usable bandwidths, losses, output capabilities, sizes, prices and construction options within the brief. Respect explicit component choices and exclusions. A smaller constrained market needs evidence of its coverage, not irrelevant candidates added to reach a number.

## Search each required role

| Role | Coverage and comparisons needed before commitment |
|---|---|
| Active drivers: LF, midrange, HF, coaxial or full-range as applicable | Multiple manufacturers and relevant product families, impedance variants, useful bandwidth/directivity, motor and suspension parameters, output limits, mounting size and cost. Compare LF alignments over the allowed volume/tuning range, rather than one inherited box. Compare HF sources with compatible horns/waveguides and their protection conditions. Do not rank by a single advertised sensitivity, resonance or material. |
| Horns and waveguides | Different compatible mouth sizes, coverage patterns, profiles, depths and mounting systems. Research the driver and horn as a pairing, with exact-fixture data distinguished from an assumed transfer. A preferred horn fixes a compatibility constraint, not a single compression-driver candidate. |
| Passive radiators | Relevant catalogue families, sizes and diaphragm areas; excursion, moving mass/compliance, added-mass range and attachment, orientation, displacement and availability. Compare allowable radiator counts and tuning masses with the actual driver/box, checking radiator output limits and fit. Do not search only the woofer maker's matching radiator. |
| Reflex ports | Complete flared kits and modular flanges, tubes, inner flares and compatible elbows where useful. Cover bore/area, count allowed by the brief, flare geometry, achievable physical length, mounting/recess, internal projection, mouth clearance and support. Compare actual buildable assemblies, including custom-cut stock tube, rather than rejecting a family because its shipped length is wrong. Keep acoustic effective length distinct from cut length. Compare loading hardware before crossover construction/fitting. |
| Crossover components | Actual manufacturer series and stocked values across suppliers, including internal gaps and values outside an inherited list. Cover useful inductance/DCR/core/wire-gauge combinations, capacitance/dielectric/ESR/voltage choices, and resistance/power/mounting choices. Compare affordable and premium series by modeled differences. Preserve exact SKU, value, tolerance, losses, ratings, dimensions, price/tax basis and dated availability together. |
| Other required parts | Apply the same search to terminals, protection parts, transformers, mounting hardware, damping and supports when they affect performance, fit, cost or availability. State the functional requirement and compare compatible options; trivial interchangeable fasteners do not need a driver-sized shortlist. |

Avoid excluding an entire technology or price class merely because it was absent from an earlier project. Conversely, architecture constraints such as passive-only, a particular port count or a specified horn remain constraints. Research depth follows the importance and uncertainty of the choice.

## Make a broad pool affordable to evaluate

Use inexpensive physical and compatibility screens first; exclude only with a stated reason. Retain contrasting promising choices and alternatives near uncertain screening boundaries. Small predicted differences below source uncertainty do not justify pruning. Give each serious contender its own appropriate loading, level and crossover fit before final system ranking; copying the incumbent's crossover can reject a compatible driver for the wrong reason.

Record which combinations were screened, fitted or not tried, and why. A candidate-per-iteration limit controls detailed design work, not catalogue discovery. If the useful shortlist exceeds the detailed budget, prioritize experiments that could change selection and state the untested remainder. Do not silently take the first few entries or equate an optimizer's retained subset with the entire inventory.

## Reopen searches when the design exposes a gap

Perform a targeted expansion before attributing these symptoms to physical necessity:

- A fitted value reaches an inventory endpoint, lands in an unexplained internal gap, or turns into a large series/parallel bank.
- Cost, component count, dissipation, resistance or board size is dominated by a few positions.
- A driver pairing needs extensive correction, fails its crossover window/protection target, or is supported by weaker fixture data than other plausible pairings.
- A port or radiator misses tuning, clearance or output because only one diameter, shipped length, mass range, count or supplier was considered.
- A budget, architecture, availability or performance revision invalidates the previous screen; or the apparent winner is selected from a narrow or uncertain pool.

For every crossover bank, distinguish a needed electrical function from its physical realization. Search for a single catalogue part and nearby realizable values with suitable loss, rating and size before freezing the bank. Compare refitted single-body alternatives with the actual bank; equal nominal values alone do not establish equivalence. Separately test removal/refitting of correction functions where their benefit is doubtful. Keep a bank when stress sharing or another demonstrated requirement earns it, and record why the simpler realizations were rejected. Count every physical body and its price in selection; do not use a combined symbol to hide construction complexity.

Expansion updates the inventory, then the affected screens and fits. Preserve the incumbent and rerun comparable contenders if new stock or revised source evidence could change their ranking. A wider list without revisiting the design does not fix an inventory-limited result.

## Close the search with evidence

Before selection, summarize coverage by role, retained alternatives, exclusions, unresolved evidence and each triggered expansion's outcome. A useful stopping basis is that relevant catalogue families and parameter ranges have been searched, credible alternatives compared on the requested system objectives, and further searches are unlikely to change the decision. An explicit user time/iteration limit can stop work sooner; state what remains unsearched or untested and narrow the conclusion accordingly. Neither meeting a count nor exhausting a local JSON list proves optimality or impossibility.
