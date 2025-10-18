"""Select platform for Ambientika Smart integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    DEVICE_ROLE_MASTER,
    DOMAIN,
    FAN_SPEEDS,
    HUMIDITY_LEVELS,
    ICON_FORM_SELECT,
    LIGHT_SENSOR_LEVELS,
    OPERATION_MODES,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambientika select based on a config entry."""
    coordinator: AmbentikaDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    device_serial = config_entry.data[CONF_DEVICE_SERIAL]
    device_role = config_entry.data[CONF_DEVICE_ROLE]

    # Only add select entity for master devices
    if device_role == DEVICE_ROLE_MASTER:
        entities: list[SelectEntity] = [
            AmbentikaOperatingModeSelect(coordinator, device_serial, device_role)
        ]
        async_add_entities(entities)


class AmbentikaOperatingModeSelect(
    CoordinatorEntity[AmbentikaDataUpdateCoordinator], SelectEntity
):
    """Select entity for operating mode control."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the operating mode select."""
        super().__init__(coordinator)
        self._device_serial = device_serial
        self._device_role = device_role
        self._attr_unique_id = f"{device_serial}_operating_mode_select"
        self._attr_name = f"Ambientika {device_role.title()} Operating Mode"
        self._attr_icon = ICON_FORM_SELECT
        self._attr_options = OPERATION_MODES
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_serial)},
            "name": f"Ambientika {device_role.title()} {device_serial}",
            "manufacturer": "Südwind",
            "model": "Ambientika Smart",
            "serial_number": device_serial,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def current_option(self) -> str | None:
        """Return the current operating mode."""
        if self.coordinator.data is None:
            return None

        current_mode = self.coordinator.data.get("operatingMode")
        if current_mode in OPERATION_MODES:
            return current_mode
        return "Smart"  # Default

    async def async_select_option(self, option: str) -> None:
        """Change the operating mode."""
        if self.coordinator.data is None:
            return

        # Get current settings for other parameters
        current_fan = self.coordinator.data.get("fanSpeed", "Low")
        fan_speed = FAN_SPEEDS.get(current_fan, 1)

        current_humidity = self.coordinator.data.get("humidityLevel", "Dry")
        humidity_level = HUMIDITY_LEVELS.get(current_humidity, 1)

        current_light = self.coordinator.data.get("lightSensorLevel", "Off")
        if isinstance(current_light, str):
            light_sensor_level = LIGHT_SENSOR_LEVELS.get(current_light, 0)
        else:
            light_sensor_level = int(current_light) if current_light is not None else 0

        success = await self.coordinator.async_change_mode(
            option, fan_speed, humidity_level, light_sensor_level
        )

        if not success:
            _LOGGER.error(
                "Failed to change operating mode to %s for device %s",
                option,
                self._device_serial,
            )