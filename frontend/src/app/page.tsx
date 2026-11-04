'use client';
import {useEffect, useMemo, useRef, useState} from 'react';
import {useInvestigation} from '@/hooks/useInvestigation';
import type {View} from '@/lib/presentation';
import {outcomeText, sampleName, stretch, testName} from '@/lib/presentation';
import {currentStage} from '@/lib/investigation-view';
import {createConsoleRevealSession} from '@/lib/console-reveal';
import HeaderBar from '@/components/HeaderBar';
import WorkspaceSelector from '@/components/WorkspaceSelector';
import CurrentStepBanner from '@/components/CurrentStepBanner';
import InvestigationControls from '@/components/InvestigationControls';
import InvestigationConsole from '@/components/InvestigationConsole';
import InvestigationSteps from '@/components/InvestigationSteps';
import LatticeCanvas, {snapshotBounds} from '@/components/LatticeCanvas';
import StressStrainPlot from '@/components/StressStrainPlot';
import HypothesisPanel from '@/components/HypothesisPanel';
import PlannerPanel from '@/components/PlannerPanel';
import EvidenceUpdateCard from '@/components/EvidenceUpdateCard';
import ResultSummary from '@/components/ResultSummary';
import EvidenceTimeline from '@/components/EvidenceTimeline';
import HelpPanel from '@/components/HelpPanel';
import AIActionPanel from '@/components/AIActionPanel';
import AuditReportModal, {downloadReport} from '@/components/AuditReportModal';
import DemoWalkthrough from '@/components/DemoWalkthrough';

export default function Workbench() {
  const app = useInvestigation();
  const {workspace, selected, data, health, busy, study, evaluation} = app;
  const [view, setView] = useState<View>('investigate'), [help, setHelp] = useState(false), [modal, setModal] = useState(false), [comparison, setComparison] = useState(''), [showTest, setShowTest] = useState(false);
  const helpRef = useRef<HTMLDivElement>(null);
  const consoleRevealSession = useRef(createConsoleRevealSession());
  const [guideTarget, setGuideTarget] = useState<{id: string} | null>(null);
  const state = data?.investigation, baseline = data?.case.baseline_simulation;
  const deterministic = workspace !== 'original' && study?.version === 3;
  const counter = comparison ? state?.executed_experiments[comparison] : undefined;
  const bounds = useMemo(() => snapshotBounds([...(baseline?.snapshots || []), ...(counter?.snapshots || [])]), [baseline, counter]);
  const virialLimit = useMemo(() => Math.max(.01, ...[...(baseline?.snapshots || []), ...(counter?.snapshots || [])].flatMap(frame => frame.atoms.map(atom => Math.abs(atom[5])))), [baseline, counter]);
  const validation = evaluation?.rows.find(row => row.case_id === selected);
  useEffect(() => {setComparison(''); setShowTest(false); setView('investigate'); setGuideTarget(null)}, [selected, workspace]);
  useEffect(() => {if (help) helpRef.current?.scrollIntoView({behavior: 'instant', block: 'start'})}, [help]);
  useEffect(() => {
    if (!guideTarget) return;
    const target = document.getElementById(guideTarget.id) || document.getElementById('workspace');
    if (!target) return;
    const previousTabIndex = target.getAttribute('tabindex');
    target.setAttribute('tabindex', '-1');
    target.scrollIntoView({behavior: 'instant', block: 'start'});
    target.focus({preventScroll: true});
    target.classList.add('guide-target');
    const timer = setTimeout(() => target.classList.remove('guide-target'), 2500);
    return () => {
      clearTimeout(timer); target.classList.remove('guide-target');
      if (previousTabIndex == null) target.removeAttribute('tabindex');
      else target.setAttribute('tabindex', previousTabIndex);
    };
  }, [guideTarget, view]);
  const chooseView = (next: View) => {setGuideTarget(null); setView(next)};
  const navigateGuide = (next: View, id: string) => {setView(next); setGuideTarget({id})};
  return <main className="shell"><HeaderBar health={health} state={state || null} registeredStudy={workspace === 'demonstration'} view={view} onView={chooseView} onHelp={() => setHelp(value => !value)}/>
    <div className="page-heading"><div><span className="overline">Small atoms. Big questions.</span><h2>Find out why a simulated material breaks.</h2><p>Look closer. Test an explanation. Let the evidence decide.</p></div><span className="research-stamp">Research workspace<span>2D materials simulation</span></span></div>
    <WorkspaceSelector workspace={workspace} onWorkspace={app.changeWorkspace} cases={app.cases} selected={selected} onSample={app.setSelected} busy={busy}/>
    <InvestigationControls state={state} busy={busy} ready={!!data && !app.loading} onRun={() => {chooseView('investigate'); app.action('auto-investigate')}} onSuggest={() => {chooseView('investigate'); app.action('hypothesize')}} onResults={() => chooseView('results')} onReset={() => {if (window.confirm('Reset this investigation? Current explanations, progress and conclusions will be cleared. Saved simulation records remain preserved.')) app.action('reset')}}/>
    {view !== 'evidence' && (app.consolePending || app.consoleRequest > 0 || !!app.activity?.events.length) && <InvestigationConsole revealSession={consoleRevealSession.current} onTests={() => navigateGuide('investigate','plan')} activity={app.activity} submitting={app.consolePending} request={app.consoleRequest} error={app.consoleError} caseId={selected} onResults={() => {chooseView('results'); setGuideTarget({id:'verify'})}} onEvidence={() => {chooseView('evidence'); setGuideTarget({id:'evidence-console'})}}/>}
    <CurrentStepBanner state={state} busy={busy} stage={currentStage(state, busy)} elapsed={app.elapsed} cancelling={app.cancelling} canCancel={!!app.jobId} onCancel={app.cancel}/>
    <InvestigationSteps stage={currentStage(state, busy)}/>
    {app.error && <div className="error" role="alert"><div><strong>We could not complete that request.</strong><p>{app.error}</p></div><button onClick={app.retry} disabled={busy}>Retry connection</button></div>}
    <div id="workspace" tabIndex={-1}>
    {baseline && state && data ? <>
      <div className="section-title"><div><span className="overline">{view === 'investigate' ? 'Explore & test' : view === 'results' ? 'Compare & understand' : 'Inspect & reproduce'}</span><h2>{view === 'investigate' ? sampleName(selected) : view === 'results' ? 'Follow the measured result' : 'The evidence behind the answer'}</h2></div><span className="sample-id mono">{selected} · {data.case.atom_count} atoms</span></div>
      {(baseline.outcome === 'EXECUTION_FAILED' || !baseline.numerical_check.is_valid) && <div className="notice"><strong>The original simulation did not pass all checks.</strong><p>Recorded curves are available for inspection. Failed runs cannot support a causal conclusion; valid runs are checked separately.</p></div>}
      {view !== 'evidence' && <div className="comparison-strip"><span><i className="line-key"/>Original sample <strong>{stretch(baseline.max_observed_strain)} recorded stretch</strong></span><label>Compare with<select aria-label="Counterfactual comparison" value={comparison} onChange={e => {setComparison(e.target.value); setShowTest(false)}}><option value="">Original sample only</option>{Object.keys(state.executed_experiments).map(id => <option key={id} value={id}>{testName(state.proposed_experiments.find(p => p.experiment_id === id)?.intervention || id)}</option>)}</select></label></div>}
      {view === 'investigate' && <div className="investigation-grid"><div className="material-stack">{counter && <div className="viewer-switch" role="group" aria-label="Displayed material"><button aria-pressed={!showTest} onClick={() => setShowTest(false)}>Original sample</button><button aria-pressed={showTest} onClick={() => setShowTest(true)}>Selected test change</button></div>}<LatticeCanvas simulation={showTest && counter ? counter : baseline} bounds={bounds} virialLimit={virialLimit} title={showTest && counter ? 'The material · test change' : 'The material · original sample'}/><StressStrainPlot baseline={baseline} counterfactual={counter} deterministic={deterministic}/></div><aside className="story-stack"><EvidenceUpdateCard sample={data.case} state={state}/><PlannerPanel proposals={state.proposed_experiments} completed={Object.keys(state.executed_experiments)} busy={busy} onRun={id => app.action('experiment', {proposal_id: id})}/></aside><div className="explanations-area"><HypothesisPanel hypotheses={state.hypotheses} deterministic={deterministic}/></div></div>}
      {view === 'results' && <div className="results-stack"><ResultSummary state={state} baseline={baseline} deterministic={deterministic} onEvidence={() => chooseView('evidence')}/><div className="stats"><div className="stat"><span>Highest original tensile stress</span><strong>{baseline.peak_stress.toFixed(3)} <small>LJ units</small></strong><p>{deterministic ? 'Deterministic replay, not a thermal sample' : `Run spread ±${baseline.peak_stress_std.toFixed(3)}`}</p></div><div className="stat"><span>Original fracture measurement</span><strong>{baseline.outcome === 'FRACTURED' ? stretch(baseline.failure_strain) : 'Not available'}</strong><p>{outcomeText(baseline)}</p></div><div className="stat"><span>Recorded test comparisons</span><strong>{state.verifications.length}</strong><p>Execution and evidence are checked separately</p></div></div><StressStrainPlot baseline={baseline} counterfactual={counter} deterministic={deterministic}/>{counter && <div className="grid2"><LatticeCanvas simulation={baseline} bounds={bounds} virialLimit={virialLimit} title="Original sample"/><LatticeCanvas simulation={counter} bounds={bounds} virialLimit={virialLimit} title="Selected test change"/></div>}<HypothesisPanel hypotheses={state.hypotheses} deterministic={deterministic}/></div>}
      {view === 'evidence' && <div className="evidence-stack"><div className="report-banner"><div><h3>A readable trail. The full record.</h3><p>Saved simulations, actual action sources, checks and immutable run identities.</p></div><div className="toolbar"><button onClick={() => setModal(true)}>Open full report</button><button className="primary" onClick={() => downloadReport(state)}>Download evidence ↓</button></div></div><InvestigationConsole revealSession={consoleRevealSession.current} onTests={() => navigateGuide('investigate','plan')} activity={app.activity} submitting={app.consolePending} error={app.consoleError} caseId={selected} onResults={() => {chooseView('results'); setGuideTarget({id:'verify'})}} onEvidence={() => chooseView('evidence')} inEvidence/><EvidenceTimeline state={state}/><AIActionPanel state={state}/><section className="panel"><div className="panelhead"><h2>Simulation records</h2></div><div className="panelbody">{[[baseline, 'Original sample'] as const, ...Object.entries(state.executed_experiments).map(([id, sim]) => [sim, testName(state.proposed_experiments.find(p => p.experiment_id === id)?.intervention || id)] as const)].map(([sim, name]) => <details className="run-record" key={sim.sim_id}><summary>{name} · {outcomeText(sim)}</summary><dl className="technical-grid"><dt>Simulation ID</dt><dd>{sim.sim_id}</dd><dt>Engine / version</dt><dd>{sim.engine_used} / {sim.solver_version}</dd><dt>Units</dt><dd>{sim.units}</dd><dt>Measurement horizon</dt><dd>{stretch(sim.max_observed_strain)} stretch</dd><dt>Compute time</dt><dd>{sim.wall_time_sec.toFixed(2)} s</dd><dt>Protocol hash</dt><dd>{sim.protocol_hash}</dd><dt>Configuration hash</dt><dd>{sim.initial_configuration_hash}</dd><dt>Seed / replay labels</dt><dd>{sim.replicate_seeds.join(', ')}</dd></dl><p className="caption">{sim.numerical_check.notes}</p><p className="caption">{sim.replicate_results.length} replicate records. Complete numerical checks, geometry conventions and per-run outcomes are retained in the JSON report.</p></details>)}</div></section></div>}
      <div className="bottom-tools">{workspace === 'original' && <button className="text-button" disabled={busy} onClick={() => {localStorage.setItem('nano-sample-demonstration', 'DEMO_501'); app.changeWorkspace('demonstration'); setHelp(true)}}>Explore the guided example ↗</button>}{workspace !== 'original' && <details><summary>Investigation guide</summary><DemoWalkthrough onNavigate={navigateGuide}/></details>}</div>
      {modal && <AuditReportModal state={state} onClose={() => setModal(false)} deterministic={deterministic}/>}
    </> : <section className="panel loading-panel" aria-busy={app.loading}><div className="panelbody">{app.error ? <><h2>Simulation service unavailable</h2><p>We could not load this workspace. Retry the connection above.</p></> : app.loading ? <><span className="spinner" aria-hidden="true"/><h2>Loading your material sample</h2><p>Connecting to real, recorded simulations…</p><div className="skeleton"/></> : <><h2>No simulated samples are available yet</h2><p>This workspace needs a generated or restored dataset.</p><button onClick={app.retry}>Check again</button></>}<details><summary>Local setup help</summary><p className="caption">Start the API with <code>make backend</code> and frontend with <code>make frontend</code>. Original data generation uses <code>make data</code>; existing frozen records must not be overwritten.</p></details></div></section>}
    </div>
    {help && <div ref={helpRef}><div className="row-between help-title"><h2>How NanoForensics works</h2><button onClick={() => setHelp(false)}>Close guide ×</button></div><HelpPanel/></div>}
    {workspace !== 'original' && <aside className="study-note study-scope"><details><summary>Study scope and this sample</summary><div><strong>Full published study: {study?.validation_status || 'loading status…'}</strong><p>{study?.validation_status === 'NOT_VALIDATED' ? 'The complete study did not meet all its preset criteria.' : study?.validation_status === 'HELD_OUT_VALIDATED' ? 'Registered held-out criteria passed within the published study scope.' : 'Read the published status and scope before interpreting results.'} {workspace === 'live' ? 'This AI workspace is a post-study rehearsal, not a new blinded validation.' : 'Saved study findings use deterministic tools, without model inference.'}</p></div><a href="/study-evidence/v3/STUDY_REPORT.md" target="_blank" rel="noreferrer">Read the study ↗</a><p>{study?.scope}</p><p className="caption">{study?.study_id} · {data?.case.observed_configuration?.study_partition || 'Partition not loaded'}</p>{validation && <p>{validation.passed ? 'This geometry met its registered checks.' : 'This geometry did not validate a repair.'} {validation.scoring} · Timestep convergence: {validation.timestep_convergence == null ? 'not applicable' : validation.timestep_convergence ? 'passed' : 'not passed'}.</p>}<p className="caption">V3 is an athermal deterministic reference, not a thermal population study. Earlier negative development studies remain archived. Replay labels are not independent thermal samples.</p><p className="caption mono">Registration {study?.registration_hash || '—'}<br/>Public protocol: {JSON.stringify(data?.case.observed_configuration?.public_protocol || {})}</p></details></aside>}
    <footer className="footer"><span><strong>NanoForensics</strong> / Push the frontier</span><p>A 2D Lennard-Jones computational testbed. Results do not validate real engineering materials.</p><a href="#workspace">Back to workspace ↑</a></footer>
  </main>;
}
