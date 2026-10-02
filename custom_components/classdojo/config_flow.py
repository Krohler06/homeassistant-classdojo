"""Config flow for ClassDojo."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ClassDojoApiClient, ClassDojoAuthError, ClassDojoConnectionError
from .const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_STUDENT_ID, DEFAULT_SCAN_INTERVAL, DOMAIN, ERROR_AUTH_INVALID, ERROR_CANNOT_CONNECT, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def _validate_credentials(hass: HomeAssistant, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate email/password and discover linked students."""
    client = ClassDojoApiClient(email=data[CONF_EMAIL], password=data[CONF_PASSWORD], session=async_get_clientsession(hass))
    try:
        await client.async_login()
        return await client.async_get_students()
    except ClassDojoAuthError as err:
        raise InvalidAuth from err
    except ClassDojoConnectionError as err:
        raise CannotConnect from err


class ClassDojoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the two-step ClassDojo config flow."""

    VERSION = 2

    def __init__(self) -> None:
        self._email: str | None = None
        self._password: str | None = None
        self._students: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Collect credentials and discover students."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._students = await _validate_credentials(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = ERROR_AUTH_INVALID
            except CannotConnect:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                self._email = user_input[CONF_EMAIL]
                self._password = user_input[CONF_PASSWORD]
                return await self.async_step_student()
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required(CONF_EMAIL): str, vol.Required(CONF_PASSWORD): str}), errors=errors)

    async def async_step_student(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Select a student discovered from the authenticated family account."""
        if user_input is not None:
            student_id = user_input[CONF_STUDENT_ID]
            await self.async_set_unique_id(f"{self._email}_{student_id}")
            self._abort_if_unique_id_configured()
            name = next((s.get("name") for s in self._students if (s.get("id") or s.get("studentId") or s.get("name")) == student_id), student_id)
            return self.async_create_entry(title=f"ClassDojo - {name}", data={CONF_EMAIL: self._email, CONF_PASSWORD: self._password, CONF_STUDENT_ID: student_id})
        if not self._students:
            return self.async_abort(reason="no_students")
        options = {s.get("id") or s.get("studentId") or s.get("name"): s.get("name", "Unknown") for s in self._students}
        return self.async_show_form(step_id="student", data_schema=vol.Schema({vol.Required(CONF_STUDENT_ID): vol.In(options)}))

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return ClassDojoOptionsFlow(config_entry)


class ClassDojoOptionsFlow(config_entries.OptionsFlow):
    """Handle ClassDojo options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current = self.config_entry.options.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds() // 60))
        schema = vol.Schema({vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(cv.positive_int, vol.Range(min=int(MIN_SCAN_INTERVAL.total_seconds() // 60), max=int(MAX_SCAN_INTERVAL.total_seconds() // 60)))})
        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(Exception):
    """Cannot connect to the service."""


class InvalidAuth(Exception):
    """Credentials were rejected or authentication is not verified."""
