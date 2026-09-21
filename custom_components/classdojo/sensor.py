"""ClassDojo sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator, _client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ClassDojoAccountSensor(coordinator, entry)], update_before_add=True)
    children = coordinator.data.get("children", []) if coordinator.data else []
    async_add_entities([ClassDojoChildSensor(coordinator, entry, child) for child in children], update_before_add=True)


class ClassDojoAccountSensor(CoordinatorEntity, SensorEntity):
    """Account connectivity sensor."""
    _attr_name = "ClassDojo account"
    _attr_icon = "mdi:school"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_account"

    @property
    def native_value(self):
        return "connected" if self.coordinator.data.get("connected") else "unavailable"

    @property
    def extra_state_attributes(self):
        data = dict(self.coordinator.data or {})
        data.pop("children", None)
        return data


class ClassDojoChildSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a discovered child."""

    def __init__(self, coordinator, entry, child):
        super().__init__(coordinator)
        self.child_id = str(child.get("id") or child.get("name"))
        self._attr_unique_id = f"{entry.entry_id}_child_{self.child_id}"
        self._attr_name = child.get("name", f"Child {self.child_id}")
        self._attr_icon = "mdi:account-child"

    @property
    def native_value(self):
        child = next((c for c in self.coordinator.data.get("children", []) if str(c.get("id") or c.get("name")) == self.child_id), {})
        return child.get("points", child.get("score"))

    @property
    def extra_state_attributes(self):
        return next((c for c in self.coordinator.data.get("children", []) if str(c.get("id") or c.get("name")) == self.child_id), {})
