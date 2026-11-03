# Project state — scientific audit complete (2026-11-04)

Latest tested source checkpoint: 1dd84cf on science/root-cause-audit. Original working build remains available at 00c4375; initial build checkpoints and archived evidence are retained. A documentation-only acceptance checkpoint follows the source commit.

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

## Prospective demonstration active

[~] V1 preregistration committed before any new trajectories; original checkpoint f4fbbca preserved.
[ ] Independent development, analysis lock, held-out generation/scoring and isolated dashboard integration.
Original immutable database fingerprint: runtime/demonstration/original-fingerprint.json. User edits retained.

[x] Separate study generator, geometric tools, analysis and namespace implemented; registration unchanged.
[x] Development baselines generated with real MD; target runtime exceeded honestly (~15 s/run).
[~] Development competing-arm outcomes and prospective held-out lock pending.
