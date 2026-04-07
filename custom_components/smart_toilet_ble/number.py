"""Support for Smart Toilet BLE number entities."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS
from .entity import SmartToiletEntity

# Number entity definitions: (unique_id_suffix, name, function_code, min, max, step)
NUMBERS = [
    ("seat_temp", "Seat Temperature", 0x40, 0, 5, 1),
    ("water_temp", "Water Temperature", 0x41, 0, 5, 1),
    ("wind_temp", "Wind Temperature", 0x42, 0, 5, 1),
    ("pressure", "Water Pressure", 0x43, 0, 5, 1),
    ("position", "Nozzle Position", 0x44, 0, 5, 1),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE number entities."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    numbers = []
    for number_id, name, function, min_val, max_val, step in NUMBERS:
        numbers.append(
            SmartToiletNumber(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                number_id=number_id,
                name=name,
                function=function,
                min_value=min_val,
                max_value=max_val,
                step=step,
            )
        )
    
    async_add_entities(numbers)


class SmartToiletNumber(SmartToiletEntity, NumberEntity):
    """Representation of a Smart Toilet BLE number entity."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        number_id: str,
        name: str,
        function: int,
        min_value: int,
        max_value: int,
        step: int,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entry_id)
        
        self._number_id = number_id
        self._function = function
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_number_{number_id}"
        self._attr_icon = ICONS.get(number_id, "mdi:gauge")
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = NumberMode.SLIDER
        self._attr_native_unit_of_measurement = "level"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        if hasattr(self.coordinator, '_last_values') and self._number_id in self.coordinator._last_values:
            return float(self.coordinator._last_values[self._number_id])
        return 0.0

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        level = int(value)
        success = await self.coordinator.send_toilet_command(self._function, level)
        if success:
            # Value is tracked in coordinator._last_values
            self.async_write_ha_state()
