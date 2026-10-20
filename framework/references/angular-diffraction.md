---
id: angular-diffraction
applies_when: Predicting angular cabinet diffraction with a planar edge approximation
updated: 2026-10-20
---

# Angular edge radiation

The distributed-edge-dipole approximation gives a point source's direct factor
`(1+cos(theta))/2`. Edge contributions have opposite sign forward and positive sign
behind. For a centered circular baffle of radius L in the far field, the analytical
normalized response is

`D=(1+mu)/2 - mu/2 exp(-jkL) J0(kL sin(theta))`, `mu=cos(theta)`.

This is equation 21 of Urban et al. It tends to 1/2 in every direction at low
frequency and is continuous at the shadow boundary. It is an approximate physical
model, not an exact solution of arbitrary cabinet scattering.

The local convex-polygon extension integrates delayed edge dipoles using each
segment's subtended source angle divided by 2*pi. Segment source/receiver path
lengths remain explicit. This weighting reproduces the circular formula and the
far-field low-frequency monopole limit; its accuracy for a particular polygon must
be checked by refinement and independent BEM or measurements. The optional finite
distance spreading factor is a spherical-path extension of the far-field model.

Circular and rectangular piston factors weight the direct field and edge
illumination separately. An open thin baffle subtracts the rear-facing source,
giving `mu*(D_piston-edge_sum)`; it has opposite front/back phase and a low-frequency
gradient rolloff. The roundover transfer remains a declared first-order approximation,
not a solved curved-edge boundary.

Use `model: distributed_edge_dipole` in `baffle_diffraction`. Its `angular_model`
contains radiator directivity already, so downstream summation replaces the section's
analytic directivity instead of multiplying it twice. Existing on-axis approximation
remains available for compatibility. The new model does not represent thick side
walls, nonconvex visibility, higher-order diffraction or material absorption.

## Sources

- M. Urban, C. Heil, C. Pignon, C. Combet and P. Bauman, “The Distributed Edge
  Dipole (DED) Model for Cabinet Diffraction Effects,” *JAES* 52(10), 1043–1059,
  October 2004, equations 10–22. [Authors' publication archive](https://www.l-acoustics.com/education/scientific-resources/scientific-publications/page/2/).
  Full paper inspected; circular analytical formula supplies an independent test.
- T. Lokki, V. Pulkki and P. T. Calamia, “Measurement and modeling of diffraction
  from an edge of a thin panel,” *Applied Acoustics* 69(9), 824–832, 2008,
  [doi:10.1016/j.apacoust.2007.05.005](https://doi.org/10.1016/j.apacoust.2007.05.005).
  Independent edge-measurement validation methodology, not validation of this implementation.
- U. P. Svensson, R. I. Fred and J. Vanderkooy, “An analytic secondary source model
  of edge diffraction impulse responses,” *JASA* 106(5), 2331–2344, 1999.
  More complete edge-source formulation; the local approximation is not that solver.
