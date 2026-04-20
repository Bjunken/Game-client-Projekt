import json
from pathlib import Path

SESSION_FILE = Path(__file__).parent.parent / "data" / "session.json"


def save_session(username):
    data = {
        "logged_in": True,
        "username": username
    }
    with open(SESSION_FILE, "w") as file:
        json.dump(data, file)

def load_session():
    if not SESSION_FILE.exists():
        return None

    with open(SESSION_FILE, "r") as file:
        data = json.load(file)

    if data.get("logged_in"):
        return data.get("username")

    return None

def clear_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()