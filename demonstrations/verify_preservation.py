"""Verify original records byte-for-byte, without reading private preparations."""
import hashlib
import json
import sqlite3
from backend.config import ROOT,DB_PATH


def verify():
    expected=json.loads((ROOT/'runtime/demonstration/original-fingerprint.json').read_text())
    with sqlite3.connect('file:'+str(DB_PATH.resolve())+'?mode=ro',uri=True) as db:
        rows=db.execute('SELECT case_id,public,input FROM specimens ORDER BY case_id').fetchall()
        results=db.execute('SELECT cache_key,sim_id,data FROM results ORDER BY cache_key').fetchall()
    assert hashlib.sha256(json.dumps(rows).encode()).hexdigest()==expected['specimens_sha256'],'Original frozen specimens changed'
    # Original new result insertion is not needed by this study. Assert the entire original result table unchanged.
    assert hashlib.sha256(json.dumps(results).encode()).hexdigest()==expected['results_sha256'],'Original result table changed'
    return {'original_specimens_unchanged':len(rows),'original_result_rows_unchanged':len(results),'fingerprint_source':expected['source_checkpoint']}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
