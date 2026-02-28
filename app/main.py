from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, events, volunteers

app = FastAPI(title="Volunteer Hours Management API", version="0.1.0")

app.include_router(auth.router)
app.include_router(volunteers.router)
app.include_router(events.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
