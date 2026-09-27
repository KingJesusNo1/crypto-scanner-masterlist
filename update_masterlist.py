import json
import urllib.request
from datetime import datetime, timezone

BITVAVO_URL = "https://api.bitvavo.com/v2/markets"
GATE_EU_URL = "https://api.gateeu.com/api/v4/spot/currency_pairs"

HEADERS = {
    "User-Agent": "crypto-scanner-masterlist/1.0",
    "Accept": "application/json",
}


def get_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


assets = {}


def add_asset(symbol, exchange, pair):
    symbol = symbol.upper()

    if symbol not in assets:
        assets[symbol] = {
            "symbol": symbol,
            "exchanges": [],
            "pairs": []
        }

    if exchange not in assets[symbol]["exchanges"]:
        assets[symbol]["exchanges"].append(exchange)

    assets[symbol]["pairs"].append({
        "exchange": exchange,
        "pair": pair
    })


# BITVAVO
bitvavo = get_json(BITVAVO_URL)

for market in bitvavo:
    if market.get("status") != "trading":
        continue

    pair = market.get("market", "")
    base = market.get("base")

    if not base and "-" in pair:
        base = pair.split("-")[0]

    if base:
        add_asset(base, "BITVAVO", pair)


# GATE EUROPE
gate = get_json(GATE_EU_URL)

for market in gate:
    if market.get("trade_status") != "tradable":
        continue

    base = market.get("base")
    pair = market.get("id", "")

    if base:
        add_asset(base, "GATE_EUROPE", pair)


# MASTERLIST
masterlist = sorted(
    assets.values(),
    key=lambda x: x["symbol"]
)

bitvavo_assets = sum(
    1 for x in masterlist if "BITVAVO" in x["exchanges"]
)

gate_assets = sum(
    1 for x in masterlist if "GATE_EUROPE" in x["exchanges"]
)

both = sum(
    1 for x in masterlist
    if "BITVAVO" in x["exchanges"]
    and "GATE_EUROPE" in x["exchanges"]
)

output = {
    "last_verified": datetime.now(timezone.utc).isoformat(),
    "coverage": "FULL",
    "statistics": {
        "bitvavo_assets": bitvavo_assets,
        "gate_europe_assets": gate_assets,
        "both_exchanges": both,
        "unique_assets": len(masterlist)
    },
    "assets": masterlist
}

with open("masterlist.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(json.dumps(output["statistics"], indent=2))
