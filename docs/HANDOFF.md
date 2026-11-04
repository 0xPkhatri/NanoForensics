# Handoff — scientific root-cause audit complete

## Investigation controls follow-up — 2026-11-04

Moved investigation mode controls directly after Workspace/Sample. Primary action is Run full investigation, changing to View results when complete with Investigate again retained. Renamed manual disclosure Explore step by step; reset is a quiet secondary action inside it with confirmation and preservation wording. Removed duplicated action controls from the lower page/status banner. Backend behavior unchanged.

Validation: production buildPASS, TypeScriptPASS,6 UI logic testsPASS; live previewHTTP200 and served-markup ordering/labelsPASS. Existing next-env bytes restored. Browser visual QA remains unverified due the previously documented browser-tool issue; no full backend/E2E rerun for this frontend-only placement/copy change.


Latest verified redesign source checkpoint: `b94578b` on `design/frontend-simplification`. Build/typecheck,6 UI logic,56 regression and11 live HTTP checks passed. Rendered browser QA remains blocked; preview uses isolated copies. The following continuity commit changes documentation only.

## Latest task: redesign implementation on design/frontend-simplification

Implemented the user-approved plan; prior frontend stays on science/predeclared-demonstration. Read docs/FRONTEND_REDESIGN_IMPLEMENTATION.md for delivered files, tests, preview ownership, limitations and rollback precautions. Automated gates:6 UI checks,56 regression tests,11 live HTTP tests, production build and typecheck pass. Original4 specimens/29 results preserved; all12 task source DB tables unchanged. Historical preservation script already failed before tests on original states; do not overwrite those user states to force agreement.

Previewlocalhost:3000/API:8000 is owned by runtime/frontend-redesign/preview and uses preview-original/study/rehearsal.db copies, new provider calls disabled. Prior runtime/demo owned processes were stopped for isolated testing. No real provider invocation or scientific-code change. User TEST_RESULTS formatting, next-env bytes and repomix file remain uncommitted and preserved; snapshots in runtime/frontend-redesign.

Remaining limitation: browser transport fails on navigation/DOM/screenshot with timeoutMs error, including after troubleshooting and fresh binding. Do not claim screenshot/mobile visual QA. Human comprehension targets not measured. Next action is rendered desktop/mobile review when browser works; do not redo MD or tune scientific outcomes.

## Latest task: frontend redesign plan complete (2026-11-04)

User requested analysis of PlantDebugger GitHub/video and one detailed plan to simplify NanoForensics. Deliverable: docs/FRONTEND_REDESIGN_PLAN.md. Reference source inspected at d69507aa48aec773a5cf72761e5ff60c491eefc1 in /private/tmp/nanoforensics-plantdebugger-reference. Video inspected using 12-second sampled contact sheet plus full-resolution frames at24/72/108 seconds; no audio transcription claimed. Current frontend source reviewed; preview port3000 was offline, so no rendered current-dashboard QA was completed.

Plan adopts the light Commander style, not the reference's older dark homepage: cream sheets, charcoal NOW banner, blue actions, orange current-test highlights, simple copy, material/evidence/next-test composition and three views. It preserves all science, namespace separation, uncertainty, per-action provenance and full-study NOT_VALIDATED. No application code was changed. Implementation is pending, beginning with phases1–2 in that plan. Suggested next reads: `cat docs/FRONTEND_REDESIGN_PLAN.md` and `git status --short`. Follow its phase gates during implementation. Preserve pre-existing TEST_RESULTS formatting, next-env changes and repomix-output.xml.

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

## Completed follow-up: genuine live Muse rehearsal

User requested live hypotheses, planning, evidence revision and a polished DEMO_501 hackathon walkthrough while preserving all science. New code in backend/live_muse, third dashboard dataset, AI action receipts and guided steps. Do not edit backend/demonstration or other locked source. Provider configuration was missing; verified https://api.meta.ai/v1 and muse-spark-1.3 in official Meta docs and added them to ignored .env. Existing key never exposed. Tiny probe token budgets returned reasoning-only/null content; transport now uses minimal reasoning, validates finish_reason/model identity and retains usage even on failure.

Real acceptance completed: python -m scripts.verify_live_muse,6 fresh counterfactual MD replays,121.95s. Hypothesis call8.917s, planning5.100s, revisions7.459s/6.716s; all schema-valid LIVE_MUSE_SPARK_API. Model independently chose boundary repair first, revised on−0.61%, then increased interior score0.35→0.92 on+47.85%. Independent verifier still decides statuses. Scores are subjective, case already published; no new blind validation. Full study NOT_VALIDATED.

Evidence in docs/live-muse/{acceptance-summary.json,action-trace.json.gz,preservation.json}; runtime/live-muse/rehearsal.db isolates mutable AI states and copies of real immutable MD. Main initializes from public bundle only into empty workspace; no study decisions copied into AI state. CLI acceptance uses real service; mocked provider unit tests are explicitly contract tests, not integration proof. Source/study table snapshots at runtime/live-muse; verify all4 tables and frozen Git evidence using python -m scripts.verify_rehearsal_preservation.

Final verification:56 regression testsPASS13.28s (one dependency deprecation warning), production build/typecheckPASS, original evaluator with separate outputs4 NO_DECISION per method, live full-stack11PASS83.19s. E2E isolates all3 DBs with provider disabled; real service acceptance is separate. Additional actual HTTP-worker hypotheses/planningPASS on DEMO_401; no new MD in that check. Browser inspected new live receipts, actual plots, guided steps, fullNOT_VALIDATED and frozen-study no-model telemetry. Owned runtime/demo preview restored on3000/8000; tab left on liveDEMO_501.

Model quality review found an initial localization error (surface notch wrongly placed on reported crack side). Original transcript retained. Added explicit visible component centroids/side; first grounded rehearsal had one locally invalid revision/fallback and remainsNOT_VERIFIED. Its rejected payloads were not retained in the earlier receipt format, so exact validation subtype is unknown; do not claim a specific cause. Receipts now retain parsed attempts and distinct retry request hashes. Revision schema restricts evidence IDs to completed experiments. Final grounded actual-provider rehearsal passed all4 calls with explicitly reused immutable MD. Initial fresh run still proves6 actual counterfactual MD executions. Later budget_used_sec is cumulative across workspace runs. No blind discovery or full-study success claim.

Latest accepted source/evidence/walkthrough checkpoint d6015e3; earlier real-provider milestone b4d68ea. The following continuity checkpoint only records this accepted source. Read docs/live-muse/INTEGRATION_REPORT.md and DEMO_501_WALKTHROUGH.md. Preserve first, mixed-failure and final receipts. All frozen study Git files remain byte-identical to71779ef; all4 tables in original/study DBs match before-task snapshots. Scientific lock f551d9d verified. New mutable AI DB only:runtime/live-muse/rehearsal.db. Do not run CLI and HTTP investigations concurrently against the same rehearsal DB; select a new NANO_LIVE_MUSE_DB to preserve an existing rehearsal.

Useful commands:make verify-live-muse (real calls+freshMD); python -m scripts.verify_live_muse --reuse-md (newcalls+explicit real cache); python -m scripts.verify_rehearsal_preservation (local before-task snapshots required); make test; make build; bash scripts/verify_e2e.sh after stopping owned preview. Restore user next-env bytes from runtime/live-muse/next-env.original after builds. User TEST_RESULTS formatting and next-env edits remain unstaged; repomix-output.xml stays untracked. Do not stage wholesale or expose .env. No pending task remains. Provider availability and outputs can vary; failure must remain visible, never cherry-picked or relabeled live.

## Latest documentation task completed

User requested one comprehensive beginner-readable detail.md. Created it at the repository root, covering the objective, workflow, real MD, live/fallback provenance, all main files, three workspaces, scientific results/limitations, setup, API/storage/jobs, tests and practical use. Local links/code fences checked. This is a documentation-only addition; full study remains NOT_VALIDATED. No pending work for this request. Preserve the existing user-owned TEST_RESULTS formatting, next-env edits and repomix file.
