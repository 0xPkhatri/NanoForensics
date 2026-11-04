# NanoForensics frontend redesign plan

Prepared 2026-11-04. Status: implemented on `design/frontend-simplification`; automated gates pass. Rendered browser and human usability review remain pending. See [implementation report](FRONTEND_REDESIGN_IMPLEMENTATION.md).

## 1. Recommended direction

Make NanoForensics feel like a clear investigation workspace: warm paper backgrounds, strong charcoal headings, blue controls, orange emphasis, a large material view, and a short explanation of what is happening now.

The first screen should answer three questions immediately:

1. What does this project do? **Find out why a simulated material breaks.**
2. What can I do? **Choose a sample and start an investigation.**
3. What happens next? **Inspect the material, compare possible explanations, run tests, and check the evidence.**

This is a frontend redesign. Preserve the real physics, API behavior, independent verifier, frozen evidence, and separation between original cases, published study, and live AI rehearsal. Easier language must retain the meaning of uncertain and failed results.

## 2. What was reviewed

### Reference project

- [PlantDebugger repository](https://github.com/marcosanyo/PlantDebugger/tree/main), inspected locally at commit `d69507aa48aec773a5cf72761e5ff60c491eefc1`.
- Its `README.md`, Commander HTML, Commander styles and polish styles, including the distinction between the older dark homepage styles and the light Commander workspace shown in the video.
- [Commander layout source](https://github.com/marcosanyo/PlantDebugger/blob/d69507aa48aec773a5cf72761e5ff60c491eefc1/services/plant-debugger/plant_debugger/static/commander.html).
- [Commander color and layout styles](https://github.com/marcosanyo/PlantDebugger/blob/d69507aa48aec773a5cf72761e5ff60c491eefc1/services/plant-debugger/plant_debugger/static/commander.css).
- [Commander visual refinements](https://github.com/marcosanyo/PlantDebugger/blob/d69507aa48aec773a5cf72761e5ff60c491eefc1/services/plant-debugger/plant_debugger/static/commander-polish.css).

### Uploaded video

Local file: `/Users/prakash_mac/Downloads/vidssave.com Plant Debugger Devpost Demo 720P.mp4`. Measured duration: 239.708 seconds; resolution: 1280 × 720. Visual review used a 20-frame contact sheet sampled every 12 seconds across the video and larger frames at 00:24, 01:12, and 01:48. This review does not claim a full audio transcription or frame-by-frame review.

| Approximate video position | Observed presentation pattern | Adaptation for NanoForensics |
| --- | --- | --- |
| 00:00 | Product title and physical-world context | A short purpose statement tied to a material sample |
| 00:12–00:36 | Cream workspace, dark NOW banner, process diagram, adjacent evidence/task cards | Current investigation banner, large atom view, evidence and next-test column |
| 00:36–01:00 | Inspection evidence is attached to a specific action | Attach each measurement and model update to its experiment |
| 01:00–01:24 | Small intervention, observed response, updated diagnosis | Show prediction, measured result, and resulting explanation change together |
| 01:24–02:00 | Follow-up intervention and evidence verification | Show actual repeated tests and independent result checks |
| 02:00–03:00 | Cloud records and audit evidence | Provide a separate readable Evidence view and raw export |
| 03:00–03:24 | Phone/tablet operator demonstration | Use a stacked mobile workspace with a persistent current action |
| 03:24–03:59 | Architecture and deterministic verification explained | Explain AI, physics, and verification roles through a short help panel |

The exact palette below comes from the reference source. Video observations describe the visible sampled sequence; repository behavior beyond those frames comes from source/README inspection. Winning status was supplied by the user and was not independently verified.

### Our current frontend

Reviewed `page.tsx`, `globals.css`, API types, and all main presentation components: HeaderBar, LatticeCanvas, StressStrainPlot, HypothesisPanel, PlannerPanel, AuditReportModal, AIActionPanel, and DemoWalkthrough. Current source checkpoint: `23f2525`.

The local preview at `127.0.0.1:3000` was offline during this review. Browser inspection was attempted but did not produce a rendered dashboard. Current-product findings below are source-based; visual QA is an implementation gate, not a completed check.

## 3. Why the current experience is difficult

| Current issue | Effect on a new visitor | Planned change |
| --- | --- | --- |
| Dark navy surfaces and many equally weighted borders/badges | Most sections compete for attention | Warm light surfaces, fewer badges, clear section hierarchy |
| Long introductory, study, and provenance blocks before the material | The purpose and next action take too long to find | One-line purpose, compact truthful status, expandable supporting details |
| Three technical dataset options in one dropdown | Users must understand research history before starting | Plain workspace names with a one-sentence explanation |
| All six scientific sections on one long page | Users lose the current task while scrolling | Three views, persistent status, focused investigation workspace |
| “Counterfactual,” “virial,” “SNR,” “CV,” and raw enum strings | The interface assumes a specialist audience | Plain main labels with exact scientific terms in help/details |
| Multiple starting actions, reset, and exports at similar emphasis | No obvious first step | One primary Start investigation action; manual controls secondary |
| Planner opens with a utility formula and numeric table | Users see implementation mechanics before intent | Recommended test card with why, expected observation, and time estimate |
| Atom colors are normalized separately per frame | Similar colors can represent different damage amounts | Stable per-measurement scales, visible numeric legend |
| Lattice defaults to the first available counterfactual, while frame resets to initial | Users can lose track of which sample/result is visible | Explicit original/test selector, persistent run/frame identity |
| Original and edited geometries are fitted independently | Changes can look like differences in magnification | Shared comparison bounds and linked zoom where comparison is enabled |
| Long live receipts appear before the material in AI mode | Audit details obscure the scientific story | Compact action provenance in context, full receipts in Evidence |
| Generic loading panel also mentions backend startup commands | A product user receives developer instructions | Separate loading, unavailable-service, no-data, and retry states |

## 4. What to take from PlantDebugger

Adopt the light industrial worksheet character: paper-colored background, sheet panels, strong title rules, a fine grid inside the material viewer, and purposeful blue/orange accents. Adapt the NOW banner and the evidence → explanation update → next action pattern.

Improve readability beyond the reference: its very small uppercase labels, dense borders, and side-by-side browser windows are unsuitable as defaults for our audience. Use larger text, a single responsive workspace, generous spacing, and sentence-case controls. NanoForensics has one user workspace; it does not need Commander/Operator roles, equipment photos, or plant controls.

Create our own components and material illustrations. Use the reference as design guidance rather than importing its CSS stack or branding.

## 5. Visual system

### Color tokens

| Token | Proposed value | Purpose |
| --- | --- | --- |
| `--page` | `#F2EEE4` | Warm background, matching reference paper |
| `--surface` | `#FFFDF8` | Main cards and chart canvas |
| `--surface-muted` | `#EAE4D8` | Grouped controls and metadata |
| `--ink` | `#18212A` | Main text and current-status banner |
| `--text-secondary` | `#535B58` | Supporting body text; contrast-check before acceptance |
| `--line` | `#C8C0B2` | Quiet dividers and chart grid |
| `--line-strong` | `#918A80` | Selected panel boundaries |
| `--blue` | `#2457D6` | Primary actions, selected tabs, original sample curve |
| `--blue-soft` | `#E7EDFF` | Selected backgrounds |
| `--orange` | `#E4612D` | Highlights and current test; avoid small white text on this fill |
| `--orange-strong` | `#B94218` | Orange button fill if white-text contrast passes |
| `--orange-soft` | `#FFF0E8` | Test-change cards |
| `--green` | `#1C7A55` | Evidence supports an explanation; successful execution checks |
| `--green-soft` | `#E7F4ED` | Positive result background |
| `--amber` | `#855315` | Uncertain results, offline fallback, incomplete runs |
| `--red` | `#B83D35` | Execution errors and failed checks |

Use blue for the primary button, orange for the active test, and green only when the underlying evidence/status warrants it. Use icons and words with colors. Do not color a rejected hypothesis as a system failure. Verify actual combinations to WCAG AA; proposed hex values are not a completed accessibility audit.

### Typography, spacing, and shape

- Body: system sans-serif, 16 px, approximately 1.55 line height; no font-download dependency required.
- Page title: 32–40 px on desktop, 28–32 px on mobile. Section headings: 20–24 px.
- Supporting text: 14 px minimum for meaningful content. Monospace only for IDs, timestamps, hashes, and aligned numeric readouts.
- Use sentence case. Reserve uppercase for short optional labels, not full explanations.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48 px. Card padding: 20–24 px desktop, 16 px mobile.
- Cards: 1 px border, 8 px radius, restrained shadow. Thin charcoal title rules can retain the worksheet character without boxing every sentence.
- Content width: approximately 1440 px. Desktop margins: 32 px; mobile: 16 px.
- Controls: at least 44 px touch targets, visible focus, descriptive accessible names.
- Avoid decorative gradients, glass surfaces, glowing effects, and continuous animation.

## 6. Navigation and workspace structure

Use three main views: **Investigate**, **Results**, and **Evidence**. Keep **How it works** as an accessible help panel. The scientific loop still has six stages; the views organize it without changing its behavior.

| View | Question it answers | Main content |
| --- | --- | --- |
| Investigate | What is happening, and what should we test? | Sample viewer, current step, possible explanations, recommended test |
| Results | What changed, and what does that support? | Original/test comparison, measured outcomes, independent verdict |
| Evidence | Can I inspect and reproduce this? | Timeline, model receipts, run IDs, checks, per-run results, export |

### Workspace selection

Keep all three API namespaces and databases separate. Present them as:

| Existing internal workspace | Display label | Required explanation |
| --- | --- | --- |
| `original` | Original samples | Four preserved benchmark samples; existing evidence may be inconclusive |
| `demonstration` | Published study | Saved deterministic simulations and published findings; no live model inference |
| `live` | AI investigation | New model actions in an isolated post-study rehearsal; results depend on measured evidence |

Default to the user's last valid workspace. On a first visit, open Original samples and offer an explicit **Explore the guided example** link into the published study. Do not silently select a successful case or switch to a workspace that calls the provider. Sample choices remain neutral: “Sample Alpha · CASE_ALPHA,” or an existing opaque DEMO ID. Never add defect names to case cards.

Workspace and sample selectors stay visible. Changing them must not cancel or reset an investigation. Disable switching during active operations for the first implementation, and explain why. Later background-job navigation can be added deliberately.

### Desktop wireframe

```text
NanoForensics        Investigate | Results | Evidence        Help
Find out why a simulated material breaks.
Original samples v    Sample Alpha · CASE_ALPHA v   Physics / AI status

┌ NOW ───────────────────────────────────────────────────────────┐
│ Ready to investigate this sample           [Start investigation]│
│ We will compare possible causes using simulated tests.         │
└───────────────────────────────────────────────────────────────┘
Inspect → Explain → Choose a test → Run test → Check evidence → Conclude

┌ THE MATERIAL ─────────────────────┐ ┌ WHAT WE LEARNED ──────────┐
│ Original sample | Selected test   │ │ Measured observation      │
│                                  │ │ Possible explanations     │
│      Real atom coordinates       │ │ What changed after a test │
│      and measured bond loss      │ └───────────────────────────┘
│                                  │ ┌ NEXT TEST ────────────────┐
│ Start | Peak load | Last frame    │ │ What it changes           │
│ legend + frame/run identity       │ │ Why it is useful          │
├ STRETCHING RESPONSE ──────────────┤ │ Estimated time            │
│ Original / test curves            │ │ [Run this test]           │
└──────────────────────────────────┘ └───────────────────────────┘
Compact outcome / study limitation    [View results] [View evidence]
```

At widths above 1200 px use approximately 62%/38% columns. At 768–1199 px use a stacked material/result area with supporting cards below. Below 768 px: current status, primary action, next test, material, chart, explanations. Keep source order logical and avoid duplicating controls in inaccessible hidden copies. Only the header and a compact mobile action bar may be sticky; they must not cover content or focused controls.

## 7. Six-stage investigation experience

The progress rail reflects actual available state. It may revisit stages when new evidence prompts another test. It must not run on a timer or imply that every investigation completes all steps successfully.

| Stage | Display label | What the user sees |
| --- | --- | --- |
| Observe | Inspect | Original material, recorded response, observed facts |
| Hypothesize | Explain | Possible causes and the observations each would explain |
| Plan | Choose a test | Recommended change, why it helps, expected observation |
| Experiment | Run test | Actual worker status, elapsed time, cancel control |
| Verify | Check evidence | Execution check separately from scientific support |
| Conclude | Conclude | Supported explanation or clear uncertainty, plus evidence links |

### Initial and running screens

Initial title: **Find out why this material breaks.** Supporting copy: “Compare possible causes by changing one condition and checking the simulated result.” Primary CTA: **Start investigation**. Secondary: **Explore the sample**. Put manual hypothesis generation under **Choose tests myself**.

During a run, replace vague activity with actual messages such as “Generating possible explanations,” “Running test 1,” and “Checking the result.” The existing server message remains available as details. Show elapsed time and remaining compute budget as **Compute used: X of Y**; do not present budget as an ETA. Show an ETA only when the existing estimate has an explainable basis. Use indeterminate progress when no step count is furnished.

### Material viewer

- Title: **The material**. Helper: “Each dot is an atom. Links show nearby atoms.” Display links are proximity guides, not the verifier's severed-reference-bond graph; disclose this distinction in technical help.
- Default coloring: **Lost neighbors**. Other choices: **Neighbor count** and **Local tensile stress**, with scientific definitions in help.
- Use a sequential, contrast-tested damage palette and a fixed numeric scale for the selected dataset/comparison. Zero must have the same meaning in every frame; show scale limits and any clipping.
- Name frames **Start**, **Highest load**, and **Fracture** or **Last recorded frame**, driven by outcome. Show strain, timestep, simulation ID, and replicate identity in details.
- Current API supplies selected snapshots, generally three, not a continuous trajectory. Use a snapshot stepper. Do not imply smooth playback or interpolate atomic positions into invented motion.
- Keep original and selected test clearly labeled. Highlight measured damage only; no case-specific defect arrows or inferred ground-truth overlays.
- Add explicit zoom/reset buttons, keyboard-accessible frame controls, a summary of atom-count/damage measurements, and an accessible alternative to hover-only atom inspection.
- Preserve actual coordinate geometry and aspect ratio. Use shared bounds for comparisons and reset frame/selection intentionally when switching runs.

### Possible explanations

Each card shows a short title, “Why it might fit,” “What would test it,” a status label, and its action source. Put long mechanisms and missing evidence under **See evidence**. Do not truncate model text into a different meaning or replace it with a fixed diagnosis.

Label any model confidence as **Model score — not a measured probability**. Offline scores must be called **Heuristic score**. These scores remain distinct from independent scientific verdicts. Predicted improvements are clearly labeled **Prediction**, never displayed as measured results.

### Recommended test

Replace the default utility table with one leading card plus **Other tests**. Rank using the actual proposal utility, retaining all alternatives. Card content: “What changes,” “What stays the same,” “Why this test helps,” “What the proposal predicts,” estimated runtime, and **Run this test**. Keep utility/gain/risk and seed details in **How this was ranked**. Execute existing validated proposal IDs only.

Do not call every intervention a repair: changing loading rate or temperature tests a condition, and geometric edits may fail to improve the response. Use “test change” when speaking generically.

### Results

Use an outcome headline derived from the verifier and execution status. Below it, show **Original sample**, **After the test change**, and **Measured difference**. Keep original/test identity visible across viewer, chart, and results. Do not call a counterfactual “improved” unless the reported metric supports that direction.

Chart title: **How the material responds to stretching**. X-axis: **Stretch (%)** with technical engineering-strain definition; convert displayed values by ×100 consistently in axes and tooltips. Y-axis: **Tensile stress (LJ reduced units)**. Do not rename stress to applied force or convert reduced units to MPa. Blue solid line = original; orange dashed line = test change. Keep standard-deviation/replay-spread labeling accurate and do not call either a confidence interval.

Show failure strain only when measured and valid. For censored runs, show **No fracture observed up to X% stretch**. A null recovery is **Not available**, not zero. Keep valid-run count and uncertainty context beside aggregate metrics. Place simulation failure reasons beside the affected result; invalid numerical data cannot be presented as causal evidence.

### Evidence

Readable event cards: time, action, new observation, result, and source. Link each event to its experiment/run and model receipt where supplied. Show actual before/after model scores only when recorded. If there is no structured update, show the existing recorded explanation; do not manufacture a belief-revision narrative.

Keep filters simple: **All**, **AI actions**, **Simulations**, **Checks**. Provide **Download full evidence (JSON)** using the existing raw export, and preserve complete per-run hashes, seed identities, errors, units, and protocol details. Long raw JSON can remain collapsed below a readable summary. The main result must remain understandable without opening JSON.

## 8. Plain-language dictionary

Centralize display labels in a presentation helper. Backend enum values and exported evidence stay unchanged.

| Current wording | Main UI wording | Explanation or exact term in details |
| --- | --- | --- |
| Blind specimen | Sample | Preparation is withheld during investigation |
| Autonomous investigation | Start investigation | Automatically compare explanations and tests |
| Generate hypotheses | Suggest possible causes | Hypothesis generation |
| Competing mechanisms | Possible explanations | Physical mechanisms proposed for testing |
| Counterfactual | Test change | Compare a changed condition with the original |
| Counterfactual planner | Choose the next test | Proposal utility and constraints |
| Run paired test | Run this test | Uses matched seeds where applicable |
| Coordination Z | Neighbor count | Number of nearby atoms under the defined cutoff |
| Bond loss ΔZ | Lost neighbors | Net coordination loss; distinct from severed reference bonds |
| Per-atom tensile virial | Local tensile stress | Exact per-atom virial measurement and convention |
| Failure strain | Stretch at fracture | Engineering strain at confirmed fracture |
| Peak stress | Highest tensile stress | Keep reduced-unit label |
| Right-censored | No fracture observed during this run | Does not establish that fracture is impossible |
| SNR | Effect compared with run-to-run variation | Signal-to-noise definition in details; deterministic metric labeled separately |
| CV | Relative run-to-run variation | Coefficient of variation and sample context |
| Utility score | Test priority | Information gain − cost penalty − risk |
| Numerical consistency | Simulation checks | Integration, temperature, and validity checks |
| SUPPORTED | Evidence supports this | Not proof or universal material validation |
| REJECTED | Evidence does not support this | Scoped to the tested explanation/protocol |
| INCONCLUSIVE | Not enough evidence | Existing evidence cannot decide |
| PENDING | Not tested yet | If execution failed: “No scientific verdict” |
| EXECUTION_FAILED | Simulation could not complete reliably | Execution error, separate from a hypothesis verdict |
| heal_interior_vacancy | Restore missing interior atoms | Proposed operation, not confirmation that atoms were missing |
| smooth_surface_notch | Restore missing edge atoms | Proposed operation, not a disclosed preparation label |
| normalize_strain_rate | Use the reference stretching rate | No claim that a slower rate is always correct |
| normalize_temperature | Use the reference temperature | Preserve protocol values and units |
| repeat_replicate_seeds | Repeat with additional runs | Identify independent seeds versus deterministic replays |

## 9. Visible honesty and exceptional states

Simplify explanations through layers while retaining a compact visible limitation appropriate to the workspace. Published-study and rehearsal views must continue to say **Full published study: NOT_VALIDATED** with a short explanation: “The complete study did not meet all its preset criteria.” A successful case cannot replace that study-level result.

| State | Main presentation | Available action |
| --- | --- | --- |
| Service connecting | “Connecting to the simulation service…” with skeleton regions | Wait; no misleading ready state |
| API unavailable | “Cannot connect to the simulation service.” | Retry; developer setup in optional help |
| No generated samples | “No simulated samples are available yet.” | Retry after setup; no fabricated examples |
| Ready, no hypotheses | Explain what the investigation will do | Start investigation |
| Connection probe succeeded, no action | “AI connection checked · no action yet” | Request a real action |
| Action succeeded live | “Last AI action: Muse Spark · [time]” | Open that action's receipt |
| Offline fallback | “Offline mode · rule-based suggestions” | Explain unavailable provider without hiding fallback |
| Published deterministic study | “Saved study · no model inference” | Inspect saved evidence |
| Running actual MD | “Running simulation…” plus server progress | Cancel current job |
| Reused immutable MD | “Using a saved simulation” | Inspect run/source receipt |
| Cancel requested | “Stopping the current job…” | Await server acknowledgement |
| Cancelled or timed out | Show confirmed execution status and retained evidence | Resume/retry only through supported API actions |
| Numerical failure | “Simulation checks failed; this run cannot support a conclusion.” | Inspect error and valid remaining runs |
| Censored | “No fracture observed up to X% stretch” | Inspect horizon; no invented fracture strain |
| Evidence inconclusive | “The tests did not identify a clear cause.” | Inspect remaining allowed proposals/evidence |
| Supported result | Verifier-supported explanation and measured comparison | View evidence/export |
| Mixed action sources | Label latest action and source per card/receipt | Review full AI history |

Do not use a permanent “Live AI” badge based on startup or old receipts. The header shows the relevant latest action and timestamp; individual hypotheses and proposals retain their own provenance. Display a concise physics label such as **Physics: LAMMPS** or **Physics: NumPy**, with exact solver/potential/version in details.

Retain a brief scope line: **Research simulation in 2D; results do not validate real engineering materials.** Keep full methodology one click away.

## 10. Component and file changes

| Existing file | Planned responsibility |
| --- | --- |
| `frontend/src/app/page.tsx` | Compose the three views and current workspace/sample; move request/polling state out of dense JSX |
| `frontend/src/app/globals.css` | Replace dark styling with semantic light tokens, responsive grid, readable controls, chart/viewer surfaces |
| `frontend/src/app/layout.tsx` | Review metadata, font stack, page language, and global accessibility structure |
| `HeaderBar.tsx` | Branding, navigation, workspace identity, concise operation-specific provenance |
| `LatticeCanvas.tsx` | Light grid, stable color scale, legends, frame/run identity, zoom controls and accessible measurements |
| `StressStrainPlot.tsx` | Light Plotly theme, consistent percent formatting, explicit original/test identity, accurate spread labels |
| `HypothesisPanel.tsx` | Plain explanation cards, source badge, qualified score, evidence disclosure |
| `PlannerPanel.tsx` | Recommended test card, alternatives, details for ranking; preserve actual utility and proposal execution |
| `AIActionPanel.tsx` | Compact in-context receipts plus full history inside Evidence |
| `DemoWalkthrough.tsx` | Optional guided example; six short stage descriptions, actual data and clear post-study status |
| `AuditReportModal.tsx` | Readable report-first layout; preserve complete export and keyboard focus behavior |
| `frontend/src/lib/api.ts` | Retain wire contracts; remove display phrasing to presentation helpers when appropriate |

Proposed additions:

- `frontend/src/lib/presentation.ts`: typed labels, formatting, status mappings and deterministic summaries based only on public data.
- `frontend/src/lib/investigation-view.ts`: derive current stage, selected experiment, provenance context, and displayable result state from actual API records.
- `frontend/src/hooks/useInvestigation.ts`: existing fetching, polling, pending state, cancellation and job recovery, with stale-response protection.
- `frontend/src/components/CurrentStepBanner.tsx`: current action, explanation, elapsed/budget context and primary action.
- `frontend/src/components/InvestigationSteps.tsx`: accessible six-stage indicator.
- `frontend/src/components/WorkspaceSelector.tsx`: clearly separated workspace/sample selection.
- `frontend/src/components/EvidenceUpdateCard.tsx`: measured observation → recorded explanation update → proposed next test.
- `frontend/src/components/ResultSummary.tsx`: execution status, scientific verdict, uncertainty and comparison.
- `frontend/src/components/HelpPanel.tsx`: glossary, scientific roles and methodology links.

Do not add another UI framework or upgrade Next/React for this redesign. The actual package currently uses Next 16 and React 19; do not follow the older stack label by downgrading it. Use existing Tailwind/CSS, canvas and Plotly capabilities.

## 11. Implementation sequence and acceptance criteria

Effort ranges are planning estimates for focused engineering time, not execution promises. Total initial estimate: 23–35 hours; adjust after the first working layout.

| Phase | Work | Completion gate | Estimate |
| --- | --- | --- | --- |
| 1. Foundations and copy | Token palette, shared labels, navigation/state specification, accessible controls | Main labels understandable without the glossary; scientific meaning preserved | 2–3 h |
| 2. Workspace shell | Header, workspace selector, NOW banner, stage rail, three views, loading/error states | One obvious starting action; all namespaces reachable; no science/API behavior change | 4–6 h |
| 3. Investigation story | Explanation cards, recommended/alternative test cards, observed evidence update | User can explain why a test was selected; execute/cancel/recover supported jobs | 4–6 h |
| 4. Material and chart | Stable scales, labeled snapshots, shared bounds, light Plotly theme, accessible controls | Every displayed geometry/curve comes from real returned data; outcome and units accurate | 5–7 h |
| 5. Results and evidence | Outcome summary, per-action receipts, evidence timeline, report/export, workspace limitations | No live/fallback confusion, no fabricated result, no loss of audit detail | 4–6 h |
| 6. Responsive QA and demo | Mobile/tablet layouts, keyboard checks, browser scenarios, production build and regression gates | All checks below pass with screenshots and recorded limitations | 4–7 h |

Maintain a runnable checkpoint after each phase. Preserve existing user changes in `docs/TEST_RESULTS.md`, `frontend/next-env.d.ts`, and `repomix-output.xml`. Avoid broad staging or automatic database resets. Update continuity docs with actual results.

## 12. Verification plan

### User comprehension

Ask three people unfamiliar with the project to use the real interface. Treat these as targets until measured:

1. Within 10 seconds, describe the product as testing explanations for material failure.
2. Within 20 seconds, identify the sample and the Start investigation action.
3. Without opening advanced details, explain what the next test changes and why it is useful.
4. After a run, distinguish a measured result from an AI prediction.
5. Correctly recognize offline mode, an inconclusive result, and no observed fracture.

Record observed success/failure rather than declaring the UI intuitive based on appearance.

### Browser scenarios

- Inspect at 1440 × 900, 1280 × 720 (demo recording), 1024 × 768, 768 × 1024, and 390 × 844.
- Check all three workspaces, sample switching, empty explanations, alternatives, long AI text and unavailable API.
- Inspect real saved supported and inconclusive evidence; retain the study-level NOT_VALIDATED label.
- Verify null failure/recovery, invalid runs, no experiments, old receipts, live action, fallback action and mixed-source history.
- Exercise an authorized actual job, cancellation, reload/job recovery, and immutable cached result identity through the existing API workflow.
- Verify chart resize, percent tooltips, explicit comparison selection, stable legend, snapshot labels and no fabricated animation.
- Check keyboard navigation, visible focus, modal focus trap/return, Escape, color contrast, touch controls, reduced motion and screen-reader status announcements.
- Confirm no unexpected horizontal page scrolling and no primary action obscured by sticky content.

Use clearly labeled test fixtures only for frontend state coverage; never represent them as scientific data or live model proof. Scientific acceptance uses existing real records and sanctioned MD gates.

### Engineering gates during implementation

- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- `make test`
- `.venv/bin/python -m demonstrations.verify_preservation`
- `.venv/bin/python -m scripts.verify_rehearsal_preservation` when its required local snapshots exist.
- `bash scripts/verify_e2e.sh`, following the documented owned-server stop/restore procedure and isolated test databases.

Inspect gate behavior before running anything that initializes or mutates data. Add targeted frontend tests for status/provenance mapping, null/censored results and stale-response protection because incorrect displays can misrepresent science. Update visible-text assertions if copy changes, preserving semantic assertions. Do not add tests that merely compare every new label to itself.

No provider call is needed to repaint the UI. Existing live receipts can verify historical display only; claim a new live operation only after a new real response succeeds. Do not regenerate frozen cases, change scientific thresholds, edit hash-locked scientific code, or rerun study design search.

## 13. Proposed four-minute demonstration

| Time | On-screen sequence | Message |
| --- | --- | --- |
| 00:00–00:25 | Purpose, neutral sample selection, material | “Two samples can look similar in a chart but fail for different reasons.” |
| 00:25–00:55 | Actual possible explanations | “The system proposes explanations that can be tested.” |
| 00:55–01:25 | Recommended test and rationale | “It chooses a change that can distinguish the explanations.” |
| 01:25–02:20 | Actual simulation progress and returned comparison | “The physics computes the outcome.” |
| 02:20–03:00 | Measured evidence, recorded model update, next test if present | “New evidence can change which explanation fits.” |
| 03:00–03:35 | Independent verdict and uncertainty | “The verifier decides what the evidence supports.” |
| 03:35–04:00 | Evidence receipt/export and study limitation | “The record is inspectable; the complete published study remains NOT_VALIDATED.” |

This is a storyboard, not a promised run duration or prescribed outcome. If computation takes longer, show the actual wait or explicitly switch to a labeled saved run. Disclose cuts/speed changes. A fallback, failed test, or inconclusive verdict changes the narrative to match the evidence.

## 14. Definition of done

- A visitor understands the purpose, current step, and next action without knowing molecular-dynamics vocabulary.
- The delivered workspace visibly follows the reference's cream/charcoal/blue/orange direction with larger, simpler typography.
- The material and evidence-to-next-test story dominate the investigation view.
- All original workspaces, cases, real simulations, actions, job recovery, cancellation and exports remain usable.
- Current action provenance, immutable run identity, outcome, uncertainty and limitations stay accurate and accessible.
- Study-wide NOT_VALIDATED and post-study rehearsal status cannot be mistaken for a validated blind discovery.
- Browser, accessibility, production build and relevant regression/preservation gates have recorded results.
- The redesigned frontend is implemented and visually reviewed before this plan's implementation items are marked complete.

## 15. Current deliverable boundary

The initial planning task produced this specification. The subsequent user-authorized implementation is now on `design/frontend-simplification`: phases1–5 and automated phase6 checks are delivered. Browser rendering checks were blocked by the browser tool, and human comprehension targets remain unmeasured. See the implementation report for exact tests, preview ownership, preservation evidence and review limitations.
