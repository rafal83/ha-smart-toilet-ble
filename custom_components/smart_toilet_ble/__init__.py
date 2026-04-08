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
    DM_TYPE_LIGHT,
    DM_TYPE_TOILET,
    DOMAIN,
    LIGHT_FUNCTION_BRIGHTNESS,
    LIGHT_FUNCTION_MODE,
    LIGHT_FUNCTION_ONOFF,
    LIGHT_FUNCTION_RGB,
    LIGHT_MODES,
    PROTOCOL_DM,
    PROTOCOL_SKS,
    RECONNECT_INTERVAL,
    WRITE_CHAR_UUID,
    TEMP_FUNCTIONS,
    PRESSURE_FUNCTION,
    build_dm_command,
    build_sks_command,
    get_model,
    get_model_commands,
)

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS = ["light", "select", "switch", "button", "sensor", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Toilet BLE from a config entry."""
    coordinator = SmartToiletCoordinator(hass, entry)

    # Don't wait for connection - let it connect in background
    hass.async_create_background_task(
        coordinator.async_connect(),
        f"smart_toilet_connect_{entry.entry_id}"
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register services
    async def async_handle_send_command(call) -> None:
        """Handle send BLE command service."""
        command_name = call.data.get("command", "")

        # Get model-specific commands
        commands = coordinator.commands
        if command := commands.get(command_name):
            await coordinator.send_toilet_command(command.function, command.param)
        else:
            _LOGGER.warning("Unknown command: %s (model: %s)", command_name, coordinator.model_id)

    async def async_handle_set_temperature(call) -> None:
        """Handle set temperature service."""
        temp_type = call.data.get("type", "")
        level = int(call.data.get("level", 0))

        if function := TEMP_FUNCTIONS.get(temp_type):
            await coordinator.send_toilet_command(function, level)
        else:
            _LOGGER.warning("Unknown temperature type: %s", temp_type)

    async def async_handle_set_pressure(call) -> None:
        """Handle set pressure service."""
        level = int(call.data.get("level", 0))
        await coordinator.send_toilet_command(PRESSURE_FUNCTION, level)

    async def async_handle_flush(call) -> None:
        """Handle flush service."""
        flush_cmd = coordinator.commands.get("flush")
        if flush_cmd:
            await coordinator.send_toilet_command(flush_cmd.function, flush_cmd.param)

    async def async_handle_stop_all(call) -> None:
        """Handle stop all service."""
        stop_cmd = coordinator.commands.get("stop")
        if stop_cmd:
            await coordinator.send_toilet_command(stop_cmd.function, stop_cmd.param)

    async def async_handle_set_light_color(call) -> None:
        """Handle set light color service."""
        r = int(call.data.get("red", 255))
        g = int(call.data.get("green", 255))
        b = int(call.data.get("blue", 255))
        await coordinator.set_light_rgb((r, g, b))

    # Register all services
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
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Unregister all services
        for service_name in ["send_command", "set_temperature", "set_pressure", "flush", "stop_all", "set_light_color"]:
            hass.services.async_remove(DOMAIN, service_name)

        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_disconnect()

    return unload_ok


class SmartToiletCoordinator(DataUpdateCoordinator):
    """Coordinator for Smart Toilet BLE device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get("name", "Smart Toilet"),
        )
        self._entry = entry
        self._mac_address = entry.data["mac_address"]
        self._device_name = entry.data.get("name", "Smart Toilet")

        # Model-specific configuration
        self._model_id = entry.data.get("model", "dm_smart_toilet")
        self._model = get_model(self._model_id)
        self._commands = get_model_commands(self._model_id)
        self._protocol = self._model.protocol

        self._ble_device: BLEDevice | None = None
        self._client: BleakClient | None = None
        self._is_connected = False
        self._reconnect_task = None
        self._connection_lock = asyncio.Lock()

        # Track last set values for sensors/numbers
        self._last_values: dict[str, int] = {}

        # Track light state (DM protocol)
        self._light_on: bool = False
        self._light_rgb: tuple[int, int, int] = (255, 255, 255)
        self._light_brightness: int = 255  # HA uses 0-255
        self._light_mode: str = "static"

    @property
    def protocol(self) -> str:
        """Return the protocol type."""
        return self._protocol

    @property
    def model_id(self) -> str:
        """Return the model ID."""
        return self._model_id

    @property
    def model(self) -> Any:
        """Return the model configuration."""
        return self._model

    @property
    def commands(self) -> dict[str, Any]:
        """Return model-specific commands."""
        return self._commands

    async def async_connect(self) -> None:
        """Connect to the BLE device using bleak-retry-connector."""
        async with self._connection_lock:
            if self._is_connected:
                return

            # Get BLE device from HA's bluetooth integration
            self._ble_device = async_ble_device_from_address(
                self.hass, self._mac_address
            )

            if self._ble_device is None:
                _LOGGER.debug(
                    "BLE device %s not discovered yet, will retry in %ds",
                    self._mac_address,
                    RECONNECT_INTERVAL
                )
                self._schedule_reconnect()
                return

            _LOGGER.debug(
                "Connecting to %s (model: %s, protocol: %s) via bleak-retry-connector",
                self._mac_address,
                self._model_id,
                self._protocol,
            )

            try:
                # Use bleak-retry-connector for reliable connection
                self._client = await establish_connection(
                    BleakClient,
                    self._ble_device,
                    self._mac_address,
                    max_attempts=3,
                )

                self._is_connected = True
                _LOGGER.info(
                    "Connected to %s at %s (model: %s, protocol: %s)",
                    self._model.name,
                    self._mac_address,
                    self._model_id,
                    self._protocol,
                )
                self.async_set_updated_data({})

            except Exception as err:
                _LOGGER.warning(
                    "Failed to connect to toilet (will retry in %ds): %s",
                    RECONNECT_INTERVAL,
                    err
                )
                self._is_connected = False
                self._ble_device = None
                self._schedule_reconnect()

    def _schedule_reconnect(self) -> None:
        """Schedule a reconnection attempt."""
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = self.hass.loop.create_task(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        """Attempt to reconnect to the device."""
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
        """Disconnect from the BLE device."""
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

    async def send_raw_command(self, command: bytes) -> bool:
        """Send a raw BLE command to the toilet."""
        if not self._is_connected or not self._client:
            _LOGGER.debug("Not connected, attempting to connect")
            await self.async_connect()

            if not self._is_connected:
                _LOGGER.warning("Still not connected after connect attempt")
                return False

        if not self._client:
            _LOGGER.error("Client not available")
            return False

        try:
            # Find writable characteristic
            write_char_uuid_found = None
            services = await self._client.get_services()
            for service in services:
                for char in service.characteristics:
                    if WRITE_CHAR_UUID in char.uuid.lower():
                        write_char_uuid_found = char.uuid
                        break
                    if "write" in char.properties or "write-without-response" in char.properties:
                        write_char_uuid_found = char.uuid
                        break
                if write_char_uuid_found:
                    break

            if not write_char_uuid_found:
                _LOGGER.error("No writable characteristic found")
                return False

            # Send command
            await self._client.write_gatt_char(
                write_char_uuid_found,
                command,
                response=False
            )

            _LOGGER.debug("Command sent: %s", command.hex())
            return True

        except Exception as err:
            _LOGGER.error("Failed to send command: %s", err)
            self._is_connected = False
            self._schedule_reconnect()
            return False

    async def send_toilet_command(self, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bool:
        """Send a toilet command using the appropriate protocol."""
        if self._protocol == PROTOCOL_SKS:
            # SKS: function is the byte1 category, param1 is the code/value
            command = build_sks_command(function, [param1, param2])
        else:
            # DM: fixed 8-byte format
            command = build_dm_command(DM_TYPE_TOILET, function, param1, param2, param3)

        # Track numeric values
        if function in self._get_function_to_key_map():
            self._last_values[self._get_function_to_key_map()[function]] = param1
            self.async_set_updated_data({})

        return await self.send_raw_command(command)

    def _get_function_to_key_map(self) -> dict[int, str]:
        """Get the function code to value key mapping for the current protocol."""
        if self._protocol == PROTOCOL_DM:
            return {
                0x40: "seat_temp",
                0x41: "water_temp",
                0x42: "wind_temp",
                0x43: "pressure",
                0x44: "position",
                0x50: "lid_open_torque",
                0x51: "lid_close_torque",
                0x52: "ring_open_torque",
                0x53: "ring_close_torque",
                0x54: "volume",
                0x55: "flush_time",
                0x56: "radar_sensitivity",
                0x57: "auto_close_time",
            }
        # SKS uses plus_codes as function identifiers for sliders
        return {
            7: "position",
            13: "pressure",
            19: "water_temp",
            22: "seat_temp",
            23: "wind_temp",
            57: "wind_speed",
            28: "radar_level",
            29: "flush_level",
            30: "cover_force",
            31: "ring_force",
            32: "post_leave_flush_time",
            33: "auto_close_delay",
        }

    async def send_light_command(self, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bool:
        """Send a light command (DM protocol only, type 0x03)."""
        command = build_dm_command(DM_TYPE_LIGHT, function, param1, param2, param3)
        return await self.send_raw_command(command)

    async def turn_light_on(
        self,
        rgb: tuple[int, int, int] | None = None,
        brightness: int | None = None,
    ) -> bool:
        """Turn the light on, optionally with RGB color and brightness."""
        self._light_on = True
        if rgb is not None:
            self._light_rgb = rgb
            await self.send_light_command(
                LIGHT_FUNCTION_RGB,
                self._light_rgb[0],
                self._light_rgb[1],
                self._light_rgb[2],
            )
        if brightness is not None:
            self._light_brightness = brightness
            # Convert HA 0-255 to device 0-100
            device_brightness = round(brightness * 100 / 255)
            await self.send_light_command(LIGHT_FUNCTION_BRIGHTNESS, device_brightness)
        success = await self.send_light_command(LIGHT_FUNCTION_ONOFF, 0x01)
        if success:
            self.async_set_updated_data({})
        return success

    async def turn_light_off(self) -> bool:
        """Turn the light off."""
        self._light_on = False
        success = await self.send_light_command(LIGHT_FUNCTION_ONOFF, 0x00)
        if success:
            self.async_set_updated_data({})
        return success

    async def set_light_rgb(self, rgb: tuple[int, int, int]) -> bool:
        """Set the light RGB color."""
        self._light_rgb = rgb
        success = await self.send_light_command(
            LIGHT_FUNCTION_RGB, rgb[0], rgb[1], rgb[2]
        )
        if success:
            self.async_set_updated_data({})
        return success

    async def set_light_mode(self, mode: str) -> bool:
        """Set the light effect mode."""
        if mode not in LIGHT_MODES:
            return False
        self._light_mode = mode
        success = await self.send_light_command(LIGHT_FUNCTION_MODE, LIGHT_MODES[mode])
        if success:
            self.async_set_updated_data({})
        return success

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._is_connected

    @property
    def mac_address(self) -> str:
        """Return the MAC address."""
        return self._mac_address

    @property
    def device_name(self) -> str:
        """Return the device name."""
        return self._device_name
