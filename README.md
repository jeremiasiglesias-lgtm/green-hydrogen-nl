# Green hydrogen in the Netherlands: cost vs value

**Question:** What does renewable hydrogen cost in the Netherlands, what is it worth to a Dutch buyer, and when does that value cover the cost?

A techno-economic model in Python, built by Jeremías Iglesias González (BSc Chemical Engineering and Chemistry, TU/e).

## Status (November 2026)
- ✅ Core LCOH model with sourced inputs (100 MW alkaline electrolyser, NL 2025): **€10.07/kg** at a flat power price
- ✅ Sensitivity analysis with sourced low/high ranges
- ✅ Hourly operation on 2025 Dutch day-ahead prices: cost-optimal grid hydrogen **€7.48/kg** (capacity factor 0.9); running only in EU low-price hours **€18.93/kg**
- 🔧 In progress: certified green hydrogen (RFNBO) with an offshore wind PPA
- ⏭ Next: value to buyers (grey hydrogen + CO2 price, RED III penalties and credits) vs cost per route

## Structure
- `h2_model.py`: shared model (project / technology / country inputs, LCOH, EU rules, emissions)
- `notebooks/`: one notebook per milestone (01–02 predate the shared module and contain their own model code)
- `Docs/decision_log.md`: every modelling choice and why
- `Docs/checks_and_limitations.md`: validation checks, errors caught, known limitations

## How to run
Open a notebook in Google Colab. Notebook 03 loads `h2_model.py` from Google Drive and downloads 2025 data from the ENTSO-E Transparency Platform (free API key needed).
