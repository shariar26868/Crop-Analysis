from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
_STATUS_PHRASES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
}

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error": _STATUS_PHRASES.get(exc.status_code, "Error"),
            "message": exc.detail,
            "path": str(request.url.path),
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"] if loc != "query")
        errors.append({
            "field": field,
            "message": err["msg"],
            "invalid_value": err.get("input"),
        })

    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "error": "Unprocessable Entity",
            "message": "One or more query parameters are invalid.",
            "errors": errors,
            "path": str(request.url.path),
        },
    )

def register_exception_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
