# Dépannage

## `ModuleNotFoundError: No module named 'dns'` (ou `tqdm`)

Les dépendances ne sont pas installées dans l'environnement actif :

```bash
pip install -r scripts/requirements.txt
```

Utiliser un venv (voir [INSTALLATION.md](INSTALLATION.md)).

## `Erreur : colonne 'email' absente`

Le message liste les colonnes trouvées. Relancer avec le bon nom :

```bash
python3 scripts/prefilter_emails.py --input liste.csv --email-column contact
```

Si une seule colonne est trouvée avec des `;` dedans, le séparateur est faux : ajouter `--delimiter ";"`.

## Colonne introuvable alors qu'elle existe (export Excel)

Excel ajoute un BOM UTF-8 ; le script le gère depuis la version 1.1.0. Avec une version plus ancienne, la première colonne s'appelle `﻿email`. Mettre à jour (`git pull`).

## Beaucoup de lignes « incertain »

Le résolveur DNS ne répond pas (réseau coupé, pare-feu, VPN). Ces lignes sont **gardées**, pas rejetées. Vérifier le réseau et relancer.

## Un domaine valide est rejeté `pas_de_mx`

Le script rejette les domaines sans enregistrement MX, ou avec un « null MX ». Un domaine qui reçoit du courrier sur son enregistrement A sans MX est rejeté par choix (voir [LIMITATIONS.md](LIMITATIONS.md)). Vérifier à la main : `nslookup -type=MX domaine.tld`.

## Mes sorties précédentes ont disparu

Les fichiers `emails_a_verifier.csv` et `emails_rejetes.csv` sont écrasés à chaque exécution, dans le dossier du fichier d'entrée. Les copier avant de relancer.

Voir aussi : [USAGE.md](USAGE.md).
