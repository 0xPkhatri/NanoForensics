import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {registerTestTSX} from './tsx-loader.mjs';
import {buildTerminalRows} from '../src/lib/terminal-format.ts';
registerTestTSX();
const {TerminalEventRow}=await import('../src/components/TerminalEventRow.tsx');
const raw={job_id:'ui-fixture',seq:15,timestamp:'2026-11-05T00:00:01.123Z',phase:'simulate',status:'completed',message:'UI fixture only',data:{cached:true,value:0.12345678901234566,extra:{fullMetadata:'keep-complete',escaped:'<script>fixture-only</script>',longValue:'z'.repeat(15000)}}};
const row=buildTerminalRows([raw])[0];
const props={row,query:'',activeMatch:false,onToggle:()=>{},onCopy:()=>{},register:()=>{}};
test('terminal rows default to collapsed payloads with accessible expansion and no event cards',()=>{
  const html=renderToStaticMarkup(createElement(TerminalEventRow,{...props,open:false}));
  assert.match(html,/aria-expanded="false"/);assert.match(html,/\[CACHE\]/);assert.match(html,/2026-11-05T00:00:01.123Z/);
  assert.doesNotMatch(html,/keep-complete/);assert.doesNotMatch(html,/console-event-head|reportpre/);
});
test('expanded rows render original full JSON, precise values and an individual copy action',()=>{
  const html=renderToStaticMarkup(createElement(TerminalEventRow,{...props,open:true}));
  assert.match(html,/aria-expanded="true"/);assert.match(html,/Copy event JSON/);
  assert.match(html,/0.12345678901234566/);assert.match(html,/keep-complete/);assert.ok(html.includes('z'.repeat(15000)));
  assert.doesNotMatch(html,/<script>/);
  assert.match(html,/&lt;script&gt;fixture-only&lt;\/script&gt;/);
  assert.deepEqual(JSON.parse(row.raw),raw);
});

const {default:ExecutionTerminal}=await import('../src/components/ExecutionTerminal.tsx');
const created=Date.parse('2026-11-05T00:00:00Z')/1000;
const view=(events,status='COMPLETE')=>renderToStaticMarkup(createElement(ExecutionTerminal,{activity:{job:{id:'ui-fixture',case_id:'DEMO_FIXTURE',kind:'investigate',status,created,updated:created+60.5,elapsed_sec:60.5,error:null},events},caseId:'DEMO_FIXTURE',follow:true,onFollow:()=>{}}));
test('complete terminal is one container with accessible controls and collapsed original events',()=>{
  const html=view([raw]);
  assert.equal((html.match(/class="execution-terminal"/g)||[]).length,1);
  for(const label of ['NanoForensics / Execution Console','COMPLETED','Search logs','Copy logs','Jump to latest','Download JSON','Download .log','Auto-follow','Expand console'])assert.ok(html.includes(label),label);
  assert.doesNotMatch(html,/console-event-head|reportpre|keep-complete/);
});
test('running panel uses confirmed simulation context and stops for failed or cancelled jobs',()=>{
  const start={...raw,status:'started',data:{role:'test_change',replicate_index:2,replicate_total:3,engine_requested:'LAMMPS_BINARY',fresh_requested:true}};
  const running=view([start],'RUNNING');
  assert.match(running,/Waiting for the simulation result/);assert.match(running,/replicate 2\/3/);assert.match(running,/run elapsed 00:59/);
  assert.match(running,/LAMMPS \(selected\)/);
  for(const status of ['COMPLETE','FAILED','CANCELLED']){
    const html=view([start],status);
    assert.doesNotMatch(html,/class="terminal-active-operation"/);
    assert.ok(html.includes(status==='COMPLETE'?'COMPLETED':status));
  }
});

const {default:InvestigationConsole}=await import('../src/components/InvestigationConsole.tsx');
test('technical view has the same nine-stage sidebar beside the terminal',()=>{
  const html=renderToStaticMarkup(createElement(InvestigationConsole,{activity:null,caseId:'DEMO_FIXTURE',onResults:()=>{},onEvidence:()=>{}}));
  assert.match(html,/console-body technical-console-layout/);
  assert.equal((html.match(/class="console-phases"/g)||[]).length,1);
  assert.match(html,/Initialize/);assert.match(html,/Finish job/);
  assert.doesNotMatch(html,/terminal-workflow/);
  assert.ok(html.indexOf('console-phases')<html.indexOf('class="execution-terminal"'));
});
