# FastF1 API Pull Summary — Miami GP 2026 Race

## session.results

```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/session_results.csv (22 rows x 22 cols)
Columns: ['DriverNumber', 'BroadcastName', 'Abbreviation', 'DriverId', 'TeamName', 'TeamColor', 'TeamId', 'FirstName', 'LastName', 'FullName', 'HeadshotUrl', 'CountryCode', 'Position', 'ClassifiedPosition', 'GridPosition', 'Q1', 'Q2', 'Q3', 'Time', 'Status', 'Points', 'Laps']
```

### DNF driver Status check (HUL, LAW, GAS, HAD)

```
   Abbreviation         TeamName  Position ClassifiedPosition  GridPosition   Status  Points Time
27          HUL             Audi      19.0                  R          10.0  Retired     0.0  NaT
30          LAW     Racing Bulls      20.0                  R          11.0  Retired     0.0  NaT
10          GAS           Alpine      21.0                  R           9.0  Retired     0.0  NaT
6           HAD  Red Bull Racing      22.0                  R          22.0  Retired     0.0  NaT
```

## session.race_control_messages

```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/race_control_messages.csv (176 rows x 9 cols)
Columns: ['Time', 'Category', 'Message', 'Status', 'Flag', 'Scope', 'Sector', 'RacingNumber', 'Lap']
```

### SC/VSC related messages

```
                  Time   Category                 Message       Status  Flag Scope  Sector RacingNumber  Lap
22 2026-05-03 17:12:15  SafetyCar     SAFETY CAR DEPLOYED     DEPLOYED  None  None     NaN         None    6
57 2026-05-03 17:24:07  SafetyCar  SAFETY CAR IN THIS LAP  IN THIS LAP  None  None     NaN         None   11
```

## session.track_status

```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/track_status.csv (17 rows x 3 cols)
Columns: ['Time', 'Status', 'Message']
```
```
                     Time Status     Message
0         0 days 00:00:00      1    AllClear
1  0 days 00:28:11.432000      2      Yellow
2  0 days 00:30:47.140000      1    AllClear
3  0 days 00:31:09.235000      2      Yellow
4  0 days 00:31:12.720000      1    AllClear
5  0 days 00:31:13.251000      2      Yellow
6  0 days 00:36:31.543000      1    AllClear
7  0 days 01:05:05.815000      2      Yellow
8  0 days 01:05:34.079000      4  SCDeployed
9  0 days 01:18:52.924000      1    AllClear
10 0 days 01:25:48.656000      2      Yellow
11 0 days 01:25:52.109000      1    AllClear
12 0 days 02:15:48.835000      2      Yellow
13 0 days 02:15:51.375000      1    AllClear
14 0 days 02:29:50.839000      2      Yellow
15 0 days 02:29:56.351000      1    AllClear
16 0 days 02:34:44.751000      2      Yellow
```

## session.get_circuit_info()

```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/circuit_info_fastf1.json
Corners: 19
Marshal lights: 19
Marshal sectors: 20
Rotation: 2.0
```

### Cross-check vs existing Miami_Race_cor.json

```
FastF1 corner count: 19
Existing (TracingInsights) corner count: 19
FastF1 rotation: 2.0
Existing rotation: 2.0
```
```
Per-corner X/Y distance (FastF1 vs existing), n=19: max=0.00, mean=0.00
```

## session.event

```
Saved -> /Users/zhangyimeng/SportsAnalytics/f1/event_info.json
```
```
{
  "RoundNumber": 4,
  "Country": "United States",
  "Location": "Miami Gardens",
  "OfficialEventName": "FORMULA 1 CRYPTO.COM MIAMI GRAND PRIX 2026",
  "EventDate": "2026-05-03 00:00:00",
  "EventName": "Miami Grand Prix",
  "EventFormat": "sprint_qualifying",
  "Session1": "Practice 1",
  "Session1Date": "2026-05-01 12:00:00-04:00",
  "Session1DateUtc": "2026-05-01 16:00:00",
  "Session2": "Sprint Qualifying",
  "Session2Date": "2026-05-01 16:30:00-04:00",
  "Session2DateUtc": "2026-05-01 20:30:00",
  "Session3": "Sprint",
  "Session3Date": "2026-05-02 12:00:00-04:00",
  "Session3DateUtc": "2026-05-02 16:00:00",
  "Session4": "Qualifying",
  "Session4Date": "2026-05-02 16:00:00-04:00",
  "Session4DateUtc": "2026-05-02 20:00:00",
  "Session5": "Race",
  "Session5Date": "2026-05-03 13:00:00-04:00",
  "Session5DateUtc": "2026-05-03 17:00:00",
  "F1ApiSupport": true
}
```