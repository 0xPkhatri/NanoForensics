# Executed results

Setup: Python 3.15 default; Python 3.13 selected for dependency compatibility. LAMMPS 30 Sep 2026 installed at /opt/homebrew/bin/lmp_serial. No tests run yet.

## Phase 1 — PASS

Command: `.venv/bin/pytest tests/test_physics_and_defects.py tests/test_verifier.py -v -s`

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 13 items

tests/test_physics_and_defects.py::test_sflj_derivative_cutoff_and_near_limit PASSED
tests/test_physics_and_defects.py::test_arbitrary_coordinates_force_virial_against_independent_reference PASSED
tests/test_physics_and_defects.py::test_tension_sign_and_grip_reaction_elastic PASSED
tests/test_physics_and_defects.py::test_nve_500_step_total_energy_conservation 500-step NVE max/terminal drift: 1.2315537663914266e-06 3.1114277362151706e-07
PASSED
tests/test_physics_and_defects.py::test_offgrid_table_and_real_lammps_output SFLJ interpolation validation: {'minimum_sampled_distance': 0.8000315365768289, 'energy_max_absolute_error': 1.1109873149450777e-05, 'force_max_absolute_error': 0.0002007423646546158, 'energy_scale_relative_error': 2.583236828522499e-07, 'force_scale_relative_error': 2.647278030751452e-07, 'points': 20000, 'lammps_pair_output_status': 'PASS', 'lammps_actual': {'minimum_sampled_distance': 0.800013, 'energy_max_absolute_error': 4.1755040321334036e-05, 'force_max_absolute_error': 0.0008497719763909117, 'energy_scale_relative_error': 9.705593324957982e-07, 'force_scale_relative_error': 1.1202707806996011e-06}}
PASSED
tests/test_physics_and_defects.py::test_native_lammps_pair_parity PASSED
tests/test_physics_and_defects.py::test_geometric_healing_changes_force_and_measured_response Actual healing effect (may be censored): 2.585403455132743 2.697648662456674 None None
PASSED
tests/test_physics_and_defects.py::test_driven_numpy_valid_reproducible_and_censored PASSED
tests/test_physics_and_defects.py::test_worker_timeout_terminates_process PASSED
tests/test_verifier.py::test_free_surface_and_notch_not_initial_fracture PASSED
tests/test_verifier.py::test_severed_reference_bonds_are_separate_from_coordination PASSED
tests/test_verifier.py::test_persistent_cluster_and_retrospective_peak PASSED
tests/test_verifier.py::test_empirical_verdicts_censoring_failures_and_id_invariance PASSED

============================== 13 passed in 1.61s ==============================
```

Calibration command: `.venv/bin/python -m benchmarks.calibrate_runtime`. Measured complete runs and native pair validation in [CALIBRATION.json](CALIBRATION.json). 12×12 retained, target strain 0.65, dt 0.002, 2000 BAOAB warmup and 50 unstrained NVE steps. Three-seed healing SNR is not inferred from the one-pair contract check; recovery is censored there.

Initial failures fixed: pair_write uses lowercase `r`; table indices require integers; actual LAMMPS linear table interpolant required 20,000 points to meet absolute and relative bounds. No scientific assertion was relaxed. Cross-engine ensemble comparison NOT_RUN (P2); native two-body and actual table parity PASS.

## Phase 2 — PASS

Generation: `.venv/bin/python -m benchmarks.generate_cases` froze 4 cases, each with actual seeds 42/137/271 before observer runs. Baseline ALPHA has two invalid temperature-stability replicates (ratios 0.363 and 0.356 exceed 0.35); retained without tuning thresholds or hidden preparation.

Command: `.venv/bin/pytest tests/test_investigation_loop.py -v -s`
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 9 items

tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_ALPHA] CASE_ALPHA INCONCLUSIVE verifications: [('heal_interior_vacancy', 'PENDING', 'EXECUTION_FAILED', None)]
PASSED
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_BETA] CASE_BETA INCONCLUSIVE verifications: [('smooth_surface_notch', 'REJECTED', 'COMPLETE', -3.5714285714286564)]
PASSED
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_GAMMA] CASE_GAMMA INCONCLUSIVE verifications: [('normalize_strain_rate', 'INCONCLUSIVE', 'COMPLETE', -28.846153846153793)]
PASSED
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_DELTA] CASE_DELTA INCONCLUSIVE verifications: [('normalize_temperature', 'INCONCLUSIVE', 'COMPLETE', 7.766990291262283)]
PASSED
tests/test_investigation_loop.py::test_public_metadata_and_permuted_ids PASSED
tests/test_investigation_loop.py::test_backend_has_no_privileged_reads PASSED
tests/test_investigation_loop.py::test_missing_credentials_and_invalid_model_json PASSED
tests/test_investigation_loop.py::test_sqlite_frozen_specimen_and_job_uniqueness PASSED
tests/test_investigation_loop.py::test_live_provenance_requires_operation_schema_success PASSED

============================== 9 passed in 4.82s ===============================
```

Phase 1 regression: 13 passed. Unchanged protocol edits now return NO_APPLICABLE_EDIT. Three-pair effects are descriptive. No live Muse credentials were available; provider-schema tests use clearly identified test fixtures, not real live-integration evidence.

## Phase 3 — PASS

Command: `.venv/bin/python -m benchmarks.evaluate`
```json
{
  "counts": {
    "Fixed checklist": {
      "CORRECT": 0,
      "INCORRECT": 0,
      "NO_DECISION": 4
    },
    "NanoForensics": {
      "CORRECT": 0,
      "INCORRECT": 0,
      "NO_DECISION": 4
    },
    "One-shot": {
      "CORRECT": 0,
      "INCORRECT": 0,
      "NO_DECISION": 4
    }
  },
  "report": "/Users/prakash_mac/Desktop/code/x/docs/BENCHMARK_REPORT.md",
  "raw": "/Users/prakash_mac/Desktop/code/x/docs/BENCHMARK_REPORT.json"
}
```

All three methods yielded 0 correct / 0 incorrect / 4 NO_DECISION. This is an honest inconclusive benchmark, not evidence of discovery or superiority. Full immutable-trial evidence: BENCHMARK_REPORT.json; readable comparison: BENCHMARK_REPORT.md.

Live backend smoke check: health HTTP 200; four cases; simultaneous duplicate auto-investigation returned [202,409]; real isolated job with 0.05-second deadline reached TIMED_OUT and was terminated/reaped.

## Phase 4 — PASS

Command: `cd frontend && npm install && npm run build`

Next.js 16.4.4 (meets 14+ requirement), React 19, Tailwind 3, Plotly. npm audit: 0 vulnerabilities. Production compilation, TypeScript and static-page generation passed.
```text

> nanoforensics-workbench@1.0.0 build
> next build

▲ Next.js 16.4.4 (Turbopack)
✓ Running next.config.mjs took 6ms

  Creating an optimized production build ...
✓ Compiled successfully in 381ms
  Running TypeScript ...
  Finished TypeScript in 738ms ...
  Collecting page data using 4 workers ...
  Generating static pages using 4 workers (0/3) ...
✓ Generating static pages using 4 workers (3/3) in 127ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
└ ○ /_not-found


○  (Static)  prerendered as static content

```

Local preview launched after build; visual/interactive QA continues with mandatory Phase 5. Counterfactual API execution now defaults to fresh computation; audit distinguishes cache reuse.

## Scientific audit correction — earlier LAMMPS trajectory evidence INVALIDATED

A final regression added explicit dump z/vz checks and failed the geometric-response test: Langevin was registered after enforce2d, so its post-force stochastic z component could evade the earlier planar constraint. This is an objective dimensionality bug, not a benchmark tuning decision. Earlier archived trajectory-based metrics, calibration and verdict evidence are invalid; pair_write force/energy checks and NumPy NVE checks remain valid. Solver bumped to sflj-1.1; enforce2d is registered last. The frozen input coordinates, preparation protocols, intervention algorithms and acceptance thresholds remain unchanged. Regenerate all trajectory records before further observer/scorer runs. Initial Phase 5 HTTP gate: 9 passed in 28.07 s, superseded pending corrected solver rerun.

## Corrected Phase 1 — PASS

Solver sflj-1.1. Explicit z/vz=0 validation passes with enforce2d after Langevin. Aggregation also excludes failed empty trajectories without crashing or contaminating means.

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 14 items

tests/test_physics_and_defects.py::test_sflj_derivative_cutoff_and_near_limit PASSED
tests/test_physics_and_defects.py::test_arbitrary_coordinates_force_virial_against_independent_reference PASSED
tests/test_physics_and_defects.py::test_tension_sign_and_grip_reaction_elastic PASSED
tests/test_physics_and_defects.py::test_nve_500_step_total_energy_conservation 500-step NVE max/terminal drift: 1.2315537663914266e-06 3.1114277362151706e-07
PASSED
tests/test_physics_and_defects.py::test_offgrid_table_and_real_lammps_output SFLJ interpolation validation: {'minimum_sampled_distance': 0.8000315365768289, 'energy_max_absolute_error': 1.1109873149450777e-05, 'force_max_absolute_error': 0.0002007423646546158, 'energy_scale_relative_error': 2.583236828522499e-07, 'force_scale_relative_error': 2.647278030751452e-07, 'points': 20000, 'lammps_pair_output_status': 'PASS', 'lammps_actual': {'minimum_sampled_distance': 0.800013, 'energy_max_absolute_error': 4.1755040321334036e-05, 'force_max_absolute_error': 0.0008497719763909117, 'energy_scale_relative_error': 9.705593324957982e-07, 'force_scale_relative_error': 1.1202707806996011e-06}}
PASSED
tests/test_physics_and_defects.py::test_native_lammps_pair_parity PASSED
tests/test_physics_and_defects.py::test_geometric_healing_changes_force_and_measured_response Actual healing effect (may be censored): 2.585425228037246 2.697670474193199 None None
PASSED
tests/test_physics_and_defects.py::test_driven_numpy_valid_reproducible_and_censored PASSED
tests/test_physics_and_defects.py::test_worker_timeout_terminates_process PASSED
tests/test_verifier.py::test_free_surface_and_notch_not_initial_fracture PASSED
tests/test_verifier.py::test_severed_reference_bonds_are_separate_from_coordination PASSED
tests/test_verifier.py::test_persistent_cluster_and_retrospective_peak PASSED
tests/test_verifier.py::test_empirical_verdicts_censoring_failures_and_id_invariance PASSED
tests/test_verifier.py::test_aggregate_excludes_failed_empty_trajectories_without_inventing_statistics PASSED

=============================== warnings summary ===============================
tests/test_verifier.py::test_aggregate_excludes_failed_empty_trajectories_without_inventing_statistics
  /Users/prakash_mac/Desktop/code/x/.venv/lib/python3.13/site-packages/pydantic/main.py:520: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected `enum` - serialized value may not be as expected [field_name='outcome', input_value='EXECUTION_FAILED', input_type=str])
    return self.__pydantic_serializer__.to_python(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 14 passed, 1 warning in 1.19s =========================
```
