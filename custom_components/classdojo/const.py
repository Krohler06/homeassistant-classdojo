from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "classdojo"
PLATFORMS = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(minutes=5)
