# Smart Toilet BLE Protocol Documentation

## Overview
This document describes the BLE protocol used by the DM-Toilet-Control Android app (v1.0.6) to control Japanese smart toilets.

## App Information
- **App Name**: DM-Toilet-Control
- **Package**: `uni_UNIEFE4A4C_v1.0.6.apk`
- **Framework**: uni-app (Vue 3) with DCloud runtime
- **Kotlin Version**: 1.8.10

## BLE Protocol Specification

### Command Structure
All commands are **8 bytes** with the following format:

| Byte 0 | Byte 1 | Byte 2 | Byte 3 | Byte 4 | Byte 5 | Byte 6 | Byte 7 |
|--------|--------|--------|--------|--------|--------|--------|--------|
| `0xAA` (sync) | `0x08` (length) | Type | Function | Param1 | Param2 | Param3 | Checksum |

### Byte Definitions
- **Byte 0**: `0xAA` - Sync byte (constant)
- **Byte 1**: `0x08` - Packet length (constant)
- **Byte 2**: Command type
  - `0x02` = Toilet control commands
  - `0x03` = Ambient light commands
- **Byte 3**: Function code (specific feature to control)
- **Byte 4-6**: Parameters (function-specific values)
- **Byte 7**: Checksum = Sum of bytes 0-6 modulo 256

### Command Generation Code

#### Standard Toilet Command
```javascript
function createCommond(type, param1, param2, param3) {
    var a = [0xAA, 0x08, 0x02, type, param1, param2, param3];
    a.push(a.reduce((sum, b) => sum + b) & 0xFF);  // checksum
    return new Uint8Array(a);
}
```

#### Ambient Light Command
```javascript
function createAmbientLightCommond(type, param1, param2, param3) {
    var a = [0xAA, 0x08, 0x03, type, param1, param2, param3];
    a.push(a.reduce((sum, b) => sum + b) & 0xFF);  // checksum
    return new Uint8Array(a);
}
```

## Toilet Control Functions

### Basic Controls
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Light | `0x01` | Toilet illumination | On/Off: 0x00/0x01 |
| Power | `0x02` | Main power | On/Off: 0x00/0x01 |
| ECO | `0x03` | Energy saving mode | On/Off: 0x00/0x01 |
| Foam | `0x04` | Foam shield | On/Off: 0x00/0x01 |
| Stop | `0x05` | Stop all operations | 0x00 |
| Auto Mode | `0x06` | Automatic mode | On/Off: 0x00/0x01 |
| Self Cleaning | `0x07` | Nozzle self-cleaning | On/Off: 0x00/0x01 |

### Washing Functions
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Women's Wash | `0x10` | 妇洗 (Fuxi) | On/Off: 0x00/0x01 |
| Butt Wash | `0x11` | 臀洗 (Tunxi) | On/Off: 0x00/0x01 |
| Child Wash | `0x12` | 童洗 (Tongxi) | On/Off: 0x00/0x01 |
| Massage | `0x13` | 按摩 (Anmo) | On/Off: 0x00/0x01 |

### Cover Controls
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Flip Cover | `0x20` | 翻盖 (Fangai) | Open: 0x01, Close: 0x00 |
| Flip Ring | `0x21` | 翻圈 (Fanquan) | Open: 0x01, Close: 0x00 |

### Cleaning Functions
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Flush | `0x30` | 冲水 (Chongshui) | Activate: 0x01 |
| Blow Dry | `0x31` | 吹风 (Chuifeng) | On/Off: 0x00/0x01 |

### Temperature Controls (with levels)
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Seat Temp | `0x40` | 坐温 (Zuowen) | Level 0-5 |
| Water Temp | `0x41` | 水温 (Shuiwen) | Level 0-5 |
| Wind Temp | `0x42` | 风温 (Fengwen) | Level 0-5 |
| Water Pressure | `0x43` | 水压 (Shuiya) | Level 0-5 |
| Position | `0x44` | 管位 (Guanwei) | Level 0-5 |

### Advanced Settings
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Lid Open Torque | `0x50` | 翻盖打开力矩 | Value 0-100 |
| Lid Close Torque | `0x51` | 翻关闭力矩 | Value 0-100 |
| Ring Open Torque | `0x52` | 翻圈打开力矩 | Value 0-100 |
| Ring Close Torque | `0x53` | 翻圈关闭力矩 | Value 0-100 |
| Volume | `0x54` | 音量语音调节 | Value 0-100 |
| Flush Time | `0x55` | 冲水时间调节 | Value 0-100 |
| Radar Sensitivity | `0x56` | 雷达挡位调节 | Value 0-10 |
| Auto Close Time | `0x57` | 自动关盖时间 | Value 0-100 |
| Auto Flush | `0x58` | 自动冲水开关 | On/Off: 0x00/0x01 |
| Auto Foam | `0x59` | 自动泡沫盾开关 | On/Off: 0x00/0x01 |
| Auto Night Light | `0x5A` | 自动夜灯开关 | On/Off: 0x00/0x01 |
| Aging Mode | `0x5B` | 老化功能开关 | On/Off: 0x00/0x01 |
| Virtual Seat | `0x5C` | 虚拟着座开关 | On/Off: 0x00/0x01 |
| Reserved 1 | `0x5D` | 预留1开关 | On/Off: 0x00/0x01 |
| Reserved 2 | `0x5E` | 预留2开关 | On/Off: 0x00/0x01 |

## Ambient Light Control

### Light Modes
| Mode | Value | Description |
|------|-------|-------------|
| Static | `0x00` | 静态 - Static color |
| Flashing | `0x01` | 闪烁 - Flashing |
| Breathing | `0x02` | 呼吸 - Breathing effect |
| Running Water | `0x03` | 流水 - Running water |
| Colorful Gradient | `0x04` | 七彩渐变 - Colorful gradient |
| Colorful Running | `0x05` | 七彩流水 - Colorful running |
| Welcome | `0x06` | 迎宾 - Welcome mode |

### Ambient Light Commands
| Function | Code | Description | Parameters |
|----------|------|-------------|------------|
| Light On/Off | `0x01` | Main ambient light | On/Off: 0x00/0x01 |
| RGB Color | `0x02` | Set RGB color | R(0-255), G(0-255), B(0-255) |
| Mode | `0x03` | Light mode | Mode value (0x00-0x06) |
| Brightness | `0x04` | Light brightness | Value 0-100 |

## BLE Connection Details

### UUIDs
**Note**: The app uses uni-app's standard BLE APIs which dynamically discover services. The typical UUIDs for similar devices are:

- **Service UUID**: `0000FFE0-0000-1000-8000-00805F9B34FB` (common for BLE modules)
- **Write Characteristic**: `0000FFE1-0000-1000-8000-00805F9B34FB`
- **Read/Notify Characteristic**: `0000FFE2-0000-1000-8000-00805F9B34FB`

### Connection Flow
1. Enable Bluetooth adapter
2. Start BLE device discovery
3. Filter devices by name or MAC address
4. Connect to device
5. Discover services and characteristics
6. Enable notifications on read characteristic
7. Write commands to write characteristic

### Command Examples

#### Example 1: Turn on toilet light
```javascript
// Type: 0x02 (toilet), Function: 0x01 (light), Param1: 0x01 (on)
[0xAA, 0x08, 0x02, 0x01, 0x01, 0x00, 0x00, 0xB6]
// Checksum: 0xAA + 0x08 + 0x02 + 0x01 + 0x01 + 0x00 + 0x00 = 0xB6
```

#### Example 2: Set seat temperature to level 3
```javascript
// Type: 0x02 (toilet), Function: 0x40 (seat temp), Param1: 0x03 (level 3)
[0xAA, 0x08, 0x02, 0x40, 0x03, 0x00, 0x00, 0xF6]
// Checksum: 0xAA + 0x08 + 0x02 + 0x40 + 0x03 + 0x00 + 0x00 = 0xF6
```

#### Example 3: Flush toilet
```javascript
// Type: 0x02 (toilet), Function: 0x30 (flush), Param1: 0x01 (activate)
[0xAA, 0x08, 0x02, 0x30, 0x01, 0x00, 0x00, 0xD6]
// Checksum: 0xAA + 0x08 + 0x02 + 0x30 + 0x01 + 0x00 + 0x00 = 0xD6
```

#### Example 4: Set ambient light to blue (RGB: 0, 0, 255)
```javascript
// Type: 0x03 (light), Function: 0x02 (RGB), R: 0, G: 0, B: 255
[0xAA, 0x08, 0x03, 0x02, 0x00, 0x00, 0xFF, 0x14]
// Checksum: 0xAA + 0x08 + 0x03 + 0x02 + 0x00 + 0x00 + 0xFF = 0x14
```

## Home Assistant Integration Options

### Option 1: Native BLE Integration (Recommended)
Use Home Assistant's built-in BLE capabilities with custom YAML configuration.

**Pros:**
- Direct connection
- No additional hardware needed (if HA has BLE)
- Faster response

**Cons:**
- Requires BLE adapter on HA host
- Limited range

### Option 2: ESPHome Bridge
Use an ESP32 with BLE to bridge commands from Home Assistant via WiFi.

**Pros:**
- Flexible placement
- WiFi range
- Can add sensors

**Cons:**
- Requires ESP32 hardware
- Additional component

## Implementation Files

See the following files for complete implementations:
- `home_assistant_native_ble.md` - Native HA BLE integration
- `esphome_ble_bridge.md` - ESPHome BLE bridge configuration
