from __future__ import annotations

from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            ClassDojoRefreshSensor(entry, "last_refresh", "Dernière actualisation"),
            ClassDojoRefreshSensor(entry, "refresh_status", "État de l’actualisation"),
            ClassDojoRefreshSensor(entry, "items_received", "Éléments reçus"),
        ]
    )


class ClassDojoRefreshSensor(CoordinatorEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry, key: str, name: str) -> None:
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        coordinator = entry.runtime_data.coordinator
        super().__init__(coordinator)

    @property
    def native_value(self):
        runtime = self._entry.runtime_data
        if self._key == "last_refresh":
            return getattr(runtime, "last_refresh", None)
        if self._key == "refresh_status":
            return "Réussie" if getattr(runtime, "last_refresh_success", False) else (
                "Échec" if getattr(runtime, "last_refresh", None) else "En attente"
            )
        summary = getattr(runtime, "data_summary", {})
        return sum(value for value in summary.values() if isinstance(value, int))
