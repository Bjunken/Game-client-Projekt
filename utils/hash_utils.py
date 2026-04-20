import bcrypt
import re

def hash_password(password):
    user_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(user_password, salt)
    return hash.decode("utf-8")

def verify_password(password, stored_hash):
    verified = password.encode("utf-8") if isinstance(password, str) else password
    stored = stored_hash.encode("utf-8") if isinstance(stored_hash, str) else stored_hash
    
    if bcrypt.checkpw(verified, stored):
        return True
    else:
        return False
    
def is_valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z]{3,16}", username))
