"""Constants for Smart Toilet BLE integration."""

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
