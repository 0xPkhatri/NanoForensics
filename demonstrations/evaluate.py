"""Freeze blind decisions before separate privileged scoring; no investigator label access."""
import argparse
import json
import time
from pathlib import Path
from backend.config import ROOT
from backend.storage.db import Store
from backend.demonstration.registration import registration,STUDY_DB,STATUS_PATH
from backend.demonstration.investigator import DemonstrationInvestigator


def evaluate(partition):
    design,digest=registration();store=Store(STUDY_DB)
    out=ROOT/'docs/demonstration';out.mkdir(parents=True,exist_ok=True)
    cases=design[partition]['case_ids'];records=[]
    decision_file=out/f'{partition}-decisions.json'
    if decision_file.exists():raise RuntimeError('Existing fixed decision transcript; refuse to rerun or overwrite')
    for case_id in cases:
        started=time.perf_counter()
        state=DemonstrationInvestigator(store).investigate(case_id,max_experiments=2)
        records.append({'case_id':case_id,'wall_time_sec':time.perf_counter()-started,'state':state.model_dump(mode='json')})
        print(partition,case_id,state.status,[(v.intervention.value,v.verdict.value,v.execution_status) for v in state.verifications],flush=True)
    # Immutable prediction/evidence transcript is fixed before the scorer opens private labels.
    decision_file.write_text(json.dumps(records,indent=2))
    truth=json.loads((ROOT/'runtime/demonstration/private'/partition/'ground_truth.json').read_text())
    rows=[];valid=True
    for record in records:
        state=record['state'];expected=truth[record['case_id']]['cause']
        observed=state['identified_cause']
        numerics=all(r['numerical_check']['is_valid'] and r['failure_strain'] is not None for r in store.public(record['case_id']).baseline_simulation.replicate_results)
        for result in state['executed_experiments'].values():numerics&=all(r['numerical_check']['is_valid'] and r['failure_strain'] is not None for r in result['replicate_results'])
        success=numerics and (observed==expected if expected is not None else observed is None and not any(h['status']=='SUPPORTED' for h in state['hypotheses']))
        valid&=success
        rows.append({'case_id':record['case_id'],'numeric_complete_uncensored':bool(numerics),'identified_cause':observed,'scientific_state':state['status'],'scoring':'CORRECT_DISTINCTION' if success and expected is not None else 'CORRECT_NEGATIVE_CONTROL' if success else 'NO_DECISION' if observed is None else 'INCORRECT','passed':bool(success)})
    result={'partition':partition,'registration_hash':digest,'validation_status':'DEVELOPMENT_CRITERIA_MET' if valid and partition=='development' else 'HELD_OUT_VALIDATED' if valid else 'NOT_VALIDATED','rows':rows,'limitations':design['scope'],'all_outcomes_disclosed':True}
    (out/f'{partition}-evaluation.json').write_text(json.dumps(result,indent=2))
    public_status={'validation_status':result['validation_status'],'partition_evaluated':partition,'registration_hash':digest,'development_result':json.loads((out/'development-evaluation.json').read_text())['validation_status'] if (out/'development-evaluation.json').exists() else None,'case_count':len(store.case_ids()),'counts':{label:sum(r['scoring']==label for r in rows) for label in ['CORRECT_DISTINCTION','CORRECT_NEGATIVE_CONTROL','NO_DECISION','INCORRECT']},'limitations':design['scope']}
    STATUS_PATH.write_text(json.dumps(public_status,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--partition',choices=['development','held_out'],required=True);args=parser.parse_args()
    print(json.dumps(evaluate(args.partition),indent=2))
