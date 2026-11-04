'use client';
import {useCallback, useEffect, useRef, useState} from 'react';
import {api, terminal} from '@/lib/api';
import type {Case, CaseResponse, Health, Job, ConsoleActivity, DemonstrationStudy, DemonstrationEvaluation} from '@/lib/api';
import {requestGate, workspaces} from '@/lib/presentation';
import type {Workspace} from '@/lib/presentation';

export function useInvestigation() {
  const [workspace, setWorkspace] = useState<Workspace>('original');
  const [selected, setSelected] = useState('');
  const [health, setHealth] = useState<Health | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [data, setData] = useState<CaseResponse | null>(null);
  const [study, setStudy] = useState<DemonstrationStudy | null>(null);
  const [evaluation, setEvaluation] = useState<DemonstrationEvaluation | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const [retry, setRetry] = useState(0);
  const [activity, setActivity] = useState<ConsoleActivity | null>(null);
  const [consoleError, setConsoleError] = useState('');
  const [consoleRequest, setConsoleRequest] = useState(0);
  const [consolePending, setConsolePending] = useState(false);
  const gate = useRef(requestGate());
  const context = useRef('');
  const consoleJob = useRef<string | null>(null);
  const consoleAwaiting = useRef(false);
  const prefix = workspaces[workspace].prefix;
  context.current = `${workspace}/${selected}`;
  const key = `nano-job-${workspace}-${selected}`;
  const busy = pending || !!jobId || !!data?.investigation.is_running || ['QUEUED', 'RUNNING'].includes(activity?.job?.status || '');

  useEffect(() => {
    const saved = localStorage.getItem('nano-workspace');
    if (saved && saved in workspaces) setWorkspace(saved as Workspace);
  }, []);
  useEffect(() => {
    let active = true;
    api<Health>('/health').then(value => {if (active) setHealth(value)}).catch(() => {});
    return () => {active = false};
  }, [retry]);
  useEffect(() => {
    let active = true;
    setLoading(true); setCases([]); setData(null); setStudy(null); setEvaluation(null); setError('');
    api<Case[]>(prefix + '/cases').then(rows => {
      if (!active) return;
      setCases(rows);
      const saved = localStorage.getItem('nano-sample-' + workspace);
      setSelected(rows.some(row => row.case_id === saved) ? saved! : rows[0]?.case_id || '');
      if (!rows.length) setLoading(false);
    }).catch(e => {if (active) {setError(e.message); setLoading(false)}});
    if (workspace !== 'original') {
      api<DemonstrationStudy>(prefix + '/study').then(value => {if (active) setStudy(value)}).catch(e => {if (active) setError(e.message)});
      fetch('/study-evidence/v3/held_out-evaluation.json', {cache: 'no-store'}).then(r => r.ok ? r.json() : null).then(value => {if (active) setEvaluation(value)}).catch(() => {});
    }
    return () => {active = false};
  }, [prefix, workspace, retry]);
  useEffect(() => {
    const token = gate.current.next();
    setData(null); setError(''); setJobId(null); setElapsed(null); setCancelling(false);
    setActivity(null); setConsoleError(''); setConsoleRequest(0); setConsolePending(false);
    consoleJob.current = null; consoleAwaiting.current = false;
    if (!selected) return;
    setLoading(true);
    localStorage.setItem('nano-sample-' + workspace, selected);
    setJobId(localStorage.getItem(key) || (workspace === 'original' ? localStorage.getItem('nano-job-' + selected) : null));
    api<CaseResponse>(`${prefix}/cases/${selected}`).then(value => {
      if (gate.current.isCurrent(token)) {setData(value); setLoading(false)}
    }).catch(e => {if (gate.current.isCurrent(token)) {setError(e.message); setLoading(false)}});
    api<ConsoleActivity>(`${prefix}/cases/${selected}/activity`).then(value => {
      if (!gate.current.isCurrent(token)) return;
      if (consoleAwaiting.current || (consoleJob.current && value.job?.id !== consoleJob.current)) return;
      setActivity(value);
      if (value.job && ['QUEUED', 'RUNNING'].includes(value.job.status)) {
        setJobId(value.job.id); localStorage.setItem(key, value.job.id);
      }
    }).catch(e => {if (gate.current.isCurrent(token)) setConsoleError(e.message)});
    return () => {gate.current.next()};
  }, [selected, prefix, workspace, key, retry]);
  useEffect(() => {
    if (!busy || !selected) return;
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => {
      try {
        const [snapshot, log] = await Promise.allSettled([
          api<CaseResponse>(`${prefix}/cases/${selected}`),
          api<ConsoleActivity>(`${prefix}/cases/${selected}/activity`),
        ]);
        if (!active) return;
        if (snapshot.status === 'fulfilled') setData(snapshot.value);
        else setError(snapshot.reason.message);
        if (log.status === 'fulfilled') {
          if (!consoleAwaiting.current && (!consoleJob.current || log.value.job?.id === consoleJob.current)) setActivity(log.value);
          setConsoleError('');
        }
        else setConsoleError(log.reason.message);
        if (jobId) {
          const job = await api<Job>(`${prefix}/jobs/${jobId}`);
          if (!active) return;
          setElapsed(job.elapsed_sec);
          if (terminal(job.status)) {
            setJobId(null); setCancelling(false); localStorage.removeItem(key);
            if (workspace === 'original') localStorage.removeItem('nano-job-' + selected);
            if (job.status !== 'COMPLETE') setError(`${job.status}: ${job.error || 'See the evidence for details.'}`);
            // Read once more after terminal acknowledgement, retaining the final server state.
            const final = await api<CaseResponse>(`${prefix}/cases/${selected}`);
            if (active) {
              setData(final);
              const history = await api<ConsoleActivity>(`${prefix}/cases/${selected}/activity`);
              if (active && !consoleAwaiting.current && (!consoleJob.current || history.job?.id === consoleJob.current)) setActivity(history);
            }
          }
        }
      } catch (e) {if (active) setError((e as Error).message)}
      finally {if (active) timer = setTimeout(tick, 1200)}
    };
    timer = setTimeout(tick, 800);
    return () => {active = false; clearTimeout(timer)};
  }, [busy, selected, prefix, workspace, jobId, key]);
  const action = useCallback(async (path: string, body: unknown = {}) => {
    if (!selected || busy) return;
    const identity = context.current;
    setPending(true); setElapsed(null); setError('');
    const showConsole = ['hypothesize', 'auto-investigate', 'experiment'].includes(path);
    if (showConsole) {consoleAwaiting.current = true; consoleJob.current = null; setActivity(null); setConsoleError(''); setConsolePending(true); setConsoleRequest(value => value + 1)}
    try {
      const result = await api<{job_id?: string}>(`${prefix}/cases/${selected}/${path}`, body);
      if (context.current !== identity) return;
      if (result.job_id) {consoleJob.current = result.job_id; consoleAwaiting.current = false; setJobId(result.job_id); localStorage.setItem(key, result.job_id)}
      const fresh = await api<CaseResponse>(`${prefix}/cases/${selected}`);
      if (context.current === identity) {
        setData(fresh);
        if (showConsole) {
          try {
            const history = await api<ConsoleActivity>(`${prefix}/cases/${selected}/activity`);
            if (context.current === identity && (!consoleJob.current || history.job?.id === consoleJob.current)) setActivity(history);
          } catch (e) {if (context.current === identity) setConsoleError((e as Error).message)}
        } else if (path === 'reset') {setActivity(null); setConsoleRequest(0)}
      }
    } catch (e) {if (context.current === identity) {setError((e as Error).message); if (showConsole) setConsoleError((e as Error).message)}}
    finally {if (context.current === identity) {setPending(false); setConsolePending(false)}}
  }, [selected, prefix, busy, key]);
  const cancel = async () => {
    if (!jobId || cancelling) return;
    setCancelling(true);
    try {await api(`${prefix}/jobs/${jobId}/cancel`, {})}
    catch (e) {setError((e as Error).message); setCancelling(false)}
  };
  const changeWorkspace = (value: Workspace) => {
    if (busy) return;
    setSelected(''); setData(null); setWorkspace(value); localStorage.setItem('nano-workspace', value);
  };
  const changeSample = (value: string) => {
    if (busy) return;
    gate.current.next(); setData(null); setSelected(value);
  };
  return {workspace, changeWorkspace, selected, setSelected: changeSample, health, cases, data, study, evaluation, activity, consoleError, consoleRequest, consolePending, error, loading, busy, jobId, cancelling, elapsed, action, cancel, retry: () => setRetry(x => x + 1)};
}
