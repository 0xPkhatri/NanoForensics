"""Baseline B has the same public observations, one call and zero interventions."""
from backend.agents.muse_agent import decide
from backend.agents.hypothesis_engine import fallback_hypotheses


def run(public):
    decision,t,provenance=decide(public.model_dump(mode='json'),'oneshot_baseline')
    hypotheses=decision.hypotheses if decision else fallback_hypotheses(public,provenance)
    ranked=sorted(hypotheses,key=lambda h:h.confidence,reverse=True)
    unique=len(ranked)>1 and ranked[0].confidence>ranked[1].confidence and ranked[0].confidence>=.5
    return {'identified_cause':ranked[0].suspected_cause.value if unique else None,'status':'UNVERIFIED_PREDICTION' if unique else 'NO_DECISION','ai_execution_mode':t.execution_mode.value,'telemetry':t.model_dump(mode='json',exclude_none=True),'provenance':provenance,'experimental_budget':0,'model_call_budget':1,'hypotheses':[h.model_dump(mode='json') for h in hypotheses]}
