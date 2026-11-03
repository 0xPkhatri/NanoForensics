"""Replay public MD evidence without access to private preparation files or mutable DBs."""
import argparse
import gzip
import hashlib
import json
from backend.demonstration.registration import PUBLIC_DIR,registration
from backend.demonstration.validation import validate_study_run
from backend.models.schemas import SpecimenInput
from backend.simulation.worker import run_bounded
from demonstrations.reproduce import physical_record


def replay(case_id=None):
    path=PUBLIC_DIR/'public-evidence.json.gz'
    expected=path.with_suffix(path.suffix+'.sha256').read_text().split()[0]
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Public evidence checksum mismatch')
    body=json.loads(gzip.decompress(path.read_bytes()))
    design,digest=registration()
    if body['registration_hash']!=digest:raise RuntimeError('Registration mismatch')
    case_id=case_id or design['held_out']['case_ids'][0]
    case=next(c for c in body['specimens'] if c['case_id']==case_id)
    previous=case['public']['baseline_simulation']['replicate_results'][0]
    inp=SpecimenInput.model_validate(case['observable_input']);inp.protocol.seed=previous['seed']
    current=validate_study_run(inp,run_bounded(inp,timeout=90));actual=current.model_dump(mode='json')
    fields=list(physical_record(current))
    equal=all(actual[key]==previous[key] for key in fields)
    result={'case_id':case_id,'seed_label':inp.protocol.seed,'registration_hash':digest,'exact_numeric_reproduction':equal,'engine':current.engine_used,'interpretation':'same-engine numerical replay, not an independent thermal sample','private_preparation_access':False,'wall_time_sec':current.wall_time_sec}
    if not equal:raise RuntimeError(json.dumps(result))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case');args=parser.parse_args()
    print(json.dumps(replay(args.case),indent=2))
