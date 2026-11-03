"""Baseline A: equivalent public observations, fixed intervention order."""
import time
from backend.agents.investigator import NanoForensicsInvestigator
from backend.agents.muse_agent import telemetry
from backend.agents.hypothesis_engine import fallback_hypotheses
from backend.agents.experiment_planner import plan
from backend.models.schemas import InvestigationState


class FixedChecklist(NanoForensicsInvestigator):
    def hypothesize(self,case_id):
        self.state=InvestigationState(case_id=case_id,status='HYPOTHESIZING',is_running=True,ai_telemetry=telemetry())
        self.state.hypotheses=fallback_hypotheses(self.store.public(case_id),{'action':'fixed_checklist','model_calls':0})
        self.state.proposed_experiments=plan(self.store.public(case_id),self.state.hypotheses,self.state.budget_total_sec,self.state.ai_execution_mode,{'action':'fixed_checklist'})
        order=[h.proposed_intervention for h in self.state.hypotheses]
        for p in self.state.proposed_experiments:
            p.utility_score=10-order.index(p.intervention)
        self._save('Fixed checklist, same visible geometry and measurement access','hypothesize')
        return self.state

    def evaluate_hypotheses(self,case_id):
        self._save('Fixed-order baseline retains verifier decisions without adaptive model calls','belief_revision')
        return self.state.hypotheses
