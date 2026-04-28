"""Support for Smart Toilet BLE buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, get_model_button_definitions
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE buttons."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]

    button_defs = get_model_button_definitions(coordinator.model_id)
    buttons = []
    for btn_def in button_defs:
        # Tuple (id, name, command_key) ou (id, name, command_key, is_config)
        btn_id, name, cmd_key = btn_def[0], btn_def[1], btn_def[2]
        is_config = btn_def[3] if len(btn_def) > 3 else False
        if cmd_key in coordinator.commands:
            buttons.append(SmartToiletButton(
                coordinator, entry.entry_id, btn_id, name, cmd_key, is_config
            ))

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
        is_config: bool = False,
    ) -> None:
        """Initialize the button from definition."""
        super().__init__(coordinator, entry_id)

        self._button_id = button_id
        self._command = coordinator.commands.get(command_key)

        self._attr_translation_key = button_id
        self._attr_unique_id = f"{entry_id}_button_{button_id}"
        self._attr_icon = ICONS.get(button_id, "mdi:gesture-tap")
        if is_config:
            self._attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Press the button."""
        if self._command:
            await self.coordinator.send_toilet_command(
                self._command.function, self._command.param
            )
