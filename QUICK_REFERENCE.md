# Smart Toilet BLE - Quick Reference Card

> ⚠️ The DM function codes below were corrected after reverse-engineering the official
> DM Toilet Control v1.0.6 app. Earlier versions of this card were wrong (used a different code
> family that some firmwares ignored silently).

## Supported Protocols

| Protocol | Header | Format | Used by |
|----------|--------|--------|---------|
| DM | `0xAA` | Fixed 8 bytes | DM Smart Toilet |
| SKS | `0x33` | Variable length | SKS Smart Toilet |

---

## DM Protocol

### Frame Format
```
[0xAA] [0x08] [TYPE] [FUNCTION] [PARAM1] [PARAM2] [PARAM3] [CHECKSUM]
```
- Type `0x02` = Toilet, `0x03` = Ambient light
- Checksum = sum of bytes 0–6 mod 256

### Action Buttons (type=0x02, params=0)

| Action | Function (dec) | Hex |
|--------|----|-----|
| Women's Wash | 1 | `AA 08 02 01 00 00 00 B5` |
| Butt Wash | 2 | `AA 08 02 02 00 00 00 B6` |
| Child Wash | 3 | `AA 08 02 03 00 00 00 B7` |
| Blow Dry | 4 | `AA 08 02 04 00 00 00 B8` |
| Cover (toggle) | 5 | `AA 08 02 05 00 00 00 B9` |
| Ring (toggle) | 6 | `AA 08 02 06 00 00 00 BA` |
| Flush | 7 | `AA 08 02 07 00 00 00 BB` |
| Auto Mode | 8 | `AA 08 02 08 00 00 00 BC` |
| Stop All | 9 | `AA 08 02 09 00 00 00 BD` |
| Power | 14 | `AA 08 02 0E 00 00 00 C2` |
| Toilet Light | 15 | `AA 08 02 0F 00 00 00 C3` |
| Self Clean | 17 | `AA 08 02 11 00 00 00 C5` |
| Foam Shield | 18 | `AA 08 02 12 00 00 00 C6` |
| Energy Saving | 19 | `AA 08 02 13 00 00 00 C7` |
| Massage | 20 | `AA 08 02 14 00 00 00 C8` |

### Sliders (type=0x02, param1=level 0–5)

| Control | Function (dec) | Template |
|---------|----|----------|
| Water Temp | 16 | `AA 08 02 10 [LVL] 00 00 [CS]` |
| Wind Temp | 32 | `AA 08 02 20 [LVL] 00 00 [CS]` |
| Water Pressure | 33 | `AA 08 02 21 [LVL] 00 00 [CS]` |
| Nozzle Position | 34 | `AA 08 02 22 [LVL] 00 00 [CS]` |
| Seat Temp | 48 | `AA 08 02 30 [LVL] 00 00 [CS]` |

### Adjustments +/− (stateless step)

| Setting | + | − |
|---------|---|---|
| Lid Open Force | 65 | 66 |
| Lid Close Force | 81 | 82 |
| Ring Open Force | 97 | 98 |
| Ring Close Force | 113 | 114 |
| Volume | 129 | 130 |
| Flush Time | 145 | 146 |
| Radar Sensitivity | 177 | 178 |
| Auto Close Delay | 209 | 210 |

### Toggles ON/OFF (distinct codes)

| Toggle | ON | OFF |
|--------|----|-----|
| Auto Flush | 193 | 194 |
| Auto Foam | 225 | 226 |
| Aging Mode | 241 | 242 |
| Virtual Seat | 70 | 71 |
| User Preset 1 | 243 | 244 |
| User Preset 2 | 245 | 246 |

### Ambient Light (type=0x03, single frame)

```
[AA] [08] [03] [MODE | 0x80(if ON)] [R*pct/100] [G*pct/100] [B*pct/100] [CS]
```

| Action | Frame |
|--------|-------|
| ON, Static, white 100% | `AA 08 03 81 FF FF FF B0` |
| ON, Static, white 50% | `AA 08 03 81 7F 7F 7F B3` |
| ON, Breathing, red 100% | `AA 08 03 83 FF 00 00 B5` |
| OFF | `AA 08 03 00 00 00 00 B5` |

**Light Modes (low 7 bits of byte 3):**
1=Static · 2=Flashing · 3=Breathing · 4=Running Water · 5=Colorful Running · 6=Colorful Gradient · 7=Welcome · 0=Off

---

## SKS Protocol

### Frame Format
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
| Radar Level | 28 | 1–5 |
| Flush Level | 29 | 1–5 |
| Cover Force | 30 | 1–5 |
| Ring Force | 31 | 1–5 |
| Post-Leave Flush | 32 | 3–60s |
| Auto Close Delay | 33 | 1–5 |

---

## BLE Connection

The DM app uses `0000FFA0`/`0000FFA1`. The original spec mentions `0000FFE0`/`0000FFE1`/`0000FFE2`.
Devices in the wild may expose either; the integration falls back to the first writable
characteristic found.

| Role | Spec UUID | DM-app UUID |
|------|-----------|-------------|
| Service | `0000FFE0-…` | `0000FFA0-…` |
| Write | `0000FFE1-…` | `0000FFA1-…` |
| Notify (DM firmware does NOT push) | `0000FFE2-…` | — |

## Checksum

```python
# DM
checksum = sum(bytes[0:7]) & 0xFF

# SKS
checksum = sum(all_preceding_bytes) & 0xFF
```

## State feedback

**DM**: none — firmware is write-only. Switches use `assumed_state=True`; sliders show the last
value sent from HA.

**SKS**: notifications on header `0x55` carry packed nibbles for the main controls; the integration
parses them in `_parse_sks_frame()`.
