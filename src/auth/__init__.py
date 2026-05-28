from copy import deepcopy
from secrets import token_urlsafe


INITIAL_USERS = {
    "admin@mergington.edu": {
        "email": "admin@mergington.edu",
        "name": "School Admin",
        "password": "adminpass",
        "role": "admin",
    },
    "michael@mergington.edu": {
        "email": "michael@mergington.edu",
        "name": "Michael",
        "password": "memberpass",
        "role": "member",
    },
    "sophia@mergington.edu": {
        "email": "sophia@mergington.edu",
        "name": "Sophia",
        "password": "memberpass",
        "role": "member",
    },
}

users = deepcopy(INITIAL_USERS)
active_tokens = {}


def normalize_email(email: str) -> str:
    return email.strip().lower()


def authenticate_user(email: str, password: str):
    user = users.get(normalize_email(email))
    if user is None or user["password"] != password:
        return None

    return {
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


def create_token_for_user(user: dict) -> str:
    token = token_urlsafe(32)
    active_tokens[token] = dict(user)
    return token


def get_user_for_token(token: str):
    return active_tokens.get(token)


def revoke_token(token: str) -> None:
    active_tokens.pop(token, None)


def reset_auth_state() -> None:
    users.clear()
    users.update(deepcopy(INITIAL_USERS))
    active_tokens.clear()
