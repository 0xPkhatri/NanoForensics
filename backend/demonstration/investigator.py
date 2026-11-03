"""Blind registered tool loop for the separate preregistered dataset."""
import time
import uuid
from backend.agents.investigator import NanoForensicsInvestigator
from backend.agents.muse_agent import telemetry,FALLBACK
from backend.models.schemas import InvestigationState,Hypothesis,ExperimentProposal,InterventionType,DefectType,SimulationSummary
from backend.simulation.numpy_md_fallback import content_hash
from backend.demonstration.geometry import missing_components,reconstruct
from backend.demonstration.registration import registration
from backend.demonstration.analysis import discriminating_contrast


class DemonstrationInvestigator(NanoForensicsInvestigator):
    run_timeout=90.

    def hypothesize(self,case_id):
        design,digest=registration();public=self.store.public(case_id)
        partition=public.observed_configuration['study_partition'];seeds=design[partition]['seeds']
        prior=self.store.state(case_id)
        self.state=InvestigationState(case_id=case_id,status='OBSERVING',is_running=True,ai_telemetry=telemetry(),budget_total_sec=1800,budget_used_sec=prior.budget_used_sec if prior else 0.)
        if self.started is None:self.started=time.perf_counter();self.previous_used=self.state.budget_used_sec
        self.state.ai_execution_mode=FALLBACK
        self.state.ai_telemetry.execution_mode=FALLBACK
        self.state.ai_telemetry.last_error='Registered deterministic demonstration; no model inference requested'
        provenance={'action':'registered_competing_hypotheses','registration_hash':digest,'ai_execution_mode':FALLBACK}
        self._save('Inspecting observable geometry and actual baseline; private preparation unavailable','observe')
        components=missing_components(public.observed_configuration['coordinates'])
        self.state.hypotheses=[];self.state.proposed_experiments=[]
        pairs=[(False,DefectType.INTERIOR_VACANCY,InterventionType.HEAL_INTERIOR_VACANCY,'Interior bond-network disruption'),(True,DefectType.SURFACE_NOTCH,InterventionType.SMOOTH_SURFACE_NOTCH,'Boundary-connected stress concentration')]
        for index,(boundary,cause,intervention,title) in enumerate(pairs):
            count=sum(len(c['sites']) for c in components if c['boundary_connected']==boundary)
            hid=f'H{index+1}'
            self.state.hypotheses.append(Hypothesis(id=hid,title=title,mechanism='A transverse missing-site component may concentrate tensile stress and initiate persistent reference-bond rupture.',suspected_cause=cause,supporting_evidence=[f'Observable candidate sites of this topology: {count}.',f'Baseline outcome: {public.baseline_simulation.outcome.value}.'],missing_evidence='Registered matched-seed repair and competing-repair contrast.',proposed_intervention=intervention,predicted_strain_recovery_pct=20,confidence=.5,status='PENDING',ai_execution_mode=FALLBACK,provenance=provenance))
            self.state.proposed_experiments.append(ExperimentProposal(experiment_id=uuid.uuid4().hex,case_id=case_id,target_hypothesis_id=hid,intervention=intervention,matched_seeds=seeds,controlled_parameters={'registration_hash':digest,'partition':partition,'units':'lj_reduced_2d'},modified_parameters={},rationale='Registered competing intervention; measured target count affects priority, not verdict.',estimated_cost_sec=12*len(seeds),expected_information_gain=.8 if count else .1,risk_penalty=.1 if count else .8,utility_score=(.8 if count else .1)-.3*(12*len(seeds)/120)-(.1 if count else .8),ai_execution_mode=FALLBACK,provenance=provenance))
        self.state.status='HYPOTHESIZING'
        self._save('Two competing mechanisms predeclared before counterfactual outcomes','hypothesize',provenance=provenance)
        self._save('Ranked both registered repairs; all available arms will be tested','plan')
        return self.state

    def propose_experiment(self,case_id,experiment_type,parameters=None,rationale='Registered study selection'):
        if experiment_type not in ['heal_interior_vacancy','smooth_surface_notch'] or any(value is not None for value in (parameters or {}).values()):
            raise ValueError('Only the two unchanged registered geometric repairs are allowed')
        return super().propose_experiment(case_id,experiment_type,parameters,rationale)

    def validate_experiment(self,experiment_id):
        p=self._proposal(experiment_id);original=self.store.specimen(p.case_id)
        edited,trace=reconstruct(original,p.intervention)
        trace.update(input_configuration_hash=content_hash(original.model_dump()),output_configuration_hash=content_hash(edited.model_dump()))
        self.edit_inputs[experiment_id]=edited
        self._save('Observable missing-component reconstruction validated','intervention',experiment_id=experiment_id,trace=trace)
        return trace

    def evaluate_hypotheses(self,case_id):
        self._save('Beliefs revised from independent verification; contrast remains pending until both arms complete','belief_revision',ai_execution_mode=FALLBACK)
        return self.state.hypotheses

    def generate_report(self,case_id):
        supported=[h for h in self.state.hypotheses if h.status=='SUPPORTED']
        contrast=None
        if len(supported)==1 and len(self.state.executed_experiments)==2:
            winner=next(p for p in self.state.proposed_experiments if p.target_hypothesis_id==supported[0].id)
            other=next(p for p in self.state.proposed_experiments if p.experiment_id!=winner.experiment_id)
            raw=lambda p:[SimulationSummary.model_validate(r) for r in self.state.executed_experiments[p.experiment_id].replicate_results]
            baseline=self.baseline_runs.get(winner.experiment_id) or [SimulationSummary.model_validate(r) for r in self.store.public(case_id).baseline_simulation.replicate_results]
            contrast=discriminating_contrast(baseline,raw(winner),raw(other))
        if contrast and contrast['is_distinguishable']:
            self.state.status='CONCLUDED';self.state.identified_cause=supported[0].suspected_cause
            self.state.final_verdict_summary='Registered recovery and competing-intervention contrast support '+supported[0].title+'. This is a bounded 2D computational demonstration.'
        else:
            self.state.status='INCONCLUSIVE';self.state.identified_cause=None
            self.state.final_verdict_summary='Registered evidence does not establish a uniquely distinguishable repair mechanism. Failures, censoring and null results are retained.'
        self._save(self.state.final_verdict_summary,'conclude',registered_contrast=contrast)
        return self.state
