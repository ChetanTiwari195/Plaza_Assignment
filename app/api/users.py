from fastapi import APIRouter, Depends, Request
from app.api.schemas import UserCreate
from app.services import users as users_service
from app.db import connect

router = APIRouter(prefix="/users", tags=["Users"])

def get_db(request: Request):
    settings = request.app.state.settings
    with connect(settings.db_path) as conn:
        yield conn

@router.post("", status_code=201)
def create_user(user: UserCreate, db = Depends(get_db)):
    return users_service.create_user(db, user.name, user.phone)

@router.get("/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    return users_service.get_user(db, user_id)
