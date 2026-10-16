---
id: bound-unvalidated-geometry-models
date: 2026-10-01
project: neat-petite-amt-v4
phase: design
confidence: low
applies_when: Modelling a geometric feature (a sunk driver pocket, a recess, a short duct or a mounting ring) with an app option built for a different geometry
tags: [model-limits, diffraction, recess, risk, measurement]
---

## What went wrong
A woofer flange sunk into a pocket was first modelled with a diffraction app's recess option, which was built for a recessed tweeter (a rigid tube with a piston at its bottom). It produced several decibels of change through the crossover region and a different network. The build was redone with the pocket as extra acoustic depth only, and that choice decided whether the selected design met its bass target. The evaluation later showed that the scored network would miss that target if the tube model were right. One model was picked, and the other became a residual risk.

## What could have helped
When no model fits the feature, run the plausible bounding models and carry the spread: a network fitted to each, the objectives under each, and which objective flips. Record the feature as a measurement item with a concrete check, for example measuring the mounted driver on the real baffle before the network is frozen. Prefer a design margin that survives both models when the brief allows it. This exposes the risk; it does not make either model validated.
