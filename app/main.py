from fastapi import FastAPI
from app.config import Settings
from app.db import init_schema
from app.errors import DomainError, app_error_handler, validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

def create_app(settings: Settings = None) -> FastAPI:
    if settings is None:
        settings = Settings()
        
    init_schema(settings.db_path)
    
    app = FastAPI()
    
    app.state.settings = settings
    
    app.add_exception_handler(DomainError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    from app.api.users import router as users_router
    from app.api.drivers import router as drivers_router
    from app.api.pricing import router as pricing_router
    from app.api.coupons import router as coupons_router
    from app.api.rides import router as rides_router
    from app.api.admin import router as admin_router
    app.include_router(users_router)
    app.include_router(drivers_router)
    app.include_router(pricing_router)
    app.include_router(coupons_router)
    app.include_router(rides_router)
    app.include_router(admin_router)
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
        
    return app
