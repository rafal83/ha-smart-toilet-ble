# Smart Toilet BLE Protocol - Quick Reference Card

## Protocol Summary
- **Packet Size**: 8 bytes
- **Sync Byte**: `0xAA`
- **Length**: `0x08`
- **Checksum**: Sum of bytes 0-6 modulo 256

## Command Format
```
[0xAA] [0x08] [TYPE] [FUNCTION] [PARAM1] [PARAM2] [PARAM3] [CHECKSUM]
  0      1      2       3         4         5         6         7
```

**Type Codes:**
- `0x02` = Toilet commands
- `0x03` = Ambient light commands

## Quick Command Reference

### Basic Controls
| Action | Function | Param1 | Command (hex) |
|--------|----------|--------|---------------|
| Light ON | `0x01` | `0x01` | `AA 08 02 01 01 00 00 B6` |
| Light OFF | `0x01` | `0x00` | `AA 08 02 01 00 00 00 B5` |
| Power ON | `0x02` | `0x01` | `AA 08 02 02 01 00 00 B7` |
| Power OFF | `0x02` | `0x00` | `AA 08 02 02 00 00 00 B6` |
| ECO ON | `0x03` | `0x01` | `AA 08 02 03 01 00 00 B8` |
| ECO OFF | `0x03` | `0x00` | `AA 08 02 03 00 00 00 B7` |
| Foam ON | `0x04` | `0x01` | `AA 08 02 04 01 00 00 B9` |
| Foam OFF | `0x04` | `0x00` | `AA 08 02 04 00 00 00 B8` |
| STOP | `0x05` | `0x00` | `AA 08 02 05 00 00 00 B8` |
| Auto ON | `0x06` | `0x01` | `AA 08 02 06 01 00 00 BB` |
| Auto OFF | `0x06` | `0x00` | `AA 08 02 06 00 00 00 BA` |
| Self Clean | `0x07` | `0x01` | `AA 08 02 07 01 00 00 BC` |

### Washing Functions
| Action | Function | Param1 | Command (hex) |
|--------|----------|--------|---------------|
| Women's Wash | `0x10` | `0x01` | `AA 08 02 10 01 00 00 C9` |
| Butt Wash | `0x11` | `0x01` | `AA 08 02 11 01 00 00 CA` |
| Child Wash | `0x12` | `0x01` | `AA 08 02 12 01 00 00 CB` |
| Massage | `0x13` | `0x01` | `AA 08 02 13 01 00 00 CC` |

### Cover Controls
| Action | Function | Param1 | Command (hex) |
|--------|----------|--------|---------------|
| Cover OPEN | `0x20` | `0x01` | `AA 08 02 20 01 00 00 D9` |
| Cover CLOSE | `0x20` | `0x00` | `AA 08 02 20 00 00 00 D8` |
| Ring OPEN | `0x21` | `0x01` | `AA 08 02 21 01 00 00 DA` |
| Ring CLOSE | `0x21` | `0x00` | `AA 08 02 21 00 00 00 D9` |

### Cleaning Functions
| Action | Function | Param1 | Command (hex) |
|--------|----------|--------|---------------|
| Flush | `0x30` | `0x01` | `AA 08 02 30 01 00 00 E9` |
| Dry ON | `0x31` | `0x01` | `AA 08 02 31 01 00 00 EA` |
| Dry OFF | `0x31` | `0x00` | `AA 08 02 31 00 00 00 E9` |

### Temperature Controls (levels 0-5)
| Action | Function | Level | Command Template |
|--------|----------|-------|------------------|
| Seat Temp | `0x40` | 0-5 | `AA 08 02 40 [LVL] 00 00 [CS]` |
| Water Temp | `0x41` | 0-5 | `AA 08 02 41 [LVL] 00 00 [CS]` |
| Wind Temp | `0x42` | 0-5 | `AA 08 02 42 [LVL] 00 00 [CS]` |
| Pressure | `0x43` | 0-5 | `AA 08 02 43 [LVL] 00 00 [CS]` |
| Position | `0x44` | 0-5 | `AA 08 02 44 [LVL] 00 00 [CS]` |

**Examples:**
- Seat Temp Level 3: `AA 08 02 40 03 00 00 F6`
- Water Temp Level 5: `AA 08 02 41 05 00 00 F8`

### Advanced Settings
| Action | Function | Values | Command Template |
|--------|----------|--------|------------------|
| Lid Open Torque | `0x50` | 0-100 | `AA 08 02 50 [VAL] 00 00 [CS]` |
| Lid Close Torque | `0x51` | 0-100 | `AA 08 02 51 [VAL] 00 00 [CS]` |
| Ring Open Torque | `0x52` | 0-100 | `AA 08 02 52 [VAL] 00 00 [CS]` |
| Ring Close Torque | `0x53` | 0-100 | `AA 08 02 53 [VAL] 00 00 [CS]` |
| Volume | `0x54` | 0-100 | `AA 08 02 54 [VAL] 00 00 [CS]` |
| Flush Time | `0x55` | 0-100 | `AA 08 02 55 [VAL] 00 00 [CS]` |
| Radar Sensitivity | `0x56` | 0-10 | `AA 08 02 56 [VAL] 00 00 [CS]` |
| Auto Close Time | `0x57` | 0-100 | `AA 08 02 57 [VAL] 00 00 [CS]` |
| Auto Flush | `0x58` | 0/1 | `AA 08 02 58 [0/1] 00 00 [CS]` |
| Auto Foam | `0x59` | 0/1 | `AA 08 02 59 [0/1] 00 00 [CS]` |
| Auto Night Light | `0x5A` | 0/1 | `AA 08 02 5A [0/1] 00 00 [CS]` |
| Aging Mode | `0x5B` | 0/1 | `AA 08 02 5B [0/1] 00 00 [CS]` |
| Virtual Seat | `0x5C` | 0/1 | `AA 08 02 5C [0/1] 00 00 [CS]` |
| Reserved 1 | `0x5D` | 0/1 | `AA 08 02 5D [0/1] 00 00 [CS]` |
| Reserved 2 | `0x5E` | 0/1 | `AA 08 02 5E [0/1] 00 00 [CS]` |

### Ambient Light Controls
| Action | Function | Params | Command Template |
|--------|----------|--------|------------------|
| Light ON/OFF | `0x01` | 0/1 | `AA 08 03 01 [0/1] 00 00 [CS]` |
| RGB Color | `0x02` | R,G,B | `AA 08 03 02 [R] [G] [B] [CS]` |
| Mode | `0x03` | 0-6 | `AA 08 03 03 [MODE] 00 00 [CS]` |
| Brightness | `0x04` | 0-100 | `AA 08 03 04 [VAL] 00 00 [CS]` |

**Light Modes:**
- `0x00` = Static
- `0x01` = Flashing
- `0x02` = Breathing
- `0x03` = Running Water
- `0x04` = Colorful Gradient
- `0x05` = Colorful Running
- `0x06` = Welcome

**Examples:**
- Light ON: `AA 08 03 01 01 00 00 B7`
- RGB Red (255,0,0): `AA 08 03 02 FF 00 00 17`
- RGB Blue (0,0,255): `AA 08 03 02 00 00 FF 14`
- Breathing Mode: `AA 08 03 03 02 00 00 BA`
- Brightness 50%: `AA 08 03 04 32 00 00 E7`

## BLE Connection Details

### Typical UUIDs
- **Service**: `0000FFE0-0000-1000-8000-00805F9B34FB`
- **Write**: `0000FFE1-0000-1000-8000-00805F9B34FB`
- **Read/Notify**: `0000FFE2-0000-1000-8000-00805F9B34FB`

### Connection Steps
1. Enable BLE adapter
2. Scan for devices
3. Connect to toilet MAC address
4. Discover services
5. Enable notifications (optional)
6. Write commands to write characteristic

## Checksum Calculation

```python
def calc_checksum(cmd_bytes):
    return sum(cmd_bytes) & 0xFF
```

**Example:**
```
Command: AA 08 02 01 01 00 00
Sum: 0xAA + 0x08 + 0x02 + 0x01 + 0x01 + 0x00 + 0x00 = 0xB6
Checksum: 0xB6
Full packet: AA 08 02 01 01 00 00 B6
```

## Python One-Liner

```python
# Generate command: python -c "cmd=[0xAA,0x08,0x02,0x01,0x01,0,0]; cmd.append(sum(cmd)&0xFF); print(' '.join(f'{b:02X}' for b in cmd))"
```

## ESPHome Lambda Template

```cpp
std::vector<uint8_t> cmd = {0xAA, 0x08, 0x02, FUNCTION, PARAM1, PARAM2, PARAM3};
uint8_t checksum = 0;
for (auto b : cmd) checksum += b;
cmd.push_back(checksum);
return cmd;
```

## Home Assistant Shell Command

```bash
# Example: Turn on light
echo -ne '\xAA\x08\x02\x01\x01\x00\x00\xB6' | gatttool -b XX:XX:XX:XX:XX:XX --char-write-req --handle=0x00XX --value=-
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Can't connect | Check MAC address, ensure toilet is in BLE mode |
| Commands fail | Verify UUIDs, check checksum calculation |
| Intermittent | Move closer, check BLE interference |
| No response | Enable notifications, check if toilet supports status |

## Files Provided

1. `BLE_PROTOCOL_DOCUMENTATION.md` - Complete protocol documentation
2. `home_assistant_native_ble.md` - Native HA integration guide
3. `esphome_ble_bridge.md` - ESPHome bridge configuration
4. `QUICK_REFERENCE.md` - This file

## Next Steps

1. Find your toilet's MAC address
2. Test commands manually
3. Choose integration method (Native HA or ESPHome)
4. Configure Home Assistant
5. Create dashboard
6. Add automations

Good luck with your smart toilet integration! 🚽
