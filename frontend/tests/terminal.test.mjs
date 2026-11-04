import {test} from 'node:test';
import assert from 'node:assert/strict';
import {buildTerminalRows, exportConsoleJSON, findRanges, jsonTokens, markParts, pendingSimulation, readableLog, searchRows, terminalEngine, terminalStatus, toggleExpanded} from '../src/lib/terminal-format.ts';

// UI contract fixtures only. These are not scientific simulation results.
const event=(seq,phase='worker',status='completed',data={})=>({seq,job_id:'fixture-job',timestamp:'2026-11-05T00:00:02.123456Z',phase,status,message:`Fixture operation ${seq}`,data});
const job={id:'fixture-job',case_id:'DEMO_FIXTURE',created:Date.parse('2026-11-05T00:00:00Z')/1000,status:'RUNNING',elapsed_sec:2.4};
test('terminal preserves event order, original timestamps, unique identities and unknown payload fields',()=>{
  const events=[event(10),event(2),event(7),event(7),null,{job_id:'fixture-job',message:{malformed:true},data:'unexpected'}];
  const rows=buildTerminalRows(events,job.created);
  assert.deepEqual(rows.map(row=>row.seq),[10,2,7,7,null,null]);
  assert.equal(new Set(rows.map(row=>row.key)).size,events.length);
  assert.equal(rows[0].timestamp,events[0].timestamp);
  assert.equal(rows[0].time,'00:02');
  assert.equal(JSON.parse(rows[5].raw).data,'unexpected');
  assert.match(rows[5].message,/Unrecognized/);
});
test('groups are contiguous presentation labels without merging or reordering records',()=>{
  const events=[event(1),event(2,'simulate','started',{experiment_id:'a',intervention:'heal_interior_vacancy'}),event(3,'simulate','completed',{experiment_id:'a',role:'baseline',cached:true}),event(4,'verify','completed',{verification:{experiment_id:'a'}}),event(5,'revise'),event(6,'simulate','started',{experiment_id:'b'}),event(7,'simulate','started',{experiment_id:'a'}),event(8,'conclude')];
  const rows=buildTerminalRows(events,job.created);
  assert.deepEqual(rows.map(row=>row.original),events);
  assert.deepEqual(rows.map(row=>row.groupId),[null,'a','a','a','a','b','a',null]);
  assert.deepEqual(rows.filter(row=>row.groupStart).map(row=>row.seq),[2,6,7]);
  assert.equal(rows[3].groupLabel,'Restore missing interior atoms');
  assert.equal(rows[4].branch,'└─');
});
test('execution, numerical checks, scientific support, fallback and cache use distinct semantics',()=>{
  const fixtures=[
    event(1,'simulate','completed',{cached:true}),
    event(2,'simulate','completed',{cached:false,numerical_check:{is_valid:true}}),
    event(3,'verify','completed',{verification:{execution_status:'COMPLETE',numerical_consistency_passed:true,verdict:'SUPPORTED',strain_recovery_pct:47.85123456789}}),
    event(4,'verify','completed',{verification:{execution_status:'EXECUTION_FAILED',numerical_consistency_passed:false,verdict:'PENDING',strain_recovery_pct:null}}),
    event(5,'hypotheses','completed',{receipt:{telemetry:{execution_mode:'OFFLINE_HEURISTIC_FALLBACK',configured_model:'fixture-model'}}}),
    event(6,'hypotheses','completed',{ai_execution_mode:'LIVE_MUSE_SPARK_API'}),
  ];
  const rows=buildTerminalRows(fixtures,job.created);
  assert.equal(rows[0].tag,'CACHE');assert.equal(rows[1].tag,'OK');
  assert.equal(rows[2].tag,'RESULT');assert.notEqual(rows[2].tone,'success');
  assert.ok(rows[2].metrics.some(value=>value.includes('+47.85123456789%')));
  assert.equal(rows[3].tone,'error');assert.ok(rows[3].metrics.some(value=>value.includes('No scientific verdict')));
  assert.equal(rows[4].tone,'warning');assert.ok(rows[4].metrics.includes('AI source: offline rule-based fallback'));
  assert.ok(rows[5].metrics.some(value=>value.includes('not confirmed')));
});
test('search includes hidden structured data and treats regex punctuation literally',()=>{
  const rows=buildTerminalRows([event(1,'worker','completed',{deep:{receipt:'[RUN] literal.a+b'}}),event(2)]);
  assert.deepEqual(searchRows(rows,'[run]'),[rows[0].key]);
  assert.equal(searchRows(rows,'literal.a+b').length,1);
  assert.equal(searchRows(rows,'literalXaab').length,0);
  assert.equal(rows.length,2);assert.equal(searchRows(rows,'not-found').length,0);
});
test('JSON syntax highlighting and cross-token search retain every character and full precision',()=>{
  const original=event(1,'worker','completed',{value:0.12345678901234566,metadata:{unknown:'full payload',large:'x'.repeat(20000)}});
  const raw=buildTerminalRows([original])[0].raw;
  assert.deepEqual(JSON.parse(raw),original);
  const tokens=jsonTokens(raw);assert.equal(tokens.map(token=>token.text).join(''),raw);
  const ranges=findRanges(raw,'"value": 0.123');
  const pieces=tokens.flatMap(token=>markParts(token.text,ranges,token.offset));
  assert.equal(pieces.map(piece=>piece.text).join(''),raw);
  assert.equal(pieces.filter(piece=>piece.match).map(piece=>piece.text).join(''),'"value": 0.123');
});
test('expansion survives a polled snapshot and exports retain all events despite filtering',()=>{
  const original={job,events:[event(1),event(2,'worker','completed',{privateFixture:'public test metadata',value:0.12345678901234566})],extraMetadata:{keep:true}};
  const rows=buildTerminalRows(original.events,job.created);
  const open=toggleExpanded(new Set(),rows[1].key);
  const polled=buildTerminalRows(JSON.parse(JSON.stringify(original.events)),job.created);
  assert.ok(open.has(polled[1].key));assert.equal(open.size,1);
  assert.equal(toggleExpanded(open,polled[1].key).size,0);assert.equal(open.size,1);
  assert.deepEqual(JSON.parse(exportConsoleJSON(original)),original);
  const selected=rows.filter(row=>searchRows(rows,'privateFixture').includes(row.key));
  assert.equal(selected.length,1);assert.equal(JSON.parse(exportConsoleJSON(original)).events.length,2);
  const readable=readableLog(rows,original);assert.match(readable,/2026-11-05T00:00:02.123456Z 00:02 \[OK\]/);
});
test('only a confirmed active simulation produces a running panel; engine selection is qualified',()=>{
  const start=event(1,'simulate','started',{role:'test_change',replicate_index:2,replicate_total:3,engine_requested:'LAMMPS_BINARY',fresh_requested:true});
  assert.ok(pendingSimulation([start],'RUNNING'));
  assert.equal(terminalEngine([start],'RUNNING'),'LAMMPS (selected)');
  assert.equal(pendingSimulation([start],'CANCELLED'),null);
  const end=event(2,'simulate','completed',{engine_used:'NUMPY_VELOCITY_VERLET_2D',cached:false});
  assert.equal(pendingSimulation([start,end],'RUNNING'),null);
  assert.equal(terminalEngine([start,end],'COMPLETE'),'NumPy (recorded)');
});
test('running, complete, failed, timeout and cancellation job labels are explicit',()=>{
  assert.equal(terminalStatus('RUNNING').label,'RUNNING');assert.equal(terminalStatus('COMPLETE').label,'COMPLETED');
  assert.equal(terminalStatus('CANCELLED').label,'CANCELLED');
  assert.equal(terminalStatus('FAILED').tone,'error');assert.match(terminalStatus('TIMED_OUT').label,/TIMED_OUT/);
  assert.equal(terminalStatus('QUEUED').label,'QUEUED');
});
