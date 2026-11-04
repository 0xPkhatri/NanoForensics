import {stageNames} from '@/lib/investigation-view';
export default function InvestigationSteps({stage}: {stage: number}) {
  return <nav className="phase-sheet" aria-label="Investigation progress"><span className="overline">The scientific loop <span className="text-muted">· tests may repeat</span></span><ol className="phase-rail">{stageNames.map((name, i) => <li key={name} className={i === stage ? 'active' : ''} aria-current={i === stage ? 'step' : undefined}><span className="phase-number">{String(i + 1).padStart(2, '0')}</span><span>{name}</span>{i < 5 && <span className="phase-arrow" aria-hidden="true">→</span>}</li>)}</ol></nav>;
}
