# Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour WC intelligents avec connectivité BLE. Supporte les protocoles DM et SKS.

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/rafal83/ha-smart-toilet-ble?style=for-the-badge&color=green)](https://github.com/rafal83/ha-smart-toilet-ble/releases)

[![Ajouter à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rafal83&repository=ha-smart-toilet-ble&category=integration)
[![Configurer l'intégration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_toilet_ble)

## Installation via HACS

1. HACS > Integrations > "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` (catégorie : Integration)
3. Installer "Smart Toilet BLE"
4. Redémarrer HA
5. Paramètres > Appareils & services > Ajouter une intégration > "Smart Toilet BLE"

## Modèles supportés

| Modèle | Protocole | App de référence |
|--------|-----------|------------------|
| DM Smart Toilet | DM (header `0xAA`, 8 octets fixes) | DM Toilet Control v1.0.6 |
| SKS Smart Toilet | SKS (header `0x33`, taille variable) | com.sks.toilet v1.1.3 |

## Fonctionnalités par modèle

### DM Smart Toilet (DM)

- **Lumière ambiante** : on/off, RGB, luminosité, 7 modes (static, breathing, flashing, etc.) — envoyée
  en une seule trame BLE comme l'app officielle
- **Contrôles** (boutons) : Power, Light, Eco, Foam, Auto Mode, Stop, Self Clean, Flush, Blow Dry,
  Women's / Butt / Child Wash, Massage, Cover, Ring
- **Niveaux** (sliders) : Seat / Water / Wind Temperature (0-5), Water Pressure (0-5), Nozzle Position (0-5)
- **Réglages avancés** (catégorie Configuration) :
  - Boutons +/− : Volume, Radar Sensitivity, Flush Time, Auto Close Delay, Lid Open/Close Force,
    Ring Open/Close Force
  - Switches ON/OFF (avec `assumed_state`) : Auto Flush, Auto Foam, Aging Mode, Virtual Seat,
    User Preset 1, User Preset 2

> Le firmware DM est unidirectionnel — il n'envoie aucune notification BLE. Les actions ponctuelles
> sont donc des **boutons** (pas des switches), et les switches ON/OFF restants supposent l'état.

### SKS Smart Toilet

- **Lavage** : Butt / Women's / Child / Assisted Wash, One-Click Clean, Moving Wash, Massage, Water Pattern
- **Nettoyage** : Full / Small Flush, Blow Dry, Self Clean
- **Couvercle** : Cover, Ring (toggles sans état)
- **Éclairage** : Night Light, Ambient Light
- **Fonctions spéciales** : Aromatherapy, Sterilization, Infrared Therapy, User Presets 1/2
- **Niveaux** : Position, Pressure, Seat / Water / Wind Temperature, Wind Speed
- **Réglages avancés** (Configuration) : 20+ switches (auto aroma, radar, foot sensor, energy
  saving, buzzer, display, sterilization modes, etc.) + sliders (Radar, Flush, Cover/Ring Force,
  Post-Leave Flush Time, Auto Close Delay)

## Internationalisation

Noms d'entités et config flow disponibles en français et anglais. La langue suit le profil
utilisateur HA. Pour ajouter une langue, créer `translations/<code>.json` (s'inspirer de `en.json` /
`fr.json`).

## Exemple de Dashboard

```yaml
type: vertical-stack
cards:
  - type: light
    entity: light.dm_smart_toilet_ambient_light

  - type: grid
    columns: 3
    cards:
      - type: button
        entity: button.dm_smart_toilet_flush
      - type: button
        entity: button.dm_smart_toilet_stop_all
      - type: button
        entity: button.dm_smart_toilet_self_clean

  - type: entities
    title: Niveaux
    entities:
      - entity: number.dm_smart_toilet_seat_temperature
      - entity: number.dm_smart_toilet_water_temperature
      - entity: number.dm_smart_toilet_water_pressure
      - entity: number.dm_smart_toilet_nozzle_position
      - entity: select.dm_smart_toilet_light_mode
```

## Structure des fichiers

```
custom_components/smart_toilet_ble/
  __init__.py       # Coordinator BLE + dispatch DM/SKS + parsing notify SKS
  const.py          # Codes function, modèles, définitions d'entités
  config_flow.py    # Configuration UI (sélection modèle + MAC)
  entity.py         # Classe de base (has_entity_name=True)
  light.py          # Lumière ambiante (RGB, brightness, on/off — 1 frame)
  select.py         # Sélecteur mode de lumière
  switch.py         # Switches ON/OFF (assumed_state)
  button.py         # Boutons d'action
  number.py         # Sliders (températures, pression, position)
  sensor.py         # Connexion
  manifest.json     # Métadonnées intégration
  strings.json      # Source des libellés (en)
  translations/
    en.json         # Anglais
    fr.json         # Français
  services.yaml     # Services HA exposés
```

## Protocole BLE

**DM** : trames fixes 8 octets `[0xAA, 0x08, type, function, p1, p2, p3, checksum]`. Codes function
reverse-engineered depuis l'APK officielle (cf. [BLE_PROTOCOL_DOCUMENTATION.md](../../BLE_PROTOCOL_DOCUMENTATION.md)).
Type `0x02` = WC, type `0x03` = lumière ambiante (envoyée en **une seule trame** combinant mode + RGB
+ luminosité, comme l'app officielle).

**SKS** : trames variables `[0x33, function, params_len, ...params, checksum]`. Réponses notify
parsées (header `0x55`).

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE local ou ESPHome `bluetooth_proxy`
- Adresse MAC du WC
- Téléphone non connecté en BLE au WC (BLE = une seule connexion à la fois)

## Support

- **Issues** : [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)
- **Logs** : Paramètres > Système > Logs > filtrer sur `smart_toilet_ble`

## License

MIT License
