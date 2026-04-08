# Installation de l'Intégration Smart Toilet BLE

## Installation

### Via HACS (recommandé)

1. Dans Home Assistant, aller sur **HACS** > **Integrations**
2. Cliquer sur **"..."** > **"Custom repositories"**
3. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` en catégorie **Integration**
4. Chercher **"Smart Toilet BLE"** et installer
5. Redémarrer Home Assistant

### Manuellement

1. Copier le dossier `custom_components/smart_toilet_ble/` vers `/config/custom_components/smart_toilet_ble/`
2. Redémarrer HA
3. Vider le cache du navigateur (Ctrl+Shift+R)

**Structure requise :**
```
/config/custom_components/smart_toilet_ble/
  __init__.py
  button.py
  config_flow.py
  const.py
  entity.py
  light.py
  number.py
  select.py
  sensor.py
  switch.py
  manifest.json
  strings.json
  services.yaml
```

## Configuration

### Étape 1 : Choisir le modèle

```
Settings > Devices & Services > Add Integration > "Smart Toilet BLE"
```

Modèles disponibles :
- **DM Smart Toilet** - Protocole DM (app DM-Toilet-Control)
- **SKS Smart Toilet** - Protocole SKS (app com.sks.toilet)
- **Auto-detect** - Détection automatique (défaut: DM Smart Toilet)

### Étape 2 : Sélectionner l'appareil

**Option A : Scan BLE**
- Sélectionner votre WC dans la liste des appareils BLE découverts
- Le RSSI indique la force du signal (plus proche de 0 = meilleur)

**Option B : Saisie manuelle**
- Entrer l'adresse MAC (format `AA:BB:CC:DD:EE:FF`)

### Trouver l'adresse MAC

1. **Via nRF Connect** (app gratuite Android/iOS) : Scanner les appareils BLE
2. **Via l'app d'origine** : L'adresse est affichée lors de la connexion
3. **Via SSH sur HA** : `bluetoothctl` > `scan on` > chercher votre WC

## Entités créées

### DM Smart Toilet (protocole DM)

| Type | Nombre | Exemples |
|------|--------|----------|
| Light | 1 | Lumière ambiante (RGB, luminosité, modes) |
| Select | 1 | Mode d'éclairage (7 effets) |
| Switches | 16 | Power, ECO, Foam, Wash, Dry, Cover... |
| Buttons | 3 | Flush, Stop, Self Clean |
| Numbers | 13 | Températures, pression, torques, volume... |
| Sensors | 1 | Statut connexion |

### SKS Smart Toilet (protocole SKS)

| Type | Nombre | Exemples |
|------|--------|----------|
| Switches | 23 | Wash, Cover, Aroma, Sterilization, Radar... |
| Buttons | 6 | Full/Small Flush, Stop, User Presets |
| Numbers | 12 | Températures, pression, position, niveaux... |
| Sensors | 1 | Statut connexion |

## Dépannage

### "Integration not found"
- Vérifier que les fichiers sont dans `/config/custom_components/smart_toilet_ble/`
- Redémarrer HA
- Vider le cache navigateur (Ctrl+Shift+R)

### "No BLE adapter found"
- Ajouter un dongle BLE USB (CSR 4.0, RTL8761B, ou HA SkyConnect)
- Ou utiliser un bridge ESPHome

### "Connection timeout"
1. Vérifier l'adresse MAC
2. Vérifier que les WC sont allumés
3. Distance < 10m
4. Pas d'interférence BLE
5. Tester : `bluetoothctl` > `connect AA:BB:CC:DD:EE:FF`

### Entités "Unavailable"
- L'intégration reconnecte automatiquement toutes les 30s
- Vérifier que les WC sont allumés
- Redémarrer HA si nécessaire

### Commandes sans effet
- Vérifier les logs : Settings > System > Logs > chercher "smart_toilet_ble"
- Vérifier que le bon modèle/protocole est sélectionné
- Tester d'abord avec l'app mobile d'origine

## Mise à jour

### Via HACS
HACS > Integrations > Smart Toilet BLE > Update

### Manuellement
1. Supprimer `/config/custom_components/smart_toilet_ble/`
2. Recopier la nouvelle version
3. Redémarrer HA

## Désinstaller

1. Settings > Devices & Services > Smart Toilet BLE > Supprimer
2. `rm -rf /config/custom_components/smart_toilet_ble`
3. Redémarrer HA
