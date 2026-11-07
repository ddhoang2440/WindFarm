# WindFarm HKT — Turbine Anomaly Event Log UI Specification (`DESIGN.md` for Google Stitch)

## 1. Product Overview & Scope
- **Application Name:** WindFarm HKT — Turbine Anomaly & Event Log Console
- **Core Purpose:** Fetch API (`/api/v1/events`) and display a clean, real-time data table of Wind Turbine Anomaly Events logged into MongoDB (`events` collection) by the AI/ML Service, plus a modal/drawer to log a new anomaly event (`POST /api/v1/events`).
- **No Charts / No Telemetry Graphs:** Metrics and time-series charts (`wind_speed`, `power_output`) are handled externally in Datadog. This web frontend focuses strictly on **Event API fetching, filtering, and tabular anomaly logging**.
- **Device Target:** `DESKTOP` (`1440x900px` responsive web app).

---

## 2. Backend Data Contract (`models/event.py` & `event_router.py`)

### 2.1. Data Model (`EventInput` / `EventRecord`)
| Field Name | Type | Example Value | UI Representation in Table |
| :--- | :--- | :--- | :--- |
| `event_id` | `int` | `1730682410` | Monospace badge `#1730682410` |
| `asset_id` | `int` | `0` | Cyan/Indigo badge `Turbine #0` |
| `event_label` | `str` | `"anomaly"` | Crimson red status pill `⚠️ ANOMALY` |
| `event_start` | `datetime` (ISO 8601) | `"2021-08-03T07:30:00"` | Formatted timestamp `2021-08-03 07:30:00` |
| `event_end` | `datetime` (ISO 8601) | `"2021-08-03T07:30:05"` | Formatted timestamp `2021-08-03 07:30:05` (with duration badge) |
| `event_description` | `str` | `"ML phát hiện bất thường. Gió: 45.0 m/s"` | Highlighted anomaly log message |

### 2.2. API Endpoints Used by Frontend
- **`GET /api/v1/events?asset_id={optional}&limit={limit}`** (Headers: `Authorization: Bearer <API_TOKEN>`, `ngrok-skip-browser-warning: 1`) → Fetch list of anomaly events sorted newest first.
- **`POST /api/v1/events`** (Headers: `Authorization: Bearer <API_TOKEN>`) → Log a new anomaly event (`EventInput`).
- **`GET /`** → Check Backend health status (`{"message": "Backend is running"}`).

---

## 3. Design System Tokens (For Stitch)

- **Background Primary:** `#1E1B4B` to `#0F0D26` (Deep Indigo Dark Theme matching `layout.css`)
- **Header / Footer Surface:** `#15123A` (`rgba(21, 18, 58, 0.85)`)
- **Card / Table Container Surface:** Frosted Glass `rgba(30, 27, 75, 0.65)`, `backdrop-filter: blur(16px)`, border `1px solid rgba(255, 255, 255, 0.12)`, border-radius `16px`
- **Primary Brand Gradient:** `linear-gradient(135deg, #A78BFA 0%, #EC4899 100%)`
- **Anomaly Alert Accent (`event_label = "anomaly"`):** `#EF4444` (Crimson Red text/border with `rgba(239, 68, 68, 0.18)` pill background)
- **Asset Badge Accent (`asset_id`):** `#38BDF8` (Sky Cyan text with `rgba(56, 189, 248, 0.16)` background)
- **Healthy / Connected Accent:** `#10B981` (Emerald Green)
- **Typography:**
  - UI & Headings: `Outfit` (`500`, `600`, `700`)
  - Timestamps & IDs (`event_id`, `event_start`, `event_end`): `JetBrains Mono` (`tabular-nums`)

---

## 4. Screen Layout Specification

### A. Top Sticky Header (`68px` height)
- **Left:** Logo icon (`#A78BFA` → `#EC4899` gradient) + Title **WindFarm HKT** + subtitle pill `Anomaly Event Log`.
- **Right:**
  - **Backend Status Indicator:** Green dot `Backend Connected (:8000)` (or Offline warning).
  - **Auto-Fetch Toggle:** Pill button `🔄 Auto-Fetch: 5s (ON)` to poll new ML anomaly events automatically.
  - **API Config Button (`⚙️ Cấu hình API`):** Opens modal to set `BACKEND_URL` (Localhost or Ngrok) and Bearer `API_TOKEN`.
  - **Primary CTA Button (`+ Log Anomaly Event`):** Opens modal to send `POST /api/v1/events`.

### B. Compact Summary Strip (3 Stat Cards in 1 Row)
1. **Total Logged Events:** Count of events fetched from `/api/v1/events` (e.g., `12 Events`).
2. **Anomaly Count (`event_label: "anomaly"`):** Count of critical ML anomalies in crimson red.
3. **Latest Detected Anomaly:** Shows `asset_id` (`Turbine #0`) and `event_end` timestamp of the most recent anomaly.

### C. Filter & Action Toolbar
- **Search Input:** Search by `event_id` or `event_description` (e.g. `"Gió: 45.0 m/s"`).
- **Asset Filter (`asset_id`):** Dropdown `[Tất cả Tuabin]` | `[Turbine #0]` | `[Turbine #1]` | `[Turbine #2]`.
- **Label Filter (`event_label`):** Dropdown `[Tất cả nhãn]` | `[anomaly]` | `[warning]` | `[maintenance]`.
- **Refresh Button (`🔄 Fetch API ngay`):** Triggers `GET /api/v1/events` immediately.

### D. Main Event Log Table (`EventRecord` Table)
Full-width glassmorphism table displaying the exact 6 fields of `EventInput`:
1. **`EVENT ID` (`event_id`):** `#1730682410` (Monospace bold)
2. **`TURBINE (`asset_id`)`:** Badge `🌀 Turbine #0`
3. **`LABEL (`event_label`)`:** Red glowing pill `🚨 ANOMALY`
4. **`START TIME (`event_start`)`:** `2021-08-03 07:30:00`
5. **`END / DETECTED (`event_end`)`:** `2021-08-03 07:30:05`
6. **`ANOMALY DESCRIPTION (`event_description`)`:** `"ML phát hiện bất thường. Gió: 45.0 m/s"`

### E. Modal 1: Log New Anomaly Event (`POST /api/v1/events`)
- Clean form with exact fields: `event_id` (auto-generated unix timestamp), `asset_id`, `event_label` (`anomaly`), `event_start`, `event_end`, and `event_description`.
- Submit button sends `POST /api/v1/events` with Bearer Token and appends to the table.

---

## 5. Ready-to-Copy Prompt for Google Stitch

Copy and paste the prompt below directly into **Google Stitch** (`https://stitch.withgoogle.com`):

```text
Design a focused, modern dark glassmorphism web screen (1440x900 Desktop) for "WindFarm HKT — Turbine Anomaly Event Log Console".
IMPORTANT: Do NOT include any charts or graphs. Focus strictly on API status, a compact summary strip, filter controls, and a clean, high-contrast Anomaly Event Log Data Table that displays data fetched from GET /api/v1/events.

Color Palette & Typography:
- Background: Deep indigo (#0F0D26 to #1E1B4B), frosted glass cards (rgba(30, 27, 75, 0.65) with 1px subtle border rgba(255,255,255,0.12)).
- Accents: Violet-to-pink brand gradient (#A78BFA to #EC4899), crimson red (#EF4444) for "anomaly" badges, sky cyan (#38BDF8) for turbine asset_id badges, emerald green (#10B981) for API online status.
- Font: Outfit for UI labels and JetBrains Mono for event_id and timestamps.

Screen Layout:
1. Top Header Bar:
   - Left: Brand logo "WindFarm HKT" + badge "Turbine Anomaly Logger".
   - Right: Green connection badge "API Connected: /api/v1/events", Auto-refresh toggle pill "Auto-Poll: 5s", API Settings button (gear icon for Base URL & Bearer Token), and a primary gradient button "+ Log Anomaly Event".
2. Compact 3-Card Summary Row:
   - Card 1: "TOTAL LOGGED EVENTS" -> "24" (Collection: events).
   - Card 2: "ACTIVE AI ANOMALIES" -> "24" in crimson red (event_label: anomaly).
   - Card 3: "LATEST ANOMALY DETECTED" -> "Turbine #0 • 2021-08-03 09:20:02".
3. Filter & Fetch Toolbar:
   - Search bar ("Tìm theo event_id hoặc event_description...").
   - Dropdown filter for asset_id ("All Turbines", "Turbine #0", "Turbine #1").
   - Dropdown filter for event_label ("All Labels", "anomaly", "warning").
   - "Fetch / Refresh API" button.
4. Main Anomaly Event Table (Full width, 6 exact columns from backend model EventInput):
   - Column 1: EVENT ID (event_id) — monospace e.g. "#1730682410", "#1730682450"
   - Column 2: ASSET ID (asset_id) — cyan badge "Turbine #0"
   - Column 3: EVENT LABEL (event_label) — glowing red pill "ANOMALY"
   - Column 4: EVENT START (event_start) — monospace "2021-08-03 07:30:00"
   - Column 5: EVENT END (event_end) — monospace "2021-08-03 07:30:05"
   - Column 6: EVENT DESCRIPTION (event_description) — "ML phát hiện bất thường. Gió: 45.0 m/s"
```
