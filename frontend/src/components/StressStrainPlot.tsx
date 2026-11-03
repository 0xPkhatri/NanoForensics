'use client';
import {useEffect,useRef,useState} from 'react';
import type {Data,Layout} from 'plotly.js';
import {Simulation,outcomeLabel} from '@/lib/api';
export default function StressStrainPlot({baseline,counterfactual,deterministic=false}:{baseline:Simulation;counterfactual?:Simulation;deterministic?:boolean}){
 const ref=useRef<HTMLDivElement>(null);const [error,setError]=useState('');
 useEffect(()=>{let stopped=false;let purge:(()=>void)|undefined;
  import('plotly.js-dist-min').then(Plotly=>{
   if(stopped||!ref.current)return;
   const data:Data[]=[];
   [[baseline,'Baseline','#8ddad9'],...(counterfactual?[[counterfactual,'Counterfactual','#d3b3ff']]:[])].forEach(tuple=>{
    const sim=tuple[0] as Simulation,name=tuple[1] as string,color=tuple[2] as string;
    const x=sim.stress_strain_curve.map(p=>p.strain),y=sim.stress_strain_curve.map(p=>p.stress),std=sim.stress_strain_curve.map(p=>p.stress_std);
    data.push({x,y:y.map((v,i)=>v-std[i]),type:'scatter',mode:'lines',line:{width:0},hoverinfo:'skip',showlegend:false});
    data.push({x,y:y.map((v,i)=>v+std[i]),type:'scatter',mode:'lines',line:{width:0},fill:'tonexty',fillcolor:name==='Baseline'?'rgba(141,218,217,.15)':'rgba(211,179,255,.15)',hoverinfo:'skip',showlegend:false});
    data.push({x,y,type:'scatter',mode:'lines',name,line:{color,width:2},hovertemplate:'ε %{x:.3f}<br>σyy %{y:.3f}<extra>'+name+'</extra>'});
    if(sim.failure_strain!=null&&sim.outcome==='FRACTURED'){const at=x.reduce((best,value,index)=>Math.abs(value-sim.failure_strain!)<Math.abs(x[best]-sim.failure_strain!)?index:best,0);data.push({x:[sim.failure_strain],y:[y[at]],mode:'markers',type:'scatter',name:name+' fracture',marker:{color,size:10,symbol:'x'}})}
   });
   const layout:Partial<Layout>={autosize:true,height:350,paper_bgcolor:'#0e1828',plot_bgcolor:'#0e1828',font:{family:'Arial',color:'#a9b9ce',size:11},margin:{l:55,r:25,t:20,b:55},xaxis:{title:{text:'Engineering strain ε'},gridcolor:'#243247',zerolinecolor:'#354558'},yaxis:{title:{text:'Tensile virial σyy · LJ units'},gridcolor:'#243247',zerolinecolor:'#354558'},legend:{orientation:'h',y:1.12},hovermode:'x unified'};
   Plotly.newPlot(ref.current,data,layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:['lasso2d','select2d']});
   const node=ref.current;const observer=new ResizeObserver(()=>{Plotly.Plots.resize(node)});observer.observe(node);purge=()=>{observer.disconnect();Plotly.purge(node)};
  }).catch(e=>setError(String(e)));
  return()=>{stopped=true;purge?.()};
 },[baseline,counterfactual]);
 return <section className="panel" id="observe"><div className="panelhead"><h2><span className="muted mono">01 / </span>Mechanical response</h2><span className="badge">{deterministic?'ACTUAL MD · EXACT REPLAYS':'ACTUAL MD · ±1σ'}</span></div>{error?<p className="error">Chart failed: {error}</p>:<div ref={ref} style={{minHeight:350}}/>}<div className="panelbody"><p className="caption">{outcomeLabel(baseline)} · {baseline.replicate_seeds.length||1} baseline {deterministic?'replay labels':'seeds'} · {baseline.stress_strain_curve.length} measured strain samples</p><p className="caption">Tensile-positive virial, mobile atoms only; nominal width × current gauge and unit thickness. {deterministic?'Any envelope is replay spread, not a population uncertainty band.':'Shading is standard deviation across numerically valid replicates.'} Numerical failures are excluded from causal comparisons.</p></div></section>
}
