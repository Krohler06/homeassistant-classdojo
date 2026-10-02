"""Constants for the ClassDojo integration."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "classdojo"
PLATFORMS = ["sensor"]

CONF_EMAIL = "email"
CONF_USERNAME = "username"  # Legacy key retained for existing entries.
CONF_PASSWORD = "password"
CONF_STUDENT_ID = "student_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
MIN_SCAN_INTERVAL = timedelta(minutes=5)
MAX_SCAN_INTERVAL = timedelta(hours=12)

API_BASE_URL = "https://api.classdojo.com/v2"
API_TIMEOUT = 20

SENSOR_TYPES = {
    "total_points": {"key": "total_points", "name": "Total Points", "icon": "mdi:trophy", "unit": "points", "device_class": None, "state_class": "total"},
    "positive_points": {"key": "positive_points", "name": "Positive Points", "icon": "mdi:thumb-up", "unit": "points", "device_class": None, "state_class": "total_increasing"},
    "negative_points": {"key": "negative_points", "name": "Negative Points", "icon": "mdi:thumb-down", "unit": "points", "device_class": None, "state_class": "total_increasing"},
    "needs_improvement_points": {"key": "needs_improvement_points", "name": "Needs Improvement Points", "icon": "mdi:alert-circle", "unit": "points", "device_class": None, "state_class": "total_increasing"},
    "class_count": {"key": "class_count", "name": "Active Classes", "icon": "mdi:school", "unit": "classes", "device_class": None, "state_class": "measurement"},
    "skills_count": {"key": "skills_count", "name": "Skills Count", "icon": "mdi:star-circle", "unit": "skills", "device_class": None, "state_class": "measurement"},
    "last_activity": {"key": "last_activity", "name": "Last Activity", "icon": "mdi:clock-outline", "unit": None, "device_class": "timestamp", "state_class": None},
}

ERROR_AUTH_INVALID = "invalid_auth"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_UNKNOWN = "unknown"
