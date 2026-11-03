"""Prospective gate: commit analysis and development predictions before held-out data."""
import hashlib
import json
import subprocess
from pathlib import Path
from backend.config import ROOT
from backend.demonstration.registration import registration,DESIGN_DIR,PUBLIC_DIR


def science_files():
    return sorted(set(list((ROOT/'backend/demonstration').glob('*.py'))+list((ROOT/'backend/simulation').glob('*.py'))+list((ROOT/'backend/simulation/input_templates').glob('*.j2'))+list((ROOT/'backend/analysis').glob('*.py'))+[ROOT/p for p in ['backend/models/schemas.py','backend/analysis/comparison.py','backend/analysis/evidence_verifier.py','backend/agents/investigator.py','demonstrations/generate.py','demonstrations/evaluate.py','demonstrations/refinement.py','demonstrations/reproduce.py','demonstrations/lock_development.py','tests/test_demonstration.py']]))


def lock():
    design,digest=registration();out=DESIGN_DIR/'development-lock.json'
    if out.exists():raise RuntimeError('Development analysis lock already exists')
    result=json.loads((PUBLIC_DIR/'development-evaluation.json').read_text())
    if not all(row['numeric_complete_uncensored'] and row.get('exact_replays',True) for row in result['rows']):raise RuntimeError('Development numerical/data validity failed; held-out generation prohibited')
    replay_file=PUBLIC_DIR/'reproducibility.json'
    if not replay_file.exists() or not json.loads(replay_file.read_text())['exact_numeric_reproduction']:raise RuntimeError('Registered fresh reproducibility check required before held-out generation')
    decisions=PUBLIC_DIR/'development-decisions-corrected.json'
    if not decisions.exists():decisions=PUBLIC_DIR/'development-decisions.json'
    files=science_files();relative=[str(p.relative_to(ROOT)) for p in files]
    if subprocess.check_output(['git','diff','HEAD','--name-only','--',*relative],cwd=ROOT).strip():raise RuntimeError('Commit scientific source before locking held-out analysis')
    body={'registration_hash':digest,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'development_decisions_file':decisions.name,'development_decisions_sha256':hashlib.sha256(decisions.read_bytes()).hexdigest(),'development_status':result['validation_status'],'held_out_generation_authorized':True,'note':'No protocol/threshold amendments permitted. Scientific development failure remains disclosed.'}
    out.write_text(json.dumps(body,indent=2)+'\n')
    return body


def verify_lock():
    _,digest=registration();fixed=json.loads((DESIGN_DIR/'development-lock.json').read_text())
    if fixed['registration_hash']!=digest or not fixed['held_out_generation_authorized']:raise RuntimeError('No matching prospective held-out authorization')
    for path,expected in fixed['source_files'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise RuntimeError('Locked scientific code changed: '+path)
    if hashlib.sha256((PUBLIC_DIR/fixed['development_decisions_file']).read_bytes()).hexdigest()!=fixed['development_decisions_sha256']:raise RuntimeError('Fixed development predictions changed')
    return fixed


if __name__=='__main__':print(json.dumps(lock(),indent=2))
