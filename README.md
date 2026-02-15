# Smart Staff Workload Distribution System

A Flask web app that intelligently assigns tasks to staff members using a weighted scoring algorithm. Employee workloads and assignment history persist across restarts via SQLite.

---

## Project Structure

```
project/
├── app.py            # Flask server and API routes
├── logic.py          # Scoring algorithm and SQLite persistence
├── data.py           # Seed data and constants (skills, colours)
├── workload.db       # SQLite database (auto-created on first run)
├── templates/
│   └── index.html    # Frontend UI
└── static/
    └── style.css     # Styles
```

---

## Requirements

- Python 3.10+
- Flask

SQLite is included in Python's standard library — no extra database software needed.

---

## Installation

**1. Clone or download the project files into a folder.**

**2. Install Flask:**

```bash
pip install flask
```

**3. Run the server:**

```bash
python app.py
```

**4. Open your browser at:**

```
http://localhost:5000
```

---

## How It Works

### Task Assignment Algorithm

When a task is submitted, every employee is scored against it:

| Factor | Points |
|---|---|
| Skill matches task requirement | +50 |
| Reliability rating | +5 × rating (max +50) |
| Current workload penalty | −2 × current hours |

The employee with the highest score is assigned the task. Anyone who would exceed **40 hours** is excluded entirely.

### Status Thresholds

| Status | Hours |
|---|---|
| 🟢 Available | Under 20h |
| 🟡 Busy | 20h – 29h |
| 🔴 Critical | 30h or more |

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the UI |
| `GET` | `/api/state` | Returns full app state (employees, log, stats) |
| `POST` | `/api/assign` | Assigns a task to the best available employee |
| `POST` | `/api/reset` | Resets all workloads to initial values and clears the log |

### POST `/api/assign` — Request body

```json
{
  "taskName": "Build login page",
  "skill":    "Software Development",
  "priority": "HIGH",
  "hours":    6
}
```

---

## Data Persistence

On first run, `workload.db` is created automatically and seeded with 20 employees across 6 skill areas. All workload changes and assignment history are written to this file immediately, so nothing is lost if the server restarts.

To start completely fresh, delete `workload.db` and restart the server — it will be re-created and re-seeded.

---

## Skills & Staff

The system ships with 20 employees across 6 disciplines:

- Software Development
- Hardware Engineering
- UI/UX Design
- Data Analytics
- Project Management
- Quality Assurance

---

## File Responsibilities

| File | Responsibility |
|---|---|
| `data.py` | Seed employees, skill list, display colours. Acts as config — not modified at runtime. |
| `logic.py` | Scoring algorithm, SQLite read/write, status calculations. |
| `app.py` | Flask routes. Thin layer — calls logic functions and returns JSON. |
| `index.html` | Full frontend. Fetches `/api/state` on load and calls API routes on user actions. |
| `style.css` | Mission-control dark theme. No framework dependencies. |
