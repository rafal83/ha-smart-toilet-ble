"""Support for Smart Toilet BLE devices."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak import BleakClient
from bleak_retry_connector import establish_connection, BLEDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DM_LIGHT_ON_BIT,
    DM_SLIDER_FUNCTION_TO_KEY,
    DM_SYNC,
    DM_TYPE_LIGHT,
    DM_TYPE_TOILET,
    DOMAIN,
    LIGHT_MODES,
    NOTIFY_CHAR_UUID,
    PRESSURE_FUNCTION,
    PROTOCOL_DM,
    PROTOCOL_SKS,
    RECONNECT_INTERVAL,
    SKS_RESPONSE_SYNC,
    SKS_SLIDER_FUNCTION_TO_KEY,
    TEMP_FUNCTIONS,
    WRITE_CHAR_UUID,
    build_dm_command,
    build_sks_command,
    get_model,
    get_model_commands,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["light", "select", "switch", "button", "sensor", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Toilet BLE from a config entry."""
    coordinator = SmartToiletCoordinator(hass, entry)

    hass.async_create_background_task(
        coordinator.async_connect(),
        f"smart_toilet_connect_{entry.entry_id}"
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def async_handle_send_command(call) -> None:
        command_name = call.data.get("command", "")
        commands = coordinator.commands
        if command := commands.get(command_name):
            await coordinator.send_toilet_command(command.function, command.param)
        else:
            _LOGGER.warning("Unknown command: %s (model: %s)", command_name, coordinator.model_id)

    async def async_handle_set_temperature(call) -> None:
        temp_type = call.data.get("type", "")
        level = int(call.data.get("level", 0))
        if function := TEMP_FUNCTIONS.get(temp_type):
            await coordinator.send_toilet_command(function, level)
        else:
            _LOGGER.warning("Unknown temperature type: %s", temp_type)

    async def async_handle_set_pressure(call) -> None:
        level = int(call.data.get("level", 0))
        await coordinator.send_toilet_command(PRESSURE_FUNCTION, level)

    async def async_handle_flush(call) -> None:
        flush_cmd = coordinator.commands.get("flush")
        if flush_cmd:
            await coordinator.send_toilet_command(flush_cmd.function, flush_cmd.param)

    async def async_handle_stop_all(call) -> None:
        stop_cmd = coordinator.commands.get("stop")
        if stop_cmd:
            await coordinator.send_toilet_command(stop_cmd.function, stop_cmd.param)

    async def async_handle_set_light_color(call) -> None:
        r = int(call.data.get("red", 255))
        g = int(call.data.get("green", 255))
        b = int(call.data.get("blue", 255))
        await coordinator.set_light_rgb((r, g, b))

    services = {
        "send_command": async_handle_send_command,
        "set_temperature": async_handle_set_temperature,
        "set_pressure": async_handle_set_pressure,
        "flush": async_handle_flush,
        "stop_all": async_handle_stop_all,
        "set_light_color": async_handle_set_light_color,
    }
    for service_name, handler in services.items():
        hass.services.async_register(DOMAIN, service_name, handler)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        for service_name in ["send_command", "set_temperature", "set_pressure", "flush", "stop_all", "set_light_color"]:
            hass.services.async_remove(DOMAIN, service_name)
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_disconnect()
    return unload_ok


class SmartToiletCoordinator(DataUpdateCoordinator):
    """Coordinator for Smart Toilet BLE device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get("name", "Smart Toilet"),
        )
        self._entry = entry
        self._mac_address = entry.data["mac_address"]
        self._device_name = entry.data.get("name", "Smart Toilet")

        self._model_id = entry.data.get("model", "dm_smart_toilet")
        self._model = get_model(self._model_id)
        self._commands = get_model_commands(self._model_id)
        self._protocol = self._model.protocol

        self._ble_device: BLEDevice | None = None
        self._client: BleakClient | None = None
        self._is_connected = False
        self._reconnect_task = None
        self._connection_lock = asyncio.Lock()
        self._write_char_uuid: str | None = None

        # Last set values for sliders/sensors (we have no state feedback)
        self._last_values: dict[str, int] = {}

        # Ambient light state (DM type 0x03)
        self._light_on: bool = False
        self._light_rgb: tuple[int, int, int] = (255, 255, 255)
        self._light_brightness: int = 255   # HA scale 0..255
        self._light_mode: str = "static"

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def model(self) -> Any:
        return self._model

    @property
    def commands(self) -> dict[str, Any]:
        return self._commands

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def mac_address(self) -> str:
        return self._mac_address

    @property
    def device_name(self) -> str:
        return self._device_name

    async def async_connect(self) -> None:
        """Connect via bleak-retry-connector."""
        async with self._connection_lock:
            if self._is_connected:
                return

            self._ble_device = async_ble_device_from_address(
                self.hass, self._mac_address
            )

            if self._ble_device is None:
                _LOGGER.debug(
                    "BLE device %s not discovered yet, will retry in %ds",
                    self._mac_address,
                    RECONNECT_INTERVAL,
                )
                self._schedule_reconnect()
                return

            _LOGGER.debug(
                "Connecting to %s (model: %s, protocol: %s)",
                self._mac_address, self._model_id, self._protocol,
            )

            try:
                self._client = await establish_connection(
                    BleakClient,
                    self._ble_device,
                    self._mac_address,
                    max_attempts=3,
                )
                self._is_connected = True
                self._write_char_uuid = self._find_write_char()
                _LOGGER.info(
                    "Connected to %s at %s (model: %s, protocol: %s)",
                    self._model.name, self._mac_address,
                    self._model_id, self._protocol,
                )
                self.async_set_updated_data({})

            except Exception as err:
                _LOGGER.warning(
                    "Failed to connect to toilet (will retry in %ds): %s",
                    RECONNECT_INTERVAL, err,
                )
                self._is_connected = False
                self._ble_device = None
                self._schedule_reconnect()

    def _find_write_char(self) -> str | None:
        """Find the writable characteristic, preferring the documented UUID."""
        if not self._client:
            return None

        fallback = None
        for service in self._client.services:
            for char in service.characteristics:
                props = char.properties
                if "write" not in props and "write-without-response" not in props:
                    continue
                if WRITE_CHAR_UUID in char.uuid.lower():
                    return char.uuid
                if fallback is None:
                    fallback = char.uuid
        return fallback

    def _schedule_reconnect(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = self.hass.loop.create_task(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        while not self._is_connected:
            try:
                await asyncio.sleep(RECONNECT_INTERVAL)
                await self.async_connect()
                if self._is_connected:
                    _LOGGER.info("Reconnected to Smart Toilet")
                    return
            except Exception as err:
                _LOGGER.debug("Reconnect attempt failed: %s", err)

    async def async_disconnect(self) -> None:
        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None

        if self._client:
            try:
                await self._client.disconnect()
                _LOGGER.info("Disconnected from Smart Toilet")
            except Exception:
                pass

        self._is_connected = False
        self._ble_device = None
        self._client = None
        self._write_char_uuid = None

    async def send_raw_command(self, command: bytes) -> bool:
        """Send a raw frame on the write characteristic."""
        if not self._is_connected or not self._client:
            _LOGGER.debug("Not connected, attempting to connect")
            await self.async_connect()
            if not self._is_connected:
                _LOGGER.warning("Still not connected after connect attempt")
                return False

        if not self._client or not self._write_char_uuid:
            _LOGGER.error("Client or write characteristic not available")
            return False

        try:
            await self._client.write_gatt_char(
                self._write_char_uuid, command, response=False
            )
            _LOGGER.debug("Command sent: %s", command.hex())
            return True
        except Exception as err:
            _LOGGER.error("Failed to send command: %s", err)
            self._is_connected = False
            self._schedule_reconnect()
            return False

    async def send_toilet_command(self, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bool:
        """Send a toilet command (type 0x02 for DM, byte1=function for SKS)."""
        if self._protocol == PROTOCOL_SKS:
            command = build_sks_command(function, [param1, param2])
        else:
            command = build_dm_command(DM_TYPE_TOILET, function, param1, param2, param3)

        # Track value if it's a slider
        slider_map = (
            DM_SLIDER_FUNCTION_TO_KEY if self._protocol == PROTOCOL_DM
            else SKS_SLIDER_FUNCTION_TO_KEY
        )
        if function in slider_map:
            self._last_values[slider_map[function]] = param1
            self.async_set_updated_data({})

        return await self.send_raw_command(command)

    # --------------------------------------------------------------
    # Ambient light (DM type 0x03)
    # --------------------------------------------------------------
    # L'app DM officielle envoie une seule trame contenant TOUT :
    #   [0xAA, 0x08, 0x03, mode | 0x80(if on), R*lightness/100, G*lightness/100, B*lightness/100, sum]
    # Donc on regroupe : un seul write par changement.

    async def _push_ambient_light(self) -> bool:
        if self._protocol != PROTOCOL_DM:
            return False

        mode_byte = LIGHT_MODES.get(self._light_mode, 0)
        if self._light_on:
            mode_byte |= DM_LIGHT_ON_BIT
        else:
            mode_byte = 0  # OFF: on n'allume aucun bit

        # HA brightness 0..255 → device lightness 0..100
        lightness_pct = round(self._light_brightness * 100 / 255)
        lightness_pct = max(0, min(100, lightness_pct))
        scale = lightness_pct / 100.0

        r = int(self._light_rgb[0] * scale)
        g = int(self._light_rgb[1] * scale)
        b = int(self._light_rgb[2] * scale)

        command = build_dm_command(DM_TYPE_LIGHT, mode_byte, r, g, b)
        success = await self.send_raw_command(command)
        if success:
            self.async_set_updated_data({})
        return success

    async def turn_light_on(
        self,
        rgb: tuple[int, int, int] | None = None,
        brightness: int | None = None,
    ) -> bool:
        self._light_on = True
        if rgb is not None:
            self._light_rgb = rgb
        if brightness is not None:
            self._light_brightness = brightness
        return await self._push_ambient_light()

    async def turn_light_off(self) -> bool:
        self._light_on = False
        return await self._push_ambient_light()

    async def set_light_rgb(self, rgb: tuple[int, int, int]) -> bool:
        self._light_rgb = rgb
        return await self._push_ambient_light()

    async def set_light_mode(self, mode: str) -> bool:
        if mode not in LIGHT_MODES:
            return False
        self._light_mode = mode
        return await self._push_ambient_light()
