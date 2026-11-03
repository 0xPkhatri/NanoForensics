"""Prospective supplemental V2 physical checks; cannot relax existing validity gates."""
import numpy as np
from backend.models.schemas import SimulationOutcome
from backend.demonstration.registration import registration
from backend.demonstration.geometry import study_components


def validate_study_run(specimen,result,version=None):
    design,digest=registration(version);checks={}
    p=specimen.protocol
    if 'true_temperature_relative_error_lt' in design['physical_validation'] and result.snapshots:
        thermal=result.diagnostics.get('thermal_diagnostics',{}).get('means',{}).get('laboratory')
        error=abs(thermal-p.temperature)/p.temperature if thermal is not None and p.temperature>0 else None
        checks['temperature_without_floor']={'measured':error,'upper_bound':.35,'passed':bool(error is not None and error<.35)}
    if 'open_slot_bank_separation_gt' in design['physical_validation'] and result.snapshots:
        q=np.asarray(specimen.coordinates);ref=np.asarray(result.reference_geometry['reference_coordinates']);a=2**(1/6);dy=a*np.sqrt(3)/2
        distances=[]
        for component in study_components(q):
            sites=np.asarray(component['sites'])
            if np.ptp(sites[:,1])<.5*dy:continue
            xmin,xmax=sites[:,0].min(),sites[:,0].max();mid=.5*(xmin+xmax)
            # Fixed central half, excluding the tips and surrounding ligaments.
            xmask=abs(q[:,0]-mid)<(xmax-xmin)/4
            lower=xmask & (abs(q[:,1]-(sites[:,1].min()-dy))<1e-6)
            upper=xmask & (abs(q[:,1]-(sites[:,1].max()+dy))<1e-6)
            distance=float(np.linalg.norm(ref[lower,None]-ref[None,upper],axis=2).min()) if lower.any() and upper.any() else None
            distances.append(distance)
        checks['open_slot_bank_separation']={'measured_distances':distances,'lower_bound':2.5,'passed':all(d is not None and d>2.5 for d in distances),'applicability':'two-row observable missing components only'}
    if 'force_moment_identity_absolute_error_lt' in design['physical_validation'] and result.snapshots:
        error=result.diagnostics.get('force_balance',{}).get('max_identity_residual')
        checks['pair_force_moment_identity']={'measured':error,'upper_bound':1e-8,'passed':error is not None and error<1e-8}
    out=result.model_copy(deep=True)
    out.diagnostics['registered_study_checks']={'registration_hash':digest,'checks':checks}
    failed=[name for name,check in checks.items() if not check['passed']]
    if failed:
        out.numerical_check.is_valid=False;out.outcome=SimulationOutcome.EXECUTION_FAILED;out.failure_strain=None
        out.error_code='REGISTERED_PHYSICAL_CHECK_FAILED';out.error_message='Failed supplemental study checks: '+', '.join(failed)
    return out
