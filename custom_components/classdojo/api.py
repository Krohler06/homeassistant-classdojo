"""API client for ClassDojo.

The upstream authentication contract is not verified here; login intentionally
fails closed until a supported protocol is documented and tested.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from yarl import URL

_LOGGER = logging.getLogger(__name__)
API_BASE_URL = "https://api.classdojo.com/v2"
STUDENTS_ENDPOINT = "/students/me"
CLASSES_ENDPOINT = "/classes"
SKILLS_ENDPOINT = "/skills"


class ClassDojoAuthError(Exception):
    """Raised when authentication is unavailable or fails."""


class ClassDojoConnectionError(Exception):
    """Raised on connection / network errors."""


class ClassDojoApiClient:
    """Async client for ClassDojo."""

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession, student_id: str | None = None, base_url: str = API_BASE_URL) -> None:
        self._email = email
        self._password = password
        self._session = session
        self._student_id = student_id
        self._base_url = base_url
        self._token: str | None = None

    async def async_login(self) -> None:
        """Fail closed: the ClassDojo login protocol is not verified."""
        raise ClassDojoAuthError("ClassDojo authentication protocol is not verified")

    async def async_get_students(self) -> list[dict[str, Any]]:
        """Return students linked to the account once authentication is supported."""
        if not self._token:
            await self.async_login()
        data = await self._async_get_json(URL(self._base_url) / STUDENTS_ENDPOINT.lstrip("/"))
        students = data.get("students") or data.get("data") or data
        if isinstance(students, dict):
            students = [students]
        return students if isinstance(students, list) else []

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch the configured student after account-level discovery."""
        students = await self.async_get_students()
        if self._student_id:
            students = [s for s in students if (s.get("id") or s.get("studentId") or s.get("name")) == self._student_id]
        enriched = []
        for student in students:
            sid = student.get("id") or student.get("studentId")
            payload = {"id": sid, "name": student.get("name") or student.get("firstName"), "total_points": student.get("total_points") or student.get("points") or 0, "positive_points": student.get("positive_points") or student.get("positives") or 0, "negative_points": student.get("negative_points") or student.get("negatives") or 0, "needs_improvement_points": student.get("needs_improvement_points") or student.get("needs_improvement") or 0, "classes": [], "skills": [], "last_activity": student.get("last_activity") or student.get("updated_at")}
            try:
                payload["classes"] = await self._fetch_classes(sid)
                payload["skills"] = await self._fetch_skills(sid)
            except ClassDojoConnectionError as err:
                _LOGGER.debug("Could not enrich student %s: %s", sid, err)
            enriched.append(payload)
        return {"students": enriched}

    async def _fetch_classes(self, student_id: str) -> list[dict[str, Any]]:
        data = await self._async_get_json(URL(self._base_url) / CLASSES_ENDPOINT.lstrip("/"), params={"studentId": student_id})
        classes = data.get("classes") or data.get("data") or []
        return [c if isinstance(c, dict) else {"name": str(c)} for c in classes] if isinstance(classes, list) else []

    async def _fetch_skills(self, student_id: str) -> list[Any]:
        try:
            data = await self._async_get_json(URL(self._base_url) / SKILLS_ENDPOINT.lstrip("/"), params={"studentId": student_id})
        except ClassDojoConnectionError:
            return []
        skills = data.get("skills") or data.get("data") or []
        return skills if isinstance(skills, list) else []

    async def _async_get_json(self, url: URL, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._token:
            await self.async_login()
        try:
            async with self._session.get(url, params=params, headers={"Authorization": f"Bearer {self._token}"}, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status == 401:
                    raise ClassDojoAuthError("Token expired or invalid")
                if resp.status >= 400:
                    raise ClassDojoConnectionError(f"GET {url} failed with status {resp.status}")
                return await resp.json(content_type=None)
        except asyncio.TimeoutError as err:
            raise ClassDojoConnectionError(f"Timeout on {url}") from err
        except aiohttp.ClientError as err:
            raise ClassDojoConnectionError(str(err)) from err
