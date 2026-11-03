# Blind benchmark evaluation

Four frozen simulated specimens; one descriptive trial per method. No population superiority claim is justified. All methods receive identical public coordinates, stress curves, trajectory snapshots and structural access. Investigator and fixed checklist each have at most four interventions, three matched seeds per condition and the same 1800 s limit. Cache hits are content-addressed and disclosed in raw audit records; wall time reflects reuse and is not a fresh-compute speed comparison. Fixed checklist uses zero model calls. One-shot has a one-call budget and **zero experimental budget by definition**; its predictions have no counterfactual verification. Live-model victories require actual verified provider calls.

| Method | Case | Scientific state | Scoring | Wall seconds | AI mode |
|---|---|---|---|---:|---|
| Fixed checklist | CASE_ALPHA | INCONCLUSIVE | NO_DECISION | 3.87 | OFFLINE_HEURISTIC_FALLBACK |
| Fixed checklist | CASE_BETA | INCONCLUSIVE | NO_DECISION | 0.06 | OFFLINE_HEURISTIC_FALLBACK |
| Fixed checklist | CASE_DELTA | INCONCLUSIVE | NO_DECISION | 0.05 | OFFLINE_HEURISTIC_FALLBACK |
| Fixed checklist | CASE_GAMMA | INCONCLUSIVE | NO_DECISION | 0.05 | OFFLINE_HEURISTIC_FALLBACK |
| NanoForensics | CASE_ALPHA | INCONCLUSIVE | NO_DECISION | 3.93 | OFFLINE_HEURISTIC_FALLBACK |
| NanoForensics | CASE_BETA | INCONCLUSIVE | NO_DECISION | 0.08 | OFFLINE_HEURISTIC_FALLBACK |
| NanoForensics | CASE_DELTA | INCONCLUSIVE | NO_DECISION | 0.09 | OFFLINE_HEURISTIC_FALLBACK |
| NanoForensics | CASE_GAMMA | INCONCLUSIVE | NO_DECISION | 0.07 | OFFLINE_HEURISTIC_FALLBACK |
| One-shot | CASE_ALPHA | NO_DECISION | NO_DECISION | 0.01 | OFFLINE_HEURISTIC_FALLBACK |
| One-shot | CASE_BETA | NO_DECISION | NO_DECISION | 0.01 | OFFLINE_HEURISTIC_FALLBACK |
| One-shot | CASE_DELTA | NO_DECISION | NO_DECISION | 0.01 | OFFLINE_HEURISTIC_FALLBACK |
| One-shot | CASE_GAMMA | NO_DECISION | NO_DECISION | 0.01 | OFFLINE_HEURISTIC_FALLBACK |

Counts (correct / incorrect / NO_DECISION):

- Fixed checklist: 0 / 0 / 4
- NanoForensics: 0 / 0 / 4
- One-shot: 0 / 0 / 4

Actual evidence, failed numerics, censoring, paired recovery/SNR and complete action traces are in BENCHMARK_REPORT.json. ALPHA baseline numerical instability is preserved. Negative rate-normalization recovery is preserved. No labels entered any investigator prompt. Statistical estimates from three pairs are descriptive.
