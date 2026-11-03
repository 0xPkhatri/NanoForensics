# Handoff — scientific root-cause audit complete

Read AGENTS.md and SCIENTIFIC_FINDINGS.md before further work. Branch science/root-cause-audit; source checkpoint 1dd84cf, starting build 00c4375 preserved. The subsequent acceptance checkpoint changes documentation/evidence only. All mandatory gates pass again: 32 backend tests, 9 live E2E tests (29.79 s), evaluator and Next.js production build; post-restoration TypeScript also passes, npm audit 0 vulnerabilities.

The original database inputs/public baselines and 29 pre-existing result rows are unchanged. Snapshot: runtime/science-audit/original.db; runner uses SQLite read-only access. Current benchmark verdicts remain inconclusive. Never replace them with slower-loading or higher-damping pilot outcomes. No thresholds or hidden preparations were tuned. The audit runner does not read privileged labels; only the separate evaluator reads preparation labels after decisions are fixed.

ALPHA: NVE dt-halving drift ratio ~0.25; driven half-dt still yields two temperature failures. Raw temperature includes motion plus excess fluctuations. Gamma 8 cools but enlarges force gradients. Separate rate-0.01 protocols yield 3/3 valid ALPHA runs and reduce early traction discrepancy from ~34% to ~18%; repair recovery +11.54% with CV26.63% remains inconclusive.
BETA: missing-site reconstruction and relaxed energy match pristine geometry. Nine pairs give +0.457% recovery, SNR0.0735, CV5.59%; proposed large recovery is rejected. Dominant persistent cluster centroids are not on the repaired left edge. Native Langevin streams depend on atom allocation/order, so integer-seed matching is not atomwise common noise.
GAMMA: normalization recovery -28.846% original, -28.355% fine cadence, -22.143% half-dt. Mean high-rate peak is lower, not elevated. Negative recovery is preserved. Three stochastic seeds do not establish convergence or a unique mechanism.
Force audit: full pair virial equals boundary plus mobile force moments to ~1e-15. LAMMPS dumped total forces separately expose bath contributions; omitted grip virial and kinetic terms also affect traction comparisons. No stress rescaling was introduced.

Statistical fixes: incomplete/censored cohorts cannot be reduced to convenient complete-pair means; duplicate/missing/unexpected seed labels cannot yield support. New red/green tests reproduced the prior defects. Existing gates retain identical bounds. Fresh result audits identify each failing gate numerically.

Evidence: docs/science-audit/measurements.json, raw-runs.jsonl.gz (159 captures, 111 distinct input-engine IDs; diagnostic repeats not independent), validation.txt. Research commands in SCIENTIFIC_FINDINGS.md reproduce cached measurements without changing the app DB. Deterministic physics studies disabled model calls intentionally; the saved API key was not exposed or changed. Actual live Muse inference remains unverified.

Demo restored on localhost:3000 / :8000 using runtime/demo PID/log records, without resetting original investigation state. Stop only these owned processes with `.venv/bin/python scripts/e2e_servers.py stop runtime/demo` before running the live E2E script. User's pre-existing TEST_RESULTS formatting and next-env.d.ts edits remain unstaged; repomix-output.xml remains untracked. Preserve them. New TEST_RESULTS sections were staged separately from the user's formatting changes.

No required audit work remains. Useful future research: larger predeclared independent ensembles, same-protocol spatially indexed noise coupling, validated flow-aware thermostatting in both engines, and finite-size/rate studies on newly registered datasets. These must not retroactively tune the frozen held-out cases.

## New active task: prospective demonstration V1

Read demonstrations/registration.json and PREREGISTRATION.md. No new trajectories generated at this checkpoint. One design, no post-outcome tuning. Original DB snapshotted/fingerprinted in runtime/demonstration. Separate database/API namespace required. Preserve existing user edits. Stage new sections of TEST_RESULTS separately from its pre-existing formatting changes.

V1 development baseline generation complete (9 real MD runs, ~140 s total); numerical gates pass so far. Development counterfactual evaluation running; do not generate held-out data until predictions and analysis code are locked in Git. The registered design/thresholds must remain unchanged even if development findings fail. Backend/API isolation and component geometry have 7 passing new tests. Original regression 35 passed before additional new tests.
