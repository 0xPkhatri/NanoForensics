'use client';
import {useEffect, useRef, useState} from 'react';
import {contentCharacters, createConsoleRevealSession, revealContent} from '@/lib/console-reveal';
import type {ConsoleRevealSession} from '@/lib/console-reveal';
import type {ConsoleActivity, ConsoleEvent} from '@/lib/api';
import {clockLabel, confirmedEvents, consoleSteps, currentComparison, eventSource, eventTime, phaseState} from '@/lib/console-view';
import ExecutionTerminal from './ExecutionTerminal';
import {difference, sampleName, sourceLabel, stretch, testName, verdictLabel, verdictTone} from '@/lib/presentation';

function eventDetails(event: ConsoleEvent) {
  const data = event.data;
  return <>
    {data.atom_count != null && <p>{data.case_id} · {data.atom_count} atoms</p>}
    {data.baseline && <p>Original sample: {data.baseline.outcome === 'FRACTURED' ? `${stretch(data.baseline.failure_strain)} stretch at fracture` : data.baseline.outcome === 'EXECUTION_FAILED' ? 'simulation checks failed' : `no fracture observed up to ${stretch(data.baseline.max_observed_strain)}`}. Highest tensile stress: {data.baseline.peak_stress.toFixed(3)} LJ units.</p>}
    {data.hypotheses && <ul className="console-explanations">{data.hypotheses.map(h => <li key={h.id}><strong>{h.id}: {h.title}</strong><small>{sourceLabel(h.ai_execution_mode)} · {h.ai_execution_mode === 'LIVE_MUSE_SPARK_API' ? 'model' : 'heuristic'} score {(h.confidence * 100).toFixed(0)}% · not a measured probability</small></li>)}</ul>}
    {data.proposals && <ul className="console-explanations">{[...data.proposals].sort((a,b) => b.utility_score-a.utility_score).map((proposal,index) => <li key={proposal.experiment_id}><strong>{index + 1}. {testName(proposal.intervention)}</strong><small>Test priority {proposal.utility_score.toFixed(2)} · {sourceLabel(proposal.ai_execution_mode)}</small></li>)}</ul>}
    {data.replicate_index != null && <p>{data.role === 'baseline' ? 'Original reference sample (unchanged)' : 'Changed sample'} · run {data.replicate_index} of {data.replicate_total} · seed/replay label {data.seed}{data.intervention ? ` · comparison: ${testName(data.intervention)}` : ''}</p>}
    {data.engine_used && <p>Executed engine: {data.engine_used === 'LAMMPS_BINARY' ? 'LAMMPS' : 'NumPy'}{data.wall_time_sec != null ? ` · ${data.wall_time_sec.toFixed(2)} s recorded compute` : ''}</p>}
    {event.status === 'started' && data.engine_requested && <p>Selected engine: {data.engine_requested === 'LAMMPS_BINARY' ? 'LAMMPS' : 'NumPy'}. Actual engine and source are confirmed when the run returns. No per-timestep progress is available.</p>}
    {data.numerical_check && <p className={data.numerical_check.is_valid ? 'text-good' : 'text-muted'}>Simulation checks {data.numerical_check.is_valid ? 'passed' : 'failed'}. {data.outcome === 'NOT_FRACTURED_WITHIN_HORIZON' ? 'No fracture was observed within this run.' : data.outcome === 'EXECUTION_FAILED' ? 'This computation cannot support a scientific verdict.' : 'A completed simulation is not a causal verdict.'}</p>}
    {data.verification && <><span className={`badge ${verdictTone(data.verification.verdict, data.verification.numerical_consistency_passed ? data.verification.execution_status : 'EXECUTION_FAILED')}`}>{verdictLabel(data.verification.verdict, data.verification.numerical_consistency_passed ? data.verification.execution_status : 'EXECUTION_FAILED')}</span><p>{data.verification.execution_status === 'COMPLETE' && data.verification.numerical_consistency_passed ? `Measured change in stretch at fracture: ${difference(data.verification.strain_recovery_pct)}.` : 'The calculation cannot provide a valid comparison.'}</p><p>{data.verification.scientific_explanation}</p></>}
    {data.belief_changes && <><p>Subjective explanation scores, not measured probabilities:</p><ul className="console-explanations">{data.belief_changes.map(change => <li key={change.hypothesis_id}>{change.hypothesis_id}: {change.before == null ? 'not recorded' : `${(change.before*100).toFixed(0)}%`} → {(change.after*100).toFixed(0)}%<small>Independent verdict: {verdictLabel(change.verifier_status)}</small></li>)}</ul></>}
    {data.summary && <p>{data.summary}</p>}
    {data.receipt?.telemetry && <p className="caption">{data.receipt.telemetry.configured_model || 'No model configured'} · {data.receipt.telemetry.last_call_latency_ms == null ? 'Latency not furnished' : `${data.receipt.telemetry.last_call_latency_ms.toFixed(0)} ms`}{data.receipt.telemetry.prompt_tokens != null ? ` · ${data.receipt.telemetry.prompt_tokens} input tokens` : ''}</p>}
  </>;
}

function ConsoleEventEntry({event, activity, animate, reducedMotion, session}: {
  event: ConsoleEvent; activity: ConsoleActivity; animate: boolean;
  reducedMotion: boolean; session: ConsoleRevealSession;
}) {
  let details;
  try {details = eventDetails(event)} catch {details = <p>Structured details could not be formatted. The complete original payload remains available below.</p>}
  const message = typeof event.message === 'string' ? event.message : 'Unrecognized event message';
  const titleLength = Array.from(message).length;
  const total = titleLength + contentCharacters(details);
  const [animateOnce] = useState(() => animate && !reducedMotion);
  const [visible, setVisible] = useState(() => animateOnce ? 0 : total);
  const [skip, setSkip] = useState(false);
  const revealing = animateOnce && !reducedMotion && !skip && visible < total;
  useEffect(() => {session.markDisplayed(event.job_id,event.seq)}, [event.job_id,event.seq,session]);
  useEffect(() => {
    if (animateOnce && reducedMotion) {setSkip(true); return}
    if (!animateOnce || skip) return;
    let frame = 0;
    const start = performance.now();
    const duration = Math.min(1200,Math.max(240,total*5));
    const tick = (now: number) => {
      const progress = Math.min(1,(now-start)/duration);
      setVisible(Math.floor(total*progress));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [animateOnce,total,reducedMotion,skip]);
  const title = revealing ? Array.from(message).slice(0,visible).join('') : message;
  const body = revealing ? revealContent(details,{remaining:Math.max(0,visible-titleLength)}) : details;
  const source = eventSource(event);
  return <li className={`console-event ${event.status}${revealing ? ' revealing' : ''}`} aria-label={message}>
    {revealing && <div className="sr-only">{message}{details}</div>}
    <div className="console-event-head"><strong aria-hidden={revealing || undefined}>{title}{revealing && visible < titleLength && <span className="typing-cursor" aria-hidden="true"/>}</strong><time dateTime={event.timestamp} title={new Date(event.timestamp).toLocaleString()}>{eventTime(event,activity)}</time></div>
    {source && <span className={`badge ${event.data?.cached === false ? 'orange' : ''}`}>{source}</span>}
    <>
      <div className="console-event-copy" aria-hidden={revealing || undefined}>{body}{revealing && visible >= titleLength && <span className="typing-cursor" aria-hidden="true"/>}</div>
      {revealing && <div className="reveal-controls"><span>Revealing a received update</span><button onClick={() => setSkip(true)}>Show now</button></div>}
      <details><summary>Technical details</summary><pre className="reportpre" tabIndex={0}>{JSON.stringify(event,null,2)}</pre></details>
    </>
  </li>;
}

export default function InvestigationConsole({activity, submitting = false, request = 0, error = '', caseId, onResults, onEvidence, onTests, inEvidence = false, revealSession}: {
  activity: ConsoleActivity | null; submitting?: boolean; request?: number; error?: string; caseId: string;
  onResults: () => void; onEvidence: () => void; onTests?: () => void; inEvidence?: boolean; revealSession?: ConsoleRevealSession;
}) {
  const [tab, setTab] = useState<'overview'|'technical'>('technical');
  const [follow, setFollow] = useState(true);
  const [reducedMotion, setReducedMotion] = useState(false);
  const localSession = useRef(createConsoleRevealSession());
  const session = revealSession || localSession.current;
  const section = useRef<HTMLElement>(null), list = useRef<HTMLDivElement>(null);
  const confirmed = submitting ? null : activity;
  const job = confirmed?.job;
  const events = confirmedEvents(confirmed);
  const running = !!job && ['QUEUED','RUNNING'].includes(job.status);
  const status = submitting ? 'Submitting request' : job?.status || 'Awaiting job confirmation';
  const completed = !submitting && job?.status === 'COMPLETE';
  const latest = events.at(-1);
  const comparison = currentComparison(confirmed);
  if (job) session.observe(job.id,latest?.seq || 0,request > 0 && !inEvidence);
  const done = consoleSteps.filter(step => phaseState(step.phase, confirmed) === 'completed').length;
  const stopped = !!job && !running && !completed;
  useEffect(() => {
    if (request > 0 && !inEvidence) {
      section.current?.scrollIntoView({behavior:'instant', block:'start'});
      setFollow(true); setTab('technical');
    }
  }, [request, inEvidence]);
  useEffect(() => {
    if (follow && list.current) list.current.scrollTop = list.current.scrollHeight;
  }, [events.length, latest?.seq, follow, tab]);
  useEffect(() => {
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReducedMotion(preference.matches);
    update(); preference.addEventListener('change',update);
    return () => preference.removeEventListener('change',update);
  }, []);
  useEffect(() => {
    const node = list.current, content = node?.querySelector(':scope > ol');
    if (!node || !content || !follow) return;
    // Growing text must keep the viewport at the bottom, not just new cards.
    const observer = new ResizeObserver(() => {node.scrollTop = node.scrollHeight});
    observer.observe(content);
    return () => observer.disconnect();
  }, [follow,tab,job?.id]);
  const download = () => {
    if (!confirmed?.job) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(confirmed, null, 2)], {type:'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = `${confirmed.job.case_id}-${confirmed.job.id}-console.json`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
  };
  const id = inEvidence ? 'evidence-console' : 'investigation-console';
  return <section ref={section} className="panel investigation-console" id={id} aria-label="Investigation console">
    {tab === 'overview' && <><div className="panelhead"><div><span className="overline">NanoForensics · Investigation console</span><h2>{submitting ? 'Starting your investigation…' : running ? 'Follow the work as it happens' : completed ? 'The investigation record' : stopped ? 'The job stopped' : 'Waiting for the worker'}</h2></div><span className={`badge ${completed ? 'good' : stopped ? 'bad' : 'warn'}`}>{status}</span></div>
    <div className="console-context"><span>{sampleName(job?.case_id || caseId)} · <span className="mono">{job?.case_id || caseId}</span></span>{job && <span>{clockLabel(job.elapsed_sec)} elapsed, including queue time</span>}<span>{done}/{consoleSteps.length} stages in this cycle · tests may repeat</span></div></>}
    <div className="console-toolbar"><div className="filter-tabs" role="group" aria-label="Console view"><button aria-pressed={tab === 'overview'} onClick={() => setTab('overview')}>Overview</button><button aria-pressed={tab === 'technical'} onClick={() => setTab('technical')}>Technical log</button></div>{tab === 'overview' && <label className="follow-control"><input type="checkbox" checked={follow} onChange={e => setFollow(e.target.checked)}/>Follow new events</label>}</div>
    {tab === 'overview' && error && <div className="notice" role="alert">Live updates are unavailable. The console retains only the last confirmed records. <details><summary>Connection details</summary><p>{error}</p></details></div>}
    <div hidden={tab !== 'technical'}>
      <ol className="terminal-workflow" aria-label="Current investigation workflow">{consoleSteps.map((step,index)=>{
        const value=phaseState(step.phase,confirmed);
        return <li key={step.phase} className={value} aria-current={value==='running'?'step':undefined} title={`${step.label}: ${value}`}><span aria-hidden="true">{value==='running'?<span className="stage-spinner"/>:value==='completed'?'✓':value==='failed'||value==='stopped'?'!':'○'}</span>{['Initialize','Inspect','Explain','Plan','Simulate','Verify','Update','Conclude','Finish'][index]}<span className="sr-only"> · {value}</span></li>;
      })}</ol>
      <ExecutionTerminal active={tab === 'technical'} activity={confirmed} caseId={caseId} follow={follow} onFollow={setFollow} submitting={submitting} error={error}/>
    </div>
    {tab === 'overview' && <>
    <p className="console-current" role="status" aria-live="polite">{running && <span className="stage-spinner current-spinner" aria-hidden="true"/>}{submitting ? 'Submitting the request. No worker execution has been confirmed yet.' : latest?.message || (job ? 'No detailed console events were recorded for this older job. Run a new investigation to see operation-level progress.' : 'Waiting for the server to confirm a job. No completed steps are assumed.')}</p>
    {comparison && <p className="console-cycle"><strong>{running ? 'Current test' : 'Last test'}:</strong> {testName(comparison.data.intervention || 'Registered comparison')}<span>Simulation, evidence checks and explanation updates refer to this test. Earlier results stay in the log.</span></p>}
    {!follow && <div className="console-follow-paused"><span>Auto-follow is paused. The log may show earlier updates.</span><button onClick={() => setFollow(true)}>Jump to latest</button></div>}
    <div className="console-body">
      {tab === 'overview' && <ol className="console-phases" aria-label="Confirmed investigation stages">{consoleSteps.map(step => {
        const value = phaseState(step.phase, confirmed);
        const label = value === 'waiting' && comparison && ['verify','revise'].includes(step.phase) ? running ? 'Waiting for this test' : 'Not run for this test' : value === 'waiting' && job && !running ? 'Not recorded' : value === 'running' ? 'In progress' : value[0].toUpperCase()+value.slice(1);
        return <li key={step.phase} className={`console-phase ${value}`} aria-current={value === 'running' ? 'step' : undefined}><span className="phase-symbol" aria-hidden="true">{value === 'running' ? <span className="stage-spinner"/> : value === 'completed' ? '✓' : value === 'failed' || value === 'stopped' ? '!' : '○'}</span><div><strong>{step.label}</strong><small>{label}</small></div></li>;
      })}</ol>}
      <div ref={list} className="console-events" tabIndex={0} aria-label="Scrollable confirmed job events" onScroll={e => {const node=e.currentTarget;if (node.scrollHeight-node.scrollTop-node.clientHeight > 55) setFollow(false)}}>
        {!events.length && <div className="empty-state compact"><h3>{submitting ? 'Requesting an isolated worker' : 'No confirmed operation events yet'}</h3><p>New events appear when the backend records them. Waiting steps have no invented times or results.</p></div>}
        <ol>{events.map(event => <ConsoleEventEntry key={`${event.job_id}:${event.seq}`} event={event} activity={confirmed!} animate={!inEvidence && session.shouldReveal(event.job_id,event.seq)} reducedMotion={reducedMotion} session={session}/>)}</ol>
      </div>
    </div>
    </>}
    <div className="console-footer"><div>{tab === 'overview' && <>{job && <span className="mono">Job {job.id}</span>}<p className="caption">Stage status follows confirmed backend events. New text has a display-only typing effect, not provider token streaming. Predictions and model scores are distinct from verified measurements.</p></>}</div><div className="toolbar">{completed && <button className="primary" onClick={job?.kind === 'hypothesize' && onTests ? onTests : onResults}>{job?.kind === 'hypothesize' && onTests ? 'Choose a test ↗' : 'Show results ↗'}</button>}{tab === 'overview' && job && <button onClick={download}>Download log ↓</button>}{!inEvidence && <button onClick={onEvidence}>Review evidence</button>}</div></div>
  </section>;
}
