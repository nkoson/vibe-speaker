---
id: exact-identity-in-candidate-revisions
date: 2026-10-05
project: neat-petite-amt-v3, neat-petite-amt-v4, neat-petite-amt-v5, neat-petite-dayton-opus, neat-petite-dayton-astra, neat-dayton-redcatt
phase: design
confidence: medium
applies_when: Revising copied records or assigning dimensions and drilling datums to a cabinet assembly and its individual panels
tags: [geometry, provenance, inventory, validation, documentation]
---

## What went wrong
Information was assigned without identifying exactly which physical item and interface it described:
- **Name match.** A name-substring update meant for a crossover board also changed a front-panel thickness deduction, because both labels contained the same word. Net air was understated until independent reconciliation caught it.
- **Copied commercial summaries.** These kept an old driver's cost or omitted an unpriced replacement.
- **Drawings.** Assembly dimensions were prominent where the builder needed loose-panel dimensions and local drilling datums. Even after those were added, it stayed unclear which board covered which edge. Correct arithmetic did not establish an understandable assembly plan.
- **Dimension roles.** Nominal machining dimensions, purchased part geometry, installed mounting faces and acoustic radiation planes were treated as interchangeable. A shared clearance parameter represented both groove thickness clearance and panel-edge float. A model field named cabinet depth also placed the rear acoustic source: extending only the cabinet lip would therefore move a radiator that physically stayed fixed if the new outside depth were copied blindly. An assumed radiator projection had meanwhile acquired the appearance of a manufacturer dimension in drawings. Rounding labels or reusing one depth for all these interfaces concealed their different meanings.
- **Stock labels.** Product-page stock labels turned out to be hidden template placeholders, not the state returned for the selected product and quantity.
- **Price basis.** Sibling stock records (thinner-wire coils) carried the thicker-wire record's prices, overstating them by tens of percent to over double. One resistor record held a business-only price including VAT while the coil records excluded VAT. A search preferred a dearer, lower-rated part on those prices, and a candidate's cost was wrong until the vendors were re-checked.
- **Derived records.** Records generated from a base record kept fields such as availability and price source that described the base part, not the derived one. A fit check that the build printed as a warning never reached the audit record, so four candidates were reported free of findings while a faceplate touched the cabinet lip.
- **Repeated stock mapping.** A materializer snapped a selected resistance again using the wrong resistor series. A later replacement of the part name, rating and tolerance left the wrong numerical resistance behind. The circuit and solver agreed with each other while disagreeing with the purchased SKU. A broad path replacement similarly changed a comparison reference into the candidate being compared, even though independent evaluation remained correct.

The project postmortems record the affected files and corrections.

## What could have helped
- **Identity.** Use stable item identities or exact matches for revisions, inspect the changed records, and recompute geometry deductions from their dimensions where possible.
- **Derived records.** Clear or re-source every field that describes the original item.
- **Realized identity.** Compare every final leaf's numerical value, loss, tolerance and rating with its exact SKU and with the selected stock row before replay. Check whether a second quantization silently reinterprets a value from another series. Scope dependency rebasing by role: a candidate's own sources may move, while its comparison references keep their original identity. An independent comparison path can prevent a self-comparison from certifying itself.
- **Prices.** Record each price's basis with it: VAT included or not, consumer or business-only, vendor and date. Convert to one basis before cost enters a ranking or a bill of materials, and treat a price shared across sibling records as unverified.
- **Drawings.** Give each cut panel an identity, its actual width, height and thickness, and a local machining datum. Separate assembled elevations from panel drilling sheets, so the builder need not derive hole locations from cabinet coordinates. An exploded view and dimensioned sections through actual joint planes can show which broad face meets which cut edge. A three-dimensional material and contact check can expose overlaps or gaps, and a separate walk-through from cut blanks tests whether the assembly is understandable.
- **Manufacturing increments.** Keep a separate nominal machining contract when a builder requests whole-number dimensions. Reconcile groove seating, thickness clearance and edge float independently; preserve factory dimensions and derive installed positions from them. Transfer irregular factory fixing patterns instead of independently rounding their coordinates. Regenerate geometry-dependent predictions as well as drawing labels, and identify conservative installation envelopes as envelopes.
- **Coordinate meanings.** Record the outside envelope, mounting plane, moving-part envelope and acoustic reference separately. Inspect what a simulation field actually controls before propagating a physical revision into it. Keep a deliberately retained acoustic prior explicit, and do not present a guessed illustration dimension as a factory specification. Compare actual source coordinates before and after a change that is meant to leave hardware unmoved.
- **Checks.** Route every geometric check into the audit record rather than a log line.
- **Totals.** Rebuild totals from the selected physical parts and show completeness separately from a known subtotal; a missing quote need not become zero.
- **Stock evidence.** Tie it to the exact SKU and requested quantity, using the rendered state or its public stock endpoint when static HTML contains contradictory hidden labels.
- **Suppliers.** When consolidating them, check replacement values, losses, ratings and physical envelopes together rather than keeping an unavailable SKU only for its identity.

These checks complement independent review and do not make the underlying driver or construction data measured.
