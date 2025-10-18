"""Switch platform for Ambientika Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    DEVICE_ROLE_MASTER,
    DOMAIN,
    ICON_HVAC,
    ICON_HVAC_OFF,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambientika switch based on a config entry."""
    coordinator: AmbentikaDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    device_serial = config_entry.data[CONF_DEVICE_SERIAL]
    device_role = config_entry.data[CONF_DEVICE_ROLE]

    # Only add switch for master devices
    if device_role == DEVICE_ROLE_MASTER:
        entities: list[SwitchEntity] = [
            AmbentikaMasterSwitch(coordinator, device_serial, device_role)
        ]
        async_add_entities(entities)


class AmbentikaMasterSwitch(CoordinatorEntity[AmbentikaDataUpdateCoordinator], SwitchEntity):
    """Switch for turning Ambentika master device on/off."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_serial = device_serial
        self._device_role = device_role
        self._attr_unique_id = f"{device_serial}_switch"
        self._attr_name = f"Ambientika {device_role.title()}"
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
    def is_on(self) -> bool:
        """Return true if the device is on."""
        if self.coordinator.data is None:
            return False
        operating_mode = self.coordinator.data.get("operatingMode")
        return operating_mode != "Off"

    @property
    def icon(self) -> str:
        """Return the icon based on device state."""
        return ICON_HVAC if self.is_on else ICON_HVAC_OFF

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        # Get current settings from coordinator data
        if self.coordinator.data is None:
            _LOGGER.error("No data available to turn on device")
            return

        # Use Smart mode as default when turning on
        operating_mode = "Smart"
        fan_speed = 1  # Low
        humidity_level = 1  # Dry
        light_sensor_level = 0  # Off

        # Try to use last known settings if available
        last_mode = self.coordinator.data.get("lastOperatingMode")
        if last_mode and last_mode != "Off":
            operating_mode = last_mode

        # Get current fan speed setting
        current_fan = self.coordinator.data.get("fanSpeed")
        if current_fan == "Low":
            fan_speed = 1
        elif current_fan == "Medium":
            fan_speed = 2
        elif current_fan == "High":
            fan_speed = 3

        # Get current humidity level
        current_humidity = self.coordinator.data.get("humidityLevel")
        if current_humidity == "Dry":
            humidity_level = 1
        elif current_humidity == "Normal":
            humidity_level = 2
        elif current_humidity == "Moist":
            humidity_level = 3

        # Get current light sensor level
        current_light = self.coordinator.data.get("lightSensorLevel")
        if current_light == "Low":
            light_sensor_level = 1
        elif current_light == "Medium":
            light_sensor_level = 2

        success = await self.coordinator.async_change_mode(
            operating_mode, fan_speed, humidity_level, light_sensor_level
        )

        if not success:
            _LOGGER.error("Failed to turn on device %s", self._device_serial)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        success = await self.coordinator.async_change_mode(
            "Off", 0, 0, 0  # Values don't matter when turning off
        )

        if not success:
            _LOGGER.error("Failed to turn off device %s", self._device_serial)