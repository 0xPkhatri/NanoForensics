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

## Prospective demonstration handoff — held-out scoring complete

Branch science/predeclared-demonstration. Latest tested integration21324d6, evidence872833f. Latest prospective lock a6e2a68 seals scientific source f551d9d and V3 development predictions. Never edit locked scientific files or rerun the design search. V1/V2 negative development studies remain archived with unopened holdouts. V3 final full-study status is NOT_VALIDATED; one held-out interior geometry passed all checks (+47.85% vs −0.61% competing recovery), boundary geometry failed recovery18% (+10.79%), pristine control correctly yielded no cause. All numerical, exact replay and finer-dt checks passed. Read docs/demonstration/v3/STUDY_REPORT.md before interpreting results. This is deterministic athermal MD, not three independent thermal observations.

Public bundles include no private preparation maps; restore on empty study DB is automatic, existing records preserved. Separate namespace /api/demonstrations and dataset dropdown retain all original cases. Report/evaluation links pass through /study-evidence. Actual UI actions request new MD unless cache reuse is explicitly selected. No live Muse inference claimed. Fresh published DEMO_501 baseline replay passed exact physical equality with LAMMPS; scripts need no hidden assignments.

Current verification:48 backend/public-data tests passed in11.08s (one dependency deprecation warning); production build and restored-next-env typecheck passed. Final live E2E10 passed82.82s; includes evidence links through port3000 and3 real fresh counterfactual replays. An earlier rerun hit macOS psutil.AccessDenied while observing a newly spawning process; test polling now retries unobservable processes but still requires actual worker identification. Failed and passing logs retained in validation.txt. No scientific code/threshold changes. A final text-only label correction identifies archived MD as stored evidence rather than current interactive work; production build/browser QA rerun.

Preview restored at http://127.0.0.1:3000 and API:8000, runtime/demo owns process records. Browser confirms DEMO_501 conclusion and real comparison curves, DEMO_502 inconclusive badge, full studyNOT_VALIDATED and explicit deterministic/no-model provenance. Scientific lock and original report/table comparisons PASS. All requested implementation/evaluation work is complete; no further design search. Original snapshot/fingerprints in runtime/demonstration; never regenerate/overwrite original data.

Useful read-only/replay commands:
- make test
- .venv/bin/python -m demonstrations.verify_preservation
- .venv/bin/python -c 'from demonstrations.lock_development import verify_lock; verify_lock()'
- .venv/bin/python -m demonstrations.replay_published
- NANO_DEMONSTRATION_DB="$PWD/runtime/reproduction/study.db" .venv/bin/python -m demonstrations.restore

Stop only owned preview before E2E: .venv/bin/python scripts/e2e_servers.py stop runtime/demo. E2E clones both original and study DBs and cleans launched processes. Restore afterwards with .venv/bin/python scripts/e2e_servers.py start runtime/demo. User next-env saved at runtime/demonstration/next-env.d.ts.original must be restored after build; user's TEST_RESULTS formatting must remain unstaged (stage own appended sections via index blob only). repomix-output.xml is user-owned and untracked. Do not expose .env credentials. None of the scientific failures justify changing thresholds, frozen data or the source lock.
