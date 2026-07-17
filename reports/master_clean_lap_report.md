# Master Clean-Lap Metadata — Miami GP 2026 Race

## Sector-time regression check (post-fix)

```
Sector1Time + Sector2Time + Sector3Time vs laptime_sum_sectortimes
Comparable rows: 1016
Tolerance: 0.05s
Rows exceeding tolerance: 0
Max deviation found: 0.000000s
Result: PASS
```
```
Cross-check: LapTime_in_seconds vs laptime_sum_sectortimes
Rows exceeding tolerance: 0, max deviation: 0.000000s
Result: PASS
```

## Weather merge (backward, on LapStartTime, tolerance=90s)

```
direction='backward' ensures each lap only gets a weather reading at-or-before its start time, never a future one - 'nearest' was tried and rejected earlier in this project for leaking future weather into early laps.
```
```
Total laps: 1040, matched weather: 1040, unmatched: 0
```

## Derived Safety Car window(s) from track_status.csv

```
SC windows found: [('0 days 01:05:34.079000', '0 days 01:18:52.924000')]
```

## Explicit boolean flag counts

```
is_green:        852 / 1040
is_pit_lap:      47 / 1040
is_accurate:     858 / 1040
is_deleted:      13 / 1040
is_sc_period:    121 / 1040
is_incident_lap: 2 / 1040
```

## Before/after clean-lap counts

```
Earlier working estimates:
  TrackStatus=='1' alone: 852
  clean_telemetry_lap (green & not-pit & accurate, Deleted allowed) from prior pass: 791

Recomputed on corrected master table:
  clean_pace_lap:      783 / 1040
  clean_telemetry_lap: 791 / 1040
```

### Laps newly excluded by SC-window / incident flags

```
Count: 0
```
```
None - GAS's and LAW's incident laps, and all SC-period laps, were already excluded by is_green (TrackStatus non-'1' during the SC period) and/or is_accurate (incomplete final laps) before these two flags were even applied. Both flags are still kept as their own explicit columns since they document *why* independently of the other filters.
```
```

Saved -> /Users/zhangyimeng/SportsAnalytics/f1/data/processed/laps_weather_merged.csv (1040 rows x 40 cols)
```
```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/data/processed/master_laps_metadata.csv (1040 rows x 49 cols)
```