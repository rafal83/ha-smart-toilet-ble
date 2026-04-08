"""Support for Smart Toilet BLE select entities."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, LIGHT_MODE_LABELS, LIGHT_MODES
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE select entities."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if "light_mode" in coordinator.model.features:
        entities.append(SmartToiletLightModeSelect(coordinator, entry.entry_id))

    async_add_entities(entities)


class SmartToiletLightModeSelect(SmartToiletEntity, SelectEntity):
    """Representation of the light effect mode selector."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry_id)

        self._attr_name = "Light Mode"
        self._attr_unique_id = f"{entry_id}_select_light_mode"
        self._attr_icon = ICONS.get("light_mode", "mdi:lightbulb-multiple")
        self._attr_options = list(LIGHT_MODE_LABELS.values())

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return LIGHT_MODE_LABELS.get(self.coordinator._light_mode)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Reverse lookup: label -> key
        mode_key = next(
            (key for key, label in LIGHT_MODE_LABELS.items() if label == option),
            None,
        )
        if mode_key:
            await self.coordinator.set_light_mode(mode_key)
            self.async_write_ha_state()
