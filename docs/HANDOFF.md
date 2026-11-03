# Handoff

Phase 1 gate PASS: 13 tests. Physics is actual pairwise SFLJ. LAMMPS native verified with pair_write. Optional table verified at 20,000 points. 500-step NVE max drift 1.23e-6. Full-run calibration in CALIBRATION.json. Common NumPy preparation precedes either loader; thermostats differ during driven loading, so cross-engine ensembles NOT_RUN. Git checkpoint contains this state.

Next: implement Phase 2. Live modules must never read privileged benchmark preparation data. Immutable visible input must suffice for all geometric edits. Use `.venv/bin/python`, `.venv/bin/pytest`.
