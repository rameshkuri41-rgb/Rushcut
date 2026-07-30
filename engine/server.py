"""
Rushcut Engine API — FastAPI + SQLite job queue.
$0 stack, no redis, no celery.

Endpoints:
  POST /jobs {topic, n_scenes} -> job_id
  GET  /jobs/{id} -> status
  GET  /jobs -> list
  GET  /output/{run_id}/rushcut_final.mp4

Run: uvicorn server:app --port 8000 --reload
"""
import os
import sqlite3
import time
import uuid
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).parent
DB = BASE / "jobs.db"
OUTPUT = BASE / "output"

# ensure .env loaded (same as pipeline.py)
_env_path = BASE / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                k, v = _line.split("=", 1)
                if v and k not in os.environ:
                    os.environ[k] = v

from pipeline import run as run_pipeline

app = FastAPI(title="Rushcut Engine", version="1.0")

# ---- db ----
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        topic TEXT,
        n_scenes INTEGER,
        status TEXT,
        output_path TEXT,
        error TEXT,
        created_at REAL,
        finished_at REAL
    )
    """)
    conn.commit()
    conn.close()

init_db()

class JobCreate(BaseModel):
    topic: str
    n_scenes: int = 6
    out_name: Optional[str] = None

def do_job(job_id: str, topic: str, n_scenes: int, out_name: str):
    conn = get_db()
    try:
        final_path = run_pipeline(topic, n_scenes, out_name=out_name)
        conn.execute("UPDATE jobs SET status='done', output_path=?, finished_at=? WHERE id=?",
                     (final_path, time.time(), job_id))
        conn.commit()
    except Exception as e:
        conn.execute("UPDATE jobs SET status='failed', error=?, finished_at=? WHERE id=?",
                     (str(e), time.time(), job_id))
        conn.commit()
        print(f"[job {job_id}] failed: {e}")
    finally:
        conn.close()

@app.post("/jobs")
def create_job(payload: JobCreate, bg: BackgroundTasks):
    job_id = uuid.uuid4().hex[:10]
    run_id = payload.out_name or job_id
    conn = get_db()
    conn.execute("INSERT INTO jobs (id, topic, n_scenes, status, created_at) VALUES (?,?,?,?,?)",
                 (job_id, payload.topic, payload.n_scenes, "queued", time.time()))
    conn.commit()
    conn.close()
    bg.add_task(do_job, job_id, payload.topic, payload.n_scenes, run_id)
    return {"job_id": job_id, "status": "queued", "run_id": run_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "job not found")
    d = dict(row)
    if d["output_path"]:
        d["video_url"] = f"/output/{Path(d['output_path']).parent.name}/rushcut_final.mp4"
    return d

@app.get("/jobs")
def list_jobs():
    conn = get_db()
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Serve output dir
OUTPUT.mkdir(exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT), name="output")

@app.get("/")
def health():
    return {"ok": True, "engine": "rushcut $0", "output": str(OUTPUT)}
