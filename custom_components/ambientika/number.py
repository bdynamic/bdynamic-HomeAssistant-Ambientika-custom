"""Number platform for Ambientika Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
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
    ICON_FAN,
    ICON_THEME_LIGHT_DARK,
    ICON_WATER,
    LIGHT_SENSOR_LEVELS,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambientika number based on a config entry."""
    coordinator: AmbentikaDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    device_serial = config_entry.data[CONF_DEVICE_SERIAL]
    device_role = config_entry.data[CONF_DEVICE_ROLE]

    # Only add number entities for master devices
    if device_role == DEVICE_ROLE_MASTER:
        entities: list[NumberEntity] = [
            AmbentikaFanSpeedNumber(coordinator, device_serial, device_role),
            AmbentikaHumidityLevelNumber(coordinator, device_serial, device_role),
            AmbentikaLightLevelNumber(coordinator, device_serial, device_role),
        ]
        async_add_entities(entities)


class AmbentikaNumberBase(CoordinatorEntity[AmbentikaDataUpdateCoordinator], NumberEntity):
    """Base class for Ambentika number entities."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
        entity_type: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device_serial = device_serial
        self._device_role = device_role
        self._entity_type = entity_type
        self._attr_unique_id = f"{device_serial}_{entity_type}_number"
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


class AmbentikaFanSpeedNumber(AmbentikaNumberBase):
    """Number entity for fan speed control."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the fan speed number."""
        super().__init__(coordinator, device_serial, device_role, "fan_speed")
        self._attr_name = f"Ambientika {device_role.title()} Fan Speed"
        self._attr_icon = ICON_FAN
        self._attr_native_min_value = 1
        self._attr_native_max_value = 3
        self._attr_native_step = 1

    @property
    def native_value(self) -> float | None:
        """Return the current fan speed value."""
        if self.coordinator.data is None:
            return None

        fan_speed = self.coordinator.data.get("fanSpeed")
        if fan_speed in FAN_SPEEDS:
            return float(FAN_SPEEDS[fan_speed])
        return 1.0  # Default to Low

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan speed."""
        if self.coordinator.data is None:
            return

        # Get current settings
        operating_mode = self.coordinator.data.get("operatingMode", "Smart")

        # Get current humidity level
        current_humidity = self.coordinator.data.get("humidityLevel", "Dry")
        humidity_level = HUMIDITY_LEVELS.get(current_humidity, 1)

        # Get current light sensor level
        current_light = self.coordinator.data.get("lightSensorLevel", "Off")
        light_sensor_level = LIGHT_SENSOR_LEVELS.get(current_light, 0)

        success = await self.coordinator.async_change_mode(
            operating_mode, int(value), humidity_level, light_sensor_level
        )

        if not success:
            _LOGGER.error("Failed to set fan speed for device %s", self._device_serial)


class AmbentikaHumidityLevelNumber(AmbentikaNumberBase):
    """Number entity for humidity level control."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the humidity level number."""
        super().__init__(coordinator, device_serial, device_role, "humidity_level")
        self._attr_name = f"Ambientika {device_role.title()} Humidity Level"
        self._attr_icon = ICON_WATER
        self._attr_native_min_value = 1
        self._attr_native_max_value = 3
        self._attr_native_step = 1

    @property
    def native_value(self) -> float | None:
        """Return the current humidity level value."""
        if self.coordinator.data is None:
            return None

        humidity_level = self.coordinator.data.get("humidityLevel")
        if humidity_level in HUMIDITY_LEVELS:
            return float(HUMIDITY_LEVELS[humidity_level])
        return 1.0  # Default to Dry

    async def async_set_native_value(self, value: float) -> None:
        """Set the humidity level."""
        if self.coordinator.data is None:
            return

        # Get current settings
        operating_mode = self.coordinator.data.get("operatingMode", "Smart")

        # Get current fan speed
        current_fan = self.coordinator.data.get("fanSpeed", "Low")
        fan_speed = FAN_SPEEDS.get(current_fan, 1)

        # Get current light sensor level
        current_light = self.coordinator.data.get("lightSensorLevel", "Off")
        light_sensor_level = LIGHT_SENSOR_LEVELS.get(current_light, 0)

        success = await self.coordinator.async_change_mode(
            operating_mode, fan_speed, int(value), light_sensor_level
        )

        if not success:
            _LOGGER.error("Failed to set humidity level for device %s", self._device_serial)


class AmbentikaLightLevelNumber(AmbentikaNumberBase):
    """Number entity for light level control."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the light level number."""
        super().__init__(coordinator, device_serial, device_role, "light_level")
        self._attr_name = f"Ambientika {device_role.title()} Light Level"
        self._attr_icon = ICON_THEME_LIGHT_DARK
        self._attr_native_min_value = 0
        self._attr_native_max_value = 2
        self._attr_native_step = 1

    @property
    def native_value(self) -> float | None:
        """Return the current light level value."""
        if self.coordinator.data is None:
            return None

        light_level = self.coordinator.data.get("lightSensorLevel")
        # Handle both string and numeric values
        if isinstance(light_level, str):
            if light_level in LIGHT_SENSOR_LEVELS:
                return float(LIGHT_SENSOR_LEVELS[light_level])
        elif isinstance(light_level, (int, float)):
            return float(light_level)

        return 0.0  # Default to Off

    async def async_set_native_value(self, value: float) -> None:
        """Set the light level."""
        if self.coordinator.data is None:
            return

        # Get current settings
        operating_mode = self.coordinator.data.get("operatingMode", "Smart")

        # Get current fan speed
        current_fan = self.coordinator.data.get("fanSpeed", "Low")
        fan_speed = FAN_SPEEDS.get(current_fan, 1)

        # Get current humidity level
        current_humidity = self.coordinator.data.get("humidityLevel", "Dry")
        humidity_level = HUMIDITY_LEVELS.get(current_humidity, 1)

        success = await self.coordinator.async_change_mode(
            operating_mode, fan_speed, humidity_level, int(value)
        )

        if not success:
            _LOGGER.error("Failed to set light level for device %s", self._device_serial)