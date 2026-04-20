import json
import os
from pathlib import Path

# Get the path to user.json in the data directory
data_file = Path(__file__).parent.parent / 'data' / 'user.json'

# Checks if user exists
def user_exists(username):
    with open(data_file, 'r') as file:
        data = json.loads(file.read())
        for user in data:
            if user["username"] == username:
                return True
        return False

# Gets user
def get_user(username):
    with open(data_file, 'r') as file:
        data = json.loads(file.read())
        for user in data:
            if user["username"] == username:
                return user
        return None

# Creates user (sends info to data base etc)
def create_user(username, password_hash, email):
    new_user = {"username": username, "password_hash": password_hash, "email": email}
    with open(data_file, 'r') as file:
        data = json.loads(file.read())
    data.append(new_user)
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)
    return True