# data.py — Employee seed data and app-wide constants

SKILLS = [
    "Software Development",
    "Hardware Engineering",
    "UI/UX Design",
    "Data Analytics",
    "Project Management",
    "Quality Assurance",
]

SKILL_CODES = {
    "Software Development": "SWD",
    "Hardware Engineering": "HWE",
    "UI/UX Design":         "UXD",
    "Data Analytics":       "DAT",
    "Project Management":   "PMG",
    "Quality Assurance":    "QAT",
}

SKILL_COLORS = {
    "Software Development": "#00FF88",
    "Hardware Engineering": "#FF6B35",
    "UI/UX Design":         "#B4E4FF",
    "Data Analytics":       "#FFD700",
    "Project Management":   "#DA70D6",
    "Quality Assurance":    "#87CEEB",
}

# Default employee roster — copied on each server start into in-memory state
INITIAL_EMPLOYEES = [
    {"name": "Alex Rivera",      "expertise": "Software Development", "reliability": 9,  "currentHours": 12},
    {"name": "Sarah Chen",       "expertise": "Software Development", "reliability": 10, "currentHours": 28},
    {"name": "Marcus Johnson",   "expertise": "Software Development", "reliability": 7,  "currentHours": 15},
    {"name": "Emma Wilson",      "expertise": "Hardware Engineering", "reliability": 8,  "currentHours": 22},
    {"name": "David Park",       "expertise": "Hardware Engineering", "reliability": 9,  "currentHours": 8},
    {"name": "Lisa Anderson",    "expertise": "Hardware Engineering", "reliability": 6,  "currentHours": 35},
    {"name": "James Taylor",     "expertise": "UI/UX Design",         "reliability": 10, "currentHours": 18},
    {"name": "Nina Patel",       "expertise": "UI/UX Design",         "reliability": 8,  "currentHours": 25},
    {"name": "Ryan Miller",      "expertise": "UI/UX Design",         "reliability": 7,  "currentHours": 10},
    {"name": "Sophie Martinez",  "expertise": "Data Analytics",       "reliability": 9,  "currentHours": 20},
    {"name": "Kevin Lee",        "expertise": "Data Analytics",       "reliability": 10, "currentHours": 5},
    {"name": "Rachel Brown",     "expertise": "Data Analytics",       "reliability": 8,  "currentHours": 32},
    {"name": "Tom Zhang",        "expertise": "Project Management",   "reliability": 7,  "currentHours": 14},
    {"name": "Maya Singh",       "expertise": "Project Management",   "reliability": 9,  "currentHours": 30},
    {"name": "Chris Davis",      "expertise": "Project Management",   "reliability": 8,  "currentHours": 16},
    {"name": "Anna Williams",    "expertise": "Quality Assurance",    "reliability": 10, "currentHours": 12},
    {"name": "Brian Moore",      "expertise": "Quality Assurance",    "reliability": 6,  "currentHours": 24},
    {"name": "Julia Garcia",     "expertise": "Quality Assurance",    "reliability": 9,  "currentHours": 8},
    {"name": "Michael Kim",      "expertise": "Software Development", "reliability": 8,  "currentHours": 20},
    {"name": "Elena Rodriguez",  "expertise": "Data Analytics",       "reliability": 7,  "currentHours": 18},
]
