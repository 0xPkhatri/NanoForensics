'use client';
import {useState} from 'react';
import type {Investigation} from '@/lib/api';
import {eventCategory} from '@/lib/investigation-view';
export default function EvidenceTimeline({state}: {state: Investigation}) {
  const [filter, setFilter] = useState('all');
  const events = state.audit_log.filter(e => filter === 'all' || eventCategory(e) === filter);
  return <section className="panel" id="report"><div className="panelhead"><div><span className="overline">The recorded investigation</span><h2>Every step has a record</h2></div><span className="count-tag">{state.audit_log.length}</span></div><div className="panelbody"><div className="filter-tabs" role="group" aria-label="Filter evidence">{[['all', 'All'], ['ai', 'AI actions'], ['simulation', 'Simulations'], ['checks', 'Checks']].map(([id, label]) => <button key={id} aria-pressed={filter === id} onClick={() => setFilter(id)}>{label}</button>)}</div><div className="timeline">{events.length ? events.map((event, index) => <article className="event" key={index}><div className="row-between"><strong>{event.stage.replaceAll('_', ' ')}</strong><time dateTime={event.timestamp}>{new Date(event.timestamp).toLocaleString()}</time></div><p>{event.message}</p>{event.cached !== undefined && <span className="badge">{event.cached ? 'Saved immutable simulation' : 'Computed during this recorded action'}</span>}<details><summary>Event details</summary><pre className="reportpre" tabIndex={0}>{JSON.stringify(event, null, 2)}</pre></details></article>) : <div className="empty-state compact"><p>{state.audit_log.length ? 'No events match this filter.' : 'The timestamped evidence trail appears after an investigation starts.'}</p></div>}</div></div></section>;
}
