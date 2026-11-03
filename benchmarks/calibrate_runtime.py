"""Measure full runs, retain a meaningful horizon; never tune using hidden labels."""
import json
import platform
from datetime import datetime,timezone
from pathlib import Path
from backend.models.schemas import SpecimenInput, Protocol
from backend.simulation.defect_generator import hex_lattice
from backend.simulation.lammps_runner import run_simulation, engine_capabilities


def calibrate(output='runtime/calibration.json'):
    q=hex_lattice(12,12)
    p=Protocol()
    s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))),protocol=p)
    result=run_simulation(s)
    # Include fallback end-to-end cost as well, so fallback can respect deadlines.
    fallback=run_simulation(s,force_numpy=True)
    data={'calibrated_at':datetime.now(timezone.utc).isoformat(),'host':{'machine':platform.machine(),'platform':platform.platform(),'python':platform.python_version()},'solver_version':result.solver_version,'atom_count':len(q),'lattice':[12,12],'protocol':p.model_dump(exclude={'seed'}), 'complete_run_wall_time_sec':result.wall_time_sec,'numpy_complete_run_wall_time_sec':fallback.wall_time_sec,'target_3_to_12_seconds_achieved':3<=result.wall_time_sec<=12,'target_note':'Faster than target is acceptable; horizon retained at strain 0.65, not shortened for timing.', 'engine':engine_capabilities(),'physical_loading_duration_lj':result.measurement_horizon['lj_time'],'observed_outcome':result.outcome,'nve_drift':result.numerical_check.energy_drift_ratio,'cross_engine_ensemble_comparison':'NOT_RUN; deterministic pair parity tested, ensemble trajectories not assumed equivalent','per_run_timeout_sec':30, 'sample_every':p.sample_every}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2))
    return data


if __name__=='__main__':
    print(json.dumps(calibrate(),indent=2))
