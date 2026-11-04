'use client';
import {useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState} from 'react';
import type {ConsoleActivity} from '@/lib/api';
import {clockLabel} from '@/lib/console-view';
import {buildTerminalRows, engineName, exportConsoleJSON, findRanges, pendingSimulation, readableLog, record, searchRows, terminalEngine, terminalStatus, toggleExpanded} from '@/lib/terminal-format';
import type {TerminalRow} from '@/lib/terminal-format';
import {copyLogText} from '@/lib/clipboard';
import {useLogFollow} from '@/hooks/useLogFollow';
import {TerminalEventRow} from './TerminalEventRow';

const EMPTY:unknown[]=[];
export default function ExecutionTerminal({activity,caseId,follow,onFollow,submitting=false,error='',active=true}:{
  activity:ConsoleActivity|null;caseId:string;follow:boolean;onFollow:(value:boolean)=>void;submitting?:boolean;error?:string;active?:boolean;
}) {
  const job=activity?.job;
  const rawEvents=Array.isArray(activity?.events)?activity.events:EMPTY;
  const rows=useMemo(()=>buildTerminalRows(rawEvents,job?.created),[rawEvents,job?.created]);
  const [query,setQuery]=useState(''),[matchesOnly,setMatchesOnly]=useState(false);
  const [open,setOpen]=useState<Set<string>>(new Set()),[selectedKey,setSelectedKey]=useState<string|null>(null),[jump,setJump]=useState(0);
  const [expanded,setExpanded]=useState(false),[notice,setNotice]=useState('');
  const terminal=useRef<HTMLElement>(null),rowNodes=useRef(new Map<string,HTMLLIElement>());
  const matches=useMemo(()=>searchRows(rows,query),[rows,query]);
  const matchingKeys=useMemo(()=>new Set(matches),[matches]);
  const visibleRows=matchesOnly && query.trim()?rows.filter(row=>matchingKeys.has(row.key)):rows;
  const activeKey=selectedKey && matchingKeys.has(selectedKey)?selectedKey:matches[0];
  const selectedIndex=activeKey?matches.indexOf(activeKey):-1;
  const state=submitting?{label:'SUBMITTING',tone:'muted' as const}:terminalStatus(job?.status);
  const scroll=useLogFollow(follow,onFollow,`${job?.id||''}:${rows.at(-1)?.key||''}:${visibleRows.length}`,active);
  const activeRun=pendingSimulation(rawEvents,job?.status);
  const activeTimestamp=activeRun?Date.parse(String(activeRun.event.timestamp)):NaN;
  const runElapsed=job && Number.isFinite(job.elapsed_sec) && Number.isFinite(activeTimestamp)?Math.max(0,job.elapsed_sec-(activeTimestamp/1000-job.created)):null;
  const register=useCallback((key:string,node:HTMLLIElement|null)=>{if(node)rowNodes.current.set(key,node);else rowNodes.current.delete(key)},[]);
  const pause=scroll.pause;
  const toggle=useCallback((key:string)=>{pause();setOpen(previous=>toggleExpanded(previous,key))},[pause]);
  useEffect(()=>{if(!active)setExpanded(false)},[active]);
  useEffect(()=>{setOpen(new Set());setSelectedKey(null);setNotice('')},[job?.id]);
  useLayoutEffect(()=>{if(selectedKey)rowNodes.current.get(selectedKey)?.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'})},[selectedKey,jump]);
  useEffect(()=>{
    if(!expanded || !active)return;
    const previous=document.activeElement as HTMLElement|null,overflow=document.body.style.overflow;
    document.body.style.overflow='hidden';terminal.current?.focus();
    const handler=(event:KeyboardEvent)=>{
      if(event.key==='Escape'){setExpanded(false);return}
      if(event.key!=='Tab')return;
      const focusable=Array.from(terminal.current?.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled),summary,a[href],[tabindex="0"]')||[]).filter(node=>node.getClientRects().length>0);
      const first=focusable[0],last=focusable.at(-1);if(!first)return;
      if(event.shiftKey && (document.activeElement===first || document.activeElement===terminal.current)){event.preventDefault();last?.focus()}
      else if(!event.shiftKey && (document.activeElement===last || document.activeElement===terminal.current)){event.preventDefault();first.focus()}
    };
    document.addEventListener('keydown',handler);
    return()=>{document.body.style.overflow=overflow;document.removeEventListener('keydown',handler);if(previous?.isConnected)previous.focus({preventScroll:true})};
  },[expanded,active]);
  const copy=useCallback(async(value:string,label:string)=>{
    try{await copyLogText(value);setNotice(label)}catch(error){setNotice((error as Error).message)}
  },[]);
  const copyEvent=useCallback((row:TerminalRow)=>{void copy(row.raw,'Original event JSON copied')},[copy]);
  const download=(format:'json'|'log')=>{
    if(!job)return;
    try{
      const value=format==='json'?exportConsoleJSON(activity):readableLog(rows,activity);
      const url=URL.createObjectURL(new Blob([value],{type:format==='json'?'application/json':'text/plain;charset=utf-8'}));
      const link=document.createElement('a');link.href=url;link.download=`${job.case_id}-${job.id}-execution.${format}`;link.click();setTimeout(()=>URL.revokeObjectURL(url),0);
      setNotice(format==='json'?'Full JSON export prepared':'Readable log export prepared');
    }catch(error){setNotice(`Export failed: ${(error as Error).message}`)}
  };
  const navigate=(direction:number)=>{
    if(!matches.length)return;
    scroll.pause();
    const current=selectedKey?matches.indexOf(selectedKey):-1;
    const key=matches[current<0?(direction>0?0:matches.length-1):(current+direction+matches.length)%matches.length];
    const row=rows.find(value=>value.key===key);
    if(row && !findRanges([row.message,...row.metrics].join('\n'),query).length)setOpen(previous=>new Set(previous).add(key));
    setSelectedKey(key);setJump(value=>value+1);
  };
  const updateQuery=(value:string)=>{scroll.pause();setQuery(value);setSelectedKey(null);if(!value.trim())setMatchesOnly(false)};
  const jumpLatest=()=>{setMatchesOnly(false);setSelectedKey(null);scroll.jump()};
  return <section ref={terminal} className={`execution-terminal${expanded?' is-expanded':''}`} tabIndex={-1} role={expanded?'dialog':'region'} aria-modal={expanded?true:undefined} aria-label="NanoForensics execution console">
    <header className="terminal-header"><div className="terminal-title"><span className="terminal-icon" aria-hidden="true">›_</span><div><h3>NanoForensics / Execution Console</h3><div className="terminal-header-meta"><span>Sample {job?.case_id||caseId||'not selected'}</span><span>Physics: {terminalEngine(rawEvents,job?.status)}</span>{job && Number.isFinite(job.elapsed_sec) && <span>{clockLabel(job.elapsed_sec)} elapsed</span>}</div></div></div><div className="terminal-header-actions"><span className={`terminal-job-status tone-${state.tone}`} role="status" aria-live="polite">{state.label}</span><button onClick={()=>setExpanded(value=>!value)} aria-pressed={expanded}>{expanded?'Exit expanded view':'Expand console'}</button></div></header>
    {active && <p className="sr-only" role="status" aria-live="polite">{rows.at(-1)?.message} {rows.at(-1)?.metrics[0] || ''}</p>}
    <div ref={scroll.viewport} className="terminal-viewport" tabIndex={0} aria-label="Chronological execution output" {...scroll.handlers}>
      {error && <p className="terminal-notice tone-warning" role="alert">[WARN] Live updates unavailable. Showing last confirmed events. {error}</p>}
      {!visibleRows.length && <p className="terminal-empty">{query.trim() && matchesOnly?'No events match this search. Complete history is retained in the JSON export.':submitting?'Submitting request. No worker execution is confirmed yet.':job?'No detailed events were recorded for this job.':'Waiting for a confirmed investigation job.'}</p>}
      <ol ref={scroll.content} className="terminal-lines" aria-label="Original events in recorded order">{visibleRows.map(row=><TerminalEventRow key={row.key} row={row} open={open.has(row.key)} query={query} activeMatch={row.key===activeKey} onToggle={toggle} onCopy={copyEvent} register={register}/>)}</ol>
      {activeRun && <aside className="terminal-active-operation" aria-label="Current confirmed simulation operation"><span className="stage-spinner" aria-hidden="true"/><div><strong>[RUN] {activeRun.data.fresh_requested===true?'New physics computation in progress':'Resolving saved or newly computed physics'}</strong><div>Selected engine: {engineName(activeRun.data.engine_requested)} · actual engine confirmed on return</div><div>{activeRun.data.role==='baseline'?'Baseline reference':'Test change'} · replicate {String(activeRun.data.replicate_index??'unreported')}/{String(activeRun.data.replicate_total??'unreported')}{runElapsed!=null?` · run elapsed ${clockLabel(runElapsed)}`:''}</div><div>Waiting for the simulation result. No per-timestep progress is available.</div></div></aside>}
    </div>
    <footer className="terminal-footer"><div className="terminal-search"><label htmlFor={`${job?.id||'pending'}-terminal-search`}>Search logs</label><input id={`${job?.id||'pending'}-terminal-search`} type="search" value={query} onChange={event=>updateQuery(event.target.value)} onKeyDown={event=>{if(event.key==='Enter'){event.preventDefault();navigate(event.shiftKey?-1:1)}}} placeholder="Messages or structured data" autoComplete="off"/><button aria-label="Previous matching event" disabled={!matches.length} onClick={()=>navigate(-1)}>↑</button><button aria-label="Next matching event" disabled={!matches.length} onClick={()=>navigate(1)}>↓</button><span className="terminal-match-count" role="status">{query.trim()?`${selectedIndex+1}/${matches.length} matching events`:`${rows.length} events`}</span><label className="terminal-toggle"><input type="checkbox" checked={matchesOnly} disabled={!query.trim()} onChange={event=>{scroll.pause();setMatchesOnly(event.target.checked)}}/>Matches only</label></div>
      <div className="terminal-controls"><label className="terminal-toggle"><input type="checkbox" checked={follow} onChange={event=>{if(event.target.checked)jumpLatest();else scroll.setFollow(false)}}/>Auto-follow</label><span className={`terminal-follow-state${follow?'':' paused'}`}>{follow?'Following latest':'Paused · reading recorded events'}</span><button onClick={jumpLatest} disabled={!rows.length}>Jump to latest</button><button onClick={()=>void copy(readableLog(visibleRows,activity),`Copied ${visibleRows.length} ${matchesOnly?'matching':'recorded'} events`)} disabled={!visibleRows.length}>{matchesOnly?'Copy visible logs':'Copy logs'}</button><button onClick={()=>download('json')} disabled={!job}>Download JSON</button><button onClick={()=>download('log')} disabled={!job}>Download .log</button></div>
      <div className="terminal-footnote"><span>Read-only operation log. Execution success does not establish scientific support. JSON export retains the complete original history.</span><span role="status" aria-live="polite">{notice}</span></div>
    </footer>
  </section>;
}
