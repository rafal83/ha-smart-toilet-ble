"""Support for Smart Toilet BLE buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, BUTTON_DEFINITIONS
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE buttons."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Filter buttons based on model features
    model_features = coordinator.model.features
    buttons = [
        SmartToiletButton(coordinator, entry.entry_id, btn_id, name, cmd_key)
        for btn_id, name, cmd_key in BUTTON_DEFINITIONS
        if cmd_key in coordinator.commands  # Only add if command exists for model
    ]
    
    async_add_entities(buttons)


class SmartToiletButton(SmartToiletEntity, ButtonEntity):
    """Representation of a Smart Toilet BLE button."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        button_id: str,
        name: str,
        command_key: str,
    ) -> None:
        """Initialize the button from definition."""
        super().__init__(coordinator, entry_id)
        
        self._button_id = button_id
        self._command = coordinator.commands.get(command_key)
        
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_button_{button_id}"
        self._attr_icon = ICONS.get(button_id, "mdi:gesture-tap")

    async def async_press(self) -> None:
        """Press the button."""
        if self._command:
            await self.coordinator.send_toilet_command(
                self._command.function, self._command.param
            )
