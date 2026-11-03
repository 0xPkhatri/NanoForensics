import numpy as np
from backend.models.schemas import SimulationOutcome
from backend.simulation.numpy_md_fallback import content_hash


def paired_statistics(baseline, counterfactual):
    b = {r.seed:r for r in baseline}
    c = {r.seed:r for r in counterfactual}
    seeds = sorted(b.keys() & c.keys())
    usable = [s for s in seeds if b[s].outcome != 'EXECUTION_FAILED' and c[s].outcome != 'EXECUTION_FAILED' and b[s].numerical_check.is_valid and c[s].numerical_check.is_valid]
    uncensored = [s for s in usable if b[s].failure_strain is not None and c[s].failure_strain is not None]
    stats = {'seeds':seeds, 'valid_seeds':usable, 'uncensored_seeds':uncensored, 'baseline_censored':sum(b[s].failure_strain is None for s in usable), 'counterfactual_censored':sum(c[s].failure_strain is None for s in usable)}
    if len(uncensored) >= 3:
        x=np.array([b[s].failure_strain for s in uncensored]); y=np.array([c[s].failure_strain for s in uncensored]); d=y-x
        std=float(d.std(ddof=1)); pooled=float(np.sqrt(x.var(ddof=1)+y.var(ddof=1)+.004**2))
        stats.update(baseline_mean=float(x.mean()), counterfactual_mean=float(y.mean()), shift=float(d.mean()), paired_std=std, recovery=float(100*d.mean()/x.mean()), snr=float(abs(d.mean())/np.sqrt(std**2+.004**2)), unpaired_snr=float(abs(d.mean())/pooled), cv=float(100*max(x.std(ddof=1)/x.mean(), y.std(ddof=1)/y.mean())), std_pct=float(100*std/x.mean()))
    if len(usable) >= 3:
        x=np.array([b[s].peak_stress for s in usable]); y=np.array([c[s].peak_stress for s in usable]); d=y-x
        stats.update(stress_shift=float(100*d.mean()/max(abs(x.mean()),1e-8)), stress_snr=float(abs(d.mean())/np.sqrt(d.var(ddof=1)+.004**2)))
    return stats


def aggregate(runs):
    if not runs: raise ValueError('No executed replicates')
    valid=[r for r in runs if r.outcome!=SimulationOutcome.EXECUTION_FAILED and r.numerical_check.is_valid]
    out=(valid[0] if valid else runs[0]).model_copy(deep=True)
    out.sim_id=content_hash({'aggregate_result_ids':[r.sim_id for r in runs]})[:24]
    out.replicate_seeds=[r.seed for r in runs]
    out.replicate_results=[r.model_dump(mode='json') for r in runs]
    out.wall_time_sec=sum(r.wall_time_sec for r in runs)
    out.diagnostics['aggregate_description']='Only valid runs contribute to means/envelopes; raw failed runs retained and condition marked failed; snapshots from first valid replicate when available.'
    out.diagnostics['valid_replicate_count']=len(valid)
    out.diagnostics['failed_replicate_count']=len(runs)-len(valid)
    if valid:
        out.peak_stress=float(np.mean([r.peak_stress for r in valid]))
        out.peak_stress_std=float(np.std([r.peak_stress for r in valid],ddof=1)) if len(valid)>1 else 0.
        for point in out.stress_strain_curve:
            measured=[r for r in valid if r.stress_strain_curve]
            values=[np.interp(point['strain'],[p['strain'] for p in r.stress_strain_curve],[p['stress'] for p in r.stress_strain_curve]) for r in measured]
            point['stress']=float(np.mean(values));point['stress_std']=float(np.std(values,ddof=1)) if len(values)>1 else 0.
    if len(valid)==len(runs) and all(r.failure_strain is not None for r in valid):
        out.failure_strain=float(np.mean([r.failure_strain for r in valid]))
        out.failure_strain_std=float(np.std([r.failure_strain for r in valid],ddof=1)) if len(valid)>1 else 0.
    else:
        out.failure_strain=None
    if len(valid)<len(runs):
        out.outcome=SimulationOutcome.EXECUTION_FAILED
        out.numerical_check.is_valid=False
        out.error_code='REPLICATE_EXECUTION_FAILED'
        out.error_message=f'{len(runs)-len(valid)} failed replicates excluded from means; no complete condition-level comparison'
    elif any(r.failure_strain is None for r in valid):
        out.outcome=SimulationOutcome.NOT_FRACTURED_WITHIN_HORIZON
    return out
