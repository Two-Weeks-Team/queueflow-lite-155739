from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from routes import router

app = FastAPI()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health", response_model=dict)
async def health() -> dict:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    html = """
    <html>
    <head>
        <title>QueueFlow Lite</title>
        <style>
            body { background-color: #111; color: #eee; font-family: Arial, Helvetica, sans-serif; padding: 2rem; }
            h1 { color: #ffcc00; }
            a { color: #66ccff; }
            table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
            th, td { border: 1px solid #444; padding: 0.5rem; text-align: left; }
            th { background: #222; }
        </style>
    </head>
    <body>
        <h1>QueueFlow Lite</h1>
        <p>Simple, real-time queue management for restaurants.</p>
        <h2>API Endpoints</h2>
        <table>
            <tr><th>Method</th><th>Path</th><th>Description</th></tr>
            <tr><td>GET</td><td>/health</td><td>Health check</td></tr>
            <tr><td>POST</td><td>/api/queue/{queue_id}/join</td><td>Join a queue</td></tr>
            <tr><td>GET</td><td>/api/queue/{queue_id}/position</td><td>Get current position and wait time</td></tr>
            <tr><td>POST</td><td>/api/queue/predict-wait-time</td><td>AI‑powered wait‑time prediction</td></tr>
            <tr><td>GET</td><td>/api/queue/{queue_id}/smart-notifications</td><td>AI‑generated smart notifications</td></tr>
        </table>
        <p>Tech Stack: FastAPI 0.115.0, PostgreSQL, DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</p>
        <p>Docs: <a href="/docs">/docs</a> | <a href="/redoc">/redoc</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
