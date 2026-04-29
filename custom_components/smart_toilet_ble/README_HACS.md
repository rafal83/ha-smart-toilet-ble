# Smart Toilet BLE - Home Assistant Integration

Intégration Home Assistant pour contrôler vos WC intelligents via BLE. Supporte les protocoles
DM (DM Smart Toilet) et SKS.

## Fonctionnalités

- **Configuration via UI** (pas de YAML)
- **Scan BLE** intégré pour trouver les WC
- **Reconnexion automatique** via `bleak-retry-connector`
- **2 protocoles** : DM (`DM Toilet Control v1.0.6`) et SKS (`com.sks.toilet v1.1.3`)
- **Lumière ambiante** RGB + luminosité + 7 modes, en une seule trame BLE
- **UI multilingue** : français et anglais (extensible)
- **Section Configuration** dans HA pour ranger les réglages avancés à part

## Modèles supportés

| Modèle | Protocole | App d'origine |
|--------|-----------|---------------|
| DM Smart Toilet | DM (`0xAA`, 8 octets fixes) | DM Toilet Control |
| SKS Smart Toilet | SKS (`0x33`, taille variable) | com.sks.toilet |

## Installation

1. HACS > Integrations > "..." > Custom repositories
2. Ajouter `https://github.com/rafal83/ha-smart-toilet-ble` (catégorie : Integration)
3. Installer "Smart Toilet BLE"
4. Redémarrer HA
5. Paramètres > Appareils & services > Ajouter une intégration > "Smart Toilet BLE"
6. Choisir le modèle et entrer/scanner l'adresse MAC

## Entités créées

### DM Smart Toilet (DM)

- 1 light (lumière ambiante : RGB + brightness + modes)
- 1 select (mode de lumière)
- 15 boutons d'action (Power, Flush, Wash, Cover, Ring, etc.)
- 16 boutons +/− en Configuration (Volume, Radar, Flush Time, Forces, etc.)
- 6 switches en Configuration (Auto Flush, Auto Foam, Aging Mode, Virtual Seat, User 1/2)
- 5 sliders (températures, pression, position)
- 1 capteur (connexion)

### SKS Smart Toilet

- 19 boutons (Wash variantes, Lights, Aroma, Sterilization, Flush, etc.)
- 4 switches Contrôles (Foam, Blow Dry, Cover, Ring)
- 20 switches Configuration (Auto Aroma, Auto Foam, Radar, Foot Sensor, Buzzer, Display, etc.)
- 12 sliders (6 Contrôles + 6 Configuration)
- 1 capteur (connexion)

## Limitations

Le firmware DM est unidirectionnel — il n'envoie **aucune notification BLE**. Conséquence :
- Les actions ponctuelles sont des **boutons** (pas des switches), pour ne pas afficher d'état faux
- Les switches restants utilisent `assumed_state` : HA ne sait pas si l'utilisateur a appuyé sur la
  télécommande physique entre temps

## Prérequis

- Home Assistant 2024.8.0+
- Adaptateur BLE local ou ESPHome `bluetooth_proxy`
- Adresse MAC du WC
- Téléphone non connecté en BLE au WC en parallèle

## Support

- **Issues** : [GitHub Issues](https://github.com/rafal83/ha-smart-toilet-ble/issues)
- **Logs** : Paramètres > Système > Logs > filtrer sur `smart_toilet_ble`

## License

MIT License
