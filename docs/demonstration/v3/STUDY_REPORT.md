# Prospective athermal demonstration V3: partial mechanistic evidence

**Full study: NOT_VALIDATED.** One held-out defect geometry met every registered physical and mechanistic criterion, the pristine negative control passed, and the second defect geometry remained inconclusive. No cases, arms, seed labels, failed development studies or negative effects were removed. The original CASE_ALPHA–DELTA specimens, baselines, 29 pre-existing result records and benchmark report remain unchanged.

## Prospective design and provenance

The original scientific-audit checkpoint is `f4fbbca`. V1 was preregistered at `b879104` and failed its development distinction criterion. Its single-row banks remained within the SFLJ cutoff (about 1.86–1.91 sigma); filling the gap did not establish the proposed uniquely dominant repair. V2 was independently preregistered at `522d133` with a two-row open slot and lower temperature. It failed supplemental temperature validation during development. Neither study's held-out partition was generated. Their registrations, negative decisions and public MD archives remain available in the parent and V2 evidence directories.

V3 was prospectively registered at `e17fc8b`, before its trajectories. Registration SHA-256: `7d87eea832b65b65550879f453c53e7546ced33a3439953995bb5c74f7347a49`. Scientific source `f551d9d998bf59c4097acc2dd54c7a59602c8e04` and development predictions were sealed by `a6e2a68`, before held-out generation. `demonstrations/v3/development-lock.json` records source hashes; held-out generation and scoring verify them.

An initial development analysis incorrectly required exactly one individually supported repair. The preregistration instead required a uniquely dominant contrast, allowing both repairs to be beneficial. This implementation error was corrected before the holdout was generated. No hypothesis, threshold, MD result or individual verification changed; zero additional MD runs were used for the correction. Both initial and corrected decisions, hashes and the correction explanation are retained. This correction is not evidence from an untouched development analysis; the subsequent held-out test remained prospective.

## Physical question and registered protocol

Can geometry-inferred reconstruction distinguish an interior transverse bond-network disruption from a boundary-connected stress concentration? Each defect specimen has a large two-row, six-column missing-site component and a competing one-site component of the other topology. A pristine specimen is a negative control. These are deliberately strong geometric interventions, not replicas of the original small-defect benchmark. Observable coordinates determine candidate sites and boundary connectivity; live tools receive no pristine site IDs or private family assignments. The generator/scorer owns private assignment files. Scoring follows frozen blind investigator decisions and timestep-refinement decisions.

All specimens use a 16×20 hexagonal 2D shifted-force Lennard-Jones lattice, cutoff 2.5 sigma, mass/epsilon/sigma in LJ reduced units. The unchanged production force engine and LAMMPS `lj/smooth/linear` template generate the actual trajectories. No stress curve is synthesized. Protocol: dt=0.002, target T=0, engineering strain rate=0.005 per LJ time, strain horizon=0.35 (70 LJ time), sample every 50 steps, warmup 4000 steps, gamma=2, pre-load NVE 500 steps, force-converged minimization tolerance=0.005. Free lateral boundaries and prescribed opposed grips use mobile-only damping. This is athermal finite-rate damped dynamics, not quasistatic equilibrium or thermal ensemble sampling.

After NVE, the opposing banks of each large slot must remain farther apart than the interaction cutoff. Reference-bond fracture detection, virial sign/normalization and numerical thresholds are unchanged: NVE drift <0.001, maximum force <10000, step displacement <0.1, raw kinetic gate <0.35. At T=0 that gate explicitly uses the existing 0.01 temperature scale; no relative error to a zero target is claimed. Pair-force moment identity residual must be <1e-8. The identity accounts for mobile force moments and omitted grip virial; it does not assert static equality of mobile stress and grip traction during damped loading.

Fracture requires the fixed retrospective global-peak load drop to 65%, accompanied by a reference-connected cluster of at least four actively ruptured mobile atoms persisting across three samples. Runs without confirmed fracture retain null failure strain. No final horizon value substitutes for a failure event.

Development used row 9 and replay labels 5801–5803. Held-out used the unseen row-8 shift and labels 6801–6803. Each three-label block tests **exact deterministic replay**, not three independent thermal samples. No population interval or statistical confidence claim is justified. Repair support requires recovery ≥18%, floor-normalized SNR ≥2.5 and CV ≤12%; identifying the dominant tested repair additionally requires ≥10 percentage points over its competitor and contrast SNR ≥2.5. The fixed strain floor is 0.004. Support indicates a dominant tested counterfactual at this protocol, not a sole physical cause.

Every held-out baseline and applicable repair was also run at dt=0.001 with doubled warmup, NVE and sampling step counts, preserving physical durations. Registered convergence limits: absolute failure-strain difference ≤0.01, relative peak-stress difference ≤5%, and the same dominant decision. No-op arms remain visible without imaginary repairs. All geometries must pass for full validation.

## Held-out measurements

| Case | Baseline failure strain | Interior repair strain / recovery | Boundary repair strain / recovery | Registered result |
|---|---:|---:|---:|---|
| DEMO_501 | 0.0815 | 0.1205 / +47.85% | 0.0810 / −0.61% | Correct interior distinction; all case-level criteria pass |
| DEMO_502 | 0.1205 | 0.1065 / −11.62% | 0.1335 / +10.79% | INCONCLUSIVE; boundary improvement below 18% |
| DEMO_503 | 0.1190 | No applicable edit | No applicable edit | Correct negative control; no identified cause |

DEMO_501 interior-repair SNR is 9.75 versus boundary-repair SNR 0.125; the competing recovery advantage is 48.47 percentage points. DEMO_502 boundary-repair SNR is 3.25 and interior-repair SNR is 3.50, but neither satisfies the complete support rule. A negative effect with large magnitude is not positive recovery. The boundary hypothesis remains inconclusive rather than being forced to pass or reject. The pristine no-op is an availability status, not experimental evidence rejecting every possible mechanism.

All held-out baseline/applicable-arm cohorts were numerically valid, uncensored and exactly replayable. All seven finer-timestep trajectories passed the registered convergence checks. Maximum failure-strain difference was 0.0005 (one original measurement interval); maximum relative peak-stress difference was 0.0000167451 (0.001675%). These convergence results support numerical stability of the measured effects; they do not rescue the failed boundary-recovery criterion.

Across the 21 coarse held-out raw replay records and seven refined trajectories, measured maximum force was 9.0807, maximum step displacement 0.002151, maximum NVE energy drift 2.82e-16, and maximum raw kinetic-temperature ratio 0.174613. The minimum applicable post-NVE opposing-bank separation was 3.0294 sigma, above the 2.5 cutoff. The maximum pair-force moment identity residual was 1.52e-15. These are extrema over retained records, not 28 independent physical observations.

Counts: **1 correct distinction, 1 correct negative control, 1 no decision, 0 incorrect diagnoses**. The full study remains **NOT_VALIDATED**. No additional design search follows this result. See [held-out scoring](held_out-evaluation.json), [blind decisions](held_out-decisions.json), [refinement and raw runs](held_out-refinement.json), and [status](status.json).

## Reproducibility, software and preservation

The fresh registered development rerun matched the stored physical record exactly. A further fresh held-out LAMMPS baseline replay from the published public bundle also matched exactly, without private preparation access; see `published-replay.json`. Replay excludes timing, process identifiers and other execution metadata, and includes the physical quantities selected by `demonstrations.reproduce.physical_record`. Exact equality is an observation on this engine/version/host, not a portability guarantee across machines or engines.

The public checksummed bundle contains six observable specimens, immutable raw/aggregate results and blind investigation states. Startup restores it only into an empty demonstration database; existing data are preserved. It contains no private preparation maps. V1/V2 public archives preserve negative evidence. Interactive demonstration operations use a separate API/database/job namespace and execute real MD when fresh recomputation is requested. The dashboard distinguishes original benchmarks, development/held-out status, whole-study failure and case-level evidence, cached/fresh results, and deterministic tools with no model inference.

Measured original-step runtime is 14.41–15.99 seconds per raw run; the 3–12 second target was **not achieved**. The physical horizon was retained. Per-run deadlines are 90 seconds and interactive job deadlines 900 seconds within the investigation budget. Timings and registered source/protocol/configuration hashes remain in raw records.

Final software verification and original-table fingerprints are recorded in `validation.txt` and the project test log. The original evaluator was rerun using a database snapshot; its separate regression reports retain four NO_DECISION outcomes for every method. Its original reports were preserved rather than replaced by the rerun. Original specimen hash: `06c6553d2d4d6bde43d7714d18586b30d931e12151f7f186fecaabd11f77f10c`; original 29-result hash: `a54344e1d6ec5e240c7cd0ddf8e63925eaccf1327bbe5645ea0c5a9e820c38ec`.

## Scope and remaining limitations

This supplies one validated held-out **interior-repair geometry** and an honest negative control, not a fully validated two-mechanism demonstration dataset. The boundary repair's subthreshold improvement is a remaining scientific limitation, not a software failure. One-row geometric generalization is narrow; exact athermal replay does not demonstrate independent thermal robustness. Small lattices, finite loading rate, damping, discrete measurement cadence and reconstruction assumptions limit interpretation. No real-material predictive validity, superiority over model baselines or verified live Muse Spark inference is claimed. The finite-temperature failures from V1/V2 and all four original inconclusive benchmarks remain part of the evidence.

## Reproduce without modifying published evidence

```sh
make test
make build
# Stop owned preview first, then use an isolated copy of the original DB:
NANO_DB="$PWD/runtime/demonstration/original-snapshot.db" bash scripts/verify_e2e.sh
.venv/bin/python -m demonstrations.verify_preservation
.venv/bin/python -c 'from demonstrations.lock_development import verify_lock; verify_lock()'
.venv/bin/python -m demonstrations.replay_published
# Restore the public bundle only into a separate empty study DB:
NANO_DEMONSTRATION_DB="$PWD/runtime/reproduction/study.db" .venv/bin/python -m demonstrations.restore
```

Original-snapshot.db is a local checkpoint artifact. On another machine select its independently preserved original DB rather than overwriting published benchmarks. Published registrations, decisions and scoring refuse overwrite. Re-generating preparation/score studies belongs in a separate named research checkout with the registration and scientific lock preserved; public replay needs no hidden assignments.
