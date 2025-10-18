"""Binary sensor platform for Ambientika Smart integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    DOMAIN,
    ICON_WATER_PERCENT_ALERT,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambientika binary sensor based on a config entry."""
    coordinator: AmbentikaDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    device_serial = config_entry.data[CONF_DEVICE_SERIAL]
    device_role = config_entry.data[CONF_DEVICE_ROLE]

    entities: list[BinarySensorEntity] = [
        AmbentikaHumidityAlarmSensor(coordinator, device_serial, device_role),
        AmbentikaNightAlarmSensor(coordinator, device_serial, device_role),
    ]

    async_add_entities(entities)


class AmbentikaBinarySensorBase(
    CoordinatorEntity[AmbentikaDataUpdateCoordinator], BinarySensorEntity
):
    """Base class for Ambentika binary sensors."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
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


class AmbentikaHumidityAlarmSensor(AmbentikaBinarySensorBase):
    """Humidity alarm binary sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the humidity alarm sensor."""
        super().__init__(coordinator, device_serial, device_role, "humidity_alarm")
        self._attr_name = f"Ambentika {device_role.title()} Humidity Alarm"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = ICON_WATER_PERCENT_ALERT

    @property
    def is_on(self) -> bool | None:
        """Return true if the humidity alarm is on."""
        if self.coordinator.data is None:
            return None
        alarm = self.coordinator.data.get("humidityAlarm")
        if alarm is None:
            return None
        # Convert string boolean to actual boolean
        if isinstance(alarm, str):
            return alarm.lower() == "true"
        return bool(alarm)


class AmbentikaNightAlarmSensor(AmbentikaBinarySensorBase):
    """Night alarm binary sensor for Ambentika device."""

    def __init__(
        self,
        coordinator: AmbentikaDataUpdateCoordinator,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the night alarm sensor."""
        super().__init__(coordinator, device_serial, device_role, "night_alarm")
        self._attr_name = f"Ambentika {device_role.title()} Night Alarm"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = ICON_WATER_PERCENT_ALERT

    @property
    def is_on(self) -> bool | None:
        """Return true if the night alarm is on."""
        if self.coordinator.data is None:
            return None
        alarm = self.coordinator.data.get("nightAlarm")
        if alarm is None:
            return None
        # Convert string boolean to actual boolean
        if isinstance(alarm, str):
            return alarm.lower() == "true"
        return bool(alarm)