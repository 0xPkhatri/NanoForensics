"""Restore only a checksummed public evidence bundle into an empty study database."""
import gzip
import hashlib
import json
from pathlib import Path
from backend.demonstration.registration import PUBLIC_DIR,registration,STUDY_DB
from backend.demonstration.storage import DemonstrationStore
from backend.models.schemas import FailureCasePublic,SpecimenInput,SimulationSummary,InvestigationState


def restore_public(path=None,store=None):
    path=Path(path or PUBLIC_DIR/'public-evidence.json.gz');store=store or DemonstrationStore(STUDY_DB)
    if store.case_ids():return {'status':'EXISTING_DATA_PRESERVED','case_count':len(store.case_ids())}
    if not path.exists():return {'status':'NO_PUBLIC_BUNDLE'}
    expected=path.with_suffix(path.suffix+'.sha256').read_text().split()[0]
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Public demonstration evidence checksum mismatch')
    body=json.loads(gzip.decompress(path.read_bytes()))
    _,digest=registration()
    if body['registration_hash']!=digest or body['private_preparations_included'] is not False:raise RuntimeError('Public archive does not match active registered study')
    for item in body['specimens']:
        store.put_specimen(FailureCasePublic.model_validate(item['public']),SpecimenInput.model_validate(item['observable_input']))
    for item in body['immutable_results']:store.save_result(item['cache_key'],SimulationSummary.model_validate(item['result']))
    for state in body.get('blind_investigation_states',[]):store.save_state(InvestigationState.model_validate(state))
    return {'status':'RESTORED_PUBLIC_MD_EVIDENCE','case_count':len(store.case_ids()),'registration_hash':digest}


if __name__=='__main__':print(json.dumps(restore_public(),indent=2))
