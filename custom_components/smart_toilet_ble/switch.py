"""Support for Smart Toilet BLE switches."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, get_model_switch_definitions
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE switches."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Use model-specific switch definitions
    switch_defs = get_model_switch_definitions(coordinator.model_id)
    switches = [
        SmartToiletSwitch(coordinator, entry.entry_id, switch_def)
        for switch_def in switch_defs
        if switch_def.on_command in coordinator.commands  # Only add if command exists
    ]
    
    async_add_entities(switches)


class SmartToiletSwitch(SmartToiletEntity, SwitchEntity):
    """Representation of a Smart Toilet BLE switch."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        switch_def: Any,
    ) -> None:
        """Initialize the switch from definition."""
        super().__init__(coordinator, entry_id)
        
        self._switch_def = switch_def
        
        # Get model-specific commands
        commands = coordinator.commands
        self._on_cmd = commands.get(switch_def.on_command)
        self._off_cmd = commands.get(switch_def.off_command) if switch_def.off_command else None
        
        self._attr_translation_key = switch_def.id
        self._attr_unique_id = f"{entry_id}_switch_{switch_def.id}"
        self._attr_icon = ICONS.get(switch_def.id, "mdi:power")
        # Le firmware ne renvoie aucun état → toujours optimiste.
        self._attr_assumed_state = True
        self._attr_should_poll = False
        if getattr(switch_def, "is_config", False):
            self._attr_entity_category = EntityCategory.CONFIG

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self._on_cmd:
            success = await self.coordinator.send_toilet_command(
                self._on_cmd.function, self._on_cmd.param
            )
            if success and self._switch_def.has_state:
                self._attr_is_on = True
                self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self._off_cmd:
            success = await self.coordinator.send_toilet_command(
                self._off_cmd.function, self._off_cmd.param
            )
            if success and self._switch_def.has_state:
                self._attr_is_on = False
                self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if not self._switch_def.has_state:
            return None
        return getattr(self, "_attr_is_on", False)
