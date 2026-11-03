"""Registered held-out timestep checks; collect all outcomes before privileged scoring."""
import json
from backend.demonstration.registration import registration,PUBLIC_DIR
from backend.demonstration.geometry import reconstruct
from backend.demonstration.validation import validate_study_run
from backend.demonstration.convergence import deterministic_winner
from backend.models.schemas import InterventionType,SimulationSummary
from backend.simulation.worker import run_bounded


def refine(store,records):
    design,_=registration();rule=design['physical_validation'].get('heldout_timestep_refinement')
    if not rule:return {'required':False,'passed':True,'cases':[]}
    cases=[]
    for record in records:
        cid=record['case_id'];state=record['state'];original=store.specimen(cid)
        old_base=SimulationSummary.model_validate(store.public(cid).baseline_simulation.replicate_results[0])
        coarse={p['intervention']:SimulationSummary.model_validate(state['executed_experiments'][p['experiment_id']]['replicate_results'][0]) for p in state['proposed_experiments'] if p['experiment_id'] in state['executed_experiments']}
        inputs={'baseline':original}
        for p in state['proposed_experiments']:
            edited,trace=reconstruct(original,InterventionType(p['intervention']))
            if trace['status']=='APPLIED':inputs[p['intervention']]=edited
        raw={};checks={}
        for name,inp in inputs.items():
            inp=inp.model_copy(deep=True)
            for key in ['dt','warmup_steps','nve_steps','sample_every']:setattr(inp.protocol,key,rule[key])
            inp.protocol.seed=rule['fixed_seed_label']
            result=validate_study_run(inp,run_bounded(inp,timeout=90))
            raw[name]=result
            previous=old_base if name=='baseline' else coarse[name]
            strain_error=abs(previous.failure_strain-result.failure_strain) if previous.failure_strain is not None and result.failure_strain is not None else None
            peak_error=abs(previous.peak_stress-result.peak_stress)/max(abs(previous.peak_stress),1e-12)
            checks[name]={'failure_strain_absolute_error':strain_error,'peak_stress_relative_error':peak_error,'numeric_valid':result.numerical_check.is_valid,'passed':bool(result.numerical_check.is_valid and strain_error is not None and strain_error<=.01 and peak_error<=.05)}
            print('held-out dt refinement',cid,name,result.outcome.value,'strain error',strain_error,'peak error',peak_error,flush=True)
        refined_arms={name:r for name,r in raw.items() if name!='baseline'}
        coarse_winner=deterministic_winner(old_base,coarse);fine_winner=deterministic_winner(raw['baseline'],refined_arms)
        identity=coarse_winner==fine_winner
        case={'case_id':cid,'checks':checks,'coarse_winner':coarse_winner,'refined_winner':fine_winner,'same_mechanism':identity,'passed':all(c['passed'] for c in checks.values()) and identity,'raw':{key:r.model_dump(mode='json') for key,r in raw.items()}}
        cases.append(case)
        (PUBLIC_DIR/'held_out-refinement.json').write_text(json.dumps({'required':True,'passed':all(c['passed'] for c in cases),'cases':cases},separators=(',',':')))
    return {'required':True,'passed':all(c['passed'] for c in cases),'cases':cases}
