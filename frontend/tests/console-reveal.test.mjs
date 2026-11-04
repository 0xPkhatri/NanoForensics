import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {contentCharacters, createConsoleRevealSession, revealContent} from '../src/lib/console-reveal.ts';

test('opening saved history is immediate, but later receipts can reveal once', () => {
  const session = createConsoleRevealSession();
  session.observe('restored-job',46,false);
  assert.equal(session.shouldReveal('restored-job',46),false);
  assert.equal(session.shouldReveal('restored-job',47),true);
  session.markDisplayed('restored-job',47);
  assert.equal(session.shouldReveal('restored-job',47),false);
  session.observe('restored-job',48,false);
  assert.equal(session.shouldReveal('restored-job',48),true);
});
test('a locally requested job can reveal its initial batch without replaying across views', () => {
  const session = createConsoleRevealSession();
  session.observe('new-job',6,true);
  assert.equal(session.shouldReveal('new-job',1),true);
  session.markDisplayed('new-job',1);
  session.observe('new-job',6,false);
  assert.equal(session.shouldReveal('new-job',1),false);
  assert.equal(session.shouldReveal('different-job',1),false);
});
test('progressive text preserves markup and never splits surrogate pairs', () => {
  const content = createElement('p',null,'Atom 🧪 ',createElement('strong',null,'70%'));
  assert.equal(contentCharacters(content),10);
  assert.equal(renderToStaticMarkup(revealContent(content,{remaining:6})),'<p>Atom 🧪</p>');
  assert.equal(renderToStaticMarkup(revealContent(content,{remaining:8})),'<p>Atom 🧪 <strong>7</strong></p>');
  assert.equal(renderToStaticMarkup(revealContent(content,{remaining:100})),renderToStaticMarkup(content));
});
