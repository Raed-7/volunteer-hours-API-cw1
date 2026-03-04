from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, events, volunteers, shifts, work_logs, imports, analytics

app = FastAPI(title="Volunteer Hours Management API", version="0.1.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": exc.errors(),
        },
    )

app.include_router(auth.router)
app.include_router(volunteers.router)
app.include_router(events.router)
app.include_router(shifts.router)
app.include_router(work_logs.router)
app.include_router(imports.router)
app.include_router(analytics.router)

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
