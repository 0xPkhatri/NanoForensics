# DEMO_501 hackathon walkthrough

**Opening:** “NanoForensics turns a failure curve into a testable investigation. Muse Spark proposes competing explanations and physical experiments; real molecular dynamics produces the evidence; an independent verifier controls the scientific conclusion.”

Keep the limitation visible throughout: **the full preregistered study is NOT_VALIDATED**. DEMO_501 is one successful held-out geometry from a partially successful athermal toy study. This presentation is a post-study AI integration rehearsal on a published case, not a new blind discovery.

## Preflight

1. Open http://127.0.0.1:3000. Select **Live Muse Spark rehearsal · separate AI workspace**, then **DEMO_501 · held_out**. The original frozen benchmark and frozen study remain separate choices.
2. Check the health endpoint and provider settings. The saved key stays in ignored `.env`; the endpoint/model are `https://api.meta.ai/v1` and `muse-spark-1.3`. Never show the key or open `.env` on screen. `make verify-live-muse` performs real calls plus six fresh counterfactual MD executions in the rehearsal database; it does not regenerate the study.
3. Keep **Live AI action receipts** open. Stored receipts establish prior successful requests, not a request happening now. A new operation needs its own successful response to earn a new live receipt. The header labels the last action; a connection-only probe cannot earn a live investigation claim.
4. Confirm **NOT_VALIDATED**, `T*=0`, fixed dt/rate/horizon, and deterministic replay labels. Three replay labels are not three independent thermal samples.
5. For a live performance, reserve about 2–3 minutes for the complete worker loop; one measured fresh run took 121.95 seconds. Provider availability and latency can change. Allow extra time; no runtime guarantee is implied.

## Four-minute presentation

| Time | Screen/action | Suggested narration |
|---|---|---|
| 0:00–0:30 | Dataset selector, frozen status and scope | “The original four benchmarks remain untouched. This separate study achieved partial success. The full study did not validate, and we show that result.” |
| 0:30–1:00 | Atomic structure and baseline response | “This is a genuine 2D shifted-force Lennard-Jones trajectory. We observe missing-site geometry and failure; we do not give the model a preparation label or the expected diagnosis.” |
| 1:00–1:30 | Click **Generate hypotheses**; inspect hypothesis/planning receipts | “These are separate fresh Muse Spark requests. The receipts record model, host, latency, provider token counts, response ID and request/response hashes. The model provides mechanisms, predictions and planning rationale within two allowlisted repairs.” |
| 1:30–3:15 | Click **Start autonomous investigation**; watch worker progress and receipt timeline | “The solver applies geometric reconstruction, runs matched replay labels, and records numerical checks. The agent receives each completed result and revises its beliefs. It cannot edit the protocol, thresholds or verifier verdict.” |
| 3:15–3:45 | Compare both curves, verification cards and score changes | “The archived measured interior repair shifts failure strain from 0.0815 to 0.1205: +47.85%. The competing boundary repair gives −0.61%. In one verified live rehearsal the interior score rose from 0.35 to 0.92 after that evidence. Scores and wording may differ on a new model call; they are subjective.” |
| 3:45–4:00 | Audit export, full-study notice | “We have a reproducible counterfactual distinction for this one geometry. The boundary case elsewhere remained inconclusive, so the full study remains NOT_VALIDATED. This is not real-material or thermal-population validation.” |

**Closing:** “The useful capability is an auditable loop: propose, intervene, measure, revise—and retain the failures.”

The **Generate hypotheses** button starts a new hypothesis/plan cycle. **Start autonomous investigation** also starts a new cycle and runs both allowed arms; its model outputs may differ from the preceding manual generation. For a continuous manually controlled cycle, run each proposal once with **Run paired test**. Neither path has a guaranteed experiment order. The first verified model chose the boundary repair first, contrary to its eventual larger-effect conclusion.

## Fast prepared-evidence presentation

Use the completed rehearsal without pressing mutation buttons. Inspect the stored receipts, compare the two measured curves, read the belief changes, then export the audit. Say “previously completed live model calls and genuine MD” rather than “the model is running live now.” The current rehearsal may use explicit immutable MD cache reuse; its trace discloses that. Fresh model inference and fresh MD are independent provenance dimensions.

For a repeat with new model calls but reused immutable MD, explicitly use:

```sh
.venv/bin/python -m scripts.verify_live_muse --reuse-md
```

For new model calls and newly executed counterfactual MD, use:

```sh
make verify-live-muse
```

These commands write only the separate AI rehearsal state/results. Run one at a time; do not run the CLI against an active HTTP investigation in the same workspace. To keep a prepared rehearsal unchanged, choose a separate `NANO_LIVE_MUSE_DB` for new CLI acceptance. Model API calls consume provider quota.

## Failure and challenge handling

- If any receipt says **OFFLINE FALLBACK**, say exactly which operation failed. The deterministic physical tools still function, but that operation is not live Muse usage. Do not hide the fallback or use an old green receipt as proof of a new request.
- If the provider is unavailable, continue with prepared evidence and say that clearly. A new inconclusive or numerically failed result must remain visible; do not reset/retry to cherry-pick a desired diagnosis.
- If asked whether the study passed, answer **“No. One held-out distinction and the negative control passed; the boundary geometry missed the fixed recovery criterion.”**
- If asked whether the AI is always right, answer **“No.”** The first live rehearsal wrongly located the boundary defect on the crack-initiation side in its initial narrative. The deterministic tool edited the measured geometry correctly. That original transcript is retained. We then supplied explicit coordinate-derived component positions to reduce this inference error; that is model-input grounding, not a changed physical result or benchmark threshold.
- If asked whether 0.92 is scientific confidence, answer **“No. It is the model's subjective score. Numerical validity and support thresholds come from the independent verifier.”**
- If asked about generalization, identify the small athermal lattice, one-row held-out geometry shift, finite rate/damping and absence of independent thermal samples. No superiority over baselines or real-material prediction is claimed.

## Evidence to have ready

- `docs/live-muse/acceptance-summary.json`: first verified live loop with six fresh MD replay executions.
- `docs/live-muse/action-trace.json.gz`: original complete action/evidence transcript, including the initial localization error.
- `docs/live-muse/grounded-acceptance-summary.json` and `grounded-action-trace.json.gz`: subsequent position-grounded rehearsal, explicitly reusing immutable MD.
- `docs/live-muse/INTEGRATION_REPORT.md`: implementation, measurements, verification and limitations.
- `docs/demonstration/v3/STUDY_REPORT.md`: unchanged scientific study report.

Before judging, recheck connection and per-action receipts; a historical successful integration does not guarantee future provider availability.
