"""Support for Smart Toilet BLE sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, SENSOR_DEFINITIONS
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE sensors."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        SmartToiletSensor(coordinator, entry.entry_id, *sensor_def)
        for sensor_def in SENSOR_DEFINITIONS
    ]
    
    async_add_entities(sensors)


class SmartToiletSensor(SmartToiletEntity, SensorEntity):
    """Representation of a Smart Toilet BLE sensor."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
        sensor_id: str,
        name: str,
        key: str,
        device_class: str | None,
        unit: str | None,
        state_class: str | None,
    ) -> None:
        """Initialize the sensor from definition."""
        super().__init__(coordinator, entry_id)
        
        self._sensor_id = sensor_id
        self._key = key
        
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_sensor_{sensor_id}"
        self._attr_icon = ICONS.get(sensor_id, "mdi:gauge")
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        if self._key == "connection":
            return "Connected" if self.coordinator.is_connected else "Disconnected"
        
        # For level sensors, return last set value if available
        if hasattr(self.coordinator, '_last_values') and self._key in self.coordinator._last_values:
            return self.coordinator._last_values[self._key]
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Connection sensor is always available
        if self._key == "connection":
            return True
        return True  # Always show level sensors
