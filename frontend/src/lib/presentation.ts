import type {AIMode, Simulation, Verdict} from './api';

export type Workspace = 'original' | 'demonstration' | 'live';
export type View = 'investigate' | 'results' | 'evidence';
export const workspaces: Record<Workspace, {label: string; description: string; prefix: string}> = {
  original: {label: 'Original samples', description: 'Four preserved samples. The evidence may not identify a clear cause.', prefix: ''},
  demonstration: {label: 'Published study', description: 'Saved deterministic simulations and published findings. No model inference.', prefix: '/demonstrations'},
  live: {label: 'AI investigation', description: 'An isolated rehearsal on published samples. New actions may call Muse Spark.', prefix: '/live-muse'},
};

export const explanationNames: Record<string, {title: string; description: string}> = {
  interior_vacancy: {title: 'Could missing atoms inside matter?', description: 'A gap inside the material could change where stretching damage begins.'},
  surface_notch: {title: 'Could the edge shape matter?', description: 'A gap at a free edge could concentrate stress and change how the material breaks.'},
  high_strain_rate: {title: 'Could it be stretched too quickly?', description: 'Loading speed could change the response. Compare it with the reference rate.'},
  thermal_softening: {title: 'Could temperature affect the result?', description: 'Atomic motion could change rupture behavior. Test the reference temperature.'},
  unknown_stochastic: {title: 'Could this be run-to-run variation?', description: 'Additional runs can test whether the observed difference is repeatable.'},
};

export const testNames: Record<string, string> = {
  heal_interior_vacancy: 'Restore missing interior atoms', smooth_surface_notch: 'Restore missing edge atoms',
  normalize_strain_rate: 'Use the reference stretching rate', normalize_temperature: 'Use the reference temperature',
  repeat_replicate_seeds: 'Repeat with additional runs',
};

export const testName = (name: string) => testNames[name] || name.replaceAll('_', ' ');
export const sampleName = (id: string) => id.startsWith('CASE_') ? 'Sample ' + id.slice(5).toLowerCase().replace(/^./, x => x.toUpperCase()) : id;
export const stretch = (value: number | null | undefined) => value == null ? 'Not available' : `${(value * 100).toFixed(1)}%`;
export const difference = (value: number | null | undefined) => value == null ? 'Not available' : `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
export const sourceLabel = (mode: AIMode) => mode === 'LIVE_MUSE_SPARK_API' ? 'Muse Spark response' : 'Rule-based fallback';
export const verdictLabel = (verdict: Verdict, execution = 'COMPLETE') => execution !== 'COMPLETE' ? 'No scientific verdict' : ({SUPPORTED: 'Evidence supports this', REJECTED: 'Evidence does not support this', INCONCLUSIVE: 'Not enough evidence', PENDING: 'Not tested yet'})[verdict];
export const verdictTone = (verdict: Verdict, execution = 'COMPLETE') => execution !== 'COMPLETE' ? 'bad' : verdict === 'SUPPORTED' ? 'good' : verdict === 'INCONCLUSIVE' ? 'warn' : '';
export function outcomeText(sim: Simulation): string {
  if (sim.outcome === 'EXECUTION_FAILED') return 'Simulation checks failed';
  if (sim.outcome === 'NOT_FRACTURED_WITHIN_HORIZON') return `No fracture observed up to ${stretch(sim.max_observed_strain)} stretch`;
  return sim.failure_strain == null ? 'Fracture measurement unavailable' : `Fracture at ${stretch(sim.failure_strain)} stretch`;
}
export function frameLabel(sim: Pick<Simulation, 'outcome'>, index: number, count: number) {
  if (index === 0) return 'Start';
  if (index === count - 1 && count > 2) return sim.outcome === 'FRACTURED' ? 'Fracture' : 'Last recorded frame';
  return 'Highest load';
}
// Request identities prevent responses for a previous sample from replacing the current view.
export function requestGate() {
  let revision = 0;
  return {next: () => ++revision, isCurrent: (token: number) => token === revision};
}
