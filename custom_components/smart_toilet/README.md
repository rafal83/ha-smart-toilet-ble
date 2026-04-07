# 🚽 Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour WC japonais avec connectivité BLE. Ajoutez vos WC facilement via l'interface UI !

## 📦 Installation via HACS (Recommandé)

### Étape 1: Ajouter le Repository dans HACS

1. Dans Home Assistant, aller sur **HACS** → **Intégrations**
2. Cliquer sur **"⋮"** (3 points en haut à droite) → **"Custom repositories"**
3. Remplir:
   - **Repository**: URL de votre repo GitHub (ex: `https://github.com/votre-username/smart-toilet-ble`)
   - **Category**: **Integration**
4. Cliquer sur **"Add"**

### Étape 2: Installer l'Intégration

1. Chercher **"Smart Toilet BLE"** dans la liste
2. Cliquer sur **"Download"**
3. Cliquer sur **"Download"** pour confirmer
4. **Redémarrer** Home Assistant

### Étape 3: Ajouter Votre WC via l'UI

1. Aller sur **Settings** → **Devices & Services**
2. Cliquer sur **"+ Add Integration"** (en bas à droite)
3. Chercher **"Smart Toilet BLE"**
4. Configurer:

#### Option A: Saisie Manuelle de l'Adresse MAC

1. Entrer un nom (ex: "Smart Toilet")
2. Entrer l'adresse MAC de vos WC (ex: `AA:BB:CC:DD:EE:FF`)
3. Cliquer sur **"Submit"**

#### Option B: Scanner BLE (si disponible)

1. Cliquer sur **"Scan for devices"**
2. Attendre le scan (~10 secondes)
3. Sélectionner vos WC dans la liste
4. Cliquer sur **"Submit"**

### Trouver l'Adresse MAC de Vos WC

**Méthode 1: Via l'app mobile originale**
- Ouvrir l'app DM-Toilet-Control
- L'adresse MAC est affichée lors de la connexion

**Méthode 2: Via une app BLE scanner**
1. Installer **nRF Connect** (Android/iOS)
2. Scanner les appareils BLE
3. Chercher un appareil nommé "Smart Toilet", "BLE Toilet", ou similaire
4. Noter l'adresse MAC

**Méthode 3: Via ligne de commande (si accès SSH à HA)**
```bash
bluetoothctl scan on
```

## 🎮 Utilisation

Une fois configuré, vous aurez automatiquement:

### Switches
- 💡 **Light** - Lumière des WC
- 🔌 **Power** - Alimentation principale
- 🍃 **ECO Mode** - Mode économie d'énergie
- 🫧 **Foam Shield** - Bouclier de mousse
- 🔄 **Auto Mode** - Mode automatique
- 🚿 **Women's Wash** - Lavage féminin
- 💧 **Butt Wash** - Lavage fessier
- 👶 **Child Wash** - Lavage enfant
- 💆 **Massage** - Massage
- 💨 **Blow Dry** - Séchage
- 🚽 **Toilet Cover** - Couvercle
- ⭕ **Toilet Ring** - Abattement

### Buttons
- 🌊 **Flush** - Chasser d'eau
- 🛑 **Stop All** - Arrêt d'urgence
- 🧹 **Self Clean** - Auto-nettoyage

### Sensors
- 📶 **Connection Status** - Statut de connexion (Connected/Disconnected)
- 🌡️ **Seat Temperature Level** - Niveau température siège (0-5)
- 💧 **Water Temperature Level** - Niveau température eau (0-5)
- 💨 **Wind Temperature Level** - Niveau température air (0-5)
- 📊 **Water Pressure Level** - Niveau pression eau (0-5)
- 🎯 **Nozzle Position Level** - Niveau position buse (0-5)

### Number Entities (Sliders)
- 🌡️ **Seat Temperature** - Contrôle température siège (slider 0-5)
- 💧 **Water Temperature** - Contrôle température eau (slider 0-5)
- 💨 **Wind Temperature** - Contrôle température air (slider 0-5)
- 📊 **Water Pressure** - Contrôle pression eau (slider 0-5)
- 🎯 **Nozzle Position** - Contrôle position buse (slider 0-5)

## 📊 Créer un Dashboard

### Carte Simple

```yaml
type: entities
title: Smart Toilet
entities:
  - entity: switch.smart_toilet_light
  - entity: switch.smart_toilet_power
  - entity: button.smart_toilet_flush
  - entity: button.smart_toilet_stop
```

### Carte Complète

```yaml
type: vertical-stack
cards:
  - type: entities
    title: 🚽 Smart Toilet - Contrôles
    show_header_toggle: false
    entities:
      - entity: switch.smart_toilet_light
      - entity: switch.smart_toilet_power
      - entity: switch.smart_toilet_eco
      - entity: button.smart_toilet_flush
      - entity: button.smart_toilet_stop

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

  - type: entities
    title: 📊 Status
    entities:
      - entity: sensor.smart_toilet_connection_status
      - entity: sensor.smart_toilet_seat_temperature_level
      - entity: sensor.smart_toilet_water_temperature_level
      - entity: sensor.smart_toilet_water_pressure_level

  - type: entities
    title: 🎛️ Réglages
    entities:
      - entity: number.smart_toilet_seat_temperature
      - entity: number.smart_toilet_water_temperature
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
    for: "00:02:00"
condition:
  - condition: state
    entity_id: switch.smart_toilet_power
    state: "on"
action:
  - service: button.press
    target:
      entity_id: button.smart_toilet_flush
```

## 🔧 Dépannage

### L'intégration n'apparaît pas dans HACS

**Solution:**
1. Vérifier que HACS est installé
2. Vider le cache du navigateur (Ctrl+F5)
3. Redémarrer Home Assistant

### Erreur de Connexion BLE

**Vérifier:**
- ✅ Home Assistant a un adaptateur BLE (intégré ou dongle USB)
- ✅ L'adresse MAC est correcte
- ✅ Les WC sont allumés et en mode BLE
- ✅ Distance < 10m entre HA et les WC

**Tester la connexion:**
```bash
# En SSH sur HA
bluetoothctl
[bluetooth]# connect AA:BB:CC:DD:EE:FF
```

### Les Switches Ne Fonctionnent Pas

**Vérifier les logs:**
1. **Settings** → **System** → **Logs**
2. Chercher les erreurs "smart_toilet"

**Solutions courantes:**
- Redémarrer Home Assistant
- Vérifier que les WC supportent le protocole BLE documenté
- Tester avec l'app mobile originale d'abord

### Reconnexion Automatique

L'intégration tente de se reconnecter automatiquement toutes les 30 secondes en cas de déconnexion.

## 📝 Structure des Fichiers

```
custom_components/
└── smart_toilet/
    ├── __init__.py           # Configuration principale et coordinateur
    ├── config_flow.py        # Flow de configuration UI
    ├── const.py              # Constantes
    ├── entity.py             # Classe de base des entités
    ├── switch.py             # Entités switch
    ├── button.py             # Entités button
    ├── manifest.json         # Métadonnées de l'intégration
    ├── strings.json          # Traductions
    └── services.yaml         # Services personnalisés
```

## 🔍 Protocole BLE

Cette intégration utilise le protocole BLE suivant:
- **Packet Size**: 8 bytes
- **Sync Byte**: `0xAA`
- **Checksum**: Sum of bytes 0-6 modulo 256
- **Service UUID**: `0000FFE0-0000-1000-8000-00805F9B34FB`
- **Write UUID**: `0000FFE1-0000-1000-8000-00805F9B34FB`

Pour plus de détails, voir `BLE_PROTOCOL_DOCUMENTATION.md`.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/votre-username/smart-toilet-ble/issues)
- **Documentation**: [Wiki](https://github.com/votre-username/smart-toilet-ble/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/votre-username/smart-toilet-ble/discussions)

## 📄 License

MIT License - Voir fichier LICENSE

## 🙏 Remerciements

- Reverse engineering de l'app DM-Toilet-Control v1.0.6
- Intégration basée sur bleak pour la communication BLE
- Communauté Home Assistant pour le framework d'intégration

---

**Profitez de vos WC connectés ! 🚽✨**
