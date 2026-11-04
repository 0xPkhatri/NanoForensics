# Project state — demonstration evaluation complete (2026-11-04)

Latest verified console source checkpoint: `f93a4f4` on `design/frontend-simplification`.60 backend/11 UI/11 live HTTP checks, build/typecheck and scientific/source-DB preservation pass. PreviewHTTP200 and46-event persisted console verified through the frontend proxy. Browser-rendered QA remains blocked. Following checkpoint is documentation only.

## Live investigation console — 2026-11-04

[x] Added durable per-job operation events and an Overview/Technical log console immediately below the controls, retained in Evidence with JSON export.
[x] Real starts/returns, engine/source/replicate identity, independent checks, subjective-score changes and supervisor-confirmed terminal status; no fake progress or startup-only live claim.
[x] Polling/stale-job isolation, active-job restoration, page scroll on submission, optional internal following, results/test navigation and archived per-job retrieval.
[x]60 backend tests,11 UI logic tests, production build/typecheck and final11 live HTTP gatesPASS (83.83s). Fresh MD start was observed before completion; cached/fresh labels and fallback receipts checked.
[x]12 source DB tables and4 original specimens/29 result rows unchanged; scientific source lockf551d9dPASS. No locked scientific code/prompt/protocol/threshold changes.
[ ] Browser visual/click QA remains blocked by browser transport timeoutMs errors; no rendered acceptance claimed.

See docs/INVESTIGATION_CONSOLE.md. Current previewlocalhost:3000/API:8000 is owned by runtime/investigation-console/preview and uses preview-original/study/rehearsal.db copies, provider calls disabled. Prepared DEMO_501 real cached-MD console:46 events/12 cached LAMMPS result loads,1.644s; this is not12 fresh MD executions or new live-model acceptance. Prior preview files and source databases retained.


## Study scope placement — 2026-11-04

User requested the full published-study status, explanation and Read the study link inside the collapsed Study scope and this sample disclosure, placed last. Moved the entire disclosure after optional help and before the footer. All study/sample metadata and actual status retained. Production build/typecheck and source nesting/order checksPASS; isolated preview rebuilt/restarted. Browser visual QA remains unverified as previously documented. No backend/scientific changes.


## Investigation guide navigation fix — 2026-11-04

Renamed the presentation-oriented guide to Investigation guide / Follow an investigation. Each shortcut now names and opens a specific section (material, explanations, next test, results, evidence or conclusion), switches views when necessary, scrolls to that section, moves focus and briefly outlines it. A new navigation request is made even when the selected view is already active, fixing the previous apparent no-op. Copy explicitly distinguishes navigation from running experiments.

Production build/typecheckPASS;6 existing UI logic checksPASS; source destination checksPASS for all5 target IDs and same-view scroll/focus handling. No new backend/physics/model behavior. Preview rebuilt/restarted using isolated databases. Browser-rendered click verification remains unverified due the previously documented tool failure.


## Investigation controls follow-up — 2026-11-04

Moved investigation mode controls directly after Workspace/Sample. Primary action is Run full investigation, changing to View results when complete with Investigate again retained. Renamed manual disclosure Explore step by step; reset is a quiet secondary action inside it with confirmation and preservation wording. Removed duplicated action controls from the lower page/status banner. Backend behavior unchanged.

Validation: production buildPASS, TypeScriptPASS,6 UI logic testsPASS; live previewHTTP200 and served-markup ordering/labelsPASS. Existing next-env bytes restored. Browser visual QA remains unverified due the previously documented browser-tool issue; no full backend/E2E rerun for this frontend-only placement/copy change.


Latest verified redesign source checkpoint: `b94578b` on `design/frontend-simplification`. Build/typecheck,6 UI logic,56 regression and11 live HTTP checks passed. Rendered browser QA remains blocked; preview uses isolated copies. The following continuity commit changes documentation only.

## Latest task: frontend redesign implemented on a separate branch

[x] Branch design/frontend-simplification preserves the prior frontend on science/predeclared-demonstration.
[x] Delivered cream/charcoal/blue/orange UI, Investigate/Results/Evidence, simpler copy, actual-state progress, next-test cards, stable atom scales, correct censoring/provenance and full evidence export.
[x]6 UI logic tests,56 backend tests,11 live HTTP tests, build/typecheck and task-specific12-table preservation pass.
[ ] Rendered browser QA blocked by browser-control timeoutMs error; human usability targets unmeasured. No visual pass claimed.

Previewlocalhost:3000 uses isolated database copies with new provider calls disabled. No source scientific records or scientific code changed. See FRONTEND_REDESIGN_IMPLEMENTATION.md for logs and exact preview commands.

## Latest task: frontend redesign planning

[x] Reviewed PlantDebugger source at d69507aa48aec773a5cf72761e5ff60c491eefc1 and sampled frames across the user's 239.708-second demo video; reviewed current frontend code at source checkpoint23f2525.
[x] Added docs/FRONTEND_REDESIGN_PLAN.md: cream/charcoal/blue/orange design, plain-language dictionary, NOW banner, focused investigation/results/evidence views, component roadmap, phased estimates and scientific-display acceptance checks.
[x] Planning-only change; no application/scientific code, simulations, provider calls or databases changed. Local preview port3000 was offline, so current UI findings are source-based; browser visual QA remains pending implementation.
[x] The subsequent user request authorized implementation; see the latest implementation checkpoint above.

Latest tested integration and walkthrough checkpoint: d6015e3; earlier live-provider milestone b4d68ea on science/predeclared-demonstration. Scientific evidence checkpoint:872833f. Original audit source checkpoint:1dd84cf on science/root-cause-audit. Original working build remains available at 00c4375; initial build checkpoints and archived evidence are retained. A documentation-only acceptance checkpoint follows the source commit.

[x] Frozen inputs and baseline summaries preserved byte-for-byte; all 29 pre-existing immutable result records unchanged.
[x] Actual force/NVE, raw/flow temperature, damping, rate, sampling, geometry, stochastic-ordering and expanded-seed controls measured.
[x] 159 captured run artifacts / 111 distinct serialized input-engine result IDs retained; repeated diagnostic captures are not counted as independent samples.
[x] Censoring selection bias and duplicate/unexpected seed acceptance fixed without changing any scientific threshold.
[x] Detailed validity-gate reasons and measured force/temperature diagnostics exposed in fresh result audits; reported stress convention unchanged.
[x] Backend regression: 32 passed (original tests plus seven new regression/invariant tests).
[x] All five acceptance gates rerun: evaluator PASS, production frontend build PASS, live E2E 9 passed in 29.79 s; post-restoration TypeScript PASS; npm audit 0 vulnerabilities.
[x] Demo restored at http://127.0.0.1:3000 and API :8000; original investigation state preserved.

Measured findings and limitations: SCIENTIFIC_FINDINGS.md. ALPHA's original failure is the driven-temperature gate, with no evidence of divergent integration. Slower separate controls improve valid runs from 1/3 to 3/3 and lower traction gaps, but do not replace frozen records. Nine BETA pairs show +0.457% recovery / SNR 0.0735. GAMMA negative recovery persists under cadence and timestep controls. All four original benchmark verdicts remain INCONCLUSIVE; all methods still record four NO_DECISION outcomes. Supplemental temperature subtraction never replaces the raw gate; a uniform stress field cannot be assumed during driven Langevin loading.

Remaining limitations: small finite lattice, three-seed control pilots, non-equivalent atomwise stochastic noise when atom count/order changes, rate-sensitive failure timing, and lack of validated profile-unbiased thermostat parity. No live-model demonstration is claimed; this audit used deterministic tools with model calls disabled.

User changes preserved: original TEST_RESULTS.md formatting and next-env.d.ts edits remain unstaged; repomix-output.xml remains untracked. No secret was printed or committed. Local demo ownership: runtime/demo PID/log files. Stop only the owned demo with `.venv/bin/python scripts/e2e_servers.py stop runtime/demo`.

## Separate prospective demonstration — evaluated (2026-11-04)

[x] V1 preregistered before trajectories; negative development retained; holdout unopened.
[x] V2 independently preregistered before trajectories; negative physical validation retained; holdout unopened.
[x] Final V3 athermal registration e17fc8b; scientific source f551d9d; prospective analysis/prediction lock a6e2a68 before held-out generation.
[x] Frozen blind held-out decisions, private scoring and seven actual finer-dt MD runs completed without changing locked scientific source.
[x] Complete study NOT_VALIDATED: DEMO_501 correctly distinguished interior repair (+47.85% vs −0.61%); DEMO_502 inconclusive (+10.79% boundary recovery below fixed18%); DEMO_503 correct no-cause negative control. No incorrect diagnoses. No further design search.
[x] All held-out applicable cohorts valid, uncensored, exact deterministic replays; timestep convergence passes. No independent thermal samples or population intervals claimed.
[x] Fresh published held-out baseline replay exactly matches physical record without private preparation access.
[x] Separate dashboard/API/jobs and checksummed public bundle restore preserve existing data. Six specimens / 56 immutable result entries. Original four cases and29 result rows exact; original reports unchanged from f4fbbca.
[x] Backend/public-data regression48 passed; frontend production build/typecheck PASS. Final live full-stack E2E10 passed82.82s, including real fresh MD, cancellation, crash recovery and evidence proxy. Final display-label clarification rebuilt and checked in browser.

Evidence: docs/demonstration/v3/STUDY_REPORT.md and raw public archives. Runtime14.41–15.99s exceeds3–12s target; horizon preserved. Partial case-level evidence must not be relabeled full-study validation. All active scientific files remain hash-locked. User TEST_RESULTS formatting, next-env edits and repomix file preserved. Live-model inference remains unverified; study runs registered deterministic tools.

[x] Original and study preview restored; browser inspection verified DEMO_501 stored conclusion/curves, DEMO_502 failed-repair badge, all6 study IDs, original4-case selector and explicit no-model mode. Archived run provenance is labeled stored MD, with timestamped fresh/cache detail. No required implementation task remains; full-study scientific failure remains disclosed.

## Live Muse integration — verified provider loop (2026-11-04)

[x] Snapshot original/study databases and frozen evidence before new work; retain prior user edits.
[x] Verified official Meta endpoint/model from primary documentation; saved missing URL/model settings in ignored .env without exposing the existing key.
[x] Identified truncated reasoning-only probe responses; request minimal reasoning, adequate bounded tokens, explicit completion/model identity checks and preserve provider usage on failure.
[x] Isolated /api/live-muse AI workspace; unchanged deterministic registered MD tools/verifier and study source lock.
[x] Real Muse Spark1.3 hypotheses + separate planning + two evidence-based revisions succeeded on DEMO_501 with6 fresh MD replay executions. 121.95s loop; all4 operation receipts LIVE. Full study remains NOT_VALIDATED.
[x]55 backend tests pass16.09s; production frontend build passes; original evaluator rerun to separate output (every method4 NO_DECISION). All original/study table rows and frozen files unchanged.
[x] Final11-test live HTTP gatePASS83.19s; final56-test regressionPASS13.28s, build/typecheck/evaluatorPASS. Genuine additional HTTP-worker hypotheses/planningPASS; browser inspected live receipts and frozen no-model mode.
[x] Polished six-step dashboard guide and four-minute presenter walkthrough complete; all model limitations and fullNOT_VALIDATED explicit.
[x] Initial model localization error and subsequent mixed/fallback rehearsal retained. Coordinate-derived grounding and completed-evidence citation enum added; final actual-provider rehearsal all4 callsLIVE with explicit immutable MD reuse. No scientific results/thresholds changed.
[x] Final all-table original/study and frozen-file/source-lock preservationPASS; preview restored, user edits preserved; no required implementation work remains.

## Beginner project documentation

[x] Added root detail.md: complete simple-language project guide, three workspaces, genuine physics/AI/verifier roles, workflow, results/limitations, file map, storage/API/jobs, setup, configuration, testing and presentation.
[x] Checked local Markdown links and code-block balance against the repository. Documentation-only checkpoint; previously recorded software/scientific results remain unchanged.
