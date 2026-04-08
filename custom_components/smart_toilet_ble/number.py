"""Support for Smart Toilet BLE number entities."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, NUMBER_DEFINITIONS
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE number entities."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    numbers = [
        SmartToiletNumber(coordinator, entry.entry_id, *num_def)
        for num_def in NUMBER_DEFINITIONS
    ]
    
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
        min_value: int = 0,
        max_value: int = 5,
        step: int = 1,
        unit: str = "level",
    ) -> None:
        """Initialize the number entity from definition."""
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
        self._attr_native_unit_of_measurement = unit

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
            self.async_write_ha_state()
