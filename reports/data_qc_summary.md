# Data QC Summary — Miami GP 2026 Race

## 1. Dtype and parsing check

```
Time: raw NaN=0, parsed NaT=0, OK - matches
LapTime: raw NaN=7, parsed NaT=7, OK - matches
Sector1Time: raw NaN=24, parsed NaT=24, OK - matches
Sector2Time: raw NaN=2, parsed NaT=2, OK - matches
Sector3Time: raw NaN=2, parsed NaT=2, OK - matches
Sector1SessionTime: raw NaN=27, parsed NaT=27, OK - matches
Sector2SessionTime: raw NaN=2, parsed NaT=2, OK - matches
Sector3SessionTime: raw NaN=2, parsed NaT=2, OK - matches
PitOutTime: raw NaN=1017, parsed NaT=1017, OK - matches
PitInTime: raw NaN=1016, parsed NaT=1016, OK - matches
LapStartTime: raw NaN=0, parsed NaT=0, OK - matches
LapStartDate: raw NaN=0, parsed NaT=0, OK - matches
[weather] Time: parsed NaT=0
```

## 2. Missingness


### 2a. Overall NaN counts per column (laps)

```
Time                          0
Driver                        0
DriverNumber                  0
LapTime                       7
LapNumber                     0
Stint                         0
PitOutTime                 1017
PitInTime                  1016
Sector1Time                  24
Sector2Time                   2
Sector3Time                   2
Sector1SessionTime           27
Sector2SessionTime            2
Sector3SessionTime            2
SpeedI1                       2
SpeedI2                       2
SpeedFL                      26
SpeedST                       2
IsPersonalBest                2
Compound                      0
TyreLife                      0
FreshTyre                     0
Team                          0
LapStartTime                  0
LapStartDate                  0
TrackStatus                   0
Position                      2
Deleted                       0
DeletedReason              1027
FastF1Generated               0
IsAccurate                    0
LapTime_in_seconds            7
laptime_sum_sectortimes      24
```

### 2b. Overall NaN counts per column (weather)

```
Time             0
AirTemp          0
Humidity         0
Pressure         0
Rainfall         0
TrackTemp        0
WindDirection    0
WindSpeed        0
```

### 2c. PitOutTime / PitInTime pattern check

```
Non-null PitOutTime (out-laps): 23
Non-null PitInTime (in-laps): 24
Total laps: 1040
```
```
Out-laps (PitOutTime notna) that do NOT coincide with a stint change (excluding each driver's first lap): 0
```
```
In-laps (PitInTime notna) where next lap's Stint did NOT change (excluding each driver's last lap): 0
```

### 2d. DeletedReason vs Deleted pattern

```
Deleted==True count: 13
DeletedReason notna count: 13
Rows where Deleted/DeletedReason presence disagree: 0
```

### 2e. Sector time missingness clustering

```
Sector1Time: total missing=24, missing on LapNumber==1: 22, missing with TrackStatus != '1' (not all-green): 2
```
```
TrackStatus
1      22
124     2
```
```
Sector2Time: total missing=2, missing on LapNumber==1: 0, missing with TrackStatus != '1' (not all-green): 2
```
```
TrackStatus
124    2
```
```
Sector3Time: total missing=2, missing on LapNumber==1: 0, missing with TrackStatus != '1' (not all-green): 2
```
```
TrackStatus
124    2
```

## 3. Categorical / discrete columns


### value_counts: Driver

```
Driver
NOR    57
PIA    57
ANT    57
RUS    57
LEC    57
SAI    57
ALB    57
VER    57
HAM    57
COL    57
LIN    56
BOR    56
OCO    56
STR    56
ALO    56
PER    56
BEA    56
BOT    55
HUL     7
LAW     6
GAS     5
HAD     5
```

### value_counts: Team

```
Team
McLaren            114
Mercedes           114
Ferrari            114
Williams           114
Aston Martin       112
Haas F1 Team       112
Cadillac           111
Audi                63
Alpine              62
Red Bull Racing     62
Racing Bulls        62
```

### value_counts: Compound

```
Compound
MEDIUM    507
HARD      468
SOFT       65
```

### value_counts: TrackStatus

```
TrackStatus
1      852
4       81
12      66
41      18
24      12
124     10
21       1
```

### value_counts: Position

```
Position
3.0     57
2.0     57
1.0     57
6.0     57
7.0     57
8.0     57
9.0     57
10.0    57
5.0     57
4.0     57
16.0    56
15.0    56
13.0    56
14.0    56
17.0    56
11.0    56
12.0    56
18.0    55
19.0     7
20.0     6
22.0     4
21.0     4
nan      2
```

### value_counts: IsPersonalBest

```
IsPersonalBest
False    931
True     107
nan        2
```

### value_counts: FreshTyre

```
FreshTyre
True     999
False     41
```

### value_counts: Deleted

```
Deleted
False    1027
True       13
```

### value_counts: IsAccurate

```
IsAccurate
True     858
False    182
```

### value_counts: FastF1Generated

```
FastF1Generated
False    1038
True        2
```

### Multi-character TrackStatus codes (multiple status changes within one lap)

```
Count of laps with multi-char TrackStatus: 107
```
```
TrackStatus
12     66
41     18
24     12
124    10
21      1
```

## 4. Numeric distributions


### describe: LapTime_in_seconds

```
count    1033.000000
mean       99.835295
std        13.880537
min        91.869000
25%        93.612000
50%        94.720000
75%        96.582000
max       149.958000
```

### describe: SpeedI1

```
count    1038.000000
mean      201.165703
std        27.282187
min        84.000000
25%       207.000000
50%       210.000000
75%       212.000000
max       218.000000
```

### describe: SpeedI2

```
count    1038.000000
mean      175.225434
std        27.882645
min        50.000000
25%       182.000000
50%       184.000000
75%       186.000000
max       191.000000
```

### describe: SpeedFL

```
count    1014.000000
mean      269.492110
std        19.079183
min        83.000000
25%       266.000000
50%       275.000000
75%       280.000000
max       291.000000
```

### describe: SpeedST

```
count    1038.000000
mean      286.716763
std        61.897236
min        38.000000
25%       295.000000
50%       308.000000
75%       314.000000
max       334.000000
```

### describe: TyreLife

```
count    1040.000000
mean       14.949038
std         9.589771
min         1.000000
25%         7.000000
50%        14.000000
75%        22.000000
max        51.000000
```

### Speed plausibility (50-350 km/h expected)

```
SpeedI1: values outside [50,350]: 0 (min=84.0, max=218.0)
```
```
SpeedI2: values outside [50,350]: 0 (min=50.0, max=191.0)
```
```
SpeedFL: values outside [50,350]: 0 (min=83.0, max=291.0)
```
```
SpeedST: values outside [50,350]: 10 (min=38.0, max=334.0)
```

**Investigated — not a data error.** All 10 low `SpeedST` readings (38-48 km/h)
occur on **LapNumber == 11** for 10 different drivers (PER, ALO, STR, VER,
OCO, LIN, BOR, SAI, BOT, BEA), and all 10 rows have `TrackStatus == 41`
(status codes 4 = Safety Car + 1 = Green, i.e. a lap that transitioned
through an SC period). Slow speed-trap readings under Safety Car are
physically expected, not corrupted data. Recommend filtering on
`TrackStatus` (or requiring `TrackStatus == '1'`/`IsAccurate == True`) rather
than a hard speed floor when building "green flag pace" features.

### LapTime_in_seconds outliers (possible in/out laps)

```
IQR bounds: Q1=93.61, Q3=96.58, upper fence=101.04
Laps above upper fence: 153
Of these, laps that are out-laps (PitOutTime notna): 23
Of these, laps that are in-laps (PitInTime notna): 8
Of these, laps under non-green TrackStatus: 111
```

## 5. Internal consistency checks


### 5a. LapTime_in_seconds vs laptime_sum_sectortimes

```
Rows with both values present, tolerance=0.05s: total comparable rows=1016, diverging beyond tolerance: 0
```
```
Rows missing laptime_sum_sectortimes (no sector sum available): 24
```

### 5b. Stint monotonic increase with pit transitions per driver

```
Drivers where Stint does not monotonically increase over LapNumber: None
```

### 5c. Speed plausibility already covered above in section 4


## 6. Grouped sanity checks (per-driver lap counts & sequencing)

```
ALB: n_laps=57, lap range=(1,57), missing lap numbers within range: []
ALO: n_laps=56, lap range=(1,56), missing lap numbers within range: []
ANT: n_laps=57, lap range=(1,57), missing lap numbers within range: []
BEA: n_laps=56, lap range=(1,56), missing lap numbers within range: []
BOR: n_laps=56, lap range=(1,56), missing lap numbers within range: []
BOT: n_laps=55, lap range=(1,55), missing lap numbers within range: []
COL: n_laps=57, lap range=(1,57), missing lap numbers within range: []
GAS: n_laps=5, lap range=(1,5), missing lap numbers within range: []
HAD: n_laps=5, lap range=(1,5), missing lap numbers within range: []
HAM: n_laps=57, lap range=(1,57), missing lap numbers within range: []
HUL: n_laps=7, lap range=(1,7), missing lap numbers within range: []
LAW: n_laps=6, lap range=(1,6), missing lap numbers within range: []
LEC: n_laps=57, lap range=(1,57), missing lap numbers within range: []
LIN: n_laps=56, lap range=(1,56), missing lap numbers within range: []
NOR: n_laps=57, lap range=(1,57), missing lap numbers within range: []
OCO: n_laps=56, lap range=(1,56), missing lap numbers within range: []
PER: n_laps=56, lap range=(1,56), missing lap numbers within range: []
PIA: n_laps=57, lap range=(1,57), missing lap numbers within range: []
RUS: n_laps=57, lap range=(1,57), missing lap numbers within range: []
SAI: n_laps=57, lap range=(1,57), missing lap numbers within range: []
STR: n_laps=56, lap range=(1,56), missing lap numbers within range: []
VER: n_laps=57, lap range=(1,57), missing lap numbers within range: []
```

## 6a. DNF / short-lap-count drivers (flag)

```
4 drivers have far fewer laps than the ~55-57 race distance:
  HUL: 7 laps  (retired after lap 7 — LapTime NaN on final recorded lap, PitInTime set, TrackStatus 4/SC shortly before)
  LAW: 6 laps  (retired after lap 6 — same pattern: NaN LapTime, PitInTime set, preceded by TrackStatus 124)
  GAS: 5 laps  (retired after lap 5 — NaN LapTime, no PitInTime, TrackStatus 124 on final lap — likely on-track retirement/crash, not a pit-lane stop)
  HAD: 5 laps  (retired after lap 5 — identical pattern to GAS)
```

These are consistent with genuine DNFs (retirements), not truncated/missing
data: each driver's final row has `LapTime_in_seconds == NaN` (the lap was
never completed/crossed) while lap number sequencing up to that point is
intact with no gaps. GAS/HAD's final lap has no `PitInTime`, suggesting an
on-track stoppage (crash/mechanical) rather than a pit-lane retirement,
while HUL/LAW show a `PitInTime`, suggesting they pulled into the pits to
retire. Cross-referencing against `session.results` (Task 3, once available)
will confirm official classification/status (DNF reason) for these four.

## 7. Weather-to-laps join feasibility

```
Weather Time range: 0 days 00:00:07.716000 to 0 days 02:47:08.713000
Laps Time range: 0 days 00:58:58.087000 to 0 days 02:32:12.238000
Weather sampling interval - median: 0 days 00:01:00.003000, min: 0 days 00:00:58.950000, max: 0 days 00:01:01.066000
Both columns are session-elapsed Timedelta ('0 days HH:MM:SS...') => same time base, merge_asof feasible directly on 'Time' (sort both frames by Time first).
```
```
Overlap window: 0 days 00:58:58.087000 to 0 days 02:32:12.238000 (full laps range covered)
```