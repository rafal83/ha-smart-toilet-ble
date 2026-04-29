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
  translations/
    en.json
    fr.json
```

> Le dossier `translations/` est obligatoire pour avoir des noms d'entités lisibles dans la langue de HA.

## Configuration

### Étape 1 : Choisir le modèle

```
Paramètres > Appareils & services > Ajouter une intégration > "Smart Toilet BLE"
```

Modèles disponibles :
- **DM Smart Toilet** — protocole DM, app `DM Toilet Control v1.0.6`
- **SKS Smart Toilet** — protocole SKS, app `com.sks.toilet v1.1.3`
- **Auto-detect** — pour l'instant équivalent à DM par défaut, garde ce choix manuel pour ne pas te tromper

### Étape 2 : Sélectionner l'appareil

**Option A : Scan BLE**
- Sélectionner ton WC dans la liste des appareils BLE découverts
- Le RSSI indique la force du signal (plus proche de 0 = meilleur)

**Option B : Saisie manuelle**
- Entrer l'adresse MAC (format `AA:BB:CC:DD:EE:FF`)

### Trouver l'adresse MAC

1. **Via nRF Connect** (app gratuite Android/iOS) — scanner les appareils BLE
2. **Via l'app d'origine** — l'adresse est affichée lors de la connexion
3. **Via SSH sur HA** — `bluetoothctl` puis `scan on`, chercher ton WC

### Important : conflit avec le téléphone

Le BLE classique n'autorise **qu'une seule connexion à la fois**. Si l'app du téléphone est déjà
connectée au WC, HA n'arrivera pas à se connecter. Solutions :
- Forcer la fermeture de l'app mobile, ou
- Désactiver le Bluetooth du téléphone

## Entités créées

### DM Smart Toilet

Le DM firmware étant unidirectionnel (aucune remontée d'état), les actions ponctuelles sont des
**boutons** plutôt que des switches. Les vrais switches restants utilisent `assumed_state` (HA
mémorise la dernière commande envoyée).

| Type | Catégorie | Nb | Exemples |
|------|-----------|----|----------|
| `light` | Contrôles | 1 | Lumière ambiante (RGB + brightness + 7 modes) |
| `select` | Contrôles | 1 | Mode de lumière |
| `button` | Contrôles | 15 | Power, Flush, Stop, Self Clean, Wash (3), Massage, Cover, Ring, Light, Eco, Foam, Auto Mode, Blow Dry |
| `button` | Configuration | 16 | +/− pour Volume, Radar, Flush Time, Auto Close Delay, Lid/Ring Open/Close Force |
| `switch` | Configuration | 6 | Auto Flush, Auto Foam, Aging Mode, Virtual Seat, User 1/2 |
| `number` | Contrôles | 5 | Seat / Water / Wind Temperature, Water Pressure, Nozzle Position |
| `sensor` | Diagnostic | 1 | État de connexion |

### SKS Smart Toilet

| Type | Catégorie | Nb | Exemples |
|------|-----------|----|----------|
| `button` | Contrôles | 19 | Wash variantes, Lights, Aroma, Sterilization, Infrared, Flush, User Presets |
| `switch` | Contrôles | 4 | Foam Shield, Blow Dry, Cover, Ring |
| `switch` | Configuration | 20 | Auto Aroma, Auto Foam, Auto Deodorizer, Radar, Foot Sensor, Buzzer, Display, Sterilizations, etc. |
| `number` | Contrôles | 6 | Position, Pressure, Seat / Water / Wind Temperature, Wind Speed |
| `number` | Configuration | 6 | Radar Level, Flush Level, Cover/Ring Force, Post-Leave Flush Time, Auto Close Delay |
| `sensor` | Diagnostic | 1 | État de connexion |

## Langue de l'interface

Les noms d'entités et le config flow sont localisés. La langue affichée suit la langue de l'utilisateur
HA (Profil utilisateur > Langue).

Langues fournies : `en`, `fr`. Pour ajouter une langue, créer un fichier `translations/<code>.json`
en s'inspirant de `translations/en.json` ou `translations/fr.json`.

## Dépannage

### `Failed to send command: 'HaBleakClientWrapper' object has no attribute 'get_services'`

Bug d'une version antérieure de l'intégration. Mettre à jour vers la dernière version. La méthode
`get_services()` est obsolète, le code utilise désormais la propriété `services`.

### Les entités ne sont pas créées

- Vérifier que les fichiers sont dans `/config/custom_components/smart_toilet_ble/`
- Vérifier que le dossier `translations/` est bien présent
- Redémarrer HA
- Vider le cache navigateur (Ctrl+Shift+R)

### `BLE device ... not discovered yet`

- HA ne voit pas le WC en BLE. Causes possibles :
  - Le WC n'est pas allumé / hors de portée
  - Le téléphone est déjà connecté en BLE (cf. plus haut)
  - Pas d'adaptateur BLE sur HA — ajouter un dongle USB ou un ESPHome `bluetooth_proxy`

### Les commandes partent (`Command sent: aa08...`) mais le WC ne réagit pas

- **Mauvais protocole sélectionné**. Supprimer et reconfigurer en choisissant l'autre (DM ↔ SKS).
- Vérifier dans les logs `Command sent: ...` que les codes correspondent au protocole — par exemple
  pour Water Pressure en DM, on doit voir `aa080221xxXXXXxx` (function `0x21` = 33). Si on voit
  `aa080243...`, c'est qu'on est sur une vieille version (codes faux). Mettre à jour.

### Aucune remontée d'état (toggles "Auto Flush" toujours faux, etc.)

C'est **par conception** sur DM : le firmware n'envoie aucune notification BLE, et l'app officielle
n'en reçoit pas non plus. Les switches utilisent `assumed_state=True` — HA suppose que la dernière
commande envoyée correspond à l'état réel. Si tu agis sur le WC depuis la télécommande physique, HA
n'en saura rien.

SKS : les notifications sont parsées quand reçues, normalement les sliders se mettent à jour si le
firmware envoie des trames.

### Activer les logs DEBUG

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.smart_toilet_ble: debug
    bleak: debug
    bleak_retry_connector: debug
```

## Mise à jour

### Via HACS
HACS > Integrations > Smart Toilet BLE > Update

### Manuellement
1. Supprimer `/config/custom_components/smart_toilet_ble/`
2. Recopier la nouvelle version (penser au dossier `translations/`)
3. Redémarrer HA

> Les `unique_id` des entités sont stables, donc tes automations / scripts continuent de marcher
> après la mise à jour. Seul le **nom affiché** peut changer (suite à la traduction).

## Désinstaller

1. Paramètres > Appareils & services > Smart Toilet BLE > Supprimer
2. `rm -rf /config/custom_components/smart_toilet_ble`
3. Redémarrer HA
