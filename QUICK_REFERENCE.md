# Smart Toilet BLE - Quick Reference Card

## Supported Protocols

| Protocol | Header | Format | Used by |
|----------|--------|--------|---------|
| DM | `0xAA` | Fixed 8 bytes | DM Smart Toilet |
| SKS | `0x33` | Variable length | SKS Smart Toilet |

---

## DM Protocol

### Command Format
```
[0xAA] [0x08] [TYPE] [FUNCTION] [PARAM1] [PARAM2] [PARAM3] [CHECKSUM]
```
- Type `0x02` = Toilet, `0x03` = Ambient light
- Checksum = sum of bytes 0-6 mod 256

### Basic Controls (type=0x02)
| Action | Function | Param1 | Hex |
|--------|----------|--------|-----|
| Light ON | `0x01` | `0x01` | `AA 08 02 01 01 00 00 B6` |
| Light OFF | `0x01` | `0x00` | `AA 08 02 01 00 00 00 B5` |
| Power ON | `0x02` | `0x01` | `AA 08 02 02 01 00 00 B7` |
| Power OFF | `0x02` | `0x00` | `AA 08 02 02 00 00 00 B6` |
| ECO ON | `0x03` | `0x01` | `AA 08 02 03 01 00 00 B8` |
| Foam ON | `0x04` | `0x01` | `AA 08 02 04 01 00 00 B9` |
| STOP | `0x05` | `0x00` | `AA 08 02 05 00 00 00 B9` |
| Auto ON | `0x06` | `0x01` | `AA 08 02 06 01 00 00 BB` |
| Self Clean | `0x07` | `0x01` | `AA 08 02 07 01 00 00 BC` |

### Washing (type=0x02)
| Action | Function | Hex |
|--------|----------|-----|
| Women's Wash | `0x10` | `AA 08 02 10 01 00 00 C5` |
| Butt Wash | `0x11` | `AA 08 02 11 01 00 00 C6` |
| Child Wash | `0x12` | `AA 08 02 12 01 00 00 C7` |
| Massage | `0x13` | `AA 08 02 13 01 00 00 C8` |

### Cover (type=0x02)
| Action | Function | Param1 | Hex |
|--------|----------|--------|-----|
| Cover OPEN | `0x20` | `0x01` | `AA 08 02 20 01 00 00 D5` |
| Cover CLOSE | `0x20` | `0x00` | `AA 08 02 20 00 00 00 D4` |
| Ring OPEN | `0x21` | `0x01` | `AA 08 02 21 01 00 00 D6` |
| Ring CLOSE | `0x21` | `0x00` | `AA 08 02 21 00 00 00 D5` |

### Cleaning (type=0x02)
| Action | Function | Hex |
|--------|----------|-----|
| Flush | `0x30` | `AA 08 02 30 01 00 00 E5` |
| Dry ON | `0x31` | `AA 08 02 31 01 00 00 E6` |
| Dry OFF | `0x31` | `AA 08 02 31 00 00 00 E5` |

### Levels (type=0x02)
| Control | Function | Range | Template |
|---------|----------|-------|----------|
| Seat Temp | `0x40` | 0-5 | `AA 08 02 40 [LVL] 00 00 [CS]` |
| Water Temp | `0x41` | 0-5 | `AA 08 02 41 [LVL] 00 00 [CS]` |
| Wind Temp | `0x42` | 0-5 | `AA 08 02 42 [LVL] 00 00 [CS]` |
| Pressure | `0x43` | 0-5 | `AA 08 02 43 [LVL] 00 00 [CS]` |
| Position | `0x44` | 0-5 | `AA 08 02 44 [LVL] 00 00 [CS]` |

### Advanced Settings (type=0x02)
| Control | Function | Range |
|---------|----------|-------|
| Lid Open Torque | `0x50` | 0-100 |
| Lid Close Torque | `0x51` | 0-100 |
| Ring Open Torque | `0x52` | 0-100 |
| Ring Close Torque | `0x53` | 0-100 |
| Volume | `0x54` | 0-100 |
| Flush Time | `0x55` | 0-100 |
| Radar Sensitivity | `0x56` | 0-10 |
| Auto Close Time | `0x57` | 0-100 |
| Auto Flush | `0x58` | 0/1 |
| Auto Foam | `0x59` | 0/1 |
| Auto Night Light | `0x5A` | 0/1 |
| Aging Mode | `0x5B` | 0/1 |
| Virtual Seat | `0x5C` | 0/1 |

### Ambient Light (type=0x03)
| Action | Function | Params | Template |
|--------|----------|--------|----------|
| Light ON | `0x01` | 1 | `AA 08 03 01 01 00 00 B7` |
| Light OFF | `0x01` | 0 | `AA 08 03 01 00 00 00 B6` |
| RGB Color | `0x02` | R,G,B | `AA 08 03 02 [R] [G] [B] [CS]` |
| Mode | `0x03` | 0-6 | `AA 08 03 03 [MODE] 00 00 [CS]` |
| Brightness | `0x04` | 0-100 | `AA 08 03 04 [VAL] 00 00 [CS]` |

**Light Modes:** 0=Static, 1=Flashing, 2=Breathing, 3=Running Water, 4=Colorful Gradient, 5=Colorful Running, 6=Welcome

---

## SKS Protocol

### Command Format
```
[0x33] [FUNCTION] [PARAMS_LEN] [PARAMS...] [CHECKSUM]
```
- Checksum = sum of all preceding bytes mod 256

### Button Commands (function=0x02)
```
build_sks_command(0x02, [value, 0])
```
| Action | Value | Action | Value |
|--------|-------|--------|-------|
| Full Flush | 2 | Small Flush | 4 |
| Stop | 5 | Nozzle Pos+ | 7 |
| Butt Wash | 9 | One-Click Clean | 10 |
| Women's Wash | 11 | Pressure+ | 13 |
| Blow Dry | 15 | Self Clean | 17 |
| Water Temp | 19 | Massage | 20 |
| Seat Temp | 22 | Wind Temp | 23 |
| Foam Shield | 28 | Assisted Wash | 30 |
| Child Wash | 31 | Moving Wash | 32 |
| Ambient Light | 33 | Night Light | 34 |
| Cover | 35 | Ring | 36 |
| Aromatherapy | 42 | Infrared | 45 |
| Sterilization | 47 | User 1 | 48 |
| User 2 | 50 | Wind Speed | 57 |
| Water Pattern | 58 | | |

### Settings (function=0x04)
```
build_sks_command(0x04, [code, value])
```

**Switches (value=0/1):**

| Setting | Code | Setting | Code |
|---------|------|---------|------|
| Auto Aroma | 1 | Timed Aroma | 2 |
| Auto Ambient Light | 3 | Auto Foam | 4 |
| Auto Deodorizer | 5 | Flush on Leave | 6 |
| All-Season Heat | 7 | Position Cal. | 8 |
| Moisturize | 9 | Radar | 10 |
| Foot Sensor | 11 | Foot Sensor C/R | 12 |
| Energy Saving | 13 | Commercial | 14 |
| Buzzer | 15 | Display | 16 |
| Lid & Flush | 17 | Lid First Flush | 18 |
| Ceramic Sterilize | 19 | Nozzle Sterilize | 20 |
| Water Sterilize | 21 | Filter Reminder | 22 |
| Foam Reminder | 23 | Factory Reset | 24 |

**Sliders (value=level):**

| Setting | Code | Range |
|---------|------|-------|
| Radar Level | 28 | 1-5 |
| Flush Level | 29 | 1-5 |
| Cover Force | 30 | 1-5 |
| Ring Force | 31 | 1-5 |
| Post-Leave Flush | 32 | 3-60s |
| Auto Close Delay | 33 | 1-5 |

---

## BLE Connection

- **Service UUID**: `0000FFE0-0000-1000-8000-00805F9B34FB`
- **Write Characteristic**: `0000FFE1-0000-1000-8000-00805F9B34FB`
- **Read/Notify**: `0000FFE2-0000-1000-8000-00805F9B34FB`

## Checksum

```python
# DM
checksum = sum(bytes[0:7]) & 0xFF

# SKS
checksum = sum(all_preceding_bytes) & 0xFF
```
