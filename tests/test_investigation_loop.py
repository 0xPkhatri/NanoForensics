import builtins
import json
from pathlib import Path
import pytest
from backend.storage.db import Store
from backend.agents.investigator import NanoForensicsInvestigator
from backend.agents.muse_agent import verify_llm_connection, decide
from backend.simulation.defect_generator import transform
from backend.models.schemas import InterventionType


@pytest.fixture(scope='module')
def store():
    # Inputs were frozen by explicit generator command before live investigators.
    s=Store()
    assert len(s.case_ids())==4,'Run python -m benchmarks.generate_cases first'
    return s


def deny_truth(monkeypatch):
    original=builtins.open
    original_path=Path.open
    def safe(file,*args,**kwargs):
        assert 'ground_truth' not in str(file),'Privileged file accessed by live investigation'
        return original(file,*args,**kwargs)
    def safe_path(self,*args,**kwargs):
        assert 'ground_truth' not in str(self),'Privileged file accessed by live investigation'
        return original_path(self,*args,**kwargs)
    monkeypatch.setattr(builtins,'open',safe)
    monkeypatch.setattr(Path,'open',safe_path)


@pytest.mark.parametrize('case_id',['CASE_ALPHA','CASE_BETA','CASE_GAMMA','CASE_DELTA'])
def test_full_blind_autonomous_loop(case_id,store,monkeypatch):
    monkeypatch.delenv('META_MUSE_API_KEY',raising=False)
    deny_truth(monkeypatch)
    state=NanoForensicsInvestigator(store).investigate(case_id)
    assert state.status in ['CONCLUDED','INCONCLUSIVE'] and not state.is_running
    assert len(state.hypotheses)>=2 and state.audit_log
    assert state.ai_execution_mode=='OFFLINE_HEURISTIC_FALLBACK'
    assert state.ai_telemetry.last_error=='META_MUSE_API_KEY not configured'
    assert state.budget_used_sec<=1800
    assert any(x['stage']=='simulation' for x in state.audit_log)
    for result in state.executed_experiments.values():
        assert result.replicate_seeds==[42,137,271]
        assert len(result.replicate_results)==3
    for v in state.verifications:
        if not v.numerical_consistency_passed:
            assert v.execution_status=='EXECUTION_FAILED' and v.verdict=='PENDING'
        if v.censoring_counts['baseline'] or v.censoring_counts['counterfactual']:
            assert v.strain_recovery_pct is None
    print(case_id,state.status,'verifications:',[(v.intervention.value,v.verdict.value,v.execution_status,v.strain_recovery_pct) for v in state.verifications])


def test_public_metadata_and_permuted_ids(store,monkeypatch):
    deny_truth(monkeypatch)
    original=store.public('CASE_ALPHA');copy=original.model_copy(deep=True);copy.case_id='CASE_DELTA'
    from backend.agents.hypothesis_engine import fallback_hypotheses
    a=fallback_hypotheses(original);b=fallback_hypotheses(copy)
    assert [h.model_dump() for h in a]==[h.model_dump() for h in b]
    for case in store.case_ids():
        p=store.public(case)
        raw=p.model_dump_json()
        for forbidden in ['preparation_protocol','removed_original_site_ids','original_unmodified_lattice_site_ids','ground_truth','suspected_cause']:
            assert forbidden not in raw
        assert p.temperature_lj is None and p.reported_strain_rate is None
        assert p.observed_configuration['atom_ids']==list(range(p.atom_count))
    spec=store.specimen('CASE_ALPHA')
    a,ta=transform(spec,InterventionType.HEAL_INTERIOR_VACANCY)
    b,tb=transform(spec,InterventionType.HEAL_INTERIOR_VACANCY)
    assert a.model_dump()==b.model_dump() and ta==tb


def test_backend_has_no_privileged_reads():
    for path in Path('backend').rglob('*.py'):
        assert 'ground_truth' not in path.read_text(),path
    import inspect
    from backend.analysis import evidence_verifier
    assert 'case_id' not in inspect.getsource(evidence_verifier)


def test_missing_credentials_and_invalid_model_json(monkeypatch):
    monkeypatch.delenv('META_MUSE_API_KEY',raising=False)
    t=verify_llm_connection()
    assert t.execution_mode=='OFFLINE_HEURISTIC_FALLBACK' and t.last_call_latency_ms is None
    assert t.prompt_tokens is None
    import backend.agents.muse_agent as muse
    monkeypatch.setattr(muse,'_request',lambda *args: ({'tool':'run_shell','command':'echo fabricated'},t))
    decision,telemetry,provenance=decide({'visible':'test'})
    assert decision is None and telemetry.execution_mode=='OFFLINE_HEURISTIC_FALLBACK'


def test_sqlite_frozen_specimen_and_job_uniqueness(store):
    import sqlite3
    from concurrent.futures import ThreadPoolExecutor
    def create(_):
        try: return store.create_job('exclusive-test','test')
        except sqlite3.IntegrityError: return 'CONFLICT'
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids=list(pool.map(create,range(2)))
    assert ids.count('CONFLICT')==1
    job=next(x for x in ids if x!='CONFLICT')
    store.update_job(job,status='COMPLETE')
    reloaded=Store(store.path)
    assert reloaded.job(job)['status']=='COMPLETE'
    with pytest.raises(sqlite3.IntegrityError):
        store.put_specimen(store.public('CASE_ALPHA'),store.specimen('CASE_ALPHA'))


def test_live_provenance_requires_operation_schema_success(monkeypatch,store):
    import backend.agents.muse_agent as muse
    from backend.agents.hypothesis_engine import fallback_hypotheses
    from backend.models.schemas import LLMTelemetry
    t=LLMTelemetry(execution_mode='OFFLINE_HEURISTIC_FALLBACK',configured_model='test-provider',base_url='https://provider.invalid/v1',api_key_present=True,last_call_latency_ms=12,prompt_tokens=123,completion_tokens=40)
    hypotheses=fallback_hypotheses(store.public('CASE_BETA'))[:2]
    payload={'hypotheses':[h.model_dump(mode='json') for h in hypotheses],'ranking':[h.proposed_intervention.value for h in hypotheses],'revision':'Test provider fixture, not a real integration acceptance claim.'}
    monkeypatch.setattr(muse,'_request',lambda *args: (payload,t))
    decision,telemetry,provenance=muse.decide({'geometry':'test'})
    assert telemetry.execution_mode=='LIVE_MUSE_SPARK_API' and decision is not None
    assert provenance['request_hash'] and provenance['response_hash']
    assert decision.hypotheses[0].ai_execution_mode=='LIVE_MUSE_SPARK_API'
    assert telemetry.prompt_tokens==123
    monkeypatch.setattr(muse,'_request',lambda *args: ({'invalid':'json'},t))
    decision,telemetry,provenance=muse.decide({'geometry':'test'},'revise_after_evidence')
    assert decision is None and telemetry.execution_mode=='OFFLINE_HEURISTIC_FALLBACK'


def test_diagnostic_new_seeds_measure_variance_without_claiming_repair(store,monkeypatch):
    monkeypatch.delenv('META_MUSE_API_KEY',raising=False)
    deny_truth(monkeypatch)
    state=NanoForensicsInvestigator(store).investigate('CASE_DELTA',intervention='repeat_replicate_seeds',max_experiments=1)
    result=next(iter(state.executed_experiments.values()))
    assert {101,202,303}<set(result.replicate_seeds)
    assert len(result.replicate_results)==6
    assert len({r['seed'] for r in result.replicate_results})==6
    assert all(v.verdict not in ['SUPPORTED','REJECTED'] for v in state.verifications)
    print('Diagnostic actual seed outcomes:',[(r['seed'],r['outcome'],r['failure_strain']) for r in result.replicate_results])


def test_model_claimed_support_cannot_bypass_empirical_verifier(store,monkeypatch):
    import backend.agents.investigator as module
    from backend.agents.hypothesis_engine import fallback_hypotheses
    from backend.agents.muse_agent import telemetry
    from backend.models.schemas import ModelDecision, HypothesisStatus
    hypotheses=fallback_hypotheses(store.public('CASE_BETA'))
    for h in hypotheses:h.status=HypothesisStatus.SUPPORTED
    decision=ModelDecision(hypotheses=hypotheses,ranking=[h.proposed_intervention for h in hypotheses],revision='Controlled invalid scientific assertion fixture')
    monkeypatch.setattr(module,'decide',lambda *args:(decision,telemetry(),{'test_fixture':True}))
    trial=module.NanoForensicsInvestigator(store)
    state=trial.hypothesize('CASE_BETA')
    assert all(h.status=='PENDING' for h in state.hypotheses)
    state.is_running=False;store.save_state(state)
