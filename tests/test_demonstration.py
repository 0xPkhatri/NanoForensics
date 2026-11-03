import hashlib
from pathlib import Path
import numpy as np
from backend.demonstration.registration import registration
from backend.demonstration.geometry import missing_components,reconstruct
from backend.simulation.defect_generator import hex_lattice
from backend.models.schemas import SpecimenInput,InterventionType


def test_preregistration_hash_and_original_thresholds_are_locked():
    design,digest=registration()
    assert digest=='09f0c37f89155e4d60af658b7e1c538cb8aaf026ab0c44e9ef85f44e1322aa6a'
    assert design['physical_validation']['raw_temperature_error_lt']==.35
    assert design['scientific_validation']['failure_recovery_pct_min']==18
    assert not set(design['development']['seeds'])&set(design['held_out']['seeds'])


def test_boundary_connected_component_is_not_misclassified_as_interior():
    pristine=hex_lattice(16,20);row=9
    q=np.delete(pristine,[row*16+i for i in range(6)]+[row*16+11],axis=0)
    components=missing_components(q)
    assert sorted((c['boundary_connected'],len(c['sites'])) for c in components)==[(False,1),(True,6)]
    specimen=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    for intervention,n in [(InterventionType.HEAL_INTERIOR_VACANCY,1),(InterventionType.SMOOTH_SURFACE_NOTCH,6)]:
        repaired,trace=reconstruct(specimen,intervention)
        assert len(repaired.coordinates)==len(q)+n and trace['status']=='APPLIED'
        from scipy.spatial import cKDTree
        assert cKDTree(pristine).query(repaired.coordinates)[0].max()<1e-10
    shuffled=q[np.random.default_rng(27).permutation(len(q))]
    assert missing_components(shuffled)==components


def test_pristine_negative_control_is_a_noop_for_both_repairs():
    q=hex_lattice(16,20);s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    assert missing_components(q)==[]
    for intervention in [InterventionType.HEAL_INTERIOR_VACANCY,InterventionType.SMOOTH_SURFACE_NOTCH]:
        edited,trace=reconstruct(s,intervention)
        assert edited.model_dump()==s.model_dump() and trace['status']=='NO_APPLICABLE_EDIT'


def test_interior_component_and_secondary_edge_are_distinct_edits():
    q=hex_lattice(16,20);row=9
    q=np.delete(q,[row*16+i for i in range(5,11)]+[row*16],axis=0)
    parts=missing_components(q)
    assert sorted((x['boundary_connected'],len(x['sites'])) for x in parts)==[(False,6),(True,1)]


def test_contrast_uses_observations_only_and_rejects_censoring():
    from tests.test_verifier import run
    from backend.demonstration.analysis import discriminating_contrast
    b=[run(s,.08) for s in [1,2,3,4,5,6,7,8,9]]
    w=[run(s,.15) for s in [1,2,3,4,5,6,7,8,9]]
    c=[run(s,.081) for s in [1,2,3,4,5,6,7,8,9]]
    assert discriminating_contrast(b,w,c)['is_distinguishable']
    assert not discriminating_contrast(b,c,w)['is_distinguishable']
    w[0].failure_strain=None
    assert discriminating_contrast(b,w,c)['status']=='CENSORED'


def test_live_demo_helpers_have_no_private_preparation_access():
    import inspect
    from backend.demonstration import geometry,analysis,investigator
    for module in [geometry,analysis,investigator]:
        source=inspect.getsource(module)
        assert 'ground_truth' not in source and 'demonstrations.generate' not in source


def test_dataset_api_routes_are_isolated_and_protocol_edits_rejected(tmp_path):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.storage.db import Store
    from backend.models.schemas import FailureCasePublic,Protocol
    from tests.test_verifier import run
    with TestClient(app) as client:
        original=app.state.store
        temporary=Store(tmp_path/'isolated-demo.db')
        q=hex_lattice(6,6)
        inp=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))),protocol=Protocol())
        public=FailureCasePublic(case_id='DEMO_999',display_title='Controlled API fixture',material_system='test fixture',atom_count=len(q),nominal_strain_rate=.005,initial_observations_summary='API isolation only; not scientific demonstration evidence.',baseline_simulation=run(42),observed_configuration={'coordinates':q.tolist(),'study_partition':'development'})
        temporary.put_specimen(public,inp);app.state.demonstration_store=temporary
        assert client.get('/api/cases/DEMO_999').status_code==404
        assert client.get('/api/demonstrations/cases/CASE_ALPHA').status_code==404
        assert client.get('/api/demonstrations/cases/DEMO_999').status_code==200
        assert [c['case_id'] for c in client.get('/api/cases').json()]==original.case_ids()
        assert client.post('/api/demonstrations/cases/DEMO_999/experiment',json={'intervention':'normalize_temperature'}).status_code==422
        assert client.post('/api/demonstrations/cases/DEMO_999/experiment',json={'intervention':'heal_interior_vacancy','parameters':{'target_temperature':.01}}).status_code==422
        queued=client.post('/api/demonstrations/cases/DEMO_999/auto-investigate',json={})
        assert queued.status_code==202
        job=temporary.job(queued.json()['job_id'])
        assert job['payload']['timeout_sec']==900
        assert client.get('/api/jobs/'+job['id']).status_code==404
        assert client.post('/api/demonstrations/cases/DEMO_999/reset').status_code==409
        temporary.update_job(job['id'],status='CANCELLED')
