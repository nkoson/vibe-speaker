# References: engineering principles with sources

A reference is durable loudspeaker engineering: what the physics is, what the standard practice is, and where it is written down. It exists so that a design decision rests on the discipline rather than on whatever seemed reasonable in the moment, and so that a conclusion can be checked against a source instead of an intuition.

References are not learnings. A learning in `framework/learnings/` says what happened in one project and what to consider next time; it is written by `speaker-learnings` from a postmortem and it changes as projects accumulate. A reference says what is true of loudspeakers generally; it changes only when the engineering is stated wrongly here or a source is added. Neither is enforced by code, and neither belongs in a project's objectives: objectives come from the brief.

| Reference | Read it when |
|---|---|
| [driver-selection](driver-selection.md) | Choosing a driver from its parameters, or judging an efficiency, excursion, Xmax or power claim |
| [enclosure-alignments](enclosure-alignments.md) | Solving a bass alignment, sizing a vent, or considering a loading other than sealed and vented |
| [system-architecture](system-architecture.md) | Deciding how many sections a design needs and where the crossover frequencies go |
| [transducer-types](transducer-types.md) | Choosing or judging a dome, a compression driver, a horn or a waveguide |
| [measurement-and-model-limits](measurement-and-model-limits.md) | Reading a simulated result for what it is worth, or saying what measuring it would take |
| [cabinet-geometry](cabinet-geometry.md) | Sizing or placing anything inside or on a cabinet, and before claiming that something does or does not fit |
| [crossover-design](crossover-design.md) | Choosing a topology, fitting values, quantizing to stock, reading dissipation or impedance, or judging a crossover result |
| [baffle-and-driver-placement](baffle-and-driver-placement.md) | Choosing the baffle size, placing the drivers on it, setting the crossover frequencies that spacing has to survive, or judging an off-axis result |
| [passive-radiators](passive-radiators.md) | Choosing, sizing, tuning or placing a passive radiator, or reading a passive-radiator alignment |
| [target-response](target-response.md) | Setting the target a crossover is fitted to, or judging whether a predicted response is a good one |
| [alternative-loadings](alternative-loadings.md) | Considering bandpass, isobaric, aperiodic or cardioid loading, or judging a claim made for one |
| [horn-and-waveguide-design](horn-and-waveguide-design.md) | Sizing a horn throat, rear cavity or mouth, or deciding whether a horn model can answer the question |
| [arrays-and-directivity-control](arrays-and-directivity-control.md) | Arraying several sources of the same passband - a line array, a column, a stacked pair or an MTM |
| [cabinet-materials-and-panels](cabinet-materials-and-panels.md) | Choosing a cabinet material or wall thickness, predicting a panel resonance, or judging whether panel radiation will be audible |

## What these references cover, and where they stop

Silence here is not permission. A reference that says nothing about a topic means nobody has
established the engineering for it in this repository, not that there is no constraint. When a
decision falls outside the boundary below, say so in the candidate notes with the assumption you
made, the way you would for an unpublished dimension.

**Established and independently checked.** Thiele/Small driver selection and the efficiency law,
sealed and vented alignment mathematics, enclosure losses, vent and flared-port design, the
large-signal mechanisms of a moving-coil motor, and the IEC 62458 displacement limits. These came
through adversarial verification or from primary documents read directly. Added in the September 2026
source round, each from a primary document read at first hand and with its worked example
recomputed here: Keele's low-frequency horn design equations from Thiele/Small parameters; the
oblate-spheroidal waveguide contour and cutoff; the WST array criteria and the near/far-field border;
plate frequency parameters with edge-restraint coefficients; cabinet material moduli, loss factors
and damping-treatment data; the BBC panel-resonance audibility criterion; and AES2-2012's `Xmax` and
power-handling clauses.

**Established but unverified.** Crossover component values, compensation and notch networks, baffle
step and diffraction magnitudes, the CTA-2034-A curve-assembly geometry, measurement practice, horn
directivity, transmission lines and dipoles, the bandpass equivalent-circuit derivations, the
constraints recorded for ribbons, coaxials and full-range drivers, and the terminal and connector
conventions in `cabinet-geometry.md`. These rest on single sources -
often self-published, vendor documentation or patent specifications - and each is flagged where it is
stated. Use them, cite them, and do not treat them as settled. The **preference predictors** have
moved out of this category: they were read in Harman's own patent and agree with what was previously
recorded.

**Not covered at all.** Compression ratio, throat-cavity volume and horn efficiency as a function of
area ratio; bandpass, aperiodic and cardioid **alignment tables** (the equivalent circuits are
covered, the tabulated alignments are not); a design model for true ribbons, planar-magnetic panels,
coaxials or full-range drivers, as opposed to the constraints on them; bracing as a quantity; panel
radiation converted to an absolute SPL, which the BBC established cannot be computed from the panels
alone; a quantitative intelligibility metric tied to array geometry; and **any published figure for
how far a simulated response sits from a measured one** - a deliberate search for that figure in
September 2026 found that the comparison is conventionally reported without a number at all, which is
recorded in `measurement-and-model-limits.md` section 5.

**Claims that were checked and failed** are recorded rather than deleted, so that a popular but wrong
rule does not come back: see `system-architecture.md` section 8 for the lobing and directivity
cluster, and `driver-selection.md` sections 1 and 6 for the air-load and impedance-sweep claims.

## How to use one

Read the reference before the work it covers, not after a result looks wrong. Where a reference gives a formula, the formula is the physics and you can rely on it. Where it gives a figure that practice has settled on, it says so and gives the reason; treat that as a starting point to judge against this brief, not as a threshold to enforce or to copy into `project.json`. Where a reference says a claim needs a derivation, write the derivation into the candidate's notes, with the numbers, so a reader can check it.

Cite the reference in a project document the way you cite a result file: name it and say what you took from it. A reference is not a substitute for a datasheet. For anything about a specific part - a rating, a dimension, a curve - the manufacturer's document for that part under the condition you are using is the source, and the reference only tells you which condition to look for.

## Writing or extending one

- Sources are primary where possible: papers, textbooks, standards, manufacturer documentation. Give author, title, publication and year so a reader can find it, and a URL when the source is public.
- Separate the three kinds of statement. Physics is stated as physics. Standard practice is labelled as practice, with the reason it became standard. A judgement is labelled as a judgement.
- No project figures. If a number came from one brief, it is a learning, not a reference.
- Say what the framework's own applications do and do not model where that changes how a principle is applied, and link the application's `README.md` rather than restating it.
- Say how solid a statement is when it is not solid. Where two published conventions disagree, give both and say they disagree; where a figure is a single worked example, a vendor's default or a rule of thumb with no derivation, say so next to it. A reference that quietly launders a blog post into a design rule is worse than one that omits the topic.
- Where a claim was checked and failed, record that it failed rather than deleting it silently, so it is not reintroduced from the same popular source later.
- Every reference ends with `## Sources`. Run `python -m pytest framework/tests/test_references.py -q` after editing.
