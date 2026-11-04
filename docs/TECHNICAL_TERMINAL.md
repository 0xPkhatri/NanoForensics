# Technical terminal redesign — 2026-11-05

The Technical log tab now contains one dark, read-only execution terminal beneath the existing scientific loop. Overview retains its readable event cards. A compact nine-stage workflow above the terminal reuses confirmed backend phase states, including repeated comparisons.

## Interaction and structure

- `ExecutionTerminal.tsx` owns search, match navigation/filtering, expansion state, exports, clipboard feedback and expanded view. `TerminalEventRow.tsx` renders continuous event lines and deliberately expanded, syntax-highlighted original JSON.
- `terminal-format.ts` separates safe formatting from presentation. Events retain incoming order, sequence, timestamp and payload. Adjacent experiment contexts receive visual indentation; no event is merged or discarded. Unidentified events remain accessible.
- Search includes complete structured data. Enter/Shift+Enter and arrow buttons navigate matching events; matches found only in JSON expand that event. Filtering never changes exported history.
- Copy logs includes timestamps, sequence and status tags. Individual Copy JSON retains the full event. Download JSON exports the complete original activity and event history even while filtered; .log provides a readable complete transcript. Export is lossless relative to the API payload already parsed by JavaScript, not a reconstruction of pre-serialization numeric values.
- `useLogFollow.ts` and `log-follow.ts` coalesce follow updates with animation frames. Upward wheel/touch/keyboard/scrollbar interaction pauses following; intentional return to the bottom may resume it. Jump to latest clears filtering and resumes follow. Expanded rows and search survive polling and tab switches.
- Expanded view is an in-page overlay with focus containment, Escape, focus restoration and body scroll locking. It does not use the operating-system fullscreen API. Responsive styles wrap controls and isolate horizontal JSON scrolling.

## Scientific semantics and preserved behavior

Fallback is amber and explicitly identified; live responses require recorded action provenance. Saved immutable simulations receive CACHE. A completed calculation receives execution success, independently of numerical checks and verifier evidence verdicts. Supported evidence is not labeled full-study validation. Scientific limitations remain visible.

The running pane uses confirmed simulation-start events, replicate labels and server-derived elapsed time. Selected engine remains qualified until returned results confirm the actual engine. There is no fabricated timestep progress, percent, ETA or synthetic investigation event.

Backend execution, schemas, solver, protocols, verification criteria and event polling are unchanged. Full/step-by-step investigations, individual experiments, cancellation, reset, sample switching, saved simulation reuse, history, results and evidence remain on existing paths. No dependency or shell capability was added.

## Verification

- `npm --prefix frontend run test:ui`: 33 passed, including ordering/grouping, filtering, raw JSON preservation, immutable exports, expansion state, follow decisions, clipboard success/failure and actual server-rendered terminal states (running/completed/failed/cancelled). Expanded-payload coverage includes long strings and escaped HTML.
- `npm --prefix frontend run typecheck`: PASS.
- `npm --prefix frontend run build`: PASS. User-owned next-env bytes restored afterward. There is no configured lint script.
- `bash scripts/verify_e2e.sh` with isolated source snapshots: 11 passed in 84.68 seconds, including fresh real MD, cancellation/deadline, persistence, crash recovery and workspace isolation. Provider disabled for this regression; this is not new live-model acceptance.
- All 12 source database tables match the before-task fingerprints. Original four specimens/29 results and scientific source lock verified unchanged.
- Local preview and all three API specimen lists returned HTTP 200 after restoration. Preview uses separate original/study/rehearsal DBs, preserving existing preview history; provider key disabled.
- Seven terminal foreground/background palette pairs measured contrast >= 4.5:1. A 46-event actual saved transcript formatted in approximately 0.129 ms mean over 100 runs on this host. This measures formatting only; virtualization was not justified by the observed history size.

Browser automation failed before navigation with a timeoutMs adapter error. Real-browser visual layout, mobile behavior, actual clipboard/download interactions and expanded-view keyboard behavior remain unverified; static rendering and focused logic tests are not substitutes for those checks. Existing benign Node module-type warnings remain. Evidence is in ignored `runtime/terminal-redesign/` and committed `docs/E2E_LAST_RUN.txt`.

## Local review

Open http://127.0.0.1:3000, select the sample and choose Technical log below the scientific loop. Preview processes are owned by `runtime/investigation-console/preview`:

```sh
.venv/bin/python scripts/e2e_servers.py stop runtime/investigation-console/preview
NANO_DB="$PWD/runtime/investigation-console/preview-original.db" NANO_DEMONSTRATION_DB="$PWD/runtime/investigation-console/preview-study.db" NANO_LIVE_MUSE_DB="$PWD/runtime/investigation-console/preview-rehearsal.db" META_MUSE_API_KEY='' .venv/bin/python scripts/e2e_servers.py start runtime/investigation-console/preview
```

Preserve user-owned TEST_RESULTS formatting, next-env changes and untracked repomix-output.xml. Restore next-env from runtime/terminal-redesign/next-env.original after further builds. Do not modify frozen scientific files to address UI behavior.


## Word-by-word terminal output — 2026-11-05

Newly confirmed terminal events now reveal sequentially by word across messages and metrics, using a single ordered display queue. Saved completed history is immediate. Poll batches catch up with a bounded word batch; reduced-motion, search, opened details and hidden tabs show complete text immediately. Raw JSON, search corpus and exports always retain full confirmed events. A cursor and explicit display-only disclosure distinguish this from provider token streaming. Existing ResizeObserver/animation-frame auto-follow tracks text growth; intentional upward scrolling still pauses following. No event, backend behavior or scientific metric changed.

35 frontend testsPASS (two new sequential reveal/raw preservation tests), typecheckPASS and production buildPASS. Browser visual/interaction verification remains unavailable from the previously reported adapter failure. Owned UI alone restarted; API/ongoing investigations untouched. Refresh localhost:3000 and start an investigation to see new events reveal; historical results do not replay a fake investigation. Evidence:runtime/terminal-redesign/reveal-{tests,types,build}.txt.


## Technical stage sidebar — 2026-11-05

Technical log now places the same Initialize→Finish job stage list to the left of the terminal. Both views reuse one rendering definition and confirmed phase-state logic, including active spinner/completed/waiting/failed statuses and current-test labels. Removed redundant horizontal technical workflow. Small screens use the existing three-column stage layout above the terminal; expanded console remains independent of sidebar width. Streaming text, follow, exports and backend unchanged. Frontend36 tests/typecheck/buildPASS; added rendered sidebar placement test. Visual browser verification remains unperformed due the known browser adapter failure. UI-only preview restart preserves API and investigations. Evidence:runtime/terminal-redesign/sidebar-{tests,types,build}.txt.
