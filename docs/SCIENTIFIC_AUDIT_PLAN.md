# Scientific diagnosis audit — 2026-11-04

Starting source checkpoint: 00c4375; branch science/root-cause-audit. Preserve frozen specimens and baseline result JSON byte-for-byte. No reads of privileged preparation labels are needed. Runtime snapshot and fingerprints: runtime/science-audit. Existing user changes to TEST_RESULTS.md, next-env.d.ts and repomix-output.xml are retained.

Predeclared tests, before new outcomes:

1. Reproduce all existing physics, verifier and investigator tests using an isolated DB clone.
2. Measure ALPHA raw, affine-stream-subtracted and local-flow kinetic temperatures; retain the existing raw-temperature acceptance gate. Check dt halving at equal physical warmup, NVE duration and logging cadence. Compare increased damping as a separate physical protocol sensitivity, not a replacement frozen benchmark.
3. Validate geometric reconstruction against an independent observable pristine lattice; compare relaxed energies, permutation sensitivity and added-atom stochastic matching. Expand BETA repair observations using six additional seed labels, reporting raw effects and uncertainty without tuning verdict thresholds.
4. For GAMMA, refine sampling and timestep at matched physical intervals; compare peak/strain/reaction traction and failure time. A longer high-rate failure strain alone does not establish inertial overshoot or a repair opportunity.
5. Preserve unavailable evidence as unavailable. Add invariant-based regression tests for any proven implementation defects, then rerun all tests, evaluator, frontend build and live E2E.

Initial measurement: geometry reconstruction error <=1.8e-15; relaxed Hausdorff distance <=1.4e-14; both repaired structures share pristine minimized SFLJ energy -371.99870992023034. This validates edit geometry, not a predicted increase in ductility. ALPHA baseline raw temperature error is 0.3575 / 0.2672 / 0.3559; its NVE drift is 2.5e-7 to 1.0e-6, below unchanged 1e-3 bound.

## Sequential follow-up chosen from measured force gradients

The original/damping controls show large grip-vs-virial gaps, increasing with damping. Before interpreting this as a normalization error, verify the exact full-system virial identity: configurational stress equals the sum of boundary-force and mobile-force moments. Retain the prescribed mobile-only virial and all original thresholds. Separately test rate 0.01 for every frozen input, with matched geometric repair when applicable, to examine whether slower loading reduces body-force gradients without stronger Langevin drag. These are explicitly new protocols; no outcomes are substituted into frozen records or claimed as held-out benchmark wins.
