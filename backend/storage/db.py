"""SQLite immutable specimens/results, persisted state and durable exclusive jobs."""
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from backend.config import DB_PATH
from backend.models.schemas import FailureCasePublic, SpecimenInput, SimulationSummary, InvestigationState


class Store:
    def __init__(self, path=None):
        self.path=Path(path or DB_PATH)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS specimens(case_id TEXT PRIMARY KEY, public TEXT NOT NULL, input TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS results(cache_key TEXT PRIMARY KEY, sim_id TEXT UNIQUE NOT NULL, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS states(case_id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, case_id TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL, pid INTEGER, owner_pid INTEGER, cancel INTEGER NOT NULL DEFAULT 0, error TEXT, payload TEXT NOT NULL DEFAULT '{}', result TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_job ON jobs(case_id) WHERE status IN ('QUEUED','RUNNING');
            ''')

    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=15)
        db.row_factory=sqlite3.Row
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def put_specimen(self, public, specimen):
        with self.connect() as db:
            # Frozen inputs are never silently replaced.
            db.execute('INSERT INTO specimens VALUES(?,?,?)',(public.case_id,public.model_dump_json(),specimen.model_dump_json()))

    def case_ids(self):
        with self.connect() as db:
            return [r[0] for r in db.execute('SELECT case_id FROM specimens ORDER BY case_id')]

    def public(self, case_id):
        with self.connect() as db:
            row=db.execute('SELECT public FROM specimens WHERE case_id=?',(case_id,)).fetchone()
        if row is None: raise KeyError(case_id)
        return FailureCasePublic.model_validate_json(row[0])

    def specimen(self, case_id):
        """Executor-only input, not an agent tool or API response."""
        with self.connect() as db:
            row=db.execute('SELECT input FROM specimens WHERE case_id=?',(case_id,)).fetchone()
        if row is None: raise KeyError(case_id)
        return SpecimenInput.model_validate_json(row[0])

    def cached(self, key):
        with self.connect() as db:
            row=db.execute('SELECT data FROM results WHERE cache_key=?',(key,)).fetchone()
        return SimulationSummary.model_validate_json(row[0]) if row else None

    def save_result(self, key, result):
        if result.outcome=='EXECUTION_FAILED': return
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO results VALUES(?,?,?)',(key,result.sim_id,result.model_dump_json()))

    def result(self, sim_id):
        with self.connect() as db:
            row=db.execute('SELECT data FROM results WHERE sim_id=?',(sim_id,)).fetchone()
        if row is None: raise KeyError(sim_id)
        return SimulationSummary.model_validate_json(row[0])

    def save_state(self,state):
        with self.connect() as db:
            db.execute('INSERT INTO states VALUES(?,?) ON CONFLICT(case_id) DO UPDATE SET data=excluded.data',(state.case_id,state.model_dump_json()))

    def state(self,case_id):
        with self.connect() as db:
            row=db.execute('SELECT data FROM states WHERE case_id=?',(case_id,)).fetchone()
        return InvestigationState.model_validate_json(row[0]) if row else None

    def create_job(self,case_id,kind,payload=None,initial_state=None):
        job_id=uuid.uuid4().hex
        now=time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO jobs(id,case_id,kind,status,created,updated,payload) VALUES(?,?,?,?,?,?,?)',(job_id,case_id,kind,'QUEUED',now,now,json.dumps(payload or {})))
            if initial_state is not None:
                db.execute('INSERT INTO states VALUES(?,?) ON CONFLICT(case_id) DO UPDATE SET data=excluded.data',(case_id,initial_state.model_dump_json()))
        return job_id

    def job(self,job_id):
        with self.connect() as db:
            row=db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
        if row is None: raise KeyError(job_id)
        data=dict(row)
        for key in ['payload','result']:
            data[key]=json.loads(data[key]) if data[key] else None
        return data

    def update_job(self,job_id,**values):
        allowed={'status','pid','owner_pid','cancel','error','result'}
        if not values.keys() <= allowed: raise ValueError('unknown job field')
        if 'result' in values: values['result']=json.dumps(values['result'])
        values['updated']=time.time()
        with self.connect() as db:
            db.execute(f"UPDATE jobs SET {','.join(k+'=?' for k in values)} WHERE id=?",[*values.values(),job_id])

    def active_jobs(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM jobs WHERE status IN ('QUEUED','RUNNING')")]
