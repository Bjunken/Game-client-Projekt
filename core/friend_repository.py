import json
from pathlib import Path
from core.friend import Friend

DATA_FILE = Path(__file__).parent.parent / "data" / "friends.json"


def _load_all() -> dict:
    """Load the entire friends.json file."""
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_all(data: dict):
    """Write the entire friends.json file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_friends(username: str) -> list[Friend]:
    """
    Load the friend list for a specific user.
    Returns a list of Friend data models.
    """
    data = _load_all()
    raw_friends = data.get(username, [])
    return [Friend(f["username"], f.get("status", "offline")) for f in raw_friends]


def save_friends(username: str, friends: list[Friend]):
    """
    Save the friend list for a specific user.
    Statuses are always saved as offline — online/ingame
    is a live state, not something we persist.
    """
    data = _load_all()
    data[username] = [
        {"username": f.username, "status": "offline"}
        for f in friends
    ]
    _save_all(data)


def load_requests(username: str) -> list[str]:
    """
    Load pending incoming friend requests for a specific user.
    Stored as a simple list of usernames.
    """
    data = _load_all()
    return data.get(f"{username}_requests", [])


def save_requests(username: str, requests: list[str]):
    """Save pending incoming friend requests for a specific user."""
    data = _load_all()
    data[f"{username}_requests"] = requests
    _save_all(data)