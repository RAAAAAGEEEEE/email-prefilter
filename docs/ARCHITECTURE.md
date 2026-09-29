# Architecture

```
email-prefilter/
├── SKILL.md                    skill Claude Code (périmètre, procédure, replis)
├── scripts/
│   ├── prefilter_emails.py     le pré-filtre, un seul fichier
│   └── requirements.txt        dnspython, tqdm
├── tests/                      tests hors ligne (DNS simulé) et rejeu des evals
├── evals/                      cas d'évaluation fictifs (evals.json, fixtures)
├── emails_exemple.csv          exemple fictif
└── docs/                       documentation humaine
```

## Déroulé du script

1. **Lecture** du CSV (UTF-8, BOM toléré, séparateur réglable).
2. **Passe 1, locale** : pour chaque ligne, syntaxe (regex), puis domaine jetable (rejet) ou personnel (flag `perso_b2c`).
3. **Passe 2, DNS** : une requête MX par domaine distinct, en parallèle (`ThreadPoolExecutor`), résultat mis en cache. Un domaine sans MX ou avec un « null MX » (RFC 7505) est rejeté ; une erreur ou un timeout donne « incertain » et la ligne est gardée.
4. **Écriture** de `emails_a_verifier.csv` et `emails_rejetes.csv`, puis résumé.

## Décisions de conception

- **Aucun SMTP.** Un handshake avec le serveur du destinataire expose l'IP d'envoi (rejets, listes noires). Le script n'importe ni `smtplib` ni `socket` ; un test le vérifie.
- **Prudence en cas de doute.** Une erreur réseau ne rejette jamais une adresse.
- **Perso flagué, pas rejeté.** Un indépendant n'a parfois qu'une adresse personnelle.

Voir aussi : [USAGE.md](USAGE.md), [LIMITATIONS.md](LIMITATIONS.md).
