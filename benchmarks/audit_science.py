"""Post-benchmark sensitivity audit. Frozen records are read-only; no privileged labels."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from backend.config import ROOT
from backend.models.schemas import SpecimenInput,InterventionType,SimulationSummary
from backend.storage.db import Store
from backend.simulation.defect_generator import transform
from backend.simulation.worker import run_bounded
from backend.simulation.numpy_md_fallback import content_hash
from backend.analysis.comparison import paired_statistics

ROOT_OUTPUT=ROOT/'runtime/science-audit'
PRIMARY=[42,137,271]
EXPANDED=PRIMARY+[101,202,303,404,505,606]


def measured_run(specimen, label, root, numpy=False):
    key=content_hash({'specimen':specimen.model_dump(),'numpy':numpy,'audit':'kinematic-1'})
    path=root/'runs'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():result=SimulationSummary.model_validate_json(path.read_text())
    else:
        result=run_bounded(specimen,force_numpy=numpy)
        path.write_text(result.model_dump_json())
    return result


def metrics(result):
    d=result.diagnostics;t=d.get('thermal_diagnostics',{}).get('means',{})
    curve=result.stress_strain_curve
    stress=np.asarray([x['stress'] for x in curve]);traction=np.asarray(d.get('grip_reaction_traction',[]))
    region=(np.asarray([x['strain'] for x in curve])>.02)&(np.asarray([x['strain'] for x in curve])<.1)
    traction_error=float(np.mean(abs(stress[region]-traction[region]))/max(np.mean(abs(traction[region])),1e-9)) if region.any() and len(traction)==len(stress) else None
    return {'sim_id':result.sim_id,'seed':result.seed,'outcome':result.outcome.value,'peak_stress':result.peak_stress,'failure_strain':result.failure_strain,'crack_region':result.crack_initiation_region,'nve_drift':result.numerical_check.energy_drift_ratio,'temperature_error':result.numerical_check.thermostat_temperature_error_ratio,'max_force':result.numerical_check.max_force_norm,'max_displacement':result.numerical_check.max_step_displacement,'thermal_means':t,'early_traction_relative_error':traction_error,'wall_time_sec':result.wall_time_sec}


def conditions(specimen):
    # Every specimen receives the same predeclared controls. No case-specific solver logic.
    return [('original',{},None),('refined_dt',{'dt':specimen.protocol.dt/2,'warmup_steps':specimen.protocol.warmup_steps*2,'nve_steps':specimen.protocol.nve_steps*2,'sample_every':specimen.protocol.sample_every*2},None),('higher_damping',{'gamma':8.},None),('fine_sampling',{'sample_every':5},None),('normalized_rate',{'strain_rate':.05},None)]


def audit(root=ROOT_OUTPUT, phase='controls'):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    # SQLite URI mode=ro prevents accidental frozen input writes through this workflow.
    store=Store(ROOT/'runtime/science-audit/original.db')
    report=[]
    for case_id in store.case_ids():
        original=store.specimen(case_id)
        selected=conditions(original) if phase=='controls' else [('repair',{},InterventionType.HEAL_INTERIOR_VACANCY),('repair',{},InterventionType.SMOOTH_SURFACE_NOTCH)]
        for name,changes,edit in selected:
            s=original.model_copy(deep=True)
            trace=None
            if edit:
                s,trace=transform(s,edit)
                if trace['status']!='APPLIED':continue
            for key,value in changes.items():setattr(s.protocol,key,value)
            runs=[]
            seeds=PRIMARY if phase=='controls' else EXPANDED
            for seed in seeds:
                s.protocol.seed=seed
                result=measured_run(s,name,root)
                runs.append(result)
                print(case_id,name,seed,result.outcome.value,result.failure_strain,flush=True)
            row={'case_id':case_id,'condition':name,'changes':changes,'intervention':edit.value if edit else None,'edit_trace':trace,'runs':[metrics(r) for r in runs]}
            if phase=='repairs':
                baselines=[]
                for seed in seeds:
                    b=original.model_copy(deep=True);b.protocol.seed=seed
                    baselines.append(measured_run(b,'original',root))
                row['baseline_runs']=[metrics(r) for r in baselines]
                row['paired_statistics']=paired_statistics(baselines,runs)
                # Canonical ordering is a stochastic-sensitivity control, not an alternative repair.
                canonical=s.model_copy(deep=True)
                order=np.lexsort((np.array(canonical.coordinates)[:,0],np.array(canonical.coordinates)[:,1]))
                canonical.coordinates=np.asarray(canonical.coordinates)[order].tolist()
                canonical.atom_ids=list(range(len(order)))
                reordered=[]
                for seed in PRIMARY:
                    canonical.protocol.seed=seed
                    reordered.append(measured_run(canonical,'ordering_control',root))
                row['ordering_control']=[metrics(r) for r in reordered]
            report.append(row)
            (root/f'{phase}.json').write_text(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['controls','repairs'],default='controls');args=parser.parse_args()
    audit(phase=args.phase)
