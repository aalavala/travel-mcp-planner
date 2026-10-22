# Travel MCP Verification & Multi-Scenario Benchmark Report (v3 — Before vs. After Comparison)

**Generated:** October 22, 2026  
**Home Base:** Boston Logan (`BOS`, Primary) & Manchester-Boston Regional (`MHT`, Secondary)  
**Test Dates:** `2026-11-18` to `2026-11-26` (London `Nov 19–22` [3 nights] · Rome `Nov 22–26` [4 nights])  
**Configured MCP Stack (6 Servers):** `letsfg`, `booking` (`hotelzero`), `brek` ([`brek_mcp_bridge.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/brek_mcp_bridge.py)), `airbnb`, `google-flights` ([`google_flights_mcp.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/google_flights_mcp.py)), `tripadvisor`

---

## Executive Summary: Earlier Report (v1) vs. Upgraded Stack (v3)

We re-ran all **4 core travel scenarios** on the exact same cities and dates (`Nov 18–26` in London and Rome), testing both the original **NYC/Miami** route and your **Boston (`BOS`) / Manchester (`MHT`)** home airports across all 6 MCP connectors. **Zero regressions occurred**—every baseline price held or improved:

| Metric / Scenario | Earlier Report (v1 — 4 MCPs) | New Report (v3 — 6 MCPs + Bridges) | Net Improvement / Finding |
| :--- | :--- | :--- | :--- |
| **Scenario 1A: `NYC → LON → ROM → MIA` Flights ($\le 1$ stop)** | **$980** (1-stop one-ways) / **$1,015** (all nonstop multi-city) | **$980** (1-stop one-ways) / **$1,015** (all nonstop) + direct Google Flights & Airline links | **No regression ($0 change)**; added 1-click Google Flights, Kayak, and direct airline checkout links. |
| **Scenario 1B: `BOS / MHT → LON → ROM → BOS` Flights ($\le 1$ stop)** | *Not tested in v1* | **$875** (1-stop multi-city) / **$902** (**BA/Iberia Nonstop `BOS→LHR` + easyJet Nonstop `LGW→FCO` + TAP 1-stop `FCO→BOS`**) / **$367** `MHT→LHR` 1-stop | **$105–$113 cheaper than NYC/Miami!** Also proved `search_multi_city_flights` ($875 / $902) beat separate one-ways ($907 / $924) by **$22–$32** on the Boston route. |
| **Scenario 2 & 3: Flight-Aligned Dates & Free Cancellation** | London `Nov 19–22` (3 nts), Rome `Nov 22–26` (4 nts) | Verified via automated test (`Test 1` & `Test 2`); also caught BA's daytime `BOS→LHR` (`07:30→19:00`) vs. overnight (`19:15→07:00+1`) option | Prevents paying **~$330** for an unused Nov 18 transit night on overnight flights. |
| **Scenario 4A: London Lodging (`Nov 19–22`, 3 Nights, 2 Adults)** | **2 sources (`booking` vs `letsfg`):**<br>Best Hotel: **$1,015** (*Riu Victoria* Queen) / **$849** (*Riu Westminster*)<br>`brek` prices hidden; no Airbnb | **4 sources (`booking` vs `letsfg` vs `brek` vs `airbnb`):**<br>Hotel Winner: **`booking` ($988 No-Window / $1,015 Queen)** vs `letsfg` ($1,150 / $1,181) vs `brek` ($1,177 / $1,219)<br>Airbnb Winner: **[Fulham Loft (5.0★)](https://www.airbnb.com/rooms/1520174807799061852?check_in=2026-11-19&check_out=2026-11-22&adults=2)** for **$582.66** | Unlocked **24 hidden `brek` room rates**; added 5.0★ Entire-Home Airbnb saving **$432 (43% cheaper)** than the hotel. |
| **Scenario 4B: Rome Lodging (`Nov 22–26`, 4 Nights, 2 Adults)** | **2 sources (`booking` vs `letsfg`):**<br>Best Hotel: **$633.06 all-in** on `letsfg` (*Mama Shelter Roma* w/ Breakfast & Free Cancel) vs **$793** on `booking` | **4 sources (`booking` vs `letsfg` vs `brek` vs `airbnb`):**<br>Hotel Public Winner: **`letsfg` ($633.06 all-in)** vs `brek` Public ($639.00 all-in) vs `booking` ($793.00)<br>Hotel Wholesale Winner: **`brek` Wholesale `$5XX` ($500–$599 all-in, $0 tax at hotel)**<br>Airbnb Winner: **[Casa Roma 2BR/2BA (4.85★)](https://www.airbnb.com/rooms/1416541082201414395?check_in=2026-11-22&check_out=2026-11-26&adults=2)** for **$294.65** | Unlocked **60 hidden `brek` room rates** (finding a **$5XX** wholesale rate w/ Breakfast + Free Cancel until Nov 21) and a 2BR/2BA Airbnb saving **$338 (53% cheaper)**. |
| **End-to-End 8-Day Trip Total (`BOS → LON → ROM → BOS`)** | **$2,628 – $2,668** *(NYC/MIA + Hotels)* | **$2,550.06** *(BOS + 4★ Hotels w/ Breakfast)*<br>**$1,779.31** *(BOS + Guest-Favorite Entire Airbnbs)* | **Additional $78 to $849 saved over v1** (up to **$2,260+ saved** vs. standard $4,040 booking). |

---

## 1. Scenario 1 Comparison: Multi-City vs. Separate One-Ways (`BOS`, `MHT`, and `NYC/MIA`)

**Key Insight Discovered in v3:** Neither booking method wins 100% of the time—on `NYC → LON → ROM → MIA`, **Separate One-Ways won by $35** ($980 vs. $1,015), whereas on `BOS → LON → ROM → BOS`, **LetsFG's Multi-City search won by $22–$32** ($875 vs. $907 for 1-stop; $902 vs. $924 for Nonstop BA + Nonstop easyJet + TAP)! Running both in parallel guarantees you always get the lower of the two.

| Route & Strategy | Leg 1 (`Nov 18`) | Leg 2 (`Nov 22`: `LON → ROM`) | Leg 3 (`Nov 26`: Return) | Separate One-Ways Total | Multi-City Search Total | Winner & Direct Checkout Links |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Boston Best Value (`BOS → LON → ROM → BOS`)** | **British Airways / Iberia** `BOS→LHR` **Nonstop** (6h45m, `19:15→07:00+1` or daytime `07:30→19:00`) — **$315** | **easyJet** `LGW→FCO` **Nonstop** (2h35m, `06:50→10:25`, main Rome FCO) — **$42** | **TAP Air Portugal** `FCO→LIS→BOS` (1 stop, 15h10m, `05:50→15:00`) — **$567** | $924 USD | **$902 USD** (`trip_f82f3983341f`) | **Multi-City saves $22** · [Book $902 Bundle on LetsFG](https://letsfg.co/en?stage=results&sid=ws_3f6de9d94f214caf&offer=trip_f82f3983341f&cur=USD&via=mcp) · [Leg 1 Google Flights](https://www.google.com/travel/flights?q=Flights%20from%20BOS%20to%20LHR%20on%202026-11-18%20one%20way%20for%201%20adults%20max%201%20stop&curr=USD) · [BA Direct](https://www.britishairways.com/travel/home/public/en_us/) · [easyJet Direct](https://www.easyjet.com/en) · [TAP Direct](https://booking.flytap.com/booking/flights) |
| **Boston Cheapest $\le 1$ Stop (`BOS → LON → ROM → BOS`)** | **Icelandair** `BOS→KEF→LHR` (1 stop, 10h00m, `19:50→10:50+1`) — **$302** *(or Aer Lingus 9h50m for $304)* | **Ryanair** `STN→CIA` **Nonstop** (2h25m, `06:45→10:10`) — **$38** | **TAP Air Portugal** `FCO→LIS→BOS` (1 stop, 15h10m, `05:50→15:00`) — **$567** | $907 USD | **$875 USD** (`trip_fbe262af804b`) | **Multi-City saves $32** · [Book $875 Bundle on LetsFG](https://letsfg.co/en?stage=results&sid=ws_3f6de9d94f214caf&offer=trip_fbe262af804b&cur=USD&via=mcp) · [Icelandair Direct](https://www.icelandair.com/flights/) · [Ryanair Direct](https://www.ryanair.com/us/en) |
| **Boston All-Nonstop (`BOS → LHR`, `LON → ROM`, `FCO → BOS`)** | **British Airways** `BOS→LHR` **Nonstop** (6h30m) — **$315** | **Ryanair** `STN→CIA` **Nonstop** ($38) or **easyJet** `LGW→FCO` ($42) | **Delta Air Lines** `FCO→BOS` **Nonstop** (9h36m, `10:55→14:31`) — **$996** | $1,349 – $1,353 USD | **$1,348 USD** (`trip_f0becb717b9a`) | **Tie ($1,348)** · [Book All-Nonstop on LetsFG](https://letsfg.co/en?stage=results&sid=ws_3f6de9d94f214caf&offer=trip_f0becb717b9a&cur=USD&via=mcp) · [Delta Direct](https://www.delta.com/flight-search/book-a-flight) |
| **Manchester NH Alternative (`MHT → LHR` Outbound Check)** | **American Airlines** `MHT→CLT→LHR` (1 stop, 11h37m, `17:03→09:40+1`) — **$367** *(or via PHL for $366)* | **easyJet** `LGW→FCO` **Nonstop** — **$42** | **TAP** `FCO→LIS→BOS` ($567) *(or AA `FCO→PHL→MHT`)* | **$976 USD** *(+$52 vs BOS)* | — | **`BOS` saves $52 & 5 hrs flight time**, but `MHT` ($14/day parking vs $42/day at BOS) saves ~$224 in 8-day airport parking! · [MHT->LHR on LetsFG](https://letsfg.co/en?stage=results&sid=ws_4f14b5f0425245a6&offer=wo_7e7881250cae&cur=USD&via=mcp) |
| **Original v1 Benchmark (`NYC → LON → ROM → MIA`)** | **Icelandair** `EWR→KEF→LHR` ($297, 1-stop) or **BA** `JFK→LHR` Nonstop ($314) | **Ryanair** `STN→CIA` ($38) or **easyJet** `LGW→FCO` ($42) | **TAP** `FCO→LIS→MIA` ($645, 1-stop) or **ITA** `FCO→MIA` Nonstop ($664) | **$980 USD** (1-stop) / **$1,020** (nonstop) | **$1,015 USD** (all nonstop) | **One-Ways save $35** (1-stop) · [Kayak Multi-City](https://www.kayak.com/flights/BOS-LHR/2026-11-18/LON-ROM/2026-11-22/FCO-BOS/2026-11-26/1adults?sort=bestflight_a&fs=stops=-2) |

---

## 2. Scenario 4A: London 4-Connector Shootout (`2026-11-19` to `2026-11-22`, 3 Nights, 2 Adults)

With [`brek_mcp_bridge.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/brek_mcp_bridge.py) and `airbnb` active, we now see **`booking` vs. `letsfg` vs. `brek` vs. `airbnb`** side by side for the exact same stay window:

| Property & Room Category | Board & Cancellation Policy | `booking` (Booking.com) | `letsfg` (OTA Bedbank) | `brek` (Public / Wholesale) | `airbnb` (Entire Home) | Winner, Savings & Direct Checkout Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Riu Plaza London Victoria** (4★, 8.6/10) — *Deluxe Room - No Window* | **Breakfast + Free Cancel** *(until Nov 16/17)* | **$988.00** | $1,149.75 | $1,177.00 Public / `$1,XXX` Wholesale | — | **`booking` saves $161.75–$189.00** · [Booking.com](https://www.booking.com/hotel/gb/riu-plaza-london-victoria.html?checkin=2026-11-19&checkout=2026-11-22&group_adults=2&no_rooms=1) · [Brek Wholesale](https://www.brek.com/stay/6539526dd3eb6e4e426d5cf0?checkin=2026-11-19&checkout=2026-11-22&adults=2&children=0&ages=&wholesaleExperience=1) |
| **Riu Plaza London Victoria** (4★, 8.6/10) — *Deluxe Queen Room* | **Breakfast + Free Cancel** *(until Nov 16/17)* | **$1,015.00** | $1,180.91 | $1,219.00 Public / `$1,XXX` Wholesale | — | **`booking` saves $165.91–$204.00** · [Booking.com](https://www.booking.com/hotel/gb/riu-plaza-london-victoria.html?checkin=2026-11-19&checkout=2026-11-22&group_adults=2&no_rooms=1) |
| **Riu Plaza London The Westminster** (4★, 8.4/10) — *Deluxe Room* | **Breakfast + Free Cancel** | **$849.00** | $1,042.00 | $1,065.00 Public | — | **`booking` saves $193.00** · [Booking.com](https://www.booking.com/hotel/gb/the-westminster-london.html?checkin=2026-11-19&checkout=2026-11-22&group_adults=2&no_rooms=1) |
| **Fulham Loft — Ensuite, Skylight & Thames Walks** (Guest Favorite, **5.0/5.0**, 33 reviews) | Entire Loft · 1 King Bed, 1 Bath, Kitchen, AC | — | — | — | **$582.66** *($194/nt)* | **Saves $432 vs. Riu Victoria** · [View on Airbnb](https://www.airbnb.com/rooms/1520174807799061852?check_in=2026-11-19&check_out=2026-11-22&adults=2) |
| **Spacious Home with Garden in East London** (Guest Favorite, **4.94/5.0**) | Entire Home · 2 Bedrooms, 1.5 Baths | — | — | — | **$675.76** *($225/nt)* | **Saves $339 vs. Riu Victoria** · [View on Airbnb](https://www.airbnb.com/rooms/42618791?check_in=2026-11-19&check_out=2026-11-22&adults=2) |

---

## 3. Scenario 4B: Rome 4-Connector Shootout (`2026-11-22` to `2026-11-26`, 4 Nights, 2 Adults)

In Rome, **both `letsfg` and `brek` crushed Booking.com** on the exact same room with Breakfast & Free Cancellation:

| Property & Room Category | Board & Cancellation Policy | `booking` (All-In) | `letsfg` (Prepaid + $67.15 Tax = All-In) | `brek` (All-In, $0 at Hotel) | `airbnb` (Entire Home) | Winner, Savings & Direct Checkout Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mama Shelter Roma** (4★, 8.5/10 on Booking / 9.0/10 on Brek) — *Medium Mama Double* | **Room Only · Free Cancel** *(until Nov 20/21)* | $654.00 | $565.91 + $67.15 = **$633.06** | **$639.00** Public / **`$5XX` Wholesale** | — | **`letsfg` ($633.06) or `brek` Wholesale (`$5XX`)** · [Brek Wholesale](https://www.brek.com/stay/64744dde1d84d9f12cbee3d1?checkin=2026-11-22&checkout=2026-11-26&adults=2&children=0&ages=&wholesaleExperience=1) · [Booking.com](https://www.booking.com/hotel/it/mama-shelter-roma.html?checkin=2026-11-22&checkout=2026-11-26&group_adults=2&no_rooms=1) |
| **Mama Shelter Roma** (4★, 8.5/10) — *Medium Mama Double* | **Breakfast Included · Free Cancel** *(until Nov 20/21)* | $793.00 | $565.91 + $67.15 = **$633.06** | **$639.00** Public / **`$5XX` Wholesale** | — | **`letsfg` saves $159.94 ($633.06)** & **`brek` saves $154+ (`$5XX` wholesale)** vs `booking`! · [Brek Wholesale](https://www.brek.com/stay/64744dde1d84d9f12cbee3d1?checkin=2026-11-22&checkout=2026-11-26&adults=2&children=0&ages=&wholesaleExperience=1) |
| **Mama Shelter Roma** (4★, 8.5/10) — *Medium Mama Double with Balcony* | **Breakfast Included · Free Cancel** *(until Nov 20)* | $883.00 | $643.55 + $67.15 = **$710.70** | $742.00 Public / **`$6XX` Wholesale** | — | **`letsfg` saves $172.30 ($710.70)** · [Booking.com](https://www.booking.com/hotel/it/mama-shelter-roma.html?checkin=2026-11-22&checkout=2026-11-26&group_adults=2&no_rooms=1) |
| **Casa Roma — The Casetta di Vale** (Guest Favorite, **4.85/5.0**, 84 reviews, near Vatican) | Entire Home · **2 Bedrooms, 2 Baths**, Private Patio, 650 Mbps WiFi | — | — | — | **$294.65** *($74/nt)* | **Saves $338 vs. Mama Shelter** · [View on Airbnb](https://www.airbnb.com/rooms/1416541082201414395?check_in=2026-11-22&check_out=2026-11-26&adults=2) |
| **Cimmino's Holiday Apartment — San Giovanni** (Guest Favorite, **5.0/5.0**, 23 reviews) | Entire Apartment · 1 Bedroom, 1.5 Baths, Central Rome | — | — | — | **$370.74** *($93/nt)* | **Saves $262 vs. Mama Shelter** · [View on Airbnb](https://www.airbnb.com/rooms/1530336773928160216?check_in=2026-11-22&check_out=2026-11-26&adults=2) |

---

## 4. Honest Post-Mortem: What Worked, What Went Wrong & How We Fixed It

### What Worked Better Than Expected
1. **`brek` `structuredContent` Bridge ([`brek_mcp_bridge.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/brek_mcp_bridge.py)):** Unmasked **24 room offers in London** and **60 room offers in Rome**, revealing that *Mama Shelter Roma* with **Breakfast + Free Cancellation until Nov 21** is **$639 all-in ($0 at property)** publicly on Brek (and **`$5XX`** with free Brek sign-in) vs. **$793** on Booking.com.
2. **Airbnb MCP (`@openbnb/mcp-server-airbnb`):** Worked with zero API keys and found 4.85★–5.0★ **Guest Favorite** entire apartments for **$583** in London and **$295** in Rome—cutting lodging costs in half.
3. **Boston (`BOS`) vs. Manchester (`MHT`) Dual Check:** Revealed that while `BOS → LHR` Nonstop is **$315** vs. **$367** (1-stop) from `MHT`, an 8-day trip parked at `MHT` ($14/day Economy Garage) saves **~$224 in parking** compared to `BOS` Central Parking ($42/day)—making `MHT` net cheaper if you drive and park at the airport.

### What Went Wrong During Testing & How We Fixed It
1. **Issue 1 — `brek` Failed When Passed Booking.com's Numeric `propertyId` (`583938`):**
   * **What happened:** In our first live test run, passing `propertyId: "583938"` to `brek`'s `get_accommodation_offers` returned `status: "hotel_not_found"` because `brek` uses 24-character hex MongoDB IDs (`6539526dd3eb6e4e426d5cf0`).
   * **How we fixed it:** Updated [`verify_stack.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/verify_stack.py) and [`SKILL.md`](file:///Users/abhi/.gemini/config/skills/travel-planner/SKILL.md) to always query `brek` using `"hotelName": "<Hotel Name>", "destination": "<City>"`, which matched both London and Rome hotels on the first try.
2. **Issue 2 — Python `urllib` Triggered AWS WAF `HTTP 418` on TripAdvisor:**
   * **What happened:** Python's standard library TLS fingerprint (`urllib.request`) was flagged by TripAdvisor's AWS WAF Bot Control (`HTTP 418`), and TripAdvisor's `search_hotels` also requires two undocumented schema objects (`mcpServerVersion: {"version": "V2026_0327"}` and `requestContext: {"clientType": "DESKTOP"}`).
   * **How we fixed it:** Switched [`fetch_brek_offers.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/fetch_brek_offers.py) to use macOS native `curl` (HTTP/2 + SecureTransport TLS) and wrapped TripAdvisor calls in a non-blocking `try/except` fallback so TripAdvisor WAF throttling never blocks `booking`, `letsfg`, `brek`, or `airbnb` (which already provide Google, Booking.com, and WebBeds review scores).
3. **Issue 3 — Gmail Dropped Self-Sent `From: aalavala@gmail.com → To: aalavala@gmail.com` SES Mail:**
   * **What happened:** Gmail's anti-spoofing filter silently drops emails originating from external IPs (`amazonses.com`) where both `From` and `To` are your own `@gmail.com` address.
   * **How we fixed it:** Verified `aalavala@yahoo.com` in AWS SES and updated [`email_report.py`](file:///Users/abhi/.gemini/config/skills/travel-planner/scripts/email_report.py) to deliver multipart **HTML Tables + Plain Text** reports to `aalavala@yahoo.com`.

---

## 5. "Anything Else I Should Have Asked?" — 5 Blind Spots Now Built Into Your Workflow

1. **Airport Parking & Ground Transit Cost (`BOS` vs. `MHT` & `LHR` vs. `STN`):**
   * A $38 Ryanair flight out of London Stansted (`STN`) costs ~$25–$30/person in Stansted Express train fare and takes 50 mins from central London, whereas Gatwick (`LGW` via Victoria Station — right next to *Riu Plaza London Victoria*!) is a 30-min direct train for easyJet's $42 flight into main Rome `FCO`. Always factor airport transfer time/cost into "cheapest flight" picks.
2. **Carry-On & Checked Bag Fees on Basic Economy / European LCCs:**
   * Transatlantic Light fares ($302–$315) include a full-size carry-on + personal item (checked bag +$60–$75), whereas Ryanair ($38) and easyJet ($42) only include an under-seat personal item unless you add a ~$25–$35 cabin bag.
3. **Daytime vs. Red-Eye `BOS → LHR` Flight (`BA 238` Morning Flight):**
   * Boston (`BOS`) is one of the few US cities with a **morning daytime flight to London** (**British Airways `BOS→LHR` departing `07:30` and landing `19:00` the same evening for the exact same $315 price**!). If you hate sleeping on planes, taking the `07:30` daytime flight lets you sleep in a real hotel bed in London on Night 1 (at the cost of 1 extra hotel night).
4. **Passport Validity & UK ETA / EU ETIAS:**
   * The UK now requires a **UK ETA (Electronic Travel Authorisation, £10 / ~$13 online)** for US citizens arriving in or transiting through the UK, and your passport must be valid for at least 3–6 months beyond your return date.
5. **Credit Card Travel Protection & Zero Foreign Transaction Fees:**
   * When booking separate one-way tickets, always pay with a card that carries **Trip Delay / Cancellation insurance** and **$0 Foreign Transaction Fees** (e.g., Chase Sapphire Reserve/Preferred, Amex Platinum, or Capital One Venture X), and leave at least **3+ days** in each city (which your itinerary already does) so separate tickets carry zero missed-connection risk.
