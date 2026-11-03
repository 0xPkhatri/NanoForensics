"""Live AI overlay using unchanged registered deterministic physical tools/verifier."""
import numpy as np
from backend.demonstration.investigator import DemonstrationInvestigator
from backend.demonstration.geometry import study_components
from backend.agents.muse_agent import LIVE,FALLBACK
from backend.live_muse.inference import infer
from backend.live_muse.contracts import Hypotheses,Planning,Revision


class LiveMuseInvestigator(DemonstrationInvestigator):
    def observations(self,case_id):
        public=self.store.public(case_id);b=public.baseline_simulation
        components=study_components(public.observed_configuration['coordinates'])
        q=np.asarray(public.observed_configuration['coordinates']);xmin=float(q[:,0].min());width=float(np.ptp(q[:,0]))
        measured=[]
        for component in components:
            sites=np.asarray(component['sites']);centroid=sites.mean(axis=0);relative_x=float((centroid[0]-xmin)/width)
            measured.append({'site_count':len(sites),'boundary_connected':component['boundary_connected'],
                'inferred_missing_site_centroid_xy':centroid.tolist(),'relative_x_in_specimen':relative_x,
                'measured_side':('surface_left' if relative_x<.2 else 'surface_right' if relative_x>.8 else 'interior')})
        return {'case_id':public.case_id,'scope':'Post-study AI rehearsal, not new held-out scoring; full study NOT_VALIDATED',
            'protocol':public.observed_configuration['public_protocol'],'coordinates':public.observed_configuration['coordinates'],
            'observed_missing_components':measured,
            'baseline':{'outcome':b.outcome.value,'failure_strain':b.failure_strain,'peak_stress':b.peak_stress,
                'crack_region':b.crack_initiation_region,'numerically_valid':b.numerical_check.is_valid,
                'curve':b.stress_strain_curve,'replicate_result_ids':[r['sim_id'] for r in b.replicate_results]},
            'allowed_interventions':['heal_interior_vacancy','smooth_surface_notch'],
            'fixed_cost_convention':'Three counterfactual replays, cached immutable baseline; estimated 16 seconds per new MD run',
            'replay_interpretation':'One athermal geometry, zero independent thermal samples; no population uncertainty'}

    def _record_action(self,stage,result,t,record):
        self.state.ai_execution_mode=t.execution_mode;self.state.ai_telemetry=t
        self._save(('Verified live Muse Spark '+stage if result else 'Visible deterministic fallback for '+stage),stage,
            ai_execution_mode=t.execution_mode,provenance=record)

    def hypothesize(self,case_id):
        super().hypothesize(case_id)
        result,t,record=infer('hypothesize',self.observations(case_id),Hypotheses)
        if result:
            for candidate in result.hypotheses:
                h=next(h for h in self.state.hypotheses if h.proposed_intervention==candidate.intervention)
                h.title=candidate.title;h.mechanism=candidate.mechanism;h.supporting_evidence=candidate.evidence
                h.missing_evidence=candidate.missing_evidence;h.predicted_strain_recovery_pct=candidate.predicted_recovery_pct
                h.confidence=candidate.confidence;h.ai_execution_mode=LIVE;h.provenance=record
        self._record_action('hypothesize',result,t,record)
        self._plan(case_id)
        return self.state

    def _plan(self,case_id):
        visible=self.observations(case_id)
        visible['hypotheses']=[{'intervention':h.proposed_intervention.value,'mechanism':h.mechanism,'confidence':h.confidence} for h in self.state.hypotheses]
        visible['completed_evidence']=[v.model_dump(mode='json') for v in self.state.verifications]
        result,t,record=infer('plan_experiments',visible,Planning)
        for p in self.state.proposed_experiments:
            if p.experiment_id in self.state.executed_experiments:continue
            p.estimated_cost_sec=16*len(p.matched_seeds)
            if result:
                c=next(c for c in result.choices if c.intervention==p.intervention)
                p.expected_information_gain=c.information_gain;p.risk_penalty=c.risk;p.rationale=c.rationale
            p.utility_score=p.expected_information_gain-.3*(p.estimated_cost_sec/120)-p.risk_penalty
            p.ai_execution_mode=t.execution_mode;p.provenance=record
        self._record_action('plan',result,t,record)

    def compare_outcomes(self,baseline_id,experiment_id):
        prior={h.id:h.confidence for h in self.state.hypotheses}
        result=super().compare_outcomes(baseline_id,experiment_id)
        for h in self.state.hypotheses:h.confidence=prior[h.id]
        return result

    def evaluate_hypotheses(self,case_id):
        visible=self.observations(case_id)
        visible['prior_beliefs']=[{'intervention':h.proposed_intervention.value,'confidence':h.confidence,'predicted_recovery_pct':h.predicted_strain_recovery_pct} for h in self.state.hypotheses]
        visible['completed_evidence']=[v.model_dump(mode='json') for v in self.state.verifications]
        allowed={v.experiment_id for v in self.state.verifications}
        def validate(result):
            if not allowed or any(not set(b.evidence_ids)<=allowed for b in result.beliefs):raise ValueError('Unobserved evidence citation')
        result,t,record=infer('revise_after_evidence',visible,Revision,validate)
        before={h.id:h.confidence for h in self.state.hypotheses}
        for h in self.state.hypotheses:
            h.ai_execution_mode=t.execution_mode;h.provenance=record
            if result:
                b=next(b for b in result.beliefs if b.intervention==h.proposed_intervention)
                h.confidence=b.confidence;h.predicted_strain_recovery_pct=b.predicted_recovery_pct
                h.supporting_evidence.append(b.explanation+' Evidence: '+', '.join(b.evidence_ids))
            else:
                h.confidence=.7 if h.status=='SUPPORTED' else .1 if h.status=='REJECTED' else .25
            # Independent deterministic verifier statuses are never overwritten.
        record['belief_changes']=[{'hypothesis_id':h.id,'before':before[h.id],'after':h.confidence,'verifier_status':h.status.value} for h in self.state.hypotheses]
        self._record_action('belief_revision',result,t,record)
        if result:self._save(result.revision,'model_explanation',ai_execution_mode=LIVE,evidence_ids=sorted(allowed))
        return self.state.hypotheses
