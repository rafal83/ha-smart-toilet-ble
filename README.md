# Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour contrôler vos WC intelligents via BLE. Supporte plusieurs protocoles et marques.

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/rafal83/ha-smart-toilet-ble?style=for-the-badge&color=green)](https://github.com/rafal83/ha-smart-toilet-ble/releases)
[![License](https://img.shields.io/github/license/rafal83/ha-smart-toilet-ble?style=for-the-badge)](LICENSE)

[![Ajouter à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rafal83&repository=ha-smart-toilet-ble&category=integration)
[![Configurer l'intégration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_toilet_ble)

## Fonctionnalités

- **Configuration via UI** (pas de YAML)
- **Scan BLE** intégré pour trouver vos WC
- **Reconnexion automatique** avec `bleak-retry-connector`
- **2 protocoles supportés** : DM (DM Smart Toilet) et SKS
- **Lumière ambiante** avec RGB, luminosité et 7 modes d'effets
- **Réglages avancés** : torque couvercle, volume, radar, etc.
- **Dashboard-ready** avec icônes
- **Support multi-WC** (plusieurs appareils)

## Modèles supportés

| Modèle | Protocole | App d'origine | Description |
|--------|-----------|---------------|-------------|
| DM Smart Toilet | DM (`0xAA`, 8 octets fixes) | DM-Toilet-Control v1.0.6 | WC intelligents protocole DM |
| SKS Smart Toilet | SKS (`0x33`, taille variable) | com.sks.toilet v1.1.3 | WC SKS avec fonctions étendues |

## Installation Rapide

### Via HACS (recommandé)
1. HACS > Integrations > Menu "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` en catégorie **Integration**
3. Installer "Smart Toilet BLE"
4. Redémarrer HA

### Manuellement
```bash
# Copier le dossier custom_components/smart_toilet_ble/
# vers /config/custom_components/smart_toilet_ble/ dans HA
```

### Configurer
```
Settings > Devices & Services > Add Integration > "Smart Toilet BLE"
1. Choisir le modèle (DM Smart Toilet ou SKS)
2. Scanner ou entrer l'adresse MAC
```

## Entités créées

### DM Smart Toilet (protocole DM)

**Light (1)** - Entité lumière HA avec roue de couleur
- `light.smart_toilet_light` - On/Off, RGB, luminosité, mode d'effet

**Select (1)**
- `select.smart_toilet_light_mode` - Mode d'éclairage (Static, Flashing, Breathing, Running Water, Colorful Gradient, Colorful Running, Welcome)

**Switches (16)**
- Power, ECO Mode, Foam Shield, Auto Mode
- Women's Wash, Butt Wash, Child Wash, Massage
- Blow Dry, Toilet Cover, Toilet Ring
- Auto Flush, Auto Foam, Auto Night Light, Aging Mode, Virtual Seat

**Buttons (3)**
- Flush, Stop All, Self Clean

**Numbers (13)** - Sliders de contrôle
- Seat/Water/Wind Temperature (0-5)
- Water Pressure, Nozzle Position (0-5)
- Lid/Ring Open/Close Torque (0-100%)
- Volume, Flush Time, Auto Close Time (0-100%)
- Radar Sensitivity (0-10)

**Sensors (1)**
- Connection Status

### SKS Smart Toilet (protocole SKS)

**Switches (23)**
- Foam Shield, Butt/Women's/Child/Assisted Wash, One-Click Clean, Moving Wash, Massage, Water Pattern
- Blow Dry, Toilet Cover, Toilet Ring, Night Light, Ambient Light
- Aromatherapy, Sterilization, Infrared Therapy
- Auto Aroma/Foam/Deodorizer/Ambient Light, Flush on Leave, All-Season Heating
- Moisturize, Radar, Foot Sensor, Energy Saving, Buzzer, Display, etc.

**Buttons (6)**
- Full Flush, Small Flush, Stop All, Self Clean, User Preset 1/2

**Numbers (12)** - Sliders de contrôle
- Nozzle Position, Water Pressure, Températures, Wind Speed
- Radar/Flush Level, Cover/Ring Force, Post-Leave Flush Time, Auto Close Delay

**Sensors (1)**
- Connection Status

## Exemple de Dashboard

```yaml
type: vertical-stack
cards:
  - type: light
    entity: light.smart_toilet_light

  - type: entities
    title: Contrôles
    entities:
      - entity: switch.smart_toilet_power
      - entity: switch.smart_toilet_eco
      - entity: button.smart_toilet_flush
      - entity: button.smart_toilet_stop

  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.smart_toilet_women_wash
        name: Féminin
        show_state: false
      - type: button
        entity: switch.smart_toilet_butt_wash
        name: Fessier
        show_state: false
      - type: button
        entity: switch.smart_toilet_dry
        name: Séchage
        show_state: false

  - type: entities
    title: Réglages
    entities:
      - entity: number.smart_toilet_seat_temperature
      - entity: number.smart_toilet_water_temperature
      - entity: number.smart_toilet_water_pressure
      - entity: number.smart_toilet_nozzle_position
      - entity: select.smart_toilet_light_mode
```

## Documentation

- [Guide d'installation détaillé](./INSTALLATION_GUIDE.md)
- [Documentation du protocole BLE](./BLE_PROTOCOL_DOCUMENTATION.md)
- [Référence rapide](./QUICK_REFERENCE.md)

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE (intégré ou dongle USB)
- Adresse MAC de vos WC

## Support

- **Logs HA**: Settings > System > Logs > Chercher "smart_toilet_ble"
- **Issues**: [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)

## License

MIT License
