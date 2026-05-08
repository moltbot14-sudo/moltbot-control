#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path
from datetime import datetime

BASE = Path.home() / ".openclaw/automejora/state"
BASE.mkdir(parents=True, exist_ok=True)

PROGRESS_FILE = BASE / "progress.json"
HISTORY_FILE = BASE / "history.json"


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


state = sys.argv[1] if len(sys.argv) > 1 else "done"
current_task = sys.argv[2] if len(sys.argv) > 2 else "Sin tarea"
current_step = sys.argv[3] if len(sys.argv) > 3 else ""
tasks_done = int(sys.argv[4]) if len(sys.argv) > 4 else 0
tasks_total = int(sys.argv[5]) if len(sys.argv) > 5 else 0
tasks_error = int(sys.argv[6]) if len(sys.argv) > 6 else 0
auto = sys.argv[7].lower() == "true" if len(sys.argv) > 7 else False

percent = 0
if tasks_total > 0:
    percent = round((tasks_done / tasks_total) * 100)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

progress = {
    "pc": os.uname().nodename,
    "state": state,
    "percent": percent,
    "current_task": current_task,
    "current_step": current_step,
    "cycle_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
    "tasks_total": tasks_total,
    "tasks_done": tasks_done,
    "tasks_error": tasks_error,
    "last_update": now,
    "automejora_24_7": auto
}

save_json(PROGRESS_FILE, progress)

history = load_json(HISTORY_FILE, [])

history.append({
    "time": now,
    "state": state,
    "task": current_task,
    "step": current_step,
    "percent": percent,
    "tasks_done": tasks_done,
    "tasks_total": tasks_total,
    "tasks_error": tasks_error
})

history = history[-300:]

save_json(HISTORY_FILE, history)