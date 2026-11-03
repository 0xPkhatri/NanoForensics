"""Verify post-study integration leaves locked evidence and source DBs untouched."""
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path
from backend.config import ROOT
from demonstrations.lock_development import verify_lock


def rows(path,table):
    with sqlite3.connect('file:'+str(path.resolve())+'?mode=ro',uri=True) as db:
        return sorted(db.execute('SELECT * FROM '+table).fetchall())


def verify():
    lock=verify_lock()
    changed=subprocess.check_output(['git','diff','71779ef','--name-only','--','docs/demonstration','docs/BENCHMARK_REPORT.md','docs/BENCHMARK_REPORT.json'],cwd=ROOT).decode().splitlines()
    if changed:raise RuntimeError('Frozen study files changed: '+', '.join(changed))
    tables={}
    for name,current in [('original',ROOT/'runtime/nanoforensics.db'),('study',ROOT/'runtime/demonstration/v3/study.db')]:
        snapshot=ROOT/f'runtime/live-muse/{name}-snapshot.db'
        if not snapshot.exists():raise RuntimeError('Local before-task snapshot required: '+str(snapshot))
        for table in ['specimens','results','states','jobs']:
            before=rows(snapshot,table);after=rows(current,table)
            if before!=after:raise RuntimeError(f'{name} {table} changed')
            tables[f'{name}.{table}']={'unchanged_rows':len(after),'sha256':hashlib.sha256(json.dumps(after,separators=(',',':')).encode()).hexdigest()}
    return {'status':'PASS','scientific_lock_source':lock['source_commit'],'frozen_git_evidence_checkpoint':'71779ef','frozen_study_files_unchanged':True,'database_tables':tables}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
