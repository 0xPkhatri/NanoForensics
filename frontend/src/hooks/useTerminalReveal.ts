'use client';
import {useEffect,useMemo,useState} from 'react';
import type {TerminalRow} from '@/lib/terminal-format';
import {revealTimeline,timelineWordCount} from '@/lib/terminal-reveal';

export function useTerminalReveal(rows:TerminalRow[],jobId:string,live:boolean,active:boolean,immediate:boolean) {
  const total=useMemo(()=>timelineWordCount(rows),[rows]);
  const [progress,setProgress]=useState(()=>({jobId,count:live?0:total}));
  const [reduced,setReduced]=useState(false);
  useEffect(()=>{
    const media=window.matchMedia('(prefers-reduced-motion: reduce)');
    const update=()=>setReduced(media.matches);update();media.addEventListener('change',update);
    return()=>media.removeEventListener('change',update);
  },[]);
  const count=progress.jobId===jobId?progress.count:(live?0:total);
  useEffect(()=>{
    if(progress.jobId!==jobId){setProgress({jobId,count:live?0:total});return}
    if(count>=total)return;
    if(reduced || immediate || !active){setProgress({jobId,count:total});return}
    // Drain confirmed events sequentially. Catch up large poll batches without a long backlog.
    const timer=window.setTimeout(()=>setProgress(previous=>previous.jobId===jobId?{jobId,count:Math.min(total,previous.count+Math.max(1,Math.min(8,Math.ceil((total-previous.count)/160))))}:previous),32);
    return()=>window.clearTimeout(timer);
  },[jobId,progress.jobId,count,total,reduced,immediate,active,live]);
  return {rows:useMemo(()=>revealTimeline(rows,reduced||immediate?Infinity:count),[rows,count,reduced,immediate]),revealing:count<total && active && !reduced && !immediate};
}
