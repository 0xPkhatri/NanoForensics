import type {ConsoleActivity, ConsoleEvent} from './api';
import {clockLabel} from './console-view.ts';
import {testName} from './presentation.ts';

export type TerminalTone = 'success'|'progress'|'warning'|'error'|'muted';
export interface TerminalRow {
  key: string; original: unknown; raw: string; seq: number | null;
  timestamp: string | null; time: string; phase: string; status: string;
  tag: string; tone: TerminalTone; message: string; metrics: string[];
  groupId: string | null; groupLabel: string | null; groupStart: boolean; branch: string;
  searchText: string;
}
export interface TextRange {start:number; end:number}
export const record = (value: unknown): Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string,unknown> : {};
const text = (value: unknown) => typeof value === 'string' ? value : '';
const numeric = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);
const amount = (value: unknown) => numeric(value) ? String(value) : 'unavailable';
const signedPercent = (value: unknown) => numeric(value) ? `${value > 0 ? '+' : ''}${value}%` : 'unavailable';
const items = (value: unknown) => Array.isArray(value) ? value.map(record) : [];
export const eventKey = (job: unknown, seq: unknown, index: number) => `${text(job) || 'unknown-job'}:${numeric(seq) ? seq : `unindexed-${index}`}`;

export function rawEventJSON(event: unknown): string {
  try {return JSON.stringify(event,null,2) ?? '[Payload is not JSON]'}
  catch {return '[Payload could not be serialized as JSON]'}
}

function eventCategory(event: Record<string,unknown>, data: Record<string,unknown>): {tag:string;tone:TerminalTone} {
  const verification = record(data.verification), checks = record(data.numerical_check);
  const execution = text(data.execution_status);
  if (['CANCELLED','INTERRUPTED'].includes(execution)) return {tag:'STOP',tone:'warning'};
  if (event.status === 'failed' || ['FAILED','TIMED_OUT'].includes(execution) || data.outcome === 'EXECUTION_FAILED' || checks.is_valid === false || verification.numerical_consistency_passed === false || (text(verification.execution_status) && verification.execution_status !== 'COMPLETE')) return {tag:'ERR',tone:'error'};
  if (event.status === 'skipped') return {tag:'SKIP',tone:'warning'};
  const receipt = record(record(data.receipt).telemetry);
  const mode = receipt.execution_mode || data.ai_execution_mode;
  if (mode === 'OFFLINE_HEURISTIC_FALLBACK' && event.status === 'completed') return {tag:'AI',tone:'warning'};
  if (data.cached === true) return {tag:'CACHE',tone:'muted'};
  if (['hypotheses','revise'].includes(text(event.phase))) return {tag:'AI',tone:'progress'};
  if (event.phase === 'plan') return {tag:'PLAN',tone:'progress'};
  if (event.phase === 'verify') return {tag:event.status === 'completed' ? 'RESULT' : 'CHECK',tone:verification.verdict === 'INCONCLUSIVE' ? 'warning' : 'progress'};
  if (event.phase === 'conclude') return {tag:'CONCLUDE',tone:data.scientific_status === 'INCONCLUSIVE' ? 'warning' : 'progress'};
  if (event.phase === 'complete' && event.status === 'completed') return {tag:'DONE',tone:'success'};
  if (event.status === 'started') return {tag:'RUN',tone:'progress'};
  if (event.status === 'completed') return {tag:'OK',tone:'success'};
  return {tag:'INFO',tone:'muted'};
}

function compactMetrics(data: Record<string,unknown>, status: string): string[] {
  const output: string[] = [];
  if (numeric(data.atom_count)) output.push(`${data.atom_count} atoms`);
  const baseline = record(data.baseline);
  if (Object.keys(baseline).length) {
    output.push(`Stored baseline ${text(baseline.sim_id) || '(ID unavailable)'}`);
    if (baseline.numerical_valid === false) output.push('Baseline numerical checks failed');
    if (baseline.outcome === 'NOT_FRACTURED_WITHIN_HORIZON') output.push(`No fracture within horizon; maximum engineering strain ${amount(baseline.max_observed_strain)}`);
    else if (baseline.outcome === 'FRACTURED') output.push(`Baseline fracture strain ${amount(baseline.failure_strain)}; peak stress ${amount(baseline.peak_stress)} LJ`);
    else if (baseline.outcome === 'EXECUTION_FAILED') output.push('Baseline execution failed; not valid causal evidence');
  }
  if (text(data.role)) output.push(`${data.role === 'baseline' ? 'Baseline (unchanged reference)' : data.role === 'test_change' ? 'Test change' : text(data.role)} · replicate ${amount(data.replicate_index)}/${amount(data.replicate_total)} · seed/replay ${amount(data.seed)}`);
  if (text(data.engine_used)) output.push(`Executed engine: ${engineName(data.engine_used)}${numeric(data.wall_time_sec) ? ` · ${data.wall_time_sec} s recorded compute` : ''}`);
  else if (text(data.engine_requested)) output.push(`Selected engine: ${engineName(data.engine_requested)}; actual engine confirmed on return`);
  if (data.cached === true) output.push('Source: saved immutable MD');
  if (data.cached === false) output.push('Source: fresh computation');
  if (data.fresh_requested === true && status === 'started') output.push('New computation requested; waiting for the result');
  const checks = record(data.numerical_check);
  if (typeof checks.is_valid === 'boolean') output.push(`Numerical checks: ${checks.is_valid ? 'passed' : 'failed'} (execution reliability, not a causal verdict)`);
  if (data.outcome === 'NOT_FRACTURED_WITHIN_HORIZON') output.push(`No fracture observed; maximum engineering strain ${amount(data.max_observed_strain)}`);
  if (text(data.error_code)) output.push(`Error code: ${data.error_code}`);
  for (const h of items(data.hypotheses)) {
    const source = h.ai_execution_mode === 'LIVE_MUSE_SPARK_API' ? 'model' : 'heuristic';
    output.push(`${text(h.id)}: ${text(h.title)} · subjective ${source} score ${amount(h.confidence)} (not a measured probability)`);
    if (numeric(h.prediction_pct)) output.push(`${text(h.id)} prediction: ${signedPercent(h.prediction_pct)} recovery (not measured)`);
  }
  for (const p of items(data.proposals)) output.push(`Planned: ${testName(text(p.intervention) || 'unspecified test')} · priority ${amount(p.utility_score)}`);
  const verification = record(data.verification);
  if (Object.keys(verification).length) {
    const valid = verification.execution_status === 'COMPLETE' && verification.numerical_consistency_passed === true;
    output.push(`Execution: ${text(verification.execution_status) || 'not furnished'} · numerical validity: ${verification.numerical_consistency_passed === true ? 'passed' : 'not passed'}`);
    output.push(valid ? `Measured recovery: ${signedPercent(verification.strain_recovery_pct)} · independent verdict: ${text(verification.verdict) || 'not furnished'}` : verification.execution_status === 'EXECUTION_FAILED' || verification.numerical_consistency_passed === false ? 'No scientific verdict from an invalid computation' : 'Scientific verdict unconfirmed: execution or check metadata unavailable');
    if (text(verification.scientific_explanation)) output.push(text(verification.scientific_explanation));
    if (text(verification.statistics_label)) output.push(text(verification.statistics_label));
  }
  for (const change of items(data.belief_changes)) output.push(`${text(change.hypothesis_id)} subjective score: ${amount(change.before)} → ${amount(change.after)} · independent verdict: ${text(change.verifier_status) || 'not furnished'}`);
  const telemetry = record(record(data.receipt).telemetry);
  const mode = telemetry.execution_mode || data.ai_execution_mode;
  if (mode === 'OFFLINE_HEURISTIC_FALLBACK' && status === 'completed') output.push('AI source: offline rule-based fallback');
  else if (telemetry.execution_mode === 'LIVE_MUSE_SPARK_API' && status === 'completed') output.push(`AI source: confirmed live response${text(telemetry.configured_model) ? ` · ${telemetry.configured_model}` : ''}`);
  else if (mode === 'LIVE_MUSE_SPARK_API') output.push('Live model mode is not confirmed by a completed action receipt');
  if (numeric(telemetry.last_call_latency_ms)) output.push(`Provider latency: ${telemetry.last_call_latency_ms} ms`);
  if (numeric(telemetry.prompt_tokens)) output.push(`Provider usage: ${telemetry.prompt_tokens} input${numeric(telemetry.completion_tokens) ? ` / ${telemetry.completion_tokens} output` : ''} tokens`);
  if (text(telemetry.last_error)) output.push(`Provider note: ${telemetry.last_error}`);
  if (text(data.summary)) output.push(text(data.summary));
  if (text(data.execution_status)) output.push(`Worker execution status: ${data.execution_status}`);
  if (text(data.error)) output.push(text(data.error));
  return output;
}

export function buildTerminalRows(events: readonly unknown[], created?: number): TerminalRow[] {
  let contextId: string | null = null;
  const labels = new Map<string,string>(), occurrences = new Map<string,number>();
  return events.map((original,index) => {
    const event = record(original), data = record(event.data), verification = record(data.verification);
    const phase = text(event.phase), status = text(event.status);
    const explicitId = text(data.experiment_id) || text(verification.experiment_id);
    if (explicitId) contextId = explicitId;
    else if (['initialize','worker','observe','hypotheses','plan','conclude','complete'].includes(phase)) contextId = null;
    const groupId = explicitId || (['simulate','verify','revise'].includes(phase) ? contextId : null);
    if (groupId && text(data.intervention)) labels.set(groupId,testName(text(data.intervention)));
    const timestamp = text(event.timestamp) || null;
    const validTime = timestamp && Number.isFinite(Date.parse(timestamp));
    const time = validTime && numeric(created) ? clockLabel(Date.parse(timestamp!)/1000-created) : validTime ? timestamp! : '—';
    const message = text(event.message) || 'Unrecognized event message; inspect the original payload';
    const raw = rawEventJSON(original), metrics = compactMetrics(data,status);
    const baseKey = eventKey(event.job_id,event.seq,index), occurrence = occurrences.get(baseKey) || 0;
    occurrences.set(baseKey,occurrence+1);
    return {key:occurrence ? `${baseKey}:duplicate-${occurrence}` : baseKey, original, raw,
      seq:numeric(event.seq) ? event.seq : null, timestamp, time, phase, status,
      ...eventCategory(event,data), message, metrics, groupId,
      groupLabel:groupId ? labels.get(groupId) || `Comparison ${groupId}` : null,
      groupStart:false, branch:'', searchText:[message,...metrics,raw].join('\n')};
  }).map((row,index,rows) => ({...row, groupStart:!!row.groupId && row.groupId !== rows[index-1]?.groupId,
    branch:row.groupId ? rows[index+1]?.groupId === row.groupId ? '├─' : '└─' : ''}));
}

export function engineName(value: unknown): string {
  return value === 'LAMMPS_BINARY' ? 'LAMMPS' : value === 'NUMPY_VELOCITY_VERLET_2D' ? 'NumPy' : text(value) || 'not reported';
}
export function terminalStatus(status?: string): {label:string;tone:TerminalTone} {
  if (status === 'COMPLETE') return {label:'COMPLETED',tone:'success'};
  if (status === 'RUNNING') return {label:'RUNNING',tone:'progress'};
  if (status === 'QUEUED') return {label:'QUEUED',tone:'warning'};
  if (status === 'CANCELLED') return {label:'CANCELLED',tone:'warning'};
  if (status === 'FAILED') return {label:'FAILED',tone:'error'};
  if (status === 'TIMED_OUT' || status === 'INTERRUPTED') return {label:`FAILED · ${status}`,tone:'error'};
  return {label:typeof status === 'string' && status ? status : 'AWAITING CONFIRMATION',tone:'muted'};
}
export function pendingSimulation(events: readonly unknown[], jobStatus?: string) {
  if (jobStatus !== 'RUNNING') return null;
  const last = record(events.at(-1)), data = record(last.data);
  return last.phase === 'simulate' && last.status === 'started' && text(data.role) && text(data.engine_requested) ? {event:last,data} : null;
}
export function terminalEngine(events: readonly unknown[], jobStatus?: string): string {
  const active = pendingSimulation(events,jobStatus);
  if (active) return `${engineName(active.data.engine_requested)} (selected)`;
  const engines = [...new Set(events.flatMap(value => {const data=record(record(value).data);const engine=text(data.engine_used)||text(record(data.baseline).engine_used);return engine ? [engineName(engine)] : []}))];
  return engines.length ? `${engines.join(' / ')} (recorded)` : 'Awaiting engine report';
}

export function findRanges(value: string, query: string): TextRange[] {
  if (!query.trim()) return [];
  const escaped = query.trim().replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  return [...value.matchAll(new RegExp(escaped,'giu'))].map(match => ({start:match.index!,end:match.index!+match[0].length}));
}
export function searchRows(rows: readonly TerminalRow[], query: string): string[] {
  return query.trim() ? rows.filter(row => findRanges(row.searchText,query).length).map(row => row.key) : [];
}
export function markParts(value: string, ranges: readonly TextRange[], offset=0) {
  let cursor=0;
  const result:{text:string;match:boolean}[]=[];
  for (const range of ranges) {
    const start=Math.max(0,range.start-offset),end=Math.min(value.length,range.end-offset);
    if (end<=start || end<=cursor) continue;
    if (start>cursor) result.push({text:value.slice(cursor,start),match:false});
    result.push({text:value.slice(Math.max(cursor,start),end),match:true});cursor=end;
  }
  if (cursor<value.length) result.push({text:value.slice(cursor),match:false});
  return result;
}
export function jsonTokens(value: string) {
  const regex=/("(?:\\.|[^"\\])*"\s*:)|("(?:\\.|[^"\\])*")|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|\b(true|false|null)\b/g;
  const result:{text:string;kind:string;offset:number}[]=[];
  let cursor=0;
  for (const match of value.matchAll(regex)) {
    if (match.index!>cursor) result.push({text:value.slice(cursor,match.index),kind:'punctuation',offset:cursor});
    result.push({text:match[0],kind:match[1]?'key':match[2]?'string':match[3]?'number':match[0]==='null'?'null':'boolean',offset:match.index!});
    cursor=match.index!+match[0].length;
  }
  if (cursor<value.length) result.push({text:value.slice(cursor),kind:'punctuation',offset:cursor});
  return result;
}
export function toggleExpanded(previous: ReadonlySet<string>, key: string) {
  const next=new Set(previous);if(next.has(key))next.delete(key);else next.add(key);return next;
}
export function exportConsoleJSON(activity: ConsoleActivity | null) {return JSON.stringify(activity,null,2)}
export function readableLog(rows: readonly TerminalRow[], activity: ConsoleActivity | null): string {
  const header=`# NanoForensics / Execution Console\n# Sample ${activity?.job?.case_id || 'not reported'} · Job ${activity?.job?.id || 'not reported'} · ${activity?.job?.status || 'unconfirmed'}\n# Execution success does not establish scientific support.\n`;
  return header+rows.map(row => `${row.timestamp || 'timestamp unavailable'} ${row.time} [${row.tag}] #${row.seq ?? 'unindexed'} ${row.message}${row.metrics.map(metric=>'\n    '+metric).join('')}`).join('\n')+'\n';
}
