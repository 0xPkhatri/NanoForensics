'use client';
import {useEffect, useRef, useState} from 'react';
import type {Simulation, Snapshot} from '@/lib/api';
import {frameLabel, stretch} from '@/lib/presentation';
export type Bounds = {minX: number; maxX: number; minY: number; maxY: number};
export function snapshotBounds(snapshots: Snapshot[]): Bounds | undefined {
  const atoms = snapshots.flatMap(s => s.atoms);
  if (!atoms.length) return;
  return {minX: Math.min(...atoms.map(a => a[1])), maxX: Math.max(...atoms.map(a => a[1])), minY: Math.min(...atoms.map(a => a[2])), maxY: Math.max(...atoms.map(a => a[2]))};
}
const damageColors = ['#bbc6ca', '#e0ae50', '#c96528', '#ab3929', '#76242e', '#461d33', '#29152a'];
export default function LatticeCanvas({simulation, bounds, virialLimit: sharedVirialLimit, title = 'The material'}: {simulation: Simulation; bounds?: Bounds; virialLimit?: number; title?: string}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [frame, setFrame] = useState(0), [color, setColor] = useState(4), [zoom, setZoom] = useState(1), [atomId, setAtomId] = useState('');
  const snapshots = simulation.snapshots;
  const index = Math.min(frame, Math.max(0, snapshots.length - 1));
  const selected = snapshots[index];
  const atom = selected?.atoms.find(a => String(a[0]) === atomId);
  // A shared scale across all recorded frames; damage and coordination use absolute counts.
  const virialLimit = sharedVirialLimit ?? Math.max(.01, ...snapshots.flatMap(s => s.atoms.map(a => Math.abs(a[5]))));
  useEffect(() => {setFrame(0); setAtomId(''); setZoom(1)}, [simulation.sim_id]);
  useEffect(() => {
    const node = canvas.current;
    if (!node || !selected) return;
    let points: {atom: number[]; x: number; y: number}[] = [];
    const draw = () => {
      const ratio = window.devicePixelRatio || 1, w = node.clientWidth, h = node.clientHeight;
      node.width = w * ratio; node.height = h * ratio;
      const ctx = node.getContext('2d'); if (!ctx) return;
      ctx.scale(ratio, ratio); ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#fbf8ef'; ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = '#e8e2d5'; ctx.lineWidth = .6;
      for (let x = 0; x < w; x += 24) {ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke()}
      for (let y = 0; y < h; y += 24) {ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke()}
      const range = bounds || snapshotBounds(snapshots); if (!range) return;
      const scale = Math.min((w - 70) / Math.max(range.maxX - range.minX, 1), (h - 65) / Math.max(range.maxY - range.minY, 1)) * zoom;
      points = selected.atoms.map(a => ({atom: a, x: w / 2 + (a[1] - (range.minX + range.maxX) / 2) * scale, y: h / 2 - (a[2] - (range.minY + range.maxY) / 2) * scale}));
      ctx.strokeStyle = '#9fa9a7'; ctx.lineWidth = 1;
      points.forEach((a, i) => points.slice(i + 1).forEach(b => {if (Math.hypot(a.atom[1] - b.atom[1], a.atom[2] - b.atom[2]) < 1.5) {ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke()}}));
      points.forEach(({atom: a, x, y}) => {
        ctx.beginPath(); ctx.arc(x, y, Math.min(6, Math.max(3, scale * .19)), 0, 2 * Math.PI);
        ctx.fillStyle = color === 4 ? damageColors[Math.min(6, Math.max(0, Math.round(a[4])))] : color === 3 ? `hsl(220 65% ${88 - Math.min(8, Math.max(0, a[3])) * 7}%)` : a[5] < 0 ? `hsl(220 65% ${85 - 45 * Math.abs(a[5]) / virialLimit}%)` : `hsl(22 75% ${85 - 45 * a[5] / virialLimit}%)`;
        ctx.fill(); ctx.strokeStyle = '#fffdf8'; ctx.lineWidth = .7; ctx.stroke();
        if (String(a[0]) === atomId) {ctx.beginPath(); ctx.arc(x, y, 10, 0, Math.PI * 2); ctx.strokeStyle = '#2457d6'; ctx.lineWidth = 2; ctx.stroke()}
      });
    };
    const inspect = (event: MouseEvent) => {const rect = node.getBoundingClientRect(); const found = points.find(p => Math.hypot(event.clientX - rect.left - p.x, event.clientY - rect.top - p.y) < 10); if (found) setAtomId(String(found.atom[0]))};
    draw(); node.addEventListener('click', inspect);
    const observer = new ResizeObserver(draw); observer.observe(node);
    return () => {observer.disconnect(); node.removeEventListener('click', inspect)};
  }, [selected, snapshots, color, zoom, bounds, atomId, virialLimit]);
  const lost = selected?.atoms.filter(a => a[4] > 0).length || 0;
  return <section className="panel material-panel" id="structure"><div className="panelhead"><div><span className="overline">A closer look</span><h2>{title}</h2></div><span className="badge">{selected?.atoms.length || 0} atoms</span></div><div className="viewer-toolbar"><label>Color by<select aria-label="Atom color measurement" value={color} onChange={e => setColor(Number(e.target.value))}><option value={4}>Lost neighbors</option><option value={3}>Neighbor count</option><option value={5}>Local tensile stress</option></select></label><div className="zoom-controls"><button aria-label="Zoom out" onClick={() => setZoom(z => Math.max(.6, z - .2))}>−</button><button onClick={() => setZoom(1)} aria-label="Reset lattice zoom">Fit</button><button aria-label="Zoom in" onClick={() => setZoom(z => Math.min(3, z + .2))}>+</button></div></div>{selected ? <canvas ref={canvas} className="lattice" role="img" aria-label={`${title}: ${selected.atoms.length} atoms; ${lost} atoms have net neighbor loss. ${frameLabel(simulation, index, snapshots.length)} at ${stretch(selected.strain)} stretch. Use the atom selector for individual measurements.`}/> : <div className="empty-state">No recorded atom snapshots are available.</div>}<div className="material-legend">{color === 4 ? <><span>Lost neighbors</span>{damageColors.map((value, i) => <span key={value}><i style={{background: value}}/>{i === 6 ? '6+' : i}</span>)}</> : <span>{color === 3 ? 'Neighbor count: 0 (light) → 8+ (dark blue)' : `Local virial: blue (−${virialLimit.toFixed(2)}) → neutral (0) → orange (+${virialLimit.toFixed(2)})`}</span>}</div><div className="panelbody material-footer"><div className="frame-tabs" role="group" aria-label="Recorded snapshots">{snapshots.map((snapshot, i) => <button key={i} aria-pressed={index === i} onClick={() => setFrame(i)}>{frameLabel(simulation, i, snapshots.length)}</button>)}</div><p className="caption">{stretch(selected?.strain)} stretch · {lost} atoms with net neighbor loss. Each dot is an atom; links indicate nearby atoms.</p><details><summary>Inspect atoms and recording details</summary><label className="atom-select">Atom<select aria-label="Inspect an atom" value={atomId} onChange={e => setAtomId(e.target.value)}><option value="">Choose an atom</option>{selected?.atoms.map(a => <option key={a[0]} value={a[0]}>Atom {a[0]}</option>)}</select></label>{atom && <p className="caption">Atom {atom[0]} · x {atom[1].toFixed(3)}, y {atom[2].toFixed(3)} · neighbors {atom[3]} · net neighbor loss {atom[4]} · local virial {atom[5].toFixed(3)}</p>}<p className="caption mono">Simulation {simulation.sim_id} · step {selected?.timestep ?? '—'}</p><p className="caption">Recorded snapshots, not continuous playback. Snapshots represent the first valid replicate where available. Proximity links are display guides; severed reference bonds and persistent fracture clusters are measured separately by the verifier. Colors keep the same scale across this run's frames.</p></details></div></section>;
}
