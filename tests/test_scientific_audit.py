"""Independent invariants discovered during the scientific diagnosis audit."""
import numpy as np
from scipy.spatial import cKDTree
from backend.analysis.thermal_diagnostics import kinetic_diagnostics
from backend.simulation.defect_generator import hex_lattice,transform
from backend.simulation.numpy_md_fallback import grip_masks,relax,forces,prepare,nve_window
from backend.models.schemas import SpecimenInput,InterventionType


def test_streaming_diagnostics_decompose_kinetic_energy_without_changing_gate():
    q=hex_lattice(8,8);bottom,top,mobile=grip_masks(q)
    gauge=float(np.ptp(q[:,1]));rng=np.random.default_rng(19)
    v=rng.normal(0,.1,q.shape);v[:,1]+=.05*(q[:,1]-q[:,1].mean())
    d=kinetic_diagnostics(q,v,mobile,bottom,top,gauge,.05)
    assert np.isclose(d['laboratory'],d['affine_residual']+d['affine_stream_kinetic']+d['affine_cross_term'],rtol=1e-12)
    boosted=v+np.array([3.,-2.])
    db=kinetic_diagnostics(q,boosted,mobile,bottom,top,gauge,.05)
    assert np.isclose(db['com_removed'],d['com_removed'])
    assert np.isclose(db['local_flow_residual'],d['local_flow_residual'])
    assert db['laboratory']>d['laboratory']


def test_reconstruction_recovers_observable_geometry_and_relaxed_energy():
    pristine=hex_lattice(8,8)
    for remove,edit in [([27,28],InterventionType.HEAL_INTERIOR_VACANCY),([24,32],InterventionType.SMOOTH_SURFACE_NOTCH)]:
        q=np.delete(pristine,remove,axis=0)
        s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
        repaired,trace=transform(s,edit)
        assert trace['status']=='APPLIED'
        fixed=np.array(repaired.coordinates)
        assert len(fixed)==len(pristine)
        assert cKDTree(pristine).query(fixed)[0].max()<1e-10
        relaxed,residual=relax(fixed,grip_masks(fixed)[2])
        reference,_=relax(pristine,grip_masks(pristine)[2])
        assert residual<.005
        assert np.isclose(forces(relaxed)[1],forces(reference)[1],atol=1e-8)


def test_deterministic_nve_refinement_uses_identical_initial_microstate():
    q=hex_lattice(6,6);s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))))
    q,v,_,_,mobile,_,_=prepare(s)
    _,_,coarse,_=nve_window(q.copy(),v.copy(),mobile,dt=.002,steps=500)
    _,_,fine,_=nve_window(q.copy(),v.copy(),mobile,dt=.001,steps=1000)
    assert coarse<1e-3 and fine<1e-3
    assert fine<coarse*.4,(coarse,fine)


def test_full_pair_virial_equals_grip_and_mobile_force_moments():
    from backend.analysis.force_balance import force_moment_balance
    q=hex_lattice(8,8);bottom,top,mobile=grip_masks(q)
    q[:,1]*=1.08;q[27]+=[.04,-.07]
    f,_,vir=forces(q);v=np.zeros_like(q)
    v[mobile,1]=.03*q[mobile,1]
    result=force_moment_balance(q,v,f,vir,mobile,bottom,top,float(np.ptp(q[:,0])*np.ptp(q[:,1])))
    assert abs(result['identity_residual'])<1e-12
    from backend.analysis.stress_strain import virial_stress
    assert np.isclose(result['reported_mobile_stress'],virial_stress(v,vir,mobile,np.ptp(q[:,0])*np.ptp(q[:,1]))[1,1])
    # Non-equilibrium mobile force moments cannot be silently assumed zero.
    assert abs(result['mobile_force_moment'])>1e-3


def test_lammps_records_real_thermostat_and_internal_force_moments():
    import pytest
    from backend.simulation.lammps_runner import binary,run_simulation
    from backend.models.schemas import Protocol
    if not binary():pytest.skip('LAMMPS unavailable; realized force split NOT_RUN')
    q=hex_lattice(6,6)
    s=SpecimenInput(coordinates=q.tolist(),atom_ids=list(range(len(q))),protocol=Protocol(max_strain=.05,warmup_steps=500))
    result=run_simulation(s)
    gates=result.diagnostics['validity_gates']
    assert gates['driven_laboratory_temperature']['upper_bound']==.35
    assert gates['preload_nve_drift']['upper_bound']==1e-3
    assert result.numerical_check.is_valid==all(gate['passed'] for gate in gates.values())
    balance=result.diagnostics['force_balance']
    assert result.engine_used=='LAMMPS_BINARY'
    assert balance['max_identity_residual']<1e-10
    assert all(row['realized_mobile_force_moment'] is not None for row in balance['series'])
    assert max(abs(row['thermostat_force_moment']) for row in balance['series'])>1e-3
    assert all(np.isclose(row['mobile_force_moment'],row['realized_mobile_force_moment']-row['thermostat_force_moment']) for row in balance['series'])
