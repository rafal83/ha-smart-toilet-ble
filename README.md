# 🚽 Smart Toilet BLE - Intégration Home Assistant

Intégration Home Assistant complète avec interface UI pour contrôler vos WC japonais via BLE.

## ✨ Fonctionnalités

- ✅ **Configuration via UI** (pas de YAML !)
- ✅ **Scan BLE** intégré pour trouver vos WC
- ✅ **Reconnexion automatique** avec `bleak-retry-connector`
- ✅ **12 switches** prêts à l'emploi
- ✅ **3 boutons** pour actions momentanées
- ✅ **6 capteurs** (connexion, températures, pression, position)
- ✅ **5 sliders** de contrôle (températures, pression, position)
- ✅ **Dashboard-ready** avec icônes
- ✅ **Support multi-WC** (ajouter plusieurs appareils)

## 🚀 Installation Rapide

### 1. Copier les fichiers
```bash
# Copier le dossier custom_components/smart_toilet/
# vers /config/custom_components/smart_toilet/ dans HA
```

### 2. Redémarrer HA
```
Settings → System → Restart → Restart
```

### 3. Vider le cache
```
Chrome/Edge: Ctrl + Shift + R
Firefox: Ctrl + F5
```

### 4. Ajouter via UI
```
Settings → Devices & Services → Add Integration
Chercher "Smart Toilet BLE"
Entrer MAC ou Scanner → Terminé ! 🎉
```

## 🎮 Entités Créées

### Switches (12)
- `switch.smart_toilet_light` 💡 Lumière
- `switch.smart_toilet_power` 🔌 Alimentation
- `switch.smart_toilet_eco` 🍃 Mode ECO
- `switch.smart_toilet_foam` 🫧 Mousse
- `switch.smart_toilet_auto` 🔄 Mode auto
- `switch.smart_toilet_women_wash` 🚿 Lavage féminin
- `switch.smart_toilet_butt_wash` 💧 Lavage fessier
- `switch.smart_toilet_child_wash` 👶 Lavage enfant
- `switch.smart_toilet_massage` 💆 Massage
- `switch.smart_toilet_dry` 💨 Séchage
- `switch.smart_toilet_cover` 🚽 Couvercle
- `switch.smart_toilet_ring` ⭕ Abattement

### Buttons (3)
- `button.smart_toilet_flush` 🌊 Chasser d'eau
- `button.smart_toilet_stop` 🛑 Arrêt urgence
- `button.smart_toilet_self_clean` 🧹 Auto-nettoyage

### Sensors (6)
- `sensor.smart_toilet_connection_status` 📶 Statut connexion
- `sensor.smart_toilet_seat_temperature_level` 🌡️ Niveau température siège (0-5)
- `sensor.smart_toilet_water_temperature_level` 💧 Niveau température eau (0-5)
- `sensor.smart_toilet_wind_temperature_level` 💨 Niveau température air (0-5)
- `sensor.smart_toilet_water_pressure_level` 📊 Niveau pression eau (0-5)
- `sensor.smart_toilet_nozzle_position_level` 🎯 Niveau position buse (0-5)

### Numbers (5) - Sliders de Contrôle
- `number.smart_toilet_seat_temperature` 🌡️ Contrôle température siège (0-5)
- `number.smart_toilet_water_temperature` 💧 Contrôle température eau (0-5)
- `number.smart_toilet_wind_temperature` 💨 Contrôle température air (0-5)
- `number.smart_toilet_water_pressure` 📊 Contrôle pression eau (0-5)
- `number.smart_toilet_nozzle_position` 🎯 Contrôle position buse (0-5)

## 📊 Exemple de Dashboard

```yaml
type: vertical-stack
cards:
  # Contrôles principaux
  - type: entities
    title: 🚽 Smart Toilet - Contrôles
    show_header_toggle: false
    entities:
      - entity: switch.smart_toilet_light
      - entity: switch.smart_toilet_power
      - entity: switch.smart_toilet_eco
      - entity: button.smart_toilet_flush
      - entity: button.smart_toilet_stop

  # Fonctions de lavage
  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.smart_toilet_women_wash
        name: Féminin
        icon: mdi:shower
        show_state: false
      - type: button
        entity: switch.smart_toilet_butt_wash
        name: Fessier
        icon: mdi:water
        show_state: false
      - type: button
        entity: switch.smart_toilet_dry
        name: Séchage
        icon: mdi:hair-dryer
        show_state: false

  # Capteurs de statut
  - type: entities
    title: 📊 Status
    entities:
      - entity: sensor.smart_toilet_connection_status
      - entity: sensor.smart_toilet_seat_temperature_level
      - entity: sensor.smart_toilet_water_temperature_level
      - entity: sensor.smart_toilet_water_pressure_level

  # Sliders de contrôle
  - type: entities
    title: 🎛️ Réglages
    entities:
      - entity: number.smart_toilet_seat_temperature
      - entity: number.smart_toilet_water_temperature
      - entity: number.smart_toilet_wind_temperature
      - entity: number.smart_toilet_water_pressure
      - entity: number.smart_toilet_nozzle_position
```

## 🤖 Automatisations Exemples

### Mode Nuit
```yaml
alias: "WC - Mode nuit"
trigger:
  - platform: time
    at: "22:00:00"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.smart_toilet_eco
```

### Chasse Automatique
```yaml
alias: "WC - Chasse auto après départ"
trigger:
  - platform: state
    entity_id: binary_sensor.salle_de_bain_motion
    from: "on"
    to: "off"
    for:
      minutes: 2
condition:
  - condition: state
    entity_id: switch.smart_toilet_power
    state: "on"
action:
  - service: button.press
    target:
      entity_id: button.smart_toilet_flush
```

## 📖 Documentation

- [Guide d'installation détaillé](./INSTALLATION_GUIDE.md)
- [Documentation du protocole BLE](./BLE_PROTOCOL_DOCUMENTATION.md)
- [Référence rapide](./QUICK_REFERENCE.md)
- [Documentation de l'intégration](./custom_components/smart_toilet/README.md)

## 🔧 Prérequis

- Home Assistant 2023.8.0+
- Adaptateur BLE (intégré ou dongle USB)
- Adresse MAC de vos WC

## 🐛 Support

- **Logs HA**: Settings → System → Logs → Chercher "smart_toilet"
- **Documentation**: Voir fichiers dans `custom_components/smart_toilet/`

## 📄 License

MIT License

---

**Profitez de vos WC connectés ! 🚽✨**
