"""
Builds the authoritative laps+weather+clean-lap-flags table from the raw
TracingInsights CSV exports and the FastF1 track_status pull.

IMPORTANT: Sector1Time/Sector2Time/Sector3Time in the raw laps CSV are
plain float SECONDS, not "0 days HH:MM:SS.ffffff" strings. Do not add them
to the timedelta-parsing list below - doing so silently truncates them into
near-zero nanosecond values with no error thrown (a real bug caught in this
project). A regression check against laptime_sum_sectortimes runs below
every time this script executes.

Inputs (RAW_DIR):
  2026-Miami Grand Prix-Race.csv, 2026-Miami Grand Prix-Race-weather.csv
  track_status.csv (from 01_fetch_fastf1.py)
Outputs:
  laps_weather_merged.csv, master_laps_metadata.csv  ->  PROCESSED_DIR
  master_clean_lap_report.md                         ->  REPORTS_DIR
"""
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 200)

PROJECT_DIR = "/Users/zhangyimeng/SportsAnalytics/f1"
RAW_DIR = f"{PROJECT_DIR}/data/raw"
PROCESSED_DIR = f"{PROJECT_DIR}/data/processed"
REPORTS_DIR = f"{PROJECT_DIR}/reports"
LAPS_PATH = f"{RAW_DIR}/2026-Miami Grand Prix-Race.csv"
WEATHER_PATH = f"{RAW_DIR}/2026-Miami Grand Prix-Race-weather.csv"

out = []
def s(title, level=2):
    out.append(f"\n{'#'*level} {title}\n")
def code(txt):
    out.append("```")
    out.append(txt)
    out.append("```")

# -----------------------------------------------------------------
# Load raw CSVs
# -----------------------------------------------------------------
laps = pd.read_csv(LAPS_PATH, index_col=0)
weather = pd.read_csv(WEATHER_PATH, index_col=0)

# Columns that are genuinely "0 days HH:MM:SS.ffffff" string-encoded
# timedeltas. Sector1Time/Sector2Time/Sector3Time are excluded on purpose -
# see module docstring.
timedelta_cols = ['Time', 'LapTime', 'Sector1SessionTime', 'Sector2SessionTime',
                  'Sector3SessionTime', 'PitOutTime', 'PitInTime', 'LapStartTime']
for col in timedelta_cols:
    laps[col] = pd.to_timedelta(laps[col], errors='coerce')
laps['LapStartDate'] = pd.to_datetime(laps['LapStartDate'], errors='coerce')
weather['Time'] = pd.to_timedelta(weather['Time'], errors='coerce')

s("Sector-time regression check (post-fix)", 2)
sector_sum = laps['Sector1Time'] + laps['Sector2Time'] + laps['Sector3Time']
comparable = laps['laptime_sum_sectortimes'].notna()
diff = (sector_sum - laps['laptime_sum_sectortimes']).abs()
tol = 0.05
bad = laps[comparable & (diff > tol)]
code(f"Sector1Time + Sector2Time + Sector3Time vs laptime_sum_sectortimes\n"
     f"Comparable rows: {comparable.sum()}\n"
     f"Tolerance: {tol}s\n"
     f"Rows exceeding tolerance: {len(bad)}\n"
     f"Max deviation found: {diff[comparable].max():.6f}s\n"
     f"Result: {'PASS' if len(bad)==0 else 'FAIL'}")
if len(bad) > 0:
    raise ValueError(
        f"Sector-time regression check FAILED: {len(bad)} rows exceed "
        f"{tol}s tolerance. Do not proceed - investigate before trusting "
        f"downstream output. See rows:\n{bad[['Driver','LapNumber','Sector1Time','Sector2Time','Sector3Time','laptime_sum_sectortimes']]}"
    )

diff2 = (laps['LapTime_in_seconds'] - laps['laptime_sum_sectortimes']).abs()
comparable2 = laps['laptime_sum_sectortimes'].notna()
bad2 = laps[comparable2 & (diff2 > tol)]
code(f"Cross-check: LapTime_in_seconds vs laptime_sum_sectortimes\n"
     f"Rows exceeding tolerance: {len(bad2)}, max deviation: {diff2[comparable2].max():.6f}s\n"
     f"Result: {'PASS' if len(bad2)==0 else 'FAIL'}")

# -----------------------------------------------------------------
# merge_asof laps + weather, backward direction, joined on LapStartTime
# -----------------------------------------------------------------
s("Weather merge (backward, on LapStartTime, tolerance=90s)", 2)
code("direction='backward' ensures each lap only gets a weather reading "
     "at-or-before its start time, never a future one - 'nearest' was "
     "tried and rejected earlier in this project for leaking future "
     "weather into early laps.")

weather_sorted = weather.sort_values('Time').reset_index(drop=True)

laps_sorted_start = laps.sort_values('LapStartTime').reset_index(drop=False).rename(columns={'index': 'orig_index'})
laps_sorted_start = laps_sorted_start.drop(columns=['Time']).rename(columns={'LapStartTime': 'Time'})

merged = pd.merge_asof(
    laps_sorted_start, weather_sorted,
    on='Time', direction='backward',
    tolerance=pd.Timedelta('90s'),
)
merged = merged.rename(columns={'Time': 'LapStartTime'})
merged = merged.set_index('orig_index').sort_index()
merged.index.name = None
merged.insert(0, 'Time', laps['Time'])

n_matched = merged['AirTemp'].notna().sum()
code(f"Total laps: {len(merged)}, matched weather: {n_matched}, unmatched: {len(merged)-n_matched}")

# -----------------------------------------------------------------
# track_status.csv - derive SC window(s)
# -----------------------------------------------------------------
track_status = pd.read_csv(f"{RAW_DIR}/track_status.csv", index_col=0)
track_status['Time'] = pd.to_timedelta(track_status['Time'], errors='coerce')
track_status = track_status.sort_values('Time').reset_index(drop=True)

sc_windows = []
sc_start = None
for i, row in track_status.iterrows():
    if row['Status'] == 4:
        sc_start = row['Time']
    elif row['Status'] == 1 and sc_start is not None:
        sc_windows.append((sc_start, row['Time']))
        sc_start = None
if sc_start is not None:
    sc_windows.append((sc_start, track_status['Time'].max()))

s("Derived Safety Car window(s) from track_status.csv", 2)
code(f"SC windows found: {[(str(a), str(b)) for a,b in sc_windows]}")

# -----------------------------------------------------------------
# Boolean flags
# -----------------------------------------------------------------
df = merged.copy()

df['is_green'] = df['TrackStatus'].astype(str) == '1'
df['is_pit_lap'] = df['PitOutTime'].notna() | df['PitInTime'].notna()
df['is_accurate'] = df['IsAccurate'] == True
df['is_deleted'] = df['Deleted'] == True

def overlaps_sc(row):
    lap_start, lap_end = row['LapStartTime'], row['Time']
    if pd.isna(lap_start) or pd.isna(lap_end):
        return False
    for sc_s, sc_e in sc_windows:
        if lap_start <= sc_e and lap_end >= sc_s:
            return True
    return False

df['is_sc_period'] = df.apply(overlaps_sc, axis=1)

# is_incident_lap: confirmed Turn 17 collision between GAS and LAW.
# NOTE: race_control_messages.csv's 'Lap' column is the RACE LEADER's lap
# at message time, not GAS/LAW's own lap count - both had already retired
# well before the field reached the RCM-reported laps 8-9. The incident lap
# for each driver is identified as their own final (uncompleted) lap.
incident_drivers = {
    'GAS': "Turn 17 collision (RCM: car 10 GAS noted causing a collision, "
           "stewards investigation 17:17:00-17:19:45; GAS's own final lap "
           "never completed, matching this window). Note: RCM 'Lap' column "
           "(8-9) is the race leader's lap, not GAS's own lap count (GAS had "
           "already retired after his own lap 5).",
    'LAW': "Turn 17 collision (RCM: cars 30 LAW + 10 GAS causing a "
           "collision, stewards update 17:19:18; LAW's own final lap never "
           "completed, matching this window). Note: RCM 'Lap' column (8-9) "
           "is the race leader's lap, not LAW's own lap count (LAW had "
           "already retired after his own lap 6).",
}
df['is_incident_lap'] = False
df['incident_note'] = None
for drv, note in incident_drivers.items():
    drv_laps = df[df['Driver'] == drv]
    final_lap_mask = (df['Driver'] == drv) & (df['LapNumber'] == drv_laps['LapNumber'].max())
    df.loc[final_lap_mask, 'is_incident_lap'] = True
    df.loc[final_lap_mask, 'incident_note'] = note

s("Explicit boolean flag counts", 2)
code(f"is_green:        {df['is_green'].sum()} / {len(df)}\n"
     f"is_pit_lap:      {df['is_pit_lap'].sum()} / {len(df)}\n"
     f"is_accurate:     {df['is_accurate'].sum()} / {len(df)}\n"
     f"is_deleted:      {df['is_deleted'].sum()} / {len(df)}\n"
     f"is_sc_period:    {df['is_sc_period'].sum()} / {len(df)}\n"
     f"is_incident_lap: {df['is_incident_lap'].sum()} / {len(df)}")

# -----------------------------------------------------------------
# Combined flags
# -----------------------------------------------------------------
df['clean_pace_lap'] = (
    df['is_green'] & ~df['is_pit_lap'] & df['is_accurate'] &
    ~df['is_deleted'] & ~df['is_sc_period'] & ~df['is_incident_lap']
)
df['clean_telemetry_lap'] = (
    df['is_green'] & ~df['is_pit_lap'] & df['is_accurate'] &
    ~df['is_sc_period'] & ~df['is_incident_lap']
)

s("Before/after clean-lap counts", 2)
code(f"Earlier working estimates:\n"
     f"  TrackStatus=='1' alone: 852\n"
     f"  clean_telemetry_lap (green & not-pit & accurate, Deleted allowed) from prior pass: 791\n"
     f"\n"
     f"Recomputed on corrected master table:\n"
     f"  clean_pace_lap:      {df['clean_pace_lap'].sum()} / {len(df)}\n"
     f"  clean_telemetry_lap: {df['clean_telemetry_lap'].sum()} / {len(df)}")

prior_telemetry = df['is_green'] & ~df['is_pit_lap'] & df['is_accurate']
newly_excluded = df[prior_telemetry & ~df['clean_telemetry_lap']]
s("Laps newly excluded by SC-window / incident flags", 3)
code(f"Count: {len(newly_excluded)}")
if len(newly_excluded):
    code(newly_excluded[['Driver','LapNumber','is_sc_period','is_incident_lap','incident_note']].sort_values(['Driver','LapNumber']).to_string())
else:
    code("None - GAS's and LAW's incident laps, and all SC-period laps, were "
         "already excluded by is_green (TrackStatus non-'1' during the SC "
         "period) and/or is_accurate (incomplete final laps) before these "
         "two flags were even applied. Both flags are still kept as their "
         "own explicit columns since they document *why* independently of "
         "the other filters.")

# -----------------------------------------------------------------
# Save
# -----------------------------------------------------------------
merged_out_path = f"{PROCESSED_DIR}/laps_weather_merged.csv"
merged.to_csv(merged_out_path)
code(f"\nSaved -> {merged_out_path} ({merged.shape[0]} rows x {merged.shape[1]} cols)")

master_out_path = f"{PROCESSED_DIR}/master_laps_metadata.csv"
df.to_csv(master_out_path)
code(f"Saved -> {master_out_path} ({df.shape[0]} rows x {df.shape[1]} cols)")

with open(f"{REPORTS_DIR}/master_clean_lap_report.md", "w") as f:
    f.write("# Master Clean-Lap Metadata — Miami GP 2026 Race\n")
    f.write("\n".join(out))

print("Done.")
print("Sector-time regression check bad rows:", len(bad))
print("clean_pace_lap:", df['clean_pace_lap'].sum())
print("clean_telemetry_lap:", df['clean_telemetry_lap'].sum())
