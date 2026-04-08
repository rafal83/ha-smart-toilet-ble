# Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour contrôler vos WC intelligents via BLE. Supporte les protocoles DM (DM Smart Toilet) et SKS.

## Fonctionnalités

- **Configuration via UI** (pas de YAML)
- **Scan BLE** intégré pour trouver vos WC
- **Reconnexion automatique** en cas de déconnexion
- **2 protocoles** : DM (DM Smart Toilet) et SKS
- **Lumière ambiante** avec RGB, luminosité et 7 modes d'effets
- **Réglages avancés** : torques, volume, radar, timers, etc.
- **Support multi-WC**

## Modèles supportés

| Modèle | Protocole | App d'origine |
|--------|-----------|---------------|
| DM Smart Toilet | DM (`0xAA`, 8 octets fixes) | DM-Toilet-Control |
| SKS Smart Toilet | SKS (`0x33`, taille variable) | com.sks.toilet |

## Installation

1. HACS > Integrations > "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` (catégorie: Integration)
3. Installer "Smart Toilet BLE"
4. Redémarrer HA
5. Settings > Devices & Services > Add Integration > "Smart Toilet BLE"
6. Choisir le modèle et entrer/scanner l'adresse MAC

## Entités créées

### DM Smart Toilet (DM)
- 1 light (RGB + brightness + modes)
- 1 select (mode éclairage)
- 16 switches
- 3 buttons
- 13 numbers (sliders)
- 1 sensor (connexion)

### SKS Smart Toilet
- 23 switches
- 6 buttons
- 12 numbers (sliders)
- 1 sensor (connexion)

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE (intégré ou dongle USB)
- Adresse MAC de vos WC

## Support

- **Issues**: [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)
- **Logs**: Settings > System > Logs > chercher "smart_toilet_ble"

## License

MIT License
