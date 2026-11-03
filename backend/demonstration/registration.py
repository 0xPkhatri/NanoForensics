"""Public, immutable study design. Contains no specimen-to-family assignments."""
import hashlib
import json
import os
from pathlib import Path
from backend.config import ROOT

REGISTRATION_PATH=ROOT/'demonstrations/registration.json'
STUDY_DB=Path(os.getenv('NANO_DEMONSTRATION_DB',str(ROOT/'runtime/demonstration/study.db')))
STATUS_PATH=ROOT/'docs/demonstration/status.json'


def registration():
    data=REGISTRATION_PATH.read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    expected=(REGISTRATION_PATH.parent/'registration.sha256').read_text().split()[0]
    if actual!=expected:raise RuntimeError('Preregistered study design hash changed')
    return json.loads(data),actual


def public_status():
    design,digest=registration()
    data=json.loads(STATUS_PATH.read_text()) if STATUS_PATH.exists() else {'validation_status':'NOT_GENERATED'}
    return {'study_id':design['study_id'],'registration_hash':digest,'scope':design['scope'],**data}
