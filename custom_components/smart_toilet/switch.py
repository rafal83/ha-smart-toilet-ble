"""Support for Smart Toilet BLE switches."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS
from .entity import SmartToiletEntity

# Switch definitions: (unique_id_suffix, name, function_code, on_param, off_param, has_state)
SWITCHES = [
    ("light", "Light", 0x01, 0x01, 0x00, True),
    ("power", "Power", 0x02, 0x01, 0x00, True),
    ("eco", "ECO Mode", 0x03, 0x01, 0x00, True),
    ("foam", "Foam Shield", 0x04, 0x01, 0x00, True),
    ("auto", "Auto Mode", 0x06, 0x01, 0x00, True),
    ("women_wash", "Women's Wash", 0x10, 0x01, None, False),
    ("butt_wash", "Butt Wash", 0x11, 0x01, None, False),
    ("child_wash", "Child Wash", 0x12, 0x01, None, False),
    ("massage", "Massage", 0x13, 0x01, None, False),
    ("dry", "Blow Dry", 0x31, 0x01, 0x00, True),
    ("cover", "Toilet Cover", 0x20, 0x01, 0x00, True),
    ("ring", "Toilet Ring", 0x21, 0x01, 0x00, True),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE switches."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
    for switch_id, name, function, on_param, off_param, has_state in SWITCHES:
        switches.append(
            SmartToiletSwitch(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                switch_id=switch_id,
                name=name,
                function=function,
                on_param=on_param,
                off_param=off_param,
                has_state=has_state,
            )
        )
    
    async_add_entities(switches)


class SmartToiletSwitch(SmartToiletEntity, SwitchEntity):
    """Representation of a Smart Toilet BLE switch."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        switch_id: str,
        name: str,
        function: int,
        on_param: int | None,
        off_param: int | None,
        has_state: bool,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry_id)
        
        self._switch_id = switch_id
        self._function = function
        self._on_param = on_param
        self._off_param = off_param
        self._has_state = has_state
        self._attr_name = f"{coordinator.mac_address.split(':')[-1]} - {name}"
        self._attr_unique_id = f"{entry_id}_switch_{switch_id}"
        self._attr_icon = ICONS.get(switch_id, "mdi:power")
        self._attr_assumed_state = not has_state
        self._attr_should_poll = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self._on_param is not None:
            success = await self.coordinator.send_toilet_command(
                self._function, self._on_param
            )
            if success and self._has_state:
                self._attr_is_on = True
                self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self._off_param is not None:
            success = await self.coordinator.send_toilet_command(
                self._function, self._off_param
            )
            if success and self._has_state:
                self._attr_is_on = False
                self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # Since we can't read state from toilet, assume off for momentary switches
        if not self._has_state:
            return None
        return getattr(self, "_attr_is_on", False)
