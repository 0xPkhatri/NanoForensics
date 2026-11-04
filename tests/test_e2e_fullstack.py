"""Mandatory LIVE HTTP gate: execute via bash scripts/verify_e2e.sh."""
import concurrent.futures
import json
import os
from pathlib import Path
import signal
import sys
import time
import httpx
import psutil
import pytest

pytestmark=[pytest.mark.e2e,pytest.mark.skipif(os.getenv('NANO_E2E_LIVE')!='1',reason='Requires both live servers: run bash scripts/verify_e2e.sh')]
BASE='http://127.0.0.1:8000/api'


@pytest.fixture(scope='module')
def client():
    with httpx.Client(base_url=BASE,timeout=15.) as c:
        yield c


def wait_job(client,job_id,timeout=115):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        response=client.get('/jobs/'+job_id);assert response.status_code==200
        job=response.json()
        if job['status'] not in ['QUEUED','RUNNING']:
            return job
        # Event loop and UI remain responsive under actual CPU work.
        assert client.get('/health').status_code==200
        assert httpx.get('http://127.0.0.1:3000',timeout=10).status_code==200
        time.sleep(.2)
    pytest.fail(f'Job {job_id} did not terminate: {job}')


def alive(pid):
    try:return psutil.Process(pid).is_running() and psutil.Process(pid).status()!=psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:return False


def wait_worker(client,job_id):
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        job=client.get('/jobs/'+job_id).json()
        pid=job.get('pid')
        if pid and alive(pid):
            try:
                descendants=psutil.Process(pid).children(recursive=True)
            except (psutil.NoSuchProcess,psutil.AccessDenied):
                descendants=[]
            actual=[]
            for process in descendants:
                try:
                    if 'backend.simulation.worker' in process.cmdline():actual.append(process)
                except (psutil.NoSuchProcess,psutil.AccessDenied):
                    # macOS can deny KERN_PROCARGS2 during spawn/exit. Poll again;
                    # never count an unobserved process as a simulation worker.
                    continue
            if actual:return pid,[p.pid for p in descendants]
        assert job['status'] in ['QUEUED','RUNNING'],job
        time.sleep(.02)
    pytest.fail('No real simulation subprocess observed')


def test_health_cors_dashboard_and_blind_metadata(client):
    response=client.get('/health');assert response.status_code==200
    health=response.json();assert health['cases_ready'] and health['calibrated_atom_count']==144
    assert health['engine']['engine'] in ['LAMMPS_BINARY','NUMPY_VELOCITY_VERLET_2D']
    assert health['ai_telemetry']['execution_mode']=='OFFLINE_HEURISTIC_FALLBACK'
    assert health['ai_telemetry']['last_error']=='META_MUSE_API_KEY not configured'
    response=client.options('/cases',headers={'Origin':'http://localhost:3000','Access-Control-Request-Method':'GET'})
    assert response.headers['access-control-allow-origin']=='http://localhost:3000'
    cases=client.get('/cases').json()
    assert {c['case_id'] for c in cases}=={'CASE_ALPHA','CASE_BETA','CASE_GAMMA','CASE_DELTA'}
    for c in cases:
        assert c['temperature_lj'] is None and c['reported_strain_rate'] is None
        assert c['nominal_strain_rate']==.05
        assert c['observed_configuration']['atom_ids']==list(range(c['atom_count']))
        for forbidden in ['ground_truth','preparation_protocol','removed_original_site_ids','original_unmodified_lattice_site_ids']:
            assert forbidden not in json.dumps(c)
        assert all(len(r['sim_id'])==24 for r in c['baseline_simulation']['replicate_results'])
    dashboard=httpx.get('http://127.0.0.1:3000')
    assert dashboard.status_code==200 and 'NanoForensics' in dashboard.text
    assert 'Lennard-Jones computational testbed' in dashboard.text
    proxy=httpx.get('http://127.0.0.1:3000/api/health')
    assert proxy.status_code==200 and proxy.json()['cases_ready']
    assert client.get('/cases/INTERIOR_VOID').status_code==404


def test_request_validation_and_admin_guard(client):
    assert client.post('/cases/CASE_ALPHA/experiment',json={'intervention':'run_shell','parameters':{'command':'echo fake'}}).status_code==422
    assert client.post('/cases/CASE_ALPHA/experiment',json={'proposal_id':'unregistered'}).status_code==422
    assert client.post('/cases/CASE_ALPHA/experiment',json={}).status_code==422
    assert client.post('/cases/CASE_ALPHA/auto-investigate',json={'timeout_sec':-1}).status_code==422
    assert client.post('/benchmarks/evaluate').status_code==403


def test_conflict_reset_and_real_worker_cancellation(client):
    assert client.post('/cases/CASE_BETA/reset').status_code==200
    def submit(_):
        return httpx.post(BASE+'/cases/CASE_BETA/auto-investigate',json={'force_recompute':True},timeout=10)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:responses=list(pool.map(submit,range(2)))
    assert sorted(r.status_code for r in responses)==[202,409]
    job_id=next(r.json()['job_id'] for r in responses if r.status_code==202)
    assert client.post('/cases/CASE_BETA/reset').status_code==409
    assert client.post('/cases/CASE_BETA/hypothesize').status_code==409
    pid,children=wait_worker(client,job_id)
    print('Real worker cancellation:',pid,children)
    assert client.post('/jobs/'+job_id+'/cancel').status_code==202
    terminal=wait_job(client,job_id)
    assert terminal['status']=='CANCELLED' and terminal['error']
    assert not alive(pid) and all(not alive(p) for p in children)
    assert not (Path('runtime/job_tmp')/job_id).exists()
    assert not client.get('/cases/CASE_BETA').json()['investigation']['is_running']
    assert client.post('/cases/CASE_BETA/reset').status_code==200


def test_real_job_and_replicate_deadlines(client):
    response=client.post('/cases/CASE_GAMMA/auto-investigate',json={'timeout_sec':.05,'force_recompute':True})
    assert response.status_code==202
    job=wait_job(client,response.json()['job_id'])
    assert job['status']=='TIMED_OUT' and not alive(job['pid'])
    from backend.simulation.worker import run_bounded
    from backend.storage.db import Store
    failed=run_bounded(Store().specimen('CASE_GAMMA'),timeout=.5)
    print('Actual replicate timeout:',failed.error_code,failed.wall_time_sec)
    assert failed.outcome=='EXECUTION_FAILED' and failed.error_code=='RUN_TIMEOUT'
    assert failed.wall_time_sec<5


@pytest.mark.parametrize('case_id',['CASE_ALPHA','CASE_DELTA'])
def test_full_closed_loop_http_investigation_and_sqlite_persistence(client,case_id):
    assert client.post(f'/cases/{case_id}/reset').status_code==200
    response=client.post(f'/cases/{case_id}/auto-investigate',json={'force_recompute':True})
    assert response.status_code==202
    job=wait_job(client,response.json()['job_id'])
    assert job['status']=='COMPLETE',job
    state=client.get('/cases/'+case_id).json()['investigation']
    assert state['status'] in ['CONCLUDED','INCONCLUSIVE'] and not state['is_running']
    assert state['ai_execution_mode']=='OFFLINE_HEURISTIC_FALLBACK'
    assert len(state['hypotheses'])>=2 and state['verifications']
    stages={e['stage'] for e in state['audit_log']}
    assert {'observe','hypothesize','plan','intervention','simulation','verify','belief_revision','conclude'}<=stages
    assert any(e.get('cached') is False for e in state['audit_log'] if e['stage']=='simulation')
    for experiment in state['executed_experiments'].values():
        assert experiment['replicate_seeds']==[42,137,271]
        assert len(experiment['replicate_results'])==3
        assert all(r['initial_configuration_hash'] and r['protocol_hash'] for r in experiment['replicate_results'])
    for v in state['verifications']:
        if v['execution_status']=='EXECUTION_FAILED': assert v['verdict']=='PENDING'
        if any(v['censoring_counts'].values()):assert v['strain_recovery_pct'] is None
    from backend.storage.db import Store
    persisted=Store().state(case_id).model_dump(mode='json')
    assert persisted==state
    print(case_id,state['status'],[(v['intervention'],v['verdict'],v['execution_status']) for v in state['verifications']])


def test_proposal_execution_and_immutable_result_http(client):
    response=client.post('/cases/CASE_BETA/hypothesize');assert response.status_code==202
    assert wait_job(client,response.json()['job_id'])['status']=='COMPLETE'
    state=client.get('/cases/CASE_BETA').json()['investigation']
    proposal=next(p for p in state['proposed_experiments'] if p['intervention']=='smooth_surface_notch')
    response=client.post('/cases/CASE_BETA/experiment',json={'proposal_id':proposal['experiment_id'],'force_recompute':True})
    assert response.status_code==202
    assert wait_job(client,response.json()['job_id'])['status']=='COMPLETE'
    state=client.get('/cases/CASE_BETA').json()['investigation']
    summary=state['executed_experiments'][proposal['experiment_id']]
    raw=summary['replicate_results'][0]
    immutable=client.get('/results/'+raw['sim_id'])
    assert immutable.status_code==200 and immutable.json()['seed']==42
    assert immutable.json()['initial_configuration_hash']==raw['initial_configuration_hash']


def test_server_restart_preserves_durable_state(client):
    from scripts.e2e_servers import stop,start
    directory=Path(os.environ['NANO_E2E_DIR'])
    before=client.get('/cases/CASE_DELTA').json()['investigation']
    stop('api',directory);start('api',directory)
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        try:
            if client.get('/health').status_code==200:break
        except httpx.HTTPError:pass
        time.sleep(.1)
    after=client.get('/cases/CASE_DELTA').json()['investigation']
    assert before==after


def test_server_crash_recovers_orphaned_worker_and_unlocks_case(client):
    from scripts.e2e_servers import start
    directory=Path(os.environ['NANO_E2E_DIR'])
    assert client.post('/cases/CASE_ALPHA/reset').status_code==200
    response=client.post('/cases/CASE_ALPHA/auto-investigate',json={'force_recompute':True})
    job_id=response.json()['job_id']
    worker,children=wait_worker(client,job_id)
    server=int((directory/'api.pid').read_text())
    os.kill(server,signal.SIGKILL)
    deadline=time.monotonic()+10
    while alive(server) and time.monotonic()<deadline:time.sleep(.05)
    start('api',directory)
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        try:
            if client.get('/health').status_code==200:break
        except httpx.HTTPError:pass
        time.sleep(.1)
    job=wait_job(client,job_id)
    assert job['status']=='INTERRUPTED',job
    assert not alive(worker) and all(not alive(pid) for pid in children)
    assert not (Path('runtime/job_tmp')/job_id).exists()
    assert client.post('/cases/CASE_ALPHA/reset').status_code==200
    print('Crash recovery:',job['status'],'worker descendants terminated; durable case lock released')


def test_separate_demonstration_routes_and_real_counterfactual(client):
    """Runs in an isolated copy of the demonstration DB; no published data changes."""
    demo=BASE+'/demonstrations'
    study=httpx.get(demo+'/study',timeout=10)
    assert study.status_code==200 and study.json()['registration_hash']
    evidence=httpx.get('http://127.0.0.1:3000/study-evidence/v3/held_out-evaluation.json',timeout=15)
    assert evidence.status_code==200
    assert evidence.json()['registration_hash']==study.json()['registration_hash']
    report=httpx.get('http://127.0.0.1:3000/study-evidence/v3/STUDY_REPORT.md',timeout=15)
    assert report.status_code==200 and 'NOT_VALIDATED' in report.text
    all_cases=httpx.get(demo+'/cases',timeout=15).json()
    if not all_cases:
        pytest.fail('Generate the registered demonstration before its integration acceptance gate')
    selected=next(c for c in all_cases if c['observed_configuration']['study_partition']=='development' and c['atom_count']<320)
    case_id=selected['case_id']
    assert client.get('/cases/'+case_id).status_code==404
    assert httpx.get(demo+'/cases/CASE_ALPHA').status_code==404
    assert httpx.post(demo+'/cases/'+case_id+'/experiment',json={'intervention':'normalize_strain_rate'}).status_code==422
    response=httpx.post(demo+'/cases/'+case_id+'/hypothesize',timeout=15)
    assert response.status_code==202
    def wait_demo(job_id,limit=240):
        deadline=time.monotonic()+limit
        while time.monotonic()<deadline:
            job=httpx.get(demo+'/jobs/'+job_id,timeout=15).json()
            if job['status'] not in ['QUEUED','RUNNING']:return job
            assert client.get('/health').status_code==200
            time.sleep(.5)
        pytest.fail('Demo job timed out in test')
    assert wait_demo(response.json()['job_id'])['status']=='COMPLETE'
    state=httpx.get(demo+'/cases/'+case_id,timeout=15).json()['investigation']
    proposal=state['proposed_experiments'][0]
    response=httpx.post(demo+'/cases/'+case_id+'/experiment',json={'proposal_id':proposal['experiment_id'],'force_recompute':True},timeout=15)
    assert response.status_code==202
    job_id=response.json()['job_id']
    assert client.get('/jobs/'+job_id).status_code==404
    assert httpx.post(demo+'/cases/'+case_id+'/reset').status_code==409
    assert wait_demo(job_id)['status']=='COMPLETE'
    state=httpx.get(demo+'/cases/'+case_id,timeout=15).json()['investigation']
    result=state['executed_experiments'][proposal['experiment_id']]
    assert result['replicate_seeds']==[5801,5802,5803]
    assert len(result['replicate_results'])==3
    assert any(e.get('cached') is False for e in state['audit_log'] if e['stage']=='simulation')
    assert state['ai_execution_mode']=='OFFLINE_HEURISTIC_FALLBACK'
    proxy=httpx.get('http://127.0.0.1:3000/api/demonstrations/study',timeout=15)
    assert proxy.status_code==200 and proxy.json()['registration_hash']==study.json()['registration_hash']
    print('Separate demonstration real MD:',case_id,len(result['replicate_results']),'fresh counterfactual seeds; original namespace unaffected')


def test_live_muse_workspace_fallback_provenance_and_frozen_study_isolation(client):
    """Real HTTP worker and genuine immutable MD cache; no provider call is faked."""
    base=BASE+'/live-muse';case_id='DEMO_501'
    frozen_before=httpx.get(BASE+'/demonstrations/cases/'+case_id,timeout=15).json()
    assert httpx.get(base+'/study').json()['validation_status']=='NOT_VALIDATED'
    assert httpx.get(base+'/cases/'+case_id).json()['investigation']['status']=='OBSERVING'
    assert httpx.post(base+'/cases/'+case_id+'/experiment',json={'intervention':'normalize_temperature'}).status_code==422
    def wait_live(job_id):
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            job=httpx.get(base+'/jobs/'+job_id,timeout=15).json()
            if job['status'] not in ['QUEUED','RUNNING']:return job
            time.sleep(.2)
        pytest.fail('Live workspace worker did not complete')
    r=httpx.post(base+'/cases/'+case_id+'/hypothesize',timeout=15)
    assert r.status_code==202 and wait_live(r.json()['job_id'])['status']=='COMPLETE'
    state=httpx.get(base+'/cases/'+case_id,timeout=15).json()['investigation']
    assert state['ai_execution_mode']=='OFFLINE_HEURISTIC_FALLBACK'
    assert all(h['ai_execution_mode']=='OFFLINE_HEURISTIC_FALLBACK' for h in state['hypotheses'])
    r=httpx.post(base+'/cases/'+case_id+'/experiment',json={'proposal_id':state['proposed_experiments'][0]['experiment_id'],'force_recompute':False},timeout=15)
    assert r.status_code==202
    job_id=r.json()['job_id'];assert client.get('/jobs/'+job_id).status_code==404
    assert httpx.get(BASE+'/demonstrations/jobs/'+job_id).status_code==404
    assert wait_live(job_id)['status']=='COMPLETE'
    state=httpx.get(base+'/cases/'+case_id,timeout=15).json()['investigation']
    actions=[a['provenance'] for a in state['audit_log'] if a.get('provenance',{}).get('action') in ['hypothesize','plan_experiments','revise_after_evidence']]
    assert {a['action'] for a in actions}=={'hypothesize','plan_experiments','revise_after_evidence'}
    assert all(a['telemetry']['execution_mode']=='OFFLINE_HEURISTIC_FALLBACK' and a['telemetry']['last_error']=='META_MUSE_API_KEY not configured' for a in actions)
    assert len(state['verifications'])==1
    assert httpx.get(BASE+'/demonstrations/cases/'+case_id,timeout=15).json()==frozen_before
    proxy=httpx.get('http://127.0.0.1:3000/api/live-muse/study',timeout=15)
    assert proxy.status_code==200 and proxy.json()['rehearsal']
    dashboard = httpx.get('http://127.0.0.1:3000',timeout=15).text
    assert '<option value="live">AI investigation</option>' in dashboard
    assert '<option value="demonstration">Published study</option>' in dashboard
    print('Live workspace fallback receipts, cached genuine MD and frozen-study isolation verified')
