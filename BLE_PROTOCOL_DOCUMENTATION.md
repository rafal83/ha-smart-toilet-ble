# Smart Toilet BLE Protocol Documentation

## Overview

This document describes the two BLE protocols supported by this integration, reverse-engineered from Android control apps.

## Supported Protocols

| Protocol | App | Header | Packet Size | Checksum |
|----------|-----|--------|-------------|----------|
| **DM** | DM-Toilet-Control v1.0.6 | `0xAA` | Fixed 8 bytes | Sum of bytes 0-6 mod 256 |
| **SKS** | com.sks.toilet v1.1.3 | `0x33` | Variable length | Sum of all bytes mod 256 |

---

## DM Protocol (DM Smart Toilet)

### Command Structure

All commands are **8 bytes** with the following format:

| Byte 0 | Byte 1 | Byte 2 | Byte 3 | Byte 4 | Byte 5 | Byte 6 | Byte 7 |
|--------|--------|--------|--------|--------|--------|--------|--------|
| `0xAA` (sync) | `0x08` (length) | Type | Function | Param1 | Param2 | Param3 | Checksum |

**Type codes:**
- `0x02` = Toilet control commands
- `0x03` = Ambient light commands

### Command Generation

```python
def build_dm_command(cmd_type, function, param1=0, param2=0, param3=0):
    cmd = [0xAA, 0x08, cmd_type, function, param1, param2, param3]
    cmd.append(sum(cmd) & 0xFF)
    return bytes(cmd)
```

### Toilet Control Functions (type=0x02)

#### Basic Controls
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Light | `0x01` | Toilet illumination | On/Off: 0x01/0x00 |
| Power | `0x02` | Main power | On/Off: 0x01/0x00 |
| ECO | `0x03` | Energy saving mode | On/Off: 0x01/0x00 |
| Foam | `0x04` | Foam shield | On/Off: 0x01/0x00 |
| Stop | `0x05` | Stop all operations | 0x00 |
| Auto Mode | `0x06` | Automatic mode | On/Off: 0x01/0x00 |
| Self Cleaning | `0x07` | Nozzle self-cleaning | 0x01 |

#### Washing Functions
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Women's Wash | `0x10` | Bidet wash | On: 0x01 |
| Butt Wash | `0x11` | Rear wash | On: 0x01 |
| Child Wash | `0x12` | Child wash | On: 0x01 |
| Massage | `0x13` | Massage mode | On: 0x01 |

#### Cover Controls
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Flip Cover | `0x20` | Toilet lid | Open: 0x01, Close: 0x00 |
| Flip Ring | `0x21` | Toilet ring | Open: 0x01, Close: 0x00 |

#### Cleaning Functions
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Flush | `0x30` | Flush | Activate: 0x01 |
| Blow Dry | `0x31` | Blow dry | On/Off: 0x01/0x00 |

#### Temperature & Level Controls
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Seat Temp | `0x40` | Seat temperature | Level 0-5 |
| Water Temp | `0x41` | Water temperature | Level 0-5 |
| Wind Temp | `0x42` | Air dryer temperature | Level 0-5 |
| Water Pressure | `0x43` | Water pressure | Level 0-5 |
| Nozzle Position | `0x44` | Nozzle position | Level 0-5 |

#### Advanced Settings
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Lid Open Torque | `0x50` | Lid open force | Value 0-100 |
| Lid Close Torque | `0x51` | Lid close force | Value 0-100 |
| Ring Open Torque | `0x52` | Ring open force | Value 0-100 |
| Ring Close Torque | `0x53` | Ring close force | Value 0-100 |
| Volume | `0x54` | Speaker volume | Value 0-100 |
| Flush Time | `0x55` | Flush duration | Value 0-100 |
| Radar Sensitivity | `0x56` | Presence sensor | Value 0-10 |
| Auto Close Time | `0x57` | Auto close delay | Value 0-100 |
| Auto Flush | `0x58` | Auto flush toggle | On/Off: 0x01/0x00 |
| Auto Foam | `0x59` | Auto foam toggle | On/Off: 0x01/0x00 |
| Auto Night Light | `0x5A` | Auto night light | On/Off: 0x01/0x00 |
| Aging Mode | `0x5B` | Aging mode | On/Off: 0x01/0x00 |
| Virtual Seat | `0x5C` | Virtual seat | On/Off: 0x01/0x00 |

### Ambient Light Commands (type=0x03)

| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Light On/Off | `0x01` | Main ambient light | On/Off: 0x01/0x00 |
| RGB Color | `0x02` | Set RGB color | R(0-255), G(0-255), B(0-255) |
| Mode | `0x03` | Light effect mode | Mode value (0x00-0x06) |
| Brightness | `0x04` | Light brightness | Value 0-100 |

**Light Modes:**

| Mode | Value | Description |
|------|-------|-------------|
| Static | `0x00` | Static color |
| Flashing | `0x01` | Flashing |
| Breathing | `0x02` | Breathing effect |
| Running Water | `0x03` | Running water |
| Colorful Gradient | `0x04` | Colorful gradient |
| Colorful Running | `0x05` | Colorful running |
| Welcome | `0x06` | Welcome mode |

### DM Command Examples

```python
# Turn on toilet light
[0xAA, 0x08, 0x02, 0x01, 0x01, 0x00, 0x00, 0xB6]

# Set seat temperature to level 3
[0xAA, 0x08, 0x02, 0x40, 0x03, 0x00, 0x00, 0xF6]

# Flush
[0xAA, 0x08, 0x02, 0x30, 0x01, 0x00, 0x00, 0xD6]

# Set ambient light to blue (RGB: 0, 0, 255)
[0xAA, 0x08, 0x03, 0x02, 0x00, 0x00, 0xFF, 0x14]

# Set brightness to 50%
[0xAA, 0x08, 0x03, 0x04, 0x32, 0x00, 0x00, 0xE7]

# Set breathing mode
[0xAA, 0x08, 0x03, 0x03, 0x02, 0x00, 0x00, 0xBA]
```

---

## SKS Protocol (com.sks.toilet)

### Command Structure

Variable-length packets:

| Byte 0 | Byte 1 | Byte 2 | Byte 3..N | Byte N+1 |
|--------|--------|--------|-----------|----------|
| `0x33` (sync) | Function | Params Length | Params... | Checksum |

**Response header:** `0x55`

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

- `0x02` (byte1=2): Button/action commands - `build_sks_command(0x02, [value, 0])`
- `0x04` (byte1=4): Settings commands - `build_sks_command(0x04, [code, value])`
- `0x33` (byte1=51): Query commands
- `0x05`: Register read
- `0x06`: Register write

### Button Commands (function=0x02)

| Action | Value | Description |
|--------|-------|-------------|
| Full Flush | 2 | Full flush |
| Small Flush | 4 | Small flush |
| Stop | 5 | Stop all |
| Nozzle Pos+ | 7 | Nozzle position up |
| Nozzle Pos- | 8 | Nozzle position down |
| Butt Wash | 9 | Rear wash |
| One-Click Clean | 10 | One-click clean |
| Women's Wash | 11 | Bidet wash |
| Water Pressure+ | 13 | Water pressure up |
| Water Pressure- | 14 | Water pressure down |
| Blow Dry | 15 | Blow dry toggle |
| Self Clean | 17 | Self clean |
| Water Temp | 19 | Water temperature cycle |
| Massage | 20 | Massage mode |
| Seat Temp | 22 | Seat temperature cycle |
| Wind Temp | 23 | Wind temperature cycle |
| Foam Shield | 28 | Foam shield toggle |
| Assisted Wash | 30 | Assisted wash |
| Child Wash | 31 | Child wash |
| Moving Wash | 32 | Moving wash |
| Ambient Light | 33 | Ambient light toggle |
| Night Light | 34 | Night light toggle |
| Cover | 35 | Cover toggle |
| Ring | 36 | Ring toggle |
| Aromatherapy | 42 | Aromatherapy toggle |
| Infrared Therapy | 45 | Infrared therapy toggle |
| Sterilization | 47 | Sterilization toggle |
| User Preset 1 | 48 | User preset 1 |
| User Preset 2 | 50 | User preset 2 |
| Wind Speed | 57 | Wind speed cycle |
| Water Pattern | 58 | Water pattern change |

### Settings Commands (function=0x04)

#### Switches (code, value=0/1)

| Setting | Code | Description |
|---------|------|-------------|
| Auto Aroma | 1 | Automatic aromatherapy |
| Timed Aroma | 2 | Timed aromatherapy |
| Auto Ambient Light | 3 | Auto ambient light |
| Auto Foam | 4 | Auto foam shield |
| Auto Deodorizer | 5 | Auto deodorizer |
| Flush on Leave | 6 | Flush when leaving seat |
| All-Season Heating | 7 | All-season seat heating |
| Position Calibration | 8 | Nozzle calibration |
| Moisturize | 9 | Moisturize function |
| Radar | 10 | Radar sensor on/off |
| Foot Sensor | 11 | Foot sensor on/off |
| Foot Sensor Cover/Ring | 12 | Foot sensor cover/ring mode |
| Energy Saving | 13 | Energy saving mode |
| Commercial Mode | 14 | Commercial mode |
| Buzzer | 15 | Buzzer on/off |
| Display | 16 | Display on/off |
| Close Lid & Flush | 17 | Close lid then flush |
| Lid First Then Flush | 18 | Lid first then flush |
| Auto Ceramic Sterilize | 19 | Auto ceramic sterilize |
| Auto Nozzle Sterilize | 20 | Auto nozzle sterilize |
| Auto Water Sterilize | 21 | Auto water sterilize |
| Filter Reminder | 22 | Filter replacement reminder |
| Foam Liquid Reminder | 23 | Foam liquid refill reminder |
| Factory Reset | 24 | Factory reset (confirm) |
| Open Ring Foam | 25 | Open ring foam |

#### Sliders (code, value=level)

| Setting | Code | Range | Description |
|---------|------|-------|-------------|
| Radar Level | 28 | 1-5 | Radar sensitivity |
| Flush Level | 29 | 1-5 | Flush intensity |
| Cover Force | 30 | 1-5 | Cover open/close force |
| Ring Force | 31 | 1-5 | Ring open/close force |
| Post-Leave Flush Time | 32 | 3-60s | Delay before auto flush |
| Auto Close Delay | 33 | 1-5 | Auto lid close delay |

### SKS Data Parsing (responses, header=0x55)

The device sends back status data with packed bitfields:

```
Function 1/2: Main data
  byte[0] bits 4-7: water_temp, bits 0-3: seat_temp
  byte[1] bits 4-7: wind_temp, bits 0-3: water_pressure
  byte[2] bits 4-7: nozzle_position, bits 0-3: wind_speed

Function 3: Settings data (packed booleans + levels)

Function 160 (0xA0): UI configuration (which features are available)
```

---

## BLE Connection Details

### UUIDs
- **Service UUID**: `0000FFE0-0000-1000-8000-00805F9B34FB`
- **Write Characteristic**: `0000FFE1-0000-1000-8000-00805F9B34FB`
- **Read/Notify Characteristic**: `0000FFE2-0000-1000-8000-00805F9B34FB`

### Connection Flow
1. Enable Bluetooth adapter
2. Start BLE device discovery
3. Connect to device by MAC address
4. Discover services and characteristics
5. Enable notifications on read characteristic
6. Write commands to write characteristic
