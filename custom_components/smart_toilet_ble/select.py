"""Support for Smart Toilet BLE select entities."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN, ICONS, LIGHT_MODES
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

        self._attr_translation_key = "light_mode"
        self._attr_unique_id = f"{entry_id}_select_light_mode"
        self._attr_icon = ICONS.get("light_mode", "mdi:lightbulb-multiple")
        # Les options sont les CLÉS — HA les traduit via translations/<lang>.json
        # entity.select.light_mode.state.<key>
        self._attr_options = list(LIGHT_MODES.keys())

    @property
    def current_option(self) -> str | None:
        """Return the current selected option (its key)."""
        return self.coordinator._light_mode

    async def async_select_option(self, option: str) -> None:
        """Change the selected option (option = mode key)."""
        if option in LIGHT_MODES:
            await self.coordinator.set_light_mode(option)
            self.async_write_ha_state()
