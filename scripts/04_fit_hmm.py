"""
Fits pooled GaussianHMM driving-state models (n_components in {4, 6, 8}) on
the resampled telemetry, across ALL drivers/laps together (not per-driver),
so states are comparable across drivers for later branches.

Uses hmmlearn's native fitting loop (n_iter/tol) and its built-in min_covar
regularization against state collapse (a state's variance shrinking to ~0
mid-EM, which produces NaN log-likelihood and an invalid transition matrix -
observed on this 5-feature set at n_components>=6 with min_covar left at its
default). Since EM only finds a local optimum, this script tries multiple
random restarts (hmmlearn's own `random_state` / init) and keeps whichever
converged run has the highest log-likelihood - hmmlearn has no built-in
multi-restart selection, so that part is ours.

MODEL SELECTION: raw log-likelihood (or per-timestep log-likelihood) is NOT
a fair way to compare different n_components on its own - more states means
more free parameters, so likelihood mechanically increases (or at worst
stays flat) as n_components grows, regardless of whether the extra states
are real. This script also reports BIC (Bayesian Information Criterion),
which penalizes parameter count, so "n=8 has higher log-likelihood but a
worse (higher) BIC than n=6" is the kind of comparison that actually
supports a model-selection conclusion - "n=8 never converged across 12
restarts" (the argument used in branch1a_hmm_report.md) is a weaker,
indirect argument for the same conclusion and should be corroborated with
BIC once n=8 can be fit at all.

CAVEAT (methodology, not fixed by this script): GaussianHMM assumes
continuous-Gaussian emissions for every feature, including `brake`, which
is actually binary (0/1) - see CLAUDE.md's established data facts. This is
an accepted engineering approximation, not a "legal" continuous feature
like the other four.

SENSITIVITY CHECKS worth running before trusting a single fit:
- --covariance-type full  (default 'diag' assumes features are conditionally
  independent given the state - e.g. speed and acc_x are almost certainly
  correlated during hard braking, which 'diag' cannot represent. Only 5
  features here, so 'full' is cheap to try.)
- --min-covar 0.05  (default 0.1 is a fairly conservative variance floor
  now that features are standardized to unit variance - worth checking
  whether a smaller floor changes which states are recovered, or whether
  0.1 was silently merging two states that should be distinct.)

Usage: python3 04_fit_hmm.py <n_components> [n_restarts] [--covariance-type TYPE] [--min-covar VALUE]
  e.g. python3 04_fit_hmm.py 6 5
       python3 04_fit_hmm.py 6 5 --covariance-type full
       python3 04_fit_hmm.py 6 5 --min-covar 0.05

Inputs:
  resampled_telemetry.parquet (from 03_build_resampled_dataset.py, in PROCESSED_DIR)
Outputs:
  branch1a_feature_scaler.joblib (written once, on first run)  ->  MODELS_DIR
  candidate_models/hmm_n{N}[_covfull][_mincovarX].joblib, matching _ll.txt  ->  MODELS_DIR
"""
import sys
import os
import argparse
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM
import joblib
import warnings
warnings.filterwarnings('ignore')

PROJECT_DIR = "/Users/zhangyimeng/SportsAnalytics/f1"
PROCESSED_DIR = f"{PROJECT_DIR}/data/processed"
MODELS_DIR = f"{PROJECT_DIR}/models"
CANDIDATES_DIR = f"{MODELS_DIR}/candidate_models"
os.makedirs(CANDIDATES_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("n_components", type=int)
parser.add_argument("n_restarts", type=int, nargs="?", default=5)
parser.add_argument("--covariance-type", type=str, default="diag",
                    choices=["diag", "full", "spherical", "tied"])
parser.add_argument("--min-covar", type=float, default=0.1)
args = parser.parse_args()

n_components = args.n_components
n_restarts = args.n_restarts
covariance_type = args.covariance_type
min_covar = args.min_covar

FEATURE_COLS = ['speed', 'throttle', 'brake', 'acc_x', 'acc_y']
n_features = len(FEATURE_COLS)

# -----------------------------------------------------------------
# Feature prep (re-derives X/lengths every run - cheap relative to fitting,
# and avoids depending on separately-saved .npy intermediates going stale)
# -----------------------------------------------------------------
full = pd.read_parquet(f"{PROCESSED_DIR}/resampled_telemetry.parquet")
full = full.sort_values(['Driver', 'LapNumber', 'distance']).reset_index(drop=True)

lap_keys = full[['Driver', 'LapNumber']].drop_duplicates()
lengths = full.groupby(['Driver', 'LapNumber'], sort=False).size().values

# lengths only means what we think it means if each (Driver, LapNumber)
# group is contiguous in the sorted frame - verify before trusting it
group_id = (full['Driver'] != full['Driver'].shift()) | (full['LapNumber'] != full['LapNumber'].shift())
n_contiguous_groups = group_id.sum()
assert n_contiguous_groups == len(lap_keys), "Lap groups are not contiguous after sort - lengths array would be wrong"
assert lengths.sum() == len(full)

X_raw = full[FEATURE_COLS].values.astype(np.float64)

scaler_path = f"{MODELS_DIR}/branch1a_feature_scaler.joblib"
scaler = StandardScaler()
X = scaler.fit_transform(X_raw)
joblib.dump(scaler, scaler_path)

print(f"Feature matrix: {X.shape}, features={FEATURE_COLS}")
print(f"Sequences (laps): {len(lengths)}, total timesteps: {lengths.sum()}")


def n_free_params(n_components, n_features, covariance_type):
    """Count of free parameters in a GaussianHMM, for BIC."""
    n_startprob = n_components - 1
    n_transmat = n_components * (n_components - 1)
    n_means = n_components * n_features
    if covariance_type == 'diag':
        n_covars = n_components * n_features
    elif covariance_type == 'spherical':
        n_covars = n_components
    elif covariance_type == 'tied':
        n_covars = n_features * (n_features + 1) // 2
    elif covariance_type == 'full':
        n_covars = n_components * n_features * (n_features + 1) // 2
    else:
        raise ValueError(f"unknown covariance_type {covariance_type}")
    return n_startprob + n_transmat + n_means + n_covars


# -----------------------------------------------------------------
# Fit with multiple random restarts, using hmmlearn's own convergence
# monitor (model.monitor_.converged) and min_covar regularization -
# no manual iteration loop or mid-fit snapshotting needed.
# -----------------------------------------------------------------
print(f"\nFitting GaussianHMM n_components={n_components}, covariance_type={covariance_type}, "
      f"min_covar={min_covar}, {n_restarts} restarts...")

best_model = None
best_ll = -np.inf

for seed in range(n_restarts):
    model = GaussianHMM(
        n_components=n_components,
        covariance_type=covariance_type,
        n_iter=100,
        tol=1e-3,
        random_state=seed,
        verbose=False,
        min_covar=min_covar,
    )
    try:
        model.fit(X, lengths)
        ll = model.score(X, lengths)
        transmat_ok = np.all(np.isfinite(model.transmat_)) and np.allclose(model.transmat_.sum(axis=1), 1.0)
        valid = model.monitor_.converged and np.isfinite(ll) and transmat_ok
        print(f"  seed={seed}: ll={ll if np.isfinite(ll) else 'NaN'}, "
              f"converged={model.monitor_.converged}, valid={valid}")
    except Exception as e:
        print(f"  seed={seed}: FAILED ({e})")
        continue

    if valid and ll > best_ll:
        best_ll = ll
        best_model = model

if best_model is None:
    print(f"n_components={n_components}: ALL {n_restarts} restarts failed/diverged.")
    sys.exit(1)

k = n_free_params(n_components, n_features, covariance_type)
n_obs = len(X)
bic = -2 * best_ll + k * np.log(n_obs)
aic = -2 * best_ll + 2 * k

print(f"\nBest: n_components={n_components}, ll={best_ll:.1f}, per_timestep_ll={best_ll/len(X):.5f}")
print(f"Free parameters: {k}, BIC={bic:.1f}, AIC={aic:.1f}")
print("Lower BIC/AIC is better - compare these across n_components runs, "
      "not raw log-likelihood, since likelihood alone mechanically favors more states.")

suffix = f"n{n_components}"
if covariance_type != 'diag':
    suffix += f"_cov{covariance_type}"
if min_covar != 0.1:
    suffix += f"_mincovar{min_covar}"

joblib.dump(best_model, f"{CANDIDATES_DIR}/hmm_{suffix}.joblib")
with open(f"{CANDIDATES_DIR}/hmm_{suffix}_ll.txt", "w") as f:
    f.write(f"log_likelihood={best_ll}\nn_free_params={k}\nBIC={bic}\nAIC={aic}\n")
print(f"Saved -> {CANDIDATES_DIR}/hmm_{suffix}.joblib")

# NOTE: if this still collapses frequently at higher n_components, the
# next lever to try (in order of preference) is raising min_covar further,
# then covariance_type='spherical' (fewer free params per state), before
# reaching for manual workarounds again. See branch1a_hmm_report.md for
# the model-selection writeup (n=4 vs 6 vs 8 comparison and known
# reproducibility caveat on the n=6 restart search) - that writeup predates
# the BIC/AIC reporting added here and should be updated with BIC numbers
# once n=8 can be fit reliably enough to compute one.
