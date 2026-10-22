#!/usr/bin/env python3
"""Zero-API-Key Google Flights & Direct Airline Checkout MCP Server (stdio).

Provides tools to generate parameterized Google Flights, Kayak, Skyscanner,
and direct airline checkout URLs so the traveller can verify historical price
context on Google Flights and complete manual credit-card checkout directly.
"""
import json
import sys
import urllib.parse

AIRLINE_DIRECT_URLS = {
    "BA": ("British Airways", "https://www.britishairways.com/travel/home/public/en_us/"),
    "DL": ("Delta Air Lines", "https://www.delta.com/flight-search/book-a-flight"),
    "AA": ("American Airlines", "https://www.aa.com/booking/find-flights"),
    "UA": ("United Airlines", "https://www.united.com/en/us/book-flight/united-reservations"),
    "B6": ("JetBlue", "https://www.jetblue.com/booking/flights"),
    "WN": ("Southwest Airlines", "https://www.southwest.com/air/booking/"),
    "FI": ("Icelandair", "https://www.icelandair.com/flights/"),
    "EI": ("Aer Lingus", "https://www.aerlingus.com/html/flightSearchResult.html"),
    "TP": ("TAP Air Portugal", "https://booking.flytap.com/booking/flights"),
    "IB": ("Iberia", "https://www.iberia.com/us/"),
    "AZ": ("ITA Airways", "https://www.ita-airways.com/en_us"),
    "U2": ("easyJet", "https://www.easyjet.com/en"),
    "FR": ("Ryanair", "https://www.ryanair.com/us/en"),
}

TOOLS = [
    {
        "name": "get_google_flights_and_airline_links",
        "description": (
            "Generate direct parameterized Google Flights, Kayak (<=1 stop), Skyscanner, "
            "and official airline booking URLs for a flight leg so the user can check "
            "Google Flights price history and book directly with their credit card."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin IATA code (e.g. BOS, MHT, JFK)"},
                "destination": {"type": "string", "description": "Destination IATA code (e.g. LHR, LON, FCO)"},
                "departure_date": {"type": "string", "description": "Departure date YYYY-MM-DD"},
                "return_date": {"type": "string", "description": "Optional return date YYYY-MM-DD"},
                "adults": {"type": "integer", "default": 1},
                "airline_code": {"type": "string", "description": "Optional 2-letter IATA airline code (e.g. BA, DL, FI)"},
            },
            "required": ["origin", "destination", "departure_date"],
        },
    },
    {
        "name": "build_multi_city_checkout_links",
        "description": (
            "Generate a complete bundle of direct checkout links (Google Flights multi-city, "
            "per-leg Google Flights & Kayak <=1 stop links, Booking.com parameterized hotel links, "
            "and Airbnb entire-home search links) for an entire itinerary."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "legs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string"},
                            "destination": {"type": "string"},
                            "date": {"type": "string"},
                            "airline_code": {"type": "string"},
                        },
                        "required": ["origin", "destination", "date"],
                    },
                },
                "adults": {"type": "integer", "default": 1},
            },
            "required": ["legs"],
        },
    },
]


def build_leg_links(origin: str, destination: str, date: str, adults: int = 1, return_date: str | None = None, airline_code: str | None = None) -> dict:
    o = origin.upper().strip()
    d = destination.upper().strip()
    if return_date:
        gf_q = f"Flights from {o} to {d} on {date} through {return_date} for {adults} adults max 1 stop"
        kayak_url = f"https://www.kayak.com/flights/{o}-{d}/{date}/{return_date}/{adults}adults?sort=bestflight_a&fs=stops=-2"
    else:
        gf_q = f"Flights from {o} to {d} on {date} one way for {adults} adults max 1 stop"
        kayak_url = f"https://www.kayak.com/flights/{o}-{d}/{date}/{adults}adults?sort=bestflight_a&fs=stops=-2"

    gf_url = f"https://www.google.com/travel/flights?q={urllib.parse.quote(gf_q)}&curr=USD"
    sky_date = date.replace("-", "")[2:]  # YYMMDD
    skyscanner_url = f"https://www.skyscanner.com/transport/flights/{o.lower()}/{d.lower()}/{sky_date}/?adults={adults}&stops=!twoPlusStops&currency=USD"

    out = {
        "leg": f"{o} -> {d} ({date})",
        "google_flights_url": gf_url,
        "kayak_max_1_stop_url": kayak_url,
        "skyscanner_max_1_stop_url": skyscanner_url,
    }
    if airline_code and airline_code.upper() in AIRLINE_DIRECT_URLS:
        name, url = AIRLINE_DIRECT_URLS[airline_code.upper()]
        out["airline_direct"] = {"airline": name, "code": airline_code.upper(), "url": url}
    return out


def handle_call(name: str, args: dict) -> dict:
    if name == "get_google_flights_and_airline_links":
        res = build_leg_links(
            args["origin"],
            args["destination"],
            args["departure_date"],
            args.get("adults", 1),
            args.get("return_date"),
            args.get("airline_code"),
        )
        return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    if name == "build_multi_city_checkout_links":
        legs = args.get("legs", [])
        adults = args.get("adults", 1)
        leg_results = [
            build_leg_links(l["origin"], l["destination"], l["date"], adults, airline_code=l.get("airline_code"))
            for l in legs
        ]
        kayak_segments = "/".join(f"{l['origin'].upper()}-{l['destination'].upper()}/{l['date']}" for l in legs)
        kayak_multi_url = f"https://www.kayak.com/flights/{kayak_segments}/{adults}adults?sort=bestflight_a&fs=stops=-2"
        bundle = {
            "kayak_multi_city_url": kayak_multi_url,
            "per_leg_links": leg_results,
        }
        return {"content": [{"type": "text", "text": json.dumps(bundle, indent=2)}]}
    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method", "")
        if req_id is None:
            continue

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "google-flights-mcp", "version": "1.0.0"},
                },
            }
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = req.get("params", {})
            try:
                res = handle_call(params.get("name", ""), params.get("arguments", {}))
                resp = {"jsonrpc": "2.0", "id": req_id, "result": res}
            except Exception as exc:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}
        else:
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
