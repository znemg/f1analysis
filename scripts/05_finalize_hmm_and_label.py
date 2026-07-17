"""
Loads the chosen HMM candidate (default n=6, per the model-selection
writeup in branch1a_hmm_report.md - n=4/n=6 converged to comparable
log-likelihood, n=8 never converged cleanly across 12 restarts), decodes
states via Viterbi, attaches human-readable labels, and produces the
diagnostic plots/tables.

CAVEAT (methodology, not a bug): GaussianHMM models every feature's
per-state emission as continuous-Gaussian, including `brake`, which is
actually binary (0/1). This is an accepted engineering approximation for
this project (see CLAUDE.md's established data facts on `brake`), not a
"legal" continuous feature like the other four - stated here explicitly
rather than left implicit.

Usage: python3 05_finalize_hmm_and_label.py [n_components]
  defaults to n_components=6

Inputs:
  resampled_telemetry.parquet (must already have a `rule_state` column,
  added by 03_build_resampled_dataset.py) - PROCESSED_DIR
  branch1a_feature_scaler.joblib, candidate_models/hmm_n{N}.joblib - MODELS_DIR
  Miami Grand Prix/Race/corners.json (the canonical per-session corners
  file per CLAUDE.md's file inventory - NOT Miami_Race_cor.json in
  data/raw/, which is a different, undocumented schema that happens to
  hold the same underlying data) - external TracingInsights folder
Outputs:
  branch1a_state_labeled_telemetry.parquet  ->  PROCESSED_DIR
  branch1a_hmm_model.joblib                 ->  MODELS_DIR
  hmm_state_feature_table.csv, hmm_state_occupancy_by_corner_zone.csv,
  hmm_state_occupancy_sample_laps.png, hmm_transition_matrix_heatmap.png
                                             ->  DIAGNOSTICS_DIR
"""
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROJECT_DIR = "/Users/zhangyimeng/SportsAnalytics/f1"
PROCESSED_DIR = f"{PROJECT_DIR}/data/processed"
MODELS_DIR = f"{PROJECT_DIR}/models"
CANDIDATES_DIR = f"{MODELS_DIR}/candidate_models"
DIAGNOSTICS_DIR = f"{PROJECT_DIR}/diagnostics"
CORNERS_PATH = "/Users/zhangyimeng/SportsAnalytics/2026/Miami Grand Prix/Race/corners.json"
N_COMPONENTS = int(sys.argv[1]) if len(sys.argv) > 1 else 6

FEATURE_COLS = ['speed', 'throttle', 'brake', 'acc_x', 'acc_y']

# Human-readable labels derived from inspecting this specific n=6 model's
# per-state feature means (see branch1a_hmm_report.md section 5) - if
# re-fitting from scratch (different seed/restart landing on a different
# but equally-valid local optimum), state indices may not line up with
# these labels 1:1. Re-inspect hmm_state_feature_table.csv before trusting
# this mapping blindly.
STATE_LABELS_N6 = {
    0: "flat-out (transition-in sub-phase)",
    1: "lift-and-coast at top speed (pre-braking)",
    2: "mid-corner partial throttle (phase A)",
    3: "flat-out acceleration / max speed",
    4: "mid-corner partial throttle (phase B)",
    5: "hard braking",
}

model = joblib.load(f"{CANDIDATES_DIR}/hmm_n{N_COMPONENTS}.joblib")
scaler = joblib.load(f"{MODELS_DIR}/branch1a_feature_scaler.joblib")

full = pd.read_parquet(f"{PROCESSED_DIR}/resampled_telemetry.parquet")
full = full.sort_values(['Driver', 'LapNumber', 'distance']).reset_index(drop=True)

assert 'rule_state' in full.columns, (
    "resampled_telemetry.parquet is missing 'rule_state' - it should have "
    "been added by 03_build_resampled_dataset.py. Re-run that script first, "
    "or the final cross-tab against the rule-based baseline will KeyError."
)

lengths = full.groupby(['Driver', 'LapNumber'], sort=False).size().values
group_id = (full['Driver'] != full['Driver'].shift()) | (full['LapNumber'] != full['LapNumber'].shift())
assert group_id.sum() == len(full[['Driver','LapNumber']].drop_duplicates())

# dtype matches 04_fit_hmm.py (float64) - 05 previously used float32 here,
# an unnecessary inconsistency between the two scripts (harmless for
# .predict() in practice, but worth eliminating so a future debugging
# session never has to wonder if a dtype mismatch explains a discrepancy).
X = scaler.transform(full[FEATURE_COLS].values.astype(np.float64))

# -----------------------------------------------------------------
# Decode states (Viterbi - most probable state sequence)
# -----------------------------------------------------------------
states = model.predict(X, lengths)
full['hmm_state'] = states
if N_COMPONENTS == 6:
    full['hmm_state_label'] = full['hmm_state'].map(STATE_LABELS_N6)
else:
    full['hmm_state_label'] = full['hmm_state'].astype(str)
    print(f"NOTE: no human-readable labels defined for n={N_COMPONENTS}; "
          f"hmm_state_label just stringifies the state index. Inspect "
          f"hmm_state_feature_table.csv and add labels manually if needed.")

full.to_parquet(f"{PROCESSED_DIR}/branch1a_state_labeled_telemetry.parquet", index=False)
joblib.dump(model, f"{MODELS_DIR}/branch1a_hmm_model.joblib")
print(f"Saved branch1a_state_labeled_telemetry.parquet ({full.shape})")
print(f"Saved branch1a_hmm_model.joblib (n_components={N_COMPONENTS})")

# -----------------------------------------------------------------
# Per-state feature table
# -----------------------------------------------------------------
means_unscaled = scaler.inverse_transform(model.means_)
unique, counts = np.unique(states, return_counts=True)
occupancy = dict(zip(unique, counts))

state_table = pd.DataFrame(means_unscaled, columns=FEATURE_COLS)
state_table.insert(0, 'state', range(N_COMPONENTS))
state_table['occupancy_pct'] = [occupancy.get(i, 0) / len(states) * 100 for i in range(N_COMPONENTS)]
state_table['self_transition_p'] = np.diag(model.transmat_)
state_table.to_csv(f"{DIAGNOSTICS_DIR}/hmm_state_feature_table.csv", index=False)
print("\nPer-state feature means:")
print(state_table.to_string(index=False))

# -----------------------------------------------------------------
# Occupancy by corner-zone (within 100m of a corner apex vs. not)
#
# Fixed (code review caught two real bugs in an earlier version):
# 1. Was reading Miami_Race_cor.json (project root) - an undocumented file
#    with a different schema (list of per-corner dicts keyed 'Number') that
#    only worked by coincidence because it happens to hold the same
#    underlying data as the canonical file. Now reads
#    Miami Grand Prix/Race/corners.json, the file CLAUDE.md's file
#    inventory actually registers as the per-session corners source
#    (parallel arrays keyed 'CornerNumber'/'Distance').
# 2. The track is a closed loop, so a point near the end of `distance`
#    (e.g. 5300m on a ~5340m lap) can be physically right next to a corner
#    at distance~0 just past the start/finish line - a plain
#    abs(corner_dist - d) doesn't know that and would wrongly call it "far
#    from any corner". Fixed by taking the minimum of the direct distance
#    and the wrap-around distance (lap_length - diff).
# -----------------------------------------------------------------
with open(CORNERS_PATH) as f:
    corners_raw = json.load(f)
corner_distances = list(zip(corners_raw['CornerNumber'], corners_raw['Distance']))
corner_dist_arr = np.array([d for _, d in corner_distances])

lap_length = full['distance'].max()  # approx circuit length from the resampled grid

def min_wrapped_gap(d):
    diff = np.abs(corner_dist_arr - d)
    wrapped = np.minimum(diff, lap_length - diff)
    return wrapped.min()

# 为什么100m？这个还要确定
full['near_corner'] = full['distance'].apply(lambda d: min_wrapped_gap(d) < 100)
occ_by_zone = full.groupby(['near_corner', 'hmm_state']).size().unstack(fill_value=0)
occ_by_zone_pct = occ_by_zone.div(occ_by_zone.sum(axis=1), axis=0) * 100
occ_by_zone_pct.to_csv(f"{DIAGNOSTICS_DIR}/hmm_state_occupancy_by_corner_zone.csv")
print("\nState occupancy % by zone:")
print(occ_by_zone_pct.to_string())

# -----------------------------------------------------------------
# Diagnostic plots
# -----------------------------------------------------------------
state_colors_6 = {0: 'tab:blue', 1: 'tab:purple', 2: 'tab:orange',
                  3: 'tab:green', 4: 'gold', 5: 'tab:red'}
cmap = plt.get_cmap('tab10')
state_colors = state_colors_6 if N_COMPONENTS == 6 else {i: cmap(i) for i in range(N_COMPONENTS)}

sample_laps = [('NOR', 30), ('VER', 30), ('LEC', 30), ('HAM', 30)]
fig, axes = plt.subplots(len(sample_laps), 1, figsize=(14, 3.2 * len(sample_laps)), sharex=False)
for ax, (drv, lapnum) in zip(axes, sample_laps):
    lap = full[(full['Driver'] == drv) & (full['LapNumber'] == lapnum)]
    if len(lap) == 0:
        ax.set_title(f"{drv} lap {lapnum} - no data")
        continue
    for state, color in state_colors.items():
        mask = lap['hmm_state'] == state
        ax.scatter(lap.loc[mask, 'distance'], lap.loc[mask, 'speed'], c=[color], s=4, label=f"State {state}")
    for num, dist in corner_distances:
        ax.axvline(dist, color='gray', linestyle=':', alpha=0.4, lw=0.8)
        ax.text(dist, 55, str(num), fontsize=7, color='gray', ha='center')
    ax.set_ylabel('Speed (km/h)')
    ax.set_title(f"{drv} lap {lapnum} - HMM state (n={N_COMPONENTS}) vs distance, corner numbers marked")
    ax.legend(markerscale=3, fontsize=7, loc='upper right', ncol=3)
axes[-1].set_xlabel('Distance (m)')
plt.tight_layout()
plt.savefig(f"{DIAGNOSTICS_DIR}/hmm_state_occupancy_sample_laps.png", dpi=110)
plt.close()
print(f"\nSaved hmm_state_occupancy_sample_laps.png")

fig, ax = plt.subplots(figsize=(6.5, 5.5))
im = ax.imshow(model.transmat_, cmap='viridis', vmin=0, vmax=1)
ax.set_xticks(range(N_COMPONENTS)); ax.set_yticks(range(N_COMPONENTS))
ax.set_xlabel('To state'); ax.set_ylabel('From state')
ax.set_title(f'HMM (n={N_COMPONENTS}) transition matrix')
for i in range(N_COMPONENTS):
    for j in range(N_COMPONENTS):
        val = model.transmat_[i, j]
        ax.text(j, i, f"{val:.2f}", ha='center', va='center',
                color='white' if val < 0.5 else 'black', fontsize=9)
plt.colorbar(im, ax=ax, label='P(transition)')
plt.tight_layout()
plt.savefig(f"{DIAGNOSTICS_DIR}/hmm_transition_matrix_heatmap.png", dpi=110)
plt.close()
print("Saved hmm_transition_matrix_heatmap.png")

# -----------------------------------------------------------------
# HMM vs rule-based baseline cross-tab
# -----------------------------------------------------------------
ct = pd.crosstab(full['hmm_state'], full['rule_state'], normalize='index') * 100
print("\nHMM state vs rule-based label (row %):")
print(ct.round(1).to_string())
