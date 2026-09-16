---
id: validation-reruns-are-not-design-iterations
date: 2026-09-14
project: forte-iii-three-way
phase: process
confidence: low
applies_when: A model or input error is found after design iterations have started
tags: [process, iterations, budget, corrections]
---

## Observation
Three iterations were requested. Two of them were spent discovering the propagation, normalization and source errors; their candidates were re-evaluated with corrected models but not redesigned. The count of three was preserved mechanically while only one iteration explored validated alternatives.

## Why it mattered
The user asked for three rounds of design exploration and effectively received one. The iteration counter measured work done, not design learned.

## Advice
When a correction invalidates the feedback that earlier candidates were designed against, consider recording it in the project log as a model correction and asking the user whether the affected iterations should count, rather than deciding silently either way. Keep the corrected re-evaluations of old candidates as history, and treat a genuinely new candidate designed against the corrected model as the unit of an iteration. Validating the chain before iteration one makes the question rare.

## Evidence
- `framework/projects/forte-iii-three-way/postmortem.md`, reason 6
- `framework/projects/forte-iii-three-way/reference/simulation-audit.md`, last paragraph
