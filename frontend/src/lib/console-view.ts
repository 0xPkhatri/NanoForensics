import type {ConsoleActivity, ConsoleEvent, ConsolePhase} from './api';
export const consoleSteps: {phase: ConsolePhase; label: string}[] = [
  {phase:'initialize',label:'Initialize'}, {phase:'observe',label:'Inspect the sample'},
  {phase:'hypotheses',label:'Suggest explanations'}, {phase:'plan',label:'Plan tests'},
  {phase:'simulate',label:'Run simulations'}, {phase:'verify',label:'Check evidence'},
  {phase:'revise',label:'Update explanations'}, {phase:'conclude',label:'Conclude'},
  {phase:'complete',label:'Finish job'},
];
// Verification and revision repeat for each comparison. Their earlier completions
// remain in the log, but cannot check off a later experiment's pending stages.
export function currentComparison(activity: ConsoleActivity | null) {
  return [...confirmedEvents(activity)].reverse().find(event =>
    event.phase === 'simulate' && !!event.data.experiment_id &&
    (event.status === 'skipped' || (event.status === 'started' && !event.data.role)));
}
export type PhaseState = 'waiting'|'running'|'completed'|'failed'|'skipped'|'stopped';
export function phaseState(phase: ConsolePhase, activity: ConsoleActivity | null): PhaseState {
  const cycle = ['simulate','verify','revise'].includes(phase) ? currentComparison(activity) : undefined;
  const relevant = confirmedEvents(activity).filter(event => event.phase === phase && (!cycle || event.seq >= cycle.seq));
  if (!relevant.length) return 'waiting';
  const last = relevant.at(-1)!;
  let state: PhaseState = last.status === 'started' ? 'running' : last.status;
  // A finished replicate is not a finished comparison. Wait for the explicit
  // comparison boundary before checking off the simulation phase.
  if (phase === 'simulate' && last.status === 'completed' && !last.data.comparison_complete) state = 'running';
  if (state === 'running' && activity?.job && !['QUEUED','RUNNING'].includes(activity.job.status)) return 'stopped';
  return state;
}
export const clockLabel = (seconds: number) => `${Math.floor(Math.max(0,seconds)/60).toString().padStart(2,'0')}:${Math.floor(Math.max(0,seconds)%60).toString().padStart(2,'0')}`;
export function eventTime(event: ConsoleEvent, activity: ConsoleActivity) {
  const created = activity.job?.created;
  return created == null ? '—' : clockLabel((Date.parse(event.timestamp)/1000) - created);
}
export function eventSource(event: ConsoleEvent): string | null {
  const receiptMode = event.data.receipt?.telemetry?.execution_mode;
  const mode = receiptMode || event.data.ai_execution_mode;
  if (receiptMode === 'LIVE_MUSE_SPARK_API' && event.status === 'completed') return 'Confirmed live model response';
  if (mode === 'OFFLINE_HEURISTIC_FALLBACK' && event.status === 'completed') return 'Rule-based fallback';
  if (event.data.cached === true) return 'Saved immutable simulation';
  if (event.data.cached === false) return 'Fresh simulation';
  if (event.phase === 'observe') return 'Stored baseline measurements';
  return null;
}
export function confirmedEvents(activity: ConsoleActivity | null) {
  return (activity?.events || []).filter(event => event.job_id === activity?.job?.id);
}
