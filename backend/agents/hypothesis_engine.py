from backend.models.schemas import Hypothesis, DefectType, InterventionType
from backend.simulation.defect_generator import infer_missing_sites

PAIRS=[(DefectType.INTERIOR_VACANCY,InterventionType.HEAL_INTERIOR_VACANCY,'Interior missing-site stress concentration'),(DefectType.SURFACE_NOTCH,InterventionType.SMOOTH_SURFACE_NOTCH,'Edge geometry stress concentration'),(DefectType.HIGH_STRAIN_RATE,InterventionType.NORMALIZE_STRAIN_RATE,'Inertial loading response'),(DefectType.THERMAL_SOFTENING,InterventionType.NORMALIZE_TEMPERATURE,'Thermal rupture variability')]


def fallback_hypotheses(public,provenance=None):
    q=public.observed_configuration['coordinates']
    interior=len(infer_missing_sites(q,True));edge=len(infer_missing_sites(q,False))
    out=[]
    for k,(cause,intervention,title) in enumerate(PAIRS):
        obs=[f'Visible geometric candidate sites: interior={interior}, edge={edge}.',f'Measured crack region: {public.baseline_simulation.crack_initiation_region}.', f'Baseline outcome: {public.baseline_simulation.outcome}.']
        out.append(Hypothesis(id=f'H{k+1}',title=title,mechanism='Local topology, inertia or thermal motion may alter emergent bond rupture; requires an isolated counterfactual.',suspected_cause=cause,supporting_evidence=obs,missing_evidence='Three numerically valid, uncensored matched-seed intervention pairs.',proposed_intervention=intervention,predicted_strain_recovery_pct=20,confidence=.25,status='PENDING',provenance=provenance or {}))
    return out


def update_from_verification(hypotheses,result):
    for h in hypotheses:
        if h.id==result.hypothesis_id:
            h.status=result.verdict
            h.supporting_evidence.append(result.scientific_explanation)
            h.confidence=.7 if result.verdict=='SUPPORTED' else .1 if result.verdict=='REJECTED' else .25
    return hypotheses
