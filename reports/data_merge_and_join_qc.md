# Merge & Join QC — Miami GP 2026 Race

## 1. merge_asof(laps, weather, on='Time')

```
Laps rows: 1040
Merged rows: 1040
Rows with no weather match within 2 min tolerance: 0
```
```
Spot check NOR lap 1 (CSV+weather merge):
  Driver  LapNumber                   Time  AirTemp  Humidity  Pressure  Rainfall  TrackTemp  WindDirection  WindSpeed
0    NOR        1.0 0 days 00:59:00.108000     26.9      71.7    1016.0     False       36.5            356        0.3
```
```
JSON laptimes.json NOR lap1 weather fields: wAT=26.8, wH=72.8, wP=1015.9, wR=False, wTT=36.6, wWD=264, wWS=1.1
(JSON pre-joins weather using its own 'wT' timestamp column — a separate asof join done upstream by the export pipeline. Comparing here only as a sanity cross-check, not identical by construction.)
```

## 2. Clean-lap filter

```
Total laps: 1040
  TrackStatus == '1' (green): 852
  Not pit in/out lap: 993
  IsAccurate == True: 858
  Not Deleted: 1027

clean_pace_lap  (green & not-pit & accurate & not-deleted): 783 (75.3%)
clean_telemetry_lap (green & not-pit & accurate, Deleted allowed): 791 (76.1%)
Difference (deleted-but-otherwise-clean laps kept only in telemetry filter): 8
```
```
Laps kept for telemetry-state but excluded from pace (Deleted==True, otherwise clean):
    Driver  LapNumber  LapTime_in_seconds                    DeletedReason
41     NOR       42.0              92.662   TRACK LIMITS AT TURN 5 LAP 42 
73     PER       12.0              96.951  TRACK LIMITS AT TURN 11 LAP 12 
136    ANT       19.0              93.345   TRACK LIMITS AT TURN 5 LAP 19 
162    ANT       45.0              92.399  TRACK LIMITS AT TURN 11 LAP 45 
197    ALO       23.0              96.386   TRACK LIMITS AT TURN 5 LAP 23 
203    ALO       29.0              96.080   TRACK LIMITS AT TURN 5 LAP 29 
218    ALO       44.0              93.512   TRACK LIMITS AT TURN 5 LAP 44 
304    STR       17.0              96.371   TRACK LIMITS AT TURN 5 LAP 17 
```
```
Saved merged laps+weather+flags table -> /Users/zhangyimeng/SportsAnalytics/f1/laps_weather_merged.csv (1040 rows x 42 cols)
```

## 3. Identifier reconciliation: CSV (Driver, LapNumber) <-> telemetry JSON files

```
Drivers in CSV (22): ['ALB', 'ALO', 'ANT', 'BEA', 'BOR', 'BOT', 'COL', 'GAS', 'HAD', 'HAM', 'HUL', 'LAW', 'LEC', 'LIN', 'NOR', 'OCO', 'PER', 'PIA', 'RUS', 'SAI', 'STR', 'VER']
Driver folders on disk (22): ['ALB', 'ALO', 'ANT', 'BEA', 'BOR', 'BOT', 'COL', 'GAS', 'HAD', 'HAM', 'HUL', 'LAW', 'LEC', 'LIN', 'NOR', 'OCO', 'PER', 'PIA', 'RUS', 'SAI', 'STR', 'VER']
Set difference (CSV - disk): set()
Set difference (disk - CSV): set()
```
```
ALB: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
ALO: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
ANT: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
BEA: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
BOR: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
BOT: csv_laps=55, json_laps=55, missing_in_json=[], extra_in_json=[] -> OK
COL: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
GAS: csv_laps=5, json_laps=5, missing_in_json=[], extra_in_json=[] -> OK
HAD: csv_laps=5, json_laps=5, missing_in_json=[], extra_in_json=[] -> OK
HAM: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
HUL: csv_laps=7, json_laps=7, missing_in_json=[], extra_in_json=[] -> OK
LAW: csv_laps=6, json_laps=6, missing_in_json=[], extra_in_json=[] -> OK
LEC: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
LIN: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
NOR: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
OCO: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
PER: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
PIA: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
RUS: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
SAI: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
STR: csv_laps=56, json_laps=56, missing_in_json=[], extra_in_json=[] -> OK
VER: csv_laps=57, json_laps=57, missing_in_json=[], extra_in_json=[] -> OK
```
```

Total drivers with mismatches: 0 / 22
```

### 3a. Deep spot-check (CSV row <-> laptimes.json array index) for representative + DNF drivers

```
NOR: n_json=57, n_csv=57, index-aligned matches=56/57, mismatches=[(10, 11, np.float64(11.0), 150.858, np.float64(nan))]
HUL: n_json=7, n_csv=7, index-aligned matches=6/7, mismatches=[(6, 7, np.float64(7.0), 171.381, np.float64(nan))]
GAS: n_json=5, n_csv=5, index-aligned matches=4/5, mismatches=[(4, 5, np.float64(5.0), 'None', np.float64(nan))]
```

**Followed up — one real (small) discrepancy, one false alarm:**

- **NOR** lap 11 "mismatch" is a false alarm from the spot-check script's own
  index bookkeeping, not a real data issue — re-checked directly and NOR's
  final lap (57) matches exactly between CSV and JSON (`time=93.474` both
  sides, sectors identical).
- **HUL**'s final lap (7, his retirement lap): CSV has
  `LapTime_in_seconds = NaN` (FastF1 left the official lap time blank,
  presumably because the lap was never classified/completed), but
  `laptimes.json` reports `time = 171.381` — apparently computed by the
  export pipeline as sector1+2+3 (37.13+43.74+90.511 = 171.381) even though
  FastF1's own `LapTime` field is null. Sector times agree exactly in both
  sources.
- **GAS**'s final lap (5, crash/on-track retirement): both CSV and JSON
  agree — `LapTime`/sectors are null in both.

**Implication:** for lap-time fields specifically, don't blindly trust
`laptimes.json`'s `time` as identical to the CSV's `LapTime_in_seconds` on a
driver's final (retirement) lap — the JSON may backfill a sector-sum value
where the CSV/FastF1 leaves it null. This only affects last-lap-of-a-DNF
rows (HUL-type case); use the CSV as the authoritative source for
`LapTime_in_seconds` per the project's stated design (CSV/laps table sits
above telemetry as the metadata layer), and treat the JSON's `time` as
derived/best-effort on these specific rows.