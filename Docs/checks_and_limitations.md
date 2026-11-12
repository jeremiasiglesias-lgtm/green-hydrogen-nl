# Checks and limitations: green hydrogen model

What was verified, what was caught and fixed, and what the model cannot do yet. A line is added every time something is checked, caught or found missing.
Becomes the README section "Validation and limitations" and the limitations page of the dashboard.
Choices and their reasons, and the version history, live in `decision_log.md`.

## 1. Validation checks: what was verified, and against what
| # | Date | Check | Result |
|---|---|---|---|
| V1 | 6 Nov 2026 | Cost parts add up to the total LCOH (automatic check in the model) | Passes |
| V2 | 6 Nov | Without economies of scale (exponent 1.0), LCOH does not depend on plant size (automatic check) | Passes |
| V3 | 6 Nov | LCOH rises €0.055/kg per €1/MWh of electricity = MWh needed per kg (54.6 kWh), independent of capacity factor | Matches hand calculation |
| V4 | 6 Nov | Stack cost is zero when the stack outlives the plant (automatic check); 60,000 h stack gives one replacement in year ~13.7 | Passes |
| V5 | 7 Nov | Each new cost predicted by hand before running (water ~€0.01/kg, grid €1.5M/yr ÷ ~0.8 million kg ≈ €1.87/kg) | Matches predictions |
| V6 | 7 Nov | Grid tariff contribution (€1.87/kg) vs TNO 2024 (grid tariffs add > €2/kg in Dutch projects) | Consistent |
| V7 | 9 Nov | Every base value lies inside its sourced (low, high) range (automatic check) | Passes |
| V8 | 9 Nov | LCOH almost exactly proportional to efficiency: 10.07 × 47/54.6 = €8.67 by hand vs €8.70 from the model | Matches |
| V9 | 9 Nov | TNO capex scenario (€13.16/kg) vs TNO's own base case for Dutch projects (€13.69/kg) | Close: model structure is sound; the gap with the base case comes from the capex input |
| V10 | 10 Nov | Hourly price data: 8,760 hours, no missing hours | Passes |
| V11 | 10 Nov | 2025 average day-ahead price vs published figure (Electricity Maps: €86.8/MWh) | Matches: €86.8 |
| V12 | 11 Nov | Negative-price hours 2025 vs published figure (Synertics: 584) | Matches: 584 |
| V13 | 11 Nov | Shared module at 100 MW reproduces earlier results (€10.07 base, €7.48 at CF 0.9, €6.40 at €1,000/kW) | Matches |
| V14 | 11 Nov | Offshore wind capacity factor 2025 from ENTSO-E (0.377) vs typical values (~0.40–0.50) | Plausible |
| V15 | 11 Nov | ENTSO-E average production vs installed capacity: solar 57 MW vs 29,282 MW; onshore 807 vs 7,178 MW; offshore 1,787 vs 4,739 MW | Confirms C7 |

## 2. Problems caught and fixed
| # | Date | Problem | How it was caught | Fix |
|---|---|---|---|---|
| C8 | 6 Nov | Changelog lines added to the notebook before the changes themselves: the notebook claimed sourced values and stack replacement that were not in the code yet | Review of the notebook: base LCOH still €5.73 | Changes made first, changelog filled in with the real result afterwards |
| C1 | 9 Nov | Efficiency range 47–73 kWh/kg: the high end came from an old (2017) survey including outdated systems, and made efficiency look dominant | Tornado chart dominated by one bar; source critique | Range 50.5–57.6 from recent sources |
| C2 | 9 Nov | Electricity price range 77–87 €/MWh too narrow, with the base at the top edge | One-sided tornado bar, although electricity is ~47% of the cost | 77–96 €/MWh (three post-crisis years); 2022 as stress test |
| C9 | 9 Nov | Outdated text after the base case changed (section 5 still quoted €4.63 vs €5.73/kg) | Review of text cells against outputs | Text updated to current results |
| C10 | 9 Nov | TNO scenario: setting the reference size to 100 MW with a 10 MW plant scaled TNO's price up to ~€3,830/kW | Review of the scenario inputs | Intended (smaller plants cost more per kW), explained in the notebook; size issue removed by the 100 MW base (D7) |
| C11 | 9 Nov | Tornado legend showed both colours as blue (empty bars carry no colour) | Visual check of the chart | Labels put on the first real bar of each colour |
| C3 | 10 Nov | ENTSO-E download included the first value of 2026 (8,761 hours) | Hour count ≠ 8,760 | Filter `index < end` (placed after the download, not before) |
| C4 | 10 Nov | From 1 Oct 2025 prices are 15-minute values: a plain average over-weights Oct–Dec (€87.3 vs €86.8) | 15,386 values; time stamps 15 minutes apart | Resample to hourly means |
| C5 | 11 Nov | Green-hours rule applied as ≤ €20/MWh only; the EU rule is ≤ €20 OR < 0.36 × ETS price (≈ €26.6 in 2025) | Rereading the regulation during the project review | `rfnbo_price_threshold()`: 1,144 → 1,211 hours; €19.96 → €18.93/kg |
| C6 | 11 Nov | Wrong hydrogen output figures in an explanation (10× too low) | Recalculated during the review | 10 MW makes ~160,000 kg/yr at CF 0.1 and ~1.44 million at CF 0.9 |
| C7 | 11 Nov | ENTSO-E under-reports Dutch solar (CF 0.002) and onshore wind (CF 0.113): most of it is connected to regional grids, while installed capacity counts everything | Capacity factors compared with typical values (~0.10 and ~0.25–0.30); confirmed by V15 | 3b uses offshore wind only (D16); solar/onshore later from a weather-based source |

## 3. Known limitations
**Data and sources**
- One year of prices and production (2025); other years may give different results.
- 15-minute prices averaged to hourly: slightly understates the value of flexibility.
- Solar and onshore wind profiles not yet usable (C7).
- Installed capacity taken at the start of 2025: capacity added during the year makes the offshore capacity factor slightly too high.
- Some inputs rest on weak or second-hand sources: capex via a news article quoting the IEA (not the report itself); efficiency via a manufacturer citing BNEF; stack replacement cost (48%) from a single study on PEM; compressor capex is an EU programme target, not a market price.

**Costs not (yet) included or not yet sourced**
- Hydrogen network entry tariff (input exists, value 0 until sourced).
- Energy tax, levies, supplier and balancing fees on electricity (input exists, value 0; tax check still open).
- Indirect project costs: land, permits, development, interest during construction (input exists, value 0; explains part of the IEA vs TNO capex gap).
- Hydrogen storage for steady delivery to a buyer.
- Standby energy and restart costs; Guarantees of Origin for green routes.
- Possible revenues: oxygen, waste heat.

**Policy context not yet modelled**
- Dutch grid tariffs apply in full to electrolysers, while Germany and Belgium exempt them; a Dutch exemption is under discussion. A policy lever for Milestone 4.

**Physics and operation**
- The plant switches on and off freely every hour: no minimum load or start-up time.
- Constant efficiency: no degradation over stack life, no part-load curve yet (function exists, curve not sourced).
- Availability assumed at 95% (not yet sourced).

**Method**
- Levelised cost with a constant-price annuity (CRF), not a year-by-year cash flow; strictly, the discount rate should be a real rate.
- One-at-a-time sensitivity: inputs that move together (gas price → power price and grey hydrogen cost) are not captured.
- Perfect knowledge of day-ahead prices (realistic for the day-ahead market, not for longer horizons).
- Capex scope: IEA equipment-based figure, assumed to refer to large-scale plants (D6, to verify).
- Emissions use the average grid factor; the marginal (gas plant) factor only as a stress test.
