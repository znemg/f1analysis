# 2026 Miami GP — Decision Analytics

Single-race performance attribution: how strategic decisions, driver
behavior, vehicle characteristics, and race conditions interact to produce
outcomes. **Not** race prediction. Focuses on car/engineering behavior more
than driver-vs-driver comparison.

## Root question

**The energy allocation curve across the lap.** Across different corner and
straight terrain, does a driver's actual harvest/deploy allocation track the
theoretical marginal-utility curve implied by the 350kW rate cap and 9MJ
per-lap harvest limit — and where does the gap between actual and optimal
allocation show up?

(No public data gives a true physical optimum, so the project substitutes an
**empirical frontier**: the best-performing laps within this race, grouped
by track segment, stand in for "optimal.")

## Branches

- **Branch 1 — Segment discovery.** *(Hard dependency — nothing else starts
  until this is validated. Currently the only active branch.)* Can
  unsupervised segmentation (HMM) over speed/throttle/brake/gear recover a
  driving-state vocabulary — pure acceleration, friction braking,
  lift-and-coast, engine-brake harvest, super-clipping — without those
  states being predefined? Does the mix of states vary systematically by
  terrain type in a way consistent with known harvest strategy?

- **Branch 2 — Corner-exit deployment intensity.** Does MGU-K deployment on
  corner exit scale with the length of the straight ahead?

- **Branch 3 — Harvest doctrine within an engine family.** Holding
  power-unit hardware constant (Mercedes-engine teams as the primary group,
  Ferrari-engine teams as a cross-check), do teams show distinct,
  data-determined harvest doctrines, and do those doctrines relate to
  results?

- **Branch 4 — Overtake Mode as a deployment decision under attack.** Does
  deployment behavior in DRS-range attacking segments differ from a free-air
  straight of equal length, and does that predict overtake success?

- **Branch 5 — Phase attribution to competitive advantage.** Using the
  Branch 1 segments, which behavioral state carries the largest Shapley
  weight in explaining a team's sector-time advantage?

## Status

Branch 1a (state discovery) is fitted and validated; everything else is
blocked on it per the analysis order. See `CLAUDE.md` for full project
context, data sources, established facts, file inventory, and current
open issues — that file is the authoritative, continuously-updated source
of truth for this project, not this README.
