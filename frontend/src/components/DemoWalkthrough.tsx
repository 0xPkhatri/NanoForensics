import type {View} from '@/lib/presentation';
export default function DemoWalkthrough({onNavigate}: {onNavigate?: (view: View) => void}) {
  const steps: [View, string, string][] = [
    ['investigate', '1 · Inspect the sample', 'Look at the recorded material and its stretching response. This is a small 2D research simulation.'],
    ['investigate', '2 · Compare explanations', 'Start the investigation, or suggest possible causes with the manual controls. Each action shows its source.'],
    ['investigate', '3 · Choose a useful test', 'Read what the next test changes and why the planner selected it. Predictions are not measurements.'],
    ['results', '4 · Follow the measured result', 'Compare the original and changed simulations. Actual compute time varies; saved data is identified as saved.'],
    ['evidence', '5 · Check how the explanation changed', 'Review actual model responses, fallback actions and independent checks in the timestamped evidence trail.'],
    ['results', '6 · Keep the conclusion in scope', 'A single case can provide partial evidence. The complete published study remains NOT_VALIDATED.'],
  ];
  return <section className="panel blockgap" aria-label="Hackathon walkthrough"><div className="panelhead"><div><span className="overline">Post-study presentation guide</span><h2>From a question to measured evidence</h2></div></div><div className="panelbody"><p>AI proposes. Physics tests. An independent verifier checks what the evidence supports.</p><div className="cards">{steps.map(([view, title, text]) => <article key={title} className="hypothesis"><h3>{title}</h3><p className="caption">{text}</p>{onNavigate && <button onClick={() => onNavigate(view)}>Open {view}</button>}</article>)}</div></div></section>;
}
