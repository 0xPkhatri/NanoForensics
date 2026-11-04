"""Console telemetry invariants. Cached MD below is genuine published evidence."""
import json
import pytest
from backend.api.progress import activity, emit
from backend.api.progress_observer import observed_class
from backend.api.jobs import JobManager
from backend.demonstration.storage import DemonstrationStore
from backend.live_muse.storage import initialize
from backend.live_muse.investigator import LiveMuseInvestigator
from backend.models.schemas import InvestigationState
from backend.agents.muse_agent import telemetry


@pytest.fixture
def store(tmp_path):
    result = DemonstrationStore(tmp_path/'console.db')
    initialize(result)
    return result


def test_job_events_are_durable_and_latest_job_does_not_reuse_old_history(store):
    first = store.create_job('DEMO_501','hypothesize')
    emit(store,first,'hypotheses','started','Request started')
    store.update_job(first,status='COMPLETE')
    old = activity(store,'DEMO_501')
    assert old.job.id == first and old.events[0].status == 'started'
    assert old.events[0].phase == 'hypotheses'  # No synthetic completion from job status.
    reopened = DemonstrationStore(store.path)
    assert activity(reopened,'DEMO_501') == old
    second = store.create_job('DEMO_501','experiment')
    current = activity(store,'DEMO_501')
    assert current.job.id == second and not current.events
    assert activity(store,'DEMO_501',first).job.id == first
    assert activity(store,'DEMO_502',first).job is None
    assert activity(store,'DEMO_502').job is None


def test_cached_real_md_has_started_events_and_true_source_without_science_changes(store,monkeypatch):
    monkeypatch.setenv('META_MUSE_API_KEY','')
    original = LiveMuseInvestigator(store).investigate('DEMO_501',max_experiments=2,force_recompute=False)
    verdicts = [(v.intervention,v.verdict,v.strain_recovery_pct) for v in original.verifications]
    baseline = store.public('DEMO_501').model_dump_json()
    job_id = store.create_job('DEMO_501','investigate')
    before = store.state('DEMO_501').audit_log
    assert all('console' not in event for event in before)
    observed = observed_class(LiveMuseInvestigator,job_id,live=True)(store)
    result = observed.investigate('DEMO_501',max_experiments=2,force_recompute=False)
    events = activity(store,'DEMO_501').events
    assert [(v.intervention,v.verdict,v.strain_recovery_pct) for v in result.verifications] == verdicts
    assert store.public('DEMO_501').model_dump_json() == baseline
    runs = [event for event in events if event.phase=='simulate' and 'cached' in event.data]
    assert len(runs)==12 and all(event.data['cached'] is True for event in runs)
    assert all(event.data['engine_used'] for event in runs)
    assert all(event.data['protocol_hash'] for event in runs)
    for run in runs:
        assert any(previous.seq < run.seq and previous.phase=='simulate' and previous.status=='started'
                   and previous.data.get('experiment_id')==run.data['experiment_id']
                   and previous.data.get('role')==run.data['role']
                   and previous.data.get('replicate_index')==run.data['replicate_index'] for previous in events)
    hypotheses = [event for event in events if event.phase=='hypotheses' and event.status=='completed']
    assert len(hypotheses)==1
    assert hypotheses[0].data['receipt']['telemetry']['execution_mode']=='OFFLINE_HEURISTIC_FALLBACK'
    revisions = [event for event in events if event.phase=='revise' and event.status=='completed']
    assert len(revisions)==2 and all(event.data['belief_changes'] for event in revisions)
    verify = [event for event in events if event.phase=='verify' and event.status=='completed']
    assert len(verify)==2 and all('verification' in event.data for event in verify)
    assert not any(event.phase=='complete' for event in events)  # Only supervisor confirms completion.
    for forbidden in ['ground_truth','removed_original_site_ids','original_unmodified_lattice_site_ids','request_messages','Authorization']:
        assert forbidden not in json.dumps([event.model_dump(mode='json') for event in events])
    assert not any(event.get('stage')=='console' for event in result.audit_log)


def test_cancel_before_launch_clears_state_and_records_confirmed_terminal_job(store):
    state=InvestigationState(case_id='DEMO_501',status='OBSERVING',is_running=True,ai_telemetry=telemetry())
    job_id=store.create_job('DEMO_501','investigate',initial_state=state)
    store.update_job(job_id,cancel=1)
    manager=JobManager(store,worker_module='backend.live_muse.job_worker')
    assert manager._claim() is None
    result=activity(store,'DEMO_501')
    assert result.job.status=='CANCELLED' and not store.state('DEMO_501').is_running
    assert result.events[-1].phase=='complete' and result.events[-1].status=='failed'
    assert not manager.children


def test_terminal_failure_does_not_claim_scientific_completion(store):
    job_id=store.create_job('DEMO_501','investigate')
    emit(store,job_id,'simulate','started','Run is pending')
    manager=JobManager(store)
    manager._finish(job_id,'TIMED_OUT','Deadline reached')
    result=activity(store,'DEMO_501')
    assert result.job.status=='TIMED_OUT'
    assert not any(event.phase=='simulate' and event.status=='completed' for event in result.events)
    assert result.events[-1].data['execution_status']=='TIMED_OUT'
