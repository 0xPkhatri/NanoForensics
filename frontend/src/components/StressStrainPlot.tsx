'use client';
import {useEffect, useRef, useState} from 'react';
import type {Data, Layout} from 'plotly.js';
import type {Simulation} from '@/lib/api';
import {outcomeText} from '@/lib/presentation';
export default function StressStrainPlot({baseline, counterfactual, deterministic = false}: {baseline: Simulation; counterfactual?: Simulation; deterministic?: boolean}) {
  const ref = useRef<HTMLDivElement>(null), [error, setError] = useState('');
  useEffect(() => {
    let stopped = false, purge: (() => void) | undefined;
    setError('');
    import('plotly.js-dist-min').then(async Plotly => {
      if (stopped || !ref.current) return;
      const data: Data[] = [];
      const runs: [Simulation, string, string][] = [[baseline, 'Original sample', '#2457d6']];
      if (counterfactual) runs.push([counterfactual, 'Test change', '#b94218']);
      runs.forEach(([sim, name, color], index) => {
        const x = sim.stress_strain_curve.map(p => p.strain * 100), y = sim.stress_strain_curve.map(p => p.stress), std = sim.stress_strain_curve.map(p => p.stress_std || 0);
        data.push({x, y: y.map((v, i) => v - std[i]), type: 'scatter', mode: 'lines', line: {width: 0}, hoverinfo: 'skip', showlegend: false});
        data.push({x, y: y.map((v, i) => v + std[i]), type: 'scatter', mode: 'lines', line: {width: 0}, fill: 'tonexty', fillcolor: index ? 'rgba(185,66,24,.1)' : 'rgba(36,87,214,.10)', hoverinfo: 'skip', showlegend: false});
        data.push({x, y, type: 'scatter', mode: 'lines', name, line: {color, width: 2.5, dash: index ? 'dash' : 'solid'}, hovertemplate: 'Stretch %{x:.2f}%<br>Stress %{y:.3f} LJ<extra>' + name + '</extra>'});
        if (sim.outcome === 'FRACTURED' && sim.failure_strain != null && x.length) {
          const at = x.reduce((best, value, i) => Math.abs(value - sim.failure_strain! * 100) < Math.abs(x[best] - sim.failure_strain! * 100) ? i : best, 0);
          data.push({x: [sim.failure_strain * 100], y: [y[at]], type: 'scatter', mode: 'markers', name: name + ' fracture', marker: {color, size: 10, symbol: 'x'}});
        }
      });
      const layout: Partial<Layout> = {autosize: true, height: 310, paper_bgcolor: '#fffdf8', plot_bgcolor: '#fffdf8', font: {family: 'system-ui, sans-serif', color: '#535b58', size: 13}, margin: {l: 62, r: 22, t: 56, b: 56}, xaxis: {title: {text: 'Stretch (%)'}, gridcolor: '#e9e3d7', zerolinecolor: '#c8c0b2'}, yaxis: {title: {text: 'Tensile stress · LJ units'}, gridcolor: '#e9e3d7', zerolinecolor: '#c8c0b2'}, legend: {orientation: 'h', y: 1.22, font: {size: 12}}, hovermode: 'x unified'};
      const node = ref.current;
      await Plotly.newPlot(node, data, layout, {responsive: true, displaylogo: false, displayModeBar: false});
      if (stopped) {Plotly.purge(node); return}
      const observer = new ResizeObserver(() => Plotly.Plots.resize(node)); observer.observe(node);
      purge = () => {observer.disconnect(); Plotly.purge(node)};
    }).catch(e => {if (!stopped) setError(String(e))});
    return () => {stopped = true; purge?.()};
  }, [baseline, counterfactual]);
  return <section className="panel chart-panel" id="observe"><div className="panelhead"><div><span className="overline">The measured response</span><h2>What happens as it stretches?</h2></div></div>{error ? <p className="error">The chart could not load: {error}</p> : <div ref={ref} className="response-chart" role="img" aria-label={`Measured stretching response. ${outcomeText(baseline)}. ${counterfactual ? 'A dashed orange line shows the selected test change.' : 'A solid blue line shows the original sample.'}`}/>}<div className="panelbody chart-notes"><p className="caption">{outcomeText(baseline)}. {deterministic ? 'Shading shows deterministic replay spread, not population uncertainty.' : 'Shading shows ±1 standard deviation across valid runs, not a confidence interval.'}</p><details><summary>Measurements and units</summary><p className="caption">Engineering strain × 100 = stretch percentage. Tensile-positive virial stress from mobile atoms; nominal width × current gauge length, unit thickness. LJ reduced units, not MPa. Numerical failures are excluded from causal comparisons; any failed recorded curves are diagnostic only.</p><p className="caption">{baseline.stress_strain_curve.length} measured samples · {baseline.replicate_results.filter(run => run.outcome !== 'EXECUTION_FAILED' && run.numerical_check.is_valid).length} numerically valid / {baseline.replicate_results.length} recorded runs · {baseline.replicate_seeds.length} {deterministic ? 'replay labels; no independent thermal samples' : 'seed labels; limited-sample statistics'}</p><div className="tablewrap"><table><caption>Recorded stress and stretch (original sample)</caption><thead><tr><th>Stretch (%)</th><th>Stress (LJ)</th><th>Spread</th></tr></thead><tbody>{baseline.stress_strain_curve.map((point, i) => <tr key={i}><td>{(point.strain * 100).toFixed(2)}</td><td>{point.stress.toFixed(4)}</td><td>{point.stress_std?.toFixed(4) ?? '—'}</td></tr>)}</tbody></table></div></details></div></section>;
}
