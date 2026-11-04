import type {Audit, Investigation, Telemetry} from './api';
export interface ActionReceipt {action: string; telemetry: Telemetry; request_hash?: string; response_hash?: string; belief_changes?: {hypothesis_id: string; before: number; after: number; verifier_status: string}[]}
export function actionReceipts(state: Investigation | null | undefined) {
  return (state?.audit_log || []).filter(event => !!(event.provenance as ActionReceipt | undefined)?.telemetry).map(event => ({event, record: event.provenance as ActionReceipt}));
}
export function currentStage(state: Investigation | null | undefined, busy: boolean): number {
  if (!state) return 0;
  if (!busy && ['CONCLUDED', 'INCONCLUSIVE'].includes(state.status)) return 5;
  const last = state.audit_log.at(-1)?.stage || '';
  if (busy) {
    if (/verif|compar|evaluat|belief_revision/.test(last)) return 4;
    if (state.status === 'EXPERIMENTING') return 3;
    if (state.status === 'HYPOTHESIZING') return 1;
    return 0;
  }
  if (state.proposed_experiments.some(p => !state.executed_experiments[p.experiment_id])) return 2;
  if (state.verifications.length) return 4;
  if (state.hypotheses.length) return 1;
  return 0;
}
export const stageNames = ['Inspect', 'Explain', 'Choose a test', 'Run test', 'Check evidence', 'Conclude'];
export function eventCategory(event: Audit): 'ai' | 'simulation' | 'checks' | 'other' {
  if ((event.provenance as ActionReceipt | undefined)?.telemetry || event.stage === 'model_explanation') return 'ai';
  if (/simulation|experiment|cache/.test(event.stage)) return 'simulation';
  if (/verif|compar|evaluat/.test(event.stage)) return 'checks';
  return 'other';
}
