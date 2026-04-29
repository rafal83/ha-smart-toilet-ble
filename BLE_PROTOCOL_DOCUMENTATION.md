# Smart Toilet BLE Protocol Documentation

## Overview

This document describes the two BLE protocols supported by this integration. The **DM** protocol codes were
reverse-engineered from the official `DM Toilet Control v1.0.6` Android app (uni-app bundle in
`assets/apps/__UNI__EFE4A4C/www/app-service.js`). Earlier versions of this document contained
incorrect function codes — they have been corrected.

## Supported Protocols

| Protocol | App | Header | Packet Size | Checksum |
|----------|-----|--------|-------------|----------|
| **DM** | DM-Toilet-Control v1.0.6 | `0xAA` | Fixed 8 bytes | Sum of bytes 0-6 mod 256 |
| **SKS** | com.sks.toilet v1.1.3 | `0x33` | Variable length | Sum of all bytes mod 256 |

---

## DM Protocol (DM Smart Toilet)

### Command Structure

All commands are **8 bytes**:

| Byte 0 | Byte 1 | Byte 2 | Byte 3 | Byte 4 | Byte 5 | Byte 6 | Byte 7 |
|--------|--------|--------|--------|--------|--------|--------|--------|
| `0xAA` (sync) | `0x08` (length) | Type | Function | Param1 | Param2 | Param3 | Checksum |

**Type codes:**
- `0x02` = Toilet control commands
- `0x03` = Ambient light commands

### How the official app builds frames

The app exposes two helpers:

```js
// Toilet (type 0x02)
createCommond(value, p1, p2, p3) → [0xAA, 0x08, 0x02, value, p1, p2, p3, sum]

// Ambient light (type 0x03)
createAmbientLightCommond(value, p1, p2, p3) → [0xAA, 0x08, 0x03, value, p1, p2, p3, sum]
```

For toilet commands, the app calls `sendCommand(key, value)` where `value` is the function code below.
The 3 params carried are NOT a level for action buttons — they are the **current temperatures**
(water/wind/seat), sent as a piggyback state. For sliders (`shuiya`, `guanwei`) the params are
overridden with `[level, 0, 0]`.

In the integration we send `[level, 0, 0]` for sliders and `[0, 0, 0]` for action buttons — both work,
the firmware only looks at the function code (byte 3) for actions.

### Toilet Function Codes (type=0x02)

#### Action Buttons (param1 ignored)

These are **single-shot actions**. The official app sends them with the 3 piggyback temps in params,
but the firmware only reads the function code.

| Action | Code (dec) | Code (hex) | App key |
|--------|------------|------------|---------|
| Women's Wash | 1 | `0x01` | fuxi |
| Butt Wash | 2 | `0x02` | tunxi |
| Child Wash | 3 | `0x03` | tongxi |
| Blow Dry | 4 | `0x04` | chuifeng |
| Cover (toggle) | 5 | `0x05` | fangai |
| Ring (toggle) | 6 | `0x06` | fanquan |
| Flush | 7 | `0x07` | chongshui |
| Auto Mode | 8 | `0x08` | zidong |
| Stop All | 9 | `0x09` | stop |
| Power | 14 | `0x0E` | power |
| Toilet Light | 15 | `0x0F` | light |
| Self Clean | 17 | `0x11` | zijie |
| Foam Shield | 18 | `0x12` | paomou |
| Energy Saving | 19 | `0x13` | jieneng |
| Massage | 20 | `0x14` | anmo |

#### Sliders (param1 = level, 0-5)

| Control | Code (dec) | Code (hex) | App key |
|---------|------------|------------|---------|
| Water Temperature | 16 | `0x10` | shuiwen |
| Wind Temperature | 32 | `0x20` | fengwen |
| Water Pressure | 33 | `0x21` | shuiya |
| Nozzle Position | 34 | `0x22` | guanwei |
| Seat Temperature | 48 | `0x30` | zuowen |

#### Settings: pairs of +/- codes

These are stateless increment/decrement actions — the firmware keeps an internal level and only the
delta is sent.

| Setting | + (jia) | − (jian) |
|---------|---------|----------|
| Lid Open Force | 65 (`0x41`) | 66 (`0x42`) |
| Lid Close Force | 81 (`0x51`) | 82 (`0x52`) |
| Ring Open Force | 97 (`0x61`) | 98 (`0x62`) |
| Ring Close Force | 113 (`0x71`) | 114 (`0x72`) |
| Volume | 129 (`0x81`) | 130 (`0x82`) |
| Flush Time | 145 (`0x91`) | 146 (`0x92`) |
| Radar Sensitivity | 177 (`0xB1`) | 178 (`0xB2`) |
| Auto Close Delay | 209 (`0xD1`) | 210 (`0xD2`) |

#### Toggles: distinct ON/OFF codes

| Toggle | ON | OFF |
|--------|----|----|
| Auto Flush | 193 (`0xC1`) | 194 (`0xC2`) |
| Auto Foam | 225 (`0xE1`) | 226 (`0xE2`) |
| Aging Mode | 241 (`0xF1`) | 242 (`0xF2`) |
| Virtual Seat | 70 (`0x46`) | 71 (`0x47`) |
| User Preset 1 | 243 (`0xF3`) | 244 (`0xF4`) |
| User Preset 2 | 245 (`0xF5`) | 246 (`0xF6`) |

### Ambient Light Commands (type=0x03)

The DM app sends the **entire light state in a single frame**:

```
[0xAA, 0x08, 0x03, mode | 0x80(if on), R*lightness/100, G*lightness/100, B*lightness/100, sum]
```

- Bit 7 of byte 3 (`0x80`) = light enabled. Without it = light OFF.
- `mode` (low 7 bits): effect mode
- Params 1-3 = RGB values pre-multiplied by the lightness percentage (0-100)

#### Light Modes

| Mode | Value | App key |
|------|-------|---------|
| Static | 1 | jingtai |
| Flashing | 2 | shanshuo |
| Breathing | 3 | huxi |
| Running Water | 4 | liushui |
| Colorful Running | 5 | qicailiushui |
| Colorful Gradient | 6 | qicaijianbian |
| Welcome | 7 | yingbin |
| Off | 0 | guandeng |

### DM Command Examples

```python
# Flush
[0xAA, 0x08, 0x02, 7, 0, 0, 0, 0xBB]

# Set seat temperature to level 3
[0xAA, 0x08, 0x02, 48, 3, 0, 0, 0x05]

# Set water pressure to level 4
[0xAA, 0x08, 0x02, 33, 4, 0, 0, 0xD9]

# Volume up (+1)
[0xAA, 0x08, 0x02, 129, 0, 0, 0, 0x35]

# Auto Flush ON
[0xAA, 0x08, 0x02, 193, 0, 0, 0, 0x75]

# Ambient light: static white at 50%
[0xAA, 0x08, 0x03, 0x81, 127, 127, 127, 0xB3]

# Ambient light: OFF
[0xAA, 0x08, 0x03, 0, 0, 0, 0, 0xB5]
```

---

## SKS Protocol (com.sks.toilet)

### Command Structure

Variable-length packets:

| Byte 0 | Byte 1 | Byte 2 | Byte 3..N | Byte N+1 |
|--------|--------|--------|-----------|----------|
| `0x33` (sync) | Function | Params Length | Params... | Checksum |

**Response header (incoming notify frames):** `0x55`

### Command Generation

```python
def build_sks_command(function, params=None):
    if params is None:
        params = []
    cmd = [0x33, function, len(params)] + params
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)
```

### Function Categories

- `0x02` (byte1=2): Button/action commands — `build_sks_command(0x02, [value, 0])`
- `0x04` (byte1=4): Settings commands — `build_sks_command(0x04, [code, value])`
- `0x33` (byte1=51): Query commands
- `0x05`: Register read
- `0x06`: Register write

### Button Commands (function=0x02)

| Action | Value | Action | Value |
|--------|-------|--------|-------|
| Full Flush | 2 | Small Flush | 4 |
| Stop | 5 | Nozzle Pos+ | 7 |
| Nozzle Pos- | 8 | Butt Wash | 9 |
| One-Click Clean | 10 | Women's Wash | 11 |
| Pressure+ | 13 | Pressure- | 14 |
| Blow Dry | 15 | Self Clean | 17 |
| Water Temp | 19 | Massage | 20 |
| Seat Temp | 22 | Wind Temp | 23 |
| Foam Shield | 28 | Assisted Wash | 30 |
| Child Wash | 31 | Moving Wash | 32 |
| Ambient Light | 33 | Night Light | 34 |
| Cover | 35 | Ring | 36 |
| Aromatherapy | 42 | Infrared Therapy | 45 |
| Sterilization | 47 | User 1 | 48 |
| User 2 | 50 | Wind Speed | 57 |
| Water Pattern | 58 | | |

### Settings Commands (function=0x04)

#### Switches (code, value=0/1)

| Setting | Code | Setting | Code |
|---------|------|---------|------|
| Auto Aroma | 1 | Timed Aroma | 2 |
| Auto Ambient Light | 3 | Auto Foam | 4 |
| Auto Deodorizer | 5 | Flush on Leave | 6 |
| All-Season Heating | 7 | Position Calibration | 8 |
| Moisturize | 9 | Radar | 10 |
| Foot Sensor | 11 | Foot Sensor Cover/Ring | 12 |
| Energy Saving | 13 | Commercial Mode | 14 |
| Buzzer | 15 | Display | 16 |
| Close Lid & Flush | 17 | Lid First Then Flush | 18 |
| Auto Ceramic Sterilize | 19 | Auto Nozzle Sterilize | 20 |
| Auto Water Sterilize | 21 | Filter Reminder | 22 |
| Foam Liquid Reminder | 23 | Factory Reset | 24 |
| Open Ring Foam | 25 | | |

#### Sliders (code, value=level)

| Setting | Code | Range |
|---------|------|-------|
| Radar Level | 28 | 1-5 |
| Flush Level | 29 | 1-5 |
| Cover Force | 30 | 1-5 |
| Ring Force | 31 | 1-5 |
| Post-Leave Flush Time | 32 | 3-60s |
| Auto Close Delay | 33 | 1-5 |

### SKS Data Parsing (incoming frames, header=0x55)

The SKS firmware sends back state with packed bitfields:

```
Function 1/2: Main data
  byte[0] bits 4-7: water_temp, bits 0-3: seat_temp
  byte[1] bits 4-7: wind_temp,  bits 0-3: water_pressure
  byte[2] bits 4-7: nozzle_pos, bits 0-3: wind_speed

Function 3:   Settings data (packed booleans + levels)
Function 160: UI configuration (which features are available)
```

The integration parses these in `_parse_sks_frame()` to populate sliders.

---

## BLE Connection Details

### UUIDs

The DM **app** uses a different service than what was originally documented. In practice, devices in
the wild expose either set, so the integration tries the documented UUID first, then falls back to
the first writable characteristic found.

| Spec source | Service | Write | Notify |
|-------------|---------|-------|--------|
| Original spec | `0000FFE0-…` | `0000FFE1-…` | `0000FFE2-…` |
| DM app v1.0.6 | `0000FFA0-…` | `0000FFA1-…` | (none — app does not subscribe) |

### Connection Flow
1. Enable Bluetooth adapter
2. Discover the device by MAC (Home Assistant's `async_ble_device_from_address`)
3. Connect via `bleak-retry-connector.establish_connection`
4. Iterate services/characteristics, pick a writable one (preferring `FFE1`)
5. Subscribe to ALL notify-capable characteristics (so we don't miss anything)
6. Write commands

### About state feedback

**The DM firmware is unidirectional.** The official `DM Toilet Control v1.0.6` app does not contain
any call to `onBLECharacteristicValueChange`, `notifyBLECharacteristicValueChange`, or any read API.
It writes commands and never listens. Empirical testing confirms the WC does not push notifications
on the standard `FFE2` UUID either. As a consequence, this integration cannot know:

- Whether the toilet is currently powered on or off
- Whether a toggle (auto flush, foam, etc.) is currently enabled
- The current actual level of seat temperature, water pressure, etc., if changed via the physical
  remote

Switches use `assumed_state=True`, sliders display the last value sent from HA. SKS firmware does
push notifications and is parsed when received.
