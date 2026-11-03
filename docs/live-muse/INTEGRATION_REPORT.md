# Live Muse Spark integration — verified post-study rehearsal

**Genuine live hypothesis generation, structured experiment planning and evidence-based belief revision were verified against Meta's API. The full scientific study remains NOT_VALIDATED.** These are post-study integration rehearsals on the already published DEMO_501 specimen, not new blinded discovery or new held-out scoring.

## Preservation and isolation

Scientific evidence checkpoint `71779ef`, the original four benchmark specimens/results, all preregistered study files, and scientific thresholds are unchanged. The development lock still verifies source `f551d9d`. All four tables—specimens, immutable results, investigation states and jobs—of both original and scientific-study databases match before-task snapshots exactly. See `preservation.json`. No existing investigation state was reset for this work.

The new `/api/live-muse` routes and `runtime/live-muse/rehearsal.db` isolate model hypotheses, plans, belief updates and job state. Initialization restores observable specimens and copies of genuine immutable MD into an empty AI workspace, then omits published investigation decisions from that workspace's initial state. Existing workspace data are preserved. No preparation/scoring files are live tools. The model receives public coordinates, coordinate-inferred missing components, the identical physical protocol, baseline measurements, and only experiment evidence actually completed in that rehearsal. It does not receive archived counterfactual conclusions or private family assignments in advance.

`LiveMuseInvestigator` subclasses the unchanged registered tool controller. It does not implement new physics, alter fracture detection or change support thresholds. The two physical repair choices and protocols are fixed. The model authors competing hypotheses/predictions and separate information-gain/risk/rationale outputs; the backend computes utility with a fixed formula and calibrated cost estimate. Model belief scores cannot replace deterministic verifier statuses or the frozen study status.

## Actual provider configuration and initial failure

The key was already saved in ignored `.env`, but endpoint/model values were missing. Meta's official [overview](https://dev.meta.ai/docs/overview) and [model catalog](https://dev.meta.ai/docs/models) supplied `https://api.meta.ai/v1` and `muse-spark-1.3`. Those nonsecret settings were added locally. No credentials were printed or committed.

The first 32-token health probe received no final JSON; a diagnostic 128-token request returned HTTP200 with `finish_reason=length`, null content and126 reasoning tokens. The previous parser reported a TypeError and discarded available usage. Using documented [minimal reasoning and completion-token settings](https://dev.meta.ai/docs/protocols/chat-completions), the corrected probe succeeded. The parser now records available usage/response IDs before content validation, rejects incomplete responses and mismatched returned model identities, and reports sanitized failures. Action outputs use the provider's [JSON-schema format](https://dev.meta.ai/docs/structured-output) plus independent local Pydantic/action/evidence validation. Deadlines and output sizes remain bounded.

A successful probe establishes connection/structured-response support only. Every scientific AI action needs its own schema-valid actual response; otherwise its mode is OFFLINE_HEURISTIC_FALLBACK. Provider token fields are shown only when supplied. Request messages, response hashes, parsed outputs, model/host, latency and provider response IDs are preserved, without authentication headers. Subsequent validation retries have distinct request hashes and retained parsed responses; retry messages never authorize new tools.

## Measured live rehearsals (all retained)

| Rehearsal | Hypotheses | Planning | Revision1 | Revision2 | MD provenance | Integration result |
|---|---:|---:|---:|---:|---|---|
| Initial verified loop | 8.917s | 5.100s | 7.459s | 6.716s | Six freshly executed counterfactual replays; immutable baseline reused | VERIFIED_LIVE |
| First position-grounded loop | 7.094s | 4.439s | Fallback after local validation | 6.536s | Explicit immutable MD cache reuse | NOT_VERIFIED / mixed |
| Final position-grounded loop | 10.390s | 5.270s | 7.702s | 4.622s | Explicit immutable MD cache reuse | VERIFIED_LIVE |

The initial complete fresh-MD loop took121.954s including model/tool/MD work. Later `budget_used_sec` fields are cumulative across workspace invocations and must not be described as individual-loop wall time. No simulation horizon was shortened.

Initial provider usage (input/output tokens): hypotheses32241/604, planning32203/317, revisions32728/585 and33198/629. Final position-grounded usage:32375/738,32348/383,32882/701 and33366/363. These are actual furnished counts, not estimates. Repeated baseline curves make the current prompt sizable (~32–33k tokens per call); future context compaction is an optimization, not part of the validation claim.

The first model chose the boundary repair first. It revised that mechanism downward after measured−0.6135% recovery (independent REJECTED verdict), then raised its interior score0.35→0.92 after measured+47.8528% recovery (independent SUPPORTED verdict). The final grounded model chose the interior repair first and changed its score0.55→0.72→0.75, while its boundary score changed0.35→0.30→0.20. Model order, wording and scores are variable; no particular score or experiment order is an acceptance requirement.

The observed physics remains the published model/protocol response: baseline failure strain0.0815, interior-repair0.1205 and boundary-repair0.0810. The independent registered contrast identifies the larger tested repair effect at this geometry. Actual scientific conclusions, not model confidence, determine the case verdict. All three scientific study cases remain visible; DEMO_502 is still inconclusive and the complete study is still NOT_VALIDATED.

## Model errors and bounded responses

The initial model described the boundary defect as lying on the reported right-side crack region, although the measured missing site was on the left. It was a model localization error. Its speculative causal narrative is not an independently verified explanation. Deterministic reconstruction still edited the actual inferred geometry; it never executed model-authored coordinates or commands. The original transcript, error and measured results are retained unchanged.

We added explicit coordinate-derived component centroids/relative positions and reminded the model that defect location need not equal crack-initiation region. The grounded hypotheses correctly distinguished the left-edge missing site from the reported right-side crack. These measurements come from visible coordinates; no hidden preparation labels or published desired verdicts were added to the model input.

One subsequent revision failed local schema/evidence validation twice and fell back visibly. That run is NOT_VERIFIED, retained in `grounded-failed-summary.json` and `grounded-failed-trace.json.gz`. Its earlier receipt format retained response hashes rather than rejected parsed bodies, so the exact validation subtype cannot be reconstructed and is not claimed here. The improved receipt format now retains each parsed attempt. Revision citation IDs are also constrained in the request schema to actual completed experiment IDs, with a local validation check retained. The final independently requested rehearsal passed all four action calls. The mixed run is not omitted from the integration history.

Syntactic and evidence-reference validation cannot prove a model narrative is scientifically correct. Incorrect location inference in the first run illustrates that limitation. A model response can be live and still wrong. Scores are subjective, not calibrated posterior probabilities; exact athermal replays are not independent thermal observations.

## Dashboard and presentation

The three dataset choices distinguish original frozen benchmark, frozen scientific study and separate live AI rehearsal. The study's NOT_VALIDATED banner and frozen case-level status remain prominent. The live header describes the last successful action, while the action panel explicitly identifies stored historical receipts and each operation's live/fallback mode, model, host, latency, provider usage, response hash/ID and before/after score changes. A startup probe alone cannot earn an investigation-live claim. Hypothesis and proposal provenance remain per action; mixed operations can be inspected individually.

The guided DEMO_501 panel gives six presentation steps. The [walkthrough](DEMO_501_WALKTHROUGH.md) provides a four-minute script, prepared-evidence and fresh-run variants, failure handling and honest judging answers. A prepared receipt is not presented as a request currently happening, and a fresh model call is not conflated with fresh MD. No simulated model response is used in the real-provider acceptance evidence.

## Reproduction and acceptance

```sh
# Real provider calls; separate mutable rehearsal workspace only:
make verify-live-muse
# New provider calls with disclosed reuse of actual immutable MD:
.venv/bin/python -m scripts.verify_live_muse --reuse-md
# Use another NANO_LIVE_MUSE_DB to preserve an existing rehearsal.

# Contract/physics/investigation regression and software gates:
make test
make build
# Stop the owned preview first; E2E makes isolated copies/workspaces:
.venv/bin/python scripts/e2e_servers.py stop runtime/demo
NANO_DB="$PWD/runtime/live-muse/original-snapshot.db" bash scripts/verify_e2e.sh
.venv/bin/python -m scripts.verify_rehearsal_preservation
```

Local before-task DB snapshots are needed for the full-table preservation check. Public integration/MD evidence does not contain private preparations. Do not run CLI acceptance concurrently with an HTTP investigation against the same rehearsal DB. CLI repeated acceptance replaces that workspace's mutable AI state; published scientific records remain unchanged. Provider availability/latency and model output can change; historical success is not a guarantee of future service.

Final executed gates:56 backend/public-data/AI contract tests passed (one dependency deprecation warning),11 live full-stack tests passed in83.19s, frontend production build/typecheck passed, and the original evaluator retained4 NO_DECISION outcomes per method using separate output files. Final executed commands/logs are in `validation.txt` and project TEST_RESULTS. A further genuine HTTP-worker check generated live hypotheses and a live plan for DEMO_401 without new MD; its receipt is `http-live-acceptance.json`. Browser inspection confirmed the new receipts, model scores/curve rendering, the frozen study's explicit no-model mode, and the guided DEMO_501 panel. Provider-fixture tests exercise invalid JSON, truncation, wrong model identity, duplicate/unregistered actions, unavailable evidence IDs, retry hashes and immutable verifier authority; they are explicitly not live integration evidence. Live HTTP E2E uses absent credentials to verify real fallback behavior and namespace isolation, while actual-provider acceptance is recorded separately above. Both are required for an honest integration claim.

Evidence files: first `acceptance-summary.json` / `action-trace.json.gz`; mixed `grounded-failed-summary.json` / `grounded-failed-trace.json.gz`; final `grounded-acceptance-summary.json` / `grounded-action-trace.json.gz`. Frozen scientific evidence remains exclusively under its existing study directories and has not been rewritten.
