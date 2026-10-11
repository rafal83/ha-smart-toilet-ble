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
    DM_FUNC_POSITION,
    DM_FUNC_SEAT_TEMP,
    DM_FUNC_WATER_PRESSURE,
    DM_FUNC_WATER_TEMP,
    DM_FUNC_WIND_TEMP,
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
    WRITE_CHAR_UUIDS,
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
        self._command_lock = asyncio.Lock()
        self._write_char_uuid: str | None = None

        # DM internal state for piggybacked temperature and level parameters
        # Defaults match DM-Toilet app state: shuiwen=1 (34°C), fengwen=0 (off), zuowen=0 (off)
        self._dm_water_temp: int = 1
        self._dm_wind_temp: int = 0
        self._dm_seat_temp: int = 0
        self._dm_pressure: int = 0
        self._dm_position: int = 0

        # Last set values for sliders/sensors (we have no state feedback)
        self._last_values: dict[str, int] = {
            "water_temp": 1,
            "wind_temp": 0,
            "seat_temp": 0,
            "pressure": 0,
            "position": 0,
        }

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

    def _handle_disconnect(self, client: BleakClient) -> None:
        """Handle spontaneous BLE disconnect."""
        _LOGGER.info("Spontaneous BLE disconnect from %s (%s)", self._model.name, self._mac_address)
        self._is_connected = False
        self._client = None
        self._write_char_uuid = None
        self.async_set_updated_data({})
        self._schedule_reconnect()

    async def async_connect(self) -> None:
        """Connect via bleak-retry-connector with disconnect callback."""
        async with self._connection_lock:
            if self._is_connected and self._client and self._client.is_connected:
                return

            # Clean up any stale client
            if self._client:
                try:
                    await self._client.disconnect()
                except Exception:
                    pass
                self._client = None

            self._ble_device = async_ble_device_from_address(
                self.hass, self._mac_address, connectable=True
            )

            if self._ble_device is None:
                _LOGGER.debug(
                    "BLE device %s not discovered yet, will retry in %ds",
                    self._mac_address,
                    RECONNECT_INTERVAL,
                )
                self._is_connected = False
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
                    disconnected_callback=self._handle_disconnect,
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
                self._client = None
                self._write_char_uuid = None
                self._ble_device = None
                self._schedule_reconnect()

    def _find_write_char(self) -> str | None:
        """Find the writable characteristic, preferring documented UUIDs (ffe1 / ffa1)."""
        if not self._client:
            return None

        # Look specifically for ffe1 or ffa1 first (matching DM app ble/robot.js)
        fallback = None
        for service in self._client.services:
            for char in service.characteristics:
                props = char.properties
                if "write" not in props and "write-without-response" not in props:
                    continue
                char_uuid_lower = char.uuid.lower()
                for known_uuid in WRITE_CHAR_UUIDS:
                    if known_uuid.lower() in char_uuid_lower or known_uuid[:8].lower() in char_uuid_lower:
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

        client = self._client
        self._is_connected = False
        self._client = None
        self._write_char_uuid = None
        self._ble_device = None

        if client:
            try:
                await client.disconnect()
                _LOGGER.info("Disconnected from Smart Toilet")
            except Exception:
                pass
        self.async_set_updated_data({})

    async def send_raw_command(self, command: bytes) -> bool:
        """Send a raw frame on the write characteristic with sequential locking."""
        async with self._command_lock:
            if not self._is_connected or not self._client or not self._client.is_connected:
                _LOGGER.debug("Not connected, attempting to connect before sending command")
                await self.async_connect()
                if not self._is_connected or not self._client or not self._client.is_connected:
                    _LOGGER.warning("Cannot send command: BLE connection failed")
                    return False

            if not self._write_char_uuid:
                self._write_char_uuid = self._find_write_char()
                if not self._write_char_uuid:
                    _LOGGER.error("Client or write characteristic not available")
                    return False

            try:
                await self._client.write_gatt_char(
                    self._write_char_uuid, command, response=False
                )
                _LOGGER.debug("Command sent: %s", command.hex())
                # Small pacing delay matching the toilet MCU buffer processing window
                await asyncio.sleep(0.15)
                return True
            except Exception as err:
                _LOGGER.error("Failed to send command: %s", err)
                self._is_connected = False
                self._client = None
                self._write_char_uuid = None
                self._schedule_reconnect()
                return False

    async def send_toilet_command(
        self,
        function: int,
        param1: int | None = None,
        param2: int | None = None,
        param3: int | None = None,
    ) -> bool:
        """Send a toilet command (type 0x02 for DM, byte1=function for SKS)."""
        if self._protocol == PROTOCOL_SKS:
            p1 = param1 if param1 is not None else 0
            p2 = param2 if param2 is not None else 0
            command = build_sks_command(function, [p1, p2])
            if function in SKS_SLIDER_FUNCTION_TO_KEY:
                self._last_values[SKS_SLIDER_FUNCTION_TO_KEY[function]] = p1
                self.async_set_updated_data({})
        else:
            # DM Protocol: exact behavior reverse-engineered from DM Toilet Control app
            # (ble/manager.js sendCommand)
            if function == DM_FUNC_WATER_PRESSURE:
                if param1 is not None:
                    self._dm_pressure = int(param1)
                p1, p2, p3 = self._dm_pressure, 0, 0
                self._last_values["pressure"] = self._dm_pressure
            elif function == DM_FUNC_POSITION:
                if param1 is not None:
                    self._dm_position = int(param1)
                p1, p2, p3 = self._dm_position, 0, 0
                self._last_values["position"] = self._dm_position
            else:
                # Update temperature if this command is one of the temp sliders
                if function == DM_FUNC_WATER_TEMP and param1 is not None:
                    self._dm_water_temp = int(param1)
                    self._last_values["water_temp"] = self._dm_water_temp
                elif function == DM_FUNC_WIND_TEMP and param1 is not None:
                    self._dm_wind_temp = int(param1)
                    self._last_values["wind_temp"] = self._dm_wind_temp
                elif function == DM_FUNC_SEAT_TEMP and param1 is not None:
                    self._dm_seat_temp = int(param1)
                    self._last_values["seat_temp"] = self._dm_seat_temp

                # All other commands (buttons, toggles, flush, etc.) piggyback current temperatures
                p1 = self._dm_water_temp
                p2 = self._dm_wind_temp
                p3 = self._dm_seat_temp

            command = build_dm_command(DM_TYPE_TOILET, function, p1, p2, p3)
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
