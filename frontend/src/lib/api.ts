export type AIMode='LIVE_MUSE_SPARK_API'|'OFFLINE_HEURISTIC_FALLBACK';
export type Verdict='PENDING'|'SUPPORTED'|'REJECTED'|'INCONCLUSIVE';
export interface Telemetry {execution_mode:AIMode;configured_model:string;base_url:string;api_key_present:boolean;last_call_latency_ms?:number;last_error?:string;prompt_tokens?:number;completion_tokens?:number}
export interface Snapshot {timestep:number;strain:number;stress_yy:number;potential_energy:number;kinetic_energy:number;atoms:number[][]}
export interface NumericalCheck {is_valid:boolean;energy_drift_ratio:number;max_force_norm:number;max_step_displacement:number;thermostat_temperature_error_ratio:number;notes:string}
export interface Simulation {sim_id:string;seed:number;replicate_seeds:number[];replicate_results:Simulation[];peak_stress:number;peak_stress_std:number;failure_strain:number|null;failure_strain_std:number;max_observed_strain:number;outcome:'FRACTURED'|'NOT_FRACTURED_WITHIN_HORIZON'|'EXECUTION_FAILED';stress_strain_curve:{strain:number;stress:number;stress_std:number}[];snapshots:Snapshot[];numerical_check:NumericalCheck;engine_used:string;wall_time_sec:number;protocol_hash:string;initial_configuration_hash:string;crack_initiation_region:string;units:string;solver_version:string;error_code:string|null;error_message:string|null}
export interface Case {case_id:string;display_title:string;atom_count:number;material_system:string;initial_observations_summary:string;baseline_simulation:Simulation}
export interface Hypothesis {id:string;title:string;mechanism:string;suspected_cause:string;confidence:number;status:Verdict;supporting_evidence:string[];missing_evidence:string;proposed_intervention:string;predicted_strain_recovery_pct:number;ai_execution_mode:AIMode}
export interface Proposal {experiment_id:string;target_hypothesis_id:string;intervention:string;rationale:string;estimated_cost_sec:number;expected_information_gain:number;risk_penalty:number;utility_score:number;matched_seeds:number[];ai_execution_mode:AIMode}
export interface Verification {experiment_id:string;hypothesis_id:string;intervention:string;verdict:Verdict;execution_status:string;strain_recovery_pct:number|null;signal_to_noise_ratio:number;cv_pct:number|null;numerical_consistency_passed:boolean;scientific_explanation:string;censoring_counts:Record<string,number>;statistics_label:string;matched_seeds_used:number[]}
export interface Audit {timestamp:string;stage:string;message:string;cached?:boolean;[key:string]:unknown}
export interface Investigation {case_id:string;status:string;is_running:boolean;current_step_message:string;ai_telemetry:Telemetry;ai_execution_mode:AIMode;budget_total_sec:number;budget_used_sec:number;hypotheses:Hypothesis[];proposed_experiments:Proposal[];executed_experiments:Record<string,Simulation>;verifications:Verification[];identified_cause:string|null;final_verdict_summary:string;audit_log:Audit[]}
export interface CaseResponse {case:Case;investigation:Investigation}
export interface Health {status:string;engine:{engine:string;pair_validation:string;reason?:string};calibrated_atom_count:number;ai_telemetry:Telemetry;budget_limit_sec:number;cases_ready:boolean}
export interface Job {id:string;status:string;error?:string;current_step_message:string;elapsed_sec:number}

export async function api<T>(path:string,body?:unknown):Promise<T>{
 const response=await fetch('/api'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(15000),cache:'no-store'});
 if(!response.ok){const message=await response.text();throw new Error(`HTTP ${response.status}: ${message}`)}
 return response.json() as Promise<T>;
}
export const terminal=(status:string)=>!['QUEUED','RUNNING'].includes(status);
export const outcomeLabel=(s:Simulation)=>s.outcome==='NOT_FRACTURED_WITHIN_HORIZON'?'NO_FRACTURE_OBSERVED · right-censored':s.outcome;
export const pct=(value:number|null|undefined)=>value==null?'—':`${value.toFixed(2)}%`;
