"""Registered deterministic scientific tools and auditable adaptive controller."""
import time
from datetime import datetime, timezone
from backend.config import BUDGET, SEEDS, RUN_TIMEOUT
from backend.models.schemas import InvestigationState, InterventionType, InterventionParameters, HypothesisStatus
from backend.agents.muse_agent import decide, telemetry, FALLBACK
from backend.agents.hypothesis_engine import fallback_hypotheses, update_from_verification
from backend.agents.experiment_planner import plan
from backend.simulation.defect_generator import transform, infer_missing_sites
from backend.simulation.numpy_md_fallback import content_hash
from backend.simulation.lammps_runner import engine_capabilities
from backend.simulation.worker import run_bounded
from backend.analysis.comparison import aggregate
from backend.analysis.evidence_verifier import verify
from backend.storage.db import Store


class BudgetExceeded(RuntimeError): pass


class NanoForensicsInvestigator:
    TOOL_NAMES=('inspect_case','get_structural_evidence','list_experiments','propose_experiment','validate_experiment','run_lammps','compare_outcomes','evaluate_hypotheses','generate_report')

    def __init__(self,store=None):
        self.store=store or Store()
        self.state=None
        self.started=None
        self.previous_used=0.
        self.ranking=None
        self.provenance={}
        self.edit_inputs={}
        self.baseline_runs={}
        self.force_recompute=False

    def inspect_case(self,case_id):
        return self.store.public(case_id).model_dump(mode='json')

    def get_structural_evidence(self,case_id,region='all',measurement='missing_sites'):
        if region not in ['all','interior','surface'] or measurement not in ['missing_sites','coordination','bond_loss']:
            raise ValueError('Unsupported structural query')
        public=self.store.public(case_id)
        q=public.observed_configuration['coordinates']
        return {'interior_candidate_sites':infer_missing_sites(q,True).tolist(),'edge_candidate_sites':infer_missing_sites(q,False).tolist(),'snapshots':[s.model_dump() for s in public.baseline_simulation.snapshots], 'query':{'region':region,'measurement':measurement}}

    def _save(self,message,stage,**detail):
        if self.started is not None:
            self.state.budget_used_sec=self.previous_used+time.perf_counter()-self.started
        self.state.current_step_message=message
        self.state.audit_log.append({'timestamp':datetime.now(timezone.utc).isoformat(),'stage':stage,'message':message,**detail})
        self.store.save_state(self.state)

    def _budget(self):
        used=self.previous_used+time.perf_counter()-self.started
        if used>=self.state.budget_total_sec:
            raise BudgetExceeded('Investigation compute budget exhausted')
        return self.state.budget_total_sec-used

    def hypothesize(self,case_id):
        self.state=self.store.state(case_id) or InvestigationState(case_id=case_id,status='OBSERVING',ai_telemetry=telemetry(),budget_total_sec=BUDGET)
        if self.started is None:
            self.started=time.perf_counter(); self.previous_used=self.state.budget_used_sec
        self.state.is_running=True
        self._save('Inspecting blind observed specimen','observe')
        decision,t,provenance=decide(self.inspect_case(case_id))
        self.state.ai_telemetry=t;self.state.ai_execution_mode=t.execution_mode;self.provenance=provenance
        self.state.executed_experiments={}
        self.state.verifications=[]
        self.state.hypotheses=decision.hypotheses if decision else fallback_hypotheses(self.store.public(case_id),provenance)
        for h in self.state.hypotheses:
            h.status=HypothesisStatus.PENDING
        self.ranking=decision.ranking if decision else None
        self.state.status='HYPOTHESIZING'
        self._save('Competing hypotheses generated','hypothesize',ai_execution_mode=t.execution_mode,provenance=provenance)
        self.state.proposed_experiments=plan(self.store.public(case_id),self.state.hypotheses,self._budget(),t.execution_mode,provenance,self.ranking)
        self._save('Candidate interventions ranked by information, cost and risk','plan')
        return self.state

    def list_experiments(self,case_id):
        state=self.store.state(case_id)
        return [p.model_dump(mode='json') for p in state.proposed_experiments] if state else []

    def propose_experiment(self,case_id,experiment_type,parameters=None,rationale='User-selected allowlisted intervention'):
        from backend.models.schemas import ExperimentProposal
        import uuid
        intervention=InterventionType(experiment_type)
        params=InterventionParameters.model_validate(parameters or {})
        existing=next((p for p in self.state.proposed_experiments if p.intervention==intervention),None)
        if existing:
            existing.modified_parameters=params.model_dump(exclude_none=True)
            return existing
        h=next((h for h in self.state.hypotheses if h.proposed_intervention==intervention),None)
        p=ExperimentProposal(experiment_id=uuid.uuid4().hex,case_id=case_id,target_hypothesis_id=h.id if h else 'DIAGNOSTIC',intervention=intervention,matched_seeds=(SEEDS+[101,202,303] if intervention==InterventionType.REPEAT_REPLICATE_SEEDS else SEEDS),controlled_parameters={'matched_seeds':SEEDS},modified_parameters=params.model_dump(exclude_none=True),rationale=rationale,estimated_cost_sec=18,expected_information_gain=.2,risk_penalty=.1,utility_score=-.08,ai_execution_mode=FALLBACK,provenance={'action':'registered_user_selection'})
        self.state.proposed_experiments.append(p)
        return p

    def _proposal(self,experiment_id):
        return next(p for p in self.state.proposed_experiments if p.experiment_id==experiment_id)

    def validate_experiment(self,experiment_id):
        p=self._proposal(experiment_id)
        original=self.store.specimen(p.case_id)
        edited,trace=transform(original,p.intervention,InterventionParameters.model_validate(p.modified_parameters))
        trace.update(input_configuration_hash=content_hash(original.model_dump()),output_configuration_hash=content_hash(edited.model_dump()),removed_atom_ids=[])
        self.edit_inputs[p.experiment_id]=edited
        self._save('Geometric/protocol transformation validated','intervention',experiment_id=experiment_id,trace=trace)
        return trace

    def _run(self,specimen,fresh=False):
        remaining=self._budget()
        key=content_hash({'input':specimen.model_dump(),'solver_version':'sflj-1.1','engine':engine_capabilities()})
        result=None if fresh else self.store.cached(key)
        cached=result is not None
        if result is None:
            result=run_bounded(specimen,timeout=min(getattr(self,'run_timeout',RUN_TIMEOUT),remaining))
            self.store.save_result(key,result)
        self._save(f'{"Cached immutable" if cached else "Freshly computed"} replicate seed {specimen.protocol.seed}','simulation',seed=specimen.protocol.seed,result_id=result.sim_id,cached=cached,outcome=result.outcome,wall_time_sec=result.wall_time_sec,relaxation_convergence=result.diagnostics.get('minimization_residual'),error_code=result.error_code)
        return result

    def run_lammps(self,experiment_id):
        p=self._proposal(experiment_id)
        self.state.status='EXPERIMENTING'
        baseline=[];counter=[]
        original=self.store.specimen(p.case_id)
        edited=self.edit_inputs[experiment_id]
        for seed in p.matched_seeds:
            b=original.model_copy(deep=True);b.protocol.seed=seed
            c=edited.model_copy(deep=True);c.protocol.seed=seed
            baseline.append(self._run(b));counter.append(self._run(c,fresh=self.force_recompute))
        self.baseline_runs[experiment_id]=baseline
        summary=aggregate(counter)
        self.store.save_result('aggregate:'+summary.sim_id,summary)
        self.state.executed_experiments[experiment_id]=summary
        self._save('Matched-seed counterfactual completed','experiment',experiment_id=experiment_id,raw_result_ids=[r.sim_id for r in counter])
        return summary

    def compare_outcomes(self,baseline_id,experiment_id):
        from backend.models.schemas import SimulationSummary
        p=self._proposal(experiment_id)
        summary=self.state.executed_experiments[experiment_id]
        raw=[SimulationSummary.model_validate(r) for r in summary.replicate_results]
        result=verify(p,self.baseline_runs[experiment_id],raw)
        self.state.verifications.append(result)
        self.state.hypotheses=update_from_verification(self.state.hypotheses,result)
        self._save('Independent empirical verification completed','verify',verification=result.model_dump(mode='json'))
        return result.model_dump(mode='json')

    def evaluate_hypotheses(self,case_id):
        visible={'case':self.inspect_case(case_id),'hypotheses':[h.model_dump(mode='json') for h in self.state.hypotheses],'completed_evidence':[v.model_dump(mode='json') for v in self.state.verifications],'remaining_budget_sec':self._budget()}
        decision,t,provenance=decide(visible,'revise_after_evidence')
        self.state.ai_telemetry=t;self.state.ai_execution_mode=t.execution_mode;self.provenance=provenance
        if decision:
            self.ranking=decision.ranking
            # Measured verifier status is authoritative; update only model confidence/predictions.
            for h in self.state.hypotheses:
                candidate=next((x for x in decision.hypotheses if x.proposed_intervention==h.proposed_intervention),None)
                if candidate:
                    h.confidence=candidate.confidence;h.provenance=provenance;h.ai_execution_mode=t.execution_mode
        revision=decision.revision if decision else 'Deterministic revision: use independent verification; retain PENDING when evidence is unavailable; consider remaining interventions.'
        done={p.intervention for p in self.state.proposed_experiments if p.experiment_id in self.state.executed_experiments}
        attempted={a.get('intervention') for a in self.state.audit_log if a.get('stage')=='attempted'}
        fresh=plan(self.store.public(case_id),self.state.hypotheses,self._budget(),t.execution_mode,provenance,self.ranking)
        for updated in fresh:
            for existing in self.state.proposed_experiments:
                if existing.intervention==updated.intervention and existing.intervention not in done and existing.intervention.value not in attempted:
                    existing.utility_score=updated.utility_score
                    existing.expected_information_gain=updated.expected_information_gain
                    existing.ai_execution_mode=updated.ai_execution_mode
                    existing.provenance=updated.provenance
        self.state.proposed_experiments += [p for p in fresh if p.intervention not in done and p.intervention.value not in attempted and not any(x.intervention==p.intervention for x in self.state.proposed_experiments)]
        self._save(revision,'belief_revision',ai_execution_mode=t.execution_mode,provenance=provenance)
        return self.state.hypotheses

    def generate_report(self,case_id):
        supported=[h for h in self.state.hypotheses if h.status=='SUPPORTED']
        if len(supported)==1:
            self.state.identified_cause=supported[0].suspected_cause
            self.state.status='CONCLUDED'
            self.state.final_verdict_summary=f'Empirical support for {supported[0].title}; three-pair descriptive evidence, not validated real-material prediction.'
        else:
            self.state.identified_cause=None;self.state.status='INCONCLUSIVE'
            self.state.final_verdict_summary='No unique cause established. Censored, unavailable, noisy or competing evidence is retained in the audit.'
        self._save(self.state.final_verdict_summary,'conclude')
        return self.state

    def investigate(self,case_id,only_proposal=None,intervention=None,parameters=None,max_experiments=4,force_recompute=False):
        self.force_recompute=force_recompute
        self.started=time.perf_counter()
        old=self.store.state(case_id);self.previous_used=old.budget_used_sec if old else 0.
        try:
            if only_proposal and old and old.hypotheses:
                self.state=old
                self.state.is_running=True
                self.provenance={"action":"execute_registered_proposal"}
            else:
                self.hypothesize(case_id)
            if intervention:
                chosen=self.propose_experiment(case_id,intervention,parameters)
                only_proposal=chosen.experiment_id
            count=0;attempted=set()
            while count<max_experiments:
                self._budget()
                options=[p for p in self.state.proposed_experiments if p.intervention not in attempted]
                if only_proposal: options=[p for p in options if p.experiment_id==only_proposal]
                if not options: break
                p=max(options,key=lambda p:p.utility_score)
                attempted.add(p.intervention);count+=1
                self._save('Selected bounded intervention','attempted',intervention=p.intervention.value,experiment_id=p.experiment_id)
                trace=self.validate_experiment(p.experiment_id)
                if trace['status']=='NO_APPLICABLE_EDIT':
                    self._save('NO_APPLICABLE_EDIT: no imaginary repair performed','data_availability',experiment_id=p.experiment_id)
                else:
                    self.run_lammps(p.experiment_id)
                    self.compare_outcomes(self.store.public(case_id).baseline_simulation.sim_id,p.experiment_id)
                    self.evaluate_hypotheses(case_id)
                if only_proposal: break
            return self.generate_report(case_id)
        except BudgetExceeded as exc:
            self.state.status='INCONCLUSIVE';self.state.final_verdict_summary=str(exc)
            self._save(str(exc),'budget')
            return self.state
        finally:
            if self.state:
                self.state.is_running=False
                self._save('Investigation stopped; results persisted','complete')
