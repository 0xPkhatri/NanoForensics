"""Owned process groups for the live E2E script and restart acceptance checks."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
import psutil

ROOT=Path(__file__).resolve().parents[1]


def start(kind,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000'] if kind=='api' else ['npm','start']
    cwd=ROOT if kind=='api' else ROOT/'frontend'
    with (directory/f'{kind}.log').open('a') as log:
        proc=subprocess.Popen(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=os.environ.copy())
    (directory/f'{kind}.pid').write_text(str(proc.pid))
    return proc.pid


def stop(kind,directory):
    file=Path(directory)/f'{kind}.pid'
    if not file.exists():return
    pid=int(file.read_text())
    try:
        os.killpg(pid,signal.SIGTERM)
        process=psutil.Process(pid)
        try: process.wait(timeout=5)
        except psutil.TimeoutExpired:
            os.killpg(pid,signal.SIGKILL)
    except (ProcessLookupError,psutil.NoSuchProcess):pass


if __name__=='__main__':
    action,directory=sys.argv[1:3]
    kind=sys.argv[3] if len(sys.argv)>3 else 'both'
    for selected in (['api','ui'] if kind=='both' else [kind]):
        if action=='start':start(selected,directory)
        elif action=='stop':stop(selected,directory)
        else:raise ValueError(action)
