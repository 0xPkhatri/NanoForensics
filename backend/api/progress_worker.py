"""Fixed worker entrypoints with observational instrumentation only."""
import importlib
import sys
from backend.api.progress_observer import observed_class
from backend.api.progress import activity, emit

WORKERS = {
    'backend.api.job_worker': ('Store', 'NanoForensicsInvestigator'),
    'backend.demonstration.job_worker': ('Store', 'DemonstrationInvestigator'),
    'backend.live_muse.job_worker': ('DemonstrationStore', 'LiveMuseInvestigator'),
}


def run(module_name, path, job_id):
    store_name, scientist_name = WORKERS[module_name]
    module = importlib.import_module(module_name)
    store = getattr(module, store_name)(path)
    original = getattr(module, scientist_name)
    setattr(module, scientist_name, observed_class(original, job_id, live=module_name == 'backend.live_muse.job_worker'))
    try:
        module.run(store, job_id)
    except Exception as exc:
        # Avoid spilling arbitrary exception payloads or provider secrets into telemetry.
        history = activity(store, store.job(job_id)['case_id']).events
        phase = history[-1].phase if history else 'worker'
        emit(store, job_id, phase, 'failed', 'Worker operation failed', error_code=type(exc).__name__)
        store.update_job(job_id, error=f'{type(exc).__name__}: worker operation failed')
        raise
    finally:
        setattr(module, scientist_name, original)


if __name__ == '__main__':
    run(*sys.argv[1:4])
