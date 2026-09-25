from __future__ import annotations

from datetime import datetime
import logging
from time import monotonic

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ClassDojoClient
from .const import DOMAIN, PLATFORMS, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = ClassDojoClient(
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )

    async def async_update_data():
        started = monotonic()
        _LOGGER.debug("Starting ClassDojo data refresh")
        try:
            data = await hass.async_add_executor_job(client.fetch_data)
        except Exception as err:
            duration = round(monotonic() - started, 2)
            entry.runtime_data.last_refresh = datetime.now().isoformat()
            entry.runtime_data.last_refresh_success = False
            entry.runtime_data.last_refresh_error = type(err).__name__
            _LOGGER.exception(
                "ClassDojo data refresh failed after %.2f seconds (%s)",
                duration,
                type(err).__name__,
            )
            raise UpdateFailed(f"ClassDojo refresh failed ({type(err).__name__})") from err

        duration = round(monotonic() - started, 2)
        entry.runtime_data.last_refresh = datetime.now().isoformat()
        entry.runtime_data.last_refresh_success = True
        entry.runtime_data.last_refresh_error = None
        entry.runtime_data.last_refresh_duration = duration
        entry.runtime_data.data_summary = _summarize_data(data)
        _LOGGER.debug(
            "ClassDojo data refresh completed in %.2f seconds; data summary: %s",
            duration,
            entry.runtime_data.data_summary,
        )
        return data

    entry.runtime_data = type("ClassDojoRuntimeData", (), {})()
    entry.runtime_data.last_refresh = None
    entry.runtime_data.last_refresh_success = False
    entry.runtime_data.last_refresh_error = None
    entry.runtime_data.last_refresh_duration = None
    entry.runtime_data.data_summary = {}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        if isinstance(err, ConfigEntryNotReady):
            raise
        raise ConfigEntryNotReady(f"ClassDojo first refresh failed ({type(err).__name__})") from err

    entry.runtime_data.coordinator = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


def _summarize_data(data: object) -> dict[str, int | str]:
    """Return structural counts only; never include names, IDs, or values."""
    if isinstance(data, dict):
        summary: dict[str, int | str] = {"top_level_keys": len(data)}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                # Report only counts, not field names or payload contents.
                summary[f"{type(value).__name__}_items"] = len(value)
        return summary
    if isinstance(data, (list, tuple, set)):
        return {"collection_items": len(data)}
    return {"data_type": type(data).__name__}


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
