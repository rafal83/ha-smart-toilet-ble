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

from .const import (
    DOMAIN, 
    TOILET_MODELS, 
    DEFAULT_MODEL,
    get_model,
)

_LOGGER = logging.getLogger(__name__)

# MAC address pattern
MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


def validate_mac_address(mac: str) -> bool:
    """Validate MAC address format."""
    if not mac:
        return False
    return bool(MAC_PATTERN.match(mac.strip()))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Toilet BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}
        self._selected_model: str = DEFAULT_MODEL

    def _get_discovered_devices(self) -> dict[str, str]:
        """Get discovered BLE devices from Home Assistant."""
        self._discovered_devices = {}
        
        try:
            devices = async_discovered_service_info(self.hass, connectable=True)
            
            for device in devices:
                address = device.address
                name = device.name if device.name else "Unknown Device"
                
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
        """Handle the initial step - select model."""
        errors: dict[str, str] = {}
        
        # Build model selector
        model_options = [
            selector.SelectOptionDict(value=model_id, label=f"{model.name} ({model.manufacturer})")
            for model_id, model in TOILET_MODELS.items()
        ]
        model_options.insert(0, selector.SelectOptionDict(
            value="auto_detect",
            label="🔍 Auto-detect (recommended)"
        ))
        
        data_schema = vol.Schema({
            vol.Required("model", default=DEFAULT_MODEL): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=model_options,
                    mode="dropdown",
                )
            ),
        })
        
        if user_input is not None:
            model = user_input.get("model", DEFAULT_MODEL)
            
            if model == "auto_detect":
                # Try to auto-detect
                discovered = self._get_discovered_devices()
                if discovered:
                    # For now, default to generic - auto-detection can be enhanced later
                    self._selected_model = DEFAULT_MODEL
                else:
                    self._selected_model = DEFAULT_MODEL
            else:
                self._selected_model = model
            
            # Proceed to device selection
            return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "model_count": str(len(TOILET_MODELS)),
            },
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection - scan or manual MAC entry."""
        errors: dict[str, str] = {}
        
        discovered = self._get_discovered_devices()
        
        if discovered:
            device_options = [
                selector.SelectOptionDict(value=addr, label=name)
                for addr, name in discovered.items()
            ]
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
            data_schema = vol.Schema({
                vol.Required("mac_address", default=""): str,
            })
        
        if user_input is not None:
            device_selection = user_input.get("device_selection", "manual")
            
            if device_selection == "manual":
                return await self.async_step_manual()
            else:
                mac_address = device_selection.strip()
                
                if not validate_mac_address(mac_address):
                    errors["device_selection"] = "invalid_mac"
                else:
                    for existing_entry in self._async_current_entries():
                        if existing_entry.data.get("mac_address") == mac_address:
                            return self.async_abort(reason="already_configured")
                    
                    model = get_model(self._selected_model)
                    return self.async_create_entry(
                        title=f"{model.name} ({mac_address[-5:]})",
                        data={
                            "name": model.name,
                            "mac_address": mac_address.upper(),
                            "model": self._selected_model,
                        },
                    )

        return self.async_show_form(
            step_id="device",
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
            
            if not validate_mac_address(mac_address):
                errors["mac_address"] = "invalid_mac"
            else:
                for existing_entry in self._async_current_entries():
                    if existing_entry.data.get("mac_address") == mac_address:
                        return self.async_abort(reason="already_configured")
                
                model = get_model(self._selected_model)
                return self.async_create_entry(
                    title=f"{model.name} ({mac_address[-5:]})",
                    data={
                        "name": user_input.get("name", model.name),
                        "mac_address": mac_address.upper(),
                        "model": self._selected_model,
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

        # Build model selector for options
        model_options = [
            selector.SelectOptionDict(value=model_id, label=f"{model.name} ({model.manufacturer})")
            for model_id, model in TOILET_MODELS.items()
        ]

        schema = vol.Schema({
            vol.Optional(
                "name",
                default=self.config_entry.data.get("name", "Smart Toilet")
            ): str,
            vol.Optional(
                "model",
                default=self.config_entry.data.get("model", DEFAULT_MODEL)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=model_options,
                    mode="dropdown",
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
