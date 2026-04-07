# Smart Toilet BLE Integration for Home Assistant

Intégration Home Assistant complète avec interface UI (config flow) pour contrôler vos WC japonais via BLE.

## ✨ Fonctionnalités

- ✅ **Installation via HACS** ou manuelle
- ✅ **Configuration via UI** (pas de YAML à éditer !)
- ✅ **Scan BLE** intégré pour trouver vos WC
- ✅ **Reconnexion automatique** en cas de déconnexion
- ✅ **12 switches** prêts à l'emploi
- ✅ **3 boutons** pour actions momentanées
- ✅ **Dashboard-ready** avec icônes
- ✅ **Support multi- WC** (ajouter plusieurs appareils)

## 🚀 Installation Rapide

### 1. Copier les fichiers
```bash
# Copier le dossier custom_components/smart_toilet/
# vers /config/custom_components/smart_toilet/ dans HA
```

### 2. Redémarrer HA
- Settings → System → Restart

### 3. Vider le cache
- Ctrl+Shift+R dans le navigateur

### 4. Ajouter via UI
- Settings → Devices & Services → Add Integration
- Chercher "Smart Toilet BLE"
- Entrer l'adresse MAC ou scanner

## 📖 Documentation Complète

Voir [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) pour les instructions détaillées.

## 📁 Structure

```
custom_components/smart_toilet/
├── __init__.py           # Core & coordinator
├── config_flow.py        # UI configuration flow
├── const.py              # Constants
├── entity.py             # Base entity class
├── switch.py             # Switch entities (12)
├── button.py             # Button entities (3)
├── manifest.json         # Integration metadata
├── strings.json          # Translations (FR/EN)
├── services.yaml         # Custom services
├── hacs.json            # HACS metadata
└── README.md            # This file
```

## 🎮 Entités Créées

### Switches
- `switch.toilet_light` - Lumière
- `switch.toilet_power` - Alimentation
- `switch.toilet_eco` - Mode ECO
- `switch.toilet_foam` - Mousse
- `switch.toilet_auto` - Auto
- `switch.toilet_women_wash` - Lavage féminin
- `switch.toilet_butt_wash` - Lavage fessier
- `switch.toilet_child_wash` - Lavage enfant
- `switch.toilet_massage` - Massage
- `switch.toilet_dry` - Séchage
- `switch.toilet_cover` - Couvercle
- `switch.toilet_ring` - Abattement

### Buttons
- `button.toilet_flush` - Chasser d'eau
- `button.toilet_stop` - Arrêt urgence
- `button.toilet_self_clean` - Auto-nettoyage

## 🔧 Prérequis

- Home Assistant 2023.8.0+
- Adaptateur BLE (intégré ou dongle USB)
- Adresse MAC de vos WC

## 🐛 Support

- **Issues**: [GitHub Issues](https://github.com/votre-username/smart-toilet-ble/issues)
- **Logs**: HA → Settings → System → Logs → Chercher "smart_toilet"

## 📄 License

MIT License
