"""Constants for the Ambientika Smart integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "ambientika"

# Configuration
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_DEVICE_SERIAL: Final = "device_serial"
CONF_DEVICE_ROLE: Final = "device_role"

# Device roles
DEVICE_ROLE_MASTER: Final = "master"
DEVICE_ROLE_SLAVE: Final = "slave"

# API endpoints
API_BASE_URL: Final = "https://app.ambientika.eu:4521"
API_AUTH_ENDPOINT: Final = f"{API_BASE_URL}/users/authenticate"
API_DEVICE_STATUS_ENDPOINT: Final = f"{API_BASE_URL}/device/device-status"
API_CHANGE_MODE_ENDPOINT: Final = f"{API_BASE_URL}/device/change-mode"
API_RESET_FILTER_ENDPOINT: Final = f"{API_BASE_URL}/device/reset-filter"
API_TOKEN_INFO_ENDPOINT: Final = f"{API_BASE_URL}/users/token-info"

# Update intervals
UPDATE_INTERVAL: Final = 30  # seconds
TOKEN_REFRESH_THRESHOLD: Final = 5  # days

# Operation modes
OPERATION_MODES: Final = [
    "Smart",
    "Auto",
    "ManualHeatRecovery",
    "Night",
    "AwayHome",
    "Surveillance",
    "TimedExpulsion",
    "Expulsion",
    "Intake",
    "MasterSlaveFlow",
    "SlaveMasterFlow",
    "Off",
]

# Fan speeds
FAN_SPEEDS: Final = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
}

# Humidity levels
HUMIDITY_LEVELS: Final = {
    "Dry": 1,
    "Normal": 2,
    "Moist": 3,
}

# Light sensor levels
LIGHT_SENSOR_LEVELS: Final = {
    "NotAvailable": 0,
    "Off": 0,
    "Low": 1,
    "Medium": 2,
}

# Filter status
FILTER_STATUS_GOOD: Final = "Good"
FILTER_STATUS_MEDIUM: Final = "Medium"
FILTER_STATUS_BAD: Final = "Bad"

# Device classes
DEVICE_CLASS_TEMPERATURE: Final = "temperature"
DEVICE_CLASS_HUMIDITY: Final = "humidity"

# Unit of measurement
UNIT_CELSIUS: Final = "°C"
UNIT_PERCENT: Final = "%"
UNIT_LQI: Final = "lqi"

# Icons
ICON_HVAC: Final = "mdi:hvac"
ICON_HVAC_OFF: Final = "mdi:hvac-off"
ICON_FAN: Final = "mdi:fan"
ICON_FAN_SPEED_1: Final = "mdi:fan-speed-1"
ICON_FAN_SPEED_2: Final = "mdi:fan-speed-2"
ICON_FAN_SPEED_3: Final = "mdi:fan-speed-3"
ICON_FAN_ALERT: Final = "mdi:fan-alert"
ICON_WATER: Final = "mdi:water"
ICON_WATER_PERCENT: Final = "mdi:water-percent"
ICON_WATER_PERCENT_ALERT: Final = "mdi:water-percent-alert"
ICON_THERMOMETER: Final = "mdi:thermometer"
ICON_AIR_FILTER: Final = "mdi:air-filter"
ICON_MOLECULE_CO2: Final = "mdi:molecule-co2"
ICON_STAR_BOX: Final = "mdi:star-box"
ICON_LINK_BOX_VARIANT: Final = "mdi:link-box-variant"
ICON_HELP_BOX: Final = "mdi:help-box"
ICON_THEME_LIGHT_DARK: Final = "mdi:theme-light-dark"
ICON_WIFI: Final = "mdi:wifi"
ICON_LEAF_CIRCLE_OUTLINE: Final = "mdi:leaf-circle-outline"
ICON_FORM_SELECT: Final = "mdi:form-select"
ICON_KEY_CHAIN: Final = "mdi:key-chain"

# Services
SERVICE_RESET_FILTER: Final = "reset_filter"
SERVICE_CHANGE_MODE: Final = "change_mode"

# Platforms
PLATFORMS: Final = [
    "sensor",
    "binary_sensor",
    "switch",
    "number",
    "select",
]