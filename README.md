# ClassDojo pour Home Assistant

Intégration personnalisée Home Assistant pour ClassDojo.

## Installation HACS

1. HACS → Intégrations → ⋮ → Dépôts personnalisés.
2. Ajouter `https://github.com/Krohler06/homeassistant-classdojo` comme **Intégration**.
3. Installer **ClassDojo**, redémarrer Home Assistant puis ajouter l’intégration depuis **Paramètres → Appareils et services**.

## Configuration

L’intégration utilise les identifiants du compte parent ClassDojo. Les données accessibles dépendent du compte et des réponses réellement fournies par ClassDojo.

## Entités

La v2 crée un capteur de compte et des capteurs pour les enfants découverts. Les attributs bruts utiles sont conservés pour faciliter l’analyse et l’évolution de l’intégration.

## Dépannage

Activez les logs ciblés :

```yaml
logger:
  logs:
    custom_components.classdojo: debug
```

Aucun contournement d’authentification ou de protection n’est utilisé. Certaines données peuvent ne pas être disponibles avec un compte parent.
