from PySide6.QtCore import QObject, Signal
from core.friend import Friend
from core import friend_repository


class FriendManager(QObject):
    """
    Manages the friend list and incoming requests for the logged-in user.
    Persists changes to disk automatically on every modification.
    Emits signals when data changes so the UI can react.
    """

    friends_updated = Signal()
    requests_updated = Signal()

    def __init__(self, username: str):
        super().__init__()

        # The logged-in user — needed to scope persistence correctly
        self.username = username

        # Load from disk on startup
        self.friends: list[Friend] = friend_repository.load_friends(username)
        self.requests: list[str] = friend_repository.load_requests(username)

    # --- Internal helpers ---

    def _save(self):
        """Persist current state to disk."""
        friend_repository.save_friends(self.username, self.friends)
        friend_repository.save_requests(self.username, self.requests)

    # --- Friend list ---

    def add_friend(self, username: str):
        if self.get_friend(username) is not None:
            return  # Already a friend, ignore
        friend = Friend(username, "offline")
        self.friends.append(friend)
        self._save()
        self.friends_updated.emit()

    def remove_friend(self, username: str):
        self.friends = [f for f in self.friends if f.username != username]
        self._save()
        self.friends_updated.emit()

    def get_friend(self, username: str) -> Friend | None:
        for f in self.friends:
            if f.username == username:
                return f
        return None

    def set_friend_status(self, username: str, status: str):
        """
        Update a friend's live status.
        Note: status is NOT persisted — it's always reset to offline on load.
        """
        friend = self.get_friend(username)
        if friend:
            friend.set_status(status)
            self.friends_updated.emit()

    # --- Friend requests ---

    def add_request(self, username: str):
        if username not in self.requests:
            self.requests.append(username)
            self._save()
            self.requests_updated.emit()

    def accept_request(self, username: str):
        if username in self.requests:
            self.requests.remove(username)
            self.add_friend(username)  # also saves and emits friends_updated
        self._save()
        self.requests_updated.emit()

    def decline_request(self, username: str):
        if username in self.requests:
            self.requests.remove(username)
        self._save()
        self.requests_updated.emit()