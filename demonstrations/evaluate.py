"""Freeze blind decisions before separate privileged scoring; no investigator label access."""
import argparse
import json
import time
from pathlib import Path
from backend.config import ROOT
from backend.demonstration.storage import DemonstrationStore as Store
from backend.demonstration.registration import registration,STUDY_DB,STATUS_PATH,STUDY_DIR,PUBLIC_DIR
from backend.demonstration.investigator import DemonstrationInvestigator


def evaluate(partition,correct_development=False):
    design,digest=registration();store=Store(STUDY_DB)
    store.retain_frozen_baselines()
    if partition=='held_out':
        from demonstrations.lock_development import verify_lock
        verify_lock()
    out=PUBLIC_DIR;out.mkdir(parents=True,exist_ok=True)
    cases=design[partition]['case_ids'];records=[]
    initial_file=out/f'{partition}-decisions.json'
    decision_file=out/'development-decisions-corrected.json' if correct_development else initial_file
    if decision_file.exists():raise RuntimeError('Existing fixed decision transcript; refuse to rerun or overwrite')
    initial=json.loads(initial_file.read_text()) if correct_development else None
    if correct_development and partition!='development':raise RuntimeError('No retrospective held-out correction allowed')
    if correct_development:
        evaluation=out/'development-evaluation.json'
        backup=out/'development-evaluation.initial.json'
        if not backup.exists():backup.write_bytes(evaluation.read_bytes())
    for case_id in cases:
        started=time.perf_counter()
        if correct_development:
            from backend.models.schemas import InvestigationState
            scientist=DemonstrationInvestigator(store)
            scientist.state=InvestigationState.model_validate(next(r['state'] for r in initial if r['case_id']==case_id))
            state=scientist.generate_report(case_id)
        else:state=DemonstrationInvestigator(store).investigate(case_id,max_experiments=2)
        records.append({'case_id':case_id,'wall_time_sec':time.perf_counter()-started,'state':state.model_dump(mode='json')})
        print(partition,case_id,state.status,[(v.intervention.value,v.verdict.value,v.execution_status) for v in state.verifications],flush=True)
    # Immutable prediction/evidence transcript is fixed before the scorer opens private labels.
    decision_file.write_text(json.dumps(records,separators=(',',':')))
    refinement={'required':False,'passed':True,'cases':[]}
    if partition=='held_out':
        from demonstrations.refinement import refine
        refinement=refine(store,records)
    truth=json.loads((STUDY_DIR/'private'/partition/'ground_truth.json').read_text())
    rows=[];valid=True
    for record in records:
        state=record['state'];expected=truth[record['case_id']]['cause']
        observed=state['identified_cause']
        numerics=all(r['numerical_check']['is_valid'] and r['failure_strain'] is not None for r in store.public(record['case_id']).baseline_simulation.replicate_results)
        for result in state['executed_experiments'].values():numerics&=all(r['numerical_check']['is_valid'] and r['failure_strain'] is not None for r in result['replicate_results'])
        replay=True
        if design['scientific_validation'].get('exact_replay_required'):
            from backend.demonstration.analysis import exact_replays
            from backend.models.schemas import SimulationSummary
            groups=[[SimulationSummary.model_validate(r) for r in store.public(record['case_id']).baseline_simulation.replicate_results]]+[[SimulationSummary.model_validate(r) for r in summary['replicate_results']] for summary in state['executed_experiments'].values()]
            replay=all(exact_replays(group) for group in groups)
        converged=not refinement['required'] or next(c for c in refinement['cases'] if c['case_id']==record['case_id'])['passed']
        success=numerics and replay and converged and (observed==expected if expected is not None else observed is None and not any(h['status']=='SUPPORTED' for h in state['hypotheses']))
        valid&=success
        rows.append({'case_id':record['case_id'],'numeric_complete_uncensored':bool(numerics),'exact_replays':replay,'timestep_convergence':converged if refinement['required'] else None,'convergence_status':('PASS' if converged else 'FAIL') if refinement['required'] else 'NOT_RUN_DEVELOPMENT','identified_cause':observed,'scientific_state':state['status'],'scoring':'CORRECT_DISTINCTION' if success and expected is not None else 'CORRECT_NEGATIVE_CONTROL' if success else 'NO_DECISION' if observed is None else 'INCORRECT','passed':bool(success)})
    result={'partition':partition,'registration_hash':digest,'validation_status':'DEVELOPMENT_CRITERIA_MET' if valid and partition=='development' else 'HELD_OUT_VALIDATED' if valid else 'NOT_VALIDATED','rows':rows,'limitations':design['scope'],'all_outcomes_disclosed':True}
    (out/f'{partition}-evaluation.json').write_text(json.dumps(result,indent=2))
    public_status={'validation_status':result['validation_status'],'partition_evaluated':partition,'registration_hash':digest,'development_result':json.loads((out/'development-evaluation.json').read_text())['validation_status'] if (out/'development-evaluation.json').exists() else None,'case_count':len(store.case_ids()),'counts':{label:sum(r['scoring']==label for r in rows) for label in ['CORRECT_DISTINCTION','CORRECT_NEGATIVE_CONTROL','NO_DECISION','INCORRECT']},'limitations':design['scope']}
    STATUS_PATH.write_text(json.dumps(public_status,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--partition',choices=['development','held_out'],required=True);parser.add_argument('--correct-development-implementation',action='store_true');args=parser.parse_args()
    print(json.dumps(evaluate(args.partition,args.correct_development_implementation),indent=2))
