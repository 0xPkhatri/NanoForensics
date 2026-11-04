# Project state — demonstration evaluation complete (2026-11-04)

## Current comparison progress and console placement — 2026-11-04

Fixed the screenshot-reported confusion: simulate/verify/revise indicators are now scoped to the latest actual comparison boundary, including repeated proposal IDs and skipped edits. A second test cannot inherit green verification/revision checkmarks from the first. Prior results remain in the immutable event log. The console labels Current test/Last test, explains the current-cycle scope, distinguishes unchanged reference samples from changed samples, and offers Jump to latest when following is paused.

Moved the entire investigation console below The scientific loop, after the NOW status banner. The NOW message now prefers the latest confirmed running console event over an older completed-replicate audit message. Added explicit readable cancel-button text/background colors to fix the white-on-white appearance.

Validation:16 frontend testsPASS (two new cycle-reset regressions), production buildPASS, user-restored-next-env TypeScriptPASS, source ordering/previewHTTP200PASS. No backend/physics/provider changes or extra simulation runs; backend/E2E not rerun for this frontend status/layout fix. Browser visual QA remains unverified as previously documented. Logs:runtime/console-cycle-fix.


## Active-stage and received-text animation — 2026-11-04

Added a spinner/blue highlight only for backend-confirmed active stages; completed, failed, stopped and waiting stages keep their actual states. New human-readable event text reveals progressively with a cursor and Show now control. Source badges, timestamps, raw technical JSON, result navigation and actual stage completion are never delayed by typing. The effect is presentation after receipt, not provider token streaming.

Saved history is immediate; a shared page-local reveal session prevents replay across views. New receipts on a restored running job can animate. Reduced-motion preferences disable typing/motion; screen readers have the full received text. ResizeObserver follows growing text only when following is enabled. Switching to Technical log skips the active reveal.

Validation:14 frontend testsPASS (including history/session/Unicode/markup reveal tests), production buildPASS, restored-next-env TypeScriptPASS, previewHTTP200. A React key warning found by static-render testing was fixed and the final tests have no key warnings. Existing Node module-type warning remains non-fatal. No backend/scientific change or new physics/provider call; backend/E2E gates not rerun for this display-only extension. Rendered animation/reduced-motion/browser interaction verification remains pending due the prior browser-tool failure. Logs:runtime/console-animation.


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


## Technical terminal redesign completed — 2026-11-05

[x] Inspected event schema, polling, progress and auto-follow; retained existing backend behavior.
[x] Replaced Technical log cards with a single terminal, compact workflow, full on-demand JSON, search/navigation/filtering, clipboard/export and expanded view.
[x] Preserved input order and full history; differentiated fallback/live AI, saved/fresh computation, numerical checks and scientific verdicts.
[x] 33 UI tests, typecheck, production build and isolated full-stack11 tests (84.68s) passed. All12 source DB tables unchanged; scientific source lock/original preservation PASS.
[x] Preview restored on3000/8000 using isolated copies; all three sample APIs200. No dependency/backend changes.

Browser automation failed before navigation; visual/mobile and real-browser interaction QA remain unverified. See docs/TECHNICAL_TERMINAL.md. Latest verified prior checkpoint e20d85e; this milestone is checkpointed in the following Git commit. User next-env/TEST_RESULTS edits and repomix file preserved.

Verified terminal implementation checkpoint: `8b3309b` on `design/frontend-simplification`. Subsequent continuity commit only records this tested source checkpoint.


## Terminal visibility follow-up — 2026-11-05

Screenshot showed Overview selected, whose original cards were deliberately retained. Technical log now opens by default on mount and new investigation requests. Overview remains available. Frontend33 tests/typecheck/buildPASS; owned UI restarted without stopping API or active investigations. Refresh localhost:3000 to load the new default. No backend/scientific changes.


## Word-by-word terminal output — 2026-11-05

Newly confirmed terminal events now reveal sequentially by word across messages and metrics, using a single ordered display queue. Saved completed history is immediate. Poll batches catch up with a bounded word batch; reduced-motion, search, opened details and hidden tabs show complete text immediately. Raw JSON, search corpus and exports always retain full confirmed events. A cursor and explicit display-only disclosure distinguish this from provider token streaming. Existing ResizeObserver/animation-frame auto-follow tracks text growth; intentional upward scrolling still pauses following. No event, backend behavior or scientific metric changed.

35 frontend testsPASS (two new sequential reveal/raw preservation tests), typecheckPASS and production buildPASS. Browser visual/interaction verification remains unavailable from the previously reported adapter failure. Owned UI alone restarted; API/ongoing investigations untouched. Refresh localhost:3000 and start an investigation to see new events reveal; historical results do not replay a fake investigation. Evidence:runtime/terminal-redesign/reveal-{tests,types,build}.txt.


## Technical stage sidebar — 2026-11-05

Technical log now places the same Initialize→Finish job stage list to the left of the terminal. Both views reuse one rendering definition and confirmed phase-state logic, including active spinner/completed/waiting/failed statuses and current-test labels. Removed redundant horizontal technical workflow. Small screens use the existing three-column stage layout above the terminal; expanded console remains independent of sidebar width. Streaming text, follow, exports and backend unchanged. Frontend36 tests/typecheck/buildPASS; added rendered sidebar placement test. Visual browser verification remains unperformed due the known browser adapter failure. UI-only preview restart preserves API and investigations. Evidence:runtime/terminal-redesign/sidebar-{tests,types,build}.txt.


## Architecture images — 2026-11-05

Created two matching landscape PNG diagrams under docs/architecture: scientific workflow and implemented technical architecture. Built-in image_gen used; prompts retained in prompts.json. Reviewed against backend/main.py, useInvestigation.ts and detail.md, then inspected both generated images. Revised workflow ordering/arrows and lattice schematic. Both PNG chunk CRCs and compressed image payloads verified with Python stdlib; prompt JSON parses. Pillow unavailable in the project venv; validation used stdlib instead. Stress plot is explicitly schematic and NOT_VALIDATED scope retained. Architecture uses actual local Next.js/FastAPI/jobs/SQLite and live-model-versus-fallback distinctions, without assumed cloud deployment. No application code, protocols, DBs or scientific data changed; no software tests repeated for image-only artifacts. Assets checkpoint6f22ca3; prior tested UI checkpointa0df38e preserved. Deliverables:docs/architecture/README.md. No pending work for this image request.


## README presentation refresh — 2026-11-05

Rewrote root README in the presentation-first structure requested using PlantDebugger's public README as a reference (retrieved raw README after GitHub page fetch failed). Original NanoForensics copy: clear problem/loop, honest badges, both generated architecture images, current three-workspace/UI walkthrough, portable install/start steps, environment table, AI/physics/verifier responsibilities, measured findings/NOT_VALIDATED, testing/replay/live acceptance, project map and documentation links. No hosted deployment, video, award or license invented. Removed stale denial of earlier live Muse acceptance; retained per-action fallback, mixed-failure evidence and post-study scope. Verified36 local links/anchors and balanced fences; reviewed labels/defaults/commands against repository files. Documentation only; application/scientific checks not rerun and source/data unchanged. Existing user TEST_RESULTS formatting, next-env and repomix edits preserved. No pending work for this README request.


## Complete detail.md refresh — 2026-11-05

Updated root beginner guide against current source, latest README and dated acceptance reports. Replaced old workspace/button names; documented Investigate/Results/Evidence order, controls near selectors, console below scientific loop, study-scope disclosure at bottom, default Technical log and shared left stage list, current-comparison progress, ordered word reveal versus real streaming, follow/search/JSON/copy/full exports/expanded view, working guide navigation, both architecture diagrams, event schema/job_events/activity API, current frontend/hooks/test file map, portable setup/Node recommendation, isolated preview ownership and fresh/saved presentation walkthrough. Corrected historical acceptance table to backend60/frontend36/E2E11 with dates/milestone context and retained browser adapter limitation. Preserved scientific methods, original negative findings, fullNOT_VALIDATED and historical live receipts. Validation:16 Markdown links/anchors,139 literal repository paths, balanced fences/current controlsPASS; git diff checkPASS. Documentation only; no software tests/provider calls/physics rerun, no backend/source/data edits. User TEST_RESULTS formatting, next-env edit and repomix file preserved. No pending work for this guide update.
