import sys
from backend.demonstration.storage import DemonstrationStore
from backend.live_muse.investigator import LiveMuseInvestigator


def run(store,job_id):
    job=store.job(job_id);payload=job['payload'];scientist=LiveMuseInvestigator(store)
    if job['kind']=='hypothesize':
        state=scientist.hypothesize(job['case_id']);state.is_running=False;store.save_state(state)
    else:
        state=scientist.investigate(job['case_id'],only_proposal=payload.get('proposal_id'),intervention=payload.get('intervention'),parameters=payload.get('parameters'),max_experiments=min(payload.get('max_experiments',2),2),force_recompute=payload.get('force_recompute',True))
    store.update_job(job_id,result={'case_id':state.case_id,'status':state.status,'ai_execution_mode':state.ai_execution_mode,'verifications':len(state.verifications),'budget_used_sec':state.budget_used_sec})


if __name__=='__main__':
    store=DemonstrationStore(sys.argv[1])
    try:run(store,sys.argv[2])
    except Exception as exc:
        store.update_job(sys.argv[2],error=type(exc).__name__)
        raise
