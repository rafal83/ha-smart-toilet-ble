"""Config flow for Smart Toilet BLE integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from bleak import BleakScanner

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Smart Toilet"): str,
    vol.Required("mac_address"): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    mac_address = data["mac_address"]
    
    # Basic MAC address validation
    if not mac_address or len(mac_address) < 17:
        raise InvalidMACAddress("Invalid MAC address format")
    
    # Test connection
    try:
        devices = await BleakScanner.discover(timeout=5.0)
        found = any(d.address == mac_address or d.address.lower() == mac_address.lower() for d in devices)
        
        if not found:
            _LOGGER.warning("Device %s not found in scan, but continuing anyway", mac_address)
            
    except Exception as err:
        _LOGGER.warning("Could not scan for devices: %s", err)
        # Continue anyway - device might be asleep
    
    return {"title": data["name"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Toilet BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if MAC is already configured
            for existing_entry in self._async_current_entries():
                if existing_entry.data.get("mac_address") == user_input["mac_address"]:
                    return self.async_abort(reason="already_configured")
            
            # Validate input
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidMACAddress:
                errors["mac_address"] = "invalid_mac"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        "name": user_input["name"],
                        "mac_address": user_input["mac_address"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_scan(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle BLE device scanning step."""
        if user_input is not None:
            mac_address = user_input["mac_address"]
            name = self._discovered_devices.get(mac_address, "Smart Toilet")
            
            return self.async_create_entry(
                title=name,
                data={
                    "name": name,
                    "mac_address": mac_address,
                },
            )

        # Scan for BLE devices
        _LOGGER.info("Scanning for BLE devices...")
        try:
            devices = await BleakScanner.discover(timeout=10.0)
            
            # Filter and format devices
            self._discovered_devices = {}
            devices_dict = {}
            
            for device in devices:
                if device.name:
                    self._discovered_devices[device.address] = device.name
                    devices_dict[device.address] = f"{device.name} ({device.address})"
            
            if not devices_dict:
                return self.async_show_form(
                    step_id="scan",
                    errors={"base": "no_devices_found"},
                    description_placeholders={},
                )

            scan_schema = vol.Schema({
                vol.Required("mac_address"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=k, label=v)
                            for k, v in devices_dict.items()
                        ],
                        mode="dropdown",
                    )
                ),
            })

            return self.async_show_form(
                step_id="scan",
                data_schema=scan_schema,
            )
            
        except Exception as err:
            _LOGGER.error("Failed to scan for devices: %s", err)
            return self.async_show_form(
                step_id="scan",
                errors={"base": "scan_failed"},
                description_placeholders={"error": str(err)},
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


class InvalidMACAddress(Exception):
    """Error to indicate an invalid MAC address was given."""
