from app.db import transaction
from app.repositories import users as users_repo
from app.errors import DuplicatePhone, NotFoundError

def create_user(conn, name: str, phone: str) -> dict:
    with transaction(conn):
        try:
            user_id = users_repo.create(conn, name, phone)
        except ValueError:
            raise DuplicatePhone()
    return dict(users_repo.get_by_id(conn, user_id))

def get_user(conn, user_id: int) -> dict:
    row = users_repo.get_by_id(conn, user_id)
    if not row:
        raise NotFoundError("USER_NOT_FOUND", "User not found")
    return dict(row)
