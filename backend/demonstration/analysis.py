"""Registered contrast criteria, independent of case ID or hidden preparation."""
import numpy as np
from scipy.stats import t
from backend.models.schemas import SimulationSummary


def discriminating_contrast(baseline,winner,competitor):
    cohorts=[baseline,winner,competitor]
    seeds=[r.seed for r in baseline]
    if len(seeds)<3 or len(seeds)!=len(set(seeds)) or any({r.seed for r in c}!=set(seeds) or len(c)!=len(seeds) for c in cohorts):return {'is_distinguishable':False,'status':'UNMATCHED_SEEDS'}
    if any(not r.numerical_check.is_valid or r.outcome=='EXECUTION_FAILED' for c in cohorts for r in c):return {'is_distinguishable':False,'status':'EXECUTION_FAILED'}
    if any(r.failure_strain is None for c in cohorts for r in c):return {'is_distinguishable':False,'status':'CENSORED'}
    by_seed=[{r.seed:r for r in c} for c in cohorts]
    x=np.array([by_seed[0][s].failure_strain for s in seeds]);w=np.array([by_seed[1][s].failure_strain for s in seeds]);c=np.array([by_seed[2][s].failure_strain for s in seeds])
    delta=w-c;mean=float(delta.mean());std=float(delta.std(ddof=1));snr=abs(mean)/np.sqrt(std**2+.004**2)
    margin=100*mean/float(x.mean());half=float(t.ppf(.975,len(seeds)-1)*std/np.sqrt(len(seeds)))
    return {'status':'COMPLETE','n':len(seeds),'mean_strain_contrast':mean,'contrast_recovery_percentage_points':margin,'contrast_snr':float(snr),'mean_contrast_t_interval95':[mean-half,mean+half],'interval_assumption':'Student-t, approximately normal independent seed-block contrasts; limited scope','is_distinguishable':bool(margin>=10 and snr>=2.5 and mean-half>0)}
