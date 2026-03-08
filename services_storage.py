from __future__ import annotations
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_STATE = {
    "profile": {"name": "ضيف", "school": "مدرسة", "grade": "غير محدد", "avatar": "👤"},
    "points": 0,
    "badges": [],
    "history": [],
    "tests": {"مبتدئ": [], "متوسط": [], "متقدم": []},
    "games": {"word_match_best": 0, "reorder_best": 0},
}

def get_state():
    """إدارة الحالة عبر Streamlit session_state"""
    if "app_data" not in st.session_state:
        st.session_state.app_data = json.loads(json.dumps(DEFAULT_STATE))
    return st.session_state.app_data

def get_points() -> int:
    return int(get_state().get("points", 0))

def add_points(n: int):
    get_state()["points"] = max(0, get_points() + int(n))

def get_profile() -> dict:
    return get_state().get("profile", DEFAULT_STATE["profile"])

def set_profile(name, school, grade, avatar):
    get_state()["profile"] = {
        "name": name.strip() or "ضيف",
        "school": school.strip() or "مدرسة",
        "grade": grade.strip() or "غير محدد",
        "avatar": avatar.strip() or "👤"
    }

def add_badge(badge: str):
    badges = get_state().setdefault("badges", [])
    if badge not in badges:
        badges.append(badge)

def get_badges() -> list:
    return get_state().get("badges", [])

def add_history(item: dict):
    item["ts"] = datetime.now().isoformat(timespec="seconds")
    history = get_state().setdefault("history", [])
    history.insert(0, item)
    get_state()["history"] = history[:200]

def get_history() -> list:
    return get_state().get("history", [])

def add_test_result(level: str, result: dict):
    tests = get_state().setdefault("tests", {})
    if level not in tests:
        tests[level] = []
    tests[level].insert(0, result)
    tests[level] = tests[level][:100]

def get_tests(level: str) -> list:
    return get_state().get("tests", {}).get(level, [])

def set_game_best(key: str, score: int):
    games = get_state().setdefault("games", {})
    if int(score) > int(games.get(key, 0)):
        games[key] = int(score)

def get_game_best(key: str) -> int:
    return int(get_state().get("games", {}).get(key, 0))
