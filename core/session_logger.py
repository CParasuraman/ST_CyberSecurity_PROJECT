import json
import os
from datetime import datetime

LOG_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "session_log.json")


def log_session(session_type: str,
                details: dict):
    """
    Log a cracking session to disk.
    Called automatically after each crack.
    """
    os.makedirs(
        os.path.dirname(LOG_PATH),
        exist_ok=True)

    sessions = _load()
    entry = {
        "id":        len(sessions) + 1,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"),
        "type":      session_type,
        "details":   details,
    }
    sessions.append(entry)
    _save(sessions)
    return entry


def load_sessions() -> list:
    return _load()


def clear_sessions():
    _save([])


def _load() -> list:
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r",
                  encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(sessions: list):
    with open(LOG_PATH, "w",
              encoding="utf-8") as f:
        json.dump(sessions, f,
                  indent=2,
                  ensure_ascii=False)