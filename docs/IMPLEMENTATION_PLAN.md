# NanoForensics implementation plan

Authoritative requirements: ../AGENTS.md. Repository root is the existing workspace `x` (no extra nested checkout).

1. Phase 1: contracts, analytic SFLJ, NumPy and verified LAMMPS trajectory paths, geometric edits, reference rupture, empirical verifier; calibrate complete runs. Gate: pytest physics + verifier.
2. Phase 2: immutable blind cases, SQLite, bounded live JSON inference with visible fallback, deterministic registered tools and adaptive investigation. Gate: investigation pytest.
3. Phase 3: asynchronous durable API jobs, actual process cancellation/timeouts and fair comparator evaluation. Gate: python -m benchmarks.evaluate.
4. Phase 4: Next.js scientific workbench and operational documentation. Gate: npm install && npm run build.
5. Phase 5: live two-server E2E, duplicate lock, persistence, cancellation, timeout and full investigations. Gate: bash scripts/verify_e2e.sh.

Never infer success from expected benchmark labels. Commit each passed phase; preserve executed outputs. Three seeds: 42, 137, 271. Physical data can be censored or numerically invalid.

## Accepted completion

[x] All five ordered gates passed with corrected solver sflj-1.1.
[x] Source and evidence checkpointed in Git.
[x] Late dimensionality failure preserved, corrected and independently checked; all affected evidence regenerated.
[x] Actual live two-server cancellation, deadline, persistence, crash recovery and fresh investigations passed.
[x] Benchmark NO_DECISION counts and absent live-provider credentials disclosed.
