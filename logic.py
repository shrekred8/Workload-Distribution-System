# logic.py — Business logic + SQLite persistence layer
# data.py is gone — all constants and seed data live in the DB.

import sqlite3
from datetime import datetime

DB_PATH = "workload.db"

# ── Seed data (written to DB once, never imported again) ───────────────────────

_SEED_EMPLOYEES = [
    {"name": "Alex Rivera",     "expertise": "Software Development", "reliability": 9,  "seed_hours": 12},
    {"name": "Sarah Chen",      "expertise": "Software Development", "reliability": 10, "seed_hours": 28},
    {"name": "Marcus Johnson",  "expertise": "Software Development", "reliability": 7,  "seed_hours": 15},
    {"name": "Emma Wilson",     "expertise": "Hardware Engineering", "reliability": 8,  "seed_hours": 22},
    {"name": "David Park",      "expertise": "Hardware Engineering", "reliability": 9,  "seed_hours": 8},
    {"name": "Lisa Anderson",   "expertise": "Hardware Engineering", "reliability": 6,  "seed_hours": 35},
    {"name": "James Taylor",    "expertise": "UI/UX Design",         "reliability": 10, "seed_hours": 18},
    {"name": "Nina Patel",      "expertise": "UI/UX Design",         "reliability": 8,  "seed_hours": 25},
    {"name": "Ryan Miller",     "expertise": "UI/UX Design",         "reliability": 7,  "seed_hours": 10},
    {"name": "Sophie Martinez", "expertise": "Data Analytics",       "reliability": 9,  "seed_hours": 20},
    {"name": "Kevin Lee",       "expertise": "Data Analytics",       "reliability": 10, "seed_hours": 5},
    {"name": "Rachel Brown",    "expertise": "Data Analytics",       "reliability": 8,  "seed_hours": 32},
    {"name": "Tom Zhang",       "expertise": "Project Management",   "reliability": 7,  "seed_hours": 14},
    {"name": "Maya Singh",      "expertise": "Project Management",   "reliability": 9,  "seed_hours": 30},
    {"name": "Chris Davis",     "expertise": "Project Management",   "reliability": 8,  "seed_hours": 16},
    {"name": "Anna Williams",   "expertise": "Quality Assurance",    "reliability": 10, "seed_hours": 12},
    {"name": "Brian Moore",     "expertise": "Quality Assurance",    "reliability": 6,  "seed_hours": 24},
    {"name": "Julia Garcia",    "expertise": "Quality Assurance",    "reliability": 9,  "seed_hours": 8},
    {"name": "Michael Kim",     "expertise": "Software Development", "reliability": 8,  "seed_hours": 20},
    {"name": "Elena Rodriguez", "expertise": "Data Analytics",       "reliability": 7,  "seed_hours": 18},
]

_SEED_SKILLS = [
    {"name": "Software Development", "code": "SWD", "color": "#00FF88"},
    {"name": "Hardware Engineering", "code": "HWE", "color": "#FF6B35"},
    {"name": "UI/UX Design",         "code": "UXD", "color": "#B4E4FF"},
    {"name": "Data Analytics",       "code": "DAT", "color": "#FFD700"},
    {"name": "Project Management",   "code": "PMG", "color": "#DA70D6"},
    {"name": "Quality Assurance",    "code": "QAT", "color": "#87CEEB"},
]


# ── Database setup ─────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create all tables and seed them on the very first run.
    Safe to call on every startup — skips seeding if rows already exist.
    """
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS skills (
                name  TEXT PRIMARY KEY,
                code  TEXT NOT NULL,
                color TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS employees (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL UNIQUE,
                expertise     TEXT    NOT NULL REFERENCES skills(name),
                reliability   INTEGER NOT NULL,
                seed_hours    INTEGER NOT NULL,
                current_hours INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assignment_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT    NOT NULL,
                task_name TEXT    NOT NULL,
                skill     TEXT    NOT NULL,
                priority  TEXT    NOT NULL,
                hours     INTEGER NOT NULL,
                success   INTEGER NOT NULL,
                assignee  TEXT,
                score     INTEGER,
                eligible  INTEGER,
                reasons   TEXT,
                message   TEXT
            );
        """)

        # Seed skills
        if conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO skills (name, code, color) VALUES (:name, :code, :color)",
                _SEED_SKILLS
            )

        # Seed employees
        if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            conn.executemany(
                """INSERT INTO employees (name, expertise, reliability, seed_hours, current_hours)
                   VALUES (:name, :expertise, :reliability, :seed_hours, :seed_hours)""",
                _SEED_EMPLOYEES
            )


# ── Skill helpers ──────────────────────────────────────────────────────────────

def get_all_skills() -> list:
    """Return all skills as a list of dicts, ordered by name."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM skills ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def get_skill_names() -> list:
    return [s["name"] for s in get_all_skills()]


def _skill_lookup() -> dict:
    """Return {skill_name: {code, color}} for quick enrichment lookups."""
    return {s["name"]: s for s in get_all_skills()}


# ── Employee helpers ───────────────────────────────────────────────────────────

def get_all_employees() -> list:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM employees ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def _enrich(emp: dict, skill_map: dict) -> dict:
    """Attach computed display fields used by the frontend."""
    st    = get_status(emp["current_hours"])
    skill = skill_map.get(emp["expertise"], {"code": "???", "color": "#aaa"})
    return {
        **emp,
        "currentHours": emp["current_hours"],
        "status":       st["label"],
        "statusColor":  st["color"],
        "statusBg":     st["bg"],
        "skillCode":    skill["code"],
        "skillColor":   skill["color"],
        "initials":     "".join(p[0] for p in emp["name"].split()).upper(),
        "loadPct":      round(emp["current_hours"] / 40 * 100, 1),
    }


def get_all_employees_enriched() -> list:
    skill_map = _skill_lookup()
    return [_enrich(e, skill_map) for e in get_all_employees()]


# ── Assignment log helpers ─────────────────────────────────────────────────────

def get_log(limit: int = 15) -> list:
    skill_map = _skill_lookup()
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM assignment_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    entries = []
    for r in rows:
        e = dict(r)
        e["success"]   = bool(e["success"])
        e["taskName"]  = e.pop("task_name")
        skill          = skill_map.get(e["skill"], {"code": "???", "color": "#aaa"})
        e["skillCode"] = skill["code"]
        e["skillColor"]= skill["color"]
        entries.append(e)
    return entries


def _write_log_entry(entry: dict):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO assignment_log
               (ts, task_name, skill, priority, hours, success,
                assignee, score, eligible, reasons, message)
               VALUES (:ts, :task_name, :skill, :priority, :hours, :success,
                       :assignee, :score, :eligible, :reasons, :message)""",
            entry
        )


# ── Core algorithm ─────────────────────────────────────────────────────────────

def get_status(hours: int) -> dict:
    if hours >= 30:
        return {"label": "CRITICAL", "color": "#FF3B30", "bg": "rgba(255,59,48,0.15)"}
    if hours >= 20:
        return {"label": "BUSY",     "color": "#FF9F0A", "bg": "rgba(255,159,10,0.15)"}
    return     {"label": "AVAIL",    "color": "#30D158", "bg": "rgba(48,209,88,0.15)"}


def calc_score(emp: dict, task_skill: str) -> int:
    score = 0
    if emp["expertise"] == task_skill:
        score += 50
    score += emp["reliability"] * 5
    score -= emp["current_hours"] * 2
    return score


def assign_task(task_name: str, task_skill: str, priority: str, task_hours: int) -> dict:
    employees  = get_all_employees()
    best_emp   = None
    best_score = float("-inf")
    eligible   = 0

    for emp in employees:
        if emp["current_hours"] + task_hours > 40:
            continue
        eligible += 1
        score = calc_score(emp, task_skill)
        if score > best_score:
            best_score = score
            best_emp   = emp

    ts = datetime.now().strftime("%H:%M:%S")

    if best_emp is None:
        _write_log_entry({
            "ts": ts, "task_name": task_name, "skill": task_skill,
            "priority": priority, "hours": task_hours, "success": 0,
            "assignee": None, "score": None, "eligible": 0,
            "reasons": None, "message": "All employees would exceed the 40-hour limit.",
        })
        return {"success": False, "message": "All employees would exceed the 40-hour limit."}

    # Persist workload update
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET current_hours = current_hours + ? WHERE id = ?",
            (task_hours, best_emp["id"])
        )

    # Build reasons
    reasons = []
    if best_emp["expertise"] == task_skill:   reasons.append("Skill match")
    if best_emp["reliability"] >= 9:          reasons.append("High reliability")
    if best_emp["current_hours"] <= 15:       reasons.append("Low workload")
    reason_text = " · ".join(reasons) if reasons else "Best available"

    _write_log_entry({
        "ts": ts, "task_name": task_name, "skill": task_skill,
        "priority": priority, "hours": task_hours, "success": 1,
        "assignee": best_emp["name"], "score": best_score,
        "eligible": eligible, "reasons": reason_text, "message": None,
    })

    return {
        "success": True, "assignee": best_emp["name"],
        "score": best_score, "eligible": eligible, "reasons": reason_text,
    }


def get_stats() -> dict:
    employees = get_all_employees()
    return {
        "total":     len(employees),
        "available": sum(1 for e in employees if e["current_hours"] < 20),
        "busy":      sum(1 for e in employees if 20 <= e["current_hours"] < 30),
        "critical":  sum(1 for e in employees if e["current_hours"] >= 30),
    }


def reset_all():
    """Restore every employee's hours to their seed value and wipe the log."""
    with get_db() as conn:
        conn.execute("UPDATE employees SET current_hours = seed_hours")
        conn.execute("DELETE FROM assignment_log")
