from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse


from app.routers import auth, events, volunteers, shifts, work_logs, imports, analytics, stats

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

            :root {
                --bg-1: #0f172a;
                --bg-2: #111827;
                --bg-3: #1e293b;
                --surface: rgba(255, 255, 255, 0.08);
                --surface-2: rgba(255, 255, 255, 0.06);
                --border: rgba(255, 255, 255, 0.12);
                --text: #e5e7eb;
                --muted: #cbd5e1;
                --muted-2: #94a3b8;
                --primary: #3b82f6;
                --primary-2: #2563eb;
                --focus: #facc15;
            }

            /* ── Colour-blind mode: high-contrast greyscale ─────────────────────── */
html.cb-mode {
    --primary: #ffffff;
    --primary-2: #cccccc;
    --focus: #ffffff;
}

html.cb-mode body {
    background: #000000;
}

html.cb-mode .hero {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.3);
}

html.cb-mode .badge {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.4);
    color: #ffffff;
}

html.cb-mode .btn-primary {
    background: #ffffff;
    color: #000000;
    box-shadow: none;
}

html.cb-mode .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.35);
    color: #ffffff;
}

html.cb-mode .stat-card,
html.cb-mode .card,
html.cb-mode .panel {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.25);
}

html.cb-mode .a11y-cb-btn.a11y-active {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.5);
    color: #ffffff;
}

            /* ── Accessibility toolbar ─────────── */
            #a11y-bar {
                position: fixed;
                top: 14px;
                right: 16px;
                z-index: 999;
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(15, 23, 42, 0.88);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 14px;
                padding: 8px 14px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45);
            }

            .a11y-label {
                font-size: 0.7rem;
                color: #94a3b8;
                font-weight: 700;
                letter-spacing: 0.07em;
                text-transform: uppercase;
                margin-right: 2px;
                font-family: Inter, Arial, sans-serif;
            }

            .a11y-group {
                display: flex;
                gap: 4px;
            }

            .a11y-btn {
                background: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.13);
                color: #e5e7eb;
                border-radius: 8px;
                padding: 5px 10px;
                cursor: pointer;
                font-weight: 700;
                font-family: Inter, Arial, sans-serif;
                transition: background 0.15s, border-color 0.15s;
                line-height: 1;
            }

            .a11y-btn:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.25);
            }

            .a11y-btn:focus {
                outline: 2px solid var(--focus);
                outline-offset: 2px;
            }

            .a11y-btn.a11y-active {
                background: rgba(59, 130, 246, 0.32);
                border-color: rgba(96, 165, 250, 0.55);
                color: #bfdbfe;
            }

            .a11y-divider {
                width: 1px;
                height: 22px;
                background: rgba(255, 255, 255, 0.12);
                flex-shrink: 0;
            }

            .a11y-cb-btn {
                display: flex;
                align-items: center;
                gap: 5px;
                padding: 5px 12px;
                font-size: 0.8rem;
            }

            .a11y-cb-btn.a11y-active {
                background: rgba(245, 158, 11, 0.22);
                border-color: rgba(245, 158, 11, 0.5);
                color: #fde68a;
            }

            /* Text size button visual scale */
            .a11y-txt-sm { font-size: 0.75rem; }
            .a11y-txt-md { font-size: 0.88rem; }
            .a11y-txt-lg { font-size: 1.05rem; }

            /* ── Base layout ────────── */
            html {
                scroll-behavior: smooth;
            }

            body {
                margin: 0;
                font-family: Inter, Arial, sans-serif;
                background:
                    radial-gradient(circle at top left, #1d4ed8 0%, transparent 30%),
                    radial-gradient(circle at top right, #7c3aed 0%, transparent 25%),
                    linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-3) 100%);
                color: var(--text);
                min-height: 100vh;
            }

            .skip-link {
                position: absolute;
                left: 16px;
                top: -48px;
                background: #ffffff;
                color: #111827;
                padding: 12px 16px;
                border-radius: 10px;
                font-weight: 700;
                text-decoration: none;
                z-index: 1000;
                transition: top 0.2s ease;
            }

            .skip-link:focus {
                top: 16px;
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

            .stats-strip {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 14px;
                margin-top: 28px;
            }

            .stat-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 18px;
                padding: 18px;
            }

            .stat-card strong {
                display: block;
                color: #ffffff;
                font-size: 1rem;
                margin-bottom: 6px;
            }

            .stat-card span {
                color: var(--muted);
                font-size: 0.95rem;
                line-height: 1.6;
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
                #a11y-bar {
                    top: 10px;
                    right: 10px;
                    padding: 6px 10px;
                    gap: 6px;
                }
                .a11y-label {
                    display: none;
                }
            }
        </style>
    </head>
    <body>

        <!-- Accessibility controls -->
        <div id="a11y-bar" role="region" aria-label="Accessibility controls">
            <span class="a11y-label" aria-hidden="true">Accessibility</span>

            <div class="a11y-group" role="group" aria-label="Text size">
                <button class="a11y-btn a11y-txt-sm" id="txt-sm"
                        onclick="a11ySize('small')"
                        aria-label="Small text size"
                        title="Small text">A</button>
                <button class="a11y-btn a11y-txt-md a11y-active" id="txt-md"
                        onclick="a11ySize('medium')"
                        aria-label="Medium text size (default)"
                        title="Medium text">A</button>
                <button class="a11y-btn a11y-txt-lg" id="txt-lg"
                        onclick="a11ySize('large')"
                        aria-label="Large text size"
                        title="Large text">A</button>
            </div>

            <div class="a11y-divider" aria-hidden="true"></div>

            <button class="a11y-btn a11y-cb-btn" id="cb-toggle"
                    onclick="a11yCB()"
                    aria-pressed="false"
                    aria-label="Toggle colour-blind friendly mode"
                    title="Colour-blind friendly mode">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"/>
                </svg>
                CB Mode
            </button>
        </div>

        <a class="skip-link" href="#main-content">Skip to main content</a>

        <main id="main-content" class="page">
            <header class="hero" aria-label="Project introduction">
                <div class="badge">FastAPI • Volunteer Management • Analytics</div>
                <h1>Volunteer Hours Management API</h1>
                <p class="subtitle">
                    A backend API for managing volunteers, events, shifts, work logs,
                    flexible CSV imports, and analytics. It helps organisers record
                    participation accurately and turn attendance data into meaningful
                    volunteer-hour insights.
                </p>

                <nav class="actions" aria-label="Quick links">
                    <a class="btn btn-primary" href="/docs">Open API Docs</a>
                    <a class="btn btn-secondary" href="/health">Check Health Status</a>
                </nav>

                <section class="stats-strip" aria-label="Quick summary">
                    <div class="stat-card">
                        <strong>Secure Access</strong>
                        <span>JWT authentication with role-based access for admin and organiser users.</span>
                    </div>
                    <div class="stat-card">
                        <strong>Flexible Imports</strong>
                        <span>Supports volunteer, event, and attendance files from real spreadsheets.</span>
                    </div>
                    <div class="stat-card">
                        <strong>Worked Hours</strong>
                        <span>Calculates official worked time using shift boundaries and validation rules.</span>
                    </div>
                </section>

                <section class="grid" aria-label="Core features">
                    <article class="card">
                        <h3>Authentication</h3>
                        <p>Secure login, protected routes, and role support for organisers and admins.</p>
                    </article>
                    <article class="card">
                        <h3>Volunteer Tracking</h3>
                        <p>Manage volunteers, events, shifts, and work logs with structured API endpoints.</p>
                    </article>
                    <article class="card">
                        <h3>CSV Imports</h3>
                        <p>Import volunteers, events, and attendance from different spreadsheet formats.</p>
                    </article>
                    <article class="card">
                        <h3>Analytics</h3>
                        <p>Generate leaderboard, awards, and volunteer summaries from imported or manually added records.</p>
                    </article>
                </section>
            </header>

            <section class="section" aria-label="Project details">
                <section class="panel">
                    <h2>Project Purpose</h2>
                    <p>
                        This system is designed for volunteer event management. It helps organisers
                        store records accurately, calculate official worked hours, and produce
                        useful summaries for recognition, reporting, and decision-making.
                    </p>
                </section>

                <aside class="panel">
                    <h2>Quick Access</h2>
                    <ul>
                        <li><strong>/docs</strong> — interactive Swagger interface</li>
                        <li><strong>/stats</strong> — overall project totals</li>
                        <li><strong>/health</strong> — service status check</li>
                    </ul>
                    <p class="footer-note">
                        Tip: start with <code>/docs</code> to explore routes and test the full API.
                    </p>
                </aside>
            </section>
        </main>

        <script>
            (function () {
                'use strict';

                function a11ySize(size) {
                    var sizes  = { small: '13px', medium: '16px', large: '20px' };
                    var btnIds = { small: 'txt-sm', medium: 'txt-md', large: 'txt-lg' };
                    document.documentElement.style.fontSize = sizes[size] || '16px';
                    try { localStorage.setItem('a11y-size', size); } catch (e) {}
                    ['txt-sm', 'txt-md', 'txt-lg'].forEach(function (id) {
                        document.getElementById(id).classList.remove('a11y-active');
                    });
                    var target = document.getElementById(btnIds[size]);
                    if (target) { target.classList.add('a11y-active'); }
                }

                function a11yCB() {
                    var on  = document.documentElement.classList.toggle('cb-mode');
                    var btn = document.getElementById('cb-toggle');
                    btn.setAttribute('aria-pressed', String(on));
                    btn.classList.toggle('a11y-active', on);
                    try { localStorage.setItem('a11y-cb', on ? '1' : '0'); } catch (e) {}
                }

                // Restore saved preferences on load
                var savedSize = 'medium';
                try { savedSize = localStorage.getItem('a11y-size') || 'medium'; } catch (e) {}
                a11ySize(savedSize);

                var cbOn = false;
                try { cbOn = localStorage.getItem('a11y-cb') === '1'; } catch (e) {}
                if (cbOn) {
                    document.documentElement.classList.add('cb-mode');
                    var cbBtn = document.getElementById('cb-toggle');
                    if (cbBtn) {
                        cbBtn.setAttribute('aria-pressed', 'true');
                        cbBtn.classList.add('a11y-active');
                    }
                }

                // Expose to global scope for inline onclick handlers
                window.a11ySize = a11ySize;
                window.a11yCB  = a11yCB;
            }());
        </script>
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
app.include_router(stats.router)

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
