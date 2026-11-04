import type {View} from '@/lib/presentation';
export default function DemoWalkthrough({onNavigate}: {onNavigate?: (view: View, section: string) => void}) {
  const steps: [View, string, string, string, string][] = [
    ['investigate', 'structure', '1 · Inspect the sample', 'Look at the recorded material and how it responds to stretching. This is a small 2D research simulation.', 'Go to material'],
    ['investigate', 'hypotheses', '2 · Compare explanations', 'Read the possible causes. If none are listed yet, use Suggest possible causes in Explore step by step at the top.', 'Go to explanations'],
    ['investigate', 'plan', '3 · Choose a useful test', 'Read what the next test changes and why it was selected. Use Run this test there to execute it.', 'Go to next test'],
    ['results', 'verify', '4 · Follow the measured result', 'Compare the original and changed simulations. If no test has run yet, the results view will explain what is still needed.', 'Go to results'],
    ['evidence', 'report', '5 · Check how the explanation changed', 'Review recorded model responses, fallback actions and independent checks in the evidence trail.', 'Go to evidence'],
    ['results', 'verify', '6 · Read the conclusion', 'A single case can provide partial evidence. The complete published study remains NOT_VALIDATED.', 'Read conclusion'],
  ];
  return <section className="panel blockgap" aria-label="Investigation guide"><div className="panelhead"><div><span className="overline">Step-by-step guide</span><h2>Follow an investigation</h2></div></div><div className="panelbody"><p>These shortcuts take you to the relevant section. They do not run experiments. To run the entire workflow, use <strong>Run full investigation</strong> at the top.</p><p className="caption">AI proposes explanations. Physics tests them. An independent verifier checks what the evidence supports. This workspace uses published samples; it is not a new blinded study.</p><div className="cards">{steps.map(([view, section, title, text, action]) => <article key={title} className="hypothesis"><h3>{title}</h3><p className="caption">{text}</p>{onNavigate && <button onClick={() => onNavigate(view, section)}>{action} <span aria-hidden="true">↑</span></button>}</article>)}</div></div></section>;
}
