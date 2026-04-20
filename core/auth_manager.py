from core.user_repository import user_exists, get_user, create_user

class AuthManager:
    def login(self, username, password, remember):
        if not user_exists(username):
            return False, "Invalid username."
        if not password():
            return False, "Invalid password."
        return True, "Login successful."