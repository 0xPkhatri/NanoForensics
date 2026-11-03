"""Small independent cross-engine ensemble; descriptive, not a forced parity gate."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import t
from backend.config import ROOT,SEEDS
from backend.models.schemas import SpecimenInput
from backend.simulation.defect_generator import hex_lattice
from backend.simulation.lammps_runner import engine_capabilities
from backend.simulation.worker import run_bounded


def describe(values):
    a=np.asarray(values,float);n=len(a)
    if not n:return {'n':0,'mean':None,'mean_ci95':None}
    mean=float(a.mean())
    half=float(t.ppf(.975,n-1)*a.std(ddof=1)/np.sqrt(n)) if n>1 else None
    return {'n':n,'mean':mean,'std':float(a.std(ddof=1)) if n>1 else None,'mean_ci95':[mean-half,mean+half] if half is not None else None,'interval_assumption':'Student-t interval assuming independent approximately normal outcomes; n=3 is not adequately powered'}


def validate(output=None):
    output=Path(output or ROOT/'docs/ENGINE_COMPARISON.json')
    caps=engine_capabilities()
    if caps['engine']!='LAMMPS_BINARY':
        result={'status':'NOT_RUN','reason':'Verified LAMMPS binary unavailable','capabilities':caps}
    else:
        q=hex_lattice(12,12)
        specimen=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
        raw={}
        for mode in ['LAMMPS_BINARY','NUMPY_VELOCITY_VERLET_2D']:
            raw[mode]=[]
            for seed in SEEDS:
                s=specimen.model_copy(deep=True);s.protocol.seed=seed
                raw[mode].append(run_bounded(s,force_numpy=mode.startswith('NUMPY')))
        summaries={}
        for mode,runs in raw.items():
            valid=[r for r in runs if r.numerical_check.is_valid and r.outcome!='EXECUTION_FAILED']
            uncensored=[r for r in valid if r.failure_strain is not None]
            summaries[mode]={'peak_stress':describe([r.peak_stress for r in valid]),'failure_strain':describe([r.failure_strain for r in uncensored]) if len(uncensored)==len(valid) else {'mean':None,'reason':'Censoring prevents a naive failure-strain mean','uncensored_count':len(uncensored)},'fracture_count':sum(r.outcome=='FRACTURED' for r in valid),'censored_count':sum(r.outcome=='NOT_FRACTURED_WITHIN_HORIZON' for r in valid),'failed_count':len(runs)-len(valid),'crack_regions':[r.crack_initiation_region for r in valid]}
        left=summaries['LAMMPS_BINARY']['peak_stress']['mean'];right=summaries['NUMPY_VELOCITY_VERLET_2D']['peak_stress']['mean']
        shift=100*(left-right)/right if left is not None and right else None
        valid_pairs=[(a,b) for a,b in zip(raw['LAMMPS_BINARY'],raw['NUMPY_VELOCITY_VERLET_2D']) if a.numerical_check.is_valid and b.numerical_check.is_valid]
        agreement=sum(a.crack_initiation_region==b.crack_initiation_region for a,b in valid_pairs)/len(valid_pairs) if valid_pairs else None
        result={'status':'DESCRIPTIVE_LOW_SAMPLE','solver_version':'sflj-1.1','seeds':SEEDS,'input_protocol':specimen.protocol.model_dump(exclude={'seed'}),'configuration_hash':raw['LAMMPS_BINARY'][0].initial_configuration_hash,'matching':'Identical epsilon=sigma=mass=1, cutoff=2.5, 2D free-x/gripped-y, shared minimization/warmup/NVE, dt, engineering strain-rate/time and sampling; loading Langevin splittings/PRNGs differ. Seed equality does not imply trajectory identity.','native_two_body_pair_validation':caps,'distributions':summaries,'peak_stress_mean_relative_difference_pct':shift,'target_15pct_observed_for_peak_mean':abs(shift)<=15 if shift is not None else None,'target_note':'15% is a target, not an acceptance assertion for n=3. No population equivalence or synthetic agreement claimed.','descriptive_crack_region_agreement_fraction':agreement,'raw':{mode:[r.model_dump(mode='json') for r in runs] for mode,runs in raw.items()}}
    output.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='raw'},indent=2))
    return result


if __name__=='__main__':validate()
