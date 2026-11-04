'use client';
import {memo, useId, useMemo} from 'react';
import type {TerminalRow, TextRange} from '@/lib/terminal-format';
import {findRanges, jsonTokens, markParts} from '@/lib/terminal-format';

export function HighlightedText({text,query='',ranges,offset=0}:{text:string;query?:string;ranges?:TextRange[];offset?:number}) {
  return <>{markParts(text,ranges||findRanges(text,query),offset).map((part,index)=>part.match?<mark key={index}>{part.text}</mark>:<span key={index}>{part.text}</span>)}</>;
}
export function JSONPayload({raw,query}:{raw:string;query:string}) {
  const tokens=useMemo(()=>jsonTokens(raw),[raw]);
  const ranges=useMemo(()=>findRanges(raw,query),[raw,query]);
  return <pre className="terminal-json" tabIndex={0} aria-label="Complete original event JSON"><code>{tokens.map((token,index)=><span key={index} className={`json-${token.kind}`}><HighlightedText text={token.text} ranges={ranges} offset={token.offset}/></span>)}</code></pre>;
}

export const TerminalEventRow=memo(function TerminalEventRow({row,open,query,activeMatch,onToggle,onCopy,register}:{
  row:TerminalRow;open:boolean;query:string;activeMatch:boolean;
  onToggle:(key:string)=>void;onCopy:(row:TerminalRow)=>void;register:(key:string,node:HTMLLIElement|null)=>void;
}) {
  const detailId=useId();
  const visibleText=[row.message,...row.metrics].join('\n');
  const payloadOnly=!!query.trim() && findRanges(row.raw,query).length>0 && !findRanges(visibleText,query).length;
  return <li ref={node=>register(row.key,node)} className={`terminal-event tone-${row.tone}${row.groupId?' grouped':''}${activeMatch?' active-match':''}`}>
    {row.groupStart && <div className="terminal-group-heading"><span>EXPERIMENT</span><strong>{row.groupLabel}</strong><code>{row.groupId}</code></div>}
    <button className="terminal-line" aria-expanded={open} aria-controls={detailId} onClick={()=>onToggle(row.key)}>
      <time dateTime={row.timestamp||undefined} title={row.timestamp||'Timestamp unavailable'}>{row.time}</time>
      <span className="terminal-tag">[{row.tag}]</span>
      <span className="terminal-message">{row.branch && <span className="terminal-branch" aria-hidden="true">{row.branch} </span>}<HighlightedText text={row.message} query={query}/></span>
      <span className="terminal-disclosure" aria-hidden="true">{open?'▾':'▸'}</span>
    </button>
    {row.metrics.length>0 && <div className="terminal-metrics">{row.metrics.map((metric,index)=><div key={index}><HighlightedText text={metric} query={query}/></div>)}</div>}
    {payloadOnly && !open && <button className="terminal-payload-match" onClick={()=>onToggle(row.key)}>Match in structured payload · expand details</button>}
    <div id={detailId} hidden={!open} className="terminal-details">
      {open && <><div className="terminal-detail-actions"><span>Original payload · sequence {row.seq ?? 'not furnished'}</span><button onClick={()=>onCopy(row)}>Copy event JSON</button></div><JSONPayload raw={row.raw} query={query}/></>}
    </div>
  </li>;
});
