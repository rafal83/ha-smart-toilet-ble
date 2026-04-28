"""Support for Smart Toilet BLE light with RGB color."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartToiletCoordinator
from .const import DOMAIN
from .entity import SmartToiletEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Toilet BLE light."""
    coordinator: SmartToiletCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Only add light if the model supports it
    if "light" in coordinator.model.features:
        entities = [SmartToiletLight(coordinator, entry.entry_id)]
        async_add_entities(entities)


class SmartToiletLight(SmartToiletEntity, LightEntity):
    """Representation of the Smart Toilet BLE light."""

    def __init__(
        self,
        coordinator: SmartToiletCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator, entry_id)

        self._attr_translation_key = "ambient"
        self._attr_unique_id = f"{entry_id}_light"
        self._attr_icon = "mdi:lightbulb"

        if "rgb" in coordinator.model.features:
            self._attr_color_mode = ColorMode.RGB
            self._attr_supported_color_modes = {ColorMode.RGB}
        else:
            self._attr_color_mode = ColorMode.ONOFF
            self._attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator._light_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self.coordinator._light_brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the RGB color value."""
        if self._attr_color_mode == ColorMode.RGB:
            return self.coordinator._light_rgb
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        rgb = kwargs.get(ATTR_RGB_COLOR)
        if rgb is not None:
            rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        await self.coordinator.turn_light_on(rgb=rgb, brightness=brightness)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.coordinator.turn_light_off()
        self.async_write_ha_state()
