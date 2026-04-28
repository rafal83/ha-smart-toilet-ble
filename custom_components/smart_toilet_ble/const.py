"""Constants for Smart Toilet BLE integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


DOMAIN = "smart_toilet_ble"
MANUFACTURER = "Smart Toilet"

# BLE Configuration
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"

# Connection settings
CONNECT_TIMEOUT = 10.0
COMMAND_TIMEOUT = 5.0
RECONNECT_INTERVAL = 30
MAX_RECONNECT_ATTEMPTS = 3

# ============================================================================
# PROTOCOL DEFINITIONS
# ============================================================================

# DM Protocol (DM-Toilet-Control v1.0.6, reverse-engineered from app source)
# Trame fixe 8 octets : [0xAA, 0x08, type, function, p1, p2, p3, sum]
#   type 0x02 = commandes WC
#   type 0x03 = lumière ambiante
PROTOCOL_DM = "dm"
DM_SYNC = 0xAA
DM_LENGTH = 0x08
DM_TYPE_TOILET = 0x02
DM_TYPE_LIGHT = 0x03

# SKS Protocol (com.sks.toilet)
PROTOCOL_SKS = "sks"
SKS_SYNC = 0x33
SKS_RESPONSE_SYNC = 0x55
SKS_FUNC_BUTTON = 0x02
SKS_FUNC_SETTING = 0x04
SKS_FUNC_QUERY = 0x33
SKS_FUNC_JICUN_READ = 0x05
SKS_FUNC_JICUN_WRITE = 0x06

# DM ambient light (type 0x03) — l'app envoie une seule trame:
#   [0xAA, 0x08, 0x03, mode|0x80, R*lightness/100, G*lightness/100, B*lightness/100, sum]
# Bit 7 (0x80) du mode = light ON. Sans ce bit = light OFF.
DM_LIGHT_MODE_OFF = 0x00
DM_LIGHT_MODE_STATIC = 1
DM_LIGHT_MODE_FLASHING = 2
DM_LIGHT_MODE_BREATHING = 3
DM_LIGHT_MODE_RUNNING = 4
DM_LIGHT_MODE_COLORFUL_RUNNING = 5
DM_LIGHT_MODE_COLORFUL_GRADIENT = 6
DM_LIGHT_MODE_WELCOME = 7
DM_LIGHT_ON_BIT = 0x80

LIGHT_MODES = {
    "static": DM_LIGHT_MODE_STATIC,
    "flashing": DM_LIGHT_MODE_FLASHING,
    "breathing": DM_LIGHT_MODE_BREATHING,
    "running_water": DM_LIGHT_MODE_RUNNING,
    "colorful_running": DM_LIGHT_MODE_COLORFUL_RUNNING,
    "colorful_gradient": DM_LIGHT_MODE_COLORFUL_GRADIENT,
    "welcome": DM_LIGHT_MODE_WELCOME,
}

LIGHT_MODE_LABELS = {
    "static": "Static",
    "flashing": "Flashing",
    "breathing": "Breathing",
    "running_water": "Running Water",
    "colorful_running": "Colorful Running",
    "colorful_gradient": "Colorful Gradient",
    "welcome": "Welcome",
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ToiletCommand:
    name: str
    label: str
    function: int
    param: int
    category: str = "basic"


@dataclass
class SwitchDefinition:
    id: str
    name: str
    on_command: str
    off_command: str
    has_state: bool = True
    is_config: bool = False


@dataclass
class ToiletModel:
    id: str
    name: str
    description: str
    commands: dict[str, ToiletCommand]
    features: list[str] = field(default_factory=list)
    manufacturer: str = "Generic"
    protocol: str = PROTOCOL_DM
    service_uuid: str = SERVICE_UUID
    write_char_uuid: str = WRITE_CHAR_UUID
    switch_definitions: list[SwitchDefinition] | None = None
    button_definitions: list[tuple] | None = None
    number_definitions: list[tuple] | None = None
    sensor_definitions: list[tuple] | None = None


# ============================================================================
# COMMAND BUILDERS
# ============================================================================

def build_dm_command(cmd_type: int, function: int, param1: int = 0, param2: int = 0, param3: int = 0) -> bytes:
    cmd = [DM_SYNC, DM_LENGTH, cmd_type, function, param1, param2, param3]
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)


def build_sks_command(function: int, params: list[int] | None = None) -> bytes:
    if params is None:
        params = []
    cmd = [SKS_SYNC, function, len(params)] + params
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)


# ============================================================================
# DM PROTOCOL — codes function reverse-engineered from DM Toilet Control v1.0.6
# ============================================================================
#
# L'app utilise `createCommond(value, p1, p2, p3)` qui produit la trame
# [0xAA, 0x08, 0x02, value, p1, p2, p3, sum].
#
# - Pour les sliders (water_temp, wind_temp, water_pressure, position, seat_temp):
#   `value` = le code function du slider, `p1` = level demandé, p2/p3 = 0
# - Pour tous les autres boutons/toggles :
#   `value` = le code function de l'action, p1/p2/p3 = état des températures
#   (envoyé en piggyback ; les passer à 0 est OK pour les actions ponctuelles)

# Codes pour les sliders (bytes 3 + 4 = function + level)
DM_FUNC_WATER_TEMP = 16        # shuiwen
DM_FUNC_WIND_TEMP = 32         # fengwen
DM_FUNC_WATER_PRESSURE = 33    # shuiya
DM_FUNC_POSITION = 34          # guanwei
DM_FUNC_SEAT_TEMP = 48         # zuowen

# Codes pour les boutons/actions (byte 3 = code, params = ignorés)
DM_FUNC_WOMEN_WASH = 1         # fuxi
DM_FUNC_BUTT_WASH = 2          # tunxi
DM_FUNC_CHILD_WASH = 3         # tongxi
DM_FUNC_BLOW_DRY = 4           # chuifeng
DM_FUNC_COVER = 5              # fangai
DM_FUNC_RING = 6               # fanquan
DM_FUNC_FLUSH = 7              # chongshui
DM_FUNC_AUTO_MODE = 8          # zidong
DM_FUNC_STOP = 9               # stop
DM_FUNC_POWER = 14             # power
DM_FUNC_LIGHT = 15             # light (toilet illumination, distinct from ambient)
DM_FUNC_SELF_CLEAN = 17        # zijie
DM_FUNC_FOAM = 18              # paomou
DM_FUNC_ECO = 19               # jieneng
DM_FUNC_MASSAGE = 20           # anmo

# Réglages avancés — paires de codes +/- (incrémentent/décrémentent une valeur interne)
DM_FUNC_LID_OPEN_FORCE_PLUS = 65       # fangai-kai +
DM_FUNC_LID_OPEN_FORCE_MINUS = 66      # fangai-kai -
DM_FUNC_LID_CLOSE_FORCE_PLUS = 81      # fangai-guan +
DM_FUNC_LID_CLOSE_FORCE_MINUS = 82     # fangai-guan -
DM_FUNC_RING_OPEN_FORCE_PLUS = 97      # fanquan-kai +
DM_FUNC_RING_OPEN_FORCE_MINUS = 98     # fanquan-kai -
DM_FUNC_RING_CLOSE_FORCE_PLUS = 113    # fanquan-guan +
DM_FUNC_RING_CLOSE_FORCE_MINUS = 114   # fanquan-guan -
DM_FUNC_VOLUME_PLUS = 129              # yinliang +
DM_FUNC_VOLUME_MINUS = 130             # yinliang -
DM_FUNC_FLUSH_TIME_PLUS = 145          # chongshui-time +
DM_FUNC_FLUSH_TIME_MINUS = 146         # chongshui-time -
DM_FUNC_RADAR_PLUS = 177               # leida +
DM_FUNC_RADAR_MINUS = 178              # leida -
DM_FUNC_AUTO_CLOSE_PLUS = 209          # zidong-guangai +
DM_FUNC_AUTO_CLOSE_MINUS = 210         # zidong-guangai -

# Réglages avancés — toggles ON/OFF (codes distincts pour ON et OFF)
DM_FUNC_AUTO_FLUSH_ON = 193            # zidong-chongshui ON
DM_FUNC_AUTO_FLUSH_OFF = 194           # zidong-chongshui OFF
DM_FUNC_AUTO_FOAM_ON = 225             # zidong-paomo ON
DM_FUNC_AUTO_FOAM_OFF = 226            # zidong-paomo OFF
DM_FUNC_AGING_MODE_ON = 241            # laohua ON
DM_FUNC_AGING_MODE_OFF = 242           # laohua OFF
DM_FUNC_VIRTUAL_SEAT_ON = 70           # xuni-zhaozuo ON
DM_FUNC_VIRTUAL_SEAT_OFF = 71          # xuni-zhaozuo OFF
DM_FUNC_USER_1_ON = 243                # yuliu-1 ON
DM_FUNC_USER_1_OFF = 244               # yuliu-1 OFF
DM_FUNC_USER_2_ON = 245                # yuliu-2 ON
DM_FUNC_USER_2_OFF = 246               # yuliu-2 OFF


DM_SMART_TOILET_COMMANDS = {
    # Boutons (actions ponctuelles, sans état)
    "power": ToiletCommand("power", "Power", DM_FUNC_POWER, 0, "basic"),
    "light": ToiletCommand("light", "Toilet Light", DM_FUNC_LIGHT, 0, "basic"),
    "eco": ToiletCommand("eco", "Energy Saving", DM_FUNC_ECO, 0, "basic"),
    "foam": ToiletCommand("foam", "Foam Shield", DM_FUNC_FOAM, 0, "basic"),
    "auto_mode": ToiletCommand("auto_mode", "Auto Mode", DM_FUNC_AUTO_MODE, 0, "basic"),
    "stop": ToiletCommand("stop", "Stop All", DM_FUNC_STOP, 0, "basic"),
    "self_clean": ToiletCommand("self_clean", "Self Clean", DM_FUNC_SELF_CLEAN, 0, "cleaning"),
    "flush": ToiletCommand("flush", "Flush", DM_FUNC_FLUSH, 0, "cleaning"),
    "blow_dry": ToiletCommand("blow_dry", "Blow Dry", DM_FUNC_BLOW_DRY, 0, "cleaning"),
    "women_wash": ToiletCommand("women_wash", "Women's Wash", DM_FUNC_WOMEN_WASH, 0, "wash"),
    "butt_wash": ToiletCommand("butt_wash", "Butt Wash", DM_FUNC_BUTT_WASH, 0, "wash"),
    "child_wash": ToiletCommand("child_wash", "Child Wash", DM_FUNC_CHILD_WASH, 0, "wash"),
    "massage": ToiletCommand("massage", "Massage", DM_FUNC_MASSAGE, 0, "wash"),
    "cover": ToiletCommand("cover", "Toilet Cover", DM_FUNC_COVER, 0, "cover"),
    "ring": ToiletCommand("ring", "Toilet Ring", DM_FUNC_RING, 0, "cover"),

    # Réglages +/- (paires de boutons distincts)
    "lid_open_force_plus": ToiletCommand("lid_open_force_plus", "Lid Open Force +", DM_FUNC_LID_OPEN_FORCE_PLUS, 0, "advanced"),
    "lid_open_force_minus": ToiletCommand("lid_open_force_minus", "Lid Open Force -", DM_FUNC_LID_OPEN_FORCE_MINUS, 0, "advanced"),
    "lid_close_force_plus": ToiletCommand("lid_close_force_plus", "Lid Close Force +", DM_FUNC_LID_CLOSE_FORCE_PLUS, 0, "advanced"),
    "lid_close_force_minus": ToiletCommand("lid_close_force_minus", "Lid Close Force -", DM_FUNC_LID_CLOSE_FORCE_MINUS, 0, "advanced"),
    "ring_open_force_plus": ToiletCommand("ring_open_force_plus", "Ring Open Force +", DM_FUNC_RING_OPEN_FORCE_PLUS, 0, "advanced"),
    "ring_open_force_minus": ToiletCommand("ring_open_force_minus", "Ring Open Force -", DM_FUNC_RING_OPEN_FORCE_MINUS, 0, "advanced"),
    "ring_close_force_plus": ToiletCommand("ring_close_force_plus", "Ring Close Force +", DM_FUNC_RING_CLOSE_FORCE_PLUS, 0, "advanced"),
    "ring_close_force_minus": ToiletCommand("ring_close_force_minus", "Ring Close Force -", DM_FUNC_RING_CLOSE_FORCE_MINUS, 0, "advanced"),
    "volume_plus": ToiletCommand("volume_plus", "Volume +", DM_FUNC_VOLUME_PLUS, 0, "advanced"),
    "volume_minus": ToiletCommand("volume_minus", "Volume -", DM_FUNC_VOLUME_MINUS, 0, "advanced"),
    "flush_time_plus": ToiletCommand("flush_time_plus", "Flush Time +", DM_FUNC_FLUSH_TIME_PLUS, 0, "advanced"),
    "flush_time_minus": ToiletCommand("flush_time_minus", "Flush Time -", DM_FUNC_FLUSH_TIME_MINUS, 0, "advanced"),
    "radar_plus": ToiletCommand("radar_plus", "Radar Sensitivity +", DM_FUNC_RADAR_PLUS, 0, "advanced"),
    "radar_minus": ToiletCommand("radar_minus", "Radar Sensitivity -", DM_FUNC_RADAR_MINUS, 0, "advanced"),
    "auto_close_plus": ToiletCommand("auto_close_plus", "Auto Close Delay +", DM_FUNC_AUTO_CLOSE_PLUS, 0, "advanced"),
    "auto_close_minus": ToiletCommand("auto_close_minus", "Auto Close Delay -", DM_FUNC_AUTO_CLOSE_MINUS, 0, "advanced"),

    # Toggles ON/OFF (vrais switches, codes distincts)
    "auto_flush_on": ToiletCommand("auto_flush_on", "Auto Flush On", DM_FUNC_AUTO_FLUSH_ON, 0, "advanced"),
    "auto_flush_off": ToiletCommand("auto_flush_off", "Auto Flush Off", DM_FUNC_AUTO_FLUSH_OFF, 0, "advanced"),
    "auto_foam_on": ToiletCommand("auto_foam_on", "Auto Foam On", DM_FUNC_AUTO_FOAM_ON, 0, "advanced"),
    "auto_foam_off": ToiletCommand("auto_foam_off", "Auto Foam Off", DM_FUNC_AUTO_FOAM_OFF, 0, "advanced"),
    "aging_mode_on": ToiletCommand("aging_mode_on", "Aging Mode On", DM_FUNC_AGING_MODE_ON, 0, "advanced"),
    "aging_mode_off": ToiletCommand("aging_mode_off", "Aging Mode Off", DM_FUNC_AGING_MODE_OFF, 0, "advanced"),
    "virtual_seat_on": ToiletCommand("virtual_seat_on", "Virtual Seat On", DM_FUNC_VIRTUAL_SEAT_ON, 0, "advanced"),
    "virtual_seat_off": ToiletCommand("virtual_seat_off", "Virtual Seat Off", DM_FUNC_VIRTUAL_SEAT_OFF, 0, "advanced"),
    "user_1_on": ToiletCommand("user_1_on", "User Preset 1 On", DM_FUNC_USER_1_ON, 0, "advanced"),
    "user_1_off": ToiletCommand("user_1_off", "User Preset 1 Off", DM_FUNC_USER_1_OFF, 0, "advanced"),
    "user_2_on": ToiletCommand("user_2_on", "User Preset 2 On", DM_FUNC_USER_2_ON, 0, "advanced"),
    "user_2_off": ToiletCommand("user_2_off", "User Preset 2 Off", DM_FUNC_USER_2_OFF, 0, "advanced"),
}


# ============================================================================
# DM-specific entity definitions
# ============================================================================

# Tous les boutons / actions ponctuelles → ButtonEntity (pas SwitchEntity)
# car le firmware ne renvoie aucun état, donc un toggle serait toujours faux.
DM_BUTTON_DEFINITIONS = [
    # Basic
    ("power", "Power", "power"),
    ("light", "Toilet Light", "light"),
    ("eco", "Energy Saving", "eco"),
    ("foam", "Foam Shield", "foam"),
    ("auto_mode", "Auto Mode", "auto_mode"),
    ("stop", "Stop All", "stop"),
    # Cleaning
    ("self_clean", "Self Clean", "self_clean"),
    ("flush", "Flush", "flush"),
    ("blow_dry", "Blow Dry", "blow_dry"),
    # Wash
    ("women_wash", "Women's Wash", "women_wash"),
    ("butt_wash", "Butt Wash", "butt_wash"),
    ("child_wash", "Child Wash", "child_wash"),
    ("massage", "Massage", "massage"),
    # Cover
    ("cover", "Toilet Cover", "cover"),
    ("ring", "Toilet Ring", "ring"),
    # Advanced +/-  (4ᵉ élément True = entity_category=config dans HA)
    ("lid_open_force_plus", "Lid Open Force +", "lid_open_force_plus", True),
    ("lid_open_force_minus", "Lid Open Force -", "lid_open_force_minus", True),
    ("lid_close_force_plus", "Lid Close Force +", "lid_close_force_plus", True),
    ("lid_close_force_minus", "Lid Close Force -", "lid_close_force_minus", True),
    ("ring_open_force_plus", "Ring Open Force +", "ring_open_force_plus", True),
    ("ring_open_force_minus", "Ring Open Force -", "ring_open_force_minus", True),
    ("ring_close_force_plus", "Ring Close Force +", "ring_close_force_plus", True),
    ("ring_close_force_minus", "Ring Close Force -", "ring_close_force_minus", True),
    ("volume_plus", "Volume +", "volume_plus", True),
    ("volume_minus", "Volume -", "volume_minus", True),
    ("flush_time_plus", "Flush Time +", "flush_time_plus", True),
    ("flush_time_minus", "Flush Time -", "flush_time_minus", True),
    ("radar_plus", "Radar Sensitivity +", "radar_plus", True),
    ("radar_minus", "Radar Sensitivity -", "radar_minus", True),
    ("auto_close_plus", "Auto Close Delay +", "auto_close_plus", True),
    ("auto_close_minus", "Auto Close Delay -", "auto_close_minus", True),
]

# Vrais switches : codes ON et OFF distincts → l'utilisateur garde le contrôle de l'état
# Tous sont des réglages avancés → is_config=True (rangés dans la section "Configuration" de HA)
DM_SWITCH_DEFINITIONS = [
    SwitchDefinition("auto_flush", "Auto Flush", "auto_flush_on", "auto_flush_off", is_config=True),
    SwitchDefinition("auto_foam", "Auto Foam", "auto_foam_on", "auto_foam_off", is_config=True),
    SwitchDefinition("aging_mode", "Aging Mode", "aging_mode_on", "aging_mode_off", is_config=True),
    SwitchDefinition("virtual_seat", "Virtual Seat", "virtual_seat_on", "virtual_seat_off", is_config=True),
    SwitchDefinition("user_1", "User Preset 1", "user_1_on", "user_1_off", is_config=True),
    SwitchDefinition("user_2", "User Preset 2", "user_2_on", "user_2_off", is_config=True),
]

# Sliders DM (function code → level 0-5)
DM_NUMBER_DEFINITIONS = [
    ("seat_temp", "Seat Temperature", DM_FUNC_SEAT_TEMP, 0, 5, 1, "level"),
    ("water_temp", "Water Temperature", DM_FUNC_WATER_TEMP, 0, 5, 1, "level"),
    ("wind_temp", "Wind Temperature", DM_FUNC_WIND_TEMP, 0, 5, 1, "level"),
    ("pressure", "Water Pressure", DM_FUNC_WATER_PRESSURE, 0, 5, 1, "level"),
    ("position", "Nozzle Position", DM_FUNC_POSITION, 0, 5, 1, "level"),
]


# ============================================================================
# SKS PROTOCOL MODEL (com.sks.toilet v1.1.3)
# ============================================================================

SKS_TOILET_COMMANDS = {
    "stop": ToiletCommand("stop", "Stop All", SKS_FUNC_BUTTON, 5, "basic"),
    "foam_on": ToiletCommand("foam_on", "Foam Shield On", SKS_FUNC_BUTTON, 28, "basic"),
    "foam_off": ToiletCommand("foam_off", "Foam Shield Off", SKS_FUNC_BUTTON, 28, "basic"),
    "self_clean": ToiletCommand("self_clean", "Self Clean", SKS_FUNC_BUTTON, 17, "cleaning"),
    "butt_wash": ToiletCommand("butt_wash", "Butt Wash", SKS_FUNC_BUTTON, 9, "wash"),
    "women_wash": ToiletCommand("women_wash", "Women's Wash", SKS_FUNC_BUTTON, 11, "wash"),
    "child_wash": ToiletCommand("child_wash", "Child Wash", SKS_FUNC_BUTTON, 31, "wash"),
    "assisted_wash": ToiletCommand("assisted_wash", "Assisted Wash", SKS_FUNC_BUTTON, 30, "wash"),
    "one_click_clean": ToiletCommand("one_click_clean", "One-Click Clean", SKS_FUNC_BUTTON, 10, "wash"),
    "moving_wash": ToiletCommand("moving_wash", "Moving Wash", SKS_FUNC_BUTTON, 32, "wash"),
    "massage": ToiletCommand("massage", "Massage", SKS_FUNC_BUTTON, 20, "wash"),
    "water_pattern": ToiletCommand("water_pattern", "Water Pattern Change", SKS_FUNC_BUTTON, 58, "wash"),
    "flush": ToiletCommand("flush", "Full Flush", SKS_FUNC_BUTTON, 2, "cleaning"),
    "small_flush": ToiletCommand("small_flush", "Small Flush", SKS_FUNC_BUTTON, 4, "cleaning"),
    "dry_on": ToiletCommand("dry_on", "Blow Dry On", SKS_FUNC_BUTTON, 15, "cleaning"),
    "dry_off": ToiletCommand("dry_off", "Blow Dry Off", SKS_FUNC_BUTTON, 15, "cleaning"),
    "cover_open": ToiletCommand("cover_open", "Cover Open", SKS_FUNC_BUTTON, 35, "cover"),
    "cover_close": ToiletCommand("cover_close", "Cover Close", SKS_FUNC_BUTTON, 35, "cover"),
    "ring_open": ToiletCommand("ring_open", "Ring Open", SKS_FUNC_BUTTON, 36, "cover"),
    "ring_close": ToiletCommand("ring_close", "Ring Close", SKS_FUNC_BUTTON, 36, "cover"),
    "night_light": ToiletCommand("night_light", "Night Light", SKS_FUNC_BUTTON, 34, "basic"),
    "ambient_light": ToiletCommand("ambient_light", "Ambient Light", SKS_FUNC_BUTTON, 33, "basic"),
    "aromatherapy": ToiletCommand("aromatherapy", "Aromatherapy", SKS_FUNC_BUTTON, 42, "basic"),
    "sterilization": ToiletCommand("sterilization", "Sterilization", SKS_FUNC_BUTTON, 47, "basic"),
    "infrared_therapy": ToiletCommand("infrared_therapy", "Infrared Therapy", SKS_FUNC_BUTTON, 45, "basic"),
    "user_1": ToiletCommand("user_1", "User Preset 1", SKS_FUNC_BUTTON, 48, "basic"),
    "user_2": ToiletCommand("user_2", "User Preset 2", SKS_FUNC_BUTTON, 50, "basic"),
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

SKS_SWITCH_DEFINITIONS = [
    SwitchDefinition("foam", "Foam Shield", "foam_on", "foam_off", has_state=False),
    SwitchDefinition("dry", "Blow Dry", "dry_on", "dry_off", has_state=False),
    SwitchDefinition("cover", "Toilet Cover", "cover_open", "cover_close", has_state=False),
    SwitchDefinition("ring", "Toilet Ring", "ring_open", "ring_close", has_state=False),
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
    ("butt_wash", "Butt Wash", "butt_wash"),
    ("women_wash", "Women's Wash", "women_wash"),
    ("child_wash", "Child Wash", "child_wash"),
    ("assisted_wash", "Assisted Wash", "assisted_wash"),
    ("one_click_clean", "One-Click Clean", "one_click_clean"),
    ("moving_wash", "Moving Wash", "moving_wash"),
    ("massage", "Massage", "massage"),
    ("water_pattern", "Water Pattern", "water_pattern"),
    ("night_light", "Night Light", "night_light"),
    ("ambient_light", "Ambient Light", "ambient_light"),
    ("aromatherapy", "Aromatherapy", "aromatherapy"),
    ("sterilization", "Sterilization", "sterilization"),
    ("infrared_therapy", "Infrared Therapy", "infrared_therapy"),
]

SKS_NUMBER_DEFINITIONS = [
    # Contrôles (8e élément non-fourni → False)
    ("position", "Nozzle Position", 7, 0, 4, 1, "level"),
    ("pressure", "Water Pressure", 13, 0, 2, 1, "level"),
    ("seat_temp", "Seat Temperature", 22, 0, 2, 1, "level"),
    ("water_temp", "Water Temperature", 19, 0, 2, 1, "level"),
    ("wind_temp", "Wind Temperature", 23, 0, 2, 1, "level"),
    ("wind_speed", "Wind Speed", 57, 0, 4, 1, "level"),
    # Réglages (8e élément True = config)
    ("radar_level", "Radar Level", 28, 1, 5, 1, "level", True),
    ("flush_level", "Flush Level", 29, 1, 5, 1, "level", True),
    ("cover_force", "Cover Force", 30, 1, 5, 1, "level", True),
    ("ring_force", "Ring Force", 31, 1, 5, 1, "level", True),
    ("post_leave_flush_time", "Post-Leave Flush Time", 32, 3, 60, 1, "s", True),
    ("auto_close_delay", "Auto Close Delay", 33, 1, 5, 1, "level", True),
]


# ============================================================================
# TOILET MODELS REGISTRY
# ============================================================================

TOILET_MODELS: dict[str, ToiletModel] = {
    "dm_smart_toilet": ToiletModel(
        id="dm_smart_toilet",
        name="DM Smart Toilet",
        description="DM-Toilet-Control protocol (fixed 8-byte packets, header 0xAA)",
        commands=DM_SMART_TOILET_COMMANDS,
        features=["light", "rgb", "wash", "cover", "flush", "blow_dry",
                  "auto_flush", "auto_foam", "aging_mode", "virtual_seat",
                  "user_presets", "advanced_settings", "light_mode"],
        manufacturer="DM",
        protocol=PROTOCOL_DM,
        switch_definitions=DM_SWITCH_DEFINITIONS,
        button_definitions=DM_BUTTON_DEFINITIONS,
        number_definitions=DM_NUMBER_DEFINITIONS,
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

DEFAULT_MODEL = "dm_smart_toilet"


# ============================================================================
# SLIDER FUNCTION → KEY MAP (used to remember last-set values)
# ============================================================================

DM_SLIDER_FUNCTION_TO_KEY = {
    DM_FUNC_SEAT_TEMP: "seat_temp",
    DM_FUNC_WATER_TEMP: "water_temp",
    DM_FUNC_WIND_TEMP: "wind_temp",
    DM_FUNC_WATER_PRESSURE: "pressure",
    DM_FUNC_POSITION: "position",
}

SKS_SLIDER_FUNCTION_TO_KEY = {
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


# Temperature/pressure shortcuts (for service calls)
TEMP_FUNCTIONS = {
    "seat": DM_FUNC_SEAT_TEMP,
    "water": DM_FUNC_WATER_TEMP,
    "wind": DM_FUNC_WIND_TEMP,
}
PRESSURE_FUNCTION = DM_FUNC_WATER_PRESSURE
POSITION_FUNCTION = DM_FUNC_POSITION

MIN_LEVEL = 0
MAX_LEVEL = 5

# Entity icons
ICONS = {
    "light": "mdi:lightbulb",
    "power": "mdi:power",
    "eco": "mdi:leaf",
    "foam": "mdi:chart-bubble",
    "auto_mode": "mdi:autorenew",
    "women_wash": "mdi:shower",
    "butt_wash": "mdi:water",
    "child_wash": "mdi:baby-carriage",
    "massage": "mdi:spa",
    "blow_dry": "mdi:hair-dryer",
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
    "auto_flush": "mdi:water-sync",
    "auto_foam": "mdi:chart-bubble",
    "aging_mode": "mdi:cog-outline",
    "virtual_seat": "mdi:seat",
    "user_1": "mdi:account",
    "user_2": "mdi:account-outline",
    "lid_open_force_plus": "mdi:plus",
    "lid_open_force_minus": "mdi:minus",
    "lid_close_force_plus": "mdi:plus",
    "lid_close_force_minus": "mdi:minus",
    "ring_open_force_plus": "mdi:plus",
    "ring_open_force_minus": "mdi:minus",
    "ring_close_force_plus": "mdi:plus",
    "ring_close_force_minus": "mdi:minus",
    "volume_plus": "mdi:volume-plus",
    "volume_minus": "mdi:volume-minus",
    "flush_time_plus": "mdi:plus",
    "flush_time_minus": "mdi:minus",
    "radar_plus": "mdi:plus",
    "radar_minus": "mdi:minus",
    "auto_close_plus": "mdi:plus",
    "auto_close_minus": "mdi:minus",
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


# Default fallbacks (used if a model doesn't override)
SWITCH_DEFINITIONS = DM_SWITCH_DEFINITIONS
BUTTON_DEFINITIONS = DM_BUTTON_DEFINITIONS
NUMBER_DEFINITIONS = DM_NUMBER_DEFINITIONS
SENSOR_DEFINITIONS = [
    ("connection", "Connection Status", "connection", None, None, None),
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model(model_id: str | None = None) -> ToiletModel:
    if model_id and model_id in TOILET_MODELS:
        return TOILET_MODELS[model_id]
    return TOILET_MODELS[DEFAULT_MODEL]


def get_model_commands(model_id: str | None = None) -> dict[str, ToiletCommand]:
    return get_model(model_id).commands


def get_model_features(model_id: str | None = None) -> list[str]:
    return get_model(model_id).features


def get_model_switch_definitions(model_id: str | None = None) -> list[SwitchDefinition]:
    model = get_model(model_id)
    return model.switch_definitions if model.switch_definitions is not None else SWITCH_DEFINITIONS


def get_model_button_definitions(model_id: str | None = None) -> list[tuple]:
    model = get_model(model_id)
    return model.button_definitions if model.button_definitions is not None else BUTTON_DEFINITIONS


def get_model_number_definitions(model_id: str | None = None) -> list[tuple]:
    model = get_model(model_id)
    return model.number_definitions if model.number_definitions is not None else NUMBER_DEFINITIONS


def command_exists(command_name: str, model_id: str | None = None) -> bool:
    return command_name in get_model_commands(model_id)
