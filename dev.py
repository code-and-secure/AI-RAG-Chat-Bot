"""
Start both backend (FastAPI) and frontend (Vite) in a single terminal.
Usage: python dev.py
"""
import subprocess
import sys
import os
import threading
import signal

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

CYAN  = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def stream(proc: subprocess.Popen, label: str, color: str):
    assert proc.stdout
    for line in proc.stdout:
        print(f"{color}[{label}]{RESET} {line}", end="", flush=True)

processes: list[subprocess.Popen] = []

def shutdown(*_):
    print(f"\n{YELLOW}Shutting down…{RESET}")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print(f"{CYAN}[backend]{RESET} Starting FastAPI on http://localhost:8000")
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
    cwd=BACKEND_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
processes.append(backend)

print(f"{YELLOW}[frontend]{RESET} Starting Vite on http://localhost:5173")
frontend = subprocess.Popen(
    "npm run dev",
    cwd=FRONTEND_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    shell=True,
)
processes.append(frontend)

threading.Thread(target=stream, args=(backend,  "backend ",  CYAN),   daemon=True).start()
threading.Thread(target=stream, args=(frontend, "frontend", YELLOW), daemon=True).start()

print("Press Ctrl+C to stop both servers.\n")
backend.wait()
