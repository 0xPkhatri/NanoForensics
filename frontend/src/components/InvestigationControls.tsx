import type {Investigation} from '@/lib/api';

export default function InvestigationControls({state, busy, ready, onRun, onSuggest, onReset, onResults}: {
  state?: Investigation;
  busy: boolean;
  ready: boolean;
  onRun: () => void;
  onSuggest: () => void;
  onReset: () => void;
  onResults: () => void;
}) {
  const complete = !busy && ['CONCLUDED', 'INCONCLUSIVE'].includes(state?.status || '');
  return <section className="investigation-controls" aria-label="Choose investigation mode">
    <div className="investigation-mode">
      <div><span className="overline">Choose how to explore</span><p>{complete ? 'Your investigation has results to explore.' : 'Let the system guide you through the complete investigation.'}</p></div>
      <div className="toolbar"><button className="primary" disabled={!ready || busy} onClick={complete ? onResults : onRun}>{busy ? 'Investigation running…' : complete ? 'View results' : 'Run full investigation'} <span aria-hidden="true">↗</span></button>{complete && <button onClick={onRun} disabled={!ready}>Investigate again</button>}</div>
    </div>
    <details className="step-by-step"><summary>Explore step by step</summary><div className="manual-controls"><div><h3>Start with possible explanations</h3><p>Suggest possible causes, then choose individual tests in the investigation view. This replaces the current investigation's explanations and progress; saved simulation records remain preserved.</p><button disabled={!ready || busy} onClick={onSuggest}>Suggest possible causes</button></div><div className="reset-controls"><p>Want to clear this investigation and start over?</p><button className="text-button reset-button" disabled={!ready || busy} onClick={onReset}>Reset investigation</button><small>A confirmation is required. Saved simulations are preserved.</small></div></div></details>
  </section>;
}
