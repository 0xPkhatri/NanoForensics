import sys
from backend.storage.db import Store
from backend.agents.investigator import NanoForensicsInvestigator


def run(store,job_id):
    job=store.job(job_id); payload=job['payload']
    investigator=NanoForensicsInvestigator(store)
    if job['kind']=='hypothesize':
        state=investigator.hypothesize(job['case_id']);state.is_running=False;store.save_state(state)
    elif job['kind']=='evaluate':
        import subprocess
        from backend.config import ROOT
        # Privileged scoring is a separate executable; never passed to investigator tools.
        result=subprocess.run([sys.executable,'-m','benchmarks.evaluate','--db',str(store.path.resolve())],cwd=ROOT,capture_output=True,text=True,timeout=1700)
        if result.returncode: raise RuntimeError('Benchmark scorer failed; inspect CLI report')
        store.update_job(job_id,result={'report':'docs/BENCHMARK_REPORT.md','message':'Separate scorer completed; ground-truth data are not API payloads.'})
        return
    else:
        state=investigator.investigate(job['case_id'],only_proposal=payload.get('proposal_id'),intervention=payload.get('intervention'),parameters=payload.get('parameters'),max_experiments=payload.get('max_experiments',4))
    store.update_job(job_id,result={'case_id':state.case_id,'status':state.status,'ai_execution_mode':state.ai_execution_mode,'verifications':len(state.verifications),'budget_used_sec':state.budget_used_sec})


if __name__=='__main__':
    store=Store(sys.argv[1])
    try:
        run(store,sys.argv[2])
    except Exception as exc:
        store.update_job(sys.argv[2],error=f'{type(exc).__name__}: {str(exc)[:2000]}')
        raise
