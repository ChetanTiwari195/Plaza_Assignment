from fastapi import APIRouter, Depends, Request, Response
from app.api.schemas import CouponCreate
from app.services import coupons as coupons_service
from app.db import connect

router = APIRouter(prefix="/coupons", tags=["Coupons"])

def get_db(request: Request):
    settings = request.app.state.settings
    with connect(settings.db_path) as conn:
        yield conn

@router.post("", status_code=201)
def create_coupon(coupon: CouponCreate, db = Depends(get_db)):
    return coupons_service.create_coupon(
        db, coupon.code, coupon.type.value, coupon.value, 
        coupon.max_discount_paise, coupon.expires_at
    )

@router.get("/{code}")
def get_coupon(code: str, db = Depends(get_db)):
    return coupons_service.get_coupon(db, code)

@router.delete("/{code}", status_code=204)
def delete_coupon(code: str, db = Depends(get_db)):
    coupons_service.delete_coupon(db, code)
    return Response(status_code=204)
