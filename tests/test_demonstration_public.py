import gzip
import json
from pathlib import Path
import pytest
from backend.demonstration.registration import PUBLIC_DIR
from backend.demonstration.storage import DemonstrationStore
from demonstrations.restore import restore_public


def test_public_bundle_restores_both_partitions_without_private_labels(tmp_path):
    path=PUBLIC_DIR/'public-evidence.json.gz'
    assert path.exists(),'Package the preregistered MD evidence before acceptance'
    raw=json.loads(gzip.decompress(path.read_bytes()))
    assert raw['private_preparations_included'] is False
    text=json.dumps(raw)
    for forbidden in ['removed_original_site_ids','original_unmodified_lattice_site_ids','ground_truth']:
        assert forbidden not in text
    store=DemonstrationStore(tmp_path/'public.db')
    assert restore_public(path,store)['status']=='RESTORED_PUBLIC_MD_EVIDENCE'
    assert len(store.case_ids())==6
    assert {store.public(c).observed_configuration['study_partition'] for c in store.case_ids()}=={'development','held_out'}
    before=store.public(store.case_ids()[0]).model_dump_json()
    assert restore_public(path,store)['status']=='EXISTING_DATA_PRESERVED'
    assert store.public(store.case_ids()[0]).model_dump_json()==before


def test_corrupted_archive_is_rejected_before_any_records_are_written(tmp_path):
    source=PUBLIC_DIR/'public-evidence.json.gz'
    target=tmp_path/'tampered.json.gz';data=bytearray(source.read_bytes());data[-1]^=1
    target.write_bytes(data)
    target.with_suffix(target.suffix+'.sha256').write_bytes(source.with_suffix(source.suffix+'.sha256').read_bytes())
    store=DemonstrationStore(tmp_path/'empty.db')
    with pytest.raises(RuntimeError,match='checksum mismatch'):restore_public(target,store)
    assert store.case_ids()==[]
