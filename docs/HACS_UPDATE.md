# Mettre à jour l'intégration depuis HACS

Ce dépôt est un dépôt personnalisé HACS. La branche par défaut est `main`. Sans release ni tag, HACS peut afficher un SHA de commit à la place d'un numéro de version : **cela ne signifie pas qu'un tag est nécessaire pour récupérer les derniers changements**. Pour ce dépôt, le commit `16e03c7` est ancien ; les correctifs e-mail et compatibilité des entrées existantes figurent déjà dans `main` à partir de `96a57d4`.

1. Vérifier dans HACS que le dépôt personnalisé est `Krohler06/ha-classdojo` et que la catégorie est **Integration**. Si une branche ou une version a été épinglée, sélectionner la branche par défaut (`main`).
2. Dans HACS, ouvrir ClassDojo, actualiser les informations du dépôt, puis choisir **Retélécharger** (ou **Mettre à jour** si proposé). Si un sélecteur de version apparaît, choisir la branche `main`, pas une ancienne révision.
3. Redémarrer **Home Assistant** (pas seulement le navigateur). Le dossier chargé doit être `config/custom_components/classdojo` et provenir de ce dépôt.
4. Si HACS continue d'afficher `16e03c7`, consulter la version de HACS, ses journaux et la sélection de branche/version du dépôt ; vérifier qu'aucune copie manuelle de `custom_components/classdojo` n'écrase l'installation. En dernier recours, sauvegarder la configuration puis supprimer et réinstaller **uniquement le téléchargement HACS**. Ne pas supprimer l'entrée d'intégration Home Assistant ni les données utilisateur juste pour corriger le téléchargement.

Les correctifs e-mail ne rendent pas la connexion réelle à ClassDojo opérationnelle : son protocole d'authentification est encore à vérifier. Ne pas partager de HAR complet, de cookies ni de codes e-mail lors du diagnostic.
