"""Sensor platform for Ambientika Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    DEVICE_ROLE_MASTER,
    DOMAIN,
    FAN_SPEEDS,
    FILTER_STATUS_BAD,
    FILTER_STATUS_GOOD,
    FILTER_STATUS_MEDIUM,
    HUMIDITY_LEVELS,
    ICON_AIR_FILTER,
    ICON_FAN_ALERT,
    ICON_FAN_SPEED_1,
    ICON_FAN_SPEED_2,
    ICON_FAN_SPEED_3,
    ICON_HELP_BOX,
    ICON_LEAF_CIRCLE_OUTLINE,
    ICON_LINK_BOX_VARIANT,
    ICON_MOLECULE_CO2,
    ICON_STAR_BOX,
    ICON_THEME_LIGHT_DARK,
    ICON_THERMOMETER,
    ICON_WATER,
    ICON_WATER_PERCENT,
    ICON_WIFI,
    LIGHT_SENSOR_LEVELS,
    UNIT_LQI,
    UNIT_PERCENT,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambientika sensor based on a config entry."""
    coordinator: AmbentikaDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    device_serial = config_entry.data[CONF_DEVICE_SERIAL]
    device_role = config_entry.data[CONF_DEVICE_ROLE]

    entities: list[SensorEntity] = [
        AmbentikaTemperatureSensor(coordinator, device_serial, device_role),
        AmbentikaHumiditySensor(coordinator, device_serial, device_role),
        AmbentikaFilterStatusSensor(coordinator, device_serial, device_role),
        AmbentikaAirQualitySensor(coordinator, device_serial, device_role),
        AmbentikaDeviceRoleSensor(coordinator, device_serial, device_role),
        AmbentikaSignalStrengthSensor(coordinator, device_serial, device_role),
    ]

    # Add master-only sensors
    if device_role == DEVICE_ROLE_MASTER:
        entities.extend([
            AmbentikaOperatingModeSensor(coordinator, device_serial, device_role),
            AmbentikaFanSpeedSensor(coordinator, device_serial, device_role),
            AmbentikaHumidityLevelSensor(coordinator, device_serial, device_role),
            AmbentikaLightSensorSensor(coordinator, device_serial, device_role),
        ])

    async_add_entities(entities)


class AmbentikaSensorBase(CoordinatorEntity[AmbentikaDataUpdateCoordinator], SensorEntity):
    """Base class for Ambentika sensors."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_serial = device_serial
        self._device_role = device_role
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{device_serial}_{sensor_type}"
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


class AmbentikaTemperatureSensor(AmbentikaSensorBase):
    """Temperature sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, device_serial, device_role, "temperature")
        self._attr_name = f"Ambientika {device_role.title()} Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = ICON_THERMOMETER

    @property
    def native_value(self) -> float | None:
        """Return the temperature value."""
        if self.coordinator.data is None:
            return None
        temp = self.coordinator.data.get("temperature")
        if temp is None:
            return None
        try:
            return float(temp)
        except (ValueError, TypeError):
            return None


class AmbentikaHumiditySensor(AmbentikaSensorBase):
    """Humidity sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the humidity sensor."""
        super().__init__(coordinator, device_serial, device_role, "humidity")
        self._attr_name = f"Ambientika {device_role.title()} Humidity"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UNIT_PERCENT
        self._attr_icon = ICON_WATER_PERCENT

    @property
    def native_value(self) -> float | None:
        """Return the humidity value."""
        if self.coordinator.data is None:
            return None
        humidity = self.coordinator.data.get("humidity")
        if humidity is None:
            return None
        try:
            return float(humidity)
        except (ValueError, TypeError):
            return None


class AmbentikaFilterStatusSensor(AmbentikaSensorBase):
    """Filter status sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the filter status sensor."""
        super().__init__(coordinator, device_serial, device_role, "filter_status")
        self._attr_name = f"Ambientika {device_role.title()} Filter Status"
        self._attr_icon = ICON_AIR_FILTER

    @property
    def native_value(self) -> str | None:
        """Return the filter status."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("filtersStatus")


class AmbentikaOperatingModeSensor(AmbentikaSensorBase):
    """Operating mode sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the operating mode sensor."""
        super().__init__(coordinator, device_serial, device_role, "operating_mode")
        self._attr_name = f"Ambientika {device_role.title()} Operating Mode"
        self._attr_icon = ICON_LEAF_CIRCLE_OUTLINE

    @property
    def native_value(self) -> str | None:
        """Return the operating mode."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("operatingMode")


class AmbentikaFanSpeedSensor(AmbentikaSensorBase):
    """Fan speed sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the fan speed sensor."""
        super().__init__(coordinator, device_serial, device_role, "fan_speed")
        self._attr_name = f"Ambientika {device_role.title()} Fan Speed"

    @property
    def native_value(self) -> str | None:
        """Return the fan speed."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("fanSpeed")

    @property
    def icon(self) -> str:
        """Return the icon based on fan speed."""
        fan_speed = self.native_value
        if fan_speed == "Low":
            return ICON_FAN_SPEED_1
        elif fan_speed == "Medium":
            return ICON_FAN_SPEED_2
        elif fan_speed == "High":
            return ICON_FAN_SPEED_3
        return ICON_FAN_ALERT


class AmbentikaHumidityLevelSensor(AmbentikaSensorBase):
    """Humidity level sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the humidity level sensor."""
        super().__init__(coordinator, device_serial, device_role, "humidity_level")
        self._attr_name = f"Ambientika {device_role.title()} Humidity Level"
        self._attr_icon = ICON_WATER

    @property
    def native_value(self) -> str | None:
        """Return the humidity level."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("humidityLevel")


class AmbentikaAirQualitySensor(AmbentikaSensorBase):
    """Air quality sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the air quality sensor."""
        super().__init__(coordinator, device_serial, device_role, "air_quality")
        self._attr_name = f"Ambientika {device_role.title()} Air Quality"
        self._attr_icon = ICON_MOLECULE_CO2

    @property
    def native_value(self) -> str | None:
        """Return the air quality."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("airQuality")


class AmbentikaDeviceRoleSensor(AmbentikaSensorBase):
    """Device role sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the device role sensor."""
        super().__init__(coordinator, device_serial, device_role, "device_role")
        self._attr_name = f"Ambentika {device_role.title()} Device Role"

    @property
    def native_value(self) -> str | None:
        """Return the device role."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("deviceRole")

    @property
    def icon(self) -> str:
        """Return the icon based on device role."""
        device_role = self.native_value
        if device_role == "Master":
            return ICON_STAR_BOX
        elif device_role in ["SlaveEqualMaster", "SlaveOppositeMaster"]:
            return ICON_LINK_BOX_VARIANT
        return ICON_HELP_BOX


class AmbentikaLightSensorSensor(AmbentikaSensorBase):
    """Light sensor sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the light sensor sensor."""
        super().__init__(coordinator, device_serial, device_role, "light_sensor")
        self._attr_name = f"Ambentika {device_role.title()} Light Sensor"
        self._attr_icon = ICON_THEME_LIGHT_DARK

    @property
    def native_value(self) -> str | None:
        """Return the light sensor level."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("lightSensorLevel")


class AmbentikaSignalStrengthSensor(AmbentikaSensorBase):
    """Signal strength sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the signal strength sensor."""
        super().__init__(coordinator, device_serial, device_role, "signal_strength")
        self._attr_name = f"Ambentika {device_role.title()} Signal Strength"
        self._attr_native_unit_of_measurement = UNIT_LQI
        self._attr_icon = ICON_WIFI

    @property
    def native_value(self) -> str | None:
        """Return the signal strength."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("signalStrenght")