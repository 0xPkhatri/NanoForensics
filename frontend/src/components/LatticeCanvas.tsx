'use client';
import {useEffect,useRef,useState} from 'react';
import {Snapshot} from '@/lib/api';
export default function LatticeCanvas({snapshots}:{snapshots:Snapshot[]}){
 const canvas=useRef<HTMLCanvasElement>(null);const [frame,setFrame]=useState(0);const [color,setColor]=useState(4);const [zoom,setZoom]=useState(1);const [hover,setHover]=useState<number[]|null>(null);
 const selected=snapshots[Math.min(frame,snapshots.length-1)];
 useEffect(()=>{setFrame(0);setHover(null)},[snapshots]);
 useEffect(()=>{
  const node=canvas.current;if(!node||!selected)return;
  const draw=()=>{
   const ratio=window.devicePixelRatio||1;const w=node.clientWidth,h=350;node.width=w*ratio;node.height=h*ratio;
   const ctx=node.getContext('2d');if(!ctx)return;ctx.scale(ratio,ratio);ctx.clearRect(0,0,w,h);
   ctx.fillStyle='#0a1320';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#152438';
   for(let x=0;x<w;x+=30){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}
   for(let y=0;y<h;y+=30){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
   const atoms=selected.atoms;const xs=atoms.map(a=>a[1]),ys=atoms.map(a=>a[2]);
   const loX=Math.min(...xs),hiX=Math.max(...xs),loY=Math.min(...ys),hiY=Math.max(...ys);
   const scale=Math.min((w-80)/Math.max(hiX-loX,1),(h-60)/Math.max(hiY-loY,1))*zoom;
   const xy=(a:number[])=>[w/2+(a[1]-(loX+hiX)/2)*scale,h/2-(a[2]-(loY+hiY)/2)*scale];
   ctx.strokeStyle='#294453';ctx.lineWidth=.6;
   atoms.forEach((a,i)=>atoms.slice(i+1).forEach(b=>{if(Math.hypot(a[1]-b[1],a[2]-b[2])<1.5){const p=xy(a),q=xy(b);ctx.beginPath();ctx.moveTo(...p as [number,number]);ctx.lineTo(...q as [number,number]);ctx.stroke()}}));
   const min=Math.min(...atoms.map(a=>a[color])),max=Math.max(...atoms.map(a=>a[color]));
   atoms.forEach(a=>{const [x,y]=xy(a);const t=(a[color]-min)/Math.max(max-min,.01);ctx.beginPath();ctx.arc(x,y,Math.min(5,Math.max(2.5,scale*.17)),0,2*Math.PI);ctx.fillStyle=color===4?`hsl(${180-170*t} 75% ${60-t*10}%)`:`hsl(${210-180*t} 65% 65%)`;ctx.fill()});
   node.onmousemove=(event)=>{const rect=node.getBoundingClientRect();let found:number[]|null=null;atoms.forEach(a=>{const [x,y]=xy(a);if(Math.hypot(event.clientX-rect.left-x,event.clientY-rect.top-y)<9)found=a});setHover(found)};
  };draw();const observer=new ResizeObserver(draw);observer.observe(node);return()=>{observer.disconnect();node.onmousemove=null};
 },[selected,color,zoom]);
 return <section className="panel" id="structure"><div className="panelhead"><h2><span className="muted mono">02 / </span>Atomic structure</h2><select aria-label="Atom color measurement" value={color} onChange={e=>setColor(Number(e.target.value))}><option value={4}>Bond loss ΔZ</option><option value={3}>Coordination Z</option><option value={5}>Per-atom tensile virial</option></select></div><canvas ref={canvas} style={{height:350}} aria-label="Interactive molecular lattice, hover atoms for measurements" onWheel={e=>setZoom(z=>Math.max(.6,Math.min(3,z-e.deltaY*.001)))}/><div className="panelbody"><div className="toolbar"><label className="caption" htmlFor="frame">Trajectory frame</label><input id="frame" aria-label="Trajectory frame" type="range" min="0" max={Math.max(0,snapshots.length-1)} value={frame} onChange={e=>setFrame(Number(e.target.value))}/><span className="caption mono">{['Initial','Peak stress','Fracture / last'][frame]} · ε {selected?.strain.toFixed(3)??'—'}</span><button onClick={()=>setZoom(1)} aria-label="Reset lattice zoom">Reset view</button></div><p className="caption">{hover?`Atom ${hover[0]} · x ${hover[1].toFixed(3)}, y ${hover[2].toFixed(3)} · Z ${hover[3]} · ΔZ ${hover[4]} · virial ${hover[5].toFixed(3)}`:'Hover to inspect an atom. Scroll to zoom. Cyan → red indicates increasing bond loss.'}</p><p className="caption">Actual coordinates; reference bonds are measured after equilibration and NVE. Aggregate snapshots show the first replicate.</p></div></section>
}
