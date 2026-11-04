import {test} from 'node:test';
import assert from 'node:assert/strict';
import {followDecision} from '../src/lib/log-follow.ts';
const bottom={top:600,previousTop:600,height:1000,viewport:400,following:true,programmatic:false,userIntent:false};
test('manual upward scroll pauses; new content and programmatic movement do not pause following',()=>{
  assert.equal(followDecision({...bottom,top:300,userIntent:true}),'pause');
  assert.equal(followDecision({...bottom,height:1300}),'keep');
  assert.equal(followDecision({...bottom,top:300,programmatic:true}),'keep');
});
test('paused reading is not overridden by appends, resizing or near-bottom layout changes',()=>{
  assert.equal(followDecision({...bottom,top:200,following:false,height:1400}),'keep');
  assert.equal(followDecision({...bottom,following:false}),'keep');
});
test('user returning to the bottom can resume, without prematurely resuming while reading',()=>{
  assert.equal(followDecision({...bottom,following:false,userIntent:true}),'resume');
  assert.equal(followDecision({...bottom,top:200,following:false,userIntent:true}),'keep');
});
