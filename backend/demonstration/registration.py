"""Public immutable study designs. No specimen-to-family assignments."""
import hashlib
import json
import os
from pathlib import Path
from backend.config import ROOT


def active_version():
    path=ROOT/'demonstrations/active-study.json'
    version=int(os.getenv('NANO_DEMONSTRATION_VERSION',str(json.loads(path.read_text())['version'] if path.exists() else 1)))
    if version not in [1,2,3]:raise RuntimeError('Unregistered study version')
    return version


def registration(version=None):
    version=VERSION if version is None else int(str(version).removeprefix('v'))
    path=ROOT/'demonstrations'/('registration.json' if version==1 else f'v{version}/registration.json')
    data=path.read_bytes();actual=hashlib.sha256(data).hexdigest()
    expected=path.with_name('registration.sha256').read_text().split()[0]
    if actual!=expected:raise RuntimeError('Preregistered study design hash changed')
    return json.loads(data),actual


VERSION=active_version()
STUDY_DIR=ROOT/'runtime/demonstration' if VERSION==1 else ROOT/f'runtime/demonstration/v{VERSION}'
PUBLIC_DIR=ROOT/'docs/demonstration' if VERSION==1 else ROOT/f'docs/demonstration/v{VERSION}'
DESIGN_DIR=ROOT/'demonstrations' if VERSION==1 else ROOT/f'demonstrations/v{VERSION}'
STUDY_DB=Path(os.getenv('NANO_DEMONSTRATION_DB',str(STUDY_DIR/'study.db')))
STATUS_PATH=PUBLIC_DIR/'status.json'


def public_status():
    design,digest=registration()
    data=json.loads(STATUS_PATH.read_text()) if STATUS_PATH.exists() else {'validation_status':'NOT_GENERATED'}
    return {'study_id':design['study_id'],'registration_hash':digest,'scope':design['scope'],'version':VERSION,'previous_studies':[{'version':v,'development_status':'NOT_VALIDATED','held_out_status':'NOT_GENERATED'} for v in range(1,VERSION)],**data}
