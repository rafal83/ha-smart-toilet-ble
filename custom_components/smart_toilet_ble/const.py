"""Constants for Smart Toilet BLE integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


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

# ============================================================================
# PROTOCOL DEFINITIONS
# ============================================================================

# --- DM Protocol (DM-Toilet-Control app) ---
# Fixed 8-byte packets: [0xAA, 0x08, type, function, param1, param2, param3, checksum]
PROTOCOL_DM = "dm"
DM_SYNC = 0xAA
DM_LENGTH = 0x08
DM_TYPE_TOILET = 0x02
DM_TYPE_LIGHT = 0x03

# --- SKS Protocol (com.sks.toilet app) ---
# Variable-length packets: [0x33, function, params_len, ...params, checksum]
PROTOCOL_SKS = "sks"
SKS_SYNC = 0x33
SKS_RESPONSE_SYNC = 0x55
SKS_FUNC_BUTTON = 0x02   # byte1=2: button/action commands
SKS_FUNC_SETTING = 0x04  # byte1=4: settings commands
SKS_FUNC_QUERY = 0x33    # byte1=51: query commands
SKS_FUNC_JICUN_READ = 0x05
SKS_FUNC_JICUN_WRITE = 0x06

# Light functions (DM protocol ambient light)
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


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ToiletCommand:
    """Represents a BLE toilet command."""
    name: str
    label: str
    function: int
    param: int
    category: str = "basic"  # basic, wash, cover, cleaning, temp, advanced


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
    features: list[str] = field(default_factory=list)
    manufacturer: str = "Generic"
    protocol: str = PROTOCOL_DM  # "dm" or "sks"
    # BLE UUIDs (can be model-specific)
    service_uuid: str = SERVICE_UUID
    write_char_uuid: str = WRITE_CHAR_UUID
    # Model-specific entity definitions (override globals if set)
    switch_definitions: list[SwitchDefinition] | None = None
    button_definitions: list[tuple] | None = None
    number_definitions: list[tuple] | None = None
    sensor_definitions: list[tuple] | None = None


# ============================================================================
# COMMAND BUILDERS
# ============================================================================

def build_dm_command(cmd_type: int, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bytes:
    """Build a DM protocol command (fixed 8 bytes)."""
    cmd = [DM_SYNC, DM_LENGTH, cmd_type, function, param1, param2, param3]
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)


def build_sks_command(function: int, params: list[int] | None = None) -> bytes:
    """Build an SKS protocol command (variable length)."""
    if params is None:
        params = []
    cmd = [SKS_SYNC, function, len(params)] + params
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)


# ============================================================================
# DM PROTOCOL MODEL (DM-Toilet-Control / Generic Japanese)
# ============================================================================

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

# ============================================================================
# SKS PROTOCOL MODEL (com.sks.toilet v1.1.3)
# ============================================================================
# SKS commands use a different scheme:
#   Buttons:  build_sks_command(0x02, [value, 0])     -> toggles a function
#   Settings: build_sks_command(0x04, [code, value])   -> sets a setting

SKS_TOILET_COMMANDS = {
    # Basic controls (byte1=2, toggle buttons)
    "stop": ToiletCommand("stop", "Stop All", SKS_FUNC_BUTTON, 5, "basic"),
    "foam_on": ToiletCommand("foam_on", "Foam Shield On", SKS_FUNC_BUTTON, 28, "basic"),
    "foam_off": ToiletCommand("foam_off", "Foam Shield Off", SKS_FUNC_BUTTON, 28, "basic"),
    "self_clean": ToiletCommand("self_clean", "Self Clean", SKS_FUNC_BUTTON, 17, "cleaning"),

    # Washing functions
    "butt_wash": ToiletCommand("butt_wash", "Butt Wash", SKS_FUNC_BUTTON, 9, "wash"),
    "women_wash": ToiletCommand("women_wash", "Women's Wash", SKS_FUNC_BUTTON, 11, "wash"),
    "child_wash": ToiletCommand("child_wash", "Child Wash", SKS_FUNC_BUTTON, 31, "wash"),
    "assisted_wash": ToiletCommand("assisted_wash", "Assisted Wash", SKS_FUNC_BUTTON, 30, "wash"),
    "one_click_clean": ToiletCommand("one_click_clean", "One-Click Clean", SKS_FUNC_BUTTON, 10, "wash"),
    "moving_wash": ToiletCommand("moving_wash", "Moving Wash", SKS_FUNC_BUTTON, 32, "wash"),
    "massage": ToiletCommand("massage", "Massage", SKS_FUNC_BUTTON, 20, "wash"),
    "water_pattern": ToiletCommand("water_pattern", "Water Pattern Change", SKS_FUNC_BUTTON, 58, "wash"),

    # Cleaning & drying
    "flush": ToiletCommand("flush", "Full Flush", SKS_FUNC_BUTTON, 2, "cleaning"),
    "small_flush": ToiletCommand("small_flush", "Small Flush", SKS_FUNC_BUTTON, 4, "cleaning"),
    "dry_on": ToiletCommand("dry_on", "Blow Dry On", SKS_FUNC_BUTTON, 15, "cleaning"),
    "dry_off": ToiletCommand("dry_off", "Blow Dry Off", SKS_FUNC_BUTTON, 15, "cleaning"),

    # Cover controls
    "cover_open": ToiletCommand("cover_open", "Cover Open", SKS_FUNC_BUTTON, 35, "cover"),
    "cover_close": ToiletCommand("cover_close", "Cover Close", SKS_FUNC_BUTTON, 35, "cover"),
    "ring_open": ToiletCommand("ring_open", "Ring Open", SKS_FUNC_BUTTON, 36, "cover"),
    "ring_close": ToiletCommand("ring_close", "Ring Close", SKS_FUNC_BUTTON, 36, "cover"),

    # Lights
    "night_light": ToiletCommand("night_light", "Night Light", SKS_FUNC_BUTTON, 34, "basic"),
    "ambient_light": ToiletCommand("ambient_light", "Ambient Light", SKS_FUNC_BUTTON, 33, "basic"),

    # Special functions
    "aromatherapy": ToiletCommand("aromatherapy", "Aromatherapy", SKS_FUNC_BUTTON, 42, "basic"),
    "sterilization": ToiletCommand("sterilization", "Sterilization", SKS_FUNC_BUTTON, 47, "basic"),
    "infrared_therapy": ToiletCommand("infrared_therapy", "Infrared Therapy", SKS_FUNC_BUTTON, 45, "basic"),
    "user_1": ToiletCommand("user_1", "User Preset 1", SKS_FUNC_BUTTON, 48, "basic"),
    "user_2": ToiletCommand("user_2", "User Preset 2", SKS_FUNC_BUTTON, 50, "basic"),

    # Settings switches (byte1=4, code+value)
    "auto_aroma_on": ToiletCommand("auto_aroma_on", "Auto Aroma On", SKS_FUNC_SETTING, 1, "advanced"),
    "auto_aroma_off": ToiletCommand("auto_aroma_off", "Auto Aroma Off", SKS_FUNC_SETTING, 1, "advanced"),
    "timed_aroma_on": ToiletCommand("timed_aroma_on", "Timed Aroma On", SKS_FUNC_SETTING, 2, "advanced"),
    "timed_aroma_off": ToiletCommand("timed_aroma_off", "Timed Aroma Off", SKS_FUNC_SETTING, 2, "advanced"),
    "auto_ambient_light_on": ToiletCommand("auto_ambient_light_on", "Auto Ambient Light On", SKS_FUNC_SETTING, 3, "advanced"),
    "auto_ambient_light_off": ToiletCommand("auto_ambient_light_off", "Auto Ambient Light Off", SKS_FUNC_SETTING, 3, "advanced"),
    "auto_foam_on": ToiletCommand("auto_foam_on", "Auto Foam On", SKS_FUNC_SETTING, 4, "advanced"),
    "auto_foam_off": ToiletCommand("auto_foam_off", "Auto Foam Off", SKS_FUNC_SETTING, 4, "advanced"),
    "auto_deodorizer_on": ToiletCommand("auto_deodorizer_on", "Auto Deodorizer On", SKS_FUNC_SETTING, 5, "advanced"),
    "auto_deodorizer_off": ToiletCommand("auto_deodorizer_off", "Auto Deodorizer Off", SKS_FUNC_SETTING, 5, "advanced"),
    "flush_on_leave_on": ToiletCommand("flush_on_leave_on", "Flush on Leave On", SKS_FUNC_SETTING, 6, "advanced"),
    "flush_on_leave_off": ToiletCommand("flush_on_leave_off", "Flush on Leave Off", SKS_FUNC_SETTING, 6, "advanced"),
    "all_season_heat_on": ToiletCommand("all_season_heat_on", "All-Season Heating On", SKS_FUNC_SETTING, 7, "advanced"),
    "all_season_heat_off": ToiletCommand("all_season_heat_off", "All-Season Heating Off", SKS_FUNC_SETTING, 7, "advanced"),
    "moisturize_on": ToiletCommand("moisturize_on", "Moisturize On", SKS_FUNC_SETTING, 9, "advanced"),
    "moisturize_off": ToiletCommand("moisturize_off", "Moisturize Off", SKS_FUNC_SETTING, 9, "advanced"),
    "radar_on": ToiletCommand("radar_on", "Radar On", SKS_FUNC_SETTING, 10, "advanced"),
    "radar_off": ToiletCommand("radar_off", "Radar Off", SKS_FUNC_SETTING, 10, "advanced"),
    "foot_sensor_on": ToiletCommand("foot_sensor_on", "Foot Sensor On", SKS_FUNC_SETTING, 11, "advanced"),
    "foot_sensor_off": ToiletCommand("foot_sensor_off", "Foot Sensor Off", SKS_FUNC_SETTING, 11, "advanced"),
    "foot_sensor_cover_on": ToiletCommand("foot_sensor_cover_on", "Foot Sensor Cover/Ring On", SKS_FUNC_SETTING, 12, "advanced"),
    "foot_sensor_cover_off": ToiletCommand("foot_sensor_cover_off", "Foot Sensor Cover/Ring Off", SKS_FUNC_SETTING, 12, "advanced"),
    "energy_saving_on": ToiletCommand("energy_saving_on", "Energy Saving On", SKS_FUNC_SETTING, 13, "advanced"),
    "energy_saving_off": ToiletCommand("energy_saving_off", "Energy Saving Off", SKS_FUNC_SETTING, 13, "advanced"),
    "commercial_mode_on": ToiletCommand("commercial_mode_on", "Commercial Mode On", SKS_FUNC_SETTING, 14, "advanced"),
    "commercial_mode_off": ToiletCommand("commercial_mode_off", "Commercial Mode Off", SKS_FUNC_SETTING, 14, "advanced"),
    "buzzer_on": ToiletCommand("buzzer_on", "Buzzer On", SKS_FUNC_SETTING, 15, "advanced"),
    "buzzer_off": ToiletCommand("buzzer_off", "Buzzer Off", SKS_FUNC_SETTING, 15, "advanced"),
    "display_on": ToiletCommand("display_on", "Display On", SKS_FUNC_SETTING, 16, "advanced"),
    "display_off": ToiletCommand("display_off", "Display Off", SKS_FUNC_SETTING, 16, "advanced"),
    "lid_flush_on": ToiletCommand("lid_flush_on", "Close Lid & Flush On", SKS_FUNC_SETTING, 17, "advanced"),
    "lid_flush_off": ToiletCommand("lid_flush_off", "Close Lid & Flush Off", SKS_FUNC_SETTING, 17, "advanced"),
    "lid_first_flush_on": ToiletCommand("lid_first_flush_on", "Lid First Then Flush On", SKS_FUNC_SETTING, 18, "advanced"),
    "lid_first_flush_off": ToiletCommand("lid_first_flush_off", "Lid First Then Flush Off", SKS_FUNC_SETTING, 18, "advanced"),
    "auto_ceramic_sterilize_on": ToiletCommand("auto_ceramic_sterilize_on", "Auto Ceramic Sterilize On", SKS_FUNC_SETTING, 19, "advanced"),
    "auto_ceramic_sterilize_off": ToiletCommand("auto_ceramic_sterilize_off", "Auto Ceramic Sterilize Off", SKS_FUNC_SETTING, 19, "advanced"),
    "auto_nozzle_sterilize_on": ToiletCommand("auto_nozzle_sterilize_on", "Auto Nozzle Sterilize On", SKS_FUNC_SETTING, 20, "advanced"),
    "auto_nozzle_sterilize_off": ToiletCommand("auto_nozzle_sterilize_off", "Auto Nozzle Sterilize Off", SKS_FUNC_SETTING, 20, "advanced"),
    "auto_water_sterilize_on": ToiletCommand("auto_water_sterilize_on", "Auto Water Sterilize On", SKS_FUNC_SETTING, 21, "advanced"),
    "auto_water_sterilize_off": ToiletCommand("auto_water_sterilize_off", "Auto Water Sterilize Off", SKS_FUNC_SETTING, 21, "advanced"),
}

# SKS-specific entity definitions
SKS_SWITCH_DEFINITIONS = [
    # Toggle buttons (stateless, same code for on/off)
    SwitchDefinition("foam", "Foam Shield", "foam_on", "foam_off", has_state=False),
    SwitchDefinition("butt_wash", "Butt Wash", "butt_wash", None, has_state=False),
    SwitchDefinition("women_wash", "Women's Wash", "women_wash", None, has_state=False),
    SwitchDefinition("child_wash", "Child Wash", "child_wash", None, has_state=False),
    SwitchDefinition("assisted_wash", "Assisted Wash", "assisted_wash", None, has_state=False),
    SwitchDefinition("one_click_clean", "One-Click Clean", "one_click_clean", None, has_state=False),
    SwitchDefinition("moving_wash", "Moving Wash", "moving_wash", None, has_state=False),
    SwitchDefinition("massage", "Massage", "massage", None, has_state=False),
    SwitchDefinition("water_pattern", "Water Pattern", "water_pattern", None, has_state=False),
    SwitchDefinition("dry", "Blow Dry", "dry_on", "dry_off", has_state=False),
    SwitchDefinition("cover", "Toilet Cover", "cover_open", "cover_close", has_state=False),
    SwitchDefinition("ring", "Toilet Ring", "ring_open", "ring_close", has_state=False),
    SwitchDefinition("night_light", "Night Light", "night_light", None, has_state=False),
    SwitchDefinition("ambient_light", "Ambient Light", "ambient_light", None, has_state=False),
    SwitchDefinition("aromatherapy", "Aromatherapy", "aromatherapy", None, has_state=False),
    SwitchDefinition("sterilization", "Sterilization", "sterilization", None, has_state=False),
    SwitchDefinition("infrared_therapy", "Infrared Therapy", "infrared_therapy", None, has_state=False),
    # Settings switches (stateful, on/off pairs via byte1=4)
    SwitchDefinition("auto_aroma", "Auto Aroma", "auto_aroma_on", "auto_aroma_off"),
    SwitchDefinition("timed_aroma", "Timed Aroma", "timed_aroma_on", "timed_aroma_off"),
    SwitchDefinition("auto_ambient_light", "Auto Ambient Light", "auto_ambient_light_on", "auto_ambient_light_off"),
    SwitchDefinition("auto_foam", "Auto Foam", "auto_foam_on", "auto_foam_off"),
    SwitchDefinition("auto_deodorizer", "Auto Deodorizer", "auto_deodorizer_on", "auto_deodorizer_off"),
    SwitchDefinition("flush_on_leave", "Flush on Leave", "flush_on_leave_on", "flush_on_leave_off"),
    SwitchDefinition("all_season_heat", "All-Season Heating", "all_season_heat_on", "all_season_heat_off"),
    SwitchDefinition("moisturize", "Moisturize", "moisturize_on", "moisturize_off"),
    SwitchDefinition("radar", "Radar", "radar_on", "radar_off"),
    SwitchDefinition("foot_sensor", "Foot Sensor", "foot_sensor_on", "foot_sensor_off"),
    SwitchDefinition("foot_sensor_cover", "Foot Sensor Cover/Ring", "foot_sensor_cover_on", "foot_sensor_cover_off"),
    SwitchDefinition("energy_saving", "Energy Saving", "energy_saving_on", "energy_saving_off"),
    SwitchDefinition("commercial_mode", "Commercial Mode", "commercial_mode_on", "commercial_mode_off"),
    SwitchDefinition("buzzer", "Buzzer", "buzzer_on", "buzzer_off"),
    SwitchDefinition("display", "Display", "display_on", "display_off"),
    SwitchDefinition("lid_flush", "Close Lid & Flush", "lid_flush_on", "lid_flush_off"),
    SwitchDefinition("lid_first_flush", "Lid First Then Flush", "lid_first_flush_on", "lid_first_flush_off"),
    SwitchDefinition("auto_ceramic_sterilize", "Auto Ceramic Sterilize", "auto_ceramic_sterilize_on", "auto_ceramic_sterilize_off"),
    SwitchDefinition("auto_nozzle_sterilize", "Auto Nozzle Sterilize", "auto_nozzle_sterilize_on", "auto_nozzle_sterilize_off"),
    SwitchDefinition("auto_water_sterilize", "Auto Water Sterilize", "auto_water_sterilize_on", "auto_water_sterilize_off"),
]

SKS_BUTTON_DEFINITIONS = [
    ("flush", "Full Flush", "flush"),
    ("small_flush", "Small Flush", "small_flush"),
    ("stop", "Stop All", "stop"),
    ("self_clean", "Self Clean", "self_clean"),
    ("user_1", "User Preset 1", "user_1"),
    ("user_2", "User Preset 2", "user_2"),
]

# SKS slider controls use plus/minus codes via byte1=2
# For SKS, function stores the plus_code, and we send build_sks_command(0x02, [code, value])
SKS_NUMBER_DEFINITIONS = [
    # (id, name, plus_code, min, max, step, unit)
    ("position", "Nozzle Position", 7, 0, 4, 1, "level"),
    ("pressure", "Water Pressure", 13, 0, 2, 1, "level"),
    ("seat_temp", "Seat Temperature", 22, 0, 2, 1, "level"),
    ("water_temp", "Water Temperature", 19, 0, 2, 1, "level"),
    ("wind_temp", "Wind Temperature", 23, 0, 2, 1, "level"),
    ("wind_speed", "Wind Speed", 57, 0, 4, 1, "level"),
    # Settings sliders (byte1=4)
    ("radar_level", "Radar Level", 28, 1, 5, 1, "level"),
    ("flush_level", "Flush Level", 29, 1, 5, 1, "level"),
    ("cover_force", "Cover Force", 30, 1, 5, 1, "level"),
    ("ring_force", "Ring Force", 31, 1, 5, 1, "level"),
    ("post_leave_flush_time", "Post-Leave Flush Time", 32, 3, 60, 1, "s"),
    ("auto_close_delay", "Auto Close Delay", 33, 1, 5, 1, "level"),
]


# ============================================================================
# TOILET MODELS REGISTRY
# ============================================================================

TOILET_MODELS: dict[str, ToiletModel] = {
    "generic_japanese": ToiletModel(
        id="generic_japanese",
        name="Generic Japanese Toilet",
        description="DM-Toilet-Control protocol (fixed 8-byte packets, header 0xAA)",
        commands=GENERIC_JAPANESE_COMMANDS,
        features=["light", "rgb", "power", "eco", "foam", "auto", "wash", "cover",
                  "flush", "dry", "auto_flush", "auto_foam", "auto_night_light",
                  "aging_mode", "virtual_seat", "advanced_settings", "light_mode"],
        manufacturer="Generic",
        protocol=PROTOCOL_DM,
    ),
    "sks_toilet": ToiletModel(
        id="sks_toilet",
        name="SKS Smart Toilet",
        description="SKS protocol (variable-length packets, header 0x33)",
        commands=SKS_TOILET_COMMANDS,
        features=["wash", "cover", "flush", "small_flush", "dry", "foam",
                  "night_light", "ambient_light", "aromatherapy", "sterilization",
                  "infrared_therapy", "self_clean", "user_presets",
                  "auto_aroma", "timed_aroma", "auto_ambient_light", "auto_foam",
                  "auto_deodorizer", "flush_on_leave", "all_season_heat",
                  "moisturize", "radar", "foot_sensor", "energy_saving",
                  "buzzer", "display", "advanced_settings"],
        manufacturer="SKS",
        protocol=PROTOCOL_SKS,
        switch_definitions=SKS_SWITCH_DEFINITIONS,
        button_definitions=SKS_BUTTON_DEFINITIONS,
        number_definitions=SKS_NUMBER_DEFINITIONS,
    ),
}

# Default model
DEFAULT_MODEL = "generic_japanese"


# ============================================================================
# DEFAULT ENTITY DEFINITIONS (used by DM protocol models)
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

# Temperature and pressure control functions (DM protocol)
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
    "small_flush": "mdi:water-pump-off",
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
    # SKS-specific
    "night_light": "mdi:weather-night",
    "ambient_light": "mdi:lightbulb-group",
    "aromatherapy": "mdi:spa",
    "sterilization": "mdi:shield-bug-outline",
    "infrared_therapy": "mdi:radiator",
    "assisted_wash": "mdi:hand-wash",
    "one_click_clean": "mdi:auto-fix",
    "moving_wash": "mdi:swap-horizontal",
    "water_pattern": "mdi:waves",
    "user_1": "mdi:account",
    "user_2": "mdi:account-outline",
    "auto_aroma": "mdi:spa-outline",
    "timed_aroma": "mdi:timer-sand",
    "auto_ambient_light": "mdi:lightbulb-auto",
    "auto_deodorizer": "mdi:air-filter",
    "flush_on_leave": "mdi:exit-run",
    "all_season_heat": "mdi:thermometer-check",
    "moisturize": "mdi:water-opacity",
    "radar": "mdi:radar",
    "foot_sensor": "mdi:foot-print",
    "foot_sensor_cover": "mdi:foot-print",
    "energy_saving": "mdi:leaf",
    "commercial_mode": "mdi:store",
    "buzzer": "mdi:bell",
    "display": "mdi:monitor",
    "lid_flush": "mdi:toilet",
    "lid_first_flush": "mdi:toilet",
    "auto_ceramic_sterilize": "mdi:shield-check",
    "auto_nozzle_sterilize": "mdi:shield-check",
    "auto_water_sterilize": "mdi:shield-check",
    "wind_speed": "mdi:fan",
    "radar_level": "mdi:radar",
    "flush_level": "mdi:water-pump",
    "cover_force": "mdi:rotate-right",
    "ring_force": "mdi:rotate-left",
    "post_leave_flush_time": "mdi:timer-outline",
    "auto_close_delay": "mdi:timer-lock-outline",
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


def get_model_switch_definitions(model_id: str | None = None) -> list[SwitchDefinition]:
    """Get switch definitions for a model (model-specific or default)."""
    model = get_model(model_id)
    return model.switch_definitions if model.switch_definitions is not None else SWITCH_DEFINITIONS


def get_model_button_definitions(model_id: str | None = None) -> list[tuple]:
    """Get button definitions for a model (model-specific or default)."""
    model = get_model(model_id)
    return model.button_definitions if model.button_definitions is not None else BUTTON_DEFINITIONS


def get_model_number_definitions(model_id: str | None = None) -> list[tuple]:
    """Get number definitions for a model (model-specific or default)."""
    model = get_model(model_id)
    return model.number_definitions if model.number_definitions is not None else NUMBER_DEFINITIONS


def command_exists(command_name: str, model_id: str | None = None) -> bool:
    """Check if a command exists for a model."""
    return command_name in get_model_commands(model_id)
