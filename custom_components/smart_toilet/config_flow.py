"""Config flow for Smart Toilet BLE integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# MAC address pattern
MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


def validate_mac_address(mac: str) -> bool:
    """Validate MAC address format."""
    if not mac:
        return False
    return bool(MAC_PATTERN.match(mac.strip()))


def format_ble_device_name(device) -> str:
    """Format a BLE device for display in the selector."""
    name = device.name if device.name else "Unknown Device"
    address = device.address
    rssi = f" (RSSI: {device.rssi})" if hasattr(device, 'rssi') and device.rssi else ""
    return f"{name} - {address}{rssi}"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Toilet BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}

    def _get_discovered_devices(self) -> dict[str, str]:
        """Get discovered BLE devices from Home Assistant."""
        self._discovered_devices = {}
        
        try:
            # Get all discovered BLE devices from HA's bluetooth integration
            devices = async_discovered_service_info(self.hass, connectable=True)
            
            for device in devices:
                address = device.address
                name = device.name if device.name else "Unknown Device"
                
                # Only show devices with a name (filter out random MACs)
                if name != "Unknown Device" or address not in self._discovered_devices:
                    rssi = f" (RSSI: {device.rssi})" if device.rssi else ""
                    self._discovered_devices[address] = f"{name} - {address}{rssi}"
            
            _LOGGER.debug("Discovered %d BLE devices", len(self._discovered_devices))
            
        except Exception as err:
            _LOGGER.warning("Could not get discovered devices: %s", err)
        
        return self._discovered_devices

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - show scan results or manual entry."""
        errors: dict[str, str] = {}
        
        # Get discovered devices
        discovered = self._get_discovered_devices()
        
        # Build schema with discovered devices
        if discovered:
            # Create selector with discovered devices + manual entry option
            device_options = [
                selector.SelectOptionDict(value=addr, label=name)
                for addr, name in discovered.items()
            ]
            
            # Add manual entry option
            device_options.insert(0, selector.SelectOptionDict(
                value="manual",
                label="✏️ Enter MAC address manually"
            ))
            
            data_schema = vol.Schema({
                vol.Required("device_selection", default="manual"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=device_options,
                        mode="dropdown",
                    )
                ),
            })
        else:
            # No devices found, go straight to manual entry
            data_schema = vol.Schema({
                vol.Required("mac_address", default=""): str,
            })
        
        if user_input is not None:
            device_selection = user_input.get("device_selection", "manual")
            
            if device_selection == "manual":
                # Show manual MAC entry form
                return await self.async_step_manual(user_input)
            else:
                # Use selected device from scan
                mac_address = device_selection.strip()
                
                # Validate MAC format
                if not validate_mac_address(mac_address):
                    errors["device_selection"] = "invalid_mac"
                else:
                    # Check if MAC is already configured
                    for existing_entry in self._async_current_entries():
                        if existing_entry.data.get("mac_address") == mac_address:
                            return self.async_abort(reason="already_configured")
                    
                    # Success - create entry
                    device_name = discovered.get(mac_address, "Smart Toilet")
                    return self.async_create_entry(
                        title=device_name.split(" - ")[0],  # Use just the name part
                        data={
                            "name": device_name.split(" - ")[0],
                            "mac_address": mac_address.upper(),
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_count": str(len(discovered)),
            },
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual MAC address entry."""
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
        
        data_schema = vol.Schema({
            vol.Required("name", default="Smart Toilet"): str,
            vol.Required("mac_address", default=""): str,
        })
        
        return self.async_show_form(
            step_id="manual",
            data_schema=data_schema,
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
