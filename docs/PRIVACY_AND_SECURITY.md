# Confidentialité et sécurité

## Ce qui sort de la machine

- **Requêtes DNS MX** : le **nom de domaine** de chaque adresse (`exemple.fr`, jamais l'adresse complète) est envoyé au résolveur DNS configuré sur votre machine (souvent celui de votre fournisseur d'accès). Ce résolveur voit donc la liste des domaines de vos prospects.
- **Rien d'autre** : aucune connexion SMTP, aucun appel à un service tiers, aucune télémétrie.
- Les fichiers de sortie sont écrits localement, à côté du fichier d'entrée.

## Données personnelles

Une liste d'adresses de prospects est une donnée personnelle.

- Ne jamais committer une vraie liste : le `.gitignore` refuse `*.csv` sauf `emails_exemple.csv` (fictif) et `evals/fixtures/*.csv` (fictifs, en `.example`).
- Si vous utilisez le skill dans Claude Code, l'en-tête et les lignes lues par Claude passent par votre session ; limiter la lecture à l'en-tête suffit au skill.
- Supprimer les CSV de sortie quand la campagne est finie.

## Injection de formule (Excel)

Une adresse peut commencer par `+` ou `-` (la regex l'autorise) et une autre colonne peut contenir `=...` : à l'ouverture dans un tableur, ces valeurs peuvent être interprétées comme des formules. Le script recopie les colonnes telles quelles. N'ouvrir les sorties que si l'origine de la liste est sûre, ou les importer en texte.

## Aucune clé, aucune variable d'environnement

Voir [CONFIGURATION.md](CONFIGURATION.md).

## Signaler un problème de sécurité

Voir [../SECURITY.md](../SECURITY.md).

Voir aussi : [LIMITATIONS.md](LIMITATIONS.md).
