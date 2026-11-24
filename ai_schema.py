from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PackSpec:
    name: str
    platform: str
    namespace: str
    description: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    blocks: list[dict[str, Any]] = field(default_factory=list)
    recipes: list[dict[str, Any]] = field(default_factory=list)
    functions: list[dict[str, Any]] = field(default_factory=list)
    textures: list[dict[str, Any]] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)

def _clean_id(value: str, fallback: str = "pack") -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", str(value).strip().lower()).strip("_")
    return (value or fallback)[:32]

def normalize(raw: dict[str, Any]) -> PackSpec:
    if not isinstance(raw, dict):
        raise ValueError("AI response was not a JSON object.")
    platform = str(raw.get("platform", "bedrock")).lower()
    if platform not in {"bedrock", "java"}:
        raise ValueError("platform must be 'bedrock' or 'java'.")
    name = str(raw.get("name") or "Generated Pack").strip()
    namespace = _clean_id(str(raw.get("namespace") or name), "pack")
    def list_of_dicts(key: str) -> list[dict[str, Any]]:
        value = raw.get(key, [])
        if value is None: return []
        if not isinstance(value, list): raise ValueError(f"{key} must be a list.")
        return [x for x in value if isinstance(x, dict)]
    return PackSpec(
        name=name[:80], platform=platform, namespace=namespace,
        description=str(raw.get("description", "")).strip()[:300],
        items=list_of_dicts("items"), blocks=list_of_dicts("blocks"),
        recipes=list_of_dicts("recipes"), functions=list_of_dicts("functions"),
        textures=list_of_dicts("textures"),
        effects=[str(x) for x in raw.get("effects", []) if isinstance(x, (str,int,float))][:50],
    )

def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try: return json.loads(text[start:end + 1])
            except json.JSONDecodeError as exc: raise ValueError(f"Could not parse AI JSON: {exc}") from exc
        raise ValueError("The local AI did not return valid JSON.")

def schema_prompt(user_prompt: str, platform: str) -> str:
    return f"""You are the planning engine inside BlockSmith, a Minecraft pack generator.
Return ONLY valid JSON. Never return markdown or commentary.
The target platform is {platform}.
Turn the user's natural-language request into a practical pack specification.
Do not invent unsupported Minecraft features. Prefer simple deterministic files.
JSON shape:
{{
  "name": "Pack name", "platform": "{platform}", "namespace": "lowercase_namespace",
  "description": "short description",
  "items": [{{"id":"starfall","name":"Starfall","damage":18,"durability":500,"ability":"star_projectile","cooldown":10}}],
  "blocks": [{{"id":"star_block","name":"Star Block","hardness":2.0}}],
  "recipes": [{{"id":"starfall","type":"shaped","pattern":["ABA","BCB","ABA"],"key":{{"A":"minecraft:iron_ingot","B":"minecraft:gold_ingot","C":"minecraft:diamond"}},"result":"{platform}:starfall","count":1}}],
  "functions": [{{"name":"starfall","commands":["say Starfall activated"]}}],
  "textures": [{{"id":"starfall","path":"items/starfall"}}],
  "effects": ["short description of requested visual/gameplay effects"]
}}
User request:
{user_prompt}
"""

def to_json(spec: PackSpec) -> str:
    return json.dumps(spec.__dict__, indent=2)
