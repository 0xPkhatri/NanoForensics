'use client';
import {useEffect, useRef, useState} from 'react';
import type {ConsoleActivity, ConsoleEvent} from '@/lib/api';
import {clockLabel, confirmedEvents, consoleSteps, eventSource, eventTime, phaseState} from '@/lib/console-view';
import {difference, sampleName, sourceLabel, stretch, testName, verdictLabel, verdictTone} from '@/lib/presentation';

function EventDetails({event}: {event: ConsoleEvent}) {
  const data = event.data;
  return <>
    {data.atom_count != null && <p>{data.case_id} · {data.atom_count} atoms</p>}
    {data.baseline && <p>Original sample: {data.baseline.outcome === 'FRACTURED' ? `${stretch(data.baseline.failure_strain)} stretch at fracture` : data.baseline.outcome === 'EXECUTION_FAILED' ? 'simulation checks failed' : `no fracture observed up to ${stretch(data.baseline.max_observed_strain)}`}. Highest tensile stress: {data.baseline.peak_stress.toFixed(3)} LJ units.</p>}
    {data.hypotheses && <ul className="console-explanations">{data.hypotheses.map(h => <li key={h.id}><strong>{h.id}: {h.title}</strong><small>{sourceLabel(h.ai_execution_mode)} · {h.ai_execution_mode === 'LIVE_MUSE_SPARK_API' ? 'model' : 'heuristic'} score {(h.confidence * 100).toFixed(0)}% · not a measured probability</small></li>)}</ul>}
    {data.proposals && <ul className="console-explanations">{[...data.proposals].sort((a,b) => b.utility_score-a.utility_score).map((proposal,index) => <li key={proposal.experiment_id}><strong>{index + 1}. {testName(proposal.intervention)}</strong><small>Test priority {proposal.utility_score.toFixed(2)} · {sourceLabel(proposal.ai_execution_mode)}</small></li>)}</ul>}
    {data.replicate_index != null && <p>{data.role === 'baseline' ? 'Original sample' : 'Test change'} · run {data.replicate_index} of {data.replicate_total} · seed/replay label {data.seed}{data.intervention ? ` · ${testName(data.intervention)}` : ''}</p>}
    {data.engine_used && <p>Executed engine: {data.engine_used === 'LAMMPS_BINARY' ? 'LAMMPS' : 'NumPy'}{data.wall_time_sec != null ? ` · ${data.wall_time_sec.toFixed(2)} s recorded compute` : ''}</p>}
    {event.status === 'started' && data.engine_requested && <p>Selected engine: {data.engine_requested === 'LAMMPS_BINARY' ? 'LAMMPS' : 'NumPy'}. Actual engine and source are confirmed when the run returns. No per-timestep progress is available.</p>}
    {data.numerical_check && <p className={data.numerical_check.is_valid ? 'text-good' : 'text-muted'}>Simulation checks {data.numerical_check.is_valid ? 'passed' : 'failed'}. {data.outcome === 'NOT_FRACTURED_WITHIN_HORIZON' ? 'No fracture was observed within this run.' : data.outcome === 'EXECUTION_FAILED' ? 'This computation cannot support a scientific verdict.' : 'A completed simulation is not a causal verdict.'}</p>}
    {data.verification && <><span className={`badge ${verdictTone(data.verification.verdict, data.verification.numerical_consistency_passed ? data.verification.execution_status : 'EXECUTION_FAILED')}`}>{verdictLabel(data.verification.verdict, data.verification.numerical_consistency_passed ? data.verification.execution_status : 'EXECUTION_FAILED')}</span><p>{data.verification.execution_status === 'COMPLETE' && data.verification.numerical_consistency_passed ? `Measured change in stretch at fracture: ${difference(data.verification.strain_recovery_pct)}.` : 'The calculation cannot provide a valid comparison.'}</p><p>{data.verification.scientific_explanation}</p></>}
    {data.belief_changes && <><p>Subjective explanation scores, not measured probabilities:</p><ul className="console-explanations">{data.belief_changes.map(change => <li key={change.hypothesis_id}>{change.hypothesis_id}: {change.before == null ? 'not recorded' : `${(change.before*100).toFixed(0)}%`} → {(change.after*100).toFixed(0)}%<small>Independent verdict: {verdictLabel(change.verifier_status)}</small></li>)}</ul></>}
    {data.summary && <p>{data.summary}</p>}
    {data.receipt?.telemetry && <p className="caption">{data.receipt.telemetry.configured_model || 'No model configured'} · {data.receipt.telemetry.last_call_latency_ms == null ? 'Latency not furnished' : `${data.receipt.telemetry.last_call_latency_ms.toFixed(0)} ms`}{data.receipt.telemetry.prompt_tokens != null ? ` · ${data.receipt.telemetry.prompt_tokens} input tokens` : ''}</p>}
  </>;
}

export default function InvestigationConsole({activity, submitting = false, request = 0, error = '', caseId, onResults, onEvidence, onTests, inEvidence = false}: {
  activity: ConsoleActivity | null; submitting?: boolean; request?: number; error?: string; caseId: string;
  onResults: () => void; onEvidence: () => void; onTests?: () => void; inEvidence?: boolean;
}) {
  const [tab, setTab] = useState<'overview'|'technical'>('overview');
  const [follow, setFollow] = useState(true);
  const section = useRef<HTMLElement>(null), list = useRef<HTMLDivElement>(null);
  const confirmed = submitting ? null : activity;
  const job = confirmed?.job;
  const events = confirmedEvents(confirmed);
  const running = !!job && ['QUEUED','RUNNING'].includes(job.status);
  const status = submitting ? 'Submitting request' : job?.status || 'Awaiting job confirmation';
  const completed = !submitting && job?.status === 'COMPLETE';
  const latest = events.at(-1);
  const done = consoleSteps.filter(step => phaseState(step.phase, confirmed) === 'completed').length;
  const stopped = !!job && !running && !completed;
  useEffect(() => {
    if (request > 0 && !inEvidence) {
      section.current?.scrollIntoView({behavior:'instant', block:'start'});
      setFollow(true); setTab('overview');
    }
  }, [request, inEvidence]);
  useEffect(() => {
    if (follow && list.current) list.current.scrollTop = list.current.scrollHeight;
  }, [events.length, latest?.seq, follow, tab]);
  const download = () => {
    if (!confirmed?.job) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(confirmed, null, 2)], {type:'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = `${confirmed.job.case_id}-${confirmed.job.id}-console.json`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
  };
  const id = inEvidence ? 'evidence-console' : 'investigation-console';
  return <section ref={section} className="panel investigation-console" id={id} aria-label="Investigation console">
    <div className="panelhead"><div><span className="overline">NanoForensics · Investigation console</span><h2>{submitting ? 'Starting your investigation…' : running ? 'Follow the work as it happens' : completed ? 'The investigation record' : stopped ? 'The job stopped' : 'Waiting for the worker'}</h2></div><span className={`badge ${completed ? 'good' : stopped ? 'bad' : 'warn'}`}>{status}</span></div>
    <div className="console-context"><span>{sampleName(job?.case_id || caseId)} · <span className="mono">{job?.case_id || caseId}</span></span>{job && <span>{clockLabel(job.elapsed_sec)} elapsed, including queue time</span>}<span>{done}/{consoleSteps.length} stages confirmed · stages may repeat or be omitted</span></div>
    <div className="console-toolbar"><div className="filter-tabs" role="group" aria-label="Console view"><button aria-pressed={tab === 'overview'} onClick={() => setTab('overview')}>Overview</button><button aria-pressed={tab === 'technical'} onClick={() => setTab('technical')}>Technical log</button></div><label className="follow-control"><input type="checkbox" checked={follow} onChange={e => setFollow(e.target.checked)}/>Follow new events</label></div>
    {error && <div className="notice" role="alert">Live updates are unavailable. The console retains only the last confirmed records. <details><summary>Connection details</summary><p>{error}</p></details></div>}
    <p className="console-current" role="status" aria-live="polite">{submitting ? 'Submitting the request. No worker execution has been confirmed yet.' : latest?.message || (job ? 'No detailed console events were recorded for this older job. Run a new investigation to see operation-level progress.' : 'Waiting for the server to confirm a job. No completed steps are assumed.')}</p>
    <div className="console-body">
      {tab === 'overview' && <ol className="console-phases" aria-label="Confirmed investigation stages">{consoleSteps.map(step => {
        const value = phaseState(step.phase, confirmed);
        const label = value === 'waiting' && job && !running ? 'Not recorded' : value === 'running' ? 'In progress' : value[0].toUpperCase()+value.slice(1);
        return <li key={step.phase} className={`console-phase ${value}`}><span className="phase-symbol" aria-hidden="true">{value === 'completed' ? '✓' : value === 'running' ? '●' : value === 'failed' || value === 'stopped' ? '!' : '○'}</span><div><strong>{step.label}</strong><small>{label}</small></div></li>;
      })}</ol>}
      <div ref={list} className="console-events" tabIndex={0} aria-label="Scrollable confirmed job events" onScroll={e => {const node=e.currentTarget;if (node.scrollHeight-node.scrollTop-node.clientHeight > 55) setFollow(false)}}>
        {!events.length && <div className="empty-state compact"><h3>{submitting ? 'Requesting an isolated worker' : 'No confirmed operation events yet'}</h3><p>New events appear when the backend records them. Waiting steps have no invented times or results.</p></div>}
        <ol>{events.map(event => <li key={event.seq} className={`console-event ${event.status}`}><div className="console-event-head"><strong>{event.message}</strong><time dateTime={event.timestamp} title={new Date(event.timestamp).toLocaleString()}>{activity ? eventTime(event,activity) : '—'}</time></div>{eventSource(event) && <span className={`badge ${event.data.cached === false ? 'orange' : ''}`}>{eventSource(event)}</span>}{tab === 'overview' ? <><EventDetails event={event}/><details><summary>Technical details</summary><pre className="reportpre" tabIndex={0}>{JSON.stringify(event,null,2)}</pre></details></> : <details><summary>{event.phase} · {event.status} · event {event.seq}</summary><pre className="reportpre" tabIndex={0}>{JSON.stringify(event,null,2)}</pre></details>}</li>)}</ol>
      </div>
    </div>
    <div className="console-footer"><div>{job && <span className="mono">Job {job.id}</span>}<p className="caption">Recorded status, not an animated simulation of progress. Predictions and model scores are distinct from independently verified measurements.</p></div><div className="toolbar">{completed && <button className="primary" onClick={job?.kind === 'hypothesize' && onTests ? onTests : onResults}>{job?.kind === 'hypothesize' && onTests ? 'Choose a test ↗' : 'Show results ↗'}</button>}{job && <button onClick={download}>Download log ↓</button>}{!inEvidence && <button onClick={onEvidence}>Review evidence</button>}</div></div>
  </section>;
}
