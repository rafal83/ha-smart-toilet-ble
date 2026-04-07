"""Support for Smart Toilet BLE buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS
from .entity import SmartToiletEntity

# Button definitions: (unique_id_suffix, name, function_code)
BUTTONS = [
    ("flush", "Flush", 0x30),
    ("stop", "Stop All", 0x05),
    ("self_clean", "Self Clean", 0x07),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE buttons."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    buttons = []
    for button_id, name, function in BUTTONS:
        buttons.append(
            SmartToiletButton(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                button_id=button_id,
                name=name,
                function=function,
            )
        )
    
    async_add_entities(buttons)


class SmartToiletButton(SmartToiletEntity, ButtonEntity):
    """Representation of a Smart Toilet BLE button."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        button_id: str,
        name: str,
        function: int,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id)
        
        self._button_id = button_id
        self._function = function
        self._attr_name = f"{coordinator.mac_address.split(':')[-1]} - {name}"
        self._attr_unique_id = f"{entry_id}_button_{button_id}"
        self._attr_icon = ICONS.get(button_id, "mdi:gesture-tap")

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.send_toilet_command(self._function, 0x01)
