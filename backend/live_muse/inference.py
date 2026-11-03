"""Operation-local JSON validation and safe, auditable model transport."""
from backend.agents.muse_agent import _request,telemetry,digest,FALLBACK,LIVE
import json


def infer(action,observations,contract,validate=None):
    messages=[{'role':'system','content':
        'You are a materials-science investigator in a 2D reduced-unit SFLJ toy model. '
        'Use ONLY supplied observable data and completed experiment records. Do not infer causes from opaque IDs. '
        'Missing-component positions are supplied as measured geometry. Do not assume a missing component lies at the baseline crack-initiation side. '
        'There are two allowed geometric repairs. Explain competing testable mechanisms; do not claim exclusive causation. '
        'Engineering failure-strain effects may be positive or negative. T=0 seed labels are deterministic replays, '
        'not independent thermal samples; scores are subjective, not calibrated probabilities. '
        'Physical protocols, thresholds, verifier verdicts and the frozen NOT_VALIDATED study are immutable. '
        'Before experiments, do not claim observed recovery. After experiments, cite actual evidence IDs and measured '
        'sign/magnitude when revising confidence. Numerical failures and censoring cannot prove a mechanism. '
        'Never emit code, shell commands, new protocols or a claim that the full study is validated. '
        'Return JSON matching this schema: '+json.dumps(contract.model_json_schema())},
        {'role':'user','content':json.dumps({'action':action,'observations':observations},sort_keys=True)}]
    record={'action':action,'request_hash':digest(messages),'request_messages':messages,'attempts':[]}
    schema=contract.model_json_schema()
    evidence_ids=sorted({v['experiment_id'] for v in observations.get('completed_evidence',[])})
    if action=='revise_after_evidence' and evidence_ids:
        schema['$defs']['Belief']['properties']['evidence_ids']['items']={'type':'string','enum':evidence_ids}
    t=telemetry()
    for attempt in range(2):
        record['request_hash']=digest(messages)
        record['request_messages']=[dict(message) for message in messages]
        parsed,t=_request(messages,3500,schema=schema)
        record['attempts'].append({'attempt':attempt+1,'request_hash':record['request_hash'],'telemetry':t.model_dump(mode='json',exclude_none=True),'response_hash':digest(parsed) if parsed is not None else None,'parsed_json':parsed})
        if parsed is None:break
        try:
            result=contract.model_validate(parsed)
            if validate:validate(result)
            t.execution_mode=LIVE
            record.update(parsed_json=parsed,response_hash=digest(parsed),telemetry=t.model_dump(mode='json',exclude_none=True))
            return result,t,record
        except ValueError as exc:
            record['attempts'][-1]['validation_error']=type(exc).__name__
            t.last_error='Provider JSON failed bounded action/evidence validation'
            if attempt==0:messages.append({'role':'user','content':'The previous JSON failed action/evidence validation. Return both beliefs, follow the exact schema, and cite only these completed evidence IDs: '+json.dumps(evidence_ids)})
    t.execution_mode=FALLBACK
    record.update(telemetry=t.model_dump(mode='json',exclude_none=True),fallback_reason=t.last_error)
    return None,t,record
