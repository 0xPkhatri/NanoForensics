# Scientific diagnosis audit — measured findings

The frozen cases still do not justify a unique diagnosis. The audit explains why, improves physical observability, and fixes two statistical integrity defects without changing verdict thresholds. Frozen specimen inputs, public baseline JSON and 29 existing immutable result records were checked byte-for-byte against the snapshot. This is post-benchmark sensitivity analysis, not a new held-out discovery claim.

| Question | Measurement | Supported interpretation |
|---|---|---|
| ALPHA integration instability? | Same-microstate, equal-duration NVE drift falls from 7.1231e-7 to 1.7809e-7 when dt halves; driven dt refinement still fails the raw-temperature gate in 2/3 seeds. | No evidence of a divergent integrator. The failed gate concerns driven kinetic temperature. |
| ALPHA thermal-control improvement? | At strain rate 0.01, temperature-error ratios are 0.036–0.046 versus 0.267–0.358 originally; valid baseline runs increase from 1/3 to 3/3. Early grip/virial discrepancy falls from roughly 34% to 18%. | Slower loading is a demonstrably cleaner **separate protocol**; it does not repair the frozen baseline retroactively. |
| Is stronger damping a free numerical fix? | Gamma 8 yields ALPHA temperature errors 0.008–0.016, but early grip/virial gaps grow to about 52%. | It changes mechanics and cannot be presented as an equivalent, improved benchmark. |
| BETA missing-site reconstruction bug? | Inserted coordinates match observable pristine sites within 1.8e-15; relaxed energy is -371.99870992023034 for both repaired and pristine structures. | Geometric repair is effective. A predicted ductility increase does not follow from geometry alone. |
| BETA repair after more seeds? | Nine pairs: baseline failure strain 0.182222; repaired 0.183056; recovery +0.457%; paired SNR 0.0735; CV 5.59%. | The hypothesized large recovery is rejected under the unchanged rule. Eight of nine baseline persistent-cluster centroids are interior, one is surface-right; the repaired left edge is not the measured dominant initiation site. |
| GAMMA a sampling artifact? | Rate normalization recovery: -28.846% original, -28.355% with five-step sampling on both arms, -22.143% with half-dt on both arms. | The adverse effect survives these controls; its magnitude is not fully converged with three stochastic seeds. |
| GAMMA inertial peak-stress overshoot? | Original high-rate mean peak stress 1.69088; normalized-rate mean 2.87739. | The measured peak shifts upward on normalization, opposite the hypothesized overshoot removal. A slower rate gives cracks more physical time; the present data do not establish a unique causal mechanism. |
| Can traction and virial be made equal by a constant factor? | Full pair virial = boundary-force moment + mobile-force moment to ≤1.2e-15. Mobile-only stress also excludes grip virial and includes a negative tensile-sign kinetic term. Total LAMMPS forces separately expose thermostat and realized force moments. | Non-equilibrium force moments and boundary selection explain the mismatch. Arbitrary stress rescaling would be wrong. |

The thermal audit records laboratory kinetic temperature, COM-removed temperature, affine-stream residual, four-band local-flow residual, and the exact affine kinetic decomposition. For ALPHA, local-flow residual means are 0.059–0.063 instead of raw 0.063–0.068; flow contributes but does not explain all excess kinetic energy. The laboratory-frame thermostat and the fixed temperature diagnostic are coupled to loading motion. Affine subtraction can also be misleading when the actual flow is non-affine; none of these supplemental quantities replaces the original gate.

At slower loading, ALPHA repair recovery is +11.54%, but CV is 26.63%: neither the unchanged 18% recovery nor the ≤12% CV requirement is met. BETA slower-loading repair recovery is +3.04%, with CV 22.32%. These pilots remain inconclusive and are not used to retune preparations, lattice size, rates or acceptance assertions. DELTA remains thermally noisy: its short trajectories and seed variability do not support a unique causal repair.

Added atoms change the native stochastic stream allocation. As an ordering control, the same pristine geometry with canonical ordering gives seed-42 failure strain 0.190 versus 0.180 for the appended-order BETA repair. This is a change of stochastic realization, not geometric repair failure. Equal integer seeds do not ensure atomwise identical thermal noise across different atom counts/IDs. The nine-pair estimates are descriptive; a spatially indexed common-noise implementation or larger independent ensembles would be needed to reduce this limitation.

The verifier previously selected complete pairs even when other runs were censored or invalid, and did not reject duplicate/unexpected seed labels. Regression tests first reproduced both defects. It now withholds naive failure-strain means/recovery whenever the cohort is incomplete and requires exactly the registered unique seed set. Numerical failure, censoring, seed availability and scientific verdict remain distinct. No SNR, CV, recovery, force, displacement or temperature bound was loosened.

Measurements and provenance: [compact data](science-audit/measurements.json), [compressed raw runs](science-audit/raw-runs.jsonl.gz). Recorded artifacts include repeated captures of the same input/seed under supplemental diagnostics; they are not all independent realizations. See the distinct input/engine ID count in the compact data. Raw curves, snapshots, numerical checks, thermal series and force moments are retained. There are no synthetic stress curves or ground-truth reads in the audit runner.

Reproduce on the existing frozen database (the runner snapshots it once and reads the snapshot in SQLite read-only mode):

```sh
.venv/bin/python -m benchmarks.audit_science --phase controls
.venv/bin/python -m benchmarks.audit_science --phase repairs
.venv/bin/python -m benchmarks.audit_science --phase balance
.venv/bin/python -m benchmarks.audit_science --phase slow
.venv/bin/python -m benchmarks.report_scientific_audit
```

The thermostat interpretation follows LAMMPS documentation: [temperature profiles](https://docs.lammps.org/compute_temp_profile.html) and [Langevin velocity-bias support](https://docs.lammps.org/fix_langevin.html). A profile-unbiased thermostat would require separate validation in both engines; it has not been silently substituted into this benchmark.

Verification: 32 backend tests and 9 live E2E tests PASS; evaluator completes with 0 correct / 0 incorrect / 4 NO_DECISION for each method. Production frontend build, npm dependency audit (0 vulnerabilities), and post-restoration TypeScript check PASS. Logs: [validation.txt](science-audit/validation.txt). The local demo was restored at http://127.0.0.1:3000 without resetting original investigation state. Physics studies intentionally used deterministic tools without model calls; live Muse execution was not validated by this audit.
