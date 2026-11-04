"""Durable, globally bounded job claim and actual OS process supervision."""
import json
import shutil
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
import psutil
from backend.config import ROOT, JOB_TIMEOUT
from backend.simulation.worker import kill_tree
from backend.api.progress import emit


class JobManager:
    def __init__(self,store,worker_module='backend.api.job_worker'):
        self.worker_module=worker_module
        self.store=store; self.stop_event=threading.Event();self.children={}
        self.thread=threading.Thread(target=self._loop,daemon=True,name='nano-job-supervisor')

    def start(self):
        # Recover only jobs whose supervising server is demonstrably gone.
        for job in self.store.active_jobs():
            owner=job['owner_pid']
            try:
                alive=bool(owner) and psutil.pid_exists(owner) and psutil.Process(owner).status()!=psutil.STATUS_ZOMBIE and psutil.Process(owner).create_time()<=job['created']
            except psutil.NoSuchProcess:
                alive=False
            if job['status']=='RUNNING' and not alive:
                pid=job['pid']
                if pid and psutil.pid_exists(pid):
                    try:
                        command=psutil.Process(pid).cmdline()
                        if self.worker_module in command and job['id'] in command: kill_tree(pid)
                    except psutil.NoSuchProcess: pass
                self._finish(job['id'],'INTERRUPTED','Recovered orphaned job after supervisor crash')
        self.thread.start()

    def close(self):
        self.stop_event.set();self.thread.join(timeout=5)
        for job_id,(proc,_,_) in list(self.children.items()):
            kill_tree(proc.pid);proc.wait()
            self._finish(job_id,'CANCELLED','Server shutdown terminated process tree')
        self.children.clear()

    def _claim(self):
        cancelled = None
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT COUNT(*) FROM jobs WHERE status='RUNNING'").fetchone()[0]>=2:
                return None
            row=db.execute("SELECT * FROM jobs WHERE status='QUEUED' ORDER BY created LIMIT 1").fetchone()
            if not row: return None
            if row['cancel']:
                cancelled = row['id']
            else:
                db.execute("UPDATE jobs SET status='RUNNING',owner_pid=?,updated=? WHERE id=?",(os.getpid(),time.time(),row['id']))
                claimed = dict(row)
        if cancelled:
            self._finish(cancelled,'CANCELLED','Requested cancellation before worker launch')
            return None
        return claimed

    def _finish(self,job_id,status,error=None):
        job=self.store.job(job_id)
        state=self.store.state(job['case_id'])
        if state:
            state.is_running=False
            if status!='COMPLETE':
                state.status='INCONCLUSIVE';state.final_verdict_summary=f'Execution status {status}: {error}'
                state.current_step_message=state.final_verdict_summary
                state.budget_used_sec+=max(0,time.time()-job['created'])
                from datetime import datetime,timezone
                state.audit_log.append({'timestamp':datetime.now(timezone.utc).isoformat(),'stage':'execution','status':status,'message':error})
            self.store.save_state(state)
        self.store.update_job(job_id,status=status,error=error)
        if job['kind'] != 'evaluate':
            emit(self.store, job_id, 'complete', 'completed' if status == 'COMPLETE' else 'failed',
                 'Worker job completed' if status == 'COMPLETE' else f'Worker job {status.lower()}',
                 execution_status=status, error=error,
                 elapsed_sec=max(0,time.time()-job['created']))
        shutil.rmtree(ROOT/'runtime/job_tmp'/job_id,ignore_errors=True)

    def _loop(self):
        while not self.stop_event.is_set():
            try:
                for job_id,(proc,started,limit) in list(self.children.items()):
                    job=self.store.job(job_id)
                    status=None;error=None
                    if job['cancel']:
                        kill_tree(proc.pid);status='CANCELLED';error='Requested cancellation; worker process tree terminated and reaped'
                    elif time.monotonic()-started>limit:
                        kill_tree(proc.pid);status='TIMED_OUT';error='Job deadline exceeded; worker process tree terminated and reaped'
                    elif proc.poll() is not None:
                        status='COMPLETE' if proc.returncode==0 else 'FAILED'
                        error=None if proc.returncode==0 else (job.get('error') or f'Worker exited {proc.returncode}')
                    if status:
                        proc.wait();self._finish(job_id,status,error);del self.children[job_id]
                job=self._claim()
                if job:
                    if job['kind'] != 'evaluate':
                        emit(self.store, job['id'], 'worker', 'started', 'Job claimed; launching an isolated worker')
                    job_tmp=ROOT/'runtime/job_tmp'/job['id']
                    job_tmp.mkdir(parents=True,exist_ok=True)
                    try:
                        proc=subprocess.Popen([sys.executable,'-m','backend.api.progress_worker',self.worker_module,str(self.store.path.resolve()),job['id']],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'NANO_TMP_ROOT':str(job_tmp),'TMPDIR':str(job_tmp)})
                    except OSError as exc:
                        self._finish(job['id'],'FAILED',f'Worker launch failed: {type(exc).__name__}')
                        continue
                    self.store.update_job(job['id'],pid=proc.pid)
                    payload=json.loads(job['payload'])
                    self.children[job['id']]=(proc,time.monotonic(),min(float(payload.get('timeout_sec') or JOB_TIMEOUT),1800.))
            except Exception as exc:
                # Keep poller alive; durable failure remains inspectable.
                import logging
                logging.getLogger(__name__).exception('Job supervisor error (%s)',type(exc).__name__)
            self.stop_event.wait(.1)
