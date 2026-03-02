from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, events, imports, shifts, volunteers, work_logs

app = FastAPI(title="Volunteer Hours Management API", version="0.2.0")

app.include_router(auth.router)
app.include_router(volunteers.router)
app.include_router(events.router)
app.include_router(shifts.router)
app.include_router(work_logs.router)
app.include_router(imports.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in err["loc"] if part != "body"),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": "Validation failed", "errors": errors})


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
