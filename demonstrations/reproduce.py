"""Fresh rerun of the first registered development ID/seed, irrespective of outcome."""
import hashlib
import json
from backend.demonstration.registration import registration,STUDY_DB,PUBLIC_DIR
from backend.demonstration.storage import DemonstrationStore
from backend.demonstration.validation import validate_study_run
from backend.simulation.worker import run_bounded


def physical_record(result):
    return {key:getattr(result,key) for key in ['seed','outcome','peak_stress','failure_strain','stress_strain_curve','snapshots','numerical_check','reference_geometry','protocol_hash','initial_configuration_hash','engine_used']}


def verify():
    design,digest=registration();case_id=design['development']['case_ids'][0];seed=design['development']['seeds'][0]
    store=DemonstrationStore(STUDY_DB);source=store.public(case_id).baseline_simulation.replicate_results[0]
    specimen=store.specimen(case_id);specimen.protocol.seed=seed
    fresh=validate_study_run(specimen,run_bounded(specimen,timeout=90))
    actual=fresh.model_dump(mode='json')
    keys=list(physical_record(fresh))
    # Pydantic objects are compared through the same JSON representation as stored records.
    old={key:source[key] for key in keys};new={key:actual[key] for key in keys}
    result={'registration_hash':digest,'case_id':case_id,'seed':seed,'exact_numeric_reproduction':old==new,'physical_record_sha256':hashlib.sha256(json.dumps(new,sort_keys=True).encode()).hexdigest(),'excluded':'walltime, worker PID and process telemetry','engine':fresh.engine_used,'fresh_wall_time_sec':fresh.wall_time_sec}
    (PUBLIC_DIR/'reproducibility.json').write_text(json.dumps(result,indent=2))
    if not result['exact_numeric_reproduction']:raise RuntimeError('Registered same-engine reproducibility check failed')
    return result


if __name__=='__main__':print(json.dumps(verify(),indent=2))
