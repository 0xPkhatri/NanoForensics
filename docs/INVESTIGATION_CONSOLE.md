# Live investigation console

Implemented on `design/frontend-simplification`, 2026-11-04. This adds operation telemetry and a readable console; it does not change scientific protocols, prompts, thresholds or verdict rules.

## Using it

Click **Run full investigation**, **Investigate again**, **Suggest possible causes**, or an individual **Run this test**. A console appears immediately below the investigation controls. It starts with “Submitting request”; it does not call the job running before the backend confirms it.

**Overview** shows confirmed stage states and timestamped observations. **Technical log** exposes structured execution records, simulation identities, engine/source information, numerical checks and action receipts. It is not raw shell access or streamed solver stdout.

**Follow new events** follows the internal event list. Scrolling away disables following so a user can read older events; the checkbox re-enables it. Initial submission scrolls the page to the console. Events are polled approximately every1.2 seconds. There is no simulated percentage, invented elapsed time, or timed demonstration sequence.

After a completed investigation, **Show results** opens the measured results. A hypothesis-only job instead offers **Choose a test**. **Review evidence** opens the retained console in Evidence. **Download log** exports the actual job/event JSON. Logs survive reload and are separate from mutable hypothesis state.

The main console shows the latest job for the selected sample. Earlier transcripts remain in durable storage and can be requested by job ID. Old jobs created before this feature have no detailed console transcript; the UI says so instead of reconstructing invented events.

## What is recorded

- Job acceptance, opaque sample ID, measured atom count and supervisor claim.
- Loaded public baseline measurements, immutable baseline ID and publicly disclosed protocol only.
- Start and completion of hypothesis generation and planning; actual hypotheses, priority scores and operation-specific source/receipts.
- Start of each baseline/test replicate, selected engine, seed/replay label, replicate index and total.
- Returned simulations with actual engine, cached/fresh flag, hashes, physical outcome, recorded compute duration and numerical checks.
- Actual verifier output, distinguishing execution failure, censoring, missing recovery and scientific verdict.
- Start and finish of explanation revision, with recorded before/after subjective scores and independent statuses.
- Scientific conclusion and separately confirmed terminal worker status, including cancellation, timeout, crash recovery and failure.

A requested engine is not presented as the confirmed executed engine. A requested fresh run is not marked completed before the result returns. Stored run compute time is labeled recorded compute time, distinct from current job elapsed time. Completed replicas do not complete the simulation stage until the comparison boundary is confirmed. Failed simulation checks remain failures, even if the investigation process itself finishes.

A model action earns a live label only from a completed event with a live action receipt. Startup connectivity, old model state and pending requests do not earn that label. Fallback is visible. The console does not expose private preparation records, raw prompts, model chain of thought, API keys, environment files or arbitrary worker stderr. It records published/observed information and bounded receipt summaries.

## Architecture

- `backend/api/progress.py`: explicit public console contracts, durable `job_events` table and consistent-snapshot reads. The table is created on event writes, not on read-only requests.
- `backend/api/progress_observer.py`: subclass adapters observe registered method boundaries. Returned numerical results/verdicts are not altered; progress is not appended to the scientific audit or model observations.
- `backend/api/progress_worker.py`: fixed allowlist of the three existing worker modules. It installs the observational adapter only inside the owned job process.
- `backend/api/jobs.py`: launches the adapter entrypoint, confirms job completion only after process exit and records terminal failure/cancellation. Queued cancellation now also clears mutable running state and records a terminal event without launching a worker.
- `backend/api/routes.py`: records accepted jobs and adds the activity endpoint. Existing route cloning makes the same API available in all three isolated namespaces.
- `frontend/src/hooks/useInvestigation.ts`: retrieves initial history, polls job/state/activity, restores active jobs and guards stale responses and earlier job histories during new submission.
- `frontend/src/lib/console-view.ts`: derives stage state and provenance from confirmed records only.
- `frontend/src/components/InvestigationConsole.tsx`: overview, technical view, following, timestamps, details, results/evidence navigation and JSON export.

The original/demonstration/live namespaces and job locks are retained. Console events are stored per job, so hypothesis regeneration cannot erase a job transcript. The registered locked investigator, demonstration worker, solver, potential, verifier and Pydantic scientific contracts remain byte-identical to the scientific lock.

## API

```text
GET /api/cases/{case_id}/activity
GET /api/cases/{case_id}/activity?job_id={job_id}
GET /api/demonstrations/cases/{case_id}/activity
GET /api/live-muse/cases/{case_id}/activity
```

Responses contain a typed public job summary and ordered events. The default is the latest investigation/experiment/hypothesis job for that case. A job ID is accepted only within its sample and database namespace; a mismatched ID returns404. No job returns `job=null, events=[]`. Read-only activity requests never create fictitious events.

## Verification

| Check | Actual result |
| --- | --- |
| New backend event tests | 4 passed in7.61s; durable history, genuine cached MD, unchanged scientific verdicts, no premature completion, cancellation before launch and terminal timeout |
| Complete backend regression | 60 passed in21.22s; one pre-existing dependency deprecation warning |
| Frontend logic | 11 passed; includes stale-job isolation, incomplete replicate handling, stopped/failed states, real source labels and live-receipt requirements |
| Production build / TypeScript | PASS; user's next-env bytes restored |
| Initial live HTTP gate | 11 passed in84.27s |
| Final live HTTP gate | 11 passed in83.83s; observed an in-flight start event during real fresh MD,3 fresh test runs, true cached events, actual verification/revision and supervisor completion |
| Original scientific records | 4 original specimens and29 result rows unchanged |
| Source databases | All12 source specimens/results/states/jobs tables match task-start snapshots |
| Scientific source lock | PASS, source `f551d9d998bf59c4097acc2dd54c7a59602c8e04` |
| Rendered browser/click QA | NOT_RUN: the browser-control transport still errors on navigation before a page can be inspected |

Frontend contract fixtures do not represent scientific runs or model acceptance. The backend cached-MD tests use the actual published public bundle; the live HTTP gate executes actual fresh MD. The final UI receipt-label hardening and download/navigation refinements were built and typechecked; backend event checks were rerun after the consistent-read and per-job retrieval changes. The final supervisor message wording is a presentation-only change.

## Real preview rehearsal

An actual HTTP investigation in the isolated preview produced:

- Job `76efd7f6087f4a24ba2759c31d476eed`, execution COMPLETE, elapsed1.644s including queue time.
- 46 durable operation events.
- 12 genuine cached LAMMPS result loads, not12 freshly computed runs.
- All model actions `OFFLINE_HEURISTIC_FALLBACK`; provider calls intentionally disabled.
- Actual verifier/revision/conclusion events and a separate supervisor completion event.
- Successful retrieval by immutable job ID, with a mismatched sample/job request rejected.

This is a post-study console/integration rehearsal, not a new blinded study or live-provider demonstration. The full published scientific study remains NOT_VALIDATED. Fast cached replay is not a claim about fresh simulation speed.

Local artifacts: `runtime/investigation-console/{regression.txt,progress-tests-final.txt,ui-tests.txt,e2e-final.txt,build-final.txt,acceptance-summary.json,acceptance-transcript.json,preservation.json}`. These ignored runtime artifacts are not required to infer the display rules; tests and implementation are committed. Full-stack gate stdout is also recorded in `docs/E2E_LAST_RUN.txt`.

## Preview ownership and remaining review

Preview is at `http://127.0.0.1:3000`, API8000. Owned process records/logs: `runtime/investigation-console/preview/`. It uses new copies of original, study and rehearsal databases. Earlier preview databases and all source databases are retained. The prepared DEMO_501 console is in **AI investigation → DEMO_501**, available in Evidence or in the main view after load.

```sh
.venv/bin/python scripts/e2e_servers.py stop runtime/investigation-console/preview

NANO_DB="$PWD/runtime/investigation-console/preview-original.db" \
NANO_DEMONSTRATION_DB="$PWD/runtime/investigation-console/preview-study.db" \
NANO_LIVE_MUSE_DB="$PWD/runtime/investigation-console/preview-rehearsal.db" \
META_MUSE_API_KEY='' \
.venv/bin/python scripts/e2e_servers.py start runtime/investigation-console/preview
```

Restore user next-env bytes after builds from `runtime/investigation-console/next-env.original`. Preserve existing TEST_RESULTS formatting and the untracked repomix file. Do not restart an older owned preview concurrently on3000/8000.

Still required when browser transport works: rendered desktop/mobile inspection, visible auto-follow behavior, keyboard/tab/focus checks, real button navigation and browser download verification. No screenshot or complete visual acceptance is claimed. Per-timestep MD, raw LAMMPS stdout, continuous trajectories, provider token streaming and SSE are not implemented; the UI uses truthful operation/replicate events through existing polling.


## Active-stage and received-text animation — 2026-11-04

Added a spinner/blue highlight only for backend-confirmed active stages; completed, failed, stopped and waiting stages keep their actual states. New human-readable event text reveals progressively with a cursor and Show now control. Source badges, timestamps, raw technical JSON, result navigation and actual stage completion are never delayed by typing. The effect is presentation after receipt, not provider token streaming.

Saved history is immediate; a shared page-local reveal session prevents replay across views. New receipts on a restored running job can animate. Reduced-motion preferences disable typing/motion; screen readers have the full received text. ResizeObserver follows growing text only when following is enabled. Switching to Technical log skips the active reveal.

Validation:14 frontend testsPASS (including history/session/Unicode/markup reveal tests), production buildPASS, restored-next-env TypeScriptPASS, previewHTTP200. A React key warning found by static-render testing was fixed and the final tests have no key warnings. Existing Node module-type warning remains non-fatal. No backend/scientific change or new physics/provider call; backend/E2E gates not rerun for this display-only extension. Rendered animation/reduced-motion/browser interaction verification remains pending due the prior browser-tool failure. Logs:runtime/console-animation.


## Current comparison progress and console placement — 2026-11-04

Fixed the screenshot-reported confusion: simulate/verify/revise indicators are now scoped to the latest actual comparison boundary, including repeated proposal IDs and skipped edits. A second test cannot inherit green verification/revision checkmarks from the first. Prior results remain in the immutable event log. The console labels Current test/Last test, explains the current-cycle scope, distinguishes unchanged reference samples from changed samples, and offers Jump to latest when following is paused.

Moved the entire investigation console below The scientific loop, after the NOW status banner. The NOW message now prefers the latest confirmed running console event over an older completed-replicate audit message. Added explicit readable cancel-button text/background colors to fix the white-on-white appearance.

Validation:16 frontend testsPASS (two new cycle-reset regressions), production buildPASS, user-restored-next-env TypeScriptPASS, source ordering/previewHTTP200PASS. No backend/physics/provider changes or extra simulation runs; backend/E2E not rerun for this frontend status/layout fix. Browser visual QA remains unverified as previously documented. Logs:runtime/console-cycle-fix.
