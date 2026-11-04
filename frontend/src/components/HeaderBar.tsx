import type {Health, Investigation} from '@/lib/api';
import type {View} from '@/lib/presentation';
import {actionReceipts} from '@/lib/investigation-view';
export default function HeaderBar({health, state, registeredStudy = false, view, onView, onHelp}: {health: Health | null; state: Investigation | null; registeredStudy?: boolean; view: View; onView: (view: View) => void; onHelp: () => void}) {
  const last = actionReceipts(state).at(-1);
  const telemetry = last?.record.telemetry;
  const live = !registeredStudy && telemetry?.execution_mode === 'LIVE_MUSE_SPARK_API';
  return <>
    <a className="skip-link" href="#workspace">Skip to investigation</a>
    <header className="topbar">
      <a className="logo" href="/" aria-label="NanoForensics home"><span className="brand-mark" aria-hidden="true">N<span>F</span></span><span>Nano<span className="brand-accent">Forensics</span><small>A closer look at why materials break</small></span></a>
      <nav className="mainnav" aria-label="Main navigation">{(['investigate', 'results', 'evidence'] as View[]).map(name => <button key={name} aria-current={view === name ? 'page' : undefined} onClick={() => onView(name)}>{name[0].toUpperCase() + name.slice(1)}</button>)}</nav>
      <button className="help-button" onClick={onHelp}><span aria-hidden="true">?</span> How it works</button>
    </header>
    <div className="systembar"><span><i className={health ? 'status-dot' : 'status-dot pending'} aria-hidden="true"/>{health ? `Physics: ${health.engine.engine === 'LAMMPS_BINARY' ? 'LAMMPS' : 'NumPy'}` : 'Connecting to physics service'}</span><span className={live ? 'text-good' : 'text-muted'}>{registeredStudy ? 'Saved study · no model inference' : last ? `${live ? 'Last AI action: Muse Spark' : 'Offline mode · rule-based suggestions'} · ${new Date(last.event.timestamp).toLocaleString()}` : health?.ai_telemetry.execution_mode === 'LIVE_MUSE_SPARK_API' ? 'AI connection checked · no action yet' : 'No AI action yet · rule-based fallback available'}</span><details><summary>System details</summary><div className="system-details"><p>Physics: {health?.engine.engine || 'Connecting'} · shifted-force Lennard-Jones (SFLJ)</p><p>Action mode: {registeredStudy ? 'OFFLINE_HEURISTIC_FALLBACK · deterministic study tools' : telemetry?.execution_mode || 'No recorded AI action'}</p>{telemetry && <p>{telemetry.configured_model} · {telemetry.base_url} · {telemetry.last_call_latency_ms?.toFixed(0) ?? '—'} ms</p>}{telemetry?.last_error && <p>{telemetry.last_error}</p>}<p>Live receipts describe past responses. A new action needs a new successful response.</p></div></details></div>
  </>;
}
