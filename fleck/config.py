import json
from pathlib import Path

CURRENT_SESSION_PATH = Path(__file__).parent / "data" / "sessions" / "current_session.json"

def get_current_workspace():
    if CURRENT_SESSION_PATH.exists():
        with open(CURRENT_SESSION_PATH, "r") as f:
            data = json.load(f)
            return data.get("current", "")
    return ""
