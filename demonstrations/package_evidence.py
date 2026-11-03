"""Versioned public evidence archives, with private preparation maps excluded."""
import gzip
import io
import json
import sqlite3
from pathlib import Path
from backend.config import ROOT
from backend.demonstration.registration import registration,STUDY_DB,STUDY_DIR,PUBLIC_DIR


def package():
    design,digest=registration();PUBLIC_DIR.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect('file:'+str(STUDY_DB.resolve())+'?mode=ro',uri=True) as db:
        specimens=[{'case_id':row[0],'public':json.loads(row[1]),'observable_input':json.loads(row[2])} for row in db.execute('SELECT case_id,public,input FROM specimens ORDER BY case_id')]
        states=[json.loads(row[0]) for row in db.execute('SELECT data FROM states ORDER BY case_id')]
        results=[{'cache_key':row[0],'result':json.loads(row[1])} for row in db.execute('SELECT cache_key,data FROM results ORDER BY cache_key')]
    payload={'registration_hash':digest,'study_id':design['study_id'],'scope':design['scope'],'specimens':specimens,'immutable_results':results,'blind_investigation_states':states,'private_preparations_included':False,'replicate_interpretation':design['inference'].get('validation_unit','Thermal seed blocks; no atomwise common-noise guarantee')}
    path=PUBLIC_DIR/'public-evidence.json.gz'
    with path.open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as compressed,io.TextIOWrapper(compressed,encoding='utf-8') as out:
        json.dump(payload,out,separators=(',',':'))
    import hashlib
    path.with_suffix(path.suffix+'.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n')
    timings=[r['result']['wall_time_sec'] for r in results if not r['cache_key'].startswith('aggregate:')]
    summary={'registration_hash':digest,'case_count':len(specimens),'immutable_result_count':len(results),'per_run_wall_time_sec':{'min':min(timings) if timings else None,'max':max(timings) if timings else None,'target_3_to_12_sec_met_for_all':all(3<=t<=12 for t in timings)},'archive':str(path.relative_to(ROOT)),'private_preparations_included':False}
    (PUBLIC_DIR/'evidence-index.json').write_text(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':print(json.dumps(package(),indent=2))
