export interface ScrollSnapshot {top:number;previousTop:number;height:number;viewport:number;following:boolean;programmatic:boolean;userIntent:boolean}
export function followDecision(value: ScrollSnapshot): 'pause'|'resume'|'keep' {
  if (value.programmatic) return 'keep';
  const bottom = value.height-value.viewport-value.top <= 18;
  if (value.following && value.top < value.previousTop-1 && !bottom) return 'pause';
  if (!value.following && value.userIntent && bottom) return 'resume';
  return 'keep';
}
