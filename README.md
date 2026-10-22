# Travel MCP Planner & Cross-Connector Arbitrage Suite

An end-to-end multi-MCP travel optimization skill, bridge suite, and automated regression framework for **Google Antigravity**. Searches flights and accommodations across **6 travel MCP servers** in parallel while keeping final credit-card checkout 100% manual.

---

## Architecture & 6-MCP Stack

| MCP Connector | Implementation | Purpose |
| :--- | :--- | :--- |
| **`letsfg`** | `https://letsfg.co/mcp` | 300+ airlines/OTAs (`max_stops <= 1`) and wholesale hotel bedbanks (`get_hotel_details`). |
| **`booking`** | `hotelzero` Playwright + [`patches/hotelzero-browser.js`](./patches/hotelzero-browser.js) | Live Booking.com search (`free_cancellation: true`, `min_rating: 8`) & room-matrix availability (`check_availability`). |
| **`brek`** | [`brek_mcp_bridge.py`](./skills/travel-planner/scripts/brek_mcp_bridge.py) | Proxies `https://mcp.brek.com/mcp` and injects `structuredContent` room offers into `content[0].text` so room prices are never stripped. |
| **`airbnb`** | `@openbnb/mcp-server-airbnb` | Zero-API-key search for Guest-Favorite entire homes & apartments (`airbnb_search`, `airbnb_listing_details`). |
| **`google-flights`** | [`google_flights_mcp.py`](./skills/travel-planner/scripts/google_flights_mcp.py) | Zero-API-key stdio MCP server generating parameterized **Google Flights**, **Kayak ($\le 1$ stop)**, **Skyscanner**, and **Official Airline Checkout URLs**. |
| **`tripadvisor`** | `https://production.ai-mcp-extensibility-prd.tamg.cloud/.../mcp` | Hotel review scores, sub-ratings, and comparisons (`search_hotels`, `hotel_details`, `compare_hotels`). |

---

## Core Optimization Rules Enforced Automatically

1. **Multi-City vs. Separate One-Way Flights (`max_stops <= 1`, Layovers $\le 3.5\text{h}$):**
   * Runs both `search_multi_city_flights` and standalone `search_flights` per leg, checks both **Boston Logan (`BOS`)** and **Manchester-Boston Regional (`MHT`)**, and filters out layovers over 3.5 hours.
2. **Flight-Arrival-Aligned Hotel Dates:**
   * Aligns hotel check-in to the inbound flight's **landing date (`arrival_time`)** rather than its departure date—preventing wasted hotel nights on overnight transatlantic flights.
3. **Free Cancellation & $\ge 8.0/10$ Quality Floor:**
   * Filters strictly for refundable rates (`free_cancellation: true` / `refundable: true`) with exact `free_cancellation_until` timestamps.
4. **Cross-Connector Same-Hotel Rate Matrix & All-In Tax Normalization:**
   * Compares the exact same room category and board across `booking`, `letsfg`, and `brek` (plus `airbnb` entire homes) and adds pay-at-property municipal city taxes for true apples-to-apples totals.
5. **Multipart HTML Table + Plain-Text Email Delivery:**
   * [`email_report.py`](./skills/travel-planner/scripts/email_report.py) renders Markdown tables and pre-filled checkout links into styled HTML tables and delivers them via AWS SES.

---

## Repository Structure

```text
travel-mcp-planner/
├── README.md
├── mcp_config.example.json
├── patches/
│   └── hotelzero-browser.js
├── reports/
│   └── travel_mcp_verification_report.md
└── skills/
    └── travel-planner/
        ├── SKILL.md
        └── scripts/
            ├── brek_mcp_bridge.py
            ├── email_report.py
            ├── fetch_brek_offers.py
            ├── google_flights_mcp.py
            └── verify_stack.py
```

---

## Running the Regression & Verification Suite

```bash
# Run deterministic unit tests (date alignment, layover filter, tax normalization, HTML renderer, BOS vs MHT)
python3 skills/travel-planner/scripts/verify_stack.py

# Run live MCP smoke tests against Brek & TripAdvisor
python3 skills/travel-planner/scripts/verify_stack.py --live
```
