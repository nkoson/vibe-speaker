---
id: check-protection-on-realized-transfer
date: 2026-10-01
project: neat-petite-amt-v4, neat-petite-dayton-opus, neat-petite-dayton-astra
phase: design
confidence: medium
applies_when: Fitting a crossover whose upper driver needs a protective high pass of a stated order and corner
tags: [crossover, protection, tweeter, fitting, validation]
---

## What went wrong
The tweeter's protection requirement was carried as bounds on the fitted high-pass elements and as an expected acoustic crossing frequency. The optimizer found responses that met the target curve with the electrical high pass well below the required corner. It did so first with loose bounds, then within an LC-product bound, by pairing an underdamped high pass with a large series pad. Each time the invalid builds were found only by an audit after a whole iteration had been built. Two rebuild passes followed, and archived builds that were never evaluated. Later, a fast search screened protection on a coarser frequency grid than the app's. It passed a network that the app then failed by a hundredth of a decibel, so the selected design missed the check on paper and needed a separate judgement of its absolute protection. In a later project the search screened protection on every realized transfer, but the ranking carried the margin over the maker's reference slope only as a weighted term. Two built candidates failed that margin, which has no tolerance, until an evaluator asked for a hard screen.

## What could have helped
From the first build, measure the protection on the realized network: compute the high-pass transfer at the driver terminals and check its corner and its attenuation at a protection frequency an octave or so below. Element bounds and the acoustic crossing are not the protection. When the fit cannot meet it, fix a damped protective high pass and fit only the remaining elements. That removes freedom from the voicing, so check early whether targets such as the crossing phase remain reachable. When a screen runs on a different grid or model from the app that scores the candidate, give the screen a margin, or recheck the shortlist with the app before selection. Apply the maker's condition as a hard screen in ranking and candidate selection as well as in the search, not as a weighted penalty that better figures elsewhere can buy back. Where a level pad follows the high pass, also compare the absolute drive the driver receives with the maker's rating condition. The figures to check come from the driver's own data and the brief, not from another project.

First establish what the maker's condition actually qualifies: an explicit minimum protective filter, a published operating band, and the filter used for a power-rating test are different statements. A rating-test condition is not automatically a universal minimum acoustic crossing frequency. Do not transfer the quoted power rating to a different realized network without the required evidence.

When the requested change is stronger attenuation, keep the voltage reference explicit. In Astra's CA18 revision, every modeled AMT terminal voltage below 2.5 kHz fell at the same amplifier input, while the high-pass shape normalized to its own quieter passband scored worse. The latter did not establish greater absolute low-frequency exposure. Report both readings and any specified listening-level compensation; use the user's actual protection condition for the comparison rather than silently promoting a normalized diagnostic to an unrelated hard objective. This remains a linear-network comparison, not an endurance or distortion test.
