"""Constants for Smart Toilet BLE integration."""
from dataclasses import dataclass
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


# All toilet commands registry
TOILET_COMMANDS = {
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
