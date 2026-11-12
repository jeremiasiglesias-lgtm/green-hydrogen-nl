# =====================================================================
# h2_model.py - Green hydrogen techno-economic model (shared module)
#
# Every notebook imports THIS file instead of copying the model.
# Structure (each part can be swapped independently):
#   A. PROJECT      - choices made by the project owner (size, financing)
#   B. TECHNOLOGIES - one dictionary per electrolyser technology
#   C. COUNTRIES    - everything set by a country's markets and laws
#   D. build_case() - merges A + B + C into one assumptions dictionary
#   E. Calculations - LCOH, break-even power price, emissions, EU rules
#   F. Checks       - run automatically when the file is imported
#
# To model another country: copy COUNTRY_TEMPLATE, fill in every value
# with a source, and pass it to build_case(). Nothing else changes.
# Sources for NL values: assumptions table in 01_core_model and
# claude/project_brief.md. State: 11 Nov 2026.
# =====================================================================


# ---------------------------------------------------------------------
# A. PROJECT: decided by the project owner
# ---------------------------------------------------------------------
PROJECT = {
    "capacity_kw": 100_000,         # 100 MW (typical Dutch project size; TNO reference size)
    "lifetime": 20,                 # years
    "discount_rate": 0.08,          # WACC, fraction (see decision log D3)
    "capacity_factor": 0.5,         # share of the year running; set per scenario (M3: optimum 0.9)
    "availability": 0.95,           # max share of the year the plant CAN run (maintenance); TO SOURCE
    "indirect_cost_fraction": 0.0,  # extra project costs (land, permits, development) as share of capex; TO SOURCE (TNO gap)
}


# ---------------------------------------------------------------------
# B. TECHNOLOGIES: properties of the electrolyser itself
# ---------------------------------------------------------------------
ALKALINE = {
    "technology": "Alkaline",
    "capex_per_kw": 1950,                 # €/kW installed system, non-Chinese (IEA GHR 2026 via Argus)
    "reference_capacity_kw": 100_000,     # size the capex figure applies to (decision log D6: assumed large-scale)
    "scale_exponent": 0.87,               # alkaline >10 MW (Energinet / Zauner et al.)
    "om_fraction": 0.03,                  # share of capex per year
    "efficiency": 54.6,                   # kWh/kg H2, full system, at full load (BNEF)
    "stack_lifetime_h": 90_000,           # hours (manufacturer claim)
    "stack_replacement_fraction": 0.48,   # share of capex per replacement (single study, needs 2nd source)
    "water_l_per_kg": 10,                 # L demineralised water per kg H2
    "part_load_curve": None,              # optional: {load: efficiency}, e.g. {0.2: 50, 0.5: 52, 1.0: 54.6}; TO SOURCE (M3c)
}

PEM = {
    "technology": "PEM",
    # Values still to source in Milestone 3c. None = "not filled in yet";
    # build_case() refuses to run with any None left.
    "capex_per_kw": None,
    "reference_capacity_kw": None,
    "scale_exponent": None,
    "om_fraction": None,
    "efficiency": 55.1,                   # kWh/kg, full system (BNEF via John Cockerill)
    "stack_lifetime_h": 65_000,           # hours (manufacturer claim)
    "stack_replacement_fraction": None,
    "water_l_per_kg": None,
    "part_load_curve": None,
}


# ---------------------------------------------------------------------
# C. COUNTRIES: markets, grid, taxes and laws
# ---------------------------------------------------------------------
NETHERLANDS = {
    "country": "Netherlands",
    "currency": "EUR",
    "bidding_zone": "NL",                     # ENTSO-E code for price/generation downloads

    # Electricity market
    "electricity_price": 87,                  # €/MWh, flat annual average 2025 (default when no hourly profile)
    "electricity_tax_per_mwh": 0.0,           # €/MWh energy tax + levies for a large user; TO SOURCE
    "grid_tariff_per_mw_year": 150_000,       # €/MW/yr, TenneT HV transport tariff (fits 100 MW)
    "grid_emission_factor": 0.262,            # kg CO2/kWh, average 2025 (Electricity Maps, flow-traced)

    # Utilities and hydrogen infrastructure
    "water_price_per_m3": 0.85,               # €/m³ demineralised water (Intratec)
    "compression_kwh_per_kg": 0.6,            # kWh/kg, ~30 -> 50 bar Dutch H2 network
    "compressor_capex_per_kg_day": 167,       # €/(kg/day) peak capacity (Clean Hydrogen JU)
    "compressor_om_fraction": 0.06,           # share of compressor capex per year
    "compressor_lifetime_years": 14,          # years
    "h2_network_tariff_per_kwh_h_year": 0.0,  # €/(kWh/h)/yr entry tariff Hynetwork; TO SOURCE (Germany: 25)

    # Climate policy and EU rules (RFNBO, Delegated Regulation 2023/1184)
    "ets_price": 74,                          # €/t CO2, EU ETS average 2025 (ESMA)
    "rfnbo_price_floor": 20,                  # €/MWh: hours at or below count as time-matched
    "rfnbo_ets_multiplier": 0.36,             # ... or below 0.36 x ETS price
    "grey_h2_emissions": 10.13,               # kg CO2/kg H2, SMR reference (IEAGHG 2022)
}

# Copy this, rename it (e.g. GERMANY) and fill every value WITH a source.
COUNTRY_TEMPLATE = {key: None for key in NETHERLANDS}


# ---------------------------------------------------------------------
# D. build_case(): one assumptions dictionary from the three parts
# ---------------------------------------------------------------------
HOURS_PER_YEAR = 8760
H2_LHV_KWH_PER_KG = 33.33      # energy content of hydrogen (lower heating value), kWh/kg


def build_case(project=PROJECT, technology=ALKALINE, country=NETHERLANDS, **changes):
    """Merge project, technology and country into one dictionary.
    {**a, **b} copies a, then b on top. **changes lets you override any
    value in one line, e.g. build_case(capacity_factor=0.9)."""
    case = {**project, **technology, **country, **changes}
    missing = [key for key, value in case.items() if value is None and key != "part_load_curve"]
    if missing:
        raise ValueError(f"Fill in these values (with a source) first: {missing}")
    return case


# ---------------------------------------------------------------------
# E. CALCULATIONS
# ---------------------------------------------------------------------
def crf(rate, lifetime):
    """Capital recovery factor: one-off investment -> equal yearly payment."""
    growth = (1 + rate) ** lifetime
    return rate * growth / (growth - 1)


def lcoh_breakdown(a):
    """Levelised cost of hydrogen, €/kg, split by cost item."""
    lifetime = a["lifetime"]
    rate = a["discount_rate"]
    capacity_kw = a["capacity_kw"]

    energy_kwh = capacity_kw * HOURS_PER_YEAR * a["capacity_factor"]     # kWh/yr into the electrolyser
    h2_kg = energy_kwh / a["efficiency"]                                  # kg/yr

    # Investment, with economies of scale and indirect project costs
    size_ratio = capacity_kw / a["reference_capacity_kw"]
    capex_equipment = a["reference_capacity_kw"] * a["capex_per_kw"] * size_ratio ** a["scale_exponent"]   # €
    capex_total = capex_equipment * (1 + a["indirect_cost_fraction"])                                      # €

    # Stack replacements: present value, then spread over the lifetime
    stack_life_years = a["stack_lifetime_h"] / (HOURS_PER_YEAR * a["capacity_factor"])
    replacement_pv = 0
    year = stack_life_years
    while year < lifetime:
        replacement_pv += capex_equipment * a["stack_replacement_fraction"] / (1 + rate) ** year
        year += stack_life_years

    # Compression into the H2 network (sized on peak output)
    peak_kg_per_day = capacity_kw / a["efficiency"] * 24
    compressor_capex = peak_kg_per_day * a["compressor_capex_per_kg_day"]
    compressor_replacement_pv = 0
    year = a["compressor_lifetime_years"]
    while year < lifetime:
        compressor_replacement_pv += compressor_capex / (1 + rate) ** year
        year += a["compressor_lifetime_years"]

    power_price = a["electricity_price"] + a["electricity_tax_per_mwh"]      # €/MWh paid
    peak_h2_kwh_per_h = capacity_kw / a["efficiency"] * H2_LHV_KWH_PER_KG    # H2 network capacity booked, kWh/h

    yearly = {                                                               # €/yr
        "capex": capex_total * crf(rate, lifetime),
        "om": capex_equipment * a["om_fraction"],
        "electricity": energy_kwh / 1000 * power_price,                      # kWh -> MWh
        "stack": replacement_pv * crf(rate, lifetime),
        "water": h2_kg * a["water_l_per_kg"] / 1000 * a["water_price_per_m3"],  # L -> m³
        "grid": capacity_kw / 1000 * a["grid_tariff_per_mw_year"],           # kW -> MW
        "compression": ((compressor_capex + compressor_replacement_pv) * crf(rate, lifetime)
                        + compressor_capex * a["compressor_om_fraction"]
                        + h2_kg * a["compression_kwh_per_kg"] / 1000 * power_price),
        "h2_network": peak_h2_kwh_per_h * a["h2_network_tariff_per_kwh_h_year"],
    }
    per_kg = {item: cost / h2_kg for item, cost in yearly.items()}           # €/kg
    per_kg["total"] = sum(per_kg.values())
    return per_kg


def lcoh_from(a):
    """LCOH in €/kg."""
    return lcoh_breakdown(a)["total"]


def breakeven_power_price(h2_price_per_kg, a):
    """Highest electricity price (€/MWh) at which producing one more kg still
    earns money, given the hydrogen sale price. Only variable costs count:
    the fixed costs are paid anyway, running or not.
    Dispatch rule: run in every hour with a price below this number."""
    water_per_kg = a["water_l_per_kg"] / 1000 * a["water_price_per_m3"]          # €/kg
    mwh_per_kg = (a["efficiency"] + a["compression_kwh_per_kg"]) / 1000           # MWh/kg
    return (h2_price_per_kg - water_per_kg) / mwh_per_kg - a["electricity_tax_per_mwh"]


def grid_h2_emissions(a, emission_factor=None):
    """kg CO2 per kg H2 when powered from the grid. Default: country average
    factor; pass a marginal factor (e.g. a gas plant) to test the worst case."""
    factor = a["grid_emission_factor"] if emission_factor is None else emission_factor
    return factor * (a["efficiency"] + a["compression_kwh_per_kg"])


def rfnbo_price_threshold(a):
    """EU rule: an hour counts as time-matched if its day-ahead price is at or
    below the floor OR below multiplier x ETS price -> the higher of the two."""
    return max(a["rfnbo_price_floor"], a["rfnbo_ets_multiplier"] * a["ets_price"])


def efficiency_at_load(load, a):
    """kWh/kg at a given load (0-1). Uses the technology's part-load curve
    if it has one (linear interpolation between points), else full-load value."""
    curve = a.get("part_load_curve")
    if not curve:
        return a["efficiency"]
    points = sorted(curve.items())
    if load <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= load <= x1:
            return y0 + (y1 - y0) * (load - x0) / (x1 - x0)
    return points[-1][1]


# ---------------------------------------------------------------------
# F. CHECKS: run on import, so a broken change is noticed immediately
# ---------------------------------------------------------------------
def run_checks():
    base = build_case()
    r = lcoh_breakdown(base)
    assert abs(sum(v for k, v in r.items() if k != "total") - r["total"]) < 1e-9
    # Same LCOH as the 10 MW model of 9 Nov (€10.07/kg): all costs scale linearly with size
    assert abs(r["total"] - 10.07) < 0.01, r["total"]
    # 100 MW vs 10 MW without economies of scale: same LCOH
    small = build_case(capacity_kw=10_000, reference_capacity_kw=10_000, scale_exponent=1.0)
    assert abs(lcoh_from(small) - lcoh_from(base)) < 1e-9
    # EU low-price rule 2025: max(20, 0.36 x 74) = 26.64 €/MWh
    assert abs(rfnbo_price_threshold(base) - 26.64) < 1e-9
    assert base["capacity_factor"] <= base["availability"]


run_checks()


if __name__ == "__main__":
    base = build_case()
    print(f"{base['technology']}, {base['country']}, {base['capacity_kw']/1000:.0f} MW")
    for item, value in lcoh_breakdown(base).items():
        print(f"  {item:12} €{value:.2f}/kg")
    print(f"Break-even power price at €8/kg H2: €{breakeven_power_price(8, base):.0f}/MWh")
    print(f"Grid H2 emissions (NL average 2025): {grid_h2_emissions(base):.1f} kg CO2/kg "
          f"vs grey {base['grey_h2_emissions']} kg CO2/kg")
    print(f"RFNBO low-price threshold 2025: €{rfnbo_price_threshold(base):.2f}/MWh")
