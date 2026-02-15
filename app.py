
import os
from flask import Flask, jsonify, request, render_template

from logic import (
    init_db,
    assign_task,
    get_all_employees_enriched,
    get_log,
    get_skill_names,
    get_stats,
    reset_all,
)

app = Flask(__name__, static_folder="static", template_folder="templates")

init_db()


# ── Helpers ────────────────────────────────────────────────────────────────────

def build_state() -> dict:
    skills = get_skill_names()
    return {
        "employees": get_all_employees_enriched(),
        "log":       get_log(15),
        "stats":     get_stats(),
        "skills":    skills,
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(build_state())


@app.route("/api/assign", methods=["POST"])
def api_assign():
    body       = request.get_json(force=True)
    task_name  = (body.get("taskName")  or "").strip()
    task_skill = (body.get("skill")     or "")
    priority   = (body.get("priority")  or "MEDIUM").upper()
    task_hours = int(body.get("hours",  8))

    if not task_name:
        return jsonify({"error": "taskName is required"}), 400
    if task_skill not in get_skill_names():
        return jsonify({"error": f"skill must be one of {SKILLS}"}), 400
    if task_hours < 1 or task_hours > 40:
        return jsonify({"error": "hours must be between 1 and 40"}), 400

    result = assign_task(task_name, task_skill, priority, task_hours)

    return jsonify({**build_state(), "lastResult": result})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    reset_all()
    return jsonify(build_state())


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Workload Distribution System running → http://localhost:{port}\n")
    app.run(debug=True, port=port)
