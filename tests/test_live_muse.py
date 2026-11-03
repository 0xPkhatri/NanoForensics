"""Contract/failure tests use labeled provider fixtures; live acceptance is separate."""
import json
import pytest
import httpx
from pydantic import ValidationError
from backend.agents import muse_agent
from backend.live_muse.contracts import Hypotheses,Planning,Revision
from backend.live_muse.storage import initialize
from backend.demonstration.storage import DemonstrationStore


@pytest.fixture
def store(tmp_path):
    s=DemonstrationStore(tmp_path/'rehearsal.db');initialize(s)
    return s


def mechanisms():
    return {'hypotheses':[{'intervention':i,'title':'Provider contract fixture','mechanism':'Competing geometric mechanism requiring experiments.','evidence':['Observable topology, not labels.'],'missing_evidence':'Counterfactual MD','predicted_recovery_pct':20,'confidence':.4} for i in ['heal_interior_vacancy','smooth_surface_notch']]}


@pytest.mark.parametrize('finish,content,model,error',[
 ('length',None,'muse-spark-1.3','incomplete'),
 ('stop','{"ok":true}','different-model','different'),
 ('stop','not JSON','muse-spark-1.3','JSONDecodeError')])
def test_transport_rejects_incomplete_wrong_model_or_invalid_json(monkeypatch,finish,content,model,error):
    monkeypatch.setenv('META_MUSE_API_KEY','unit-test-not-a-real-key');monkeypatch.setenv('META_MUSE_BASE_URL','https://api.meta.ai/v1');monkeypatch.setenv('META_MUSE_MODEL','muse-spark-1.3')
    body={'model':model,'id':'fixture-response','choices':[{'finish_reason':finish,'message':{'content':content}}],'usage':{'prompt_tokens':17,'completion_tokens':128}}
    monkeypatch.setattr(muse_agent.httpx,'post',lambda *a,**kw:httpx.Response(200,json=body,request=httpx.Request('POST','https://api.meta.ai/v1/chat/completions')))
    parsed,t=muse_agent._request([],256)
    assert parsed is None and t.execution_mode==muse_agent.FALLBACK and error in t.last_error
    assert t.prompt_tokens==17 and t.completion_tokens==128 and t.response_id=='fixture-response'


def test_action_contracts_reject_duplicates_and_unregistered_parameters():
    payload=mechanisms();payload['hypotheses'][1]['intervention']=payload['hypotheses'][0]['intervention']
    with pytest.raises(ValidationError):Hypotheses.model_validate(payload)
    payload=mechanisms();payload['protocol']={'temperature':.01}
    with pytest.raises(ValidationError):Hypotheses.model_validate(payload)


def test_invalid_revision_evidence_falls_back_despite_schema_success(monkeypatch):
    from backend.live_muse.inference import infer
    import backend.live_muse.inference as inference
    payload={'beliefs':[{'intervention':i,'confidence':.9,'predicted_recovery_pct':20,'explanation':'Provider fixture citing unavailable evidence','evidence_ids':['invented']} for i in ['heal_interior_vacancy','smooth_surface_notch']],'revision':'Fixture only'}
    monkeypatch.setattr(inference,'_request',lambda *a,**kw:(payload,muse_agent.telemetry()))
    def validate(r):
        if any(set(b.evidence_ids)-{'actual-result'} for b in r.beliefs):raise ValueError('Unavailable evidence')
    result,t,receipt=infer('revise_after_evidence',{},Revision,validate)
    assert result is None and t.execution_mode==muse_agent.FALLBACK and len(receipt['attempts'])==2
    assert receipt['request_hash']==muse_agent.digest(receipt['request_messages'])
    assert receipt['attempts'][0]['request_hash']!=receipt['attempts'][1]['request_hash']


def test_live_overlay_uses_real_cached_md_and_model_cannot_change_verdicts(store,monkeypatch):
    import backend.live_muse.investigator as module
    def fixture_infer(action,visible,contract,validate=None):
        if contract is Hypotheses:payload=mechanisms()
        elif contract is Planning:payload={'choices':[{'intervention':i,'information_gain':.8,'risk':.1,'rationale':'Provider fixture ranking two registered physical tools.'} for i in ['heal_interior_vacancy','smooth_surface_notch']]}
        else:
            ids=[x['experiment_id'] for x in visible['completed_evidence']]
            payload={'beliefs':[{'intervention':i,'confidence':.01,'predicted_recovery_pct':-5,'explanation':'Fixture deliberately pessimistic about both mechanisms; verifier remains authoritative.','evidence_ids':ids} for i in ['heal_interior_vacancy','smooth_surface_notch']],'revision':'Provider fixture only, not real integration evidence.'}
        result=contract.model_validate(payload)
        if validate:validate(result)
        t=muse_agent.telemetry();t.execution_mode=muse_agent.LIVE
        return result,t,{'action':action,'telemetry':t.model_dump(mode='json'),'fixture':True}
    monkeypatch.setattr(module,'infer',fixture_infer)
    import backend.demonstration.investigator as physics
    def forbidden(*a,**kw):raise AssertionError('Real frozen MD cache required in this unit test')
    monkeypatch.setattr(physics,'run_bounded',forbidden)
    before=store.public('DEMO_501').model_dump_json()
    state=module.LiveMuseInvestigator(store).investigate('DEMO_501',max_experiments=2,force_recompute=False)
    assert len(state.verifications)==2 and state.status=='CONCLUDED'
    assert state.identified_cause=='interior_vacancy'
    assert all(h.confidence==.01 for h in state.hypotheses)
    assert {h.status.value for h in state.hypotheses}=={'SUPPORTED','REJECTED'}
    assert all(a['cached'] for a in state.audit_log if a['stage']=='simulation')
    assert store.public('DEMO_501').model_dump_json()==before


def test_live_failure_is_visible_and_observations_exclude_published_decisions(store,monkeypatch):
    from backend.live_muse.investigator import LiveMuseInvestigator
    monkeypatch.setenv('META_MUSE_API_KEY','')
    trial=LiveMuseInvestigator(store);state=trial.hypothesize('DEMO_501')
    assert state.ai_execution_mode==muse_agent.FALLBACK
    assert all(h.ai_execution_mode==muse_agent.FALLBACK for h in state.hypotheses)
    assert all(p.ai_execution_mode==muse_agent.FALLBACK for p in state.proposed_experiments)
    visible=trial.observations('DEMO_501');text=json.dumps(visible)
    edge=next(c for c in visible['observed_missing_components'] if c['boundary_connected'])
    assert edge['measured_side']=='surface_left' and edge['relative_x_in_specimen']<.2
    for forbidden in ['identified_cause','verification','ground_truth','removed_original_site_ids','held_out_evaluation']:
        assert forbidden not in text
    assert state.ai_telemetry.last_error=='META_MUSE_API_KEY not configured'
    state.is_running=False;store.save_state(state)


def test_revision_request_schema_limits_citations_to_actual_completed_ids(monkeypatch):
    import backend.live_muse.inference as inference
    captured=[]
    def request(messages,max_tokens,schema=None):
        captured.append(schema)
        return None,muse_agent.telemetry()
    monkeypatch.setattr(inference,'_request',request)
    result,t,receipt=inference.infer('revise_after_evidence',{'completed_evidence':[{'experiment_id':'actual-completed-result'}]},Revision)
    assert result is None
    assert captured[0]['$defs']['Belief']['properties']['evidence_ids']['items']['enum']==['actual-completed-result']
    assert receipt['attempts'][0]['parsed_json'] is None
