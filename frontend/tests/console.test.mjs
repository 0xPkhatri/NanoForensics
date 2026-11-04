import {test} from 'node:test';
import assert from 'node:assert/strict';
import {phaseState, eventSource, confirmedEvents, eventTime} from '../src/lib/console-view.ts';

const event = (phase,status,data={},seq=1,job='new-job') => ({seq,job_id:job,phase,status,data,message:'Contract fixture only',timestamp:'2026-11-04T00:00:02Z'});
const activity = (events,status='RUNNING') => ({job:{id:'new-job',status,created:1793750400},events});
test('waiting steps have no manufactured completion or elapsed timestamps', () => {
  assert.equal(phaseState('verify',activity([])),'waiting');
  assert.equal(phaseState('complete',activity([],'COMPLETE')),'waiting');
});
test('completing one replicate does not complete the entire simulation phase', () => {
  const first=event('simulate','completed',{replicate_index:1,cached:true});
  assert.equal(phaseState('simulate',activity([first])),'running');
  const comparison=event('simulate','completed',{comparison_complete:true},2);
  assert.equal(phaseState('simulate',activity([first,comparison])),'completed');
  const next=event('simulate','started',{},3);
  assert.equal(phaseState('simulate',activity([first,comparison,next])),'running');
});
test('cancellation stops an in-flight phase instead of marking it complete', () => {
  assert.equal(phaseState('simulate',activity([event('simulate','started')],'CANCELLED')),'stopped');
  assert.equal(phaseState('simulate',activity([event('simulate','failed')],'COMPLETE')),'failed');
});
test('old job history cannot complete steps in a new job', () => {
  const value=activity([event('verify','completed',{},1,'old-job')]);
  assert.equal(confirmedEvents(value).length,0);
  assert.equal(phaseState('verify',value),'waiting');
});
test('live status requires an actual action receipt and fresh/cached labels need evidence', () => {
  assert.equal(eventSource(event('hypotheses','started',{engine_requested:'LAMMPS_BINARY'})),null);
  assert.equal(eventSource(event('simulate','started',{fresh_requested:true})),null);
  assert.equal(eventSource(event('hypotheses','completed',{ai_execution_mode:'LIVE_MUSE_SPARK_API'})),null);
  assert.equal(eventSource(event('hypotheses','started',{receipt:{telemetry:{execution_mode:'LIVE_MUSE_SPARK_API'}}})),null);
  assert.equal(eventSource(event('hypotheses','completed',{receipt:{telemetry:{execution_mode:'LIVE_MUSE_SPARK_API'}}})),'Confirmed live model response');
  assert.equal(eventSource(event('simulate','completed',{cached:false})),'Fresh simulation');
  assert.equal(eventSource(event('simulate','completed',{cached:true})),'Saved immutable simulation');
  assert.equal(eventSource(event('revise','completed',{receipt:{telemetry:{execution_mode:'OFFLINE_HEURISTIC_FALLBACK'}}})),'Rule-based fallback');
});

test('a second test does not inherit evidence checks or explanation updates from the first', () => {
  const first=[
    event('simulate','started',{experiment_id:'first'},1),
    event('simulate','completed',{experiment_id:'first',comparison_complete:true},2),
    event('verify','completed',{verification:{experiment_id:'first'}},3),
    event('revise','completed',{},4),
  ];
  assert.equal(phaseState('verify',activity(first)),'completed');
  const next=[...first,event('simulate','started',{experiment_id:'second'},5),event('simulate','started',{experiment_id:'second',role:'test_change',replicate_index:1},6)];
  assert.equal(phaseState('simulate',activity(next)),'running');
  assert.equal(phaseState('verify',activity(next)),'waiting');
  assert.equal(phaseState('revise',activity(next)),'waiting');
  const checked=[...next,event('simulate','completed',{comparison_complete:true},7),event('verify','started',{experiment_id:'second'},8)];
  assert.equal(phaseState('verify',activity(checked)),'running');
  assert.equal(phaseState('revise',activity(checked)),'waiting');
});
test('repeating the same proposal or skipping a new edit also resets downstream stage indicators', () => {
  const previous=[event('simulate','started',{experiment_id:'same'},1),event('verify','completed',{},2),event('revise','completed',{},3)];
  for (const boundary of [event('simulate','started',{experiment_id:'same'},4),event('simulate','skipped',{experiment_id:'another'},4)]) {
    const current=activity([...previous,boundary]);
    assert.equal(phaseState('verify',current),'waiting');
    assert.equal(phaseState('revise',current),'waiting');
  }
});
