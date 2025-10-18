"""Data update coordinator for Ambientika Smart devices."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AmbentikaAPI, AmbentikaAPIError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AmbentikaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the Ambientika API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: AmbentikaAPI,
        device_serial: str,
        device_role: str,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.device_serial = device_serial
        self.device_role = device_role

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_serial}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.api.get_device_status(self.device_serial)
        except AmbentikaAPIError as error:
            raise UpdateFailed(f"Error communicating with API: {error}") from error

    async def async_change_mode(
        self,
        operating_mode: str,
        fan_speed: int,
        humidity_level: int,
        light_sensor_level: int,
    ) -> bool:
        """Change device operating mode."""
        try:
            success = await self.api.change_mode(
                self.device_serial,
                operating_mode,
                fan_speed,
                humidity_level,
                light_sensor_level,
            )
            if success:
                # Trigger immediate update
                await self.async_request_refresh()
            return success
        except AmbentikaAPIError as error:
            _LOGGER.error("Error changing mode: %s", error)
            return False

    async def async_reset_filter(self) -> bool:
        """Reset device filter."""
        try:
            success = await self.api.reset_filter(self.device_serial)
            if success:
                # Trigger immediate update
                await self.async_request_refresh()
            return success
        except AmbentikaAPIError as error:
            _LOGGER.error("Error resetting filter: %s", error)
            return False