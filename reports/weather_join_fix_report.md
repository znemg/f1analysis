# Weather Join Fix — Miami GP 2026 Race

## Weather join fix: nearest -> backward, joined on LapStartTime

```
Using LapStartTime (start of lap) as the join timestamp rather than Time (lap completion), so the weather reading reflects conditions when the lap began, not when it ended. direction='backward' with tolerance=90s ensures we only ever pull a weather sample at-or-before the join time, never a future one.
```

### Match-rate comparison

```
Total laps: 1040
OLD (nearest, joined on Time/completion, tol=2min): matched=1040, unmatched=0
NEW (backward, joined on LapStartTime, tol=90s):    matched=1040, unmatched=0
```

### Rows that lost their weather match under backward/LapStartTime (had only a future reading before)

```
None — every lap that had a match under the old logic also matched under the new logic.
```

### Rows that gained a match under new logic (sanity check, should typically be empty or explainable)

```
Count: 0
```

### Rows still unmatched under backward/LapStartTime (no weather sample yet at lap start)

```
Count: 0
```

### Output

```
Overwrote /Users/zhangyimeng/SportsAnalytics/f1/laps_weather_merged.csv — shape 1040 rows x 42 cols
Join key: LapStartTime (lap start), direction='backward', tolerance=90s
clean_pace_lap: 783 True
clean_telemetry_lap: 791 True
```