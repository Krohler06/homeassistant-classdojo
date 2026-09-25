"""Privacy-preserving diagnostics for ClassDojo responses.

Only report structural metadata (types, counts, and sanitized key names). Never
include response values, headers, cookies, tokens, or raw payloads.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import ClassDojoConfigEntry

# These keys may contain personal data or credentials even when used as mapping
# keys. Do not return them in structural summaries.
_SENSITIVE_KEY_PARTS = (
    "name", "email", "user", "student", "child", "parent", "teacher",
    "school", "class", "avatar", "photo", "image", "token", "secret",
    "password", "cookie", "auth", "session", "phone", "address", "id",
)
_MAX_DEPTH = 5
_MAX_KEYS = 40
_MAX_ITEMS = 10


def _safe_key(key: Any) -> str:
    """Return a key only if it cannot identify a person or authenticate."""
    text = str(key)
    lowered = text.lower()
    if any(part in lowered for part in _SENSITIVE_KEY_PARTS):
        return "[redacted-key]"
    # Avoid leaking arbitrary server-provided key contents.
    if len(text) > 64 or not all(c.isalnum() or c in "_-" for c in text):
        return "[omitted-key]"
    return text


def _shape(value: Any, depth: int = 0) -> Any:
    """Summarize JSON-like data without returning any leaf values."""
    if isinstance(value, Mapping):
        if depth >= _MAX_DEPTH:
            return {"type": "object", "key_count": len(value)}
        fields: dict[str, Any] = {}
        for key, child in list(value.items())[:_MAX_KEYS]:
            safe = _safe_key(key)
            # Merge potentially colliding redacted names rather than exposing them.
            if safe in fields:
                continue
            fields[safe] = _shape(child, depth + 1)
        result: dict[str, Any] = {"type": "object", "fields": fields}
        if len(value) > _MAX_KEYS:
            result["omitted_key_count"] = len(value) - _MAX_KEYS
        return result
    if isinstance(value, (list, tuple)):
        sample = value[:_MAX_ITEMS]
        result = {"type": "array", "count": len(value)}
        if sample:
            # Report shapes only; no actual values are emitted.
            result["item_shapes"] = list(dict.fromkeys(
                repr(_shape(item, depth + 1)) for item in sample
            ))[:3]
        return result
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return type(value).__name__


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ClassDojoConfigEntry
) -> dict[str, Any]:
    """Return safe response structure and integration health metadata."""
    coordinator = entry.runtime_data
    client = getattr(coordinator, "client", None)
    payload = getattr(client, "last_payload", None) if client else None
    return {
        "entry": async_redact_data(entry.as_dict(), {"data", "options"}),
        "response_shape": _shape(payload) if payload is not None else None,
        "response_received": payload is not None,
    }
