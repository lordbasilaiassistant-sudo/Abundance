#!/usr/bin/env python3
"""Fetch per-country indicators from the World Bank Open Data API
and write data/countries.json. Re-run when underlying data updates.

No authentication required. Free API. Cited at the bottom of every record.
"""
import json
import shutil
import urllib.request
import urllib.parse
from pathlib import Path

# Largest populations + every country that backs a pilot or case study on
# the site + broad regional coverage. ISO3 codes (World Bank identifiers).
COUNTRIES = [
    # --- Largest populations ---
    "USA", "CHN", "IND", "IDN", "PAK",
    "NGA", "BRA", "BGD", "RUS", "MEX",
    "JPN", "ETH", "PHL", "EGY", "VNM",
    "COD", "IRN", "TUR", "DEU", "THA",
    "GBR", "FRA", "ITA", "ZAF",
    # --- Original comparison cases (case-studies.html v1) ---
    "NOR",   # sovereign-wealth dividend (Permanent Fund analog)
    "CRI",   # Costa Rica — military dissolved 1948
    "SAU",   # high consumption vs renewable water supply
    "ISL",   # Iceland post-2009 prosecutions
    "MUS",   # Mauritius post-1968 social investment
    "BTN",   # Bhutan GNH
    # --- Countries that back a pilot or new case study ---
    "KEN",   # GiveDirectly UBI RCT
    "KOR",   # South Korea — land reform + developmental state
    "BWA",   # Botswana — diamond-revenue governance / Pula Fund
    "FIN",   # Finland — Housing First; Basic Income Experiment 2017-18
    "PRT",   # Portugal — 2001 drug decriminalization
    "URY",   # Uruguay — Frente Amplio social policy
    "NAM",   # Namibia — Basic Income Grant (Otjivero)
    # --- Broad regional coverage ---
    "CAN", "AUS", "ESP", "NLD", "SWE", "CHE", "NZL", "IRL", "DNK",
    "BEL", "AUT", "GRC", "POL", "CZE", "ROU", "UKR", "KAZ",
    "SGP", "MYS", "LKA", "NPL", "KHM", "MMR", "AFG", "YEM", "IRQ",
    "PER", "CHL", "COL", "ARG", "VEN", "GTM", "BOL", "ECU", "HTI",
    "GHA", "TZA", "UGA", "RWA", "SEN", "CIV", "AGO", "MOZ", "ZMB", "ZWE", "MWI",
    "DZA", "MAR", "TUN", "SDN", "SOM",
    "QAT", "ARE", "ISR",
]

# Indicator codes. Each has a stable code and a primary source.
INDICATORS = {
    "population":               "SP.POP.TOTL",          # people
    "gdp_usd":                  "NY.GDP.MKTP.CD",       # current US$
    "gdp_per_capita_usd":       "NY.GDP.PCAP.CD",       # current US$
    "military_pct_gdp":         "MS.MIL.XPND.GD.ZS",    # %
    "electricity_kwh_per_cap":  "EG.USE.ELEC.KH.PC",    # kWh/capita (consumption; may stop 2014)
    "broadband_per_100":        "IT.NET.BBND.P2",       # fixed broadband per 100
    "health_pct_gdp":           "SH.XPD.CHEX.GD.ZS",    # % of GDP
    "poverty_pct_3usd":         "SI.POV.UMIC",          # poverty headcount $6.85/day (closest stable)
    "life_expectancy":          "SP.DYN.LE00.IN",       # years
    "renewable_water_m3_pc":    "ER.H2O.INTR.PC",       # m³/capita/yr (internal renewable freshwater)
}

# Try several recent years and use the latest available — many indicators
# have country-specific publication lag.
YEARS = "2018:2024"


def _get_json(url: str, attempts: int = 3, timeout: int = 90):
    """GET with retries — the World Bank API is occasionally slow on large
    multi-country requests."""
    last = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            print(f"  retry {i+1}/{attempts} after: {e}")
    raise last


def fetch_indicator(code: str, country_list: list[str]) -> dict[str, dict]:
    """Returns dict keyed by iso3 -> {value, year}. Picks newest value
    available within YEARS range per country."""
    country_str = ";".join(country_list)
    url = (
        f"https://api.worldbank.org/v2/country/{country_str}"
        f"/indicator/{code}?format=json&date={YEARS}&per_page=2000"
    )
    data = _get_json(url)
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return {}
    rows = data[1]
    # Group by country; pick the newest non-null value per country.
    best = {}
    for row in rows:
        iso = row.get("countryiso3code")
        val = row.get("value")
        yr  = row.get("date")
        if not iso or val is None: continue
        if iso not in best or int(yr) > int(best[iso]["year"]):
            best[iso] = {"value": val, "year": yr}
    return best


def main():
    out: dict = {
        "$schema": "Per-country primary-source data. Source: World Bank Open Data API. Re-fetched by scripts/build_countries.py.",
        "fetched_at": "2026-06-15",
        "source": "World Bank Open Data API (api.worldbank.org/v2)",
        "license": "CC-BY-4.0 (World Bank Open Data terms)",
        "indicators": {
            name: {
                "code": code,
                "source_url": f"https://data.worldbank.org/indicator/{code}",
            }
            for name, code in INDICATORS.items()
        },
        "countries": {},
    }

    # Initialize country records
    for iso in COUNTRIES:
        out["countries"][iso] = {"iso3": iso, "data": {}}

    # Fetch each indicator across all countries in one request
    for name, code in INDICATORS.items():
        print(f"fetching {name} ({code})...")
        try:
            results = fetch_indicator(code, COUNTRIES)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        for iso, payload in results.items():
            out["countries"][iso]["data"][name] = payload

    # Attach country names from the population call (we have country.value there)
    print("attaching country names...")
    country_str = ";".join(COUNTRIES)
    url = (
        f"https://api.worldbank.org/v2/country/{country_str}"
        f"?format=json&per_page=200"
    )
    meta = _get_json(url)
    if isinstance(meta, list) and len(meta) >= 2 and meta[1]:
        for c in meta[1]:
            iso = c.get("id")
            if iso in out["countries"]:
                out["countries"][iso]["name"]    = c.get("name", iso)
                out["countries"][iso]["region"]  = (c.get("region") or {}).get("value", "")
                out["countries"][iso]["capital"] = c.get("capitalCity", "")

    # Drop the indicators not actually filled (to keep the file tight)
    used = set()
    for cdat in out["countries"].values():
        used.update(cdat["data"].keys())
    out["indicators"] = {k: v for k, v in out["indicators"].items() if k in used}

    # Safety guard: never clobber good data with a failed/partial fetch.
    # Require population for at least 70% of requested countries.
    with_pop = sum(1 for c in out["countries"].values() if "population" in c["data"])
    if with_pop < 0.7 * len(COUNTRIES):
        raise SystemExit(
            f"ABORT: only {with_pop}/{len(COUNTRIES)} countries returned population data — "
            f"likely a network/API failure. Existing countries.json left untouched."
        )

    out_path = Path(__file__).resolve().parent.parent / "data" / "countries.json"
    if out_path.exists():
        shutil.copy2(out_path, out_path.with_suffix(".json.bak"))
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out_path} ({out_path.stat().st_size} bytes, {len(out['countries'])} countries; "
          f"{with_pop} with population data)")


if __name__ == "__main__":
    main()
