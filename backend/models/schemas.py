from enum import Enum

from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, model_validator

class SimulationOutcome(str, Enum):
    FRACTURED = "FRACTURED"
    NOT_FRACTURED_WITHIN_HORIZON = "NOT_FRACTURED_WITHIN_HORIZON"
    EXECUTION_FAILED = "EXECUTION_FAILED"

class DefectType(str, Enum):

    INTERIOR_VACANCY = "interior_vacancy"

    SURFACE_NOTCH = "surface_notch"

    HIGH_STRAIN_RATE = "high_strain_rate"

    THERMAL_SOFTENING = "thermal_softening"

    UNKNOWN_STOCHASTIC = "unknown_stochastic"

class InterventionType(str, Enum):

    HEAL_INTERIOR_VACANCY = "heal_interior_vacancy"

    SMOOTH_SURFACE_NOTCH = "smooth_surface_notch"

    NORMALIZE_STRAIN_RATE = "normalize_strain_rate"

    NORMALIZE_TEMPERATURE = "normalize_temperature"

    REPEAT_REPLICATE_SEEDS = "repeat_replicate_seeds"

class HypothesisStatus(str, Enum):

    PENDING = "PENDING"

    SUPPORTED = "SUPPORTED"

    REJECTED = "REJECTED"

    INCONCLUSIVE = "INCONCLUSIVE"

class AIExecutionMode(str, Enum):

    LIVE_MUSE_SPARK_API = "LIVE_MUSE_SPARK_API"

    OFFLINE_HEURISTIC_FALLBACK = "OFFLINE_HEURISTIC_FALLBACK"

class AtomSnapshot(BaseModel):

    timestep: int

    strain: float

    stress_yy: float

    potential_energy: float

    kinetic_energy: float

    # Each row: [atom_id, x, y, coordination_z, bond_loss_delta_z, per_atom_virial_yy]

    atoms: List[List[float]]

class NumericalConsistencyCheck(BaseModel):

    is_valid: bool

    max_force_norm: float

    max_step_displacement: float

    thermostat_temperature_error_ratio: float

    energy_drift_ratio: float  # Measured in pre-load NVE validation step (|ΔE_tot| / |E_tot(0)|)

    nan_detected: bool

    fracture_criterion_met: bool

    notes: str

class SimulationSummary(BaseModel):

    units: str = "lj_reduced_2d"
    solver_version: str = "sflj-1.0"
    strain_rate_convention: str = "engineering strain / LJ time"
    area_convention: str = "nominal width * current grip gauge; unit thickness; tensile-positive virial"
    effective_gauge_length: float = 0.0
    reference_geometry: Dict[str, Any] = Field(default_factory=dict)
    measurement_horizon: Dict[str, float] = Field(default_factory=dict)
    replicate_results: List[Dict[str, Any]] = Field(default_factory=list)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    sim_id: str

    seed: int

    replicate_seeds: List[int] = Field(default_factory=list)

    peak_stress: float

    peak_stress_std: float = 0.0

    failure_strain: Optional[float] = None  # null when right-censored

    failure_strain_std: float = 0.0

    toughness: float

    crack_initiation_region: str  # "interior", "surface_left", "surface_right", "distributed"

    mean_coordination_at_peak: float

    max_bond_loss_cluster_size: int = 0

    min_coordination_region: str

    stress_strain_curve: List[Dict[str, float]]  # [{"strain": float, "stress": float, "stress_std": float}, ...]

    snapshots: List[AtomSnapshot]                # [initial_frame, peak_stress_frame, fracture_frame or last frame]

    outcome: SimulationOutcome = SimulationOutcome.NOT_FRACTURED_WITHIN_HORIZON  # FRACTURED, NOT_FRACTURED_WITHIN_HORIZON, EXECUTION_FAILED

    max_observed_strain: float = 0.0

    protocol_hash: str = ""

    initial_configuration_hash: str = ""

    numerical_check: NumericalConsistencyCheck

    wall_time_sec: float

    engine_used: str                             # "LAMMPS_BINARY" or "NUMPY_VELOCITY_VERLET_2D"

class Hypothesis(BaseModel):
    model_config = {"extra": "forbid", "allow_inf_nan": False}

    id: str

    title: str

    mechanism: str

    suspected_cause: DefectType

    supporting_evidence: List[str]

    missing_evidence: str

    proposed_intervention: InterventionType

    predicted_strain_recovery_pct: float = Field(

        description="Predicted % increase in failure strain if this mechanism is repaired"

    )

    confidence: float = Field(ge=0.0, le=1.0)

    status: HypothesisStatus = HypothesisStatus.PENDING

    provenance: Dict[str, Any] = Field(default_factory=dict)
    @property
    def generated_by(self) -> AIExecutionMode:
        return self.ai_execution_mode

    ai_execution_mode: AIExecutionMode = AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK

class ExperimentProposal(BaseModel):

    provenance: Dict[str, Any] = Field(default_factory=dict)

    experiment_id: str

    case_id: str                                 # Always opaque: CASE_ALPHA, CASE_BETA, etc.

    target_hypothesis_id: str

    intervention: InterventionType

    matched_seeds: List[int]                     # Seeds matched to baseline + replicate seeds

    controlled_parameters: Dict[str, Any]

    modified_parameters: Dict[str, Any]

    rationale: str

    estimated_cost_sec: float

    expected_information_gain: float

    risk_penalty: float

    utility_score: float

    ai_execution_mode: AIExecutionMode = AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK

class VerificationResult(BaseModel):

    experiment_id: str

    hypothesis_id: str

    intervention: InterventionType

    matched_seeds_used: List[int]

    baseline_failure_strain: Optional[float] = None

    counterfactual_failure_strain: Optional[float] = None

    strain_recovery_pct: Optional[float] = None

    replicate_std_pct: float

    signal_to_noise_ratio: float

    baseline_peak_stress: float

    counterfactual_peak_stress: float

    stress_shift_pct: Optional[float] = None

    baseline_crack_region: str

    counterfactual_crack_region: str

    numerical_consistency_passed: bool

    verdict: HypothesisStatus

    execution_status: str = "COMPLETE"

    paired_mean_shift: Optional[float] = None
    paired_std: Optional[float] = None
    cv_pct: Optional[float] = None
    stress_snr: Optional[float] = None
    censoring_counts: Dict[str, int] = Field(default_factory=dict)
    baseline_result_ids: List[str] = Field(default_factory=list)
    counterfactual_result_ids: List[str] = Field(default_factory=list)
    statistics_label: str = "descriptive; three matched pairs do not establish population confidence"
    scientific_explanation: str

class FailureCasePublic(BaseModel):

    observed_configuration: Dict[str, Any] = Field(default_factory=dict)

    case_id: str                                 # Opaque: CASE_ALPHA, CASE_BETA, CASE_GAMMA, CASE_DELTA

    display_title: str                           # e.g., "Blind Specimen Alpha (2D Hexagonal LJ)"

    material_system: str

    atom_count: int

    nominal_strain_rate: float

    reported_strain_rate: Optional[float] = None  # include only if directly measured/authorized and equally shown to all baseline agents

    temperature_lj: Optional[float] = None  # private unless independently observable and disclosed to every comparator

    initial_observations_summary: str

    baseline_simulation: SimulationSummary

class LLMTelemetry(BaseModel):

    execution_mode: AIExecutionMode

    configured_model: str

    base_url: str

    api_key_present: bool

    last_call_latency_ms: Optional[float] = None

    last_error: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    response_id: Optional[str] = None

class InvestigationState(BaseModel):

    case_id: str

    status: str  # "OBSERVING", "HYPOTHESIZING", "EXPERIMENTING", "CONCLUDED", "INCONCLUSIVE"

    is_running: bool = False

    current_step_message: str = "Idle"

    ai_telemetry: LLMTelemetry

    ai_execution_mode: AIExecutionMode = AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK

    budget_total_sec: float = 1800.0

    budget_used_sec: float = 0.0

    hypotheses: List[Hypothesis] = Field(default_factory=list)

    proposed_experiments: List[ExperimentProposal] = Field(default_factory=list)

    executed_experiments: Dict[str, SimulationSummary] = Field(default_factory=dict)

    verifications: List[VerificationResult] = Field(default_factory=list)

    identified_cause: Optional[DefectType] = None

    final_verdict_summary: str = ""

    audit_log: List[Dict[str, Any]] = Field(default_factory=list)



class StrictModel(BaseModel):
    model_config = {"extra": "forbid", "allow_inf_nan": False}

class Protocol(StrictModel):
    dt: float = Field(default=0.002, gt=0, le=0.005)
    temperature: float = Field(default=0.05, ge=0, le=0.5)
    strain_rate: float = Field(default=0.05, gt=0, le=1)
    max_strain: float = Field(default=0.65, gt=0, le=1.5)
    sample_every: int = Field(default=25, ge=1, le=500)
    warmup_steps: int = Field(default=2000, ge=0, le=20000)
    gamma: float = Field(default=2.0, ge=0, le=20)
    nve_steps: int = Field(default=50, ge=50, le=1000)
    minimize_tolerance: float = Field(default=0.005, gt=0, le=0.01)
    seed: int = Field(default=42, ge=1, le=2147483646)

class SpecimenInput(StrictModel):
    coordinates: List[List[float]]
    atom_ids: List[int]
    protocol: Protocol = Field(default_factory=Protocol)
    @model_validator(mode="after")
    def valid_coordinates(self):
        import numpy as np
        q=np.asarray(self.coordinates)
        if q.ndim != 2 or q.shape[1] != 2 or not 8 <= len(q) <= 1024 or not np.isfinite(q).all():
            raise ValueError("finite N x 2 coordinates; 8 <= N <= 1024 required")
        if len(self.atom_ids) != len(q) or len(set(self.atom_ids)) != len(q):
            raise ValueError("unique atom ids required")
        return self

class InterventionParameters(StrictModel):
    target_temperature: Optional[float] = Field(default=None, ge=0.001, le=0.5)
    target_strain_rate: Optional[float] = Field(default=None, ge=0.01, le=0.2)

class ExperimentRequest(StrictModel):
    proposal_id: Optional[str] = Field(default=None, max_length=100)
    intervention: Optional[InterventionType] = None
    parameters: InterventionParameters = Field(default_factory=InterventionParameters)
    @model_validator(mode="after")
    def has_selection(self):
        if bool(self.proposal_id) == bool(self.intervention):
            raise ValueError("specify exactly one proposal_id or intervention")
        return self

class ModelDecision(StrictModel):
    hypotheses: List[Hypothesis] = Field(min_length=2, max_length=5)
    ranking: List[InterventionType] = Field(min_length=2, max_length=5)
    revision: str = Field(max_length=4000)


class InvestigationRequest(StrictModel):
    max_experiments: int = Field(default=4, ge=1, le=5)
    timeout_sec: Optional[float] = Field(default=None, ge=0.05, le=1800)
