"""Real pairwise SFLJ and velocity-Verlet/BAOAB. No case identities enter here."""
import hashlib
import json
import time
from functools import lru_cache
import numpy as np
from scipy.optimize import minimize
from backend.models.schemas import SpecimenInput, SimulationSummary, NumericalConsistencyCheck, AtomSnapshot
from backend.analysis.structure_analysis import reference_graph, rupture, localize
from backend.analysis.stress_strain import virial_stress, detect_fracture


def content_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def sflj(r, epsilon=1., sigma=1., cutoff=2.5):
    r = np.asarray(r, float)
    rc = cutoff*sigma
    if np.any(r <= 0):
        raise ValueError('overlapping atoms or non-positive radius')
    x = (sigma/r)**6
    xc = (sigma/rc)**6
    uc = 4*epsilon*(xc*xc-xc)
    fc = 24*epsilon/rc*(2*xc*xc-xc)
    u = 4*epsilon*(x*x-x) - uc + (r-rc)*fc
    f = 24*epsilon/r*(2*x*x-x) - fc
    return np.where(r < rc, u, 0.), np.where(r < rc, f, 0.)


@lru_cache(maxsize=16)
def pairs(n):
    return np.triu_indices(n, 1)


def forces(q):
    q = np.asarray(q, float)
    i, j = pairs(len(q))
    # Broadcasting over pair indices, no Python pair loops in production.
    d = q[i] - q[j]
    r = np.linalg.norm(d, axis=1)
    if not np.isfinite(r).all() or np.any(r < .65):
        raise ValueError('invalid close approach (<0.65 sigma) or nonfinite coordinates')
    selected = r < 2.5
    i, j, d, r = i[selected], j[selected], d[selected], r[selected]
    u, f = sflj(r)
    pf = d*(f/r)[:, None]
    force = np.column_stack([np.bincount(i, weights=pf[:, k], minlength=len(q))-np.bincount(j, weights=pf[:, k], minlength=len(q)) for k in range(2)])
    vv = d[:, :, None]*pf[:, None, :]/2
    virial = np.empty((len(q), 2, 2))
    for a in range(2):
        for b in range(2):
            virial[:, a, b] = np.bincount(i, weights=vv[:, a, b], minlength=len(q))+np.bincount(j, weights=vv[:, a, b], minlength=len(q))
    return force, float(u.sum()), virial


def grip_masks(q):
    low, high = q[:, 1].min(), q[:, 1].max()
    bottom, top = q[:, 1] < low+.3, q[:, 1] > high-.3
    return bottom, top, ~(bottom | top)


def relax(q, mobile, tolerance=.005):
    fixed = q.copy()
    def fun(flat):
        work = fixed.copy()
        work[mobile] = flat.reshape(-1, 2)
        f, u, _ = forces(work)
        return u, -f[mobile].ravel()
    result = minimize(fun, q[mobile].ravel(), jac=True, method='L-BFGS-B', options={'maxiter': 2000, 'gtol': tolerance/3, 'ftol': 1e-14, 'maxls': 50})
    fixed[mobile] = result.x.reshape(-1, 2)
    residual = float(np.linalg.norm(forces(fixed)[0][mobile], axis=1).max())
    if residual > tolerance:
        raise ValueError(f'minimization failed: residual {residual:.6g} > {tolerance}')
    return fixed, residual


def step(q, v, mobile, dt, rng=None, temperature=0., gamma=0., grip_delta=None, stats=None):
    # BAOAB: B half kick, A half drift, O exact OU, A half drift, B half kick.
    f, _, _ = forces(q)
    v[mobile] += .5*dt*f[mobile]
    q[mobile] += .5*dt*v[mobile]
    if gamma:
        decay = np.exp(-gamma*dt)
        v[mobile] = decay*v[mobile] + np.sqrt(temperature*(1-decay**2))*rng.standard_normal((mobile.sum(), 2))
    q[mobile] += .5*dt*v[mobile]
    if grip_delta is not None:
        q[~mobile] += grip_delta[~mobile]
    f, _, _ = forces(q)
    v[mobile] += .5*dt*f[mobile]
    if stats is not None:
        stats['max_force_all_steps']=max(stats.get('max_force_all_steps',0.),float(np.linalg.norm(f,axis=1).max()))
    return q, v


def nve_window(q, v, mobile, dt=.002, steps=50):
    energies = []
    for _ in range(steps+1):
        energies.append(forces(q)[1] + .5*float((v[mobile]**2).sum()))
        if len(energies) <= steps:
            step(q, v, mobile, dt)
    drift = np.abs(np.array(energies)-energies[0])/max(abs(energies[0]), 1e-10)
    return q, v, float(drift.max()), float(drift[-1])


def prepare(specimen):
    p = specimen.protocol
    q = np.array(specimen.coordinates, float)
    bottom, top, mobile = grip_masks(q)
    q, residual = relax(q, mobile, p.minimize_tolerance)
    rng = np.random.Generator(np.random.PCG64(p.seed))
    v = np.zeros_like(q)
    v[mobile] = rng.normal(0, np.sqrt(p.temperature), (mobile.sum(), 2))
    v[mobile] -= v[mobile].mean(axis=0)
    temps = []
    for k in range(p.warmup_steps):
        step(q, v, mobile, p.dt, rng, p.temperature, p.gamma)
        if k >= p.warmup_steps//2:
            temps.append(float((v[mobile]**2).sum())/(2*mobile.sum()))
    q, v, drift, terminal = nve_window(q, v, mobile, p.dt, p.nve_steps)
    return q, v, bottom, top, mobile, rng, {'minimization_residual': residual, 'nve_max_drift': drift, 'nve_terminal_drift': terminal, 'warmup_temperature_mean': float(np.mean(temps)) if temps else p.temperature, 'warmup_steps': p.warmup_steps}


def summarize(specimen, frames, mobile, bottom, top, diagnostics, started, engine):
    p = specimen.protocol
    ref = frames[0][1].copy()
    graph = reference_graph(ref)
    gauge = float(ref[top, 1].mean()-ref[bottom, 1].mean())
    width = float(np.ptp(ref[:, 0]))
    snapshots, clusters, temps, reactions = [], [], [], []
    thermal_series=[]
    force_balance_series=[]
    from backend.analysis.force_balance import force_moment_balance
    from backend.analysis.thermal_diagnostics import kinetic_diagnostics
    maxforce, maxdisp, minimum = 0., 0., 10.
    last_q = ref
    for frame in frames:
        k,q,v=frame[:3]
        realized_force=frame[3] if len(frame)>3 else None
        f, u, vir = forces(q)
        z, loss, _, groups = rupture(q, graph, mobile)
        # measured strain is grip separation, not timestep-displacement confusion.
        strain = float((q[top, 1].mean()-q[bottom, 1].mean())/gauge-1)
        area = width*gauge*(1+strain)
        stress = float(virial_stress(v, vir, mobile, area)[1, 1])
        atom = np.column_stack([specimen.atom_ids, q, z, loss, -vir[:, 1, 1]])
        snapshots.append(AtomSnapshot(timestep=k, strain=strain, stress_yy=stress, potential_energy=u, kinetic_energy=.5*float((v[mobile]**2).sum()), atoms=atom.tolist()))
        clusters.append(groups)
        thermal_series.append(kinetic_diagnostics(q,v,mobile,bottom,top,gauge,p.strain_rate))
        force_balance_series.append(force_moment_balance(q,v,f,vir,mobile,bottom,top,area,realized_force))
        temps.append(float((v[mobile]**2).sum())/(2*mobile.sum()))
        reactions.append(float((f[bottom, 1].sum()-f[top, 1].sum())/(2*width)))
        maxforce = max(maxforce, float(np.linalg.norm(f, axis=1).max()))
        if k:
            maxdisp = max(maxdisp, float(np.linalg.norm(q-last_q, axis=1).max())/p.sample_every)
        last_q = q
        ii, jj = pairs(len(q))
        minimum = min(minimum, float(np.linalg.norm(q[ii]-q[jj], axis=1).min()))
    stresses = [s.stress_yy for s in snapshots]
    peak, fail, cluster = detect_fracture(stresses, clusters)
    terr = abs(float(np.mean(temps))-p.temperature)/max(p.temperature, .01)
    maxforce = max(maxforce, diagnostics.get('max_force_all_steps',0.))
    maxdisp = diagnostics.get('max_step_displacement',maxdisp)
    gates={
        'preload_nve_drift':{'measured':diagnostics['nve_max_drift'],'upper_bound':.001,'units':'relative total-energy drift'},
        'force':{'measured':maxforce,'upper_bound':1e4,'units':'LJ force'},
        'step_displacement':{'measured':maxdisp,'upper_bound':.1,'units':'sigma'},
        'driven_laboratory_temperature':{'measured':terr,'upper_bound':.35,'units':'relative target-temperature error'},
    }
    for gate in gates.values():gate['passed']=bool(gate['measured']<gate['upper_bound'])
    failed_gates=[name for name,gate in gates.items() if not gate['passed']]
    diagnostics['validity_gates']=gates
    valid=not failed_gates
    check = NumericalConsistencyCheck(is_valid=bool(valid), max_force_norm=maxforce, max_step_displacement=diagnostics.get('max_step_displacement', maxdisp), thermostat_temperature_error_ratio=terr, energy_drift_ratio=diagnostics['nve_max_drift'], nan_detected=False, fracture_criterion_met=fail is not None, notes='No external work in pre-load NVE. Temperature: time-mean mobile kinetic DOF. Stress: tensile positive, negative pressure tensor. Displacement is measured each integrator step when available; sampled estimate otherwise.')
    curve = [{'strain': s.strain, 'stress': s.stress_yy, 'stress_std': 0.} for s in snapshots]
    outcome = 'EXECUTION_FAILED' if not valid else 'FRACTURED' if fail is not None else 'NOT_FRACTURED_WITHIN_HORIZON'
    diagnostics['force_balance']={'analysis_version':'force-moment-1','series':force_balance_series,'max_identity_residual':max(abs(row['identity_residual']) for row in force_balance_series)}
    diagnostics['thermal_diagnostics']={'analysis_version':'kinematic-1','gate_unchanged':'laboratory kinetic temperature; error <0.35','series':thermal_series,'means':{key:float(np.mean([row[key] for row in thermal_series])) for key in thermal_series[0]}}
    diagnostics.update(minimum_sampled_distance=minimum, grip_reaction_traction=reactions, mobile_temperature_series=temps, raw_sample_count=len(frames), stress_smoothing='centered 3-sample mean; replicated endpoints', fracture_assignment='first qualifying frame confirmed across three measurements', thermostat='NumPy BAOAB during common warmup; '+('LAMMPS Langevin + NVE during loading' if engine=='LAMMPS_BINARY' else 'BAOAB during loading'), cross_engine_ensemble='NOT_RUN')
    return SimulationSummary(sim_id=content_hash({'input': specimen.model_dump(), 'engine': engine, 'version':'sflj-1.1'})[:24], seed=p.seed, peak_stress=float(max(stresses)), failure_strain=snapshots[fail].strain if fail is not None and valid else None, toughness=float(np.trapezoid(stresses, [s.strain for s in snapshots])), crack_initiation_region=localize(cluster, ref), mean_coordination_at_peak=float(np.mean(np.array(snapshots[peak].atoms)[mobile, 3])), max_bond_loss_cluster_size=max((len(c) for gs in clusters for c in gs), default=0), min_coordination_region=localize(cluster, ref), stress_strain_curve=curve, snapshots=[snapshots[0], snapshots[peak], snapshots[fail if fail is not None else -1]], numerical_check=check, wall_time_sec=time.perf_counter()-started, engine_used=engine, outcome=outcome, max_observed_strain=snapshots[-1].strain, effective_gauge_length=gauge, reference_geometry={'width':width,'gauge':gauge,'reference_coordinates':ref.tolist(),'reference_neighbor_cutoff':1.35*2**(1/6)}, measurement_horizon={'steps':frames[-1][0], 'lj_time':frames[-1][0]*p.dt, 'target_strain':p.max_strain}, protocol_hash=content_hash(p.model_dump()), initial_configuration_hash=content_hash({'coordinates':specimen.coordinates,'atom_ids':specimen.atom_ids}), diagnostics=diagnostics, error_code=None if valid else 'NUMERICAL_VALIDITY_GATE', error_message=None if valid else 'Failed validity gates: '+', '.join(failed_gates))


def run_numpy(specimen: SpecimenInput):
    started = time.perf_counter()
    q, v, bottom, top, mobile, rng, diagnostics = prepare(specimen)
    p = specimen.protocol
    gauge = q[top, 1].mean()-q[bottom, 1].mean()
    delta = np.zeros_like(q)
    delta[top, 1], delta[bottom, 1] = .5*gauge*p.strain_rate*p.dt, -.5*gauge*p.strain_rate*p.dt
    frames = [(0, q.copy(), v.copy())]
    steps = int(np.ceil(p.max_strain/(p.strain_rate*p.dt)))
    maxdisp = 0.
    stats={}
    for k in range(1, steps+1):
        old = q.copy()
        step(q, v, mobile, p.dt, rng, p.temperature, p.gamma, delta, stats)
        maxdisp = max(maxdisp, float(np.linalg.norm(q-old, axis=1).max()))
        if k%p.sample_every == 0 or k == steps:
            frames.append((k, q.copy(), v.copy()))
    diagnostics.update(stats)
    diagnostics['max_step_displacement'] = maxdisp
    return summarize(specimen, frames, mobile, bottom, top, diagnostics, started, 'NUMPY_VELOCITY_VERLET_2D')
