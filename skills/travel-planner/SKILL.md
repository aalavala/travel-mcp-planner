---
name: travel-planner
description: >-
  Optimizes flight and accommodation searches across all 6 configured travel MCPs
  (letsfg, booking, brek, tripadvisor, airbnb, google-flights). Use this skill
  whenever the user asks to search flights, find hotels/accommodations, compare
  travel prices, or plan a single- or multi-city trip.
---

# Travel Planner & Cross-MCP Arbitrage Skill

Follow this playbook automatically whenever the user asks to plan a trip, search flights, or compare hotels. **Never execute final payment/booking tools (`book_flight`, `book_hotel`); the user always completes checkout manually with their own credit card.**

---

## 0. Traveller Defaults (Boston / New Hampshire Home Base)

* **Home Airports (Default Origin / Final Return):**
  * **Primary Hub:** **`BOS`** (Boston Logan International Airport, MA) — default for international/transatlantic and major domestic routes.
  * **Nearby Alternative:** **`MHT`** (Manchester-Boston Regional Airport, NH) — always check `MHT` alongside `BOS` for domestic/North American routes (or 1-stop connections via hubs like `BWI`, `MDW`, `CLT`, `PHL`, `ORD`) to see if `MHT` is cheaper or easier to access.
* **Default Currency:** `USD`
* **Default Email for Reports:** `aalavala@yahoo.com` (and `aalavala@gmail.com`) via [`email_report.py`](./scripts/email_report.py)

---

## 1. Flight Search Rules (`letsfg`)

1. **Multi-City vs. Separate One-Ways (Always Check Both):**
   * For any multi-city or round-trip itinerary with multi-day stays in each city, run **both**:
     * `search_multi_city_flights` (`max_stops: 1`)
     * Separate `search_flights` one-way calls per leg (`max_stops: 1`)
   * **LetsFG Sequential One-Way Quirk:** When calling `search_flights` for Leg 2+ where `origin` matches the previous search's `destination`, `letsfg` returns `status: "not_started"` on the first call to nudge toward `search_multi_city_flights`. Immediately repeat the exact same `search_flights` call a second time to force standalone one-way pricing.
   * **Wait 10–12 seconds** and call `get_flight_results` with `limit: 25`.
2. **Strict Layover & Stop Filtering:**
   * Never recommend flights with `> 1` stop.
   * Filter out 1-stop flights with **layovers > 3.5 hours** (or overnight layovers), even if they are $10–$20 cheaper.
   * Always show both the **Cheapest Reasonable ($\le 1$ stop)** option and the **Best Nonstop** option, clearly noting secondary airports (e.g., `STN`/`LGW` vs. `LHR`, `CIA` vs. `FCO`).

---

## 2. Automatic Flight-Arrival-Aligned Hotel Dates

1. **Use Landing Date (`arrival_time`), Never Departure Date:**
   * Inspect the exact arrival timestamp (`arrival_time` / `arrival`) of the inbound flight for each city.
   * Example: If `NYC -> LON` departs `2026-11-18` at `21:50` and lands `2026-11-19` at `09:45`, set London hotel `check_in` to **`2026-11-19`** (never `2026-11-18`).
2. **Zero City Overlap:**
   * Ensure City A `check_out` equals the departure date of the flight from City A to City B, and City B `check_in` equals the landing date in City B.

---

## 3. Free-Cancellation & Quality Filtering

1. **Free Cancellation Only Until Flights Are Locked In:**
   * In `booking` (`search_hotels`): pass `free_cancellation: true` and `min_rating: 8`.
   * In `letsfg` (`search_hotels` -> `get_hotel_details`): filter for `refundable: true` and report the exact `free_cancellation_until` timestamp.
   * In `brek` (`search_accommodations`): pass `freeCancellationOnly: true` and `minRating: 8.0`.
   * In `airbnb` (`airbnb_search`, if applicable): compare top-rated whole-apartment options for stays of 3+ nights.
2. **Quality Floor:**
   * Only shortlist hotels with a rating **$\ge 8.0/10$** on Booking.com or **$\ge 4.2/5$** on Google/TripAdvisor and at least **500+ reviews**.

---

## 4. Cross-Connector Same-Hotel Side-by-Side Comparison

Before recommending a final hotel in each city, pick the top 1–2 candidate properties and compare the **exact same room category, board (Room Only vs. Breakfast), and Free Cancellation policy** side by side:

1. **`booking`:** Call `check_availability` with the hotel's URL/ID, `check_in`, `check_out`, and `adults`.
2. **`letsfg`:** Do **not** rely only on `get_hotel_results` (which only previews the 4 lowest rates, often non-refundable). Always call `get_hotel_details` (`search_id`, `hotel_code`) to expose all refundable and breakfast-included room rates.
3. **`brek`:** Since `brek` puts room-level pricing inside MCP `structuredContent`, [`brek_mcp_bridge.py`](./scripts/brek_mcp_bridge.py) (or [`fetch_brek_offers.py`](./scripts/fetch_brek_offers.py) via `python3 /Users/abhi/.gemini/config/skills/travel-planner/scripts/fetch_brek_offers.py get_accommodation_offers '{"hotelName":"...","destination":"...","checkinDate":"YYYY-MM-DD","checkoutDate":"YYYY-MM-DD","adults":2,"rooms":1,"currency":"USD"}'`) extracts its full room-rate JSON array. Always pass `hotelName` + `destination` (or the 24-char hex Brek `propertyId`), never a numeric Booking.com ID.
4. **`tripadvisor`:** Call `search_hotels`, `hotel_details`, and `compare_hotels` to cross-check guest ratings, review summaries, and TripAdvisor OTA pricing.
5. **All-In Price Normalization (City Taxes):**
   * Check `facts` in `letsfg` `get_hotel_details` for any pay-at-hotel municipal/city tax (e.g., `"Paid at the hotel, not in that total: USD 67.15 local tax"`).
   * Always add that tax to the `letsfg` rate in your comparison table so the user compares **100% apples-to-apples All-In Totals** against `booking`.

---

## 5. Output Format, Verification & Direct Checkout Links (Manual Payment Only)

Always present a clean Markdown summary table containing:
* **Flight Comparison Table:** Multi-City vs. Separate One-Ways ($\le 1$ stop vs. Nonstop), checking both **`BOS`** and **`MHT`** on home legs, with airline names, flight numbers, departure/arrival timestamps, and durations.
* **Hotel Side-by-Side Rate Matrix:** Exact room name, board, `free_cancellation_until` date, `booking` all-in price, `letsfg` all-in price, `brek`/`tripadvisor` price, and the **Winner & Savings**.
* **Direct Parameterized Checkout Links:** Include clickable URLs with `checkin`, `checkout`, and `group_adults` query parameters (e.g., `https://www.booking.com/hotel/...html?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD&group_adults=2`) so the user can click and pay with their own credit card.
* **Regression & Stack Verification:** Run `python3 /Users/abhi/.gemini/config/skills/travel-planner/scripts/verify_stack.py` (or `--live`) to verify date-alignment, layover filtering, tax normalization, and HTML email rendering.
* **HTML + Plain-Text Email Delivery Helper:** To email any saved Markdown report (with styled HTML tables + plain-text fallback) to `aalavala@gmail.com` via AWS SES, run:
  `python3 /Users/abhi/.gemini/config/skills/travel-planner/scripts/email_report.py /path/to/report.md "Subject Line"`
