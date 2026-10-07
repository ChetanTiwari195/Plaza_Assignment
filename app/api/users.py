from fastapi import APIRouter, Depends, Request
from typing import Optional
from app.api.schemas import UserCreate, RideStatus
from app.services import users as users_service
from app.services import rides as rides_service
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

@router.get("/{user_id}/rides")
def get_user_rides(user_id: int, status: Optional[RideStatus] = None, db = Depends(get_db)):
    return rides_service.get_user_rides(db, user_id, status.value if status else None)
