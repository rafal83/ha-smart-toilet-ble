# Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour WC intelligents avec connectivité BLE. Supporte les protocoles DM et SKS.

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/rafal83/ha-smart-toilet-ble?style=for-the-badge&color=green)](https://github.com/rafal83/ha-smart-toilet-ble/releases)

[![Ajouter à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rafal83&repository=ha-smart-toilet-ble&category=integration)
[![Configurer l'intégration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_toilet_ble)

## Installation via HACS

1. HACS > Integrations > "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` (catégorie: Integration)
3. Installer "Smart Toilet BLE"
4. Redémarrer HA
5. Settings > Devices & Services > Add Integration > "Smart Toilet BLE"

## Modèles supportés

| Modèle | Protocole | Description |
|--------|-----------|-------------|
| DM Smart Toilet | DM (header `0xAA`, 8 octets fixes) | WC intelligents protocole DM (DM-Toilet-Control) |
| SKS Smart Toilet | SKS (header `0x33`, taille variable) | WC SKS avec fonctions étendues |

## Fonctionnalités par modèle

### DM Smart Toilet (DM)

- **Lumière ambiante** : on/off, couleur RGB, luminosité, 7 modes d'effets (static, breathing, flashing, etc.)
- **Contrôles de base** : Power, ECO, Foam, Auto Mode
- **Lavage** : Women's, Butt, Child, Massage
- **Couvercle** : Cover, Ring (open/close)
- **Nettoyage** : Flush, Blow Dry, Self Clean
- **Niveaux** : Températures siège/eau/air (0-5), pression eau (0-5), position buse (0-5)
- **Réglages avancés** : Torques couvercle/ring, volume, temps de chasse, sensibilité radar, Auto Flush/Foam/Night Light, Aging Mode, Virtual Seat

### SKS Smart Toilet

- **Lavage** : Butt, Women's, Child, Assisted, One-Click Clean, Moving Wash, Massage, Water Pattern
- **Nettoyage** : Full/Small Flush, Blow Dry, Self Clean
- **Couvercle** : Cover, Ring (toggle)
- **Éclairage** : Night Light, Ambient Light (toggle)
- **Fonctions spéciales** : Aromatherapy, Sterilization, Infrared Therapy, User Presets 1/2
- **Niveaux** : Températures, pression, position buse, vitesse vent
- **Réglages avancés** : 20+ switches (auto aroma, radar, foot sensor, energy saving, buzzer, display, sterilization modes, etc.) + sliders (niveaux radar, chasse, force couvercle, délais)

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

  - type: entities
    title: Réglages
    entities:
      - entity: number.smart_toilet_seat_temperature
      - entity: number.smart_toilet_water_temperature
      - entity: number.smart_toilet_water_pressure
      - entity: number.smart_toilet_nozzle_position
      - entity: select.smart_toilet_light_mode
```

## Structure des fichiers

```
custom_components/smart_toilet_ble/
  __init__.py       # Coordinator BLE + command dispatch (DM/SKS)
  const.py          # Protocoles, modèles, commandes, définitions d'entités
  config_flow.py    # Configuration UI (sélection modèle + MAC)
  entity.py         # Classe de base des entités
  light.py          # Lumière ambiante (RGB, brightness, on/off)
  select.py         # Sélecteur mode d'éclairage
  switch.py         # Switches (contrôles on/off)
  button.py         # Boutons (actions momentanées)
  number.py         # Sliders (niveaux, températures, réglages)
  sensor.py         # Capteur statut connexion
  manifest.json     # Métadonnées intégration
  strings.json      # Traductions config flow
  services.yaml     # Services HA
```

## Protocole BLE

Deux protocoles supportés :

**DM** : Paquets fixes 8 octets `[0xAA, 0x08, type, function, p1, p2, p3, checksum]`
**SKS** : Paquets variables `[0x33, function, params_len, ...params, checksum]`

Pour les détails, voir [BLE_PROTOCOL_DOCUMENTATION.md](../../BLE_PROTOCOL_DOCUMENTATION.md).

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE (intégré ou dongle USB)
- Adresse MAC de vos WC

## Support

- **Issues**: [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)
- **Logs**: Settings > System > Logs > chercher "smart_toilet_ble"

## License

MIT License
