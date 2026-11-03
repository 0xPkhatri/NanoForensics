"""Exact pair-force moment accounting, not a rescaling of reported tensile stress."""
import numpy as np


def force_moment_balance(q,v,force,virial,mobile,bottom,top,area,realized_force=None):
    center=.5*(q[bottom,1].mean()+q[top,1].mean())
    y=q[:,1]-center
    full=-float(virial[:,1,1].sum())/area
    included=-float(virial[mobile,1,1].sum())/area
    boundary=-float(np.sum(y[~mobile]*force[~mobile,1]))/area
    body=-float(np.sum(y[mobile]*force[mobile,1]))/area
    kinetic=-float(np.sum(v[mobile,1]**2))/area
    total=-float(np.sum(y[mobile]*realized_force[mobile,1]))/area if realized_force is not None else None
    return {'realized_mobile_force_moment':total,'thermostat_force_moment':total-body if total is not None else None,'full_configurational_virial':full,'mobile_configurational_virial':included,
            'boundary_force_moment':boundary,'mobile_force_moment':body,
            'excluded_grip_virial':full-included,'mobile_kinetic_stress':kinetic,
            'identity_residual':full-boundary-body,
            'reported_mobile_stress':included+kinetic}
