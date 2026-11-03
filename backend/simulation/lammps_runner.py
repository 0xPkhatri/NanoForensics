"""Verified external LAMMPS path. Unsupported/invalid potential fails closed to NumPy."""
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from functools import lru_cache
import numpy as np
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from backend.simulation.numpy_md_fallback import sflj, prepare, summarize, run_numpy


def binary():
    return shutil.which('lmp') or shutil.which('lmp_serial')


def _execute(exe, text, directory, timeout=30):
    path = Path(directory)/'run.in'
    path.write_text(text)
    result = subprocess.run([exe, '-in', str(path), '-log', 'none'], cwd=directory, capture_output=True, text=True, timeout=timeout)
    if result.returncode or 'ERROR' in result.stdout:
        raise RuntimeError((result.stdout+result.stderr)[-2500:])
    return result.stdout


def error_metrics(r, u, f):
    au, af = sflj(r)
    return {'minimum_sampled_distance':float(r.min()), 'energy_max_absolute_error':float(np.max(abs(u-au))), 'force_max_absolute_error':float(np.max(abs(f-af))), 'energy_scale_relative_error':float(np.max(abs(u-au))/max(np.max(abs(au)), 1e-10)), 'force_scale_relative_error':float(np.max(abs(f-af))/max(np.max(abs(af)), 1e-10))}


def generate_and_verify_sflj_table(path, r_min_valid=.8, points=5000, absolute_tolerance=2e-3, relative_tolerance=2e-5, verify_lammps=True):
    path = Path(path).resolve()
    for _ in range(6):
        r = np.linspace(r_min_valid, 2.5, points)
        u, f = sflj(r)
        probes = r[:-1]+np.diff(r)*.371
        metrics = error_metrics(probes, np.interp(probes, r, u), np.interp(probes, r, f))
        if metrics['force_max_absolute_error'] <= absolute_tolerance and metrics['energy_max_absolute_error'] <= absolute_tolerance and metrics['force_scale_relative_error'] <= relative_tolerance and metrics['energy_scale_relative_error'] <= relative_tolerance:
            break
        points *= 2
    else:
        raise ValueError('SFLJ table insufficiently accurate')
    np.savetxt(path, np.column_stack([np.arange(1, points+1), r, u, f]), header=f'SFLJ\nN {points} R {r_min_valid} 2.5\n', comments='', fmt=['%d','%.17g','%.17g','%.17g'])
    metrics.update(points=points, lammps_pair_output_status='NOT_RUN')
    if verify_lammps and binary():
        actual = verify_pair_output(binary(), f'pair_style table linear {points}\npair_coeff * * {path} SFLJ 2.5', r_min_valid)
        if actual['force_max_absolute_error'] > absolute_tolerance or actual['energy_max_absolute_error'] > absolute_tolerance or actual['force_scale_relative_error'] > relative_tolerance or actual['energy_scale_relative_error'] > relative_tolerance:
            if points >= 320000:
                raise ValueError(f'realized LAMMPS table failed: {actual}')
            return generate_and_verify_sflj_table(path, r_min_valid, points*2, absolute_tolerance, relative_tolerance, verify_lammps)
        metrics['lammps_pair_output_status'] = 'PASS'
        metrics['lammps_actual'] = actual
    return metrics


def verify_pair_output(exe, style, minimum=.8):
    with tempfile.TemporaryDirectory(prefix='nf-pair-') as tmp:
        _execute(exe, f'''units lj
atom_style atomic
boundary f f f
region box block -5 5 -5 5 -5 5
create_box 1 box
mass 1 1
{style}
pair_write 1 1 271 r {minimum+.000013} 2.5 pair.out CHECK
''', tmp)
        rows = []
        for line in (Path(tmp)/'pair.out').read_text().splitlines():
            fields = line.split()
            if len(fields)==4:
                try:
                    rows.append([float(x) for x in fields])
                except ValueError:
                    pass
        arr = np.array(rows)
        return error_metrics(arr[:, 1], arr[:, 2], arr[:, 3])


@lru_cache(maxsize=1)
def engine_capabilities():
    exe = binary()
    if not exe:
        return {'engine':'NUMPY_VELOCITY_VERLET_2D', 'reason':'LAMMPS unavailable', 'pair_validation':'NOT_RUN'}
    try:
        help_text = subprocess.run([exe, '-h'], capture_output=True, text=True, timeout=8).stdout
        native = 'lj/smooth/linear' in help_text.split()
        if native:
            errors = verify_pair_output(exe, 'pair_style lj/smooth/linear 2.5\npair_coeff * * 1.0 1.0')
            if max(errors['force_max_absolute_error'], errors['energy_max_absolute_error']) > 1e-8:
                raise ValueError(f'native output mismatch {errors}')
            return {'engine':'LAMMPS_BINARY','binary':exe,'style':'lj/smooth/linear','pair_validation':'PASS','pair_errors':errors, 'version':help_text.splitlines()[1:3]}
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_and_verify_sflj_table(Path(tmp)/'sflj.table')
        return {'engine':'LAMMPS_BINARY','binary':exe,'style':'table','pair_validation':'PASS','pair_errors':result}
    except (ValueError, RuntimeError, subprocess.SubprocessError, OSError) as exc:
        return {'engine':'NUMPY_VELOCITY_VERLET_2D', 'reason':str(exc), 'pair_validation':'FAIL'}


def run_simulation(specimen, force_numpy=False):
    caps = engine_capabilities()
    if force_numpy or caps['engine'] != 'LAMMPS_BINARY':
        result = run_numpy(specimen)
        result.diagnostics['engine_selection'] = caps
        return result
    started = time.perf_counter()
    q, v, bottom, top, mobile, _, diagnostics = prepare(specimen)
    p = specimen.protocol
    gauge = float(q[top, 1].mean()-q[bottom, 1].mean())
    nsteps = int(np.ceil(p.max_strain/(p.strain_rate*p.dt)))
    # Real IDs are mapped to contiguous execution IDs; public observable IDs retained.
    with tempfile.TemporaryDirectory(prefix='nf-md-') as tmp:
        root = Path(tmp)
        lines = ['NanoForensics immutable input', '', f'{len(q)} atoms', '1 atom types', '', f'{q[:,0].min()-20} {q[:,0].max()+20} xlo xhi', f'{q[:,1].min()-30} {q[:,1].max()+30} ylo yhi', '-0.5 0.5 zlo zhi', '', 'Masses', '', '1 1', '', 'Atoms # atomic', '']
        lines += [f'{i+1} 1 {x:.17g} {y:.17g} 0' for i, (x, y) in enumerate(q)]
        lines += ['', 'Velocities', '']+[f'{i+1} {vx:.17g} {vy:.17g} 0' for i, (vx, vy) in enumerate(v)]
        (root/'atoms.data').write_text('\n'.join(lines)+'\n')
        if caps['style'] == 'table':
            table = generate_and_verify_sflj_table(root/'sflj.table')
            style = f"pair_style table linear {table['points']}\npair_coeff * * sflj.table SFLJ 2.5"
        else:
            style = 'pair_style lj/smooth/linear 2.5\npair_coeff * * 1.0 1.0'
        env = Environment(loader=FileSystemLoader(Path(__file__).parent/'input_templates'), undefined=StrictUndefined)
        text = env.get_template('tensile_2d_lj.in.j2').render(style=style, bottom=' '.join(str(i+1) for i in np.flatnonzero(bottom)), top=' '.join(str(i+1) for i in np.flatnonzero(top)), speed=.5*gauge*p.strain_rate, dt=p.dt, temperature=p.temperature, damp=1/max(p.gamma,1e-12), seed=p.seed, sample=p.sample_every, steps=nsteps, thermostat=p.gamma > 0)
        _execute(caps['binary'], text, tmp, timeout=30)
        frames = []
        with (root/'trajectory.dump').open() as f:
            while f.readline():
                k = int(f.readline()); f.readline(); n=int(f.readline())
                for _ in range(5):
                    f.readline()
                data = np.array([[float(x) for x in f.readline().split()] for _ in range(n)])
                data = data[np.argsort(data[:, 0])]
                frames.append((k, data[:, 1:3], data[:, 3:5]))
        if frames[-1][0] != nsteps:
            data = np.loadtxt(root/'last.dump', skiprows=9, ndmin=2)
            data = data[np.argsort(data[:,0])]
            frames.append((nsteps, data[:,1:3], data[:,3:5]))
        bounds = np.loadtxt(root/'bounds.dat', comments='#', ndmin=2)
        diagnostics.update(max_step_displacement=float(bounds[:,2].max()), max_force_all_steps=float(bounds[:,1].max()), displacement_check='conservative per-step speed*dt + half force*dt² bound, measured every step', engine_selection=caps)
    return summarize(specimen, frames, mobile, bottom, top, diagnostics, started, 'LAMMPS_BINARY')
