# Project state — demonstration evaluation complete (2026-11-04)

Latest tested integration checkpoint: 21324d6 on science/predeclared-demonstration. Scientific evidence checkpoint:872833f. Original audit source checkpoint:1dd84cf on science/root-cause-audit. Original working build remains available at 00c4375; initial build checkpoints and archived evidence are retained. A documentation-only acceptance checkpoint follows the source commit.

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
