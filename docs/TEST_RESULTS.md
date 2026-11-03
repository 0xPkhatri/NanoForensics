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
