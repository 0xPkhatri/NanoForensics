import hashlib
from pathlib import Path
import numpy as np
from backend.demonstration.registration import registration
from backend.demonstration.geometry import missing_components,reconstruct
from backend.simulation.defect_generator import hex_lattice
from backend.models.schemas import SpecimenInput,InterventionType


def test_preregistration_hash_and_original_thresholds_are_locked():
    design,digest=registration('v1')
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


def test_v2_registration_and_two_row_geometry_are_locked():
    design,digest=registration('v2')
    assert digest=='e8c9481b6698c3e52ffc75af36c08a981ee5f26fa2f1e45117ce1920d4202b8d'
    assert design['physical_validation']['true_temperature_relative_error_lt']==.35
    assert design['physical_validation']['open_slot_bank_separation_gt']==2.5
    q=hex_lattice(16,20);row=9
    q=np.delete(q,[r*16+i for r in [row,row+1] for i in range(5,11)]+[row*16],axis=0)
    parts=missing_components(q,minimum_neighbors=2)
    assert sorted((c['boundary_connected'],len(c['sites'])) for c in parts)==[(False,12),(True,1)]
    s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    edited,trace=reconstruct(s,InterventionType.HEAL_INTERIOR_VACANCY)
    assert len(edited.coordinates)==len(q)+12


def test_supplemental_checks_cannot_turn_an_invalid_run_into_valid():
    from tests.test_verifier import run
    from backend.demonstration.validation import validate_study_run
    q=hex_lattice(6,6);s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    invalid=run(42,valid=False)
    assert not validate_study_run(s,invalid).numerical_check.is_valid


def test_failed_study_runs_are_frozen_and_not_silently_retried(tmp_path):
    from backend.demonstration.storage import DemonstrationStore
    from tests.test_verifier import run
    from backend.models.schemas import SimulationOutcome
    store=DemonstrationStore(tmp_path/'failed-evidence.db')
    first=run(42,valid=False);first.outcome=SimulationOutcome.EXECUTION_FAILED
    store.save_result('registered-input',first)
    store.save_result('registered-input',run(42,valid=True))
    assert store.cached('registered-input').outcome=='EXECUTION_FAILED'


def test_v2_true_temperature_guard_is_stricter_than_denominator_floor():
    from tests.test_verifier import run
    from backend.models.schemas import Protocol,AtomSnapshot
    from backend.demonstration.validation import validate_study_run
    q=hex_lattice(6,6)
    specimen=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))),protocol=Protocol(temperature=.005))
    # Controlled guard fixture only; no generated scientific curve or benchmark result.
    controlled=run(42)
    controlled.snapshots=[AtomSnapshot(timestep=0,strain=0,stress_yy=0,potential_energy=0,kinetic_energy=0,atoms=[])]
    controlled.reference_geometry={'reference_coordinates':q.tolist()}
    controlled.diagnostics={'thermal_diagnostics':{'means':{'laboratory':.007}}}
    assert abs(.007-.005)/.01<.35
    guarded=validate_study_run(specimen,controlled,version=2)
    assert guarded.outcome=='EXECUTION_FAILED' and guarded.failure_strain is None
    assert not guarded.diagnostics['registered_study_checks']['checks']['temperature_without_floor']['passed']


def test_athermal_registration_and_inference_do_not_invent_independent_samples():
    from tests.test_verifier import run
    from backend.demonstration.analysis import discriminating_contrast
    design,digest=registration('v3')
    assert digest=='7d87eea832b65b65550879f453c53e7546ced33a3439953995bb5c74f7347a49'
    assert design['protocol']['temperature']==0
    assert design['physical_validation']['heldout_timestep_refinement']['required']
    seeds=[1,2,3];baseline=[run(s,.08) for s in seeds];winner=[run(s,.15) for s in seeds];other=[run(s,.081) for s in seeds]
    contrast=discriminating_contrast(baseline,winner,other,deterministic=True)
    assert contrast['is_distinguishable'] and contrast['independent_thermal_samples']==0
    assert contrast['mean_contrast_t_interval95'] is None
    winner[0].failure_strain=.16
    assert not discriminating_contrast(baseline,winner,other,deterministic=True)['is_distinguishable']


def test_refinement_winner_is_actual_finite_difference_not_case_assignment():
    from tests.test_verifier import run
    from backend.demonstration.convergence import deterministic_winner
    b=run(1,.08)
    assert deterministic_winner(b,{'A':run(1,.15),'B':run(1,.081)})=='A'
    assert deterministic_winner(b,{'A':run(1,.081),'B':run(1,.15)})=='B'
    assert deterministic_winner(b,{'A':run(1,.15),'B':run(1,.15)}) is None
    assert deterministic_winner(b,{}) is None


def test_registered_dominance_can_distinguish_two_beneficial_repairs():
    from tests.test_verifier import run
    from backend.demonstration.convergence import deterministic_winner
    # Both interventions exceed recovery 18%; the registered contrast is what matters.
    assert deterministic_winner(run(1,.08),{'X':run(1,.15),'Y':run(1,.11)})=='X'
    assert deterministic_winner(run(1,.08),{'X':run(1,.11),'Y':run(1,.15)})=='Y'
