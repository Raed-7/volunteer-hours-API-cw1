from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse


from app.routers import auth, events, volunteers, shifts, work_logs, imports, analytics

app = FastAPI(title="Volunteer Hours Management API", version="0.1.0", docs_url=None, redoc_url=None)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": exc.errors(),
        },
    )

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Volunteer Hours Management API</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Inter, Arial, sans-serif;
                background:
                    radial-gradient(circle at top left, #1d4ed8 0%, transparent 30%),
                    radial-gradient(circle at top right, #7c3aed 0%, transparent 25%),
                    linear-gradient(135deg, #0f172a 0%, #111827 45%, #1e293b 100%);
                color: #e5e7eb;
                min-height: 100vh;
            }

            .page {
                max-width: 1100px;
                margin: 0 auto;
                padding: 48px 24px 60px;
            }

            .hero {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 28px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
            }

            .badge {
                display: inline-block;
                padding: 8px 14px;
                border-radius: 999px;
                background: rgba(59, 130, 246, 0.18);
                border: 1px solid rgba(96, 165, 250, 0.35);
                color: #bfdbfe;
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 18px;
            }

            h1 {
                margin: 0 0 14px;
                font-size: clamp(2rem, 4vw, 3.5rem);
                line-height: 1.1;
                color: #ffffff;
            }

            .subtitle {
                margin: 0;
                max-width: 760px;
                font-size: 1.08rem;
                line-height: 1.8;
                color: #cbd5e1;
            }

            .actions {
                display: flex;
                flex-wrap: wrap;
                gap: 14px;
                margin-top: 28px;
            }

            .btn {
                text-decoration: none;
                padding: 14px 18px;
                border-radius: 14px;
                font-weight: 700;
                transition: transform 0.18s ease, opacity 0.18s ease, background 0.18s ease;
                display: inline-block;
            }

            .btn:hover {
                transform: translateY(-2px);
                opacity: 0.95;
            }

            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                box-shadow: 0 10px 25px rgba(37, 99, 235, 0.35);
            }

            .btn-secondary {
                background: rgba(255, 255, 255, 0.08);
                color: #e5e7eb;
                border: 1px solid rgba(255, 255, 255, 0.14);
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
                margin-top: 28px;
            }

            .card {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 22px;
                padding: 22px;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
            }

            .card h3 {
                margin-top: 0;
                margin-bottom: 10px;
                font-size: 1.05rem;
                color: #ffffff;
            }

            .card p {
                margin: 0;
                color: #cbd5e1;
                line-height: 1.7;
                font-size: 0.96rem;
            }

            .section {
                margin-top: 30px;
                display: grid;
                grid-template-columns: 1.4fr 1fr;
                gap: 20px;
            }

            .panel {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 26px;
            }

            .panel h2 {
                margin-top: 0;
                margin-bottom: 14px;
                color: #ffffff;
                font-size: 1.3rem;
            }

            .panel p,
            .panel li {
                color: #cbd5e1;
                line-height: 1.8;
            }

            ul {
                margin: 0;
                padding-left: 20px;
            }

            .footer-note {
                margin-top: 26px;
                font-size: 0.92rem;
                color: #94a3b8;
            }

            @media (max-width: 900px) {
                .section {
                    grid-template-columns: 1fr;
                }

                .hero {
                    padding: 28px;
                }
            }
        </style>
    </head>
    <body>
        <main class="page">
            <section class="hero">
                <div class="badge">FastAPI • Volunteer Management • Analytics</div>
                <h1>Volunteer Hours Management API</h1>
                <p class="subtitle">
                    A modern backend API for managing volunteers, events, shifts, work logs,
                    CSV imports, and analytics. Built to help organisers track participation
                    accurately and turn raw attendance data into meaningful volunteer-hour insights.
                </p>

                <div class="actions">
                    <a class="btn btn-primary" href="/docs">Open Swagger Docs</a>
                    <a class="btn btn-secondary" href="/health">Health Check</a>
                </div>

                <div class="grid">
                    <article class="card">
                        <h3>Authentication</h3>
                        <p>Secure JWT-based login with role support for admin and organiser users.</p>
                    </article>
                    <article class="card">
                        <h3>Volunteer Tracking</h3>
                        <p>Create and manage volunteers, events, shifts, and work logs with structured data models.</p>
                    </article>
                    <article class="card">
                        <h3>CSV Imports</h3>
                        <p>Import volunteers, events, and attendance from real spreadsheets with flexible parsing.</p>
                    </article>
                    <article class="card">
                        <h3>Analytics</h3>
                        <p>Generate leaderboard, awards, and volunteer summaries from imported or manually added records.</p>
                    </article>
                </div>
            </section>

            <section class="section">
                <div class="panel">
                    <h2>Project Purpose</h2>
                    <p>
                        This system is designed for volunteer event management. It helps organisers
                        store records accurately, calculate official worked hours, and generate useful
                        summaries for recognition, reporting, and decision-making.
                    </p>
                </div>

                <div class="panel">
                    <h2>Quick Access</h2>
                    <ul>
                        <li><strong>/docs</strong> — interactive Swagger interface</li>
                        <li><strong>/redoc</strong> — alternative API documentation view</li>
                        <li><strong>/health</strong> — service status check</li>
                    </ul>
                    <p class="footer-note">
                        Tip: start with Swagger Docs to test routes and explore the full API.
                    </p>
                </div>
            </section>
        </main>
    </body>
    </html>
    """

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Volunteer Hours Management API • Swagger Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "filter": True,
            "tryItOutEnabled": True,
            "syntaxHighlight.theme": "monokai",
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
