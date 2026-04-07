"""Base entity for Smart Toilet BLE devices."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SmartToiletCoordinator
from .const import DOMAIN


class SmartToiletEntity(CoordinatorEntity):
    """Base class for all Smart Toilet entities."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        
        self._entry_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.mac_address)},
            name=f"Smart Toilet ({coordinator.mac_address.split(':')[-1]})",
            manufacturer="rafal83",
            model="BLE Smart Toilet",
            sw_version="1.0",
        )
        self._attr_has_entity_name = True
        self._attr_should_poll = False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.is_connected
