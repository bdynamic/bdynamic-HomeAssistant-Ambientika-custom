"""API client for Ambientika Smart devices."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_AUTH_ENDPOINT,
    API_CHANGE_MODE_ENDPOINT,
    API_DEVICE_STATUS_ENDPOINT,
    API_RESET_FILTER_ENDPOINT,
    API_TOKEN_INFO_ENDPOINT,
    TOKEN_REFRESH_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)


class AmbentikaAPIError(Exception):
    """Exception raised for API errors."""


class AmbentikaAuthError(AmbentikaAPIError):
    """Exception raised for authentication errors."""


class AmbentikaAPI:
    """API client for Ambientika Smart devices."""

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.username = username
        self.password = password
        self.session = async_get_clientsession(hass)
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

    async def authenticate(self) -> None:
        """Authenticate with the Ambientika API."""
        _LOGGER.debug("Authenticating with Ambientika API")

        payload = {
            "username": self.username,
            "password": self.password,
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.post(
                API_AUTH_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    raise AmbentikaAuthError(f"Authentication failed: {response.status}")

                data = await response.json()
                self._access_token = data.get("jwtToken")

                if not self._access_token:
                    raise AmbentikaAuthError("No access token received")

                # Get token expiry information
                await self._get_token_info()

                _LOGGER.debug("Authentication successful")

        except asyncio.TimeoutError as err:
            raise AmbentikaAPIError("Timeout during authentication") from err
        except aiohttp.ClientError as err:
            raise AmbentikaAPIError(f"Connection error during authentication: {err}") from err

    async def _get_token_info(self) -> None:
        """Get token expiry information."""
        if not self._access_token:
            return

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        try:
            async with self.session.get(
                API_TOKEN_INFO_ENDPOINT,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    valid_to = data.get("validTo")
                    if valid_to:
                        self._token_expires_at = datetime.fromtimestamp(valid_to)

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.debug("Could not get token info: %s", err)

    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self._access_token:
            await self.authenticate()
            return

        # Check if token needs refresh
        if self._token_expires_at:
            threshold = datetime.now() + timedelta(days=TOKEN_REFRESH_THRESHOLD)
            if self._token_expires_at <= threshold:
                _LOGGER.debug("Token expires soon, refreshing")
                await self.authenticate()

    async def get_device_status(self, device_serial: str) -> dict[str, Any]:
        """Get device status."""
        await self._ensure_authenticated()

        url = f"{API_DEVICE_STATUS_ENDPOINT}?deviceSerialNumber={device_serial}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        try:
            async with self.session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 401:
                    # Token expired, re-authenticate and retry
                    await self.authenticate()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    async with self.session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as retry_response:
                        if retry_response.status != 200:
                            raise AmbentikaAPIError(f"Device status request failed: {retry_response.status}")
                        return await retry_response.json()

                if response.status != 200:
                    raise AmbentikaAPIError(f"Device status request failed: {response.status}")

                return await response.json()

        except asyncio.TimeoutError as err:
            raise AmbentikaAPIError("Timeout getting device status") from err
        except aiohttp.ClientError as err:
            raise AmbentikaAPIError(f"Connection error getting device status: {err}") from err

    async def change_mode(
        self,
        device_serial: str,
        operating_mode: str,
        fan_speed: int,
        humidity_level: int,
        light_sensor_level: int,
    ) -> bool:
        """Change device operating mode."""
        await self._ensure_authenticated()

        payload = {
            "deviceSerialNumber": device_serial,
            "operatingMode": operating_mode,
            "fanSpeed": fan_speed,
            "humidityLevel": humidity_level,
            "lightSensorLevel": light_sensor_level,
        }

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.post(
                API_CHANGE_MODE_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 401:
                    # Token expired, re-authenticate and retry
                    await self.authenticate()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    async with self.session.post(
                        API_CHANGE_MODE_ENDPOINT,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as retry_response:
                        return retry_response.status == 200

                return response.status == 200

        except asyncio.TimeoutError as err:
            raise AmbentikaAPIError("Timeout changing device mode") from err
        except aiohttp.ClientError as err:
            raise AmbentikaAPIError(f"Connection error changing device mode: {err}") from err

    async def reset_filter(self, device_serial: str) -> bool:
        """Reset device filter."""
        await self._ensure_authenticated()

        url = f"{API_RESET_FILTER_ENDPOINT}?deviceSerialNumber={device_serial}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        try:
            async with self.session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 401:
                    # Token expired, re-authenticate and retry
                    await self.authenticate()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    async with self.session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as retry_response:
                        return retry_response.status == 200

                return response.status == 200

        except asyncio.TimeoutError as err:
            raise AmbentikaAPIError("Timeout resetting filter") from err
        except aiohttp.ClientError as err:
            raise AmbentikaAPIError(f"Connection error resetting filter: {err}") from err