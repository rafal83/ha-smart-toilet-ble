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
- **2 protocoles supportés** : DM (DM-Toilet-Control) et SKS (com.sks.toilet)
- **Lumière ambiante** avec RGB, luminosité et 7 modes d'effets, envoyée en une seule trame BLE
- **UI multilingue** : interface et noms d'entités en français et anglais (fr/en)
- **Section "Configuration"** dans HA pour ranger les réglages avancés à part des contrôles
- **Support multi-WC**

## Limitations connues

- **Aucune remontée d'état du WC** : le firmware DM ne renvoie aucune notification BLE (confirmé par reverse-engineering de l'app officielle DM Toilet Control v1.0.6, qui ne s'abonne d'ailleurs à aucune notify). Conséquence :
  - Les actions ponctuelles (Flush, Wash, Cover, Power, etc.) sont exposées comme des **boutons** plutôt que des switches, car aucun toggle ne pourrait refléter l'état réel.
  - Les vrais switches restants (Auto Flush, Auto Foam, Aging Mode, Virtual Seat, User Presets) utilisent `assumed_state` : HA mémorise la dernière commande envoyée mais ne peut pas savoir si l'utilisateur a appuyé sur la télécommande physique entretemps.
  - Les sliders affichent la dernière valeur envoyée depuis HA (pas la valeur réelle si elle a été modifiée par la télécommande).

## Modèles supportés

| Modèle | Protocole | App d'origine | Description |
|--------|-----------|---------------|-------------|
| **DM Smart Toilet** | DM (`0xAA`, 8 octets fixes) | DM-Toilet-Control v1.0.6 | WC protocole DM. Codes function reverse-engineered depuis l'APK officielle. |
| **SKS Smart Toilet** | SKS (`0x33`, taille variable) | com.sks.toilet v1.1.3 | WC SKS avec fonctions étendues (aroma, sterilization, presets, etc.). |

## Installation Rapide

### Via HACS (recommandé)
1. HACS > Integrations > Menu "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` en catégorie **Integration**
3. Installer "Smart Toilet BLE"
4. Redémarrer HA

### Manuellement
Copier le dossier `custom_components/smart_toilet_ble/` dans `/config/custom_components/smart_toilet_ble/` puis redémarrer HA.

### Configurer
```
Paramètres > Appareils & services > Ajouter une intégration > "Smart Toilet BLE"
1. Choisir le modèle (DM Smart Toilet ou SKS)
2. Scanner ou saisir l'adresse MAC
```

## Entités créées

### DM Smart Toilet

| Type | Nb | Catégorie | Exemples |
|------|----|-----------|----------|
| `light` | 1 | Contrôles | Lumière ambiante (RGB, brightness, modes) |
| `select` | 1 | Contrôles | Mode lumière (Static, Breathing, Welcome, etc.) |
| `button` | 15 | Contrôles | Power, Flush, Stop, Self Clean, Wash (Women/Butt/Child), Massage, Cover, Ring, Light, Eco, Foam, Auto Mode, Blow Dry |
| `button` | 16 | Configuration | Volume +/−, Radar Sensitivity +/−, Flush Time +/−, Auto Close Delay +/−, Lid/Ring Open/Close Force +/− |
| `switch` | 6 | Configuration | Auto Flush, Auto Foam, Aging Mode, Virtual Seat, User Preset 1, User Preset 2 |
| `number` | 5 | Contrôles | Seat / Water / Wind Temperature, Water Pressure, Nozzle Position (0-5) |
| `sensor` | 1 | Diagnostic | État de connexion |

### SKS Smart Toilet

| Type | Nb | Catégorie | Exemples |
|------|----|-----------|----------|
| `button` | 19 | Contrôles | Full / Small Flush, Stop, Self Clean, Wash variantes, Massage, Lights, Aromatherapy, Sterilization, Infrared, User Presets |
| `switch` | 4 | Contrôles | Foam Shield, Blow Dry, Cover, Ring |
| `switch` | 20 | Configuration | Auto Aroma, Auto Foam, Auto Deodorizer, Flush on Leave, Radar, Foot Sensor, Buzzer, Display, Sterilizations, etc. |
| `number` | 6 | Contrôles | Position, Pressure, Seat / Water / Wind Temperature, Wind Speed |
| `number` | 6 | Configuration | Radar Level, Flush Level, Cover/Ring Force, Post-Leave Flush Time, Auto Close Delay |
| `sensor` | 1 | Diagnostic | État de connexion |

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
      - type: button
        entity: button.dm_smart_toilet_butt_wash
      - type: button
        entity: button.dm_smart_toilet_women_s_wash
      - type: button
        entity: button.dm_smart_toilet_blow_dry

  - type: entities
    title: Niveaux
    entities:
      - entity: number.dm_smart_toilet_seat_temperature
      - entity: number.dm_smart_toilet_water_temperature
      - entity: number.dm_smart_toilet_water_pressure
      - entity: number.dm_smart_toilet_nozzle_position
      - entity: select.dm_smart_toilet_light_mode
```

> Les entity_id réels dépendent de la langue de HA et du nom donné à l'appareil. Adaptez-les via Paramètres > Appareils > votre WC.

## Internationalisation

Les noms d'entités sont localisés via le système de traductions de Home Assistant :

- `translations/en.json` (anglais — par défaut)
- `translations/fr.json` (français)

HA choisit automatiquement la bonne langue selon le profil utilisateur. Pour ajouter une langue, créer `translations/<code>.json` avec la même structure.

## Documentation

- [Guide d'installation détaillé](./INSTALLATION_GUIDE.md)
- [Documentation du protocole BLE](./BLE_PROTOCOL_DOCUMENTATION.md) (codes function réels après reverse de l'app DM)
- [Référence rapide des trames](./QUICK_REFERENCE.md)

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE (intégré ou dongle USB) ou ESPHome bluetooth_proxy
- Adresse MAC du WC
- Le téléphone ne doit pas être connecté au WC en parallèle (BLE = une seule connexion à la fois)

## Dépannage

- **`Failed to send command: 'HaBleakClientWrapper' object has no attribute 'get_services'`** : version trop ancienne de l'intégration. Mettre à jour.
- **Les commandes partent (`Command sent: aa08...`) mais le WC ne réagit pas** : mauvais protocole sélectionné. Supprimer et reconfigurer en choisissant l'autre (DM ↔ SKS).
- **Aucune entité visible / `BLE device ... not discovered yet`** : le WC n'est pas vu par HA en BLE. Vérifier que l'app du téléphone n'est pas connectée et que le WC est à portée.
- **Logs** : Paramètres > Système > Logs, filtrer sur `smart_toilet_ble`.

```yaml
logger:
  default: warning
  logs:
    custom_components.smart_toilet_ble: debug
    bleak: debug
    bleak_retry_connector: debug
```

## Support

- **Issues** : [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)

## License

MIT License
