"""Freeze all decisions BEFORE the separate privileged scoring step."""
import argparse
import json
import tempfile
import time
from pathlib import Path
from backend.config import ROOT
from backend.storage.db import Store
from backend.agents.investigator import NanoForensicsInvestigator
from benchmarks.fixed_checklist import FixedChecklist
from benchmarks.oneshot_baseline import run as one_shot


def clone_store(source,path):
    target=Store(path)
    with source.connect() as src,target.connect() as dst:
        for table in ['specimens','results']:
            for row in src.execute(f'SELECT * FROM {table}'):
                dst.execute(f'INSERT OR IGNORE INTO {table} VALUES({",".join("?" for _ in row)})',tuple(row))
    return target


def evaluate(source=None,output=None):
    source=source or Store(); output=Path(output or ROOT/'docs/BENCHMARK_REPORT.md')
    if len(source.case_ids())!=4: raise RuntimeError('Generate and freeze all four cases before benchmarking')
    records=[]
    with tempfile.TemporaryDirectory(prefix='nf-evaluation-') as tmp:
        for method,klass in [('Fixed checklist',FixedChecklist),('NanoForensics',NanoForensicsInvestigator)]:
            trial=clone_store(source,Path(tmp)/(method+'.db'))
            for case_id in source.case_ids():
                started=time.perf_counter()
                state=klass(trial).investigate(case_id)
                records.append({'method':method,'case_id':case_id,'identified_cause':state.identified_cause.value if state.identified_cause else None,'status':state.status,'wall_time_sec':time.perf_counter()-started,'ai_execution_mode':state.ai_execution_mode.value,'experimental_budget':4,'replicate_seeds':[42,137,271],'actual_experiments':len(state.executed_experiments),'model_calls':sum(e['stage'] in ['hypothesize','belief_revision'] and bool(e.get('provenance',{}).get('response_hash')) for e in state.audit_log),'raw':state.model_dump(mode='json')})
        for case_id in source.case_ids():
            started=time.perf_counter();result=one_shot(source.public(case_id))
            records.append({'method':'One-shot','case_id':case_id,**result,'wall_time_sec':time.perf_counter()-started})
    # Predictions and raw evidence fixed before privileged scoring opens labels.
    output.parent.mkdir(parents=True,exist_ok=True)
    raw_path=output.with_suffix('.json')
    raw_path.write_text(json.dumps(records,indent=2))
    truth=json.loads((ROOT/'benchmarks'/'ground_truth.json').read_text())
    rows=[];counts={}
    for row in records:
        decision=row['identified_cause']
        score='NO_DECISION' if decision is None else 'CORRECT' if decision==truth[row['case_id']]['cause'] else 'INCORRECT'
        counts.setdefault(row['method'],{'CORRECT':0,'INCORRECT':0,'NO_DECISION':0})[score]+=1
        rows.append(f"| {row['method']} | {row['case_id']} | {row['status']} | {score} | {row['wall_time_sec']:.2f} | {row['ai_execution_mode']} |")
    report='''# Blind benchmark evaluation

Four frozen simulated specimens; one descriptive trial per method. No population superiority claim is justified. All methods receive identical public coordinates, stress curves, trajectory snapshots and structural access. Investigator and fixed checklist each have at most four interventions, three matched seeds per condition and the same 1800 s limit. Cache hits are content-addressed and disclosed in raw audit records; wall time reflects reuse and is not a fresh-compute speed comparison. Fixed checklist uses zero model calls. One-shot has a one-call budget and **zero experimental budget by definition**; its predictions have no counterfactual verification. Live-model victories require actual verified provider calls.

| Method | Case | Scientific state | Scoring | Wall seconds | AI mode |
|---|---|---|---|---:|---|
'''+ '\n'.join(rows)+'\n\nCounts (correct / incorrect / NO_DECISION):\n\n'+ '\n'.join(f'- {method}: {v["CORRECT"]} / {v["INCORRECT"]} / {v["NO_DECISION"]}' for method,v in counts.items())+'\n\nActual evidence, failed numerics, censoring, paired recovery/SNR and complete action traces are in BENCHMARK_REPORT.json. ALPHA baseline numerical instability is preserved. Negative rate-normalization recovery is preserved. No labels entered any investigator prompt. Statistical estimates from three pairs are descriptive.\n'
    output.write_text(report)
    return {'counts':counts,'report':str(output),'raw':str(raw_path)}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--db');args=parser.parse_args()
    print(json.dumps(evaluate(Store(args.db) if args.db else None),indent=2))
