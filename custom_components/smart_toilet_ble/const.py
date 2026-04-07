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
        features=["light", "power", "eco", "foam", "auto", "wash", "cover", "flush", "dry"],
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
    SwitchDefinition("light", "Light", "light_on", "light_off"),
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

# Number (slider) definitions
NUMBER_DEFINITIONS = [
    ("seat_temp", "Seat Temperature", 0x40),
    ("water_temp", "Water Temperature", 0x41),
    ("wind_temp", "Wind Temperature", 0x42),
    ("pressure", "Water Pressure", 0x43),
    ("position", "Nozzle Position", 0x44),
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
