import {test} from 'node:test';
import assert from 'node:assert/strict';
import {revealTimeline,timelineWordCount} from '../src/lib/terminal-reveal.ts';
const rows=[{key:'a',message:'Verification finished',metrics:['Measured recovery: -0.613496932515543%','Independent verdict: REJECTED'],raw:'original payload'},{key:'b',message:'Next event',metrics:[],raw:'second payload'}];
test('word reveal keeps messages and metrics sequential and defers later events',()=>{
  assert.deepEqual(revealTimeline(rows,0),[]);
  const first=revealTimeline(rows,1);assert.equal(first.length,1);assert.equal(first[0].message,'Verification ');assert.equal(first[0].revealing,true);
  const metrics=revealTimeline(rows,5);assert.equal(metrics.length,1);assert.equal(metrics[0].metrics[0],'Measured recovery: -0.613496932515543%');assert.equal(metrics[0].raw,rows[0].raw);
});
test('completed reveal preserves all text, precision, ordering and original dataset',()=>{
  const before=JSON.stringify(rows);const result=revealTimeline(rows,timelineWordCount(rows));
  assert.deepEqual(result,rows.map(row=>({...row,revealing:false})));assert.equal(JSON.stringify(rows),before);
  assert.deepEqual(revealTimeline(rows,Infinity),result);
});
