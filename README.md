# 🦊 ClassDojo for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HA version](https://img.shields.io/badge/Home%20Assistant-2024.4%2B-blue.svg)](https://www.home-assistant.io/)

Intégration Home Assistant pour **ClassDojo**, permettant de suivre la
progression, les points et les classes de vos élèves directement depuis
Home Assistant et HACS.

> 🇬🇧 A Home Assistant integration for **ClassDojo** that exposes student
> points, classes, and skills as sensors — installable via HACS or manually.

---

## 🇫🇷 Français

### ✨ Fonctionnalités

- Authentification via identifiants ClassDojo (nom d'utilisateur / e-mail + mot de passe).
- Sélection multi-comptes : choisissez l'élève à suivre parmi ceux rattachés au compte.
- Capteurs (« sensors ») exposés pour chaque élève :
  - **Total des points** (trophy)
  - **Points positifs** / **points négatifs** / **points « à améliorer »**
  - **Nombre de classes actives**
  - **Nombre de compétences (skills)**
  - **Dernière activité** (horodatage)
- Intervalle de rafraîchissement configurable (5 minutes à 12 heures).
- Flux de configuration via interface utilisateur (config flow) avec sélection de l'élève.
- Options modifiables après installation (scan interval).
- Traductions intégrées 🇫🇷 / 🇬🇧.

### 📦 Installation via HACS

1. Ouvrez **HACS** → **Intégrations** → ⋯ → **Dépôts personnalisés**.
2. Ajoutez ce dépôt : `https://github.com/Krohler06/ha-classdojo`
   (catégorie : *Integration*).
3. Recherchez **ClassDojo** dans HACS et cliquez sur **Télécharger**.
4. Redémarrez Home Assistant.
5. Allez dans **Paramètres** → **Appareils et services** → **Ajouter une intégration** → **ClassDojo**.
6. Saisissez vos identifiants, sélectionnez l'élève, puis terminez.

### 🛠 Installation manuelle

1. Copiez le dossier `custom_components/classdojo/` dans le répertoire
   `config/custom_components/` de votre installation Home Assistant.
2. Redémarrez Home Assistant.
3. Ajoutez l'intégration **ClassDojo** depuis l'interface (voir étape 5 ci-dessus).

### ⚙️ Configuration

| Paramètre          | Description                                            | Obligatoire |
|--------------------|--------------------------------------------------------|-------------|
| `username`         | Nom d'utilisateur ou e-mail ClassDojo                  | ✅          |
| `password`         | Mot de passe ClassDojo                                 | ✅          |
| `student_id`       | Identifiant de l'élève à suivre                        | ✅          |
| `scan_interval`    | Intervalle de rafraîchissement en minutes (5–720)      | optionnel   |

### 🤖 Exemples d'automatisations

```yaml
# Notification quand un élève atteint 100 points positifs
automation:
  - alias: "ClassDojo - 100 points positifs"
    trigger:
      - platform: numeric_state
        entity_id: sensor.classdojo_<eleve>_positive_points
        above: 99
        below: 101
    action:
      - service: notify.mobile_app
        data:
          title: "🎉 Bravo !"
          message: "{{ trigger.entity_id }} vient de dépasser 100 points positifs !"
```

```yaml
# Message Telegram hebdomadaire récapitulatif
automation:
  - alias: "ClassDojo - Récap hebdomadaire"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: time
        weekday:
          - fri
    action:
      - service: telegram_bot.send_message
        data:
          message: >-
            📊 Récap ClassDojo :
            Total : {{ states('sensor.classdojo_<eleve>_total_points') }} pts,
            Positifs : {{ states('sensor.classdojo_<eleve>_positive_points') }} pts,
            Négatifs : {{ states('sensor.classdojo_<eleve>_negative_points') }} pts.
```

### ⚠️ Avertissement (Disclaimer)

Cette intégration repose sur une **API ClassDojo non officielle**. Elle peut
cesser de fonctionner à tout moment en cas de modification côté ClassDojo.
Les identifiants sont stockés dans la configuration de Home Assistant —
veillez à sécuriser votre installation. Ce projet n'est **pas affilié à
ClassDojo, Inc.** — tous les noms et marques appartiennent à leurs
propriétaires respectifs. Utilisez cette intégration à vos propres risques.

---

## 🇬🇧 English

### ✨ Features

- Login with ClassDojo credentials (username / email + password).
- Multi-student support: pick which student to track from the linked account.
- Exposed sensors per student:
  - **Total points**
  - **Positive points** / **negative points** / **needs-improvement points**
  - **Active class count**
  - **Skills count**
  - **Last activity** (timestamp)
- Configurable refresh interval (5 minutes – 12 hours).
- UI-based config flow with student selection.
- Editable options after install (scan interval).
- Built-in 🇫🇷 / 🇬🇧 translations.

### 📦 HACS Installation

1. Open **HACS** → **Integrations** → ⋯ → **Custom repositories**.
2. Add this repo: `https://github.com/Krohler06/ha-classdojo`
   (category: *Integration*).
3. Search for **ClassDojo** in HACS and click **Download**.
4. Restart Home Assistant.
5. Go to **Settings** → **Devices & Services** → **Add Integration** → **ClassDojo**.
6. Enter your credentials, choose the student, and finish.

### 🛠 Manual Installation

1. Copy `custom_components/classdojo/` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the **ClassDojo** integration from the UI (step 5 above).

### ⚙️ Configuration

| Parameter       | Description                                  | Required |
|-----------------|----------------------------------------------|----------|
| `username`      | ClassDojo username or email                  | ✅       |
| `password`      | ClassDojo password                           | ✅       |
| `student_id`    | ID of the student to track                   | ✅       |
| `scan_interval` | Refresh interval in minutes (5–720)          | optional |

### 🤖 Automation examples

```yaml
# Notify when a student hits 100 positive points
automation:
  - alias: "ClassDojo - 100 positive points"
    trigger:
      - platform: numeric_state
        entity_id: sensor.classdojo_<student>_positive_points
        above: 99
        below: 101
    action:
      - service: notify.mobile_app
        data:
          title: "🎉 Well done!"
          message: "{{ trigger.entity_id }} just passed 100 positive points!"
```

### ⚠️ Disclaimer

This integration relies on an **unofficial ClassDojo API** and may stop
working at any time if ClassDojo changes their backend. Credentials are
stored in the Home Assistant configuration — please secure your instance.
This project is **not affiliated with ClassDojo, Inc.** — all trademarks
belong to their respective owners. Use at your own risk.

---

## 🧩 Development

```bash
# Clone the repo
git clone https://github.com/Krohler06/ha-classdojo.git
cd ha-classdojo

# Symlink into your Home Assistant config
ln -s "$(pwd)/custom_components/classdojo" \
   /path/to/homeassistant/config/custom_components/classdojo
```

Project layout:

```
custom_components/classdojo/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── sensor.py
├── api.py
├── strings.json
└── translations/
    ├── en.json
    └── fr.json
```

## 📄 License

Released under the [MIT License](LICENSE).
