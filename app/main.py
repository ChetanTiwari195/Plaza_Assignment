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
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
        
    return app
