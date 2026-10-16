---
id: put-datasheet-curves-on-one-baffle-basis
date: 2026-10-02
project: neat-petite-amt-v5, neat-petite-dayton-astra
phase: research
confidence: medium
applies_when: Comparing woofers or fitting networks from manufacturers' published response curves measured on different baffles, test boxes, distances or with near-field splices
tags: [inventory, published-response, baffle-step, digitizing, sensitivity, validation]
---

## What went wrong
Woofers from several manufacturers were compared through their digitized datasheet curves, each placed on the project's own baffle model. One manufacturer measures in a small closed test box at half a metre, so its curves already contained that box's baffle step and edge ripple, and the project's model added a second step. Another manufacturer splices a near-field response below a few hundred hertz. Several records' curve levels sat 2-4 dB away from their own Thiele/Small predictions.

The comparison ranked these woofers on a mixed basis until an evaluator measured the excess rise against the T/S model. The correction then moved sensitivity in the opposite direction from the first expectation, because the test box's edge-diffraction hump sat inside the sensitivity band. Treating the test geometry as unknown left extension dependent on assumed box fronts. A later project found the manufacturer's separate test-box drawing: a generic fixture document, absent from the individual driver's datasheet. That evidence changed the correction again before candidate selection.

## What could have helped
Record each published curve's condition when the record is written: baffle or box, its size if known, distance, smoothing and splice frequency. Search the manufacturer's measurement-method and test-fixture documents before concluding that dimensions are unpublished. Match the fixture's size/volume row and coordinate orientation explicitly. Before woofers are compared or networks fitted, put every curve on one basis, for example by dividing out a modelled test-box baffle response. Known dimensions still do not make an approximate diffraction model an exact inverse of the measurement.

Check each record's curve against its own T/S model below the breakup, with excess rise and level offset as the two numbers. Where the test geometry is unknown, bracket it with plausible fronts and report the range the conclusion depends on. Keep calibration bands inside the lumped model's validity. Treat a decision that depends on the corrected region as provisional until one driver is measured on the target baffle.
