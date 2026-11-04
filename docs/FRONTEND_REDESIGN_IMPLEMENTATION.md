# Frontend redesign implementation — 2026-11-04

Branch: `design/frontend-simplification`, created from `adf1a2e` on `science/predeclared-demonstration`. The previous frontend remains on the original branch. No merge or deployment was performed.

## Delivered

- Warm cream surfaces, charcoal status banner, blue actions, orange test highlights, responsive worksheet layout and simpler navigation.
- Separate Investigate, Results and Evidence views; explicit original/test selection retained across views.
- Current-step banner, actual-state six-stage rail, workspace/sample selectors, manual controls, new-investigation action for stored conclusions and guided example.
- Plain-language explanation questions and test names. Original model wording, measured evidence, predictions and subjective scores remain available in details.
- Recommended remaining test selected using actual proposal utility; all alternatives and their ranking/controlled-parameter records remain inspectable.
- Evidence → explanation → next-step card based on public observations, recorded results and recorded revisions only.
- Light atom viewer with fixed neighbor-loss/count scales, shared original/test bounds and local-virial range, discrete recorded snapshots, explicit run identity, zoom and keyboard-accessible atom measurements.
- Light stretching chart with engineering strain displayed as a percentage, accurate reduced stress units, named original/test curves, actual fracture markers, spread labeling and accessible original-data table.
- Independent result cards separate execution failure from scientific support. Null recovery remains unavailable; censored runs retain observation horizons; outcome counts and replicate validity remain inspectable.
- Readable filtered evidence timeline, per-action AI receipts, immutable run records, full report/export, glossary and help.
- Request/polling hook preserves workspace selection and job recovery, prevents overlapping polling and stale sample responses, and awaits actual terminal job/cancellation acknowledgement.
- Study-wide status and post-study rehearsal scope remain visible. A startup probe or old live response cannot become a new live action claim.

No physics, verifier threshold, frozen preparation, scientific source lock, model prompt, database schema or API route was changed. There were no new provider calls. E2E tests exercised actual MD using isolated databases.

## Validation

| Check | Result |
| --- | --- |
| TypeScript | PASS, including restoration of user-owned next-env bytes |
| Production Next.js build | PASS |
| New UI logic checks | 6 passed; null/censoring, execution/verdict separation, snapshot labels, action provenance, stage derivation and stale-response rejection |
| Backend regression | 56 passed in 16.89 s; existing dependency deprecation warning |
| Full live HTTP gate | 11 passed in 84.53 s; real jobs, fresh MD, cancellation, deadlines, restart/crash recovery and workspace isolation |
| Isolated benchmark evaluator | PASS; all three methods retain 0 correct / 0 incorrect / 4 NO_DECISION; frozen reports untouched |
| Original scientific-record preservation | 4 original specimens and 29 original result rows unchanged |
| Task-specific database preservation | All 12 tables across original, published-study and rehearsal databases unchanged |
| Semantic text-color combinations | Eight checked combinations all exceed 4.5:1; 4.68:1 minimum among those combinations |
| Rendered desktop/mobile browser checks | NOT_RUN: browser control failed before navigation, DOM inspection and screenshot capture |
| Three-person comprehension study | NOT_RUN; these remain targets, not measured usability claims |

The initial E2E run passed 10/11; one assertion expected the old “Live Muse Spark rehearsal” text. It now checks the actual new AI investigation and Published study selector options. All scientific and job assertions were retained; the rerun passed11/11. An intermediate duplicate copy-label declaration was caught by typechecking and corrected before the final build.

The older `scripts.verify_rehearsal_preservation` comparison already failed before testing with `original states changed`: its historical snapshot predates existing investigation-state edits. This work did not reset those states. New task-specific snapshots were taken before starting isolated preview/jobs, and all12 current source tables match them. The frozen study/source checks pass independently.

Logs and task snapshots are local, ignored artifacts under `runtime/frontend-redesign/`. The current HTTP gate summary is also in `docs/E2E_LAST_RUN.txt`. The evaluator report is written to a separate runtime path, never over the frozen benchmark report.

## Local review

Preview: `http://127.0.0.1:3000`. Owned processes: `runtime/frontend-redesign/preview/{api,ui}.pid` and logs. The preview uses copies of all three databases with new provider calls disabled; existing action receipts remain labeled recorded history. Production configuration and `.env` were not changed.

Stop only these preview processes:

```sh
.venv/bin/python scripts/e2e_servers.py stop runtime/frontend-redesign/preview
```

Restart the same isolated preview:

```sh
NANO_DB="$PWD/runtime/frontend-redesign/preview-original.db" \
NANO_DEMONSTRATION_DB="$PWD/runtime/frontend-redesign/preview-study.db" \
NANO_LIVE_MUSE_DB="$PWD/runtime/frontend-redesign/preview-rehearsal.db" \
META_MUSE_API_KEY='' \
.venv/bin/python scripts/e2e_servers.py start runtime/frontend-redesign/preview
```

Use `npm --prefix frontend run test:ui` for the new logic checks (tested on Node26), `npm --prefix frontend run typecheck`, and `npm --prefix frontend run build`. After builds, retain the user's original `frontend/next-env.d.ts` bytes saved at `runtime/frontend-redesign/next-env.original`.

## Remaining review

The code implementation and automated engineering gates are complete. Visual acceptance is still pending because browser automation failed with an internal `timeoutMs` error even after documented troubleshooting and reconnection. No screenshot or responsive rendering pass is claimed. Review at1440×900,1280×720,1024×768,768×1024 and390×844; exercise all three views, workspace switching, selected comparisons, keyboard navigation and modal focus. A successful render is required before calling visual QA complete.

The full study remains NOT_VALIDATED. This UI work does not change that result.

## Reversibility

The original branch is `science/predeclared-demonstration`. Preserve the user's existing uncommitted TEST_RESULTS formatting, next-env edits and repomix file before any branch switch. Do not reset or clean the worktree. Switching frontend versions also requires rebuilding and restarting the preview. The isolated preview databases can remain for review; source scientific databases were not used for interactive test actions.
