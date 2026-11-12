# Decision log and changelog: green hydrogen model

Part 1 lists every important choice: what, why, and what would change it. Part 2 lists every change to the model in date order, with its effect on the LCOH.
Add a line at the moment a choice or change is made.
Becomes the README sections "Method and assumptions" and "Version history", and the answer to "what was your hardest decision?".
Verified results, caught errors and limitations live in `checks_and_limitations.md`.

# Part 1: Decisions

## Scope and question
| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| D1 | 5 Nov 2026 | Country: the Netherlands, grid-connected plant | Where I study; strong data (ENTSO-E, TNO); active hydrogen policy | Other countries can be added via a country dictionary (D14) |
| D17 | 5–6 Nov | Build the model structure first with placeholder inputs, then replace them one by one with sourced values | A working, checked structure first; each sourced change can then be measured on its own | – |
| D10 | 10–11 Nov | Two production routes: cost-optimal grid hydrogen vs certified green (RFNBO) | The cheapest operation is not certified green and is partly fossil-powered | – |
| D13 | 11 Nov | Research question reframed: from "cheaper than grey?" to "what is renewable hydrogen worth to a Dutch buyer, and does that cover its cost?" | Buyers face RED III mandates, penalties and credits, so grey hydrogen is not their only alternative | – |

## Project and technology
| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| D2 | 6 Nov | Base technology: alkaline | Slightly cheaper and more efficient (54.6 vs 55.1 kWh/kg); longer claimed stack life | PEM may win under variable operation: tested in Milestone 3c |
| D3 | 6 Nov | Discount rate 8% (WACC) | Sources: 7% low-risk, 10% high-risk, 4% with policy support; a Dutch project still carries technology and offtake risk | Strictly a real rate fits constant prices (~6%): fix in Milestone 5 |
| D18 | 6 Nov | Stack lifetime 90,000 h as base (manufacturer claim); 50,000 h as low value | Base follows the technology claim; IEA uses 50,000 h as the economic optimum given degradation | Field data on real stack life |
| D6 | 11 Nov | IEA capex €1,950/kW assumed to apply at large scale (100 MW reference) | IEA installed-cost figures refer to commercial-scale projects | TO VERIFY: if it refers to smaller plants, economies of scale apply |
| D7 | 11 Nov | Base size 100 MW (was 10 MW) | Typical Dutch project size; TNO reference size; matches TenneT high-voltage tariff. LCOH unchanged (€10.07/kg) because all costs scale linearly with size at these inputs | A smaller, regionally connected project needs a different grid tariff |
| D8 | 9–11 Nov | Equipment capex (IEA) as base; TNO full-project capex as a scenario (€3,050 × 0.93 = €2,840/kW, excluding the compressor modelled separately); indirect costs as a separate input (default 0) | TNO costs are much higher (€13.16/kg): keep the scope explicit instead of mixing | Resolve in Milestone 7 (benchmark) |
| D19 | 7 Nov | Water: buy demineralised water (10 L/kg) instead of purifying on site (~15 L/kg) | Simplest for a first model; the cost is tiny either way (~€0.01/kg) | Water availability (permits, scarcity) rather than price |
| D20 | 7 Nov | Compression into the Dutch hydrogen network (~30 → 50 bar); compressor sized on peak output, replaced once (14-year life) | Network delivery is the realistic Dutch route; Gasunie network pressure ~50 bar | Delivery to a specific buyer or to storage at higher pressure (up to ~2.5 kWh/kg at 200 bar) |
| D24 | 7 Nov | Restart/cycling costs deferred until the model runs hour by hour | With a flat capacity factor the model cannot see how often the plant starts | Done in Milestone 3c (count starts × cost per start, or a minimum run time) |

## Data and inputs
| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| D4 | 6 Nov | Data year 2025 | Latest full year; after the energy crisis | Repeat with 2023/2024; future price paths in Milestones 5 and 8 |
| D21 | 6–9 Nov | Capacity factor kept as an unsourced placeholder (0.5) until Milestone 3 | It is an operating decision, not a fixed input: it must come from real prices | Set from hourly prices (Milestone 3: optimum 0.9) |
| D22 | 7–9 Nov | Grid tariff: TenneT HV €150k/MW/yr as base; EHV €116k as low; non-firm contract (€57k, ~15% curtailment) as a scenario, not part of the range | The non-firm contract is a commercial choice and also cuts running hours | Regional tariffs for smaller plants; Dutch policy changes (Germany and Belgium exempt electrolysers) |
| D5 | 9 Nov | Sourced (low, high) ranges instead of ±20% in the sensitivity analysis | Equal % changes are not equally realistic | Better sources narrow or widen the ranges |
| D23 | 9 Nov | Tornado chart: hours per year excluded (fixed fact), plant size excluded (design choice), lifetime kept (choice and uncertainty), scale exponent skipped at reference size, bars below €0.05/kg not drawn | Show only real uncertainties that matter | – |
| D9 | 10 Nov | 15-minute prices (from 1 Oct 2025) averaged to hourly | One consistent time step for the whole year | Slightly understates the value of flexibility |
| D25 | 10 Nov | Operating strategy for grid hydrogen: run in the cheapest hours, with day-ahead prices known in advance | Day-ahead prices are published the day before, so scheduling on them is realistic | Profit-based dispatch with a hydrogen price (break-even power price), Milestone 3b/4 |
| D16 | 11 Nov | Milestone 3b uses offshore wind only | ENTSO-E under-reports Dutch solar and onshore wind production (see C7); offshore data is complete and matches the typical Dutch hydrogen PPA | Add solar/onshore from a weather-based source (e.g. Renewables.ninja) |

## Rules and regulation
| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| D11 | 11 Nov | Green-hours limit = max(€20, 0.36 × ETS price), using the yearly ETS average (€74/t → €26.64/MWh) | The EU rule allows either condition; the yearly average is a simplification | Hourly ETS prices would be more exact |
| D12 | 11 Nov | Emissions at the AVERAGE grid factor (262 g/kWh, 2025); marginal (gas plant) factor only as a stress test | The average is the standard reporting basis; the marginal factor shows the effect on the power system | – |

## Model structure and workflow
| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| D14 | 11 Nov | Model split into PROJECT / TECHNOLOGY / COUNTRY dictionaries in one shared module (`h2_model.py`) | Any part can be swapped; other countries and technologies plug in without code changes; no copies across notebooks | – |
| D15 | 11 Nov | Data and model stored in Google Drive, mounted in Colab | Colab's temporary storage is wiped every session | Move to GitHub in Phase C |

# Part 2: Changelog (model changes and their effect)
Base case = CF 0.5, flat electricity price, unless stated otherwise.

| Date | Change | Base LCOH |
|---|---|---|
| 5 Nov 2026 | Core model: capex (via CRF), O&M, electricity. Placeholder inputs (10 MW, €1,800/kW, 55 kWh/kg, €50/MWh) | €5.73/kg |
| 6 Nov | Assumptions moved into one dictionary; `lcoh_breakdown()` and automatic checks added | €5.73 |
| 6 Nov | Economies of scale added (exponent 1.0 placeholder) | €5.73 |
| 6 Nov | Milestone 2: electricity price chart (CF 0.5 and 0.9), ±20% tornado chart | – |
| 6 Nov | Sourced base values: capex €1,950/kW (IEA), efficiency 54.6 kWh/kg (BNEF), electricity €87/MWh (TenneT), scale exponent 0.87 | €5.73 → €7.96 |
| 6 Nov | Stack replacement added (48% of capex, 90,000 h): no replacement at CF 0.5 (60,000 h test: €8.37) | €7.96 |
| 7 Nov | Water added (10 L/kg at €0.85/m³) | €7.96 → €7.97 |
| 7 Nov | Grid transport tariff added (€150k/MW/yr, TenneT HV) | €7.97 → €9.83 |
| 7 Nov | Compression into the Dutch H2 network added (~30 → 50 bar) | €9.83 → €10.07 |
| 9 Nov | Capex scope scenario: TNO full-project capex (base unchanged) | Scenario: €13.16 |
| 9 Nov | Sourced ranges revised (efficiency, electricity price, lifetime, stack life, grid tariff); tornado redrawn with sourced ranges; scenarios: 2022 power price €18.57, non-firm grid €8.91 (€9.63 with curtailment) | €10.07 |
| 10 Nov | Milestone 3: ENTSO-E 2025 hourly prices; run in cheapest hours; optimum CF 0.9 at €77.4/MWh | Scenario: €7.48 |
| 11 Nov | Price statistics; green-hours shortcut (≤ €20: €19.96; corrected rule ≤ €26.64: €18.93); capex test €1,000/kW → €6.40 at CF 0.8 | Scenarios |
| 11 Nov | Shared module `h2_model.py`: PROJECT / TECHNOLOGY / COUNTRY structure, 100 MW base, new inputs at 0 until sourced (H2 network tariff, electricity tax, indirect costs), new functions (break-even power price, grid H2 emissions, RFNBO threshold, part-load efficiency); data in Google Drive | €10.07 (unchanged) |
| 11 Nov | Milestone 3b started: ENTSO-E generation profiles; offshore wind capacity factor 0.377 | – |
