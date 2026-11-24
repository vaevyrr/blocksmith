from __future__ import annotations
import json
import os
import platform
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

OLLAMA_BASE = "http://127.0.0.1:11434"
INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"

class SetupError(RuntimeError):
    pass

def _request_json(url: str, timeout: int = 5):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)

def ollama_ready() -> bool:
    try:
        _request_json(f"{OLLAMA_BASE}/api/tags", timeout=2)
        return True
    except Exception:
        return False

def installed_models() -> list[str]:
    data = _request_json(f"{OLLAMA_BASE}/api/tags", timeout=5)
    return [item.get("name", "") for item in data.get("models", []) if item.get("name")]

def _download_installer(progress: Callable[[str], None]) -> Path:
    if platform.system() != "Windows":
        raise SetupError("Automatic Ollama installation is currently supported on Windows only. Install Ollama from https://ollama.com/download.")
    target = Path(tempfile.gettempdir()) / "BlockSmith-OllamaSetup.exe"
    request = urllib.request.Request(INSTALLER_URL, headers={"User-Agent": "BlockSmith-Setup/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            total = int(response.headers.get("Content-Length", "0") or 0)
            downloaded = 0
            with target.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        progress(f"Downloading Ollama installer: {downloaded * 100 // total}%")
                    else:
                        progress(f"Downloading Ollama installer: {downloaded // (1024 * 1024)} MB")
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise SetupError(f"Could not download the official Ollama installer: {exc}") from exc
    if not target.exists() or target.stat().st_size < 1_000_000:
        target.unlink(missing_ok=True)
        raise SetupError("The downloaded installer looks incomplete. Please retry or install from ollama.com.")
    # Only launch a properly signed Windows installer.
    escaped_path = str(target).replace("'", "''")
    check = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"(Get-AuthenticodeSignature -LiteralPath '{escaped_path}').Status"],
        capture_output=True, text=True, timeout=20
    )
    if check.returncode != 0 or "Valid" not in check.stdout:
        target.unlink(missing_ok=True)
        raise SetupError("Windows could not verify the installer's digital signature. The file was not run.")
    return target

def ensure_ollama_installed(progress: Callable[[str], None]) -> None:
    if ollama_ready():
        return
    installer = _download_installer(progress)
    progress("Starting the official Ollama installer. Complete its setup window to continue...")
    try:
        # Keep the official interactive installer visible; do not bypass user consent/UAC.
        process = subprocess.Popen([str(installer)])
        while process.poll() is None:
            time.sleep(0.5)
        if process.returncode not in (0, None):
            raise SetupError(f"Ollama installer exited with code {process.returncode}.")
    finally:
        try:
            installer.unlink(missing_ok=True)
        except OSError:
            pass

    progress("Waiting for Ollama to start...")
    for attempt in range(90):
        if ollama_ready():
            return
        if attempt == 15:
            # If the tray app did not start automatically, try the installed CLI.
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama app.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",
            ]
            for candidate in candidates:
                if candidate.exists():
                    try:
                        subprocess.Popen([str(candidate)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        break
                    except OSError:
                        continue
        time.sleep(1)
    raise SetupError("Ollama installed, but its local service did not start. Start Ollama from the Windows Start menu and retry.")

def pull_model(model: str, progress: Callable[[str], None]) -> None:
    model = model.strip()
    if not model:
        raise SetupError("Enter a model name, such as llama3.2:3b.")
    body = json.dumps({"name": model, "stream": True}).encode("utf-8")
    request = urllib.request.Request(
        f"{OLLAMA_BASE}/api/pull", data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            for raw_line in response:
                if not raw_line.strip():
                    continue
                item = json.loads(raw_line.decode("utf-8"))
                if item.get("error"):
                    raise SetupError(item["error"])
                status = item.get("status", "Downloading model...")
                total, completed = item.get("total"), item.get("completed")
                if isinstance(total, int) and total > 0 and isinstance(completed, int):
                    progress(f"{status}: {completed * 100 // total}% ({completed // (1024*1024)} / {total // (1024*1024)} MB)")
                else:
                    progress(status)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise SetupError(f"Ollama model download failed (HTTP {exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise SetupError(f"Could not connect to Ollama: {exc}") from exc

def setup_local_ai(model: str, progress: Callable[[str], None]) -> None:
    ensure_ollama_installed(progress)
    existing = installed_models()
    if any(name == model or name.startswith(model + ":") for name in existing):
        progress(f"Model {model} is already installed.")
        return
    progress(f"Downloading local model {model}. This may take several minutes...")
    pull_model(model, progress)
    if not any(name == model or name.startswith(model + ":") for name in installed_models()):
        raise SetupError("Ollama finished the pull, but the model was not found in its model list.")
    progress(f"Setup complete. {model} is ready.")
