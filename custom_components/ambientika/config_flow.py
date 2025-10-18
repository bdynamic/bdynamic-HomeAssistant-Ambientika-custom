"""Config flow for Ambientika Smart integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import AmbentikaAPI, AmbentikaAPIError, AmbentikaAuthError
from .const import (
    CONF_DEVICE_ROLE,
    CONF_DEVICE_SERIAL,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEVICE_ROLE_MASTER,
    DEVICE_ROLE_SLAVE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

STEP_DEVICE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_SERIAL): str,
        vol.Required(CONF_DEVICE_ROLE, default=DEVICE_ROLE_MASTER): vol.In(
            [DEVICE_ROLE_MASTER, DEVICE_ROLE_SLAVE]
        ),
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass."""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api = AmbentikaAPI(hass, data[CONF_USERNAME], data[CONF_PASSWORD])

    try:
        await api.authenticate()
    except AmbentikaAuthError as err:
        raise InvalidAuth from err
    except AmbentikaAPIError as err:
        raise CannotConnect from err

    # Return info that you want to store in the config entry.
    return {"title": f"Ambientika {data[CONF_DEVICE_SERIAL]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambientika Smart."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # Test authentication
                api = AmbentikaAPI(
                    self.hass, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                await api.authenticate()
                self._user_data = user_input
                return await self.async_step_device()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Combine user data and device data
            combined_data = {**self._user_data, **user_input}

            # Check if device already configured
            await self.async_set_unique_id(user_input[CONF_DEVICE_SERIAL])
            self._abort_if_unique_id_configured()

            try:
                # Test device access
                api = AmbentikaAPI(
                    self.hass, combined_data[CONF_USERNAME], combined_data[CONF_PASSWORD]
                )
                await api.get_device_status(user_input[CONF_DEVICE_SERIAL])

                return self.async_create_entry(
                    title=f"Ambientika {user_input[CONF_DEVICE_SERIAL]} ({user_input[CONF_DEVICE_ROLE]})",
                    data=combined_data,
                )
            except AmbentikaAPIError:
                errors["base"] = "device_not_found"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="device", data_schema=STEP_DEVICE_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""