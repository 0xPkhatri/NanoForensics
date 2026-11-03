import numpy as np
from backend.analysis.structure_analysis import reference_graph, rupture, persistent_cluster
from backend.analysis.stress_strain import detect_fracture
from backend.simulation.defect_generator import hex_lattice
from backend.models.schemas import ExperimentProposal, InterventionType, SimulationSummary, NumericalConsistencyCheck
from backend.analysis.evidence_verifier import verify


def test_free_surface_and_notch_not_initial_fracture():
    q=hex_lattice(8,8); q=np.delete(q,[24,32],axis=0)
    graph=reference_graph(q); mobile=np.ones(len(q),bool)
    z,loss,severed,clusters=rupture(q,graph,mobile)
    assert z.min()<6
    assert not loss.any() and not severed.any() and not clusters


def test_severed_reference_bonds_are_separate_from_coordination():
    q=hex_lattice(8,8); graph=reference_graph(q); moved=q.copy(); moved[27]+=[0,3]
    z,loss,severed,clusters=rupture(moved,graph,np.ones(len(q),bool))
    assert severed[27]>=2
    assert loss[27]==max(0,graph[27].sum()-z[27])


def test_persistent_cluster_and_retrospective_peak():
    cluster={1,2,3,4}
    assert persistent_cluster([[cluster],[],[]]) is None
    assert persistent_cluster([[cluster],[{6,7,8,9}],[cluster]]) is None
    stresses=[1,3,6,9,10,6,3,2,2,2]
    transient=[[] for _ in stresses]; transient[6]=[cluster]
    assert detect_fracture(stresses,transient)[1] is None
    sustained=[[] for _ in stresses]
    for k in [6,7,8,9]: sustained[k]=[cluster]
    assert detect_fracture(stresses,sustained)[1]==6
    assert detect_fracture([1,2,3,4,5],[[]]*5)[1] is None


def run(seed,failure=.2,valid=True,stress=5):
    return SimulationSummary(sim_id=f'run-{seed}-{failure}-{stress}', seed=seed,peak_stress=stress,failure_strain=failure,toughness=1,crack_initiation_region='distributed',mean_coordination_at_peak=5,min_coordination_region='distributed',stress_strain_curve=[],snapshots=[],outcome='FRACTURED' if failure is not None else 'NOT_FRACTURED_WITHIN_HORIZON',wall_time_sec=1,engine_used='NUMPY_VELOCITY_VERLET_2D',numerical_check=NumericalConsistencyCheck(is_valid=valid,max_force_norm=10,max_step_displacement=.01,thermostat_temperature_error_ratio=.05,energy_drift_ratio=1e-5,nan_detected=False,fracture_criterion_met=failure is not None,notes='Controlled statistical test input, not simulated benchmark evidence'))


def proposal(intervention=InterventionType.HEAL_INTERIOR_VACANCY):
    return ExperimentProposal(experiment_id='opaque',case_id='CASE_ALPHA',target_hypothesis_id='H1',intervention=intervention,matched_seeds=[42,137,271],controlled_parameters={},modified_parameters={},rationale='Test causal repair',estimated_cost_sec=3,expected_information_gain=1,risk_penalty=0,utility_score=.1)


def test_empirical_verdicts_censoring_failures_and_id_invariance():
    b=[run(s) for s in [42,137,271]]
    p=proposal()
    assert verify(p,b,[run(s,.26) for s in [42,137,271]]).verdict=='SUPPORTED'
    assert verify(p,b,[run(s,.2) for s in [42,137,271]]).verdict=='REJECTED'
    assert verify(p,b,[run(s,.22) for s in [42,137,271]]).verdict=='INCONCLUSIVE'
    cens=verify(p,b,[run(s,None) for s in [42,137,271]])
    assert cens.verdict=='PENDING' and cens.execution_status=='INSUFFICIENT_UNCENSORED_PAIRS' and cens.strain_recovery_pct is None
    failed=verify(p,b,[run(s,.26,False) for s in [42,137,271]])
    assert failed.execution_status=='EXECUTION_FAILED' and failed.verdict=='PENDING'
    answer=verify(p,b,[run(s,.26) for s in [42,137,271]])
    p.case_id='CASE_DELTA'
    assert verify(p,b,[run(s,.26) for s in [42,137,271]]).verdict==answer.verdict
    p.intervention=InterventionType.REPEAT_REPLICATE_SEEDS
    assert verify(p,b,[run(s,.26) for s in [42,137,271]]).verdict=='INCONCLUSIVE'
