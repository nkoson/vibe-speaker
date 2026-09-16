---
id: passive-radiators
applies_when: Choosing, sizing, tuning or placing a passive radiator, or reading a passive-radiator alignment result
updated: 2026-09-15
---

# Passive radiators: sizing, tuning and where to put one

A passive radiator is a vented box in which the air mass in the duct is replaced by a suspended
diaphragm with its own mass and compliance. Small analysed and synthesized the alignments; the
system is a close relative of the vented box and reaches similar low-frequency performance, with
three differences that matter to a designer: it has no duct to fit or to make noise, it adds a
parameter that a duct does not have, and it has a notch in its response that a vented box does not.

## 1. What the radiator adds to the model

**Physics.** The radiator contributes a mass-compliance resonator in parallel with the box. Two
consequences follow.

First, the system tuning is set by the radiator's total moving mass against its own suspension
compliance *and* the box air compliance together. Adding mass lowers the tuning; the sensitivity is
roughly `-fb / (2 M)` hertz per unit mass, so a heavy radiator is a coarse adjustment and a light one
a fine one.

Second, the radiator's own suspension resonance — its mass against its compliance alone, with no box
— puts a **null in the system output below the box tuning**, where the radiator's contribution
cancels the cone's. Below that null the response falls faster than a vented box's fourth-order
roll-off. The null is a property of the part plus the mass you add to it, not of the box.

**What the framework reports.** `lf_box` with `enclosure.type: passive_radiator` returns, under
`results.radiator`, the `required_added_mass_g` for the tuning you asked for, the resulting
`total_moving_mass_g`, `null_hz` for the notch above, and `tuning_sensitivity_hz_per_g`. See
`simulations/lf_box/README.md`.

**A check that has to be made every time.** `required_added_mass_g` can come back **negative**. That
means the radiator's own mass and compliance already tune the box below the frequency you asked for,
and reaching your tuning would require removing mass from the part. The response is still computed,
so a negative value is the only thing that tells you the alignment cannot be built with that
radiator in that volume. Read the sign before reading the curve, and either pick a lighter or
stiffer radiator, ask for a lower tuning, or change the volume.

## 2. Sizing: displacement first, then compliance

**Physics, and the primary rule.** Near the tuning frequency the cone barely moves and the radiator
does nearly all the work, so the radiator travels *further* than the driver. Small's requirement is
therefore explicit: the radiator should have a suspension of high compliance and low mechanical
losses, and **a linear volume displacement limit at least twice that of the system driver**.

Volume displacement is `Vd = Sd * Xmax`, and both terms count. A radiator of the same nominal
diameter as the driver has about the same `Sd`, so it meets the rule only if its linear travel is at
least twice the driver's. Current practice among manufacturers and design guides is to size for two
to three times the driver's `Vd`, which is the same rule with margin for the fact that published
`Xmax` figures are not measured the same way by everybody.

**Practice, with its reason.** Where one radiator cannot supply the displacement, two smaller ones
are the usual answer, and they also let the pair be mounted opposite each other. Where a brief
allows only one, the displacement requirement decides the radiator, and the radiator then decides how
loud the bass can be before the *radiator*, not the driver, is the limit.

**What to read.** Give `lf_box` the radiator's `radiator_xmax_mm` in `limits` and read
`linear_scaling_to_limits`: it reports the drive voltage at which each limit is reached and which
one arrives first. A design whose radiator limit arrives before its cone limit is a design whose
radiator is too small, whatever the response curve looks like. Note that a published figure called
`Xmech` or "mechanical travel" is not a linear excursion limit, and using it as one overstates the
output.

## 3. Losses, mass and what the model does not contain

Small asks for low mechanical losses because the radiator's `Qmp` damps the alignment the way a
duct's losses damp a vented box, and a lossy suspension costs output near tuning. The mass is added
at the centre of the diaphragm on the fitting the manufacturer provides.

The lumped model contains none of the radiator's own misbehaviour: no diaphragm breakup, no
suspension non-linearity, no change of compliance with excursion or with age, and no rocking mode.
Those are the mechanisms that make a real radiator differ from its model near its limits, and they
are the reason the tuning has to be confirmed on the finished box — by the impedance minimum between
the two low-frequency peaks — rather than assumed from the mass that was fitted.

## 4. Where to mount it

This is the decision most easily got wrong, because the one argument that is easy to compute says
that it does not matter.

**What does not decide it.** At the tuning frequency both the cone and the radiator are acoustically
small and their separation is a small fraction of a wavelength, so they sum almost perfectly whatever
panel each is on. A 300 mm separation is a twentieth of a wavelength at 40 Hz. Placement cannot be
justified by the acoustic sum at tuning, and it cannot be dismissed by it either.

**What does decide it.**

*Boundary loading.* Allison measured what happens when the panel carrying a radiating surface faces a
nearby wall: the space between the panel and the wall acts as a conical horn, loading the source and
producing a large peak in power output. Turning the cabinet so that a side faces the wall restored
essentially the true half-space response. A rear-mounted radiator is exactly that configuration, and
a floorstanding speaker is usually placed with its back to a wall. If a radiator goes on the rear
panel, the minimum wall distance is part of the design and belongs in the documentation; if the
speaker must work close to a wall, the front or a side panel is the safer choice. The same paper
gives the distances at which a boundary stops helping: support falls to the free-space value at a
quarter wavelength and is slightly negative out to half a wavelength.

*Reaction force.* A moving diaphragm pushes the cabinet the other way. A radiator mounted on the same
axis as, and facing opposite to, the driver cancels most of that reaction force; a radiator on a
different panel or at a different height leaves a couple that rocks the cabinet. Nothing in this
framework models it, so it is a reason to prefer opposed or close mounting rather than a number to
report.

*Panel strength.* A radiator cutout removes most of the area of the panel bay it sits in and replaces
it with a compliant diaphragm. Putting it in the largest, least braced bay is the worst case for
both panel radiation and the radiator's own frame support. Check it against the bay layout in
`plate_structure` rather than deciding it from the elevation.

*Inside the box.* The radiator needs its swept volume clear behind it over the peak excursion the
alignment predicts, with margin, and its static body volume counted in the net volume — see
`cabinet-geometry.md`. It should also not sit in the woofer's direct near field, because above tuning
the diaphragm is a compliant membrane that transmits whatever the chamber does to it. `cavity_modes`
reports `outlet_relative_db` for the radiator's position; a large figure there is chamber sound
reaching the outside through the radiator, not bass.

**Practice, with its reason.** Same-baffle mounting close to the driver is the most predictable
choice: it keeps the pair close, keeps the radiator off the wall, and lets both flanges be carried by
the stiffest panel. Rear mounting buys baffle area and a shorter cabinet and costs the wall-distance
constraint above. Side mounting, or an opposed pair, is what a design chooses when reaction force or
a narrow baffle dominates. Each of the three is defensible; picking one without naming which of these
mechanisms drove it is not.

## 5. Making a placement claim

Write down, before freezing: the radiator's `Vd` against the driver's, with the source of each
`Xmax`; the `required_added_mass_g` and its sign; the null frequency; the predicted radiator
excursion at the stated drive and which limit arrives first; the panel it is on and the minimum
distance to a wall that panel implies; the swept volume clearance behind it; and which bay of the
panel layout it occupies. Those are the numbers a reader needs in order to disagree.

## Sources

- Small, R. H., "Passive-Radiator Loudspeaker Systems Part I: Analysis", *Journal of the Audio Engineering Society*, vol. 22, no. 8, pp. 592-601, 1974 — the model, the compliance ratio, the requirement for high compliance and low mechanical losses, and the volume displacement rule. <https://aes2.org/publications/elibrary-page/?id=2731>
- Small, R. H., "Passive-Radiator Loudspeaker Systems Part II: Synthesis", *Journal of the Audio Engineering Society*, vol. 22, no. 9, pp. 683-689, 1974 — the alignments and how the added mass sets them.
- Allison, R. F., "The Influence of Room Boundaries on Loudspeaker Power Output", *Journal of the Audio Engineering Society*, vol. 22, no. 5, pp. 314-320, 1974 — the boundary curves and the measured penalty for a radiating panel facing a wall. <https://aes2.org/publications/elibrary-page/?id=2760>
- Thiele, A. N., "Loudspeakers in Vented Boxes, Parts I and II", *Journal of the Audio Engineering Society*, vol. 19, nos. 5 and 6, 1971 — the vented alignments the passive-radiator alignments extend.
- Dickason, V., *The Loudspeaker Design Cookbook*, 8th ed., Audio Amateur Press — current practice on radiator sizing, mass fitting and confirming the tuning by impedance.
- The manufacturer's drawing and parameter sheet for the radiator in hand, for `Sd`, the linear and mechanical travel figures and the mass-fitting arrangement. Nothing here replaces it, and a figure labelled mechanical travel is not a linear limit.
- In this repository: `simulations/lf_box/README.md` for the radiator inputs and the `linear_scaling_to_limits` output, `simulations/cavity_modes/README.md` for the outlet model, and `references/cabinet-geometry.md` for the swept volume and displacement accounting.
