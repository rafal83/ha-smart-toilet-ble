"""Constants for Smart Toilet BLE integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from homeassistant.components.sensor import SensorStateClass

DOMAIN = "smart_toilet_ble"
MANUFACTURER = "Smart Toilet"

# BLE Configuration
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Connection settings
CONNECT_TIMEOUT = 10.0
COMMAND_TIMEOUT = 5.0
RECONNECT_INTERVAL = 30  # seconds
MAX_RECONNECT_ATTEMPTS = 3

# Command structure
CMD_SYNC = 0xAA
CMD_LENGTH = 0x08
CMD_TYPE_TOILET = 0x02
CMD_TYPE_LIGHT = 0x03

# Light functions
LIGHT_FUNCTION_ONOFF = 0x01
LIGHT_FUNCTION_RGB = 0x02
LIGHT_FUNCTION_MODE = 0x03
LIGHT_FUNCTION_BRIGHTNESS = 0x04

LIGHT_MODES = {
    "static": 0x00,
    "flashing": 0x01,
    "breathing": 0x02,
    "running_water": 0x03,
    "colorful_gradient": 0x04,
    "colorful_running": 0x05,
    "welcome": 0x06,
}

LIGHT_MODE_LABELS = {
    "static": "Static",
    "flashing": "Flashing",
    "breathing": "Breathing",
    "running_water": "Running Water",
    "colorful_gradient": "Colorful Gradient",
    "colorful_running": "Colorful Running",
    "welcome": "Welcome",
}


@dataclass
class ToiletCommand:
    """Represents a BLE toilet command."""
    name: str
    label: str
    function: int
    param: int
    category: str = "basic"  # basic, wash, cover, cleaning, temp


@dataclass
class SwitchDefinition:
    """Defines a switch with on/off commands."""
    id: str
    name: str
    on_command: str
    off_command: str
    has_state: bool = True


@dataclass
class ToiletModel:
    """Defines a toilet model with its specific commands and features."""
    id: str
    name: str
    description: str
    commands: dict[str, ToiletCommand]
    features: list[str] = field(default_factory=list)  # Features supported by this model
    manufacturer: str = "Generic"
    # BLE UUIDs (can be model-specific)
    service_uuid: str = SERVICE_UUID
    write_char_uuid: str = WRITE_CHAR_UUID


# ============================================================================
# TOILET MODELS REGISTRY
# ============================================================================

# Generic Japanese Toilet (default)
GENERIC_JAPANESE_COMMANDS = {
    # Basic controls
    "light_on": ToiletCommand("light_on", "Light On", 0x01, 0x01, "basic"),
    "light_off": ToiletCommand("light_off", "Light Off", 0x01, 0x00, "basic"),
    "power_on": ToiletCommand("power_on", "Power On", 0x02, 0x01, "basic"),
    "power_off": ToiletCommand("power_off", "Power Off", 0x02, 0x00, "basic"),
    "eco_on": ToiletCommand("eco_on", "ECO Mode On", 0x03, 0x01, "basic"),
    "eco_off": ToiletCommand("eco_off", "ECO Mode Off", 0x03, 0x00, "basic"),
    "foam_on": ToiletCommand("foam_on", "Foam Shield On", 0x04, 0x01, "basic"),
    "foam_off": ToiletCommand("foam_off", "Foam Shield Off", 0x04, 0x00, "basic"),
    "stop": ToiletCommand("stop", "Stop All", 0x05, 0x00, "basic"),
    "auto_on": ToiletCommand("auto_on", "Auto Mode On", 0x06, 0x01, "basic"),
    "auto_off": ToiletCommand("auto_off", "Auto Mode Off", 0x06, 0x00, "basic"),
    "self_clean": ToiletCommand("self_clean", "Self Clean", 0x07, 0x01, "cleaning"),
    
    # Washing functions
    "women_wash": ToiletCommand("women_wash", "Women's Wash", 0x10, 0x01, "wash"),
    "butt_wash": ToiletCommand("butt_wash", "Butt Wash", 0x11, 0x01, "wash"),
    "child_wash": ToiletCommand("child_wash", "Child Wash", 0x12, 0x01, "wash"),
    "massage": ToiletCommand("massage", "Massage", 0x13, 0x01, "wash"),
    
    # Cover controls
    "cover_open": ToiletCommand("cover_open", "Cover Open", 0x20, 0x01, "cover"),
    "cover_close": ToiletCommand("cover_close", "Cover Close", 0x20, 0x00, "cover"),
    "ring_open": ToiletCommand("ring_open", "Ring Open", 0x21, 0x01, "cover"),
    "ring_close": ToiletCommand("ring_close", "Ring Close", 0x21, 0x00, "cover"),
    
    # Cleaning functions
    "flush": ToiletCommand("flush", "Flush", 0x30, 0x01, "cleaning"),
    "dry_on": ToiletCommand("dry_on", "Blow Dry On", 0x31, 0x01, "cleaning"),
    "dry_off": ToiletCommand("dry_off", "Blow Dry Off", 0x31, 0x00, "cleaning"),

    # Advanced settings - On/Off switches
    "auto_flush_on": ToiletCommand("auto_flush_on", "Auto Flush On", 0x58, 0x01, "advanced"),
    "auto_flush_off": ToiletCommand("auto_flush_off", "Auto Flush Off", 0x58, 0x00, "advanced"),
    "auto_foam_on": ToiletCommand("auto_foam_on", "Auto Foam On", 0x59, 0x01, "advanced"),
    "auto_foam_off": ToiletCommand("auto_foam_off", "Auto Foam Off", 0x59, 0x00, "advanced"),
    "auto_night_light_on": ToiletCommand("auto_night_light_on", "Auto Night Light On", 0x5A, 0x01, "advanced"),
    "auto_night_light_off": ToiletCommand("auto_night_light_off", "Auto Night Light Off", 0x5A, 0x00, "advanced"),
    "aging_mode_on": ToiletCommand("aging_mode_on", "Aging Mode On", 0x5B, 0x01, "advanced"),
    "aging_mode_off": ToiletCommand("aging_mode_off", "Aging Mode Off", 0x5B, 0x00, "advanced"),
    "virtual_seat_on": ToiletCommand("virtual_seat_on", "Virtual Seat On", 0x5C, 0x01, "advanced"),
    "virtual_seat_off": ToiletCommand("virtual_seat_off", "Virtual Seat Off", 0x5C, 0x00, "advanced"),
}

# TOTO Washlet & LIXIL SATIS (Placeholder - Commandes réelles à trouver)
# These are examples showing where real codes would go.
# TODO: Replace with real reverse-engineered codes if available
TOTO_WASHLET_COMMANDS = GENERIC_JAPANESE_COMMANDS  # Placeholder
LIXIL_SATIS_COMMANDS = GENERIC_JAPANESE_COMMANDS   # Placeholder

# All supported models
TOILET_MODELS: dict[str, ToiletModel] = {
    "generic_japanese": ToiletModel(
        id="generic_japanese",
        name="Generic Japanese Toilet",
        description="Standard Japanese smart toilet with BLE control (Verified from APK reverse-engineering)",
        commands=GENERIC_JAPANESE_COMMANDS,
        features=["light", "rgb", "power", "eco", "foam", "auto", "wash", "cover", "flush", "dry", "auto_flush", "auto_foam", "auto_night_light", "aging_mode", "virtual_seat", "advanced_settings", "light_mode"],
        manufacturer="Generic",
    ),
    # Uncomment and update when real codes are discovered:
    # "toto_washlet": ToiletModel(
    #     id="toto_washlet",
    #     name="TOTO Washlet",
    #     description="TOTO Washlet with advanced bidet functions",
    #     commands=TOTO_WASHLET_COMMANDS,
    #     features=["light", "power", "eco", "foam", "auto", "wash", "cover", "flush", "dry", "ewater+"],
    #     manufacturer="TOTO",
    # ),
}

# Default model
DEFAULT_MODEL = "generic_japanese"

# ============================================================================
# ENTITY DEFINITIONS (model-agnostic, use command names)
# ============================================================================

# Switch definitions - references to command names (resolved per model)
SWITCH_DEFINITIONS = [
    SwitchDefinition("power", "Power", "power_on", "power_off"),
    SwitchDefinition("eco", "ECO Mode", "eco_on", "eco_off"),
    SwitchDefinition("foam", "Foam Shield", "foam_on", "foam_off"),
    SwitchDefinition("auto", "Auto Mode", "auto_on", "auto_off"),
    SwitchDefinition("women_wash", "Women's Wash", "women_wash", None, has_state=False),
    SwitchDefinition("butt_wash", "Butt Wash", "butt_wash", None, has_state=False),
    SwitchDefinition("child_wash", "Child Wash", "child_wash", None, has_state=False),
    SwitchDefinition("massage", "Massage", "massage", None, has_state=False),
    SwitchDefinition("dry", "Blow Dry", "dry_on", "dry_off"),
    SwitchDefinition("cover", "Toilet Cover", "cover_open", "cover_close"),
    SwitchDefinition("ring", "Toilet Ring", "ring_open", "ring_close"),
    # Advanced settings switches
    SwitchDefinition("auto_flush", "Auto Flush", "auto_flush_on", "auto_flush_off"),
    SwitchDefinition("auto_foam", "Auto Foam", "auto_foam_on", "auto_foam_off"),
    SwitchDefinition("auto_night_light", "Auto Night Light", "auto_night_light_on", "auto_night_light_off"),
    SwitchDefinition("aging_mode", "Aging Mode", "aging_mode_on", "aging_mode_off"),
    SwitchDefinition("virtual_seat", "Virtual Seat", "virtual_seat_on", "virtual_seat_off"),
]

# Button definitions - references to command names
BUTTON_DEFINITIONS = [
    ("flush", "Flush", "flush"),
    ("stop", "Stop All", "stop"),
    ("self_clean", "Self Clean", "self_clean"),
]

# Sensor definitions
SENSOR_DEFINITIONS = [
    ("connection", "Connection Status", "connection", None, None, None),
    ("seat_temp", "Seat Temperature Level", "seat_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("water_temp", "Water Temperature Level", "water_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("wind_temp", "Wind Temperature Level", "wind_temp", None, "level", SensorStateClass.MEASUREMENT),
    ("pressure", "Water Pressure Level", "pressure", None, "level", SensorStateClass.MEASUREMENT),
    ("position", "Nozzle Position Level", "position", None, "level", SensorStateClass.MEASUREMENT),
]

# Number (slider) definitions: (id, name, function, min, max, step, unit)
NUMBER_DEFINITIONS = [
    ("seat_temp", "Seat Temperature", 0x40, 0, 5, 1, "level"),
    ("water_temp", "Water Temperature", 0x41, 0, 5, 1, "level"),
    ("wind_temp", "Wind Temperature", 0x42, 0, 5, 1, "level"),
    ("pressure", "Water Pressure", 0x43, 0, 5, 1, "level"),
    ("position", "Nozzle Position", 0x44, 0, 5, 1, "level"),
    # Advanced settings - range values
    ("lid_open_torque", "Lid Open Torque", 0x50, 0, 100, 1, "%"),
    ("lid_close_torque", "Lid Close Torque", 0x51, 0, 100, 1, "%"),
    ("ring_open_torque", "Ring Open Torque", 0x52, 0, 100, 1, "%"),
    ("ring_close_torque", "Ring Close Torque", 0x53, 0, 100, 1, "%"),
    ("volume", "Volume", 0x54, 0, 100, 1, "%"),
    ("flush_time", "Flush Time", 0x55, 0, 100, 1, "%"),
    ("radar_sensitivity", "Radar Sensitivity", 0x56, 0, 10, 1, "level"),
    ("auto_close_time", "Auto Close Time", 0x57, 0, 100, 1, "%"),
]

# Temperature and pressure control functions
TEMP_FUNCTIONS = {
    "seat": 0x40,
    "water": 0x41,
    "wind": 0x42,
}

PRESSURE_FUNCTION = 0x43
POSITION_FUNCTION = 0x44

# Level range
MIN_LEVEL = 0
MAX_LEVEL = 5

# Entity icons
ICONS = {
    "light": "mdi:lightbulb",
    "power": "mdi:power",
    "eco": "mdi:leaf",
    "foam": "mdi:chart-bubble",
    "auto": "mdi:autorenew",
    "women_wash": "mdi:shower",
    "butt_wash": "mdi:water",
    "child_wash": "mdi:baby-carriage",
    "massage": "mdi:spa",
    "dry": "mdi:hair-dryer",
    "cover": "mdi:toilet",
    "ring": "mdi:circle-outline",
    "flush": "mdi:water-pump",
    "stop": "mdi:stop",
    "self_clean": "mdi:brush",
    "seat_temp": "mdi:thermometer",
    "water_temp": "mdi:thermometer-water",
    "wind_temp": "mdi:thermometer-chevron",
    "pressure": "mdi:gauge",
    "position": "mdi:axis-arrow",
    "connection": "mdi:bluetooth-connect",
    # Advanced settings
    "auto_flush": "mdi:water-sync",
    "auto_foam": "mdi:chart-bubble",
    "auto_night_light": "mdi:weather-night",
    "aging_mode": "mdi:cog-outline",
    "virtual_seat": "mdi:seat",
    "lid_open_torque": "mdi:rotate-right",
    "lid_close_torque": "mdi:rotate-left",
    "ring_open_torque": "mdi:rotate-right",
    "ring_close_torque": "mdi:rotate-left",
    "volume": "mdi:volume-high",
    "flush_time": "mdi:timer-outline",
    "radar_sensitivity": "mdi:radar",
    "auto_close_time": "mdi:timer-lock-outline",
    "light_mode": "mdi:lightbulb-multiple",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model(model_id: str | None = None) -> ToiletModel:
    """Get a toilet model by ID, or default if not found."""
    if model_id and model_id in TOILET_MODELS:
        return TOILET_MODELS[model_id]
    return TOILET_MODELS[DEFAULT_MODEL]


def get_model_commands(model_id: str | None = None) -> dict[str, ToiletCommand]:
    """Get commands for a specific model."""
    return get_model(model_id).commands


def get_model_features(model_id: str | None = None) -> list[str]:
    """Get supported features for a model."""
    return get_model(model_id).features


def command_exists(command_name: str, model_id: str | None = None) -> bool:
    """Check if a command exists for a model."""
    return command_name in get_model_commands(model_id)
