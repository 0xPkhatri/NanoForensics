from backend.simulation.numpy_md_fallback import nve_window


def validate(summary):
    c = summary.numerical_check
    return c.is_valid and not c.nan_detected and c.energy_drift_ratio < 1e-3 and c.max_force_norm < 1e4 and c.max_step_displacement < .1 and c.thermostat_temperature_error_ratio < .35


__all__ = ['nve_window', 'validate']
