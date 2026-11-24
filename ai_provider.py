from __future__ import annotations
import json
import urllib.error
import urllib.request
from ai_schema import extract_json, schema_prompt, normalize, PackSpec

class LocalAIError(RuntimeError):
    pass

class OllamaProvider:
    def __init__(self, base_url="http://127.0.0.1:11434", model="llama3.2", timeout=120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def models(self):
        request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LocalAIError(f"Could not reach Ollama at {self.base_url}. Is Ollama running?") from exc
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]

    def generate_plan(self, user_prompt, platform) -> PackSpec:
        body = {
            "model": self.model, "prompt": schema_prompt(user_prompt, platform),
            "stream": False, "format": "json", "options": {"temperature": 0.15}
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/generate", data=json.dumps(body).encode(),
            headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            raise LocalAIError(f"Ollama returned HTTP {exc.code}.") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LocalAIError(f"Could not reach Ollama at {self.base_url}. Is Ollama running?") from exc
        return normalize(extract_json(payload.get("response", "")))
