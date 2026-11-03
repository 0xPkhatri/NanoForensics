# Final accepted verification — solver sflj-1.1

All five current phase gates PASS. Phases 1/2: 14 and 11 tests respectively; combined final regression: 25 passed. Phase 3 evaluation: all three methods 0 correct / 0 incorrect / 4 NO_DECISION. Phase 4: production Next.js/TypeScript build PASS, 0 npm vulnerabilities. Phase 5: 9 live full-stack tests passed while both real servers were running, with process cleanup afterward.

Earlier LAMMPS trajectory reports below the correction notice are historical and superseded. The z/vz validation caught a dimensionality bug; enforce2d was moved after Langevin, solver/caches versioned, and all trajectories regenerated with unchanged geometry, controls and thresholds. Historical artifacts under archive are explicitly INVALID.

Current limitations: Muse API not demonstrated (credentials absent; visibly deterministic fallback). No unique benchmark diagnosis established. Three-seed cross-engine pristine-lattice comparison is descriptive, not evidence of population equivalence.


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

## Corrected solver acceptance — Phases 1 and 2 PASS

The frozen dataset was regenerated with identical visible coordinates and physical protocols; cache version sflj-1.1 prevents use of prior trajectory records. Explicit planar checks PASS. In-plane outcomes remained identical.

Phase 1 command: `.venv/bin/pytest tests/test_physics_and_defects.py tests/test_verifier.py -v -s`
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

============================== 14 passed in 1.22s ==============================
```

Phase 2 command: `.venv/bin/pytest tests/test_investigation_loop.py -v -s`
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 11 items

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
tests/test_investigation_loop.py::test_diagnostic_new_seeds_measure_variance_without_claiming_repair Diagnostic actual seed outcomes: [(42, 'FRACTURED', 0.20750000000000002), (137, 'FRACTURED', 0.12999999999999967), (271, 'FRACTURED', 0.17749999999999955), (101, 'FRACTURED', 0.20499999999999985), (202, 'FRACTURED', 0.16749999999999976), (303, 'FRACTURED', 0.2174999999999998)]
PASSED
tests/test_investigation_loop.py::test_model_claimed_support_cannot_bypass_empirical_verifier PASSED

============================== 11 passed in 4.70s ==============================
```

Diagnostic new seeds 101/202/303 ran real trajectories; repeat-only evidence cannot support a repair. Model-authored SUPPORTED statuses are reset to PENDING until independent empirical verification. Calibration refreshed; see CALIBRATION.json.

## Corrected Phase 3 — PASS

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

Current BENCHMARK_REPORT.md / .json use solver sflj-1.1 and fixed inputs. Every method: 0 CORRECT, 0 INCORRECT, 4 NO_DECISION. Historical v1 records in archive remain invalid and are not used.

## Corrected Phase 4 — PASS

Command: `cd frontend && npm install && npm run build`

0 npm vulnerabilities. Updated first-valid-replicate and excluded-failed-envelope wording.
```text

> nanoforensics-workbench@1.0.0 build
> next build

▲ Next.js 16.4.4 (Turbopack)
✓ Running next.config.mjs took 7ms

  Creating an optimized production build ...
✓ Compiled successfully in 505ms
  Running TypeScript ...
  Finished TypeScript in 749ms ...
  Collecting page data using 4 workers ...
  Generating static pages using 4 workers (0/3) ...
✓ Generating static pages using 4 workers (3/3) in 125ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
└ ○ /_not-found


○  (Static)  prerendered as static content

```

## Final Phase 5 — PASS

Command: `bash scripts/verify_e2e.sh`
```text
{
  "status": "EXISTING_FROZEN_INPUTS",
  "cases": [
    "CASE_ALPHA",
    "CASE_BETA",
    "CASE_DELTA",
    "CASE_GAMMA"
  ]
}
Both real servers are ready; running live E2E acceptance tests.
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 9 items

tests/test_e2e_fullstack.py::test_health_cors_dashboard_and_blind_metadata PASSED
tests/test_e2e_fullstack.py::test_request_validation_and_admin_guard PASSED
tests/test_e2e_fullstack.py::test_conflict_reset_and_real_worker_cancellation Real worker cancellation: 19978 [19981]
PASSED
tests/test_e2e_fullstack.py::test_real_job_and_replicate_deadlines Actual replicate timeout: RUN_TIMEOUT 0.509720957983518
PASSED
tests/test_e2e_fullstack.py::test_full_closed_loop_http_investigation_and_sqlite_persistence[CASE_ALPHA] CASE_ALPHA INCONCLUSIVE [('heal_interior_vacancy', 'PENDING', 'EXECUTION_FAILED')]
PASSED
tests/test_e2e_fullstack.py::test_full_closed_loop_http_investigation_and_sqlite_persistence[CASE_DELTA] CASE_DELTA INCONCLUSIVE [('normalize_temperature', 'INCONCLUSIVE', 'COMPLETE')]
PASSED
tests/test_e2e_fullstack.py::test_proposal_execution_and_immutable_result_http PASSED
tests/test_e2e_fullstack.py::test_server_restart_preserves_durable_state PASSED
tests/test_e2e_fullstack.py::test_server_crash_recovers_orphaned_worker_and_unlocks_case Crash recovery: INTERRUPTED worker descendants terminated; durable case lock released
PASSED

============================== 9 passed in 28.36s ==============================
E2E process logs and isolated SQLite database: /Users/prakash_mac/Desktop/code/x/runtime/e2e-pZIzHu
```

The shell trap cleaned both owned server process groups. Cancellation and deadline tests observed real nested workers; reset/hypothesis duplicates returned 409; fresh ALPHA/DELTA investigations reached terminal states; restart retained SQLite state; forced server crash recovered and terminated orphaned worker descendants. The API and dashboard remained responsive during work. Latest E2E output also retained in E2E_LAST_RUN.txt.

## Final combined regression — PASS

Command: `.venv/bin/pytest tests/test_physics_and_defects.py tests/test_verifier.py tests/test_investigation_loop.py -v`
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0 -- /Users/prakash_mac/Desktop/code/x/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/prakash_mac/Desktop/code/x
configfile: pytest.ini
plugins: anyio-4.16.0
collecting ... collected 25 items

tests/test_physics_and_defects.py::test_sflj_derivative_cutoff_and_near_limit PASSED [  4%]
tests/test_physics_and_defects.py::test_arbitrary_coordinates_force_virial_against_independent_reference PASSED [  8%]
tests/test_physics_and_defects.py::test_tension_sign_and_grip_reaction_elastic PASSED [ 12%]
tests/test_physics_and_defects.py::test_nve_500_step_total_energy_conservation PASSED [ 16%]
tests/test_physics_and_defects.py::test_offgrid_table_and_real_lammps_output PASSED [ 20%]
tests/test_physics_and_defects.py::test_native_lammps_pair_parity PASSED [ 24%]
tests/test_physics_and_defects.py::test_geometric_healing_changes_force_and_measured_response PASSED [ 28%]
tests/test_physics_and_defects.py::test_driven_numpy_valid_reproducible_and_censored PASSED [ 32%]
tests/test_physics_and_defects.py::test_worker_timeout_terminates_process PASSED [ 36%]
tests/test_verifier.py::test_free_surface_and_notch_not_initial_fracture PASSED [ 40%]
tests/test_verifier.py::test_severed_reference_bonds_are_separate_from_coordination PASSED [ 44%]
tests/test_verifier.py::test_persistent_cluster_and_retrospective_peak PASSED [ 48%]
tests/test_verifier.py::test_empirical_verdicts_censoring_failures_and_id_invariance PASSED [ 52%]
tests/test_verifier.py::test_aggregate_excludes_failed_empty_trajectories_without_inventing_statistics PASSED [ 56%]
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_ALPHA] PASSED [ 60%]
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_BETA] PASSED [ 64%]
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_GAMMA] PASSED [ 68%]
tests/test_investigation_loop.py::test_full_blind_autonomous_loop[CASE_DELTA] PASSED [ 72%]
tests/test_investigation_loop.py::test_public_metadata_and_permuted_ids PASSED [ 76%]
tests/test_investigation_loop.py::test_backend_has_no_privileged_reads PASSED [ 80%]
tests/test_investigation_loop.py::test_missing_credentials_and_invalid_model_json PASSED [ 84%]
tests/test_investigation_loop.py::test_sqlite_frozen_specimen_and_job_uniqueness PASSED [ 88%]
tests/test_investigation_loop.py::test_live_provenance_requires_operation_schema_success PASSED [ 92%]
tests/test_investigation_loop.py::test_diagnostic_new_seeds_measure_variance_without_claiming_repair PASSED [ 96%]
tests/test_investigation_loop.py::test_model_claimed_support_cannot_bypass_empirical_verifier PASSED [100%]

============================== 25 passed in 5.84s ==============================
```

## Independent cross-engine experiment — DESCRIPTIVE_LOW_SAMPLE

Command: `.venv/bin/python -m benchmarks.validate_engines`. Six actual, bounded runs on a pristine 12×12 lattice, seeds 42/137/271 per engine; same preparation/protocol. LAMMPS peak mean 2.87739, NumPy 2.85946 (0.6271% relative difference). All six fractured; crack-region agreement 2/3. Student-t uncertainty intervals, assumptions and all raw results are in ENGINE_COMPARISON.json. n=3 does not establish population equivalence or parity for all benchmark conditions.

## Final browser QA — PASS

Compiled production frontend, actual backend, corrected solver sflj-1.1. Used the Browser skill to select BETA, generate hypotheses, observe action disabling/progress, click the registered surface-repair paired test, wait for terminal state and open/close the scientific audit dialog. API audit confirms three freshly computed counterfactual replicates. Mechanical result: -3.5714% paired recovery; tested mechanism REJECTED, final investigation INCONCLUSIVE. Canvas and Plotly rendered actual data; no browser console errors. Local demo left running with owned process records in runtime/demo.

## Scientific audit resumed — 2026-11-04

Starting checkpoint 00c4375; frozen specimen snapshot and fingerprints stored in runtime/science-audit. Existing user edits are preserved. Independent baseline rerun on DB clone: 25 passed in 5.68 s. Three new invariants pass: kinetic-energy decomposition and Galilean invariance, observable repair geometry/energy, and same-microstate NVE dt refinement. Temperature diagnostics are supplemental; raw-temperature bound 0.35 is unchanged. New protocol runs are independent sensitivities, never substituted into frozen benchmark data. See SCIENTIFIC_AUDIT_PLAN.md.

## Scientific audit checkpoint — measured mechanisms and stricter inference

Original 25 tests reproduced. Expanded suite: 32 passed, including five physical audit invariants and red/green tests for partial censoring and duplicate/unexpected seed labels. No threshold changed. Nine BETA pairs give +0.457% recovery, SNR 0.0735, CV 5.59%; geometric reconstruction is exact but recovery is negligible. GAMMA negative rate-normalization recovery persists at fine sampling (-28.36%) and half-dt (-22.14%). ALPHA slower-loading pilot gives 3/3 valid runs (original 1/3) and reduces early traction discrepancy to ~18%; it is explicitly a new protocol, not a rewritten benchmark. Exact pair-force moment identities close to ~1e-15, exposing body-force and boundary contributions. See SCIENTIFIC_FINDINGS.md and science-audit/ raw artifacts. Frozen specimen/public-baseline rows and 29 existing result records verified unchanged. Full evaluator/build/live E2E reruns follow.

## Scientific audit final acceptance — 2026-11-04

Source checkpoint 1dd84cf. All gates rerun: 32 backend tests PASS; evaluator PASS (every method 0 correct / 0 incorrect / 4 NO_DECISION); production Next.js/TypeScript build PASS; post-restoration typecheck PASS; npm audit 0 vulnerabilities; live E2E 9 passed in 29.79 s while both servers ran. Cancellation, timeouts, duplicate guards, fresh investigations, persistence and crash recovery passed. Full executed output retained in science-audit/validation.txt. Frozen specimen/public-baseline rows and 29 pre-existing immutable results remain unchanged. Raw research archive has 159 diagnostic captures covering 111 distinct input-engine IDs, not 159 independent samples. See SCIENTIFIC_FINDINGS.md for measured ALPHA stability-control improvements, BETA negligible nine-pair recovery and GAMMA persistent adverse rate effect. The original demo has been restored without resetting user investigation state. Pre-existing uncommitted edits preserved.

## Prospective demonstration preregistration and implementation (before held-out data)

Registration commit b879104, SHA256 09f0c37f89155e4d60af658b7e1c538cb8aaf026ab0c44e9ef85f44e1322aa6a. New development and held-out cases use separate database, opaque namespace and fixed seed sets. No thresholds changed; V1 is one design with no post-outcome tuning. Observable component reconstruction and negative-control tests pass; API namespace/protocol guards pass. Development runs take ~15 s, exceeding the registered runtime target while preserving the full horizon. Original 4 specimen/public-baseline records and all 29 result rows verified unchanged. Development scientific validation and held-out analysis lock pending.

## Prospective studies before held-out generation

V1 preregistration b879104 failed to discriminate in development; its held-out set was not generated. V2 preregistration 522d133 added open-slot and stricter true-temperature checks; it failed those physical checks in development and its held-out set was not generated. Both negative studies and all MD records are retained. V3 preregistration e17fc8b is an explicitly athermal deterministic reference with new seeds/opaque IDs, no independent-thermal-sample confidence claim, and mandatory held-out timestep convergence. Its development satisfies the registered dominant-repair contrast. A pre-holdout implementation error requiring exactly one beneficial repair was corrected to the registered larger-effect contrast; original and corrected analyses, hashes and identical MD/verification records are retained. No protocol, geometry or threshold changed. Exact fresh trajectory reproduction passed; numerical replays are not independent samples. Backend regression 46 passed; frontend production build passes. Original 4 cases and 29 result rows remain unchanged. Held-out generation requires committed scientific source plus an explicit hash lock.
