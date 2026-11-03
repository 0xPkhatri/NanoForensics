# AGENTS.md — NanoForensics Autonomous Build Specification (Audited v2)

**Hackathon:** Meta Global AI Developer Hackathon

**Theme:** Push the Frontier

**Category:** AI for Materials Science, Scientific Discovery, and Physical Systems

**Core Stack:** Meta Muse Spark (via OpenAI-compatible API with verified health probe), LAMMPS + Vectorized NumPy 2D-SFLJ Velocity-Verlet Engine, Python 3.11+, FastAPI, SQLite, Next.js 14 (App Router), TailwindCSS, Plotly.js

---

## 0. Agent Operating Directives & Anti-Cheating Guardrails (READ FIRST)

You are an autonomous staff-level engineer building **NanoForensics** from scratch (or resuming from a verified checkpoint under Section 10). Follow these rules strictly:

1. **STRICT BAN ON HARDCODED OR SYNTHETIC PHYSICS (`Zero-Mock Policy`):**
   - You are **strictly prohibited** from generating synthetic, polynomial, spline-fitted, or lookup-table stress-strain curves, or conditioning physics calculations on `case_id` or `InterventionType` names.

   - Every stress-strain point and fracture metric MUST be computed emergently from pairwise Shifted-Force Lennard-Jones (SFLJ) interatomic forces ($F_{ij} = -\nabla U_{\text{SFLJ}}(r_{ij})$), Velocity-Verlet trajectory integration, and the virial stress tensor.

   - **Anti-Cheating Test Gate:** `tests/test_physics_and_defects.py` will pass arbitrary, unindexed atom coordinate arrays into the MD solver and verify that perturbing a single atom's position alters the local force vector and virial stress tensor in exact agreement with analytical SFLJ derivatives, and that $U(r \to r_c^-) \to 0$ and $F(r \to r_c^-) \to 0$.

2. **Blind Opaque Case Identifiers (`Zero Label Leakage`):**
   - Public case identifiers MUST be completely opaque: `CASE_ALPHA`, `CASE_BETA`, `CASE_GAMMA`, and `CASE_DELTA`.

   - Never use descriptive strings like `INTERIOR_VOID` or `SURFACE_NOTCH` in `case_id`, filenames, simulation IDs, or metadata visible to the agent.

   - Store privileged preparation descriptors, hidden labels, and the original unmodified lattice site IDs exclusively in `benchmarks/ground_truth.json` (owned by benchmark-generation and scoring code). **No live investigator, live API response, hypothesis prompt, analysis module, planner, report before conclusion, or untrusted intervention executor may access it.** Opaque IDs alone are insufficient: public metadata, baseline initialization records, and accessible filesystem paths must be checked for leakage. Public metadata must omit or normalize hidden preparation parameters unless they are genuinely measured observations and are disclosed consistently to every baseline comparator.

3. **Dual-Mode Physics Engine with Verified SFLJ Potential Parity (`lammps_runner.py`):**
   - Check `shutil.which("lmp") or shutil.which("lmp_serial")` at runtime.

   - If a LAMMPS binary is installed, execute the Jinja2 template `tensile_2d_lj.in.j2`. If unavailable, execute the vectorized NumPy 2D Shifted-Force Lennard-Jones Velocity-Verlet engine (`backend/simulation/numpy_md_fallback.py`).

   - **Verified shifted-force parity:** Never use `pair_style lj/cut` as shifted-force. Prefer native LAMMPS `pair_style lj/smooth/linear 2.5` **only after verifying it exists in the installed LAMMPS binary**. If absent, use a validated SFLJ table. Validate analytic potential/force and actual interpolated LAMMPS pair output using `pair_write` or equivalent, not only the source table. Measure force/energy errors separately on physically visited distances, compare against absolute **and** relative tolerances, and explicitly record minimum sampled distance and maximum error. The source-table analytic values must satisfy `F(r) = -dU/dr` and zero cutoff within floating-point precision. Do not impose a universal `1e-5` finite-difference derivative threshold on an independently linearly interpolated force and energy table: their derivatives need not agree exactly between nodes. A 5,000-point table is a starting choice, not a guarantee; adapt table resolution/range until validated, otherwise use native SFLJ. Detect unsupported styles and gracefully choose the verified NumPy implementation.

   - **Cross-engine validation:** Match epsilon, sigma, mass, dimensionality, cutoffs, nonperiodic boundaries, minimization, grip kinematics, thermalization, sampling frequency, and strain-rate units. Distinguish per-step displacement from physical time derivative. LAMMPS and NumPy thermostat PRNGs need not yield identical trajectories for equal integer seeds. Compare deterministic two-body forces/energies first, followed by ensemble distributions (means with uncertainty intervals) for peak stress, fracture/censoring rate, and crack-region agreement. `15%` is a target tolerance for adequately powered comparisons, not grounds to fabricate agreement. If LAMMPS unavailable, mark comparison `NOT_RUN`, not `PASS`.

   - **Runtime calibration:** Benchmark actual 2D SFLJ step cost (minimization + equilibration + driven loading + logging) on the host CPU. Start with 12×12 or 16×16 lattices, then select a physically meaningful loading horizon and sample cadence. Target 3–12 seconds per replicate when feasible; do not shorten trajectories so much that failure/censoring is unobservable. Record calibrated parameters, full simulation duration, and whether the time target was achievable. Enforce per-run and investigation budgets via terminable worker processes.

4. **Verified Meta Muse Spark Integration & Explicit Telemetry:**
   - Implement a startup verification probe (`verify_llm_connection()` in `backend/agents/muse_agent.py`) that checks `META_MUSE_BASE_URL`, `META_MUSE_API_KEY`, and `META_MUSE_MODEL`, tests structured JSON response support, and records the connection state.

   - Every hypothesis, experiment proposal, investigation, and UI header must expose the actual `ai_execution_mode` through its schema/telemetry. `LIVE_MUSE_SPARK_API` requires successful structured inference **during the relevant operation**, not just a startup probe. Record model, API host, latency, response/usage telemetry where available, and per-action provenance. Fall back visibly and deterministically on failure. Do not claim live Meta usage when operating in fallback mode; live model integration is a demonstration acceptance requirement when hackathon judging expects model use.
     - `"LIVE_MUSE_SPARK_API"` (verified live model response with latency and token usage logged)

     - `"OFFLINE_HEURISTIC_FALLBACK"` (clearly flagged deterministic fallback when API credentials are absent or unreachable)

5. **Zero Unconstrained Execution from LLM:**
   - The AI scientist agent may ONLY emit structured JSON matching `backend/models/schemas.py` and invoke registered deterministic Python tools. Never execute raw shell commands or arbitrary Python code generated by the LLM.

6. **Empirical Honesty Over Forced Benchmark Verdicts (`Zero Hardcoded Outcomes`):**
   - Target findings for `CASE_ALPHA` through `CASE_DELTA` are **empirical physical hypotheses, NOT forced rules**.

   - Neither `evidence_verifier.py` nor `muse_agent.py` may branch on `case_id`, temperature, or intervention name to force a `SUPPORTED` or `INCONCLUSIVE` verdict. If simulated evidence contradicts an expected diagnosis or fails the SNR/CV gates, the system MUST return the actual evidence-supported verdict or `INCONCLUSIVE`.

---

## 1. System Architecture & Scientific Loop

NanoForensics transforms molecular dynamics from passive simulation execution into active **counterfactual root-cause investigation**.

```text

[Stage 1: Observe]      Load blind failure case (CASE_ALPHA..DELTA: Stress-Strain + Trajectory, NO causal label)

        │

        ▼

[Stage 2: Hypothesize]  Meta Muse Spark (or flagged fallback) proposes competing physical hypotheses

        │

        ▼

[Stage 3: Plan]         Rank candidate interventions via Utility = Distinguishability - 0.3*(Cost) - Risk

        │

        ▼

[Stage 4: Experiment]   Run matched-seed replicate counterfactual MD simulations (LAMMPS / Vectorized NumPy 2D-SFLJ)

        │

        ▼

[Stage 5: Verify]       Independent verifier checks bond-loss fracture criterion, Langevin stability, & seed SNR

        │

        ▼

[Stage 6: Conclude]     Empirically mark hypotheses SUPPORTED / REJECTED / INCONCLUSIVE & generate auditable report

```

---

## 2. Target Repository Structure

Create and populate this exact file tree:

```text

NanoForensics/

├── AGENTS.md

├── README.md

├── .gitignore

├── requirements.txt

├── Makefile

├── .env.example

├── docs/

│   ├── IMPLEMENTATION_PLAN.md         # Phase-by-phase task checklist & acceptance criteria

│   ├── PROJECT_STATE.md               # Completed, active, and pending tasks (updated every unit)

│   ├── HANDOFF.md                     # Cross-agent resume notes (Codex <-> Antigravity)

│   └── TEST_RESULTS.md                # Executed gate commands, pass/fail counts, & E2E logs

├── scripts/

│   └── verify_e2e.sh                  # Phase 5 full-stack boot & end-to-end verification script

├── backend/

│   ├── __init__.py

│   ├── main.py                        # FastAPI app, CORS, startup calibration & LLM check

│   ├── config.py                      # Env config, compute budget (1800s), timeouts, LLM endpoints

│   ├── models/

│   │   ├── __init__.py

│   │   └── schemas.py                 # Pydantic v2 data contracts (Single Source of Truth)

│   ├── api/

│   │   ├── __init__.py

│   │   └── routes.py                  # REST endpoints with per-case lock guard & progress status

│   ├── agents/

│   │   ├── __init__.py

│   │   ├── muse_agent.py              # Meta Muse Spark client, health probe & flagged fallback

│   │   ├── hypothesis_engine.py       # Structured hypothesis generation & updating

│   │   └── experiment_planner.py      # Budget-aware utility scoring & selection

│   ├── simulation/

│   │   ├── __init__.py

│   │   ├── defect_generator.py        # 2D hex lattice generator + coordinate-based defect ops

│   │   ├── lammps_runner.py           # LAMMPS binary wrapper + verified SFLJ table generator

│   │   ├── numpy_md_fallback.py       # Vectorized NumPy 2D Shifted-Force LJ Velocity-Verlet engine

│   │   ├── experiment_validator.py    # Separate NVE conservation check + Langevin stability checks

│   │   └── input_templates/

│   │       └── tensile_2d_lj.in.j2    # Jinja2 template for LAMMPS 2D SFLJ tensile test

│   ├── analysis/

│   │   ├── __init__.py

│   │   ├── stress_strain.py           # Virial stress, reference-relative fracture criterion, toughness

│   │   ├── structure_analysis.py      # Reference neighbor graph, bond loss ΔZ_i & crack localization

│   │   ├── comparison.py              # Matched-seed & replicate delta statistics

│   │   └── evidence_verifier.py       # Empirical statistical + physical verification rules

│   └── storage/

│       ├── __init__.py

│       └── db.py                      # SQLite investigation state & reproducibility store

├── benchmarks/

│   ├── __init__.py

│   ├── calibrate_runtime.py           # Benchmarks host CPU & tunes lattice/step parameters

│   ├── generate_cases.py              # Runs physics engine to build CASE_ALPHA..DELTA + ground_truth.json

│   ├── fixed_checklist.py             # Baseline A: Naive fixed-order experiment runner

│   ├── oneshot_baseline.py            # Baseline B: One-shot model without counterfactual experiments

│   └── evaluate.py                    # Evaluates baselines vs NanoForensics & outputs Markdown report

├── frontend/                          # Next.js 14+ (App Router, TypeScript, Tailwind, Plotly)

│   ├── package.json

│   ├── tsconfig.json

│   ├── tailwind.config.ts

│   ├── next.config.mjs

│   └── src/

│       ├── app/

│       │   ├── layout.tsx

│       │   ├── globals.css

│       │   └── page.tsx               # 6-Screen Interactive Investigation Dashboard

│       ├── components/

│       │   ├── HeaderBar.tsx          # Shows Physics Engine + Live vs Fallback AI Telemetry

│       │   ├── LatticeCanvas.tsx      # Interactive 2D atomistic viewer colored by Z_i and bond loss ΔZ_i

│       │   ├── StressStrainPlot.tsx   # Baseline vs Counterfactual replicate envelope chart

│       │   ├── HypothesisPanel.tsx    # Competing hypotheses & predictions

│       │   ├── PlannerPanel.tsx       # Counterfactual utility table & execution controls

│       │   └── AuditReportModal.tsx   # Reproducible scientific verdict & trace log

│       └── lib/

│           └── api.ts                 # Typed API client with timeout & polling support

└── tests/

    ├── __init__.py

    ├── test_physics_and_defects.py    # SFLJ table/derivative test, NVE energy conservation, & defects

    ├── test_verifier.py               # Tests driven stability, reference-relative fracture, & blind IDs

    ├── test_investigation_loop.py     # Blind autonomous loop & empirical verdict honesty tests

    └── test_e2e_fullstack.py          # Live HTTP backend + Next.js frontend integration tests

```

---

## 3. Exact Data Contracts (`backend/models/schemas.py`)

Implement the following Pydantic v2 baseline contracts before business logic. Apply the mandatory extensions immediately below; the written fields are not an excuse to omit execution status, provenance, or censored-result representation:

```python

from enum import Enum

from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field

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

    outcome: str = "FRACTURED"  # FRACTURED, NOT_FRACTURED_WITHIN_HORIZON, EXECUTION_FAILED

    max_observed_strain: float = 0.0

    protocol_hash: str = ""

    initial_configuration_hash: str = ""

    numerical_check: NumericalConsistencyCheck

    wall_time_sec: float

    engine_used: str                             # "LAMMPS_BINARY" or "NUMPY_VELOCITY_VERLET_2D"

class Hypothesis(BaseModel):

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

    generated_by: AIExecutionMode = AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK

    ai_execution_mode: AIExecutionMode = AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK

class ExperimentProposal(BaseModel):

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

    scientific_explanation: str

class FailureCasePublic(BaseModel):

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

```

---

### 3.1 Mandatory extensions to the baseline contracts

- Add `SimulationOutcome` with `FRACTURED`, `NOT_FRACTURED_WITHIN_HORIZON`, `EXECUTION_FAILED`. `failure_strain: Optional[float]` and fracture snapshots already support censored runs; the simulation must record `max_observed_strain`, measurement horizon and outcome. A failed run must retain an error code/message and be excluded from valid statistical comparison.
- Populate `ai_execution_mode` consistently on `Hypothesis`, `ExperimentProposal`, and `InvestigationState`. Keep `generated_by` as backward-compatible alias if useful, but never let conflicting values coexist. Include execution provenance on every AI action.
- Add per-run `protocol_hash`, `initial_configuration_hash`, physical units (`lj_reduced_2d`), solver version, strain-rate convention, area/thickness convention, effective gauge length and reference geometry. `SimulationSummary` must expose replicate-level results; aggregate means without raw seeds are not auditable.
- Include optional token counts in `LLMTelemetry` only when furnished by the provider. Do not invent usage fields.
- Define API payloads explicitly, including an experiment body containing a validated `proposal_id` or allowlisted `InterventionType` and typed parameters. Use immutable reference ids for baseline and counterfactual results.
- Keep `VerificationResult` outcome status distinct from scientific verdict; a numerical failure is not an `INCONCLUSIVE` hypothesis verdict. Add confidence intervals or explicitly label low-sample statistics descriptive.
- Do not serialize physical ground-truth records inside public schemas, hidden fields, agent tools or frontend bundles.

---

## 4. Genuine Atomistic Physics & Blind Benchmark Specification

### 4.1 First-Principles 2D Shifted-Force Lennard-Jones Mechanics (`numpy_md_fallback.py` & `lammps_runner.py`)

Both the vectorized NumPy integrator and the LAMMPS runner MUST implement the exact **Shifted-Force 12-6 Lennard-Jones (SFLJ)** potential:

$$U_{\text{LJ}}(r) = 4\varepsilon \left[ \left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6 \right], \qquad F_{\text{LJ}}(r) = -\frac{dU_{\text{LJ}}}{dr} = \frac{24\varepsilon}{r} \left[ 2\left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6 \right]$$

$$U_{\text{SFLJ}}(r) = \begin{cases} U_{\text{LJ}}(r) - U_{\text{LJ}}(r_c) - (r - r_c)\left.\dfrac{dU_{\text{LJ}}}{dr}\right|_{r=r_c} & r < r_c = 2.5\sigma \\ 0 & r \ge r_c \end{cases}$$

$$\mathbf{F}_{ij}^{\text{SFLJ}}(\mathbf{r}_{ij}) = \begin{cases} \left[ F_{\text{LJ}}(r_{ij}) - F_{\text{LJ}}(r_c) \right] \dfrac{\mathbf{r}_{ij}}{r_{ij}} & r_{ij} < r_c = 2.5\sigma \\ \mathbf{0} & r_{ij} \ge r_c \end{cases}$$

1. **Verified solver and (optional) table equivalence (`lammps_runner.py`):**
   - Prefer a verified installed `lj/smooth/linear` style. If using tabulation, generate a finite, monotonic radial grid with analytically consistent energy and force; choose the lower tabulation radius from the valid, actually sampled interaction domain rather than blindly demanding force accuracy near the singular repulsive core. Test values at independent off-grid radii and verify native LAMMPS `pair_write` output. Report maximum absolute and scale-normalized errors over `[r_min_valid, 2.5 sigma]`, with `r_min_valid >= 0.85 sigma` only if trajectories actually remain in that range. Handle closer approaches as invalid states or refine the table as required. Use separate numerical derivative checks for the analytic potential and realized interpolant; never equate piecewise-linear force interpolation with the exact derivative of piecewise-linear energy.

   - Assert analytic SFLJ cutoff `U(2.5 sigma) = F(2.5 sigma) = 0`; check near-cutoff convergence. Ensure potential and force conventions, table headers and LAMMPS units agree. Fail closed if any nonfinite forces, unsupported pair style, invalid tabulation, or uncaught LAMMPS error occurs.

   - In NumPy compute pairwise displacements with broadcasting, diagonal masking, safe inverse distances and Newton-third-law force symmetry; retain a separate O(N^2) reference test on arbitrary unindexed coordinates and non-overlap configurations. Do not use O(N^2) pairwise Python loops in the production inner step.

   - **Do NOT use plain `pair_style lj/cut 2.5`** in LAMMPS. A validated `generate_and_verify_sflj_table(...)` remains required as a testable optional fallback, but it must return measured off-grid errors and reject inadequate tabulations.

2. **Boundary, equilibration, NVE and grip protocol:**
   - **A: Relax:** Minimize using FIRE or a validated damping method; verify force convergence, record residual forces and fail if unstable rather than assuming 150 iterations suffice.
   - **B: Thermalize:** Use a documented consistent Langevin integrator (e.g., BAOAB or velocity-Verlet with documented stochastic splitting), independent `PCG64(seed)` streams, target temperature, and mobile non-grip degrees of freedom. Calibrate warmup length by measured relaxation; 150 steps is a baseline only.
   - **C: NVE verification:** Restore frozen grip boundary conditions, run 50 unstrained, no-thermostat steps, compute **total energy drift** over the full window and record max/terminal drift. NVE must exclude external work and thermostat. Take reference coordinates and reference neighbor sets **after** NVE and before loading; 500-step NVE unit test uses the same energy definition.
   - **D: Driven loading:** Use free boundaries in x, frozen/prescribed top and bottom grips, mobile central atoms, and one explicit definition of engineering strain `epsilon=(L_grip(t)-L_grip(0))/L_grip(0)` and of strain-rate **per unit physical time**. If nominal rate is defined per timestep, convert using `dt`. Apply equal/opposite grip motion, compute displacement from gauge length, exclude grips from thermostat, and document heat/work exchange. Set a loading horizon sufficient to observe fracture or return a censored run.
   - **Isolation:** Every run receives a serialized configuration/protocol object (coordinates, site IDs, interventions, seed, temperature, rate); simulation functions may not inspect case IDs or hidden labels. Two identical serialized inputs must produce statistically reproducible outputs on the same engine/version.

3. **Virial stress definition and 2D normalization:**
   - Compute the kinetic and configurational virial from non-grip atoms, consistently including half of each interaction for per-atom contributions and avoiding double counting. Choose a stated effective **2D area** or line-tension normalization (nominal width × gauge length, and assumed unit thickness if reporting a 3D-equivalent stress). Record area/volume changes and whether using Cauchy or nominal stress. Stress sign must be validated using a two-particle tensile configuration and an elastic lattice test. All plotted values use the same sign/normalization; do not use arbitrary rescaling to manufacture a load drop.

   - Report $\sigma_{yy} = [\sum_{i \in M} m_i v_{i,y}^{2} + \frac12\sum_{i \in M}\sum_{j\ne i} (y_i-y_j)F_{ij,y}]/A_{eff}$ under an explicitly fixed sign convention, where `M` denotes mobile atoms. Compare the virial force response with grip reaction traction as a cross-check; if they disagree systematically, investigate boundary/normalization problems before reporting fracture.

4. **Reference-relative persistent fracture, retrospective detection and censoring:**
   - Define initial neighbors at the post-equilibration reference using cutoff `1.35 r0`; record reference coordination `Z0`. Define current-neighbor loss and **severed reference bonds separately**; compute severed bonds from the original reference pair list crossing `1.65 sigma`, not simply from current coordination. Active rupture requires at least two severed reference bonds, positive net coordination loss, and current `Z<=4`. Keep grip atoms out of candidate clusters.
   - Connect actively ruptured atoms using a documented reference-adjacency graph (not all spatially close atoms), and track overlapping/connected cluster identities through at least three consecutive measurements. A transient single-frame cluster is not fracture.
   - Smooth a fully recorded stress curve using a fixed, disclosed method; find the **global** peak retrospectively after the loading horizon. Fracture occurs at the earliest post-peak measurement at which `stress <= 0.65*positive_peak_stress` and a spatially overlapping cluster of >=4 ruptured atoms persists for 3 consecutive measurement windows. Require a positive, physically meaningful peak; otherwise mark invalid/undetermined. State whether fracture strain is assigned at first qualifying frame or third confirmation frame (use first qualifying frame, confirmed retrospectively).
   - If the horizon ends before persistent rupture or load drop, return `NOT_FRACTURED_WITHIN_HORIZON` with `max_observed_strain` and `failure_strain=null`; never fill failure strain with final strain. If the stress curve is noisy or peak occurs at the final sample, return censored/undetermined rather than inventing a post-peak fracture. Preserve snapshots at initial, peak and fracture when present; otherwise last available frame.
   - Classify crack initiation region using first persistent ruptured cluster centroid in specimen-reference coordinates. If multiple equivalent clusters appear or motion/necking makes localization ambiguous, label `distributed`; do not infer crack cause from `case_id`.

### 4.2 Blind Benchmark Cases (`benchmarks/generate_cases.py`)

**IMPORTANT: The preparation table is developer-only benchmark design information. Never put it in an agent system prompt, LLM request, investigation metadata, or browser payload.\*\***

All cases are generated by running the actual MD engine on initial atomic coordinate arrays. **The table below defines the physical preparation and expected benchmark hypotheses—actual verdicts MUST be determined empirically by `evidence_verifier.py`:**

| Opaque Case ID | Hidden Physical Preparation (Stored ONLY in `ground_truth.json`) | Expected Emergent Physical Behavior (Empirical Hypothesis) | Expected Distinguishing Counterfactual |

| :--------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

| **`CASE_ALPHA`** | **Interior Void:** Remove 3 contiguous central atoms near $(0.5 L_x, 0.5 L_y)$ before equilibration. Nominal strain rate $\dot{\varepsilon}_0$, $T^* = 0.05$. | Stress concentrates around the internal void; reference-relative bond loss $\Delta Z_i$ initiates around the interior vacancy (`crack_initiation_region == "interior"`). | `heal_interior_vacancy` (re-inserts missing lattice sites at local minimum-energy centroids and re-equilibrates with the **exact same random seed**). Increases $\varepsilon_f$ relative to `smooth_surface_notch`. |

| **`CASE_BETA`** | **Surface Notch:** Pristine interior, but 2 adjacent edge atoms removed on the left free surface $(x \approx 0, y \approx 0.5 L_y)$. Nominal strain rate $\dot{\varepsilon}_0$, $T^* = 0.05$. | Macroscopic failure strain and peak stress are close to `CASE_ALPHA`, creating an **initial macroscopic ambiguity**. However, active bond loss ($B_i^{\text{broken}} \ge 2$) initiates at `"surface_left"`. | `smooth_surface_notch` restores left-edge lattice sites and increases $\varepsilon_f$, whereas `heal_interior_vacancy` yields negligible change. |

| **`CASE_GAMMA`** | **Loading-Rate Artifact:** Defect-free lattice ($Z^{(0)}=6$ across all bulk atoms), but loaded at $4\times$ higher strain rate ($\dot{\varepsilon} = 4\dot{\varepsilon}_0$). | Elevated inertial peak stress followed by shear localization despite zero initial structural defects. | `normalize_strain_rate` ($\dot{\varepsilon} \to \dot{\varepsilon}_0$) eliminates inertial stress overshoot and restores baseline ductility. |

| **`CASE_DELTA`** | **High-Temperature Stochastic Necking:** Elevated thermal energy ($T^* = 0.38$) where thermal velocity fluctuations drive stochastic bond rupture. | Replicate runs across seeds (`seed = 101, 202, 303`) exhibit elevated variance in $\varepsilon_f$ and shifting initiation sites. | `repeat_replicate_seeds` measures intrinsic thermal seed-to-seed variance; when replicate $\text{CV} > 12\%$ or $\text{SNR} < 2.5$, the verifier empirically outputs **`INCONCLUSIVE`**. |

---

### 4.3 Blind counterfactual execution contract (mandatory)

The benchmark generator may privately know the preparation but the investigator cannot. Persist an **opaque immutable specimen input** (visible coordinates, atom ids, simulation control observables, reference sites only if inferable from public geometry) in the benchmark database. Hidden `ground_truth.json` must never be needed to execute an investigator-chosen intervention. Interventions must be geometric algorithms applied to observable coordinates:

- `heal_interior_vacancy`: infer candidate interior missing hexagonal sites from local geometric neighbor topology and lattice fit; insert only sites supported by measured void geometry, then relax.
- `smooth_surface_notch`: infer edge gaps from surface geometry, reconstruct candidate edge sites and relax.
- `normalize_strain_rate` and `normalize_temperature`: modify explicit physical protocol parameters, **not** secret case labels; values can be proposed from a public reference protocol. The model must not be told which normalization is correct.
- `repeat_replicate_seeds`: rerun an unchanged physical configuration with new seeds; it is a diagnostic replicate, **not a repair**, and must not be scored as mechanical recovery.

Validation rejects transformations with no detectable geometric target as `NO_APPLICABLE_EDIT` and records the no-op rather than making an imaginary repair. The full intervention trace includes inferred locations, inserted/removed atom ids, input/output configuration hashes, and relaxation convergence. Independently verify that identical configuration/protocol inputs produce identical initial conditions for matched seeds. Evaluation alone may compare the inferred repair against hidden preparation truth after verdicts are fixed.

**Blindness test:** Dynamically deny `ground_truth.json` reads to every module reachable by live endpoints (including helpers), mask sensitive case metadata and filenames, and verify that permuting opaque case identifiers does not change simulation results or the inference algorithm on identical inputs. Inspect model prompts and API JSON for label leakage.

---

## 5. Rigorous Scientific Verification Controls (`backend/analysis/evidence_verifier.py`)

Implement a universal, case-agnostic 4-stage verification pipeline:

1. **Gate 1 — Numeric/physical execution validity:** The 50-step and 500-step pre-load NVE energy drift must be less than `1e-3` with sensible denominator floor and no external work; report raw drift and units. Driven loading must have finite forces/positions, bounded step displacement, and measured temperature stability with thermostat reporting restricted to mobile particles. The proposed safeguards (`max_force_norm<1e4`, max step displacement `<0.10`, temperature-error ratio `<0.35`) are initial operating bounds; test and document their dimensional meaning. A valid run without fracture passes numerical validation but is _right-censored_. Any severe numerical failure makes the experiment `EXECUTION_FAILED` and prohibits a scientific verdict from that run.

2. **Gate 2 — Matched-seed execution:** Use primary seed 42 and replicates 137 and 271 for both baseline and intervention; baseline replicates must actually run, not copy seed-42 statistics. Use identical stochastic stream conventions and physically equivalent starting states except the intervention. Cache runs by content-addressed inputs, engine version, and seed. Three pairs yield descriptive effect estimates, not strong population-level statistical confidence; disclose uncertainty and expand seeds when effects are close to thresholds.

3. **Gate 3 — Paired effect size and uncertainty:** Compare matched-seed deltas per pair, not solely independent pooled standard deviations. Report mean paired failure-strain shift, recovery percentage, paired difference standard deviation, bootstrapped confidence interval when sample size permits, and noise-floor-stabilized SNR. The specified unpaired pooled SNR may be shown as an additional reproducibility metric but must not substitute for paired evidence. If some runs are censored, report censoring counts and do not compute a naive failure-strain mean or claim recovery. Compare peak stress separately under consistent normalization.
   - Compute mean failure strain shift $\Delta \bar{\varepsilon}_f = \bar{\varepsilon}_{f,\text{cf}} - \bar{\varepsilon}_{f,\text{base}}$, relative recovery $R_{\varepsilon} = (\Delta \bar{\varepsilon}_f / \bar{\varepsilon}_{f,\text{base}}) \times 100\%$, and Signal-to-Noise Ratio:

     $$\text{SNR} = \frac{|\Delta \bar{\varepsilon}_f|}{\sqrt{\sigma_{\varepsilon,\text{base}}^2 + \sigma_{\varepsilon,\text{cf}}^2 + \epsilon_{\text{floor}}^2}} \quad (\epsilon_{\text{floor}} = 0.004)$$

4. **Gate 4 — Case-agnostic empirical verdict:** Apply thresholds only to complete, numerically valid, comparable matched-seed outcomes. `SUPPORTED`: CV<=12% and either paired SNR>=2.5 with recovery>=18%, or rate-normalization peak-stress reduction>=12% with stress SNR>=2.5 and non-decreasing uncensored failure strain. `REJECTED`: CV<=12%, paired SNR<1.2 and absolute recovery<8% **when the hypothesis predicts increased failure strain**, and no unmodeled competing effect. All other valid comparable observations are `INCONCLUSIVE`, including effects below a support threshold that do not meet rejection criteria. `EXECUTION_FAILED`, `NO_APPLICABLE_EDIT`, insufficient uncensored pairs, or exceeded budget are **execution/data availability statuses**; do not convert them into experimental evidence for/against a hypothesis. A budget-limited investigation may have final `INCONCLUSIVE` scientific summary with audit log explaining absent evidence.
   - `normalize_strain_rate` is the only predeclared intervention-specific stress criterion; no case-specific branching is allowed. Report the strain-rate definition and avoid asserting that lower peak stress proves restored ductility without matched mechanical evidence. If its effect is opposite to predictions, preserve the observed sign.
   - `repeat_replicate_seeds` quantifies variance only; assign scientific support/rejection only to a causal hypothesis with an actual physically manipulated intervention. High variance can legitimately motivate `INCONCLUSIVE`.

   - **Strict honesty:** No forced verdicts by case ID or expected preparation. `INCONCLUSIVE` covers valid but underpowered/ambiguous evidence; invalid numerics are `EXECUTION_FAILED`; physically valid right-censored runs are `NOT_FRACTURED_WITHIN_HORIZON` and must not be assigned an invented failure strain. All thresholds apply to actual measured data, not benchmark wishes.

---

## 6. Agent Tool Design & Meta Muse Spark Verification (`backend/agents/`)

1. Implement `verify_llm_connection() -> LLMTelemetry` in `muse_agent.py`:
   - If `META_MUSE_API_KEY` is missing/empty, immediately return `AIExecutionMode.OFFLINE_HEURISTIC_FALLBACK` with `last_error="META_MUSE_API_KEY not configured"`.

   - If present, send a lightweight structured health check prompt (`max_tokens=32`, timeout `8.0s`). Record latency in `LLMTelemetry.last_call_latency_ms` on success, or catch errors gracefully and fall back to `OFFLINE_HEURISTIC_FALLBACK`.

2. **Registered Deterministic Tools (`NanoForensicsInvestigator`):**
   - `inspect_case(case_id: str) -> dict`

   - `get_structural_evidence(case_id: str, region: str, measurement: str) -> dict`

   - `list_experiments(case_id: str) -> list[dict]`

   - `propose_experiment(case_id: str, experiment_type: str, parameters: dict, rationale: str) -> ExperimentProposal`

   - `validate_experiment(experiment_id: str) -> dict`

   - `run_lammps(experiment_id: str) -> SimulationSummary`

   - `compare_outcomes(baseline_id: str, experiment_id: str) -> dict`

   - `evaluate_hypotheses(case_id: str) -> list[Hypothesis]`

   - `generate_report(case_id: str) -> InvestigationState`

---

### 6.1 Genuine autonomous decision-making acceptance

The live model must ingest **only visible** stress curves, atomic trajectory features, protocol metadata permitted to the observer, and completed experimental evidence. It produces at least two competing, testable hypotheses and discriminating predictions, ranks candidate interventions based on expected information gain/cost/risk, and after results revises confidence/status or proposes a follow-up. Preserve request/response hashes and parsed JSON, never credentials. The deterministic fallback uses the same allowlisted tools but is labeled clearly and evaluated separately; it cannot be counted as a live-model victory. The UI should show what changed the model's decision, not just a narrative summary. Reject invalid JSON and hallucinated tool names, and require explicit bounded schemas and retries.

---

## 7. Backend FastAPI Specification, Timeouts & Concurrency (`backend/api/routes.py`)

Run on port `8000` with CORS enabled for `http://localhost:3000` and `http://127.0.0.1:3000`:

- **Concurrency, durable jobs and timeout guardrails:**
  - Keep per-case locks _and_ SQLite transaction-backed job uniqueness/state, so duplicate requests across multiple FastAPI workers/restarts receive `409` when an active job exists. `reset` and `hypothesize` must also be protected from colliding with live investigation work. Return accepted job IDs with `202` for asynchronous long-running operations, and expose `GET /api/jobs/{job_id}`; use `GET /api/cases/{case_id}` to poll persisted progress.
  - Spawn CPU-heavy simulation replicates as isolated worker subprocesses/process-pool tasks with bounded concurrency and bounded resource usage, not as work on the FastAPI event loop. A per-run `30 s` budget and job `120 s` budget must terminate/reap underlying worker processes or isolate and mark them failed, not just cancel an awaiting coroutine. Include cancellation, cleanup of temporary files, and post-crash recovery of orphaned jobs. Store progress, error messages, and actual timing in SQLite; clear locks/state using `finally` and durable transactions.
  - Configure per-run timeouts according to calibration if the default `30 s` is physically impossible, while preserving overall `1800 s` budget and labeling runs that cannot meet demo-time limits. HTTP requests should return immediately and remain responsive during polling.

- **Endpoints:**
  - `GET /api/health` -> Returns engine mode, calibrated atom count, `ai_telemetry`, and budget limit.

  - `GET /api/cases` -> Lists `CASE_ALPHA`, `CASE_BETA`, `CASE_GAMMA`, `CASE_DELTA` (`FailureCasePublic`).

  - `GET /api/cases/{case_id}` -> Returns `FailureCasePublic` + current `InvestigationState` (including `is_running` and `current_step_message`).

  - `POST /api/cases/{case_id}/reset` -> Resets case state.

  - `POST /api/cases/{case_id}/hypothesize` -> Runs Stage 1 & 2.

  - `POST /api/cases/{case_id}/experiment` -> Executes Stage 3, 4 & 5 with matched-seed replicates.

  - `POST /api/cases/{case_id}/auto-investigate` -> Enqueues the closed-loop autonomous investigation, returns `202` and `job_id`; progress available through job/case GET endpoints.

  - `POST /api/benchmarks/evaluate` -> Enqueues evaluation of `Baseline A`, `Baseline B`, and `NanoForensics` across cases (admin/dev only, rate-limited); returns job ID.

- `GET /api/jobs/{job_id}` -> Durable job status, progress, and final result/error.
- `POST /api/jobs/{job_id}/cancel` -> Requests real worker termination and records cancellation.

---

### 7.1 Honest benchmark comparison contract

Blind cases are generated once and held fixed **before** investigator or baseline runs. Allow no tuning on held-out case labels after viewing benchmark outcomes. Fixed-checklist, one-shot and NanoForensics receive equivalent public observations and measurement access; disclose differences in experiment budget and model-call budget. Run baselines on the same material solver and seeds wherever comparison is possible, report raw outcomes and wall time, and publish a clearly named `NO_DECISION` / `INCONCLUSIVE` count alongside correct/incorrect diagnosis. The fixed checklist should not be denied geometry or labels that NanoForensics can access; one-shot may have zero interventions **by definition**, but show that as an experimental-budget difference. Avoid claims of superiority from four cases without uncertainty and repeated trials.

---

## 8. Frontend 6-Screen Interactive Experience (`frontend/src/app/page.tsx`)

Build a dark-mode scientific workbench (`bg-slate-950 text-slate-100`) with transparent telemetry and resilient async UX:

1. **Top Status & Honesty Telemetry Bar (`HeaderBar.tsx`):**
   - **Physics Engine Badge:** Shows `LAMMPS C++ Binary (SFLJ)` (emerald) or `NumPy 2D-SFLJ Velocity-Verlet` (cyan).

   - **AI Mode Badge:** Distinguishes **`🟢 LIVE: Meta Muse Spark API (latency ms)`** from **`🟠 OFFLINE FALLBACK: Deterministic Scientific Heuristics (No API Key)`**.

   - **Compute Budget Meter:** Displays wall-clock seconds consumed out of `1800s`.

2. **Blind Case Selector:** Displays `CASE_ALPHA..DELTA` without spoiling the hidden defect until concluded.

3. **Interactive 2D Atomic Structure Viewer (`LatticeCanvas.tsx`):** Renders real atomic $(x, y)$ coordinates from `AtomSnapshot` with toggleable coloring: coordination $Z_i$, reference-relative **bond loss $\Delta Z_i$**, and per-atom virial stress.

4. **Stress-Strain Replicate Comparison Chart (`StressStrainPlot.tsx`):** Plots baseline vs. counterfactual virial stress-strain curves with replicate uncertainty bands ($\pm 1\sigma$) and fracture markers.

5. **Hypothesis & Counterfactual Planner Cards (`HypothesisPanel.tsx` & `PlannerPanel.tsx`):** Disables action buttons while `is_running` is true, polls `GET /api/cases/{case_id}` every `1000ms` during active simulations to display `current_step_message`, and surfaces clear error banners on timeouts.

6. **Scientific Verdict & Reproducibility Audit Modal (`AuditReportModal.tsx`):** Shows `VerificationResult` metrics ($\Delta \bar{\varepsilon}_f$, $\text{SNR}$, replicate CV, NVE energy drift & Langevin stability check, seeds, and full tool trace).

---

### 8.1 Demo-first resilience and terminology

Clearly label the system a **2D reduced-unit Lennard-Jones computational testbed**, not validated nanoscale fracture prediction for a real engineering material. Add explanations of reduced units, small-size/time-scale limitations and empirical verdict conditions. The dashboard must display `NO_FRACTURE_OBSERVED`/censored and `EXECUTION_FAILED` states distinctly. Live model and fallback modes must never be visually conflated. A persistent audit-trace timeline should show observation -> hypotheses -> intervention -> simulation -> verification -> belief revision with real timestamps. A precomputed but genuinely simulated, immutable demo case may be loaded for fast initial rendering; interactive investigation must still execute real simulations when requested, with an explicit tag distinguishing cached data from freshly computed data.

---

## 9. Phased Execution Plan & Mandatory Acceptance Gates

Execute these phases in order. After each phase, update `docs/PROJECT_STATE.md`, `docs/TEST_RESULTS.md`, and `docs/HANDOFF.md`, and create a Git commit checkpoint. Do not advance until the gate command passes.

### Phase 1 — Calibrated SFLJ Physics Engine, NVE Conservation & Reference-Relative Fracture Tests

1. Create `.gitignore`, `requirements.txt`, `docs/IMPLEMENTATION_PLAN.md`, `docs/PROJECT_STATE.md`, `docs/HANDOFF.md`, and `docs/TEST_RESULTS.md`.

2. Implement `backend/config.py`, `backend/models/schemas.py`, `backend/simulation/*`, `backend/analysis/*`, and `benchmarks/calibrate_runtime.py`.

3. Write `tests/test_physics_and_defects.py` and `tests/test_verifier.py` verifying:
   - **Test 1 (SFLJ Analytical Derivative & LAMMPS Table Consistency Test):** Verify analytical SFLJ force derivatives on perturbed atom coordinates, verify $U(r_c)=F(r_c)=0$, and verify analytic SFLJ derivatives, off-grid table interpolation using measured absolute/relative tolerances and, when LAMMPS is available, the actual interpolated pair forces/energies. If LAMMPS is unavailable, mark its integration tests skipped with a reason.

   - **Test 2 (Microcanonical NVE Energy Conservation Test):** Run a 500-step unstrained, unthermostatted NVE simulation ($\dot{\varepsilon}_y = 0, \gamma = 0$) and verify $|\Delta E_{\text{tot}}| / |E_{\text{tot}}(0)| < 10^{-3}$.

   - **Test 3 (Driven Langevin Stability & Surface-Safe Persistent Fracture Test):** Verify free-surface and notch atoms at $\varepsilon = 0$ are not falsely flagged as fractured prior to reference bond loss ($\Delta Z_i \ge 1, B_i^{\text{broken}} \ge 2$), verify transient 1-frame bond stretches are ignored, and verify geometry-based healing modifies forces and strain response on a controlled specimen without requiring a fixed improvement or SNR. The measured effect and SNR must be reported honestly.

- **Phase 1 Gate Command:**

  ```bash

  pytest tests/test_physics_and_defects.py tests/test_verifier.py -v

  ```

### Phase 2 — Blind Benchmark Generation, SQLite Store & Empirical Agent Loop

1. Implement `backend/storage/db.py` and `benchmarks/generate_cases.py` (generating `CASE_ALPHA..DELTA` from real MD runs and isolating `benchmarks/ground_truth.json`).

2. Implement `backend/agents/muse_agent.py`, `backend/agents/hypothesis_engine.py`, and `backend/agents/experiment_planner.py`.

3. Write `tests/test_investigation_loop.py` verifying zero reads of `ground_truth.json` in `backend/`, universal empirical verdict honesty in `evidence_verifier.py` (no hardcoded `case_id` outcomes), and full autonomous loop execution across `CASE_ALPHA..DELTA`.

- **Phase 2 Gate Command:**

  ```bash

  pytest tests/test_investigation_loop.py -v

  ```

### Phase 3 — FastAPI Server, Concurrency Locks & Baseline Comparison Harness

1. Implement `backend/api/routes.py` (including per-case locks and progress messages) and `backend/main.py`.

2. Implement `benchmarks/fixed_checklist.py`, `benchmarks/oneshot_baseline.py`, and `benchmarks/evaluate.py`.

- **Phase 3 Gate Command:**

  ```bash

  python -m benchmarks.evaluate

  ```

### Phase 4 — Next.js 6-Screen Scientific Dashboard

1. Scaffold `frontend/` and implement all 6 components plus `src/lib/api.ts` with timeout and polling support.

2. Create root `Makefile` and `README.md`.

- **Phase 4 Gate Command:**

  ```bash

  cd frontend && npm install && npm run build

  ```

### Phase 5 — Mandatory Full-Stack End-to-End Acceptance Gate

1. Implement `scripts/verify_e2e.sh` and `tests/test_e2e_fullstack.py`:
   - Starts FastAPI (`http://127.0.0.1:8000`) and the compiled Next.js server (`http://127.0.0.1:3000`), waits for both health checks, executes `pytest tests/test_e2e_fullstack.py -v` **while both are running**, and then cleans up every launched process group with shell traps. Never run the E2E suite only after the servers are stopped.

   - Verifies `GET /api/health`, `GET /api/cases`, concurrent duplicate-request `409 Conflict` protection, real worker timeout/cancellation, case metadata blindness, full closed-loop HTTP investigations (submit `POST /api/cases/CASE_ALPHA/auto-investigate` and `POST /api/cases/CASE_DELTA/auto-investigate`; poll durable jobs to terminal status), SQLite state persistence, and `200 OK` dashboard rendering on port `3000`.

2. **Completion Requirement:** You MUST execute the Phase 5 gate command, fix any discovered integration failures, and record the final test output in `docs/TEST_RESULTS.md` before declaring the project complete.

- **Phase 5 Gate Command:**

  ```bash

  bash scripts/verify_e2e.sh

  ```

---

## 10. Agent Continuity & Recovery Protocol (Codex ↔ Antigravity)

This repository must support interruption, restart, context loss, and migration between coding agents (such as OpenAI Codex and Google Antigravity).

### 10.1 Persistent Project Documentation (`docs/`)

Maintain these four files throughout the entire build:

- `docs/IMPLEMENTATION_PLAN.md`: Phase-by-phase task breakdown and acceptance criteria.

- `docs/PROJECT_STATE.md`: Completed (`[x]`), active (`[~]`), and pending (`[ ]`) tasks, plus the latest verified Git commit SHA.

- `docs/HANDOFF.md`: Exact context for the next agent: what was just completed, what is in progress, any blockers or subtle findings, and the exact next commands to run.

- `docs/TEST_RESULTS.md`: Commands run, pass/fail counts, empirical benchmark outputs, and any unresolved failures.

### 10.2 STARTUP

1. Read `AGENTS.md` and all documentation under `docs/`.

2. Inspect `git status`, recent commits (`git log -n 5 --oneline`), and the actual source code.

3. Identify the last verified checkpoint.

4. Resume unfinished tasks without rebuilding completed work.

5. Verify partially implemented features by running their tests before marking them complete.

### 10.3 DURING DEVELOPMENT

1. Work in small, testable units.

2. Update `docs/PROJECT_STATE.md` after each completed unit.

3. Record actual test results and command outputs in `docs/TEST_RESULTS.md`.

4. Maintain `docs/HANDOFF.md` with current progress, blockers, and next steps.

5. Commit verified milestones to Git (`git add -A && git commit -m "checkpoint: phase X - ..."`).

6. Never commit secrets, `.env` credentials, `node_modules/`, `.next/`, or `__pycache__/`.

7. Never discard uncommitted changes without verifying whether they contain in-progress work.

### 10.4 WHEN RESUMING WITH ANOTHER AGENT

1. Read all persistent project documents (`AGENTS.md` and `docs/*`).

2. Inspect the current Git branch and working tree state.

3. Verify reported progress in `docs/PROJECT_STATE.md` against actual files and `pytest` results.

4. Resume from the last verified task.

5. Preserve existing architecture, schemas, and scientific guardrails.

### 10.5 BEFORE STOPPING

1. Update `docs/HANDOFF.md` with the current task, file changes made, latest test results, any blockers, and the exact next commands to run.

2. Update `docs/PROJECT_STATE.md` and `docs/TEST_RESULTS.md`.

3. Stage and commit all verified work so the repository is left in a clean, recoverable state.

### 10.6 COMPLETION & FINAL SIGN-OFF CRITERIA

1. All five phase gate commands (Phase 1 through Phase 5) and full-stack E2E tests (`bash scripts/verify_e2e.sh`) MUST pass.

2. `docs/PROJECT_STATE.md`, `docs/TEST_RESULTS.md`, and `docs/HANDOFF.md` must reflect the final verified state.

3. Report all empirical benchmark outcomes and any remaining environment limitations (such as offline LLM fallback mode or NumPy vs. LAMMPS binary selection) honestly.

---

\<!-- END OF NANOFORENSICS AGENTS.MD SPECIFICATION -->

## 11. Priority and objective evidence policy (Audited v2)

- **Priority P0:** actual measured physics, zero label leakage, truthful model execution provenance, deterministic counterfactual transformations, valid process isolation, functional one-case end-to-end user journey.
- **Priority P1:** all four cases, three matched-seed replicates per condition, benchmark comparator fairness, frontend decision trace and audit exports.
- **Priority P2:** optional LAMMPS cross-engine ensemble comparison and visual polish, conditional on binary availability and sufficient compute.
- Do not waive tests silently: mark each gate `PASS`, `FAIL`, `SKIPPED (with environment reason)`, or `BLOCKED (with blocker)`. A dependency-dependent P2 test may be skipped, but the full application cannot be called complete when P0 or mandatory E2E tests are blocked.
- When unexpected physics undermines an intended demo, fix the actual setup or report that outcome. Never change a scientific acceptance assertion merely to force a desired result. No benchmarks can claim successful discovery unless correctness is assessed separately from the investigator and the label was never visible to the agent.
- `AGENTS.md` must remain the single source of truth; maintain actual code/test status in docs and Git. Record any future amendments as explicit decisions with their empirical justification.
