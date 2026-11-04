"""Public operation telemetry, separate from scientific state and model inputs."""
import json
import math
import time
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

Phase = Literal['initialize', 'worker', 'observe', 'hypotheses', 'plan', 'simulate', 'verify', 'revise', 'conclude', 'complete']
EventStatus = Literal['started', 'completed', 'failed', 'skipped']


class ConsoleEvent(BaseModel):
    seq: int
    job_id: str
    timestamp: str
    phase: Phase
    status: EventStatus
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class ConsoleJob(BaseModel):
    id: str
    case_id: str
    kind: str
    status: str
    created: float
    updated: float
    elapsed_sec: float
    error: str | None = None


class ConsoleResponse(BaseModel):
    job: ConsoleJob | None = None
    events: list[ConsoleEvent] = Field(default_factory=list)


def finite_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: finite_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(item) for item in value]
    return value


def emit(store, job_id, phase: Phase, status: EventStatus, message: str, **data):
    # Callers provide allowlisted public observations/receipts, never raw worker stderr,
    # credentials, private preparations, raw prompts or serialized specimen inputs.
    with store.connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS job_events(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
            timestamp TEXT NOT NULL, phase TEXT NOT NULL, status TEXT NOT NULL,
            message TEXT NOT NULL, data TEXT NOT NULL)''')
        db.execute('CREATE INDEX IF NOT EXISTS job_events_by_job ON job_events(job_id,seq)')
        db.execute('INSERT INTO job_events(job_id,timestamp,phase,status,message,data) VALUES(?,?,?,?,?,?)',
                   (job_id, datetime.now(timezone.utc).isoformat(), phase, status, message,
                    json.dumps(finite_json(data), allow_nan=False, separators=(',', ':'))))


def activity(store, case_id, job_id=None):
    with store.connect() as db:
        db.execute('BEGIN')  # Read job status and events from one consistent snapshot.
        if job_id is None:
            job = db.execute("SELECT * FROM jobs WHERE case_id=? AND kind IN ('investigate','experiment','hypothesize') ORDER BY created DESC,rowid DESC LIMIT 1", (case_id,)).fetchone()
        else:
            job = db.execute("SELECT * FROM jobs WHERE case_id=? AND id=? AND kind IN ('investigate','experiment','hypothesize')", (case_id,job_id)).fetchone()
        if job is None:
            return ConsoleResponse()
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='job_events'").fetchone()
        events = []
        if exists:
            for row in db.execute('SELECT * FROM job_events WHERE job_id=? ORDER BY seq', (job['id'],)):
                event = dict(row); event['data'] = json.loads(event['data'])
                events.append(ConsoleEvent.model_validate(event))
        end = time.time() if job['status'] in ['QUEUED', 'RUNNING'] else job['updated']
        return ConsoleResponse(job=ConsoleJob(**{key: job[key] for key in ['id','case_id','kind','status','created','updated','error']}, elapsed_sec=max(0, end-job['created'])), events=events)
