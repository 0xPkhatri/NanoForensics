import uuid
from backend.models.schemas import ExperimentProposal
from backend.config import SEEDS
from backend.simulation.defect_generator import infer_missing_sites


def plan(public,hypotheses,remaining_budget,mode,provenance,ranking=None,estimated_run_cost=3):
    proposals=[]
    ranks=ranking or [h.proposed_intervention for h in hypotheses]
    for h in hypotheses:
        cost=estimated_run_cost*6
        if cost>remaining_budget: continue
        gain=1.-.12*ranks.index(h.proposed_intervention) if h.proposed_intervention in ranks else .3
        # Geometric target availability is a measured feature shared with comparators.
        target=True
        if h.proposed_intervention.value in ['heal_interior_vacancy','smooth_surface_notch']:
            target=bool(len(infer_missing_sites(public.observed_configuration['coordinates'],h.proposed_intervention.value=='heal_interior_vacancy')))
        risk=.1 if target else .8
        utility=gain-.3*(cost/30)-risk
        proposals.append(ExperimentProposal(experiment_id=uuid.uuid4().hex,case_id=public.case_id,target_hypothesis_id=h.id,intervention=h.proposed_intervention,matched_seeds=SEEDS,controlled_parameters={'units':'lj_reduced_2d','matched_seeds':SEEDS,'reference_rate':.05,'reference_temperature':.05},modified_parameters={},rationale=f'Discriminate {h.title}; observable target present={target}; utility=gain-0.3*(cost/30 seconds)-risk.',estimated_cost_sec=cost,expected_information_gain=gain,risk_penalty=risk,utility_score=utility,ai_execution_mode=mode,provenance=provenance))
    return sorted(proposals,key=lambda p:p.utility_score,reverse=True)
