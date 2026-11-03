# Handoff — active scientific correction

Final regression exposed LAMMPS z/vz motion because enforce2d preceded Langevin. Do NOT use the earlier benchmark results as valid scientific evidence. Solver sflj-1.1 moves enforce2d after all force-changing fixes, checks dump z/vz, and invalidates old content-addressed caches by version. No thresholds, input geometry or physical protocol have been tuned.

Next: run Phase 1 gate, archive old runtime SQLite and benchmark reports with explicit INVALID status, regenerate all four cases, then repeat gates 2–5. Keep old Git checkpoints and raw evidence for audit. No live Muse credentials available. E2E harness with process cancellation/restarts implemented, but its first 9-test pass predates dimensionality check.
