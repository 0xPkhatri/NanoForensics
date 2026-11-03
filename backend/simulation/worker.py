"""Terminable process boundary used for every interactive simulation replicate."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import psutil
from backend.config import ROOT, RUN_TIMEOUT
from backend.models.schemas import SpecimenInput, SimulationSummary, NumericalConsistencyCheck
from backend.simulation.numpy_md_fallback import content_hash


def kill_tree(pid):
    try:
        parent=psutil.Process(pid)
        children=parent.children(recursive=True)
        for p in reversed(children):
            try: p.kill()
            except psutil.NoSuchProcess: pass
        parent.kill()
        psutil.wait_procs(children+[parent],timeout=3)
    except psutil.NoSuchProcess:
        pass


def failed(specimen, code, message, elapsed):
    return SimulationSummary(sim_id=content_hash({'input':specimen.model_dump(),'failed':code,'time':time.time_ns()})[:24],seed=specimen.protocol.seed, peak_stress=0, toughness=0, crack_initiation_region='distributed',mean_coordination_at_peak=0,min_coordination_region='distributed',stress_strain_curve=[],snapshots=[],outcome='EXECUTION_FAILED',numerical_check=NumericalConsistencyCheck(is_valid=False,max_force_norm=0,max_step_displacement=0,thermostat_temperature_error_ratio=0,energy_drift_ratio=0,nan_detected=False,fracture_criterion_met=False,notes='No valid measurements; numerical zero placeholders must not enter statistics.'),wall_time_sec=elapsed,engine_used='NO_VALID_EXECUTION',error_code=code,error_message=message,protocol_hash=content_hash(specimen.protocol.model_dump()),initial_configuration_hash=content_hash(specimen.coordinates))


def run_bounded(specimen, timeout=None, force_numpy=False):
    started=time.perf_counter()
    temp_root=Path(os.getenv('NANO_TMP_ROOT',str(ROOT/'runtime/tmp')))
    temp_root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temp_root,prefix='run-') as tmp:
        inp,out=Path(tmp)/'input.json',Path(tmp)/'output.json'
        inp.write_text(specimen.model_dump_json())
        proc=subprocess.Popen([sys.executable,'-m','backend.simulation.worker',str(inp),str(out)]+(['--numpy'] if force_numpy else []),cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env={**os.environ,'TMPDIR':str(tmp)})
        try:
            _,stderr=proc.communicate(timeout=RUN_TIMEOUT if timeout is None else timeout)
            if proc.returncode or not out.exists():
                return failed(specimen,'WORKER_ERROR',stderr.decode()[-2000:],time.perf_counter()-started)
            result=SimulationSummary.model_validate_json(out.read_text())
            result.diagnostics['worker_pid']=proc.pid
            result.diagnostics['worker_wall_time_sec']=time.perf_counter()-started
            return result
        except subprocess.TimeoutExpired:
            kill_tree(proc.pid); proc.communicate()
            return failed(specimen,'RUN_TIMEOUT','Terminated and reaped simulation worker and descendants',time.perf_counter()-started)
        finally:
            if proc.poll() is None:
                kill_tree(proc.pid); proc.wait()


if __name__=='__main__':
    from backend.simulation.lammps_runner import run_simulation
    spec=SpecimenInput.model_validate_json(Path(sys.argv[1]).read_text())
    started=time.perf_counter()
    try:
        result=run_simulation(spec,force_numpy='--numpy' in sys.argv[3:])
    except Exception as exc:
        result=failed(spec,'SOLVER_ERROR',str(exc),time.perf_counter()-started)
    Path(sys.argv[2]).write_text(result.model_dump_json())
