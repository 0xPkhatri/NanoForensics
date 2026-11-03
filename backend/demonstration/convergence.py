"""Deterministic finite-difference identity; no synthetic replicas or population inference."""

def deterministic_winner(baseline,arms):
    cohort=[baseline,*arms.values()]
    if any(not r.numerical_check.is_valid or r.failure_strain is None or r.outcome=='EXECUTION_FAILED' for r in cohort):return None
    supported=[]
    for name,result in arms.items():
        change=result.failure_strain-baseline.failure_strain
        if 100*change/baseline.failure_strain>=18 and change/.004>=2.5:supported.append(name)
    if not supported or len(arms)!=2:return None
    winner=max(supported,key=lambda name:arms[name].failure_strain);other=next(name for name in arms if name!=winner)
    contrast=arms[winner].failure_strain-arms[other].failure_strain
    return winner if 100*contrast/baseline.failure_strain>=10 and contrast/.004>=2.5 else None
