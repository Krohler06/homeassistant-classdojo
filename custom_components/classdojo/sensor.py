"""Sensor platform for ClassDojo."""
from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ClassDojo sensor based on a config entry."""
    username = entry.data.get("username", "Account")
    async_add_entities([ClassDojoStatusSensor(entry.entry_id, username)], True)

class ClassDojoStatusSensor(SensorEntity):
    """Representation of a ClassDojo Status Sensor."""

    def __init__(self, entry_id: str, username: str) -> None:
        """Initialize the sensor."""
        self._attr_name = f"ClassDojo {username} Status"
        self._attr_unique_id = f"{entry_id}_status"
        self._attr_native_value = "Connected"
        self._attr_icon = "mdi:school"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return extra attributes."""
        return {
            "integration": "ClassDojo",
            "status": "Ready",
        }
