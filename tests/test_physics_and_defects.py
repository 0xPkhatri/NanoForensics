import numpy as np
import pytest
from backend.models.schemas import SpecimenInput, Protocol
from backend.simulation.numpy_md_fallback import sflj, forces, nve_window, prepare, content_hash
from backend.simulation.defect_generator import hex_lattice, infer_missing_sites, transform
from backend.simulation.lammps_runner import binary, engine_capabilities, generate_and_verify_sflj_table, run_simulation
from backend.analysis.stress_strain import virial_stress
from backend.models.schemas import InterventionType


def specimen(n=12, **kwargs):
    q=hex_lattice(n,n)
    return SpecimenInput(coordinates=q.tolist(), atom_ids=list(range(len(q))), protocol=Protocol(**kwargs))


def test_sflj_derivative_cutoff_and_near_limit():
    r=np.array([.91,1.017,1.123,1.61,2.49999]); h=1e-6
    u,f=sflj(r)
    np.testing.assert_allclose(f, -(sflj(r+h)[0]-sflj(r-h)[0])/(2*h), rtol=1e-7,atol=1e-8)
    assert sflj(2.5)==(0,0)
    assert abs(sflj(2.5-1e-8)[0])<1e-12 and abs(sflj(2.5-1e-8)[1])<1e-8


def test_arbitrary_coordinates_force_virial_against_independent_reference():
    q=np.array([[.02,.05],[1.19,.21],[.44,1.23],[1.66,1.51],[2.8,.14]])
    f,u,vir=forces(q); ref=np.zeros_like(q); vv=np.zeros((len(q),2,2)); energy=0.
    fc=24/2.5*(2/2.5**12-1/2.5**6)
    uc=4*(1/2.5**12-1/2.5**6)
    for i in range(len(q)):
        for j in range(i):
            d=q[i]-q[j]; r=np.linalg.norm(d)
            if r<2.5:
                pf=(24/r*(2/r**12-1/r**6)-fc)*d/r
                ref[i]+=pf; ref[j]-=pf
                vv[i]+=.5*np.outer(d,pf); vv[j]+=.5*np.outer(d,pf)
                energy+=4*(1/r**12-1/r**6)-uc+(r-2.5)*fc
    np.testing.assert_allclose(f,ref,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(vir,vv,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(f.sum(axis=0),0,atol=1e-12)
    assert u==pytest.approx(energy)
    changed=q.copy(); changed[2,1]+=1e-3
    f2,_,v2=forces(changed)
    assert not np.allclose(f,f2) and not np.allclose(vir,v2)
    for i in range(len(q)):
        for axis in range(2):
            a=q.copy(); b=q.copy(); a[i,axis]+=1e-6; b[i,axis]-=1e-6
            assert f[i,axis]==pytest.approx(-(forces(a)[1]-forces(b)[1])/(2e-6),rel=1e-7,abs=1e-7)


def test_tension_sign_and_grip_reaction_elastic():
    q=np.array([[0.,0.],[0.,1.25]])
    f,_,vv=forces(q)
    stress=virial_stress(np.zeros_like(q),vv,np.array([True,True]),1.)
    assert stress[1,1]>0 and f[0,1]>0
    q=hex_lattice(); q[:,1]*=1.03
    f,_,vv=forces(q)
    low=q[:,1]==q[:,1].min(); high=q[:,1]==q[:,1].max(); mobile=~(low|high)
    vir=virial_stress(np.zeros_like(q),vv,mobile,np.ptp(q[:,0])*np.ptp(q[:,1]))[1,1]
    reaction=(f[low,1].sum()-f[high,1].sum())/(2*np.ptp(q[:,0]))
    assert vir>0 and reaction>0
    assert abs(vir-reaction)/reaction<.3


def test_nve_500_step_total_energy_conservation():
    s=specimen(8,warmup_steps=500)
    q,v,_,_,mobile,_,_=prepare(s)
    _,_,drift,terminal=nve_window(q,v,mobile,steps=500)
    print('500-step NVE max/terminal drift:',drift,terminal)
    assert drift<1e-3


def test_offgrid_table_and_real_lammps_output(tmp_path):
    metrics=generate_and_verify_sflj_table(tmp_path/'sflj.table')
    print('SFLJ interpolation validation:',metrics)
    assert metrics['force_max_absolute_error']<2e-3
    if binary():
        assert metrics['lammps_pair_output_status']=='PASS'


@pytest.mark.skipif(binary() is None,reason='LAMMPS binary unavailable: actual pair output NOT_RUN')
def test_native_lammps_pair_parity():
    caps=engine_capabilities()
    assert caps['engine']=='LAMMPS_BINARY',caps
    assert caps['pair_validation']=='PASS'


def test_geometric_healing_changes_force_and_measured_response():
    s=specimen(8,max_strain=.2,warmup_steps=500)
    q=np.array(s.coordinates); center=np.linalg.norm(q-q.mean(axis=0),axis=1).argmin()
    q=np.delete(q,center,axis=0); s.coordinates=q.tolist(); s.atom_ids=list(range(len(q)))
    healed,trace=transform(s,InterventionType.HEAL_INTERIOR_VACANCY)
    assert trace['status']=='APPLIED' and len(healed.coordinates)>len(q)
    assert content_hash(s.model_dump())!=content_hash(healed.model_dump())
    old=forces(q)[0]; new=forces(np.array(healed.coordinates))[0][:len(q)]
    assert not np.allclose(old,new)
    a=run_simulation(s); b=run_simulation(healed)
    print('Actual healing effect (may be censored):',a.peak_stress,b.peak_stress,a.failure_strain,b.failure_strain)
    assert not np.allclose([p['stress'] for p in a.stress_strain_curve],[p['stress'] for p in b.stress_strain_curve])


def test_driven_numpy_valid_reproducible_and_censored():
    s=specimen(6,max_strain=.03,warmup_steps=500)
    a=run_simulation(s,force_numpy=True); b=run_simulation(s,force_numpy=True)
    assert a.numerical_check.is_valid,a.numerical_check
    assert a.sim_id==b.sim_id and a.stress_strain_curve==b.stress_strain_curve
    assert a.failure_strain is None and a.outcome=='NOT_FRACTURED_WITHIN_HORIZON'


def test_worker_timeout_terminates_process():
    from backend.simulation.worker import run_bounded
    result=run_bounded(specimen(),timeout=.01)
    assert result.outcome=='EXECUTION_FAILED' and result.error_code=='RUN_TIMEOUT'
    assert result.wall_time_sec<5
