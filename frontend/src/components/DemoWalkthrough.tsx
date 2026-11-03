export default function DemoWalkthrough(){
 return <section className="panel blockgap" aria-label="Hackathon walkthrough"><div className="panelhead"><h2>DEMO_501 · From suspicion to intervention</h2><span className="badge">POST-STUDY REHEARSAL</span></div><div className="panelbody"><p>One model proposes explanations. Real molecular dynamics tests them. An independent verifier decides what the evidence supports.</p><div className="cards">{[
 ['#observe','01 · Observe','Inspect the frozen baseline and its numerical checks. This is one athermal toy geometry, not a real material.'],
 ['#hypotheses','02 · Ask Muse Spark','Generate hypotheses. Open each action receipt to verify model, host, tokens and response hash. An API failure must show fallback.'],
 ['#plan','03 · Challenge both mechanisms','Compare model-authored rationale, information gain and risk. The two registered repairs and physical protocol remain fixed.'],
 ['#verify','04 · Run the counterfactuals','Start autonomous investigation to run both repairs, or use individual paired tests. Fresh MD takes about 15 seconds per replay; watch the worker trace.'],
 ['#report','05 · Follow the revision','Read how the model updates its subjective beliefs using measured effects and evidence IDs. It cannot override independent verdicts.'],
 ['#report','06 · Close with the limitation','Export the audit. This case has partial mechanistic evidence; the complete frozen study remains NOT_VALIDATED.'],
 ].map(([href,title,text])=><a key={title} href={href} className="hypothesis" style={{color:'inherit',textDecoration:'none'}}><h3>{title}</h3><p className="caption">{text}</p></a>)}</div></div></section>
}
