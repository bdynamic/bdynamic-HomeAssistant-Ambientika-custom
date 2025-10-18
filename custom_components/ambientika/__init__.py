"""The Ambientika Smart integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady

from .api import AmbentikaAPI, AmbentikaAPIError
from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEVICE_ROLE_MASTER,
    DOMAIN,
    PLATFORMS,
    SERVICE_CHANGE_MODE,
    SERVICE_RESET_FILTER,
)
from .coordinator import AmbentikaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambientika Smart from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    device_serial = entry.data[CONF_DEVICE_SERIAL]
    device_role = entry.data[CONF_DEVICE_ROLE]

    api = AmbentikaAPI(hass, username, password)

    # Test authentication
    try:
        await api.authenticate()
    except AmbentikaAPIError as err:
        _LOGGER.error("Failed to authenticate with Ambientika API: %s", err)
        raise ConfigEntryNotReady from err

    coordinator = AmbentikaDataUpdateCoordinator(
        hass, api, device_serial, device_role
    )

    # Fetch initial data so we have data when entities are added
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services only for master devices
    if device_role == DEVICE_ROLE_MASTER:
        await _async_register_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_register_services(
    hass: HomeAssistant, coordinator: AmbentikaDataUpdateCoordinator
) -> None:
    """Register services for the integration."""

    async def async_reset_filter(call: ServiceCall) -> None:
        """Handle reset filter service call."""
        await coordinator.async_reset_filter()

    async def async_change_mode(call: ServiceCall) -> None:
        """Handle change mode service call."""
        operating_mode = call.data.get("operating_mode", "Smart")
        fan_speed = call.data.get("fan_speed", 1)
        humidity_level = call.data.get("humidity_level", 1)
        light_sensor_level = call.data.get("light_sensor_level", 0)

        await coordinator.async_change_mode(
            operating_mode, fan_speed, humidity_level, light_sensor_level
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_FILTER,
        async_reset_filter,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CHANGE_MODE,
        async_change_mode,
    )