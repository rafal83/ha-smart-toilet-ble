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
    CONNECT_TIMEOUT,
    DOMAIN,
    RECONNECT_INTERVAL,
    WRITE_CHAR_UUID,
    TOILET_COMMANDS,
    TEMP_FUNCTIONS,
    PRESSURE_FUNCTION,
    get_model,
    get_model_commands,
)

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS = ["switch", "button", "sensor", "number"]


def calculate_checksum(command_bytes: list[int]) -> int:
    """Calculate checksum: sum of bytes 0-6 modulo 256."""
    return sum(command_bytes) & 0xFF


def create_command(cmd_type: int, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bytes:
    """Create an 8-byte BLE command."""
    cmd = [0xAA, 0x08, cmd_type, function, param1, param2, param3]
    cmd.append(calculate_checksum(cmd))
    return bytes(cmd)


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

    # Register all services
    services = {
        "send_command": async_handle_send_command,
        "set_temperature": async_handle_set_temperature,
        "set_pressure": async_handle_set_pressure,
        "flush": async_handle_flush,
        "stop_all": async_handle_stop_all,
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
        for service_name in ["send_command", "set_temperature", "set_pressure", "flush", "stop_all"]:
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
        self._model_id = entry.data.get("model", "generic_japanese")
        self._model = get_model(self._model_id)
        self._commands = get_model_commands(self._model_id)
        
        self._ble_device: BLEDevice | None = None
        self._client: BleakClient | None = None
        self._is_connected = False
        self._reconnect_task = None
        self._connection_lock = asyncio.Lock()
        
        # Track last set values for sensors
        self._last_values: dict[str, int] = {
            "seat_temp": 0,
            "water_temp": 0,
            "wind_temp": 0,
            "pressure": 0,
            "position": 0,
        }

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
                "Connecting to %s (model: %s) via bleak-retry-connector", 
                self._mac_address,
                self._model_id
            )
            
            try:
                # Use model-specific UUIDs if defined
                service_uuid = self._model.service_uuid if hasattr(self._model, 'service_uuid') else "0000ffe0-0000-1000-8000-00805f9b34fb"
                write_char_uuid = self._model.write_char_uuid if hasattr(self._model, 'write_char_uuid') else "0000ffe1-0000-1000-8000-00805f9b34fb"
                
                # Use bleak-retry-connector for reliable connection
                self._client = await establish_connection(
                    BleakClient,
                    self._ble_device,
                    self._mac_address,
                    max_attempts=3,
                )
                
                self._is_connected = True
                _LOGGER.info(
                    "✓ Connected to %s at %s (model: %s)", 
                    self._model.name,
                    self._mac_address,
                    self._model_id
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
                    _LOGGER.info("✓ Reconnected to Smart Toilet")
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

    async def send_command(self, command: bytes) -> bool:
        """Send a BLE command to the toilet."""
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
        """Send a toilet command (type 0x02)."""
        # Track temperature/pressure/position levels
        function_to_key = {
            0x40: "seat_temp",
            0x41: "water_temp",
            0x42: "wind_temp",
            0x43: "pressure",
            0x44: "position",
        }
        
        if function in function_to_key:
            self._last_values[function_to_key[function]] = param1
            self.async_set_updated_data({})
        
        command = create_command(0x02, function, param1, param2, param3)
        return await self.send_command(command)

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
