"""Package measured audit evidence; never reads preparation labels or rewrites benchmarks."""
import gzip
import io
import hashlib
import json
import sqlite3
from pathlib import Path
import numpy as np
from backend.config import ROOT,DB_PATH
from backend.models.schemas import SpecimenInput
from backend.simulation.defect_generator import hex_lattice
from backend.simulation.numpy_md_fallback import prepare,nve_window


def build_report():
    source=ROOT/'runtime/science-audit';out=ROOT/'docs/science-audit';out.mkdir(parents=True,exist_ok=True)
    phases={name:json.loads((source/(name+'.json')).read_text()) for name in ['controls','repairs','balance','slow']}
    with sqlite3.connect(source/'original.db') as a,sqlite3.connect('file:'+str(DB_PATH.resolve())+'?mode=ro',uri=True) as b:
        specimens=a.execute('SELECT case_id,public,input FROM specimens ORDER BY case_id').fetchall()
        actual=b.execute('SELECT case_id,public,input FROM specimens ORDER BY case_id').fetchall()
        assert specimens==actual,'Frozen specimen or public baseline JSON changed'
        frozen_hash=hashlib.sha256(json.dumps(specimens).encode()).hexdigest()
        previous=a.execute('SELECT cache_key,sim_id,data FROM results').fetchall()
        unchanged=sum(b.execute('SELECT sim_id,data FROM results WHERE cache_key=?',(key,)).fetchone()==(sim_id,data) for key,sim_id,data in previous)
        assert unchanged==len(previous),'An existing immutable result was rewritten'
    q=hex_lattice(6,6);s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    q,v,_,_,mobile,_,_=prepare(s)
    _,_,coarse,_=nve_window(q.copy(),v.copy(),mobile,dt=.002,steps=500)
    _,_,fine,_=nve_window(q.copy(),v.copy(),mobile,dt=.001,steps=1000)
    files=sorted((source/'runs').glob('*.json'))
    with (out/'raw-runs.jsonl.gz').open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed, io.TextIOWrapper(compressed,encoding='utf-8') as archive:
        for path in files:
            archive.write(json.dumps({'artifact_hash':path.stem,'result':json.loads(path.read_text())},separators=(',',':'))+'\n')
    record={'status':'POST_BENCHMARK_SENSITIVITY_AUDIT','source_checkpoint':'00c4375','frozen_specimens_and_public_baselines_unchanged':True,'frozen_specimen_sha256':frozen_hash,'existing_immutable_results_checked':unchanged,'unique_recorded_run_artifacts':len(files),'distinct_input_engine_result_ids':len({json.loads(path.read_text())['sim_id'] for path in files}),'nve_same_microstate_refinement':{'coarse_dt':.002,'fine_dt':.001,'physical_duration':1.,'coarse_max_total_energy_drift':coarse,'fine_max_total_energy_drift':fine,'fine_to_coarse_ratio':fine/coarse},'phases':phases,'limitations':['Protocols examined after seeing original failures: sensitivity studies, not new held-out benchmark wins.','No acceptance thresholds changed. Raw temperature gate remains laboratory kinetic error <0.35.','Nine seed pairs are descriptive; added-atom Langevin streams are not atomwise identical across topology changes.','All raw temperatures and force moments remain accessible; supplemental flow subtraction cannot retroactively make a failed baseline valid.']}
    (out/'measurements.json').write_text(json.dumps(record,indent=2))
    return record


if __name__=='__main__':
    report=build_report()
    print(json.dumps({k:v for k,v in report.items() if k!='phases'},indent=2))
