"""The ClassDojo integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ClassDojoApiClient, ClassDojoAuthError
from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_STUDENT_ID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


def _entry_email(entry: ConfigEntry) -> str:
    """Read the new email key, with compatibility for old username entries."""
    return entry.data.get(CONF_EMAIL) or entry.data[CONF_USERNAME]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ClassDojo from a config entry."""
    client = ClassDojoApiClient(
        email=_entry_email(entry),
        password=entry.data[CONF_PASSWORD],
        student_id=entry.data.get(CONF_STUDENT_ID),
        session=async_get_clientsession(hass),
    )
    scan_interval = DEFAULT_SCAN_INTERVAL
    if CONF_SCAN_INTERVAL in entry.options:
        scan_interval = timedelta(minutes=entry.options[CONF_SCAN_INTERVAL])

    async def async_update_data():
        try:
            return await client.async_get_data()
        except ClassDojoAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Error fetching ClassDojo data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=async_update_data,
        update_interval=scan_interval,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy username entries without dropping stored credentials."""
    if entry.version < 2:
        data = dict(entry.data)
        if CONF_EMAIL not in data and CONF_USERNAME in data:
            data[CONF_EMAIL] = data[CONF_USERNAME]
        hass.config_entries.async_update_entry(entry, data=data, version=2)
    return True
