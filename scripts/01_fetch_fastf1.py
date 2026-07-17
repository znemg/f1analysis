"""
Pulls supplementary session tables from the FastF1 API that aren't covered
by the TracingInsights CSV/JSON exports: official results (DNF status),
race control messages (SC/VSC/incidents), track status, circuit info, and
event metadata.

Inputs: Miami_Race_cor.json (in RAW_DIR, for the circuit-info cross-check).
Outputs (written to RAW_DIR / REPORTS_DIR):
  session_results.csv, race_control_messages.csv, track_status.csv,
  circuit_info_fastf1.json, event_info.json  ->  RAW_DIR
  fastf1_api_pull_summary.md                 ->  REPORTS_DIR
"""
import fastf1
import pandas as pd
import json
import os

pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 200)

PROJECT_DIR = "/Users/zhangyimeng/SportsAnalytics/f1"
RAW_DIR = f"{PROJECT_DIR}/data/raw"
REPORTS_DIR = f"{PROJECT_DIR}/reports"
CACHE_DIR = os.path.expanduser("~/Library/Caches/fastf1")

fastf1.Cache.enable_cache(CACHE_DIR)

print("Loading session...")
session = fastf1.get_session(2026, 'Miami', 'R')
session.load()
print("Loaded.")

out = []
def s(title, level=2):
    out.append(f"\n{'#'*level} {title}\n")
def code(txt):
    out.append("```")
    out.append(txt)
    out.append("```")

# -----------------------------------------------------------------
# session.results
# -----------------------------------------------------------------
s("session.results", 2)
results = session.results
results_path = os.path.join(RAW_DIR, "session_results.csv")
results.to_csv(results_path)
code(f"Saved -> {results_path} ({results.shape[0]} rows x {results.shape[1]} cols)\n"
     f"Columns: {list(results.columns)}")

dnf_drivers = ['HUL', 'LAW', 'GAS', 'HAD']
s("DNF driver Status check (HUL, LAW, GAS, HAD)", 3)
if 'Abbreviation' in results.columns:
    subset = results[results['Abbreviation'].isin(dnf_drivers)]
    cols_to_show = [c for c in ['Abbreviation', 'TeamName', 'Position', 'ClassifiedPosition',
                                  'GridPosition', 'Status', 'Points', 'Time'] if c in subset.columns]
    code(subset[cols_to_show].to_string())
else:
    code(f"Results columns available: {list(results.columns)}")
    code(results.to_string())

# NOTE: session.results['Status'] is generic ("Retired") for all DNFs on
# this race - it does NOT give a differentiated cause. The actual cause
# (e.g. GAS/LAW's shared Turn 17 collision) has to be cross-referenced from
# race_control_messages.csv by filtering each driver's "(ABBR)" tag - see
# fastf1_api_pull_summary.md for that analysis, done separately from this
# fetch step.

# -----------------------------------------------------------------
# session.race_control_messages
# -----------------------------------------------------------------
s("session.race_control_messages", 2)
try:
    rcm = session.race_control_messages
    rcm_path = os.path.join(RAW_DIR, "race_control_messages.csv")
    rcm.to_csv(rcm_path)
    code(f"Saved -> {rcm_path} ({rcm.shape[0]} rows x {rcm.shape[1]} cols)\n"
         f"Columns: {list(rcm.columns)}")

    s("SC/VSC related messages", 3)
    text_col = 'Message' if 'Message' in rcm.columns else None
    if text_col:
        sc_vsc = rcm[rcm[text_col].astype(str).str.contains('SAFETY CAR|VSC|VIRTUAL SAFETY', case=False, na=False)]
        code(sc_vsc.to_string())
    else:
        code("No 'Message' column found; full RCM dump above in CSV.")
except Exception as e:
    code(f"ERROR pulling race_control_messages: {e}")
    rcm = None

# -----------------------------------------------------------------
# session.track_status
# -----------------------------------------------------------------
s("session.track_status", 2)
try:
    track_status = session.track_status
    ts_path = os.path.join(RAW_DIR, "track_status.csv")
    track_status.to_csv(ts_path)
    code(f"Saved -> {ts_path} ({track_status.shape[0]} rows x {track_status.shape[1]} cols)\n"
         f"Columns: {list(track_status.columns)}")
    code(track_status.to_string())
except Exception as e:
    code(f"ERROR pulling track_status: {e}")
    track_status = None

# -----------------------------------------------------------------
# session.get_circuit_info()
# -----------------------------------------------------------------
s("session.get_circuit_info()", 2)
try:
    circuit_info = session.get_circuit_info()
    circuit_dict = {
        "corners": circuit_info.corners.to_dict(orient='records') if hasattr(circuit_info, 'corners') else None,
        "marshal_lights": circuit_info.marshal_lights.to_dict(orient='records') if hasattr(circuit_info, 'marshal_lights') else None,
        "marshal_sectors": circuit_info.marshal_sectors.to_dict(orient='records') if hasattr(circuit_info, 'marshal_sectors') else None,
        "rotation": circuit_info.rotation if hasattr(circuit_info, 'rotation') else None,
    }
    circuit_path = os.path.join(RAW_DIR, "circuit_info_fastf1.json")
    with open(circuit_path, 'w') as f:
        json.dump(circuit_dict, f, indent=2, default=str)
    code(f"Saved -> {circuit_path}\n"
         f"Corners: {len(circuit_dict['corners']) if circuit_dict['corners'] else 0}\n"
         f"Marshal lights: {len(circuit_dict['marshal_lights']) if circuit_dict['marshal_lights'] else 0}\n"
         f"Marshal sectors: {len(circuit_dict['marshal_sectors']) if circuit_dict['marshal_sectors'] else 0}\n"
         f"Rotation: {circuit_dict['rotation']}")

    # Cross-check against existing corners.json (Miami_Race_cor.json)
    existing_corners_path = os.path.join(RAW_DIR, "Miami_Race_cor.json")
    if os.path.exists(existing_corners_path):
        with open(existing_corners_path) as f:
            existing = json.load(f)
        existing_corners = existing.get('corners', [])
        existing_rotation = existing.get('rotation')
        s("Cross-check vs existing Miami_Race_cor.json", 3)
        code(f"FastF1 corner count: {len(circuit_dict['corners']) if circuit_dict['corners'] else 0}\n"
             f"Existing (TracingInsights) corner count: {len(existing_corners)}\n"
             f"FastF1 rotation: {circuit_dict['rotation']}\n"
             f"Existing rotation: {existing_rotation}")
        if circuit_dict['corners'] and existing_corners and len(circuit_dict['corners']) == len(existing_corners):
            import math
            diffs = []
            for i, (a, b) in enumerate(zip(circuit_dict['corners'], existing_corners)):
                ax, ay = a.get('X'), a.get('Y')
                bx, by = b.get('X'), b.get('Y')
                if ax is not None and bx is not None:
                    d = math.hypot(ax-bx, ay-by)
                    diffs.append(d)
            if diffs:
                code(f"Per-corner X/Y distance (FastF1 vs existing), n={len(diffs)}: "
                     f"max={max(diffs):.2f}, mean={sum(diffs)/len(diffs):.2f}")
except Exception as e:
    code(f"ERROR pulling circuit_info: {e}")
    circuit_info = None

# -----------------------------------------------------------------
# session.event
# -----------------------------------------------------------------
s("session.event", 2)
try:
    event = session.event
    event_dict = event.to_dict() if hasattr(event, 'to_dict') else dict(event)
    event_path = os.path.join(RAW_DIR, "event_info.json")
    with open(event_path, 'w') as f:
        json.dump(event_dict, f, indent=2, default=str)
    code(f"Saved -> {event_path}")
    code(json.dumps(event_dict, indent=2, default=str))
except Exception as e:
    code(f"ERROR pulling event info: {e}")

with open(os.path.join(REPORTS_DIR, "fastf1_api_pull_summary.md"), "w") as f:
    f.write("# FastF1 API Pull Summary — Miami GP 2026 Race\n")
    f.write("\n".join(out))

print("Done. Wrote fastf1_api_pull_summary.md")
