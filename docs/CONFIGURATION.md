# Configuration

Aucune variable d'environnement, aucune clé, aucun fichier de réglages : il n'y a donc pas de `.env.example`.

## Options de la ligne de commande

| Option | Effet | Défaut |
|---|---|---|
| `--input` | CSV d'entrée | `emails_bruts.csv` |
| `--email-column` | Nom de la colonne d'adresses | `email` |
| `--workers` | Threads pour les requêtes MX | `20` |
| `--delimiter` | Séparateur du CSV (un caractère) ; `;` pour un export Excel français | `,` |

## Réglages internes (dans `scripts/prefilter_emails.py`)

À modifier dans le code, avec un test (voir [../CONTRIBUTING.md](../CONTRIBUTING.md)) :

| Réglage | Où | Effet |
|---|---|---|
| `PERSO_B2C_DOMAINS` | en tête du fichier | domaines personnels flagués, jamais rejetés |
| `DISPOSABLE_DOMAINS` | en tête du fichier | domaines jetables rejetés |
| `EMAIL_REGEX` | en tête du fichier | syntaxe acceptée |
| `timeout` de `_check_mx` | 5 secondes | délai d'une requête DNS avant « incertain » |

Voir aussi : [USAGE.md](USAGE.md).
