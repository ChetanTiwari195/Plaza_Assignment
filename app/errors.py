from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

class DomainError(Exception):
    code = "INTERNAL_ERROR"
    status_code = 500
    def __init__(self, message: str):
        self.message = message

class DuplicatePhone(DomainError):
    code = "DUPLICATE_PHONE"
    status_code = 409
    def __init__(self):
        super().__init__("Phone already registered")

class NotFoundError(DomainError):
    status_code = 404
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

def app_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})

def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}})

def http_exception_handler(request: Request, exc: HTTPException):
    code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": code, "message": exc.detail}})
