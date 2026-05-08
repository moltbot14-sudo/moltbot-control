from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import subprocess
import json
import os

app = FastAPI()

HOME = Path.home()

PROGRESS_FILE = HOME / ".openclaw/automejora/state/progress.json"
HISTORY_FILE = HOME / ".openclaw/automejora/state/history.json"
BACKLOG_FILE = HOME / ".openclaw/automejora/backlog/tasks.json"
FLAG_FILE = HOME / ".openclaw/automejora/automejora_24_7.enabled"
LOG_DIR = HOME / ".openclaw/automejora/logs"

GOOGLE_TOKEN = HOME / ".openclaw/integrations/google_token.json"
GOOGLE_CREDS = HOME / ".openclaw/integrations/google_credentials.json"
GITHUB_TOKEN = HOME / ".openclaw/integrations/github_token.txt"


def read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}
    return default


def run_cmd(cmd: str):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=40
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as e:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(e)
        }


@app.get("/api/progress")
def get_progress():
    data = read_json(PROGRESS_FILE, {
        "pc": os.uname().nodename,
        "state": "offline",
        "percent": 0,
        "current_task": "Sin datos todavía",
        "current_step": "",
        "cycle_id": "",
        "tasks_total": 0,
        "tasks_done": 0,
        "tasks_error": 0,
        "last_update": "",
        "automejora_24_7": False
    })

    data["automejora_24_7"] = FLAG_FILE.exists()
    return JSONResponse(data)


@app.get("/api/history")
def get_history():
    return JSONResponse(read_json(HISTORY_FILE, []))


@app.get("/api/backlog")
def get_backlog():
    return JSONResponse(read_json(BACKLOG_FILE, []))


@app.get("/api/logs")
def get_logs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logs = sorted(LOG_DIR.glob("*.log"), reverse=True)

    if not logs:
        return {
            "file": None,
            "logs": "No hay logs todavía."
        }

    latest = logs[0]
    text = latest.read_text(encoding="utf-8", errors="ignore")

    return {
        "file": str(latest),
        "logs": text[-12000:]
    }


@app.get("/api/integrations/status")
def integrations_status():
    return {
        "google_account": "moltbot14@gmail.com",
        "google_credentials": GOOGLE_CREDS.exists(),
        "google_token": GOOGLE_TOKEN.exists(),
        "drive": GOOGLE_TOKEN.exists(),
        "gmail": GOOGLE_TOKEN.exists(),
        "github_token": GITHUB_TOKEN.exists()
    }


@app.post("/api/automejora/start")
def start_automejora():
    FLAG_FILE.write_text("enabled", encoding="utf-8")
    result = run_cmd("systemctl --user start openclaw-automejora-24-7.service")
    return {
        "ok": result["ok"],
        "message": "Automejora 24/7 activada",
        "detail": result
    }


@app.post("/api/automejora/stop")
def stop_automejora():
    if FLAG_FILE.exists():
        FLAG_FILE.unlink()

    result = run_cmd("systemctl --user stop openclaw-automejora-24-7.service")
    return {
        "ok": True,
        "message": "Automejora 24/7 pausada",
        "detail": result
    }


@app.post("/api/automejora/run-now")
def run_now():
    FLAG_FILE.write_text("enabled", encoding="utf-8")
    result = run_cmd("systemctl --user restart openclaw-automejora-24-7.service")
    return {
        "ok": result["ok"],
        "message": "Ciclo forzado ahora",
        "detail": result
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MoltBot Control</title>
<style>
body {
    margin: 0;
    background: #0d0d0d;
    color: white;
    font-family: Arial, sans-serif;
    padding: 16px;
}

h1 {
    font-size: 24px;
    margin-bottom: 16px;
}

h2 {
    font-size: 19px;
    margin-bottom: 10px;
}

.card {
    background: #1b1b1b;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 0 18px rgba(0,0,0,.35);
}

.light {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: #000;
    box-shadow: 0 0 18px #333;
    margin-bottom: 12px;
}

.green {
    background: #00d26a;
    box-shadow: 0 0 28px #00d26a;
}

.blue {
    background: #147cff;
    box-shadow: 0 0 28px #147cff;
}

.red {
    background: #ff2b2b;
    box-shadow: 0 0 28px #ff2b2b;
}

.black {
    background: #000;
    box-shadow: 0 0 18px #333;
}

.progress-wrap {
    background: #333;
    border-radius: 20px;
    overflow: hidden;
    height: 26px;
    margin: 12px 0;
}

.progress-bar {
    height: 26px;
    width: 0%;
    background: white;
    transition: .3s;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 14px;
    font-size: 16px;
    font-weight: bold;
    margin-top: 9px;
}

.start {
    background: #00d26a;
    color: #000;
}

.stop {
    background: #ff2b2b;
    color: #fff;
}

.run {
    background: #147cff;
    color: #fff;
}

.small {
    color: #bbb;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
}

.item {
    border-top: 1px solid #333;
    padding-top: 8px;
    margin-top: 8px;
}
</style>
</head>
<body>

<h1>MoltBot Control</h1>

<div class="card">
    <div id="light" class="light black"></div>
    <h2 id="pc">Cargando...</h2>

    <div class="progress-wrap">
        <div id="bar" class="progress-bar"></div>
    </div>

    <p id="percent">Mejora del ciclo: 0%</p>
    <p id="task">Ahora: -</p>
    <p id="step" class="small">Paso exacto: -</p>
    <p id="meta" class="small"></p>

    <button class="start" onclick="startAuto()">Activar automejora 24/7</button>
    <button class="run" onclick="runNow()">Forzar ciclo ahora</button>
    <button class="stop" onclick="stopAuto()">Pausar automejora</button>
</div>

<div class="card">
    <h2>Integraciones</h2>
    <p id="integrations" class="small">Cargando...</p>
</div>

<div class="card">
    <h2>Pendiente</h2>
    <div id="backlog" class="small"></div>
</div>

<div class="card">
    <h2>Qué ha hecho</h2>
    <div id="history" class="small"></div>
</div>

<div class="card">
    <h2>Logs</h2>
    <div id="logs" class="small"></div>
</div>

<script>
function colorFor(state) {
    if (state === "done") return "green";
    if (state === "working") return "blue";
    if (state === "error") return "red";
    return "black";
}

async function loadProgress() {
    try {
        const p = await (await fetch("/api/progress")).json();

        document.getElementById("light").className = "light " + colorFor(p.state);
        document.getElementById("pc").innerText = p.pc || "PC";

        const percent = p.percent || 0;
        document.getElementById("bar").style.width = percent + "%";
        document.getElementById("percent").innerText = "Mejora del ciclo: " + percent + "%";

        document.getElementById("task").innerText = "Ahora: " + (p.current_task || "-");
        document.getElementById("step").innerText = "Paso exacto: " + (p.current_step || "-");

        document.getElementById("meta").innerText =
            "Hechas: " + (p.tasks_done || 0) + "/" + (p.tasks_total || 0) +
            "\\nErrores: " + (p.tasks_error || 0) +
            "\\nÚltima actualización: " + (p.last_update || "-") +
            "\\nAutomejora 24/7: " + (p.automejora_24_7 ? "ACTIVA" : "PAUSADA");

    } catch (e) {
        document.getElementById("light").className = "light black";
        document.getElementById("pc").innerText = "Offline";
        document.getElementById("task").innerText = "Ahora: el PC no responde";
    }
}

async function loadIntegrations() {
    try {
        const i = await (await fetch("/api/integrations/status")).json();

        document.getElementById("integrations").innerText =
            "Cuenta Google: " + i.google_account +
            "\\nGoogle credentials: " + (i.google_credentials ? "OK" : "PENDIENTE") +
            "\\nGoogle token Drive/Gmail: " + (i.google_token ? "OK" : "PENDIENTE") +
            "\\nGitHub token: " + (i.github_token ? "OK" : "PENDIENTE");

    } catch (e) {
        document.getElementById("integrations").innerText = "No se pudo leer integraciones.";
    }
}

async function loadBacklog() {
    try {
        const b = await (await fetch("/api/backlog")).json();

        document.getElementById("backlog").innerHTML = b.map(x =>
            "<div class='item'><b>" + (x.titulo || x.title || "-") + "</b><br>" +
            "Estado: " + (x.estado || x.status || "-") + "<br>" +
            "Prioridad: " + (x.prioridad || x.priority || "-") + "</div>"
        ).join("");

    } catch (e) {
        document.getElementById("backlog").innerText = "No se pudo leer backlog.";
    }
}

async function loadHistory() {
    try {
        const h = await (await fetch("/api/history")).json();

        document.getElementById("history").innerHTML = h.slice(-10).reverse().map(x =>
            "<div class='item'>" +
            (x.time || "-") + "<br>" +
            "<b>" + (x.task || "-") + "</b><br>" +
            (x.step || "-") + "<br>" +
            "Progreso: " + (x.percent || 0) + "%" +
            "</div>"
        ).join("");

    } catch (e) {
        document.getElementById("history").innerText = "No se pudo leer historial.";
    }
}

async function loadLogs() {
    try {
        const l = await (await fetch("/api/logs")).json();
        document.getElementById("logs").innerText =
            "Archivo: " + (l.file || "-") + "\\n\\n" + (l.logs || "");
    } catch (e) {
        document.getElementById("logs").innerText = "No se pudo leer logs.";
    }
}

async function startAuto() {
    await fetch("/api/automejora/start", { method: "POST" });
    loadAll();
}

async function stopAuto() {
    await fetch("/api/automejora/stop", { method: "POST" });
    loadAll();
}

async function runNow() {
    await fetch("/api/automejora/run-now", { method: "POST" });
    loadAll();
}

async function loadAll() {
    await loadProgress();
    await loadIntegrations();
    await loadBacklog();
    await loadHistory();
    await loadLogs();
}

setInterval(loadAll, 3000);
loadAll();
</script>

</body>
</html>
"""