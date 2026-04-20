class Friend:
    """
    Data model representing a friend.
    No UI logic here — this is pure state.
    
    Status values:
        "online"  — logged in, idle
        "ingame"  — currently in a game
        "offline" — not logged in
    """

    VALID_STATUSES = {"online", "ingame", "offline"}

    def __init__(self, username: str, status: str = "offline"):
        self.username = username
        self.status = status

    def set_status(self, status: str):
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}")
        self.status = status

    @property
    def is_online(self) -> bool:
        return self.status in ("online", "ingame")

    @property
    def is_ingame(self) -> bool:
        return self.status == "ingame"

    def __repr__(self):
        return f"Friend(username={self.username!r}, status={self.status!r})"