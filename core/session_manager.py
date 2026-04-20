from core.user_repository import user_exists, get_user, create_user
from utils.hash_utils import verify_password
from core.session_store import save_session
# for Rate limiting / Lockout protection
from datetime import datetime, timedelta

FAILED_ATTEMPTS = {}
LOCKOUT_TIME = timedelta(minutes=5)
MAX_ATTEMPTS = 5

def is_locked(username):
    if username not in FAILED_ATTEMPTS:
        return False

    attempts, last_attempt = FAILED_ATTEMPTS[username]

    if attempts >= MAX_ATTEMPTS:
        if datetime.now() - last_attempt < LOCKOUT_TIME:
            return True
        else:
            # Lock expired → reset
            del FAILED_ATTEMPTS[username]
            return False

    return False


def record_failed_attempt(username):
    if username in FAILED_ATTEMPTS:
        attempts, _ = FAILED_ATTEMPTS[username]
        FAILED_ATTEMPTS[username] = (attempts + 1, datetime.now())
    else:
        FAILED_ATTEMPTS[username] = (1, datetime.now())


def reset_attempts(username):
    FAILED_ATTEMPTS.pop(username, None)

def login(username, password, remember=False):
    if not username or not password:
        return False, "Username and password are required."

    if is_locked(username):
        return False, "Account locked. Try again in 5 minutes."

    user = get_user(username)
    if not user:
        return False, "Username does not exist."

    if not verify_password(password, user["password_hash"]):
        record_failed_attempt(username)

        attempts, _ = FAILED_ATTEMPTS.get(username, (0, None))
        remaining = MAX_ATTEMPTS - attempts

        if remaining <= 0:
            return False, "Account locked. Try again in 5 minutes."

        return False, f"Wrong password. {remaining} attempts left."

    # Successful login
    reset_attempts(username)

    # Remember-me login
    if remember:
        save_session(username)
    return True, "Login successful"
