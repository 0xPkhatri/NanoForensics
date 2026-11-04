import {Children, cloneElement, isValidElement} from 'react';
import type {ReactNode} from 'react';

// Presentation memory is local to the page. Reloading an existing transcript
// shows it immediately; new receipts can animate once, even across view changes.
export function createConsoleRevealSession() {
  const boundaries = new Map<string, number>();
  const displayed = new Set<string>();
  const key = (job: string, seq: number) => `${job}:${seq}`;
  return {
    observe(job: string, lastSeq: number, requestedHere: boolean) {
      if (!boundaries.has(job)) boundaries.set(job, requestedHere ? 0 : lastSeq);
    },
    shouldReveal(job: string, seq: number) {
      return boundaries.has(job) && seq > boundaries.get(job)! && !displayed.has(key(job,seq));
    },
    markDisplayed(job: string, seq: number) {displayed.add(key(job,seq))},
  };
}
export type ConsoleRevealSession = ReturnType<typeof createConsoleRevealSession>;

export function contentCharacters(node: ReactNode): number {
  if (typeof node === 'string' || typeof node === 'number') return Array.from(String(node)).length;
  if (Array.isArray(node)) return node.reduce((sum, child) => sum + contentCharacters(child), 0);
  if (isValidElement<{children?: ReactNode}>(node)) return contentCharacters(node.props.children);
  return 0;
}

// Reveal text through React, retaining the actual paragraphs, lists and styles.
// Never mutate React-owned DOM or type raw JSON/provenance fields.
export function revealContent(node: ReactNode, budget: {remaining: number}): ReactNode {
  if (budget.remaining <= 0) return null;
  if (typeof node === 'string' || typeof node === 'number') {
    const characters = Array.from(String(node));
    const visible = characters.slice(0, budget.remaining).join('');
    budget.remaining = Math.max(0, budget.remaining - characters.length);
    return visible;
  }
  if (Array.isArray(node)) return Children.toArray(node).map(child => revealContent(child, budget));
  if (isValidElement<{children?: ReactNode}>(node)) return cloneElement(node, undefined, revealContent(node.props.children, budget));
  return node;
}
