"""Bounded JSON inference with operation-local provenance. Never executes model code."""
import hashlib
import json
import os
import time
from urllib.parse import urlsplit, urlunsplit
import httpx
from backend.models.schemas import LLMTelemetry, AIExecutionMode, ModelDecision

FALLBACK=AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK
LIVE=AIExecutionMode.LIVE_MUSE_SPARK_API


def telemetry():
    raw=os.getenv('META_MUSE_BASE_URL','').strip()
    url=urlsplit(raw)
    safe=urlunsplit((url.scheme,(url.hostname or '')+(f':{url.port}' if url.port else ''),url.path,'',''))
    return LLMTelemetry(execution_mode=FALLBACK,configured_model=os.getenv('META_MUSE_MODEL',''),base_url=safe,api_key_present=bool(os.getenv('META_MUSE_API_KEY','').strip()))


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,default=str).encode()).hexdigest()


def _request(messages,max_tokens,schema=None):
    t=telemetry()
    started=time.perf_counter()
    if not t.api_key_present:
        t.last_error='META_MUSE_API_KEY not configured'
        return None,t
    if not t.base_url or not t.configured_model:
        t.last_error='META_MUSE_BASE_URL and META_MUSE_MODEL must be configured'
        return None,t
    try:
        response=httpx.post(t.base_url.rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+os.environ['META_MUSE_API_KEY']},json={'model':t.configured_model,'messages':messages,'response_format':({'type':'json_schema','json_schema':{'name':'scientific_action','schema':schema,'strict':True}} if schema else {'type':'json_object'}),'max_completion_tokens':max_tokens,'reasoning_effort':'minimal','temperature':0},timeout=min(60.,max(1.,float(os.getenv('META_MUSE_TIMEOUT_SEC','30')))))
        response.raise_for_status()
        data=response.json()
        t.last_call_latency_ms=(time.perf_counter()-started)*1000
        t.response_id=data.get('id')
        usage=data.get('usage') or {}
        t.prompt_tokens=usage.get('prompt_tokens');t.completion_tokens=usage.get('completion_tokens')
        if data.get('model') != t.configured_model:
            t.last_error='Provider returned a different or missing model identity'
            return None,t
        choice=data['choices'][0]
        if choice.get('finish_reason')!='stop':
            t.last_error='Provider response incomplete or refused (finish_reason='+str(choice.get('finish_reason'))+')'
            return None,t
        parsed=json.loads(choice['message']['content'])
        if not isinstance(parsed,dict): raise ValueError('JSON object required')
        return parsed,t
    except Exception as exc:
        # Do not echo URLs, headers, credentials or provider bodies into public logs.
        t.last_call_latency_ms=(time.perf_counter()-started)*1000
        t.last_error=f'Structured inference failed: {type(exc).__name__}'+(f' HTTP {exc.response.status_code}' if isinstance(exc,httpx.HTTPStatusError) else '')
        return None,t


def verify_llm_connection():
    parsed,t=_request([{'role':'user','content':'Return JSON only: {"ok": true}'}],256)
    if parsed=={'ok':True} and type(parsed['ok']) is bool: t.execution_mode=LIVE
    elif parsed is not None: t.last_error='Structured health response did not match required object'
    return t


def decide(visible,action='hypothesize'):
    messages=[{'role':'system','content':'You investigate a 2D reduced-unit Lennard-Jones testbed. Use visible observations only; propose at least two competing causal hypotheses and rank allowlisted physical interventions by expected information gain, cost and risk. After evidence, revise predictions and explain changes; numerical failures and censoring do not prove causal mechanisms. Return JSON matching this schema. No code or shell commands. '+json.dumps(ModelDecision.model_json_schema())},{'role':'user','content':json.dumps({'action':action,'observations':visible},default=str)}]
    provenance={'action':action,'request_hash':digest(messages)}
    last=telemetry()
    for _ in range(2):
        parsed,t=_request(messages,2200)
        last=t
        if parsed is None: break
        try:
            result=ModelDecision.model_validate(parsed)
            t.execution_mode=LIVE
            provenance.update(response_hash=digest(parsed),parsed_json=parsed,telemetry=t.model_dump(mode='json',exclude_none=True))
            for h in result.hypotheses:
                h.ai_execution_mode=LIVE;h.provenance=provenance
            return result,t,provenance
        except ValueError:
            last.last_error='Provider JSON failed bounded decision schema validation'
            messages.append({'role':'user','content':'Your response failed schema validation. Return only the bounded JSON decision.'})
    last.execution_mode=FALLBACK
    provenance.update(telemetry=last.model_dump(mode='json',exclude_none=True),fallback_reason=last.last_error)
    return None,last,provenance
