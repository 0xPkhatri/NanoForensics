"""Privileged preparation. Live agents never import this module."""
import argparse
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
import numpy as np
from backend.config import ROOT
from backend.demonstration.storage import DemonstrationStore as Store
from backend.models.schemas import Protocol,SpecimenInput,FailureCasePublic
from backend.simulation.defect_generator import hex_lattice
from backend.simulation.worker import run_bounded
from backend.simulation.numpy_md_fallback import content_hash
from backend.simulation.lammps_runner import engine_capabilities
from backend.analysis.comparison import aggregate
from backend.demonstration.registration import registration,STUDY_DB,STUDY_DIR,DESIGN_DIR


def key(specimen):
    return content_hash({'input':specimen.model_dump(),'solver_version':'sflj-1.1','engine':engine_capabilities()})


def generate(partition):
    design,digest=registration();root=STUDY_DIR;store=Store(STUDY_DB)
    lock=root/f'{partition}.generation.lock';root.mkdir(parents=True,exist_ok=True)
    if partition=='held_out':
        development_lock=DESIGN_DIR/'development-lock.json'
        if not development_lock.exists():raise RuntimeError('Development analysis/prediction lock required before held-out generation')
        from demonstrations.lock_development import verify_lock
        verify_lock()
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    target=design[partition]
    truth_file=root/'private'/partition/'ground_truth.json';truth_file.parent.mkdir(parents=True,exist_ok=True)
    truth=json.loads(truth_file.read_text()) if truth_file.exists() else {}
    # Private assignment differs between partitions; IDs never condition MD or inference.
    assignment=np.random.default_rng(91832 if partition=='development' else 57391).permutation(3)
    started=time.perf_counter()
    try:
        for case_id,family in zip(target['case_ids'],assignment):
            if case_id in store.case_ids():continue
            nx,ny=design['lattice']['nx'],design['lattice']['ny'];q=hex_lattice(nx,ny);row=target['gap_row']
            if family==0:
                removed=[r*nx+i for r in range(row,row+(2 if design['version']>=2 else 1)) for i in range(5,11)]+[row*nx]
                cause='interior_vacancy'
            elif family==1:
                removed=[r*nx+i for r in range(row,row+(2 if design['version']>=2 else 1)) for i in range(6)]+[row*nx+11]
                cause='surface_notch'
            else:removed=[];cause=None
            coordinates=np.delete(q,removed,axis=0)
            inp=SpecimenInput(coordinates=coordinates.tolist(),atom_ids=list(range(len(coordinates))),protocol=Protocol(**design['protocol']))
            records=[]
            for seed in target['seeds']:
                if time.perf_counter()-started>design['budgets']['whole_study_sec']:raise TimeoutError('Registered study generation budget exceeded')
                s=inp.model_copy(deep=True);s.protocol.seed=seed
                result=run_bounded(s,timeout=design['budgets']['per_run_sec'])
                from backend.demonstration.validation import validate_study_run
                result=validate_study_run(s,result)
                store.save_result(key(s),result);records.append(result)
                print(partition,case_id,seed,result.outcome.value,result.wall_time_sec,flush=True)
            summary=aggregate(records)
            public=FailureCasePublic(case_id=case_id,display_title='Blind demonstration specimen '+case_id.split('_')[1],material_system='Separate preregistered 2D reduced-unit SFLJ computational study',atom_count=len(coordinates),nominal_strain_rate=inp.protocol.strain_rate,reported_strain_rate=inp.protocol.strain_rate,temperature_lj=inp.protocol.temperature,initial_observations_summary='Genuine simulated, immutable '+partition+' observations. Preparation withheld; all candidates receive identical observable geometry/protocol access.',baseline_simulation=summary,observed_configuration={'coordinates':inp.coordinates,'atom_ids':inp.atom_ids,'study_partition':partition,'registration_hash':digest,'public_protocol':design['protocol']})
            store.put_specimen(public,inp);store.save_result('aggregate:'+summary.sim_id,summary)
            truth[case_id]={'cause':cause,'removed_original_site_ids':removed,'original_unmodified_lattice_site_ids':list(range(len(q))),'input_hash':content_hash(inp.model_dump()),'registration_hash':digest}
            truth_file.write_text(json.dumps(truth,indent=2));truth_file.chmod(0o600)
        return {'partition':partition,'registration_hash':digest,'case_ids':target['case_ids'],'generation_wall_time_sec':time.perf_counter()-started}
    finally:lock.unlink(missing_ok=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--partition',choices=['development','held_out'],required=True);args=p.parse_args()
    print(json.dumps(generate(args.partition),indent=2))
