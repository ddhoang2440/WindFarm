# 🎬 Video Presentation Script — WindFarm HKT
## Project: WindFarm HKT — SCADA Monitoring & AI Anomaly Detection Console

---

## 📌 General Video Information
* **Target Duration:** 5 – 7 minutes (Standard for final capstone defense, technical showcase, or portfolio demo).
* **Target Audience:** Professors, academic evaluators, technical recruiters, and industrial automation engineers.
* **Presentation Tone:** Professional, confident, articulate, highlighting real-world industrial value and core technical innovations.
* **Recommended Video Resolution:** Full HD ($1920\times 1080$) or 2K, 16:9 aspect ratio, 60 FPS.

---

## 📋 Pre-Recording Checklist

1. **Start Background Services:**
   - [ ] **MongoDB Atlas:** Verify active internet connectivity and access to the `windfarm` database.
   - [ ] **Backend Service (Port 8000):** Run `python -m uvicorn src.main:app --port 8000 --reload` in `backend/`.
   - [ ] **ML Service (Port 8001):** Run `python -m uvicorn ml_service.main:app --port 8001 --reload` in `backend/`.
   - [ ] **Frontend (Port 5173):** Run `npm run dev` in `frontend/`.
2. **Prepare Browser Tabs (Chrome / Brave / Edge):**
   - [ ] Tab 1: [http://localhost:5173](http://localhost:5173) (Main SCADA Console).
   - [ ] Tab 2: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Backend Swagger API).
   - [ ] Tab 3: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) (ML Service Swagger API).
   - [ ] Place `backend/turbine_telemetry.csv` on your Desktop for easy drag-and-drop.
   - [ ] Set Bearer Token in **API Settings** (`secret-token-123`) to ensure a green **ONLINE** status.
3. **Recording Environment:**
   - [ ] Mute all desktop notifications (Discord, Slack, Telegram).
   - [ ] Test microphone clarity and eliminate fan or background noise.

---

## ⏱️ Storyboard & Script Breakdown

### 🎬 SCENE 1: INTRODUCTION & PROBLEM STATEMENT (0:00 – 0:45)
* **Duration:** 45 seconds.
* **On-Screen Visuals:**
  - Full-screen view of the static SCADA Dashboard.
  - Smooth cursor pan over the **WindFarm HKT** logo, navigation controls, and 3 KPI cards.
* **Voiceover:**
  > *"Hello everyone! Welcome to our project presentation and demonstration of **WindFarm HKT** — an industrial-grade SCADA monitoring console powered by real-time Artificial Intelligence for wind turbine clusters.*  
  > *In modern renewable energy infrastructures, unscheduled downtime caused by sudden mechanical failures—such as blade pitch control misalignment or bearing overheating—can cost thousands of dollars per day. Our project solves this problem by ingesting live sensor telemetry, engineering dynamic rolling metrics, and deploying Machine Learning to detect operational anomalies before catastrophic failures occur."*

---

### 🎬 SCENE 2: SYSTEM ARCHITECTURE & TECH STACK (0:45 – 1:45)
* **Duration:** 60 seconds.
* **On-Screen Visuals:**
  - Switch to `docs/architecture.md` (or architectural slides).
  - Point out the 4-tier flow: Frontend $\leftrightarrow$ FastAPI Gateway $\leftrightarrow$ ML Service $\leftrightarrow$ MongoDB Atlas & Datadog.
  - Briefly flash the two Swagger tabs (`http://127.0.0.1:8000/docs` and `http://127.0.0.1:8001/docs`) to demonstrate decoupled microservices.
* **Voiceover:**
  > *"Architecturally, our system is built as a **decoupled distributed microservices platform** consisting of four core components:*  
  > *1. **Frontend SCADA Console:** Built with React 19, TypeScript, and Vite, featuring an industrial Midnight Blue and Cyan SCADA theme designed for high data contrast and zero visual fatigue.*  
  > *2. **Backend API Gateway (Port 8000):** Developed in Python FastAPI with Beanie ODM and Motor. It provides centralized Bearer Token security and runs our **Dynamic Feature Engineering Pipeline**—automatically calculating 6-hour rolling wind speed averages, power standard deviations, and theoretical power indices.*  
  > *3. **ML Prediction Service (Port 8001):** Powered by a trained **RandomForest Classifier** using Scikit-learn, accepting 7 features to predict anomalies and output probabilistic risk scores.*  
  > *4. **Persistence & Observability:** MongoDB Atlas provides scalable time-series telemetry storage, while Datadog APM tracks real-time performance traces and dispatches critical alert events."*

---

### 🎬 SCENE 3: LIVE CSV STREAMING & AI ANOMALY DETECTION (1:45 – 3:30) — ⭐ *CORE HIGHLIGHT*
* **Duration:** 1 minute 45 seconds.
* **On-Screen Visuals:**
  1. Return to the SCADA Console.
  2. Click **"Upload & Start CSV Stream"** on the quick banner to open `CsvRunnerModal`.
  3. Drag and drop `turbine_telemetry.csv` into the dropzone. Observe the parser reporting 100 valid rows.
  4. Select stream interval: Click `1s / row`.
  5. Click **"Start CSV Stream"**.
  6. Focus on two synchronized visual areas:
     - The graphical progress bar advancing with successful row counts.
     - The **Live Terminal Log** window streaming requests to `POST /api/v1/telemetry`.
     - Normal row: Terminal displays green `[OK]`.
     - Anomaly row: Terminal triggers red highlight `🚨 [ANOMALY DETECTED] Row #14: ... (prob: 94.50%)`!
  7. Click **"Pause Stream"** briefly to explain, then resume or close the modal.
* **Voiceover:**
  > *"Now, let's explore our core feature: the **In-Browser CSV Telemetry Streamer**.*  
  > *I will open the CSV Runner modal and drag in `turbine_telemetry.csv`, which contains sensor readings from 5 active turbines. The client-side parser instantly validates all 100 rows.*  
  > *We can adjust the streaming interval between 3 seconds, 1 second, or 0.5 seconds per row. Let's select 1 second and click **Start CSV Stream**.*  
  > *Immediately, sensor records are dispatched sequentially to `/api/v1/telemetry`. The Backend ingests the reading, queries the last 6 hours of historical data from MongoDB, computes the 3 derived features, and calls the ML Service.*  
  > *Look at the Live Terminal: Under normal operation, the AI returns a green `[OK]` status. But the moment aerodynamic or power anomalies occur, the RandomForest model flags it instantly as `[ANOMALY DETECTED]` with a risk probability exceeding 90%! An alert event is automatically logged into the database simultaneously."*

---

### 🎬 SCENE 4: SCADA CONSOLE, SEARCH & DATA EXPLORATION (3:30 – 4:45)
* **Duration:** 1 minute 15 seconds.
* **On-Screen Visuals:**
  1. Close the modal and return to the main dashboard.
  2. Point out **Card 2 (Event Classification):** Highlight the red alert border (`card-anomaly-border`) that activated when anomalies were detected.
  3. Point out **Card 3 (Latest Event):** Hover over the description to trigger the frosted-glass **Tooltip**, then click **"Details" / "Collapse"**.
  4. Scroll down to the **Event Table:**
     - Point out the red left indicator border (`border-left: 4px solid #ef4444`) on anomaly rows.
     - Hover over alternating rows to demonstrate the smooth **Zebra Striping** and highlight effects.
  5. Demonstrate **Search Bar:**
     - Type `"pitch"` or `"vibration"` $\rightarrow$ Observe instant filtering. Click `[X]` to clear.
  6. Demonstrate **Dropdown Filters:**
     - Filter by `Turbine #1` $\rightarrow$ Table updates instantly.
     - Filter by `ANOMALY` $\rightarrow$ Only critical incidents remain. Click **"Reset Filters"**.
* **Voiceover:**
  > *"Back on the main dashboard, the SCADA console has updated dynamically:*  
  > *The 'Event Classification' KPI card has automatically triggered its red alert border to notify operators of detected anomalies. Conversely, when all turbines are healthy, it maintains a calm neutral cyan border with a '100% Normal' badge to prevent false alarms.*  
  > *The 'Latest Event' card allows quick inspection of the newest incident. Hovering over the text reveals a frosted-glass tooltip with the complete description, or we can click 'Details' to expand it inline.*  
  > *In the table below, our custom Zebra Striping and smooth hover effects prevent eye fatigue when auditing wide datasets. Critical anomalies are immediately identifiable by their vivid red left indicator border.*  
  > *Operators can perform full-text searches with our high-contrast search bar or filter instantly by specific turbine asset IDs and severity labels with a single click."*

---

### 🎬 SCENE 5: MANUAL LOGGING & RESPONSIVE DESIGN (4:45 – 5:45)
* **Duration:** 60 seconds.
* **On-Screen Visuals:**
  1. Click **"+ Log Event"**:
     - Fill in a sample incident (e.g., Turbine #2, Anomaly, Description: `"Manual inspection: excessive rotor vibration detected"`).
     - Click **Save Event** $\rightarrow$ Toast notification appears, table reloads with the new incident on top.
  2. Press `F12` to enter Chrome DevTools Mobile View (iPhone 12/14 Pro - 375px width):
     - Scroll to the **Pagination Bar:** Show how controls adapt into a clean 2-deck layout with compact icon buttons `[«] [<] Page 1/1 [>] [»]`, with zero horizontal overflow.
     - Open the CSV Runner modal in mobile view: Point out that the close button `[X]` remains neatly pinned to the top right and the interval chips stay tightly grouped.
* **Voiceover:**
  > *"In addition to automatic AI logging, field operators can manually submit maintenance logs through the 'Log Event' modal. Submitting an incident saves it directly to MongoDB via `POST /api/v1/events` with immediate toast feedback.*  
  > *Furthermore, our application is engineered with **100% responsive design**. When field technicians access the dashboard on mobile devices or rugged tablets, the interface adapts fluidly: the pagination bar transforms into a compact icon-based layout that never breaks rows, and modals automatically scale padding while keeping critical close and control buttons perfectly aligned."*

---

### 🎬 SCENE 6: CONCLUSION & CLOSING (5:45 – 6:15)
* **Duration:** 30 seconds.
* **On-Screen Visuals:**
  - Close DevTools, returning to full-screen desktop SCADA view.
  - Briefly display the project [`README.md`](file:///c:/WindFarm/README.md) showing the tech stack and team contributions.
* **Voiceover:**
  > *"In conclusion, **WindFarm HKT** demonstrates the power of combining a modern FastAPI microservices backend, predictive Machine Learning models, and an industrial-grade React 19 SCADA interface.*  
  > *For future milestones, we plan to implement full-duplex WebSockets and interactive GIS offshore turbine maps.*  
  > *Thank you very much for your time and attention. We look forward to your questions and feedback!"*

---

## 💡 Professional Recording Tips

1. **Cursor Movements:** Move your cursor steadily and deliberately. When highlighting an important UI element (like the anomaly border or probability score), draw a gentle circle around it.
2. **Smooth Transitions:** Use clean vocal bridges such as *"Next, let's take a look at..."*, *"As you can see right here..."*, and *"Notice how the interface responds..."*.
3. **Recommended Recording Tools:**
   - **OBS Studio:** Open-source, zero watermarks, 60fps recording.
   - **CapCut PC / Camtasia:** Excellent for zooming in on the Live Terminal Log or KPI cards when narrated.
4. **Audio Quality:** Set low-volume ambient background music (Corporate Tech / Lo-Fi ambient at $\approx 10\%$) behind your voice to maintain engagement.

