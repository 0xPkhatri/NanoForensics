"""Real-provider acceptance, not a mocked test or a new scientific benchmark."""
import argparse
import json
from pathlib import Path
from backend.config import ROOT
from backend.agents.muse_agent import verify_llm_connection,LIVE
from backend.demonstration.storage import DemonstrationStore
from backend.live_muse.storage import initialize,LIVE_DB
from backend.live_muse.investigator import LiveMuseInvestigator


def verify(case_id='DEMO_501',fresh=True):
    directory=ROOT/'runtime/live-muse';directory.mkdir(parents=True,exist_ok=True)
    probe=verify_llm_connection()
    (directory/'probe.json').write_text(probe.model_dump_json(indent=2))
    if probe.execution_mode!=LIVE:raise RuntimeError(probe.last_error)
    store=DemonstrationStore(LIVE_DB);initialize(store)
    scientist=LiveMuseInvestigator(store)
    state=scientist.investigate(case_id,max_experiments=2,force_recompute=fresh)
    (directory/'acceptance-state.json').write_text(state.model_dump_json(indent=2))
    actions=[a for a in state.audit_log if a.get('provenance',{}).get('action') in ['hypothesize','plan_experiments','revise_after_evidence']]
    required=['hypothesize','plan_experiments','revise_after_evidence']
    complete=all(any(a['provenance']['action']==name and a.get('ai_execution_mode')==LIVE for a in actions) for name in required)
    all_live=bool(actions) and all(a.get('ai_execution_mode')==LIVE for a in actions)
    revisions=[a for a in actions if a['provenance']['action']=='revise_after_evidence']
    summary={'integration_status':'VERIFIED_LIVE' if complete and all_live and len(state.verifications)==2 else 'NOT_VERIFIED',
        'case_id':case_id,'full_study_validation_status':'NOT_VALIDATED','post_study_rehearsal':True,
        'physics_mode':'FRESH_COUNTERFACTUAL_MD' if fresh else 'EXPLICIT_IMMUTABLE_MD_CACHE_REUSE',
        'probe':probe.model_dump(mode='json',exclude_none=True),
        'actions':[{'action':a['provenance']['action'],'timestamp':a['timestamp'],'ai_execution_mode':a.get('ai_execution_mode'),
            'request_hash':a['provenance'].get('request_hash'),'response_hash':a['provenance'].get('response_hash'),
            'telemetry':a['provenance']['telemetry'],'belief_changes':a['provenance'].get('belief_changes')} for a in actions],
        'revision_count':len(revisions),'verification_count':len(state.verifications),'scientific_state':state.status,
        'identified_larger_effect':state.identified_cause,'budget_used_sec':state.budget_used_sec,
        'limitations':'Post-study rehearsal on a known published case. No new blinded discovery, full-study validation, thermal robustness or calibrated confidence is established.'}
    (directory/'acceptance-summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    if summary['integration_status']!='VERIFIED_LIVE':raise RuntimeError('One or more required real-provider operations failed')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',default='DEMO_501');parser.add_argument('--reuse-md',action='store_true');args=parser.parse_args()
    verify(args.case,not args.reuse_md)
