# 📦 Installation de l'Intégration Smart Toilet BLE

## 🎯 Installation en 5 Étapes

### Étape 1: Copier les Fichiers

**Via Samba/SSH/File Editor:**

```bash
# Créer le dossier dans Home Assistant
mkdir -p /config/custom_components/smart_toilet

# Copier TOUS les fichiers du dossier custom_components/smart_toilet/
# vers /config/custom_components/smart_toilet/
```

**Structure à obtenir:**
```
/config/custom_components/
└── smart_toilet/
    ├── __init__.py          ✅ (coordinateur BLE)
    ├── button.py            ✅ (3 boutons)
    ├── config_flow.py       ✅ (configuration UI)
    ├── const.py             ✅ (constantes)
    ├── entity.py            ✅ (classe de base)
    ├── number.py            ✅ (5 sliders)
    ├── sensor.py            ✅ (6 capteurs)
    ├── switch.py            ✅ (12 switches)
    ├── manifest.json        ✅ (métadonnées)
    ├── strings.json         ✅ (traductions)
    ├── services.yaml        ✅ (services)
    ├── hacs.json            ✅ (HACS)
    ├── smart-toilet.png     ✅ (icône)
    └── README.md            ✅ (documentation)
```

### Étape 2: Redémarrer Home Assistant

**Via l'interface:**
- Settings → System → Restart → Restart

**Via ligne de commande:**
```bash
ha core restart
```

**⚠️ Icône de l'intégration:**
L'intégration inclut une icône personnalisée dans le dossier `brand/`.
Pour Home Assistant 2024.8+:
- L'icône s'affiche automatiquement depuis `custom_components/smart_toilet/brand/icon.png`
- Si vous voyez "icon not available":
  1. Vérifiez que HA est en version 2024.8+
  2. Redémarrez complètement HA
  3. Videz le cache du navigateur (Ctrl+Shift+R)
  4. Supprimez et recréez l'intégration si nécessaire

### Étape 3: Vider le Cache du Navigateur

**Important!** HA met en cache les intégrations.

- **Chrome/Edge**: Ctrl+Shift+R (ou Cmd+Shift+R sur Mac)
- **Firefox**: Ctrl+F5
- **Safari**: Cmd+Shift+R

### Étape 4: Trouver l'Adresse MAC de Vos WC

**Méthode 1: Via l'app mobile originale**
- Ouvrir l'app DM-Toilet-Control
- L'adresse MAC est affichée lors de la connexion

**Méthode 2: Via nRF Connect (app gratuite)**
1. Installer **nRF Connect** sur votre téléphone
2. Scanner les appareils BLE
3. Chercher un appareil avec "Toilet", "Smart", ou "BLE" dans le nom
4. Noter l'adresse MAC (format: `AA:BB:CC:DD:EE:FF`)

**Méthode 3: Via SSH sur HA**
```bash
bluetoothctl
[bluetooth]# scan on
# Attendre 10 secondes
# Chercher votre WC dans la liste
[bluetooth]# scan off
```

### Étape 5: Ajouter l'Intégration via UI

1. Aller sur **Settings** → **Devices & Services**
2. Cliquer sur **"+ Add Integration"** (en bas à droite)
3. Chercher **"Smart Toilet BLE"** ou **"Smart Toilet"**
4. **Configuration en 2 options:**

#### Option A: Sélection via Scan BLE (Recommandé)

Le scan affiche automatiquement tous les appareils BLE découverts par Home Assistant:

1. **Sélectionner votre WC** dans la liste déroulante
   - Format: `Nom - AA:BB:CC:DD:EE:FF (RSSI: -65)`
   - Le RSSI indique la force du signal (plus proche de 0 = meilleur)
   
2. Cliquer sur **"Submit"**

**💡 Astuce:** Si vos WC n'apparaissent pas dans la liste:
- Vérifiez qu'ils sont allumés et en mode BLE
- Attendez quelques secondes que HA les découvre
- Utilisez l'option manuelle ci-dessous

#### Option B: Saisie Manuelle de l'Adresse MAC

Si le scan ne trouve pas vos WC ou si vous connaissez déjà l'adresse MAC:

1. Sélectionner **"✏️ Enter MAC address manually"** dans la liste
2. Entrer les informations:
   ```
   Name: Smart Toilet
   MAC Address: AA:BB:CC:DD:EE:FF
   ```
3. Cliquer sur **"Submit"**

**Comment trouver l'adresse MAC:**
- **Via nRF Connect** (app gratuite): Scanner → Noter l'adresse
- **Via l'app originale** DM-Toilet-Control: Affichée lors de la connexion
- **Via SSH sur HA**: `bluetoothctl` → `scan on` → Attendre 10s → `scan off`

### Étape 6: Vérifier

Les entités apparaissent automatiquement:

**Switches (12):**
- `switch.smart_toilet_light`
- `switch.smart_toilet_power`
- `switch.smart_toilet_eco`
- `switch.smart_toilet_foam`
- `switch.smart_toilet_auto`
- `switch.smart_toilet_women_wash`
- `switch.smart_toilet_butt_wash`
- `switch.smart_toilet_child_wash`
- `switch.smart_toilet_massage`
- `switch.smart_toilet_dry`
- `switch.smart_toilet_cover`
- `switch.smart_toilet_ring`

**Buttons (3):**
- `button.smart_toilet_flush`
- `button.smart_toilet_stop`
- `button.smart_toilet_self_clean`

**Sensors (6):**
- `sensor.smart_toilet_connection_status`
- `sensor.smart_toilet_seat_temperature_level`
- `sensor.smart_toilet_water_temperature_level`
- `sensor.smart_toilet_wind_temperature_level`
- `sensor.smart_toilet_water_pressure_level`
- `sensor.smart_toilet_nozzle_position_level`

**Numbers (5):**
- `number.smart_toilet_seat_temperature`
- `number.smart_toilet_water_temperature`
- `number.smart_toilet_wind_temperature`
- `number.smart_toilet_water_pressure`
- `number.smart_toilet_nozzle_position`

---

## ❓ Dépannage

### Problème: "Integration not found"

**Cause:** HA n'a pas détecté l'intégration.

**Solution:**
```bash
# Vérifier que les fichiers sont bien placés
ls -la /config/custom_components/smart_toilet/
```

Si les fichiers ne sont pas là:
1. Recopier tout le dossier `custom_components/smart_toilet/`
2. Redémarrer HA
3. Vider cache navigateur (Ctrl+Shift+R)

---

### Problème: "No BLE adapter found"

**Cause:** Home Assistant n'a pas de BLE.

**Solutions:**

**Option A: Ajouter un dongle BLE**
- CSR 4.0 USB (~8€)
- RTL8761B USB (~10€)
- HA SkyConnect (~30€)

**Option B: Utiliser ESPHome Bridge**
- Voir documentation ESPHome

---

### Problème: "Connection timeout"

**Cause:** Impossible de se connecter aux WC.

**Vérifier:**
1. ✅ Adresse MAC correcte
2. ✅ WC allumés et en mode BLE
3. ✅ Distance < 10m
4. ✅ Pas d'interférence BLE

**Tester:**
```bash
# En SSH sur HA
bluetoothctl
[bluetooth]# connect AA:BB:CC:DD:EE:FF

# Si ça ne marche pas:
[bluetooth]# scan on
# Vérifier que le device apparaît
```

---

### Problème: Les entités sont "Unavailable"

**Cause:** Perte de connexion BLE.

**Solution:**
- L'intégration reconnecte automatiquement (toutes les 30s)
- Vérifier que les WC sont allumés
- Redémarrer HA si nécessaire

---

### Problème: Les commandes ne fonctionnent pas

**Vérifier les logs:**
- Settings → System → Logs
- Chercher "smart_toilet"

**Erreurs courantes:**

| Erreur | Cause | Solution |
|--------|-------|----------|
| `BleakError` | Problème BLE | Redémarrer HA |
| `No writable characteristic` | UUIDs différents | Voir logs pour détails |
| `Connection refused` | MAC incorrecte | Vérifier l'adresse |

---

## 🔄 Mettre à Jour l'Intégration

### Manuellement
1. Supprimer `/config/custom_components/smart_toilet/`
2. Recopier la nouvelle version
3. Redémarrer HA

---

## 🗑️ Désinstaller l'Intégration

1. **Supprimer l'intégration:**
   - Settings → Devices & Services
   - Smart Toilet BLE → ⋮ → Delete

2. **Supprimer les fichiers:**
   ```bash
   rm -rf /config/custom_components/smart_toilet
   ```

3. **Redémarrer HA**

---

## ✅ Checklist d'Installation

- [ ] Dossier `custom_components/smart_toilet/` copié dans `/config/`
- [ ] Tous les 14 fichiers sont présents
- [ ] Home Assistant redémarré
- [ ] Cache navigateur vidé (Ctrl+Shift+R)
- [ ] Intégration "Smart Toilet BLE" visible dans Add Integration
- [ ] Adresse MAC des WC trouvée
- [ ] Intégration configurée avec l'adresse MAC
- [ ] 26 entités visibles et disponibles (12 switches + 3 buttons + 6 sensors + 5 numbers)
- [ ] Test d'une commande (ex: light on/off)

---

**Besoin d'aide ?** Vérifiez les logs HA et la documentation ! 🚽
