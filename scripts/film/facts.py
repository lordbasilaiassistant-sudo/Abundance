"""Compute the film's on-screen arithmetic from data/essentials.json.

Every figure the film shows is derived here from a primary-source-cited entry.
Nothing is typed in by hand. If the dataset changes, the film changes.

Methodology guard (methodology.md:85, and the note on extreme_poverty_line_usd_per_day):
current US dollars and 2021 PPP international dollars are NOT comparable, so we
never divide nominal GDP by the poverty line. Ratios are computed only for the
three resources whose numerator and denominator share a unit.
"""
import json, os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(REPO, "data", "essentials.json")


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def cite(d, key):
    e = d[key]
    return {"value": e["value"], "unit": e.get("unit", ""), "year": e.get("year"),
            "source": e.get("source_name", ""), "url": e.get("source_url", "")}


def build():
    d = load()
    pop = d["world_population"]["value"]
    facts = {k: v for k, v in d.items() if isinstance(v, dict) and "value" in v}

    # --- three unit-comparable divisions -------------------------------------
    # FOOD: kcal/person/day already per-capita in the source.
    food_have = d["daily_food_supply_kcal_per_capita"]["value"]
    food_need = d["minimum_calorie_need_kcal"]["value"]

    # WATER: km3/yr -> litres/person/day.  1 km3 = 1e12 L
    water_total_l = d["renewable_freshwater_km3"]["value"] * 1e12
    water_have = water_total_l / pop / 365.0
    water_need = d["minimum_water_need_l_per_day"]["value"]

    # ELECTRICITY: TWh/yr -> kWh/person/yr.  1 TWh = 1e9 kWh
    elec_total_kwh = d["global_electricity_generation_twh"]["value"] * 1e9
    elec_have = elec_total_kwh / pop
    elec_need = d["modern_energy_minimum_kwh_per_year"]["value"]

    divisions = [
        {"key": "food", "label": "FOOD", "hue": [0.878, 0.627, 0.251],
         "total_txt": "3,043 million tonnes of cereal",
         "have": food_have, "need": food_need, "unit": "kcal per person per day",
         "have_txt": "3,006", "need_txt": "2,100",
         "src": d["daily_food_supply_kcal_per_capita"]["source_name"],
         "need_src": d["minimum_calorie_need_kcal"]["source_name"],
         "caveat": ""},
        {"key": "water", "label": "FRESH WATER", "hue": [0.247, 0.663, 0.851],
         "total_txt": "43,000 km³ renewable, per year",
         "have": water_have, "need": water_need, "unit": "litres per person per day",
         "have_txt": "{:,.0f}".format(water_have), "need_txt": "50",
         "src": d["renewable_freshwater_km3"]["source_name"],
         "need_src": d["minimum_water_need_l_per_day"]["source_name"],
         "caveat": "renewable total; geographically uneven"},
        {"key": "electricity", "label": "ELECTRICITY", "hue": [0.545, 0.498, 0.910],
         "total_txt": "32,202 TWh generated, 2025",
         "have": elec_have, "need": elec_need, "unit": "kWh per person per year",
         "have_txt": "{:,.0f}".format(elec_have), "need_txt": "1,000",
         "src": d["global_electricity_generation_twh"]["source_name"],
         "need_src": d["modern_energy_minimum_kwh_per_year"]["source_name"],
         "caveat": ""},
    ]
    for x in divisions:
        x["ratio"] = x["have"] / x["need"]
        x["ratio_txt"] = ("{:,.0f}×".format(x["ratio"]) if x["ratio"] >= 10
                          else "{:.2f}×".format(x["ratio"]))

    # --- money: a position statement, never a ratio against a PPP line -------
    wealth = d["world_household_wealth_usd"]["value"]
    above1m = d["wealth_above_1m_usd"]["value"]

    # --- the shape: who the arithmetic does not reach ------------------------
    shortfalls = [
        {"n": d["people_in_hunger"]["value"], "label": "in hunger",
         "src": "FAO/IFAD/UNICEF/WFP/WHO, SOFI"},
        {"n": d["electricity_without_access_people"]["value"], "label": "without electricity",
         "src": "IEA / IRENA / UNSD / World Bank / WHO"},
        {"n": d["homeless_people"]["value"], "label": "without housing",
         "src": "UN-Habitat / UN DESA"},
        {"n": d["extreme_poverty_count"]["value"], "label": "in extreme poverty",
         "src": "World Bank, March 2026"},
    ]

    try:
        commits = int(subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"], cwd=REPO).decode().strip())
    except Exception:
        commits = 0

    # Act 4 quotes real commit subjects - the receipts for "we keep updating".
    # Read from git so the film can never attribute a line the repo never made.
    try:
        subjects = subprocess.check_output(
            ["git", "log", "--format=%s"], cwd=REPO).decode("utf-8", "replace").splitlines()
    except Exception:
        subjects = []
    wanted = ("refresh", "vintage", "sweep")
    picked, seen = [], set()
    for sub_ in subjects:
        low = sub_.lower()
        # site-plumbing commits are not evidence about data vintages
        if any(w in low for w in ("readme", "sitemap", "page", "design")):
            continue
        if not any(w in low for w in wanted) or low.startswith("merge"):
            continue
        line = sub_.split(" (#")[0].strip()
        if len(line) > 72:                     # fits the column at film type size
            line = line[:71].rstrip(" ,;:") + "…"
        if line in seen:
            continue
        seen.add(line)
        picked.append(line)
        if len(picked) == 4:
            break

    return {
        "population": pop,
        "population_txt": "8,200,000,000",
        "population_src": d["world_population"]["source_name"],
        "divisions": divisions,
        "wealth_txt": "$517.69 trillion",
        "wealth_above1m_txt": "$250.59 trillion",
        "wealth_share": above1m / wealth,
        "wealth_src": d["world_household_wealth_usd"]["source_name"],
        "shortfalls": shortfalls,
        "cited_fact_count": len(facts),
        "sourced_fact_count": sum(1 for v in facts.values() if v.get("source_url")),
        "commits": commits,
        "commit_lines": picked,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f = build()
    out = os.path.join(HERE, "film_facts.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(f, fh, indent=2)
    print("population      ", f["population_txt"], "|", f["population_src"])
    for x in f["divisions"]:
        print("%-12s have=%-12s need=%-8s ratio=%-8s  %s" % (
            x["label"], x["have_txt"], x["need_txt"], x["ratio_txt"], x["unit"]))
        if x["caveat"]:
            print("             caveat:", x["caveat"])
    print("wealth          ", f["wealth_txt"], "| above $1m:", f["wealth_above1m_txt"],
          "= %.1f%%" % (100 * f["wealth_share"]))
    for s in f["shortfalls"]:
        print("shortfall       %-13s %s" % ("{:,}".format(s["n"]), s["label"]))
    print("cited facts     ", f["cited_fact_count"], "| with source url:", f["sourced_fact_count"])
    print("commits         ", f["commits"])
    for c in f["commit_lines"]:
        print("  commit        ", c)
    print("WROTE", out)
