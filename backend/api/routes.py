import os
import secrets
import sqlite3
import threading
import time
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Request, Header
from backend.models.schemas import ExperimentRequest, InvestigationRequest, InvestigationState
from backend.agents.muse_agent import telemetry
from backend.config import BUDGET
from backend.api.progress import ConsoleResponse, activity, emit

router=APIRouter(prefix='/api')
locks=defaultdict(threading.RLock)
last_evaluation=0.


def store(request): return getattr(request.state,'dataset_store',request.app.state.store)


def known(request,case_id):
    if case_id not in store(request).case_ids(): raise HTTPException(404,'Unknown opaque case id')


def enqueue(request,case_id,kind,payload=None):
    if getattr(request.state,'is_demonstration',False):
        payload=dict(payload or {})
        payload['timeout_sec']=min(payload.get('timeout_sec') or 900,900)
    with locks[case_id]:
        state=None
        if kind!='evaluate':
            state=store(request).state(case_id) or InvestigationState(case_id=case_id,status='OBSERVING',ai_telemetry=telemetry(),budget_total_sec=BUDGET)
            state.is_running=True;state.current_step_message='Queued for isolated worker'
        try: job_id=store(request).create_job(case_id,kind,payload,initial_state=state)
        except sqlite3.IntegrityError: raise HTTPException(409,'An active job already owns this case')
    if kind != 'evaluate':
        public = store(request).public(case_id)
        emit(store(request), job_id, 'initialize', 'completed', 'Investigation job accepted',
             case_id=case_id, atom_count=public.atom_count, job_kind=kind)
    return {'job_id':job_id,'status':'QUEUED'}


@router.get('/health')
def health(request:Request):
    return {'status':'ok','engine':request.app.state.capabilities,'calibration':request.app.state.calibration,'calibrated_atom_count':144,'ai_telemetry':request.app.state.telemetry.model_dump(mode='json',exclude_none=True),'budget_limit_sec':BUDGET,'cases_ready':len(store(request).case_ids())==4}


@router.get('/cases')
def cases(request:Request):
    return [store(request).public(c).model_dump(mode='json') for c in store(request).case_ids()]


@router.get('/cases/{case_id}')
def case(case_id:str,request:Request):
    known(request,case_id)
    public=store(request).public(case_id)
    state=store(request).state(case_id) or InvestigationState(case_id=case_id,status='OBSERVING',ai_telemetry=telemetry(),budget_total_sec=BUDGET)
    return {'case':public.model_dump(mode='json'),'investigation':state.model_dump(mode='json')}


@router.post('/cases/{case_id}/reset')
def reset(case_id:str,request:Request):
    known(request,case_id)
    with locks[case_id],store(request).connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute("SELECT 1 FROM jobs WHERE case_id=? AND status IN ('QUEUED','RUNNING')",(case_id,)).fetchone(): raise HTTPException(409,'Case has active work')
        db.execute('DELETE FROM states WHERE case_id=?',(case_id,))
    return {'case_id':case_id,'status':'RESET'}


@router.post('/cases/{case_id}/hypothesize',status_code=202)
def hypothesize(case_id:str,request:Request):
    known(request,case_id)
    return enqueue(request,case_id,'hypothesize')


@router.post('/cases/{case_id}/auto-investigate',status_code=202)
def investigate(case_id:str,request:Request,body:InvestigationRequest=InvestigationRequest()):
    known(request,case_id)
    return enqueue(request,case_id,'investigate',body.model_dump(exclude_none=True))


@router.post('/cases/{case_id}/experiment',status_code=202)
def experiment(case_id:str,request:Request,body:ExperimentRequest):
    known(request,case_id)
    if body.proposal_id:
        state=store(request).state(case_id)
        if state is None or not any(p.experiment_id==body.proposal_id for p in state.proposed_experiments): raise HTTPException(422,'Unknown registered proposal_id')
    return enqueue(request,case_id,'experiment',body.model_dump(mode='json',exclude_none=True))


@router.get('/cases/{case_id}/activity', response_model=ConsoleResponse)
def console_activity(case_id:str,request:Request,job_id:str|None=None):
    known(request,case_id)
    result = activity(store(request),case_id,job_id)
    if job_id and result.job is None: raise HTTPException(404,'Unknown job for this sample')
    return result


@router.get('/jobs/{job_id}')
def job(job_id:str,request:Request):
    try: data=store(request).job(job_id)
    except KeyError: raise HTTPException(404,'Unknown job')
    state=store(request).state(data['case_id'])
    data['current_step_message']=state.current_step_message if state else data['status']
    data['elapsed_sec']=max(0,(time.time() if data['status'] in ['QUEUED','RUNNING'] else data['updated'])-data['created'])
    return data


@router.post('/jobs/{job_id}/cancel',status_code=202)
def cancel(job_id:str,request:Request):
    try: existing=store(request).job(job_id)
    except KeyError: raise HTTPException(404,'Unknown job')
    if existing['status'] not in ['QUEUED','RUNNING']: raise HTTPException(409,'Job is already terminal')
    store(request).update_job(job_id,cancel=1)
    return {'job_id':job_id,'status':'CANCELLATION_REQUESTED'}


@router.get('/results/{sim_id}')
def result(sim_id:str,request:Request):
    try: return store(request).result(sim_id)
    except KeyError: raise HTTPException(404,'Unknown immutable result')


@router.post('/benchmarks/evaluate',status_code=202)
def evaluate(request:Request,x_admin_token:str=Header(default='')):
    global last_evaluation
    secret=os.getenv('NANO_ADMIN_TOKEN','')
    if not secret or not secrets.compare_digest(secret,x_admin_token): raise HTTPException(403,'Benchmark evaluation requires configured admin token')
    if time.monotonic()-last_evaluation<60: raise HTTPException(429,'Benchmark evaluation rate limit')
    job=enqueue(request,'BENCHMARK_EVALUATION','evaluate',{'timeout_sec':1800})
    last_evaluation=time.monotonic()
    return job
