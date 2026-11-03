"""Independent empirical rules: no access to preparation or specimen labels."""
from backend.models.schemas import VerificationResult, HypothesisStatus, InterventionType
from backend.analysis.comparison import paired_statistics
from backend.simulation.experiment_validator import validate


def verify(proposal, baseline, counterfactual, predicts_recovery=True, competing_effect=False):
    stats = paired_statistics(baseline, counterfactual)
    numeric = len(baseline)>=3 and len(counterfactual)>=3 and all(validate(r) and r.outcome != 'EXECUTION_FAILED' for r in baseline+counterfactual)
    status = 'COMPLETE' if numeric else 'EXECUTION_FAILED'
    verdict = HypothesisStatus.PENDING
    explanation = 'Numerical or execution failure: no scientific verdict assigned.'
    if numeric:
        if len(stats['uncensored_seeds']) < 3:
            status='INSUFFICIENT_UNCENSORED_PAIRS'
            explanation='Right-censored outcomes: no naive failure-strain mean or causal recovery claim. Extend the loading horizon or collect more evidence.'
        elif proposal.intervention == InterventionType.REPEAT_REPLICATE_SEEDS:
            verdict=HypothesisStatus.INCONCLUSIVE
            explanation='Replicate-only diagnostic quantifies variance and cannot establish a causal repair.'
        else:
            verdict=HypothesisStatus.INCONCLUSIVE
            if stats['cv'] <= 12:
                if (stats['snr']>=2.5 and stats['recovery']>=18) or (proposal.intervention==InterventionType.NORMALIZE_STRAIN_RATE and stats['stress_shift']<=-12 and stats['stress_snr']>=2.5 and stats['shift']>=0):
                    verdict=HypothesisStatus.SUPPORTED
                elif predicts_recovery and not competing_effect and stats['snr']<1.2 and abs(stats['recovery'])<8:
                    verdict=HypothesisStatus.REJECTED
            explanation=f"Measured paired recovery {stats['recovery']:.2f}%, paired SNR {stats['snr']:.2f}, CV {stats['cv']:.2f}%. Three pairs provide descriptive evidence. Signs and censoring are preserved."
    b=baseline[0]; c=counterfactual[0]
    return VerificationResult(experiment_id=proposal.experiment_id, hypothesis_id=proposal.target_hypothesis_id, intervention=proposal.intervention, matched_seeds_used=stats['seeds'], baseline_failure_strain=stats.get('baseline_mean'), counterfactual_failure_strain=stats.get('counterfactual_mean'), strain_recovery_pct=stats.get('recovery'), replicate_std_pct=stats.get('std_pct',0.), signal_to_noise_ratio=stats.get('snr',0.), baseline_peak_stress=sum(r.peak_stress for r in baseline)/len(baseline), counterfactual_peak_stress=sum(r.peak_stress for r in counterfactual)/len(counterfactual), stress_shift_pct=stats.get('stress_shift'), baseline_crack_region=b.crack_initiation_region, counterfactual_crack_region=c.crack_initiation_region, numerical_consistency_passed=numeric, verdict=verdict, execution_status=status, scientific_explanation=explanation, paired_mean_shift=stats.get('shift'), paired_std=stats.get('paired_std'), cv_pct=stats.get('cv'), stress_snr=stats.get('stress_snr'), censoring_counts={'baseline':stats['baseline_censored'],'counterfactual':stats['counterfactual_censored']}, baseline_result_ids=[r.sim_id for r in baseline], counterfactual_result_ids=[r.sim_id for r in counterfactual])
