from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import DOMAIN

TO_REDACT = {"email", "password", "token", "access_token", "refresh_token"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return sanitized config-entry diagnostics."""
    runtime = getattr(entry, "runtime_data", None)
    coordinator = getattr(runtime, "coordinator", None)
    result = {
        "integration": DOMAIN,
        "version": entry.version,
        "minor_version": entry.minor_version,
        "options": async_redact_data(dict(entry.options), TO_REDACT),
        "runtime_data": {
            "last_refresh": getattr(runtime, "last_refresh", None),
            "last_refresh_success": getattr(runtime, "last_refresh_success", None),
            "last_refresh_error": getattr(runtime, "last_refresh_error", None),
            "last_refresh_duration": getattr(runtime, "last_refresh_duration", None),
            "data_summary": getattr(runtime, "data_summary", {}),
            "coordinator_last_update_success": (
                coordinator.last_update_success if coordinator else None
            ),
        },
    }
    return async_redact_data(result, TO_REDACT)
