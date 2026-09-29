# Utilisation

## Dans Claude Code

Le skill se charge pour une demande de nettoyage de liste d'adresses. On peut aussi le nommer : « avec le skill email-prefilter, … ».

| Demande | Ce que fait Claude |
|---|---|
| « Nettoie cette liste avant que je paie un vérificateur » | Lit l'en-tête, lance le script, rend le résumé |
| « Mon export Excel utilise le point-virgule » | Ajoute `--delimiter ";"` et `--email-column` |
| « Combien d'adresses jetables ? » | Lance le script et lit `emails_rejetes.csv` |
| « Vérifie que les boîtes existent (SMTP) » | Refuse la partie SMTP, propose le pré-filtre puis un vérificateur payant |

## En ligne de commande

```bash
python3 scripts/prefilter_emails.py --input emails_bruts.csv
python3 scripts/prefilter_emails.py --input export.csv --email-column "E-mail" --delimiter ";"
```

Options : [CONFIGURATION.md](CONFIGURATION.md).

### Entrée

Un CSV en UTF-8 (avec ou sans BOM) avec au minimum une colonne d'adresses. Toutes les autres colonnes sont conservées.

### Sorties

Écrites dans le dossier du fichier d'entrée, **fichiers existants écrasés** :

- `emails_a_verifier.csv` : lignes gardées + `type_domaine` (`pro` ou `perso_b2c`) + `statut_mx` (`ok` ou `incertain`).
- `emails_rejetes.csv` : lignes rejetées + `raison_rejet` (`syntaxe_invalide`, `domaine_jetable`, `pas_de_mx`).

### Codes de sortie

- `0` : succès, ou fichier vide (rien à faire).
- `1` : fichier introuvable, colonne absente, séparateur invalide.

## Ensuite

Envoyer `emails_a_verifier.csv` à un vérificateur payant. Les lignes `perso_b2c` sont à traiter selon votre cible (une adresse perso peut être la seule d'un indépendant) ; les lignes `incertain` méritent un second passage du pré-filtre plus tard.

## Rejouer les cas d'évaluation

Voir [../evals/README.md](../evals/README.md).

Voir aussi : [LIMITATIONS.md](LIMITATIONS.md).
