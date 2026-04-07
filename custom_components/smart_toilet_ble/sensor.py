"""Support for Smart Toilet BLE sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS
from .entity import SmartToiletEntity

# Sensor definitions: (unique_id_suffix, name, key, device_class, unit, state_class)
SENSORS = [
    ("connection", "Connection Status", "connection", None, None, None),
    ("seat_temp", "Seat Temperature Level", "seat_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("water_temp", "Water Temperature Level", "water_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("wind_temp", "Wind Temperature Level", "wind_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("pressure", "Water Pressure Level", "pressure", None, "level", SensorStateClass.MEASUREMENT),
    ("position", "Nozzle Position Level", "position", None, "level", SensorStateClass.MEASUREMENT),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE sensors."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    for sensor_id, name, key, device_class, unit, state_class in SENSORS:
        sensors.append(
            SmartToiletSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                sensor_id=sensor_id,
                name=name,
                key=key,
                device_class=device_class,
                unit=unit,
                state_class=state_class,
            )
        )
    
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
        """Initialize the sensor."""
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
