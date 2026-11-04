import {test} from 'node:test';
import assert from 'node:assert/strict';
import {outcomeText, stretch, difference, verdictLabel, frameLabel, requestGate} from '../src/lib/presentation.ts';
import {actionReceipts, currentStage} from '../src/lib/investigation-view.ts';

const base = {hypotheses: [], proposed_experiments: [], executed_experiments: {}, verifications: [], audit_log: [], status: 'OBSERVING'};
test('censored runs report the observation horizon without a fracture measurement', () => {
  assert.equal(outcomeText({outcome: 'NOT_FRACTURED_WITHIN_HORIZON', max_observed_strain: .4, failure_strain: null}), 'No fracture observed up to 40.0% stretch');
  assert.equal(stretch(null), 'Not available');
  assert.equal(difference(null), 'Not available');
  assert.notEqual(difference(null), difference(0));
});
test('a failed execution cannot display a scientific support verdict', () => {
  assert.equal(verdictLabel('SUPPORTED', 'EXECUTION_FAILED'), 'No scientific verdict');
  assert.equal(verdictLabel('SUPPORTED', 'TIMEOUT'), 'No scientific verdict');
  assert.equal(outcomeText({outcome: 'EXECUTION_FAILED', failure_strain: .2}), 'Simulation checks failed');
});
test('final snapshots are not called fractures in censored or failed runs', () => {
  for (const outcome of ['NOT_FRACTURED_WITHIN_HORIZON', 'EXECUTION_FAILED']) assert.equal(frameLabel({outcome}, 2, 3), 'Last recorded frame');
  assert.equal(frameLabel({outcome: 'FRACTURED'}, 2, 3), 'Fracture');
});
test('startup or investigation-level telemetry alone cannot create a live action receipt', () => {
  assert.equal(actionReceipts({...base, ai_telemetry: {execution_mode: 'LIVE_MUSE_SPARK_API'}}).length, 0);
  const history = {...base, audit_log: [{timestamp: '2026-11-04T00:00:00Z', stage: 'plan', message: 'planned', provenance: {action: 'plan', telemetry: {execution_mode: 'LIVE_MUSE_SPARK_API'}}}, {timestamp: '2026-11-04T00:01:00Z', stage: 'revise', message: 'fallback', provenance: {action: 'revise', telemetry: {execution_mode: 'OFFLINE_HEURISTIC_FALLBACK'}}}]};
  assert.equal(actionReceipts(history).at(-1).record.telemetry.execution_mode, 'OFFLINE_HEURISTIC_FALLBACK');
});
test('progress derives from actual results and unexecuted proposals', () => {
  assert.equal(currentStage(base, false), 0);
  assert.equal(currentStage({...base, proposed_experiments: [{experiment_id: 'test-1'}]}, false), 2);
  assert.equal(currentStage({...base, status: 'EXPERIMENTING'}, true), 3);
  assert.equal(currentStage({...base, status: 'INCONCLUSIVE'}, false), 5);
});
test('a stale request cannot replace the latest sample after selection or cleanup', () => {
  const gate = requestGate(); const sampleA = gate.next(); const sampleB = gate.next();
  assert.equal(gate.isCurrent(sampleA), false); assert.equal(gate.isCurrent(sampleB), true);
  gate.next(); assert.equal(gate.isCurrent(sampleB), false);
});
