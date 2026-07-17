# Branch 1a — Driving-State Segmentation (HMM) Report

## Scope

Goal: recover an unsupervised driving-state vocabulary from raw per-timestep
telemetry (speed, throttle, brake, acc_x, acc_y) for every `clean_telemetry_lap`
in `master_laps_metadata.csv` (791 laps, all 22 drivers), validate the states
are physically interpretable, and compare against a rule-based baseline.

**Note on the "earlier KMeans pilot" referenced in the task instructions:**
no artifact for this pilot (script, output, or plot) exists anywhere in this
project folder or elsewhere on disk that I could locate. The `n_components=6`
starting point and the state vocabulary named in `CLAUDE.md` (pure
acceleration, friction braking, lift-and-coast, engine-brake harvest,
super-clipping) are treated here as a stated prior to test against, not as a
result I can independently reproduce or diff against. If that pilot's
artifacts exist in another session/location, point me to them and I'll add a
direct comparison.

## 1. Resampling to a distance grid

- Grid: every 5m from 0 to each lap's max recorded `distance` (~5320-5340m
  for this circuit).
- Continuous channels (`speed`, `throttle`, `rpm`, `acc_x`, `acc_y`): linear
  interpolation (`np.interp`).
- Discrete channels (`gear`, `brake`, `drs`): step/nearest-prior
  interpolation via `searchsorted`, so no fractional gear/brake values are
  invented.
- **QC performed:** confirmed `distance` is strictly monotonic non-decreasing
  for every lap (required for `np.interp` to behave correctly). Visually
  compared raw vs. resampled speed/acc_x/gear/brake traces for a sample lap
  (NOR lap 2) — overlay is near-exact; round-trip interpolation error on
  speed is mean 0.15 km/h, max 2.8 km/h. Discrete channels (`gear`, `brake`)
  stayed exactly integer/binary post-resampling, confirmed via
  `np.unique()`.
- All 791 clean_telemetry_lap laps processed with **zero skips** (no
  non-monotonic distance, no missing files) → 844,187 total resampled
  timesteps.

## 2. Engineered features

Added on the resampled grid: `speed_delta`, `rpm_delta`, `gear_delta` (first
differences), and `acc_x_smooth` (3-sample centered rolling mean).

**Smoothing check performed before applying it by default:** plotted a raw
`acc_x` segment first. The signal has real, large, fast transitions (e.g.
+1.5 → -24 across a braking zone) riding on top of genuine point-to-point
jitter (~2.1 stdev in consecutive differences vs. ~8.4 stdev overall) — a
light 3-tap smoothing was judged appropriate to reduce jitter without
flattening genuine braking transitions. `acc_x_smooth` is stored alongside
raw `acc_x`, not in place of it, so downstream branches can choose either.

## 3. Rule-based baseline

`braking` (`brake==1`) / `full_throttle` (`throttle>=99`) /
`partial_throttle_no_brake` (else):

```
full_throttle:                61.0%
partial_throttle_no_brake:    25.7%
braking:                      13.3%
```

Visual check (4 sample laps, different drivers): braking clusters exactly at
speed troughs (corner entries), full-throttle on straights, partial
elsewhere — passes the smell test.

## 4. HMM fitting (n=4, 6, 8)

Pooled `GaussianHMM` (`covariance_type='diag'`), one shared model across all
drivers (not per-driver), fit on standardized
`[speed, throttle, brake, acc_x, acc_y]` with `lengths` marking lap
boundaries so no cross-lap transitions are learned.

**Numerical stability issue encountered and handled:** default EM fitting
repeatedly drove one state's covariance to near-zero mid-training (a state's
assigned points shrinking to nothing), producing NaN log-likelihoods and an
invalid (`zero-row-sum`) transition matrix — happened on every naive attempt
at n=6 and n=8, across multiple random seeds. Fixed by fitting iteration-by-
iteration and keeping the last snapshot **before** the transition matrix
became invalid, plus `min_covar=0.1` regularization, plus multiple random
restarts (5 for n=4/6, 12 for n=8), keeping the best converged result.

**Log-likelihood comparison** (best of restarts, per-timestep, n=844,187):

| n_components | total log-likelihood | per-timestep | notes |
|---|---|---|---|
| 4 | 46,201,448 | 54.73 | converged cleanly, 28 EM iterations |
| 6 | 46,375,639 | 54.94 | best of 5 restarts, small improvement over n=4 |
| 8 | 8,470,770 | 10.03 | best of 12 restarts — **never reached a comparable optimum; all restarts hit the collapse/early-stop before converging** |

**n=8 is not a valid comparison point as fit** — every restart's transition
matrix started losing states before reaching a fit competitive with n=4/n=6.
This isn't read as "8 states are worse," it's read as "8 states are harder
to fit stably with this feature set and this regularization," which is
itself informative: the 5-feature representation doesn't cleanly support
finer subdivision beyond ~6 states without running into
degenerate-covariance instability. A more determined attempt (heavier
regularization, feature-set expansion, or a `full`/`tied` covariance
structure) might resolve this, but was out of scope for this pass.

**Chosen model: n=6**, matching the stated prior and the only model besides
n=4 that converged to a stable, well-supported optimum. All three candidate
models are saved in `branch1a_candidate_models/` for inspection.

## 5. State interpretation (n=6)

| State | Occupancy | Speed | Throttle | Brake | acc_x | acc_y | Self-transition P | Label |
|---|---|---|---|---|---|---|---|---|
| 3 | 57.1% | 284 | 100% | 0 | +2.6 | -1.0 | 0.992 | **Flat-out acceleration / max speed** (dominant straight-line state) |
| 0 | 3.4% | 287 | 99% | 0 | +2.6 | -1.1 | 0.991 | Flat-out (transition-in sub-phase — see caveat below) |
| 1 | 2.5% | 296 | 42% | 0 | -8.7 | +1.2 | 0.887 | **Lift-and-coast at top speed** (throttle lift, no brake, before a braking zone) |
| 2 | 11.8% | 153 | 48% | 0 | +2.8 | +4.1 | 0.036 | Mid-corner partial throttle (phase A) |
| 4 | 11.8% | 154 | 51% | 0 | +3.2 | +3.8 | 0.018 | Mid-corner partial throttle (phase B) |
| 5 | 13.3% | 171 | 5% | 1 | -14.1 | +7.8 | 0.933 | **Hard braking** |

**Caveat — States 0 and 3 are the same physical behavior, not two distinct
ones.** They have near-identical means and occupy the *exact same* distance
ranges on every straight (checked directly: State 0's distance histogram
matches State 3's shape across all 500m bins), and the two states never
transition to each other (0.00 both directions in the transition matrix).
State 0 is a small (3.4%), separate sticky sub-cluster the HMM is using to
represent the first few timesteps of full-throttle acceleration
(differentiated by recent temporal context, since an HMM — unlike static
clustering — can condition on history), not a materially different driving
behavior. Effective distinct-behavior count is **5, not 6.**

**Caveat — States 2 and 4 form a tightly coupled pair**, not two
independent behaviors: near-identical means (both ~153 km/h, ~48-51%
throttle, positive acc_y/lateral load — mid-corner), very low
self-transition probability (0.02-0.04), and they transition to each other
at 0.92-0.94 — i.e. the model is mostly just alternating between two labels
for what looks like one continuous cornering phase. This may reflect a real
sub-phase distinction (corner entry vs. exit, e.g. by acc_x sign trend) that
the current feature set doesn't cleanly separate, or may be an
over-parameterization at n=6. Left as two states since they still map onto
physically real corner segments (see occupancy-by-zone below), but flagged
as the weakest part of this state definition.

### Occupancy vs. distance + corner markers (4 sample laps: NOR, VER, LEC, HAM, lap 30)

`hmm_state_occupancy_sample_laps.png` — states align with track sections
exactly as expected: State 3 (green) fills the long straights (T10→T17,
T3→T9), State 5 (red) clusters precisely at every heavy-braking corner
(T1, T8, T11-16 chicane sequence, T17), State 1 (purple) appears briefly
right before the two heaviest braking zones (pre-T1, pre-T11) — this is the
lift-and-coast signature the project's stated vocabulary was looking for.
Pattern is consistent across all four drivers.

### Transition matrix

`hmm_transition_matrix_heatmap.png` — no direct high-probability
flat-out→braking transition skipping a lift-off state: **State 3 (flat-out)
never transitions directly to State 5 (braking) at any meaningful
probability** (0.00); the only path into braking is via State 1
(lift-and-coast, 0.11) or the corner states 2/4 (0.04-0.05). This is the
physically-sensible transition structure the task asked to confirm.

### Occupancy by corner-zone (within 100m of a corner apex vs. not)

```
                State 0    State 1    State 2    State 3    State 4    State 5
On a straight    5.2%       4.7%       0.2%      86.6%       0.3%       3.0%
Near a corner     1.7%      0.4%      23.2%      28.2%      23.1%      23.4%
```

Straights are dominated by State 3 as expected (86.6%); corner zones split
across the two mid-corner states (2+4 = 46.3%) and braking (23.4%), with
flat-out down to 28.2% (still substantial — corner-exit acceleration and
some flowing corners keep full throttle even near the apex marker).

## 6. HMM vs. rule-based baseline — does temporal structure change anything?

```
HMM state    rule_state=braking   rule_state=full_throttle   rule_state=partial_throttle_no_brake
0                    0%                   99.9%                        0.1%
1                    0%                    4.4%                       95.6%
2                    0%                    1.0%                       99.0%
3                    0%                  100.0%                        0.0%
4                    0%                    2.1%                       97.9%
5                  100.0%                  0.0%                        0.0%
```

**Finding:** the HMM does not contradict the rule-based baseline — `braking`
and `full_throttle` map almost perfectly 1:1 onto HMM states 5 and
{0,3} respectively. What the HMM adds is a **three-way split of the rule
baseline's single `partial_throttle_no_brake` bucket** (26% of all
timesteps) into physically distinct sub-behaviors: lift-and-coast at top
speed before braking (State 1), and two mid-corner cornering phases (States
2, 4). This is exactly the kind of distinction a static rule/threshold
can't make but a temporal model can, since "partial throttle" alone doesn't
distinguish "just lifted off at 296 km/h before a braking zone" from
"cornering at 153 km/h mid-corner" — the HMM separates these because it
conditions on the surrounding sequence, not just the instantaneous reading.
This is a legitimate, positive methods finding: **adding temporal structure
did change and improve the state definitions**, specifically by recovering
the lift-and-coast/super-clipping behavior the project's root question is
built around, which the rule-based baseline cannot see at all.

## 7. Outputs

- `branch1a_state_labeled_telemetry.parquet` — 844,187 rows × 20 cols: every
  clean-telemetry-lap timestep with resampled channels, engineered features,
  `rule_state`, `hmm_state` (0-5), `hmm_state_label` (human-readable).
- `branch1a_hmm_model.joblib` — the chosen n=6 `GaussianHMM`.
- `branch1a_feature_scaler.joblib` — the `StandardScaler` fit on the 5
  features (`speed, throttle, brake, acc_x, acc_y`); required to transform
  new data before using the saved model.
- `branch1a_candidate_models/` — all three fitted candidates (n=4, 6, 8) +
  their log-likelihoods, kept for inspection/reproducibility of the
  model-selection comparison above.
- `hmm_state_occupancy_sample_laps.png`, `hmm_transition_matrix_heatmap.png`,
  `hmm_state_feature_table.csv`, `hmm_state_occupancy_by_corner_zone.csv`,
  `resample_qc_sample_lap.png`, `rule_based_baseline_sample_laps.png` —
  supporting diagnostics referenced above.

## Summary / recommendation before Branch 2

The n=6 HMM recovers a state vocabulary that is physically interpretable,
aligns with track geometry, has a sensible transition structure, and
strictly refines (doesn't contradict) the rule-based baseline — with two
caveats worth carrying forward: (1) States 0/3 are one behavior, not two
(effective count is 5 not 6), and (2) States 2/4 are a tightly coupled
cornering pair that may warrant a richer feature set (e.g. adding
`speed_delta` or a corner-relative position feature) to cleanly separate
corner-entry from corner-exit in a later iteration. Neither caveat blocks
downstream use — both pairs are still meaningfully distinguishable from the
other four states — but Branch 3 (harvest doctrine) in particular should be
aware that "mid-corner" isn't yet cleanly split into entry/exit phases at
this state count.

**Stopping here per the task instructions — awaiting confirmation before
starting Branch 2.**
