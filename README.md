# NanoForensics

An auditable counterfactual investigation workbench for a **2D reduced-unit Lennard-Jones computational testbed**. It runs actual atomistic trajectories, proposes competing mechanisms, executes geometric/protocol interventions with matched seeds, and independently checks evidence. Small lattices and short times are educational computational experiments, not validated predictions for a real engineering material.

## Run locally

Requires Python 3.11+ (3.13 recommended), Node 20.9+, npm. An installed `lmp` or `lmp_serial` is detected and its SFLJ pair output verified; otherwise NumPy is selected visibly.

```sh
make setup
cp .env.example .env
make calibrate
make data
make build
make backend
```

In a second terminal:

```sh
make frontend
```

Open http://127.0.0.1:3000. The backend is http://127.0.0.1:8000 with API contracts at `/docs`. The Next.js server proxies `/api` to the backend. For a production-mode local UI: `cd frontend && npm start` after building.

`make setup` uses `python3.13`; substitute an available compatible Python when needed. Dependencies are isolated in `.venv`. Runtime artifacts go under `runtime/`; neither secrets nor generated databases are committed. On a clean machine `make data` generates and freezes all four specimens (three genuine baseline seeds per case); it never silently replaces existing specimens. Delete or select a **new** `NANO_DB` only when intentionally starting a separate benchmark, not to tune held-out outcomes.

## Model connection and honest results

Set `META_MUSE_BASE_URL` (OpenAI-compatible `/v1` base), `META_MUSE_API_KEY`, and `META_MUSE_MODEL` in `.env` to use Meta Muse Spark. No provider URL or model identifier is guessed. Startup probes structured JSON. Every hypothesis/revision operation separately validates its response and records request/response hashes, latency, model/host and provider-supplied usage only. A successful startup probe alone does not prove a live investigation. Without credentials or when an operation fails, the UI and action provenance show `OFFLINE_HEURISTIC_FALLBACK`. This environment has **not** demonstrated live Muse usage; a judging demo requiring live Meta inference still needs working credentials and successful per-action inference.

The current frozen benchmark yields **no unique diagnosis for any of the four cases** across all three methods. Two ALPHA baseline seeds fail the temperature-stability bound; the edge repair does not improve failure strain; rate normalization reduces failure strain; cooling yields uncertain improvement. These outcomes are preserved. See [benchmark report](docs/BENCHMARK_REPORT.md) and [test evidence](docs/TEST_RESULTS.md). No discovery or superiority claim follows from these four cases.

## Physics and verification

The potential is shifted-force 12–6 LJ with cutoff 2.5σ. The vectorized NumPy solver accumulates pair forces and half-pair per-atom virials without Python pair loops. Solver sflj-1.1 explicitly checks LAMMPS z/vz and registers enforce2d after all force-changing fixes. Both paths share force-converged L-BFGS relaxation, PCG64-seeded BAOAB equilibration, frozen-grip unstrained NVE verification, and the same post-NVE reference geometry. LAMMPS executes the Jinja2 input template for real driven trajectories; its Langevin/NVE stochastic loading integrator differs from NumPy BAOAB, so seed equality does not imply cross-engine trajectory identity. Deterministic two-body native and table-output parity is tested. A separate three-seed pristine-crystal ensemble was measured on this host: mean peak stresses differed by 0.63%, all six runs fractured, and crack-region agreement was 2/3. The small sample is descriptive and does not establish population or per-case equivalence; see [engine comparison](docs/ENGINE_COMPARISON.json). Run `.venv/bin/python -m benchmarks.validate_engines` to repeat it; absent verified LAMMPS is reported as NOT_RUN.

Engineering strain is the change in top-to-bottom grip separation divided by the post-NVE gauge. Strain rate is per LJ physical time, not per timestep. Free x boundaries, prescribed opposite grip motion, mobile-only thermostat; temperature means mobile kinetic energy per two translational DOF. Tensile-positive stress is the negative conventional kinetic-plus-configurational pressure tensor divided by nominal width × current gauge, with unit thickness. Grip-reaction agreement is checked in the elastic lattice test and the actual traction trace is retained. This is 2D normalization, not arbitrary stress scaling.

Reference neighbors are defined within 1.35r₀ after NVE. Active rupture requires two severed reference bonds beyond 1.65σ, positive net coordination loss, and current Z≤4, excluding grips. Reference-connected clusters of at least four atoms must persist across three measurements. Fracture is assigned retrospectively to the first confirmed post-global-peak frame below 65% of the positive peak, using a fixed three-sample centered stress mean. Otherwise `failure_strain=null` and the run is censored. Numerical failure is distinct from censoring and is excluded from causal evidence.

Matched seeds are 42, 137 and 271. Effects use paired deltas and a noise floor; three pairs are descriptive. A diagnostic repeat cannot establish causal repair. Geometric edits infer missing sites from measured aligned lattice rows; rotated or disordered crystals may have no applicable reconstruction. No pristine site IDs or privileged labels are available to investigator tools.

## Jobs, budgets and persistence

Interactive API requests recompute counterfactuals by default (`force_recompute=true`); immutable baseline replicates may be reused and are tagged in the audit. Set it false for explicit cache reuse. All long operations return HTTP 202 with a durable `job_id`. Poll `/api/jobs/{id}` and `/api/cases/{case_id}`. SQLite transactions enforce one active job per case across workers; conflicting reset/hypothesis/experiment requests return 409. At most two jobs run globally per database. Default run/job deadlines are 30/120 s and the investigation budget is 1800 s. Deadlines and cancellation kill and reap worker descendants; results, failures, progress and raw seed records persist in SQLite. Server restart marks orphaned work `INTERRUPTED` and releases its durable lock.

Allowlisted typed experiment bodies use either `proposal_id` or `intervention` plus bounded parameters. No model-generated shell or Python is executed. Administrative benchmark jobs require `NANO_ADMIN_TOKEN` via `X-Admin-Token` and are rate limited. Privileged scoring runs separately only after observer decisions are frozen. Evaluation has a zero-intervention one-shot comparator and discloses budget differences and cache reuse.

## Verification and continuity

```sh
make test
make evaluate
make build
make e2e
```

The E2E script starts both real servers, runs HTTP and dashboard checks while they are alive, and cleans up launched process groups. [AGENTS.md](AGENTS.md) is authoritative. [Project state](docs/PROJECT_STATE.md), [handoff](docs/HANDOFF.md), [plan](docs/IMPLEMENTATION_PLAN.md) and [executed results](docs/TEST_RESULTS.md) record ordered phase gates and Git checkpoints.

The follow-up [scientific audit](docs/SCIENTIFIC_FINDINGS.md) explains the failed diagnoses using measured temperature, force-balance, seed and rate controls. It preserves the frozen benchmark and reports protocol improvements separately from held-out results.
