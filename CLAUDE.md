# CLAUDE.md — F1 2026 Miami GP Decision Analytics Project

This file is standing context for every session in this repo. Read it before
doing anything else.

## How to work in this project (read this first)

- **Do not run any code automatically.** Write scripts, explain what they do
  section by section, and stop. I will run them myself and come back with
  output/questions. This applies to every task unless I explicitly say
  "go ahead and run it" in a specific message.
- **Read-only inspection is fine without asking** (e.g. checking a file's
  columns/shape to answer a question), but building or modifying any dataset,
  report, or pipeline step is write-the-code-and-stop.
- When you hand back a script, flag anywhere I should sanity-check the output
  myself rather than trust it blindly — especially anything involving
  time/unit conversions (see the sector-time bug below — that class of bug
  won't throw an error, it just silently corrupts data).
- Keep each processing step's output as an explicit, separate file/report
  rather than silently overwriting prior work, so earlier QC stays auditable.
- Python only for this project (not R) — see rationale in prior discussion:
  nested JSON handling, HMM/clustering/Shapley library maturity.

## Project scope

Single-race (2026 Miami GP) decision analytics and performance attribution —
how strategic decisions, driver behavior, vehicle characteristics, and race
conditions interact to produce outcomes. This is **not** race prediction.
Analytical lens prioritizes car/engineering behavior over driver-vs-driver
comparison (driver comparison is a secondary lens, not primary).

Methodological inspiration: baseball sabermetrics (*Statistical Thinking in
Sports*) — skill-vs-luck separation, hierarchical shrinkage, Shapley
decomposition, adapted to F1. Approach is ML-driven unsupervised discovery,
not hypothesis-first regression. Single-GP scope means n≈20 drivers per race
— regression-heavy or large-n methods are out of scope.

## Root question and branch structure — finalized wording, do not paraphrase away the specifics

Full bilingual version lives in `F1_questions_updated.docx` (supersedes any
earlier `F1_questions.docx`) — this section is the authoritative English
summary for quick reference.

**[ROOT] The energy allocation curve across the lap.** Across different
corner and straight terrain, does a driver's actual harvest/deploy
allocation track the theoretical marginal-utility curve implied by the
350kW rate cap and 9MJ per-lap harvest limit — and where does the gap
between actual and optimal allocation show up?

**Methodology note — what the "optimal curve" actually means.** This is
**not** a known, publicly available physical optimum — real power-unit
energy management strategy is proprietary team IP, and this project lacks
the vehicle mass, aero maps, and true battery SoC data needed to compute a
genuine physical optimum. The project substitutes an **empirical frontier**
for a theoretical physical optimum: within the Miami race itself, laps are
grouped by track segment (per `corners.json`), and the best-performing
instances in each segment (by segment time or harvest efficiency) define
the practical frontier. The gap between other drivers/teams and this
empirical benchmark is the analysis target. This relies entirely on the
~700–800 clean laps already available within this single race — extending
to multiple races is a separate, deliberate scope decision, not a default,
and should only be revisited if the single-race sample proves insufficient.

**Analysis framework — Engine-family control.** For 2026, the Mercedes
power unit supplies four teams (Mercedes, McLaren, Williams, Alpine); the
Ferrari power unit supplies three (Ferrari, Haas, Cadillac). Any branch
comparing behavior across teams — especially Branch 3, and secondarily
team-level slices of Branches 2/4/5 — should default to comparing **within
an engine family** rather than pooling all 11 teams, to strip out engine
hardware as a confound. Primary comparison group: the four Mercedes-engine
teams. Secondary cross-check group: the three Ferrari-engine teams, to test
whether doctrine divergence within a shared engine family is a robust
pattern rather than a Mercedes-specific fluke. Known limitations to state
explicitly, not assume away: customer teams sometimes receive engine
upgrades later than the works team, so "same engine" doesn't guarantee
identical hardware all season; and chassis/cooling architecture itself
constrains available harvest strategy, so this only controls for engine
hardware, not aerodynamics cleanly.

**BRANCH 1 — Segment discovery: what the car is actually doing, corner by
corner. (Hard dependency — nothing downstream gets built before this is
validated. This is the current and only active analysis step — see
Analysis Order below.)**
- *1a.* Can unsupervised segmentation (HMM/change-point detection) over
  speed/throttle/brake/gear recover a driving-state vocabulary — pure
  acceleration, friction braking, lift-and-coast, engine-brake harvest
  (downshift-heavy deceleration), and super-clipping (throttle lift near top
  speed with no brake input and no upcoming corner) — without those states
  being predefined?
- *1b.* Does the mix of discovered states vary systematically by terrain
  type — heavy-braking hairpin vs. medium-speed flowing corner vs.
  traction-limited corner exit vs. long straight — in a way consistent with
  harvesting being concentrated near top speed and on lift-off before
  hard-braking zones, and engine-brake harvest concentrated in low-gear,
  high-RPM deceleration zones?

**BRANCH 2 — Corner-exit deployment intensity.** At corner-exit segments,
does MGU-K deployment intensity scale with the length of the straight
ahead — i.e., is more energy committed on corner exits that feed longer
straights, where the resulting speed gain compounds over more distance?

**BRANCH 3 — Harvest doctrine within an engine family (rewritten).**
Holding power-unit hardware constant, does the engine-family group
(primarily the four Mercedes-engine teams) show systematically different
harvest doctrines — friction-braking-heavy, lift-and-coast/super-clip-heavy,
or engine-brake-heavy — based on the behavioral segments discovered in
Branch 1? Cluster within the engine-family group without assuming a fixed
number of doctrines; let the data determine how many are statistically
supported. Relate discovered doctrine differences to this race's results
(grid position, pace, finishing position) to test whether doctrine
differences actually translate into results. Cross-check by repeating the
same analysis on the three Ferrari-engine teams as an independent second
sample.

**BRANCH 4 — Overtake Mode as a deployment decision under attack.** Within
DRS-detection-range attacking segments, does deployment behavior (timing,
intensity, and source — Boost, Overtake Mode, or banked reserve) differ
systematically from a free-air straight of equivalent length, and does that
difference predict overtake-attempt success — separating "attacked because
energy was available" from "attacked and it worked"?

**BRANCH 5 — Phase attribution to competitive advantage.** Using the
discovered behavioral segments as the decomposition basis, which state —
high-speed harvest, corner-exit deployment, or Active-Aero-linked drag
configuration — carries the largest Shapley weight in explaining a team's
sector-time advantage at this Grand Prix?

## Analysis order

Only **Branch 1a** is an active analysis step right now. ROOT, 1b, and
Branches 2–5 all consume 1a's output (the discovered driving-state
vocabulary) as an input — none of them can start before 1a's states are
built and validated. Do not begin work on any other branch until 1a is
confirmed to produce physically sensible states (see Task 5 in the file
inventory below).

## Data sources

- **TracingInsights 2026 repo** (`github.com/TracingInsights/2026`) — primary
  telemetry source. Path structure: `{Event}/{Session}/{Driver}/{lap}_tel.json`.
  Channels in the `tel` dict: `time, distance, rel_distance, speed, throttle,
  brake, gear, rpm, acc_x, acc_y, acc_z, x, y, z, DriverAhead,
  DistanceToDriverAhead, drs`. Also per-session: `corners.json`,
  `drivers.json`, `rcm.json`, `session_laptimes.json`, `weather.json`.
- **TracingInsights CSV export tool**
  (tracinginsights.com/analysis/download-raw-data/) — source of the laps CSV
  and weather CSV. These match FastF1's `Session.laps` /
  `Session.weather_data` schema almost exactly (TracingInsights builds on
  FastF1).
- **FastF1 API** (`docs.fastf1.dev`) — used for `session.results`,
  `session.race_control_messages`, `session.track_status`,
  `session.get_circuit_info()`, `session.event`. Treat as a cross-check /
  supplementary source, not a telemetry replacement — the JSON telemetry
  above already has channel-level data.
- **OpenF1 API** (`openf1.org`) — `/v1/overtakes` endpoint, not yet used.
- **Jolpica-F1 API** (`jolpi.ca`) — grid positions, DNF/retirement reasons,
  not yet used.
- **TracingInsights-Archive** — 2018–2025 historical data, same schema,
  potential future pre/post-2026 comparison (not yet in scope).

## Established data facts — don't re-derive, use these

- **`drs` field is unreliable for 2026 Overtake Mode detection** (legacy
  field, stale) — infer Overtake Mode from other signals instead.
- **`brake` is binary (0/1), not continuous pressure.** Braking *intensity*
  must come from `acc_x`, not from `brake` itself.
- **Battery/MGU-K state-of-charge is not available from any public source.**
- **Real per-lap energy throughput ceiling is ~9–13MJ vs. a 4MJ storage
  cap** — super-clipping and engine-brake harvesting are mechanically
  distinct behaviors, both relevant to Branch 3.
- **"Manual Override Mode" and "Overtake Mode" are the same system**, not
  distinct regimes.
- **Lead-car derating above 290km/h is continuous physics** (battery-state
  linked), not a discrete mode.
- **Weather join must use `direction='backward'`**, not `'nearest'`, on
  `LapStartTime` (or `Time`, document which), tolerance ~90s — `'nearest'`
  can pull a future weather reading relative to the lap. This was a
  corrected error in this project; don't reintroduce it.
- **`Sector1Time`/`Sector2Time`/`Sector3Time` in the laps CSV are already
  float seconds** — never call `pd.to_timedelta()` on them without
  `unit='s'` (or at all, since they don't need it). Doing so silently
  truncates them into near-zero nanosecond values with no error thrown. This
  was a real bug caught in this project — always include a regression check
  (`Sector1Time + Sector2Time + Sector3Time ≈ LapTime_in_seconds`) after any
  script that touches these columns.
- **Clean-lap filter (Miami GP, validated across two independent sources):**
  `is_green` (`TrackStatus=='1'`) & not pit in/out & `IsAccurate==True` & not
  in the Safety Car window (laps 6–11 — the *only* caution period in the
  race, confirmed via `race_control_messages.csv` and `track_status.csv`
  agreeing) & not an incident lap. Multi-digit `TrackStatus` codes (`12`,
  `41`, `24`, `124`) are within-lap status-change concatenations, not
  separate incidents — all trace back to the single SC period plus scattered
  local yellows.
- **GAS and LAW retired from the same Turn 17 collision** (laps 8–9) — not
  two independent retirements. `session.results['Status']` only says
  generic "Retired" for all DNFs; the real cause comes from
  `race_control_messages`. HUL and HAD have no race control mentions —
  likely mechanical retirements with no reportable incident.
- **FastF1's circuit corner/marshal data matches the existing
  `corners.json` exactly** (19 corners, rotation 2.0°, ~0.00 coordinate
  deviation) — no discrepancy between sources, safe to treat as one
  consistent reference.
- **Reddit thread used for early ideation is background only** — research
  questions must stand independently, never cite it directly.
- **2026 engine-family groupings:** Mercedes power unit → Mercedes, McLaren,
  Williams, Alpine. Ferrari power unit → Ferrari, Haas, Cadillac. Red Bull
  Powertrains (Ford) → Red Bull, Racing Bulls. Honda → Aston Martin. Audi →
  Audi (in-house). Constructor points spread within the Mercedes-engine
  group as of mid-July 2026 is large (Mercedes ~333, McLaren ~179, Alpine
  ~60, Williams ~11) — supports the premise that within-engine-family
  results diverge a lot, i.e. hardware isn't the dominant driver of outcome
  and there's real strategy variance worth analyzing. These standings will
  keep moving over the season — re-check before citing specific numbers.

## Open questions / not yet decided

- Whether unsupervised segment discovery + physics-consistency validation is
  a sufficient standalone contribution, or needs a supervised/rule-based
  companion.
- Whether a rule-based segmentation fallback should be scoped in from the
  start (in case the HMM doesn't validate cleanly).
- Whether a pre/post-2026 same-track comparison (via TracingInsights-Archive)
  is an acceptable scope extension.

## File inventory (update paths if the working folder moves)

As of 2026-07-16 the project root was reorganized into subfolders (was
previously flat). Update this section any time a file's location changes.

```
f1/
├── CLAUDE.md
├── scripts/                     numbered pipeline scripts, run in order
│   ├── 01_fetch_fastf1.py
│   ├── 02_build_master_laps.py
│   ├── 03_build_resampled_dataset.py
│   ├── 04_fit_hmm.py
│   └── 05_finalize_hmm_and_label.py
│   (branch1a_hmm_fit_and_label.ipynb also present - notebook version of
│   04+05, not actively used per latest instruction, kept for reference)
├── data/
│   ├── raw/                     source data, read-only, never edit in place
│   └── processed/                pipeline-built tables, safe to regenerate
├── models/                      fitted HMM + scaler
│   └── candidate_models/        n=4/6/8 (+ sensitivity-check variants)
├── diagnostics/                 plots + per-state tables from Branch 1a
└── reports/                     .md writeups, one per pipeline stage
```

**`data/raw/` (read-only, never edit in place):**
- `2026-Miami Grand Prix-Race.csv` — laps table, TracingInsights CSV export tool
- `2026-Miami Grand Prix-Race-weather.csv` — weather table, same export tool
- `session_results.csv`, `race_control_messages.csv`, `track_status.csv`,
  `circuit_info_fastf1.json`, `event_info.json` — FastF1 API pull
  (`01_fetch_fastf1.py`)
- `Miami_Race_cor.json` — used ONLY as the comparison target in
  `01_fetch_fastf1.py`'s FastF1-vs-existing-corners cross-check; NOT used
  anywhere else in the pipeline. Do not read this file for corner geometry
  in any new script — the canonical corners source is
  `Miami Grand Prix/Race/corners.json` under the external TracingInsights
  telemetry folder (different schema, same underlying data — see
  `05_finalize_hmm_and_label.py`'s docstring for the schema difference).
- `Miami_Practice1_cor.json` — **confirmed unused**, zero references
  anywhere in scripts/reports/CLAUDE.md. Leftover from an early exploratory
  step before the project focused on the Race session only. Candidate for
  deletion if disk space matters; harmless to leave.
- (External, outside this project folder entirely — never moved):
  `Miami Grand Prix/Race/{DRIVER}/{lap}_tel.json` per-lap telemetry, and
  `Miami Grand Prix/Race/corners.json`, `drivers.json`, `rcm.json`,
  `session_laptimes.json`, `weather.json` — TracingInsights per-session files

**`data/processed/` (pipeline-built, regenerable by re-running scripts/):**
- `laps_weather_merged.csv`, `master_laps_metadata.csv` — from
  `02_build_master_laps.py`. Weather merge uses
  `merge_asof(direction='backward')` on `LapStartTime` (an earlier
  `'nearest'` version was corrected and superseded — don't reintroduce it).
  Sector-time dtype bug fixed with a regression check that raises if it
  ever fails again.
- `resampled_telemetry.parquet` — from `03_build_resampled_dataset.py`.
  844,187 rows (791 clean_telemetry_lap laps × ~1067 grid points each, 5m
  distance grid), includes engineered features + rule-based baseline label.
- `branch1a_state_labeled_telemetry.parquet` — from
  `05_finalize_hmm_and_label.py`. Same shape as `resampled_telemetry.parquet`
  plus `hmm_state`/`hmm_state_label` columns.

**`models/`:**
- `branch1a_feature_scaler.joblib` — `StandardScaler` fit on the 5 HMM
  features, from `04_fit_hmm.py`.
- `branch1a_hmm_model.joblib` — the finalized chosen model (currently n=6),
  written by `05_finalize_hmm_and_label.py`.
- `candidate_models/hmm_n{N}[_covfull][_mincovarX].joblib` +matching
  `_ll.txt` — every fitted candidate from `04_fit_hmm.py`, kept for the
  model-selection record (log-likelihood, BIC, AIC per file).
  **Known issue (2026-07-16, unresolved):** `candidate_models/hmm_n6.joblib`
  was overwritten during later debugging/testing with a much weaker fit
  (log-likelihood ~8.1M) than the one `reports/branch1a_hmm_report.md`
  describes and was built from (~46.4M). `models/branch1a_hmm_model.joblib`
  + `data/processed/branch1a_state_labeled_telemetry.parquet` +
  everything in `diagnostics/` are still consistent with the ORIGINAL good
  fit (all last written 2026-07-14, before the overwrite) — those are
  trustworthy. Only `candidate_models/hmm_n6.joblib` itself is stale/wrong.
  Before trusting a fresh n=6 refit, re-run `04_fit_hmm.py 6 <N>` with
  enough restarts to reach ll≈46M again (5 restarts was sometimes enough,
  sometimes wasn't — restart-count sensitivity itself is not yet resolved)
  and check the printed log-likelihood before using the saved file.

**`diagnostics/`:**
- `hmm_state_feature_table.csv`, `hmm_state_occupancy_by_corner_zone.csv`,
  `hmm_state_occupancy_sample_laps.png`, `hmm_transition_matrix_heatmap.png`
  — from `05_finalize_hmm_and_label.py`.
- `rule_based_baseline_sample_laps.png` — from an earlier ad-hoc QC pass
  (not one of the numbered scripts); static artifact, not reproducible by
  re-running the current pipeline as-is.
- `resample_qc_sample_lap.png` — same caveat as above; referenced by a
  comment in `03_build_resampled_dataset.py` but not generated by it.

**`reports/` (.md writeups, one per pipeline stage):**
- `data_inventory.md`, `data_qc_summary.md` — Task 1–2 (raw CSV inventory + QC)
- `data_merge_and_join_qc.md`, `weather_join_fix_report.md`,
  `fastf1_api_pull_summary.md` — Task 3 (merge + FastF1 API pull)
- `master_clean_lap_report.md` — Task 4 (master clean-lap table)
- `branch1a_hmm_report.md` — Task 5 / Branch 1a (HMM fitting + validation).
  Predates the BIC/AIC reporting added to `04_fit_hmm.py` — update with
  BIC numbers once n=8 can be fit reliably enough to compute one, and note
  the n=6 candidate-model staleness issue above if it isn't resolved first.

**Reference docs (not part of the pipeline, but authoritative for scope):**
- `F1_questions_updated.docx` — finalized bilingual question set (ROOT +
  methodology note + engine-family framework + 5 branches). Supersedes the
  original `F1_questions.docx`. (Location not yet confirmed inside this
  project folder — check with the user if it's needed and not found.)

## Current state (update this section as work progresses)

- Tasks 1–4 (CSV inventory/QC, weather join, FastF1 API pull, master
  clean-lap table) complete and verified — sector-time regression check
  passes, `clean_telemetry_lap` = 791.
- Task 5 / Branch 1a (resampling, feature engineering, rule-based baseline,
  HMM fit + validation) complete. `branch1a_hmm_report.md` documents the
  chosen n=6 model, its two known caveats (states 0/3 are one behavior;
  states 2/4 are a tightly-coupled pair), and the HMM-vs-rule-baseline
  comparison. **Open issue:** see the `candidate_models/hmm_n6.joblib`
  staleness note above — the saved n=6 *candidate* file no longer matches
  the report, though the *finalized* model/dataset used everywhere else
  still does. Resolve before doing further n=6 sensitivity comparisons.
- Root-cause code review (2026-07-16) found and fixed two real bugs in
  `05_finalize_hmm_and_label.py`: wrong/undocumented corners file, and a
  missing closed-loop wrap-around in the corner-proximity distance
  calculation. Also added BIC/AIC reporting and `--covariance-type`/
  `--min-covar` sensitivity-check flags to `04_fit_hmm.py`. The 100m
  "near corner" threshold used in that proximity calculation is still an
  arbitrary, unvalidated round number — not yet derived from anything
  track-specific (e.g. actual braking-zone lengths or marshal-sector
  boundaries).
- Per latest instruction, `scripts/branch1a_hmm_fit_and_label.ipynb` is not
  being used going forward — `04_fit_hmm.py`/`05_finalize_hmm_and_label.py`
  are the maintained versions; the notebook's corners-file/dtype fixes were
  NOT ported over to it and it should be treated as behind/stale if picked
  back up later.
- Analysis order per the section above: only Branch 1a is active. ROOT, 1b,
  and Branches 2–5 remain blocked until the candidate-model staleness issue
  is resolved and 1a's states are re-confirmed stable.