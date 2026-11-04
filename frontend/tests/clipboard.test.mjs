import {test} from 'node:test';
import assert from 'node:assert/strict';
import {copyLogText} from '../src/lib/clipboard.ts';
test('copy waits for actual clipboard acknowledgement and preserves text exactly',async()=>{
  const previous=Object.getOwnPropertyDescriptor(globalThis,'navigator');
  let value='',acknowledge;const receipt=new Promise(resolve=>{acknowledge=resolve});
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{clipboard:{writeText:async(text)=>{value=text;await receipt}}}});
  try{
    let complete=false;const promise=copyLogText('2026-11-05T00:00:02Z [CACHE] fixture\n0.12345678901234566').then(()=>{complete=true});
    await Promise.resolve();assert.equal(complete,false);assert.match(value,/\[CACHE\]/);
    acknowledge();await promise;assert.equal(complete,true);assert.ok(value.endsWith('0.12345678901234566'));
  }finally{if(previous)Object.defineProperty(globalThis,'navigator',previous);else delete globalThis.navigator}
});
test('unavailable or rejected clipboard reports failure rather than fake success',async()=>{
  const previous=Object.getOwnPropertyDescriptor(globalThis,'navigator');
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{clipboard:{writeText:async()=>{throw new Error('permission fixture')}}}});
  try{await assert.rejects(copyLogText('fixture'),/Clipboard is unavailable/)}
  finally{if(previous)Object.defineProperty(globalThis,'navigator',previous);else delete globalThis.navigator}
});
