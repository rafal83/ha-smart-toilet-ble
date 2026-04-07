"""Config flow for Smart Toilet BLE integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# MAC address pattern
MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Smart Toilet"): str,
    vol.Required("mac_address", default=""): str,
})


def validate_mac_address(mac: str) -> bool:
    """Validate MAC address format."""
    if not mac:
        return False
    return bool(MAC_PATTERN.match(mac.strip()))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Toilet BLE."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mac_address = user_input.get("mac_address", "").strip()
            
            # Validate MAC format
            if not validate_mac_address(mac_address):
                errors["mac_address"] = "invalid_mac"
            else:
                # Check if MAC is already configured
                for existing_entry in self._async_current_entries():
                    if existing_entry.data.get("mac_address") == mac_address:
                        return self.async_abort(reason="already_configured")
                
                # Success - create entry
                return self.async_create_entry(
                    title=user_input.get("name", "Smart Toilet"),
                    data={
                        "name": user_input.get("name", "Smart Toilet"),
                        "mac_address": mac_address.upper(),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Smart Toilet BLE."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Optional(
                "name",
                default=self.config_entry.data.get("name", "Smart Toilet")
            ): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
