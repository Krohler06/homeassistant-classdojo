"""Sensor platform for the ClassDojo integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_STUDENT_ID, DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ClassDojoSensorEntityDescription(SensorEntityDescription):
    """Describe a ClassDojo sensor."""

    value_fn: callable
    attrs_fn: callable = lambda data: {}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ClassDojo sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    student_id = entry.data.get(CONF_STUDENT_ID, "student")
    student_name = student_id

    # Try to resolve a friendly student name from latest coordinator data
    if coordinator.data and isinstance(coordinator.data, dict):
        students = coordinator.data.get("students") or []
        for s in students:
            if isinstance(s, dict) and (
                s.get("id") == student_id or s.get("studentId") == student_id
            ):
                student_name = s.get("name") or student_name
                break

    entities: list[SensorEntity] = []
    for key, meta in SENSOR_TYPES.items():
        description = _build_description(key, meta)
        entities.append(
            ClassDojoSensor(
                coordinator=coordinator,
                description=description,
                entry=entry,
                student_id=student_id,
                student_name=student_name,
            )
        )

    async_add_entities(entities)


def _build_description(key: str, meta: dict[str, Any]) -> ClassDojoSensorEntityDescription:
    """Build a SensorEntityDescription for a given sensor key."""

    def _value_fn(data: dict[str, Any] | None) -> Any:
        if not data:
            return None
        student = _get_student(data, _student_id_ctx.get())
        if student is None:
            return None
        if key == "total_points":
            return student.get("total_points")
        if key == "positive_points":
            return student.get("positive_points")
        if key == "negative_points":
            return student.get("negative_points")
        if key == "needs_improvement_points":
            return student.get("needs_improvement_points")
        if key == "class_count":
            classes = student.get("classes") or []
            return len(classes)
        if key == "skills_count":
            skills = student.get("skills") or []
            return len(skills)
        if key == "last_activity":
            ts = student.get("last_activity")
            if ts is None:
                return None
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return None

    def _attrs_fn(data: dict[str, Any] | None) -> dict[str, Any]:
        if not data:
            return {}
        student = _get_student(data, _student_id_ctx.get())
        if student is None:
            return {}
        attrs: dict[str, Any] = {
            "student_id": student.get("id") or student.get("studentId"),
            "name": student.get("name"),
        }
        if student.get("classes"):
            attrs["classes"] = [
                c.get("name") if isinstance(c, dict) else c
                for c in student["classes"]
            ]
        if student.get("skills"):
            attrs["skills"] = student["skills"]
        return attrs

    return ClassDojoSensorEntityDescription(
        key=key,
        name=meta["name"],
        icon=meta.get("icon"),
        native_unit_of_measurement=meta.get("unit"),
        device_class=meta.get("device_class"),
        state_class=meta.get("state_class"),
        value_fn=_value_fn,
        attrs_fn=_attrs_fn,
    )


# Simple context to carry student id into description callables.
_student_id_ctx: dict[str, str] = {}


def _get_student(data: dict[str, Any], student_id: str) -> dict[str, Any] | None:
    """Return the requested student payload from coordinator data."""
    students = data.get("students") or []
    for s in students:
        if not isinstance(s, dict):
            continue
        if (
            s.get("id") == student_id
            or s.get("studentId") == student_id
            or s.get("name") == student_id
        ):
            return s
    return students[0] if students else None


class ClassDojoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a ClassDojo sensor."""

    _attr_has_entity_name = True
    entity_description: ClassDojoSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: ClassDojoSensorEntityDescription,
        entry: ConfigEntry,
        student_id: str,
        student_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._student_id = student_id
        self._student_name = student_name
        _student_id_ctx["id"] = student_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{student_id}")},
            name=f"ClassDojo {student_name}",
            manufacturer="ClassDojo",
            model="Student",
            entry_type=None,
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor's current value."""
        _student_id_ctx["id"] = self._student_id
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        _student_id_ctx["id"] = self._student_id
        return self.entity_description.attrs_fn(self.coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
