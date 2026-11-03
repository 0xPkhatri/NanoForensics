"""Privileged preparation: run ONCE before observers. Not imported by the live service."""
import json
import argparse
from pathlib import Path
import numpy as np
from backend.config import ROOT, SEEDS
from backend.models.schemas import SpecimenInput, Protocol, FailureCasePublic
from backend.simulation.defect_generator import hex_lattice
from backend.simulation.worker import run_bounded
from backend.analysis.comparison import aggregate
from backend.simulation.numpy_md_fallback import content_hash
from backend.simulation.lammps_runner import engine_capabilities
from backend.storage.db import Store


def cache_key(specimen):
    return content_hash({'input':specimen.model_dump(),'solver_version':'sflj-1.1','engine':engine_capabilities()})


def generate(store=None,truth_path=None):
    store=store or Store()
    truth_path=Path(truth_path or ROOT/'benchmarks/ground_truth.json')
    if store.case_ids():
        if len(store.case_ids())!=4: raise RuntimeError('Partial frozen benchmark; inspect before regenerating')
        return {'status':'EXISTING_FROZEN_INPUTS','cases':store.case_ids()}
    truth={}
    for index,name in enumerate(['CASE_ALPHA','CASE_BETA','CASE_GAMMA','CASE_DELTA']):
        pristine=hex_lattice(12,12)
        removed=[];p=Protocol()
        if index==0:
            order=np.argsort(np.linalg.norm(pristine-pristine.mean(axis=0),axis=1));removed=order[:3].tolist()
            cause='interior_vacancy'
        elif index==1:
            edge=np.flatnonzero(pristine[:,0]<.1)
            removed=sorted(edge,key=lambda i:abs(pristine[i,1]-np.mean(pristine[:,1])))[:2]
            cause='surface_notch'
        elif index==2:
            p.strain_rate*=4;cause='high_strain_rate'
        else:
            p.temperature=.38;cause='thermal_softening'
        coords=np.delete(pristine,removed,axis=0)
        # IDs carry no pristine lattice-site gaps.
        specimen=SpecimenInput(coordinates=coords.tolist(),atom_ids=list(range(len(coords))),protocol=p)
        runs=[]
        for seed in SEEDS:
            inp=specimen.model_copy(deep=True);inp.protocol.seed=seed
            result=run_bounded(inp)
            store.save_result(cache_key(inp),result)
            runs.append(result)
        public=FailureCasePublic(case_id=name,display_title=f'Blind Specimen {name.split("_")[1].title()} (2D Hexagonal LJ)',material_system='2D reduced-unit Lennard-Jones computational testbed',atom_count=len(coords),nominal_strain_rate=.05,initial_observations_summary='Actual three-seed simulated stress and trajectory measurements. The hidden preparation is withheld; observed coordinates are equally available to every comparator.',baseline_simulation=aggregate(runs),observed_configuration={'coordinates':coords.tolist(),'atom_ids':specimen.atom_ids})
        store.save_result('aggregate:'+public.baseline_simulation.sim_id,public.baseline_simulation)
        store.put_specimen(public,specimen)
        truth[name]={'cause':cause,'removed_original_site_ids':[int(x) for x in removed],'original_unmodified_lattice_site_ids':list(range(len(pristine))),'preparation_protocol':p.model_dump(),'input_hash':content_hash(specimen.model_dump()),'frozen_before_observers':True}
    truth_path.parent.mkdir(parents=True,exist_ok=True)
    truth_path.write_text(json.dumps(truth,indent=2))
    truth_path.chmod(0o600)
    return {'status':'GENERATED','cases':store.case_ids(),'baseline_outcomes':{c:store.public(c).baseline_simulation.outcome for c in store.case_ids()}}


if __name__=='__main__':
    print(json.dumps(generate(),indent=2))
