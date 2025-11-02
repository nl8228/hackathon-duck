import time, uuid
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles 

from backend import timer

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

#{"status": "...", "name": "..."}
STATE: dict[str, dict] = {}
GO_HOME = False

#for styling
def render_page(inner_html: str, *, refresh: bool = False) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            {'<meta http-equiv="refresh" content="1">' if refresh else ''}
            <title>Duck Alarm</title>
            <link rel="stylesheet" href="/static/style.css?v=4">
        </head>
        <body>
            <h1 class="title">Duck Alarm</h1>
            <main class="panel">
                {inner_html}
            </main>
        </body>
    </html>""")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

def run_timer(alarm_id: str, seconds: int):
    timer(seconds)
    if alarm_id in STATE:
        STATE[alarm_id]["status"] = "completed"

@app.post("/api/alarm")
def receive_alarm(
    seconds: int = Form(...),
    alarm_name: str = Form(...),
    background: BackgroundTasks = None
):
    alarm_id = str(uuid.uuid4())
    STATE[alarm_id] = {"status": "running", "name": alarm_name}
    background.add_task(run_timer, alarm_id, seconds)
    return RedirectResponse(url=f"/alarm/{alarm_id}", status_code=303)

@app.get("/alarm/{alarm_id}", response_class=HTMLResponse)
def alarm_page(alarm_id: str):
    global GO_HOME
    entry = STATE.get(alarm_id)
    if entry is None:
        return render_page("<h2>Alarm not found.</h2>")

    name = entry.get("name")
    status = entry.get("status")

    if status == "completed":
        if GO_HOME:
            GO_HOME = False
            return RedirectResponse("/", status_code=303)
        return render_page(f"""
            <h2>⏰ Time's up!</h2>
            <p><strong>Alarm:</strong> {name}</p>
            <p><small>ID: {alarm_id}</small></p>
            <div class="actions">
              <a class="btn" href="/">Set another alarm</a>
            </div>
        """)

    return render_page(f"""
        <h2>Alarm running…</h2>
        <p><strong>Alarm:</strong> {name}</p>
        <p><small>ID: {alarm_id}</small></p>
        <p>This page will update when it completes.</p>
    """, refresh=True)


@app.post("/api/go-home")
def api_go_home():
    global GO_HOME
    GO_HOME = True
    return {"ok": True}
