"""The four synthetic companies of the final kernel and their contexts (FINAL_KERNEL_SPEC.md section 3).

Each company has a profile, a forecast mandate, a data dictionary of eight information sources in three families
(three, three and two sources), a regime descriptor with three values that name no family, and, for each of the two
three-source families, event templates that make that family plausibly relevant. In the family marked ``pair``, the
second source is a second measurement of the first. The same templates serve as the genuine clue and as red
herrings, so the text alone cannot tell them apart.

``context(...)`` builds an episode's context from the company, the X ids, the episode's regime and the families its
event log names; the event log builder never sees which source is useful. No text here uses the words the benchmark
forbids (see ``BANNED``); a test checks every template, dictionary entry and header.
"""
from __future__ import annotations

import numpy as np

BANNED = ("noise", "noisy", "driver", "proxy", "retired", "split", "individually", "decompos", "conditional",
          "attribution", "budget", "avoid", "irrelevant", "useful", "red herring", "clue")

COMPANIES = (
    {
        "key": "c1", "name": "Northbrook Water",
        "profile": "Northbrook Water supplies drinking water to about 410,000 people across a mixed urban, coastal "
                   "and rural area. It runs its own treatment works and a network of reservoirs and pump stations.",
        "target": "treated-water demand leaving the treatment works (megalitres per hour)",
        "regime_name": "Supply configuration",
        "regimes": ("Configuration North: both treatment works in service, network fed from the north reservoirs",
                    "Configuration South: one treatment works in service, part of the area fed by a bulk import",
                    "Configuration Combined: the merged network after the integration of the neighbouring company"),
        "families": (
            {"name": "Weather", "pair": True, "sources": (
                ("Area air-temperature forecast", "day-ahead forecast of hourly air temperature averaged over the "
                 "supply area, from the company's main weather service"),
                ("Second-service temperature forecast", "day-ahead forecast of hourly air temperature for the same "
                 "area from a second, independent weather service"),
                ("Rainfall forecast", "day-ahead forecast of hourly rainfall averaged over the supply area"))},
            {"name": "Community activity", "pair": False, "sources": (
                ("School-term calendar index", "published school calendar for the area, as an hourly index of term "
                 "activity"),
                ("Visitor-occupancy index", "booked hotel and holiday-let occupancy for the coming day, from the "
                 "regional tourism board"),
                ("Public-events attendance forecast", "expected hourly attendance at licensed public events in the "
                 "area, from the local authority"))},
            {"name": "Network operations", "pair": False, "sources": (
                ("Pump-station maintenance schedule", "planned maintenance hours at the pump stations for the "
                 "coming day"),
                ("Pressure-management setting", "planned district pressure settings for the coming day"))},
        ),
        "events": (
            ("Customer services reported that household complaints and call volumes have recently moved with how "
             "hot or wet the days were.",
             "The company extended its garden-watering customer programme across the supply area.",
             "The regulator asked the company to explain how outdoor water use responds to conditions outside."),
            ("Local footfall and visitor patterns in the supply area changed noticeably ahead of this period.",
             "The local authority revised its calendar of term dates and licensed public events for the area.",
             "Several large venues and accommodation sites in the area changed their opening arrangements."),
        ),
    },
    {
        "key": "c2", "name": "Coastline Grocers",
        "profile": "Coastline Grocers runs 140 grocery stores along the coast and in two inland cities, with "
                   "online ordering and click-and-collect from most stores.",
        "target": "checkout transactions across all stores (thousands per hour)",
        "regime_name": "Store format mix",
        "regimes": ("Format mix A: mostly large-format stores, weekly-shop focus",
                    "Format mix B: mostly convenience-format stores after the store conversions",
                    "Format mix C: mixed estate after the franchise programme"),
        "families": (
            {"name": "Promotions and pricing", "pair": True, "sources": (
                ("Planned promotion intensity", "share of the range on promotion for the coming day, from the "
                 "marketing plan"),
                ("Recorded promotion intensity", "share of the range on promotion for the coming day, as loaded "
                 "into the store pricing system"),
                ("Competitor discount index", "index of announced competitor discounts for the coming day, from "
                 "a price-monitoring service"))},
            {"name": "Local movement", "pair": False, "sources": (
                ("Footfall forecast", "day-ahead hourly footfall forecast near the stores, from a mobile-data "
                 "provider"),
                ("Public-transport ridership forecast", "day-ahead hourly ridership forecast for the bus and tram "
                 "lines serving the stores"),
                ("Local events index", "hourly index of scheduled local events near the stores"))},
            {"name": "Supply chain", "pair": False, "sources": (
                ("Delivery-slot fill rate", "share of online delivery slots booked for the coming day"),
                ("Stock-availability index", "planned on-shelf availability for the coming day"))},
        ),
        "events": (
            ("The commercial team reported that basket sizes have recently tracked how aggressive the weekly "
             "offers were, both ours and the market's.",
             "A new pricing and promotions system was rolled out to all stores.",
             "Two competitors announced a long-running discount campaign in our main regions."),
            ("Store managers reported that customer traffic has recently followed how busy the surrounding streets "
             "and transport lines were.",
             "The city councils changed bus and tram timetables and pedestrianised several shopping streets.",
             "The regional events calendar for the period was expanded."),
        ),
    },
    {
        "key": "c3", "name": "Ridgeway Parcels",
        "profile": "Ridgeway Parcels operates a sorting hub that receives parcels from online retailers and "
                   "trunk routes and sends them on to local delivery depots.",
        "target": "parcels arriving at the sorting hub (thousands per hour)",
        "regime_name": "Network role",
        "regimes": ("Role 1: regional hub serving the surrounding counties",
                    "Role 2: national overflow hub taking diverted volume from other hubs",
                    "Role 3: hub after the commissioning of the new automated sorting line"),
        "families": (
            {"name": "Client order signals", "pair": True, "sources": (
                ("Largest client's order forecast", "day-ahead hourly order forecast shared by the largest retail "
                 "client"),
                ("Client order forecast from the shared portal", "the same client's day-ahead order forecast as "
                 "published on the shared logistics portal"),
                ("Marketplace promotion calendar", "hourly index of announced marketplace promotions"))},
            {"name": "Transport conditions", "pair": False, "sources": (
                ("Trunk-road congestion forecast", "day-ahead hourly congestion forecast for the main trunk "
                 "routes"),
                ("Port arrival schedule", "scheduled container arrivals at the nearest port for the coming day"),
                ("Air-freight slot forecast", "booked air-freight slots at the regional airport for the coming "
                 "day"))},
            {"name": "Workforce", "pair": False, "sources": (
                ("Rostered sorting staff", "rostered sorting staff per hour for the coming day"),
                ("Agency staff bookings", "agency staff booked per hour for the coming day"))},
        ),
        "events": (
            ("Account managers reported that inbound volume has recently followed what the retail clients said they "
             "would send.",
             "The largest retail client moved more of its orders through the hub.",
             "The online marketplace announced a new calendar of sales events."),
            ("The operations team reported that arrival peaks have recently shifted with conditions on the trunk "
             "routes and at the port.",
             "Roadworks began on two trunk routes and the port changed its berthing schedule.",
             "The airport added late-evening freight slots."),
        ),
    },
    {
        "key": "c4", "name": "Helios Data Centres",
        "profile": "Helios Data Centres operates a campus of three data halls that hosts enterprise and research "
                   "computing for about sixty tenants.",
        "target": "electricity drawn by the campus (megawatts, hourly average)",
        "regime_name": "Tenant mix",
        "regimes": ("Tenant mix 1: mostly enterprise tenants on long contracts",
                    "Tenant mix 2: mostly research and model-training tenants",
                    "Tenant mix 3: mixed tenancy after the third hall opened"),
        "families": (
            {"name": "Compute bookings", "pair": True, "sources": (
                ("Booked batch-compute reservations", "batch-compute reservations booked for the coming day, from "
                 "the booking system"),
                ("Scheduler-reported reservations", "the same reservations as reported by the cluster scheduler "
                 "for the coming day"),
                ("Tenant deployment calendar", "hourly index of announced tenant deployments and migrations"))},
            {"name": "Outside conditions", "pair": False, "sources": (
                ("Wet-bulb temperature forecast", "day-ahead hourly wet-bulb temperature forecast for the campus"),
                ("Solar-irradiance forecast", "day-ahead hourly solar-irradiance forecast for the campus roof "
                 "array"),
                ("Wind-speed forecast", "day-ahead hourly wind-speed forecast for the campus"))},
            {"name": "Facilities", "pair": False, "sources": (
                ("Planned maintenance windows", "planned maintenance hours in the data halls for the coming day"),
                ("Generator test schedule", "scheduled backup-generator test hours for the coming day"))},
        ),
        "events": (
            ("The tenant team reported that demand on the halls has recently moved with how much compute tenants "
             "had booked and deployed.",
             "Several tenants moved their batch work onto the campus booking system.",
             "A large tenant announced a programme of deployments and migrations."),
            ("The facilities team reported that load has recently varied with the weather around the campus.",
             "The cooling plant was reconfigured to rely more on outside air.",
             "A new rooftop solar array and wind monitoring were commissioned."),
        ),
    },
)

SOURCES_PER_COMPANY = 8
FAMILY_SIZES = (3, 3, 2)
QUESTION = ("Which of the eight information sources currently carry predictive information for {target}, and what "
            "does the evidence support?")


def sources(company: dict) -> list[dict]:
    """The company's eight sources in dictionary order, each with its family index and position in the family."""
    out = []
    for f, fam in enumerate(company["families"]):
        for j, (name, desc) in enumerate(fam["sources"]):
            out.append({"family": f, "position": j, "name": name, "description": desc,
                        "pair": fam["pair"] and j < 2})
    return out


def event_log(company: dict, families: list[int], rng: np.random.Generator) -> list[dict]:
    """The episode's dated events: one template from each named family (only the two three-source families have
    templates), on a day drawn from -28..-1. It takes the named families and a random stream, never roles; events are
    sorted by (day, family, template)."""
    events = []
    for f in families:
        t = int(rng.integers(0, len(company["events"][f])))
        events.append({"day": int(rng.integers(-28, 0)), "family": f, "template": t,
                       "text": company["events"][f][t]})
    return sorted(events, key=lambda e: (e["day"], e["family"], e["template"]))


def context(company: dict, x_ids: dict, period: int, regime: int, events: list[dict]) -> dict:
    """The episode's context: structured fields (company, period, regime, names by X id) and the rendered text. It
    holds nothing about which source is useful."""
    srcs = sources(company)
    names = {x_ids[i]: s["name"] for i, s in enumerate(srcs)}
    lines = [f"Company: {company['name']}", f"Profile: {company['profile']}",
             f"Forecast mandate: each day, forecast the next day's 24 hourly values of {company['target']}.",
             f"Study period {period}: days 1-126 are available for research in three rounds (days 1-84, 1-112, "
             "1-126).", f"{company['regime_name']} in this study period: {company['regimes'][regime]}", "",
             "Data dictionary (each source's values for a day are known before that day starts):"]
    for f, fam in enumerate(company["families"]):
        lines.append(f"- {fam['name']}:")
        for i, s in enumerate(srcs):
            if s["family"] == f:
                lines.append(f"  - {x_ids[i]}: {s['name']}. {s['description'][0].upper()}{s['description'][1:]}.")
    lines += ["", "Operating and event log:"]
    lines += [f"- Day {e['day']}: {e['text']}" for e in events]
    lines += ["", "Research question: " + QUESTION.format(target=company["target"])]
    return {"company": company["key"], "company_name": company["name"], "episode": period,
            "regime": company["regimes"][regime], "names": names, "text": "\n".join(lines) + "\n"}
