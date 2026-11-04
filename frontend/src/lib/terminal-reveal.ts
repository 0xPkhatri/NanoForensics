import type {TerminalRow} from './terminal-format';

/** Display-only word boundaries; original events and export payloads stay untouched. */
export function revealWords(text:string):number[] {
  return Array.from(text.matchAll(/\S+\s*/g),match=>match.index!+match[0].length);
}
export function revealTimeline(rows:TerminalRow[],count:number) {
  let remaining=count;
  return rows.flatMap(row=>{
    const text=[row.message,...row.metrics].join('\n'),ends=revealWords(text);
    if(remaining<=0 && ends.length)return [];
    const words=Math.min(remaining,ends.length),complete=words>=ends.length;
    remaining-=ends.length;
    const lines=(complete?text:text.slice(0,ends[Math.max(0,words-1)]||0)).split('\n');
    return [{...row,message:lines[0],metrics:lines.slice(1),revealing:!complete}];
  });
}
export function timelineWordCount(rows:TerminalRow[]) {
  return rows.reduce((sum,row)=>sum+revealWords([row.message,...row.metrics].join('\n')).length,0);
}
