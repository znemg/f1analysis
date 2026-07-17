# Data Inventory — Miami GP 2026 Race

## Laps CSV (2026-Miami Grand Prix-Race.csv) — shape 1040 rows x 33 cols

### Columns and dtypes

```
Time: object
Driver: object
DriverNumber: int64
LapTime: object
LapNumber: float64
Stint: float64
PitOutTime: object
PitInTime: object
Sector1Time: float64
Sector2Time: float64
Sector3Time: float64
Sector1SessionTime: object
Sector2SessionTime: object
Sector3SessionTime: object
SpeedI1: float64
SpeedI2: float64
SpeedFL: float64
SpeedST: float64
IsPersonalBest: object
Compound: object
TyreLife: float64
FreshTyre: bool
Team: object
LapStartTime: object
LapStartDate: object
TrackStatus: int64
Position: float64
Deleted: bool
DeletedReason: object
FastF1Generated: bool
IsAccurate: bool
LapTime_in_seconds: float64
laptime_sum_sectortimes: float64
```

### First 5 rows

```
                     Time Driver  DriverNumber                 LapTime  LapNumber  Stint PitOutTime PitInTime  Sector1Time  Sector2Time  Sector3Time      Sector1SessionTime      Sector2SessionTime      Sector3SessionTime  SpeedI1  SpeedI2  SpeedFL  SpeedST IsPersonalBest Compound  TyreLife  FreshTyre     Team            LapStartTime             LapStartDate  TrackStatus  Position  Deleted DeletedReason  FastF1Generated  IsAccurate  LapTime_in_seconds  laptime_sum_sectortimes
0  0 days 00:59:00.108000    NOR             1  0 days 00:01:38.115000        1.0    1.0        NaN       NaN          NaN       34.453       25.729                     NaN  0 days 00:58:34.505000  0 days 00:59:00.288000    213.0    183.0    273.0    298.0          False   MEDIUM       1.0       True  McLaren  0 days 00:57:21.749000  2026-05-03 17:04:02.494            1       3.0    False           NaN            False       False              98.115                      NaN
1  0 days 01:00:32.878000    NOR             1  0 days 00:01:32.770000        2.0    1.0        NaN       NaN       32.593       34.600       25.577  0 days 00:59:32.761000  0 days 01:00:07.361000  0 days 01:00:32.938000    211.0    184.0    271.0    317.0           True   MEDIUM       2.0       True  McLaren  0 days 00:59:00.108000  2026-05-03 17:05:40.853            1       3.0    False           NaN            False        True              92.770                   92.770
2  0 days 01:02:06.141000    NOR             1  0 days 00:01:33.263000        3.0    1.0        NaN       NaN       32.816       34.702       25.745  0 days 01:01:05.754000  0 days 01:01:40.456000  0 days 01:02:06.201000    209.0    185.0    270.0    313.0          False   MEDIUM       3.0       True  McLaren  0 days 01:00:32.878000  2026-05-03 17:07:13.623            1       3.0    False           NaN            False        True              93.263                   93.263
3  0 days 01:03:39.955000    NOR             1  0 days 00:01:33.814000        4.0    1.0        NaN       NaN       33.089       34.864       25.861  0 days 01:02:39.290000  0 days 01:03:14.154000  0 days 01:03:40.015000    205.0    186.0    273.0    310.0          False   MEDIUM       4.0       True  McLaren  0 days 01:02:06.141000  2026-05-03 17:08:46.886            1       3.0    False           NaN            False        True              93.814                   93.814
4  0 days 01:05:13.797000    NOR             1  0 days 00:01:33.842000        5.0    1.0        NaN       NaN       32.883       35.214       25.745  0 days 01:04:12.898000  0 days 01:04:48.112000  0 days 01:05:13.857000    210.0    183.0    281.0    308.0          False   MEDIUM       5.0       True  McLaren  0 days 01:03:39.955000  2026-05-03 17:10:20.700           12       3.0    False           NaN            False        True              93.842                   93.842
```

### Memory usage (deep)

```
Index                       8320
Time                       73840
Driver                     54080
DriverNumber                8320
LapTime                    73567
LapNumber                   8320
Stint                       8320
PitOutTime                 34177
PitInTime                  34216
Sector1Time                 8320
Sector2Time                 8320
Sector3Time                 8320
Sector1SessionTime         72773
Sector2SessionTime         73762
Sector3SessionTime         73762
SpeedI1                     8320
SpeedI2                     8320
SpeedFL                     8320
SpeedST                     8320
IsPersonalBest             37432
Compound                   56134
TyreLife                    8320
FreshTyre                   1040
Team                       60254
LapStartTime               73840
LapStartDate               74880
TrackStatus                 8320
Position                    8320
Deleted                     1040
DeletedReason              33895
FastF1Generated             1040
IsAccurate                  1040
LapTime_in_seconds          8320
laptime_sum_sectortimes     8320

Total: 941.3 KB
```

## Weather CSV (2026-Miami Grand Prix-Race-weather.csv) — shape 168 rows x 8 cols

### Columns and dtypes

```
Time: object
AirTemp: float64
Humidity: float64
Pressure: float64
Rainfall: bool
TrackTemp: float64
WindDirection: int64
WindSpeed: float64
```

### First 5 rows

```
                     Time  AirTemp  Humidity  Pressure  Rainfall  TrackTemp  WindDirection  WindSpeed
0  0 days 00:00:07.716000     25.7      76.2    1016.2     False       34.9            162        1.5
1  0 days 00:01:07.703000     25.7      76.4    1016.2     False       35.0             95        0.7
2  0 days 00:02:07.712000     25.8      75.9    1016.2     False       34.7             33        0.6
3  0 days 00:03:07.706000     25.9      75.9    1016.2     False       35.3             30        1.1
4  0 days 00:04:07.716000     25.9      76.7    1016.2     False       35.2             79        0.8
```

### Memory usage (deep)

```
Index             1344
Time             11928
AirTemp           1344
Humidity          1344
Pressure          1344
Rainfall           168
TrackTemp         1344
WindDirection     1344
WindSpeed         1344

Total: 21.0 KB
```