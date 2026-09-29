---
name: email-prefilter
description: >
  Pré-filtre gratuitement une liste d'emails (CSV) avant de payer un
  vérificateur tiers (NeverBounce, ZeroBounce, Reoon...), pour une campagne
  de prospection email BtoB. Trois couches sans risque pour la réputation
  IP (syntaxe, type de domaine perso/jetable, résolution DNS MX, jamais
  de handshake SMTP). À utiliser quand l'utilisateur veut nettoyer une
  liste d'emails de prospection avant envoi ou avant vérification payante,
  réduire le volume à faire vérifier par un service payant, ou détecter les
  adresses jetables/mal formées dans un CSV de prospects.
license: MIT
compatibility: >
  Claude Code (skills personnels ou par projet). Python 3.10+ avec
  dnspython et tqdm (scripts/requirements.txt). Accès DNS sortant requis
  pour la couche MX ; aucune connexion SMTP.
metadata:
  author: Anto1nx
  version: "1.1.0"
  repository: https://github.com/RAAAAAGEEEEE/email-prefilter
allowed-tools: Read Bash(python:*) Bash(python3:*)
---

# Email Prefilter

Version 1.1.0 ([CHANGELOG.md](CHANGELOG.md)).

## Principe

Ne jamais payer un vérificateur d'email tiers sur une liste brute. Éliminer
d'abord gratuitement, en local, tout ce qui est détectable sans connexion au
serveur mail cible :

1. **Syntaxe** : regex email pragmatique, élimine les fautes de format.
2. **Type de domaine** : domaines personnels B2C connus (gmail.com,
   wanadoo.fr...) : **flagués, jamais rejetés d'office** (un artisan solo n'a
   parfois qu'une adresse perso). Domaines jetables/temporaires
   (mailinator.com, yopmail.com...) : **rejetés**, aucune valeur pour une
   campagne.
3. **MX record** : requête DNS pure (aucune connexion SMTP, donc aucun risque
   pour la réputation de l'IP d'envoi). Domaine sans MX, ou avec un « null
   MX » (RFC 7505, le domaine déclare ne recevoir aucun courrier) : rejeté.
   Timeout/erreur DNS : gardé mais marqué incertain (principe de prudence,
   ne jamais rejeter à tort un domaine potentiellement valide).

Seuls les survivants doivent être envoyés à un vérificateur payant (facture
réduite au strict nécessaire).

## Périmètre

- **Dans** : nettoyer un CSV d'adresses avant envoi ou avant vérification
  payante ; expliquer les rejets ; choisir la colonne et le séparateur.
- **Hors** :
  - vérifier qu'une boîte existe (handshake SMTP, `RCPT TO`) : refusé, risque
    pour la réputation de l'IP d'envoi ;
  - envoyer une campagne, gérer le consentement ou l'opt-out ;
  - dédoublonner ou enrichir la liste ;
  - trancher la conformité légale (RGPD, prospection) : à rappeler, pas à
    décider.

## Modes et ordre

1. **Inspecter** : lire l'en-tête du CSV (colonne d'adresses, séparateur).
2. **Exécuter** : lancer le script (commande ci-dessous), jamais autre chose.
3. **Rapporter** : compter gardés, rejetés par raison, perso flagués, MX
   incertains ; rappeler que la suite payante reste nécessaire.

Le script écrit deux fichiers à côté du CSV d'entrée et n'en modifie aucun
autre. Le skill ne modifie pas de code : pas de procédure PLAN/FIX/VERIFY.

## Utilisation

```bash
python3 scripts/prefilter_emails.py --input emails_bruts.csv
```

Options : `--email-column` (défaut `email`), `--workers` (défaut 20),
`--delimiter` (défaut `,` ; `;` pour un export Excel français). Le BOM UTF-8
d'Excel est géré. Colonnes en entrée : au minimum la colonne d'adresses ;
toutes les autres sont conservées dans les sorties.

Sorties (à côté du fichier d'entrée, fichiers existants écrasés) :

- `emails_a_verifier.csv` : survivants, avec `type_domaine` (`pro` /
  `perso_b2c`) et `statut_mx` (`ok` / `incertain`).
- `emails_rejetes.csv` : rejetés, avec `raison_rejet` (`syntaxe_invalide`,
  `domaine_jetable`, `pas_de_mx`).
- Résumé chiffré en console.

Codes de sortie : 0 succès (ou fichier vide), 1 fichier introuvable, colonne
absente ou séparateur invalide.

## Dépendances

```bash
python3 -m venv venv
source venv/bin/activate   # ou venv\Scripts\activate sous Windows
pip install -r scripts/requirements.txt
```

## Replis et erreurs

- Colonne absente : le script liste les colonnes trouvées ; relancer avec
  `--email-column <nom>`, ne pas deviner en silence.
- CSV avec `;` : relancer avec `--delimiter ";"`.
- Beaucoup de `incertain` : réseau ou résolveur DNS bloqué ; relancer plus
  tard, ne pas rejeter ces lignes.
- Dépendances absentes (`ModuleNotFoundError: dns`) : installer
  `scripts/requirements.txt` dans un venv.
- Demande de handshake SMTP : refuser, expliquer, proposer ce skill puis un
  vérificateur payant.

## Exemples d'invocation

- « Nettoie cette liste de prospects avant que je paie NeverBounce. »
- « Pré-filtre mon export Excel, le séparateur est le point-virgule. »
- « Combien d'adresses jetables dans emails_bruts.csv ? »

## Exemple de rapport (sortie réelle du 2026-09-29 sur `emails_exemple.csv`, DNS réel)

```
Total traité       : 3
Gardés             : 1 -> emails_a_verifier.csv
Rejetés            : 2 -> emails_rejetes.csv
  - domaine_jetable: 1
  - pas_de_mx: 1
Dont perso_b2c (flagués, gardés) : 1
Dont MX incertain (flagués, gardés) : 0
```

Le résultat MX dépend du DNS public au moment de l'exécution.

## Limites à connaître

- Ne remplace pas une vérification payante réelle (existence de boîte au
  niveau SMTP) : c'est un pré-filtre, pas un vérificateur. Objectif :
  réduire le volume à faire vérifier, pas éliminer l'étape payante.
- Les listes de domaines perso/jetables sont statiques dans le script,
  centrées sur le marché français : à étendre si besoin.
- Un domaine sans MX mais avec un enregistrement A serait accepté par
  certains serveurs (RFC 5321) : ce script le rejette, par choix.
- Cache MX par domaine en mémoire (par exécution) ; pas de dédoublonnage des
  adresses.

Détail : [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Évaluations, tests, installation

- Cas d'évaluation : [evals/README.md](evals/README.md) (5 cas).
- Tests hors ligne (DNS simulé) : `python -m unittest discover -s tests`
  après installation des dépendances.
- Installation personnelle : `~/.claude/skills/email-prefilter/` ; par
  projet : `.claude/skills/email-prefilter/`
  ([docs/INSTALLATION.md](docs/INSTALLATION.md)).

## Sécurité et confidentialité

Les adresses restent sur la machine ; seuls les **noms de domaine** (pas les
adresses complètes) sont envoyés au résolveur DNS configuré, en requêtes MX.
Aucune connexion SMTP, aucun service tiers. Une liste d'adresses est une
donnée personnelle : ne jamais la committer.
Détail : [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).

## Références et attributions

Dépendances : dnspython (ISC), tqdm (MPL-2.0 et MIT). Détail :
[docs/LEGAL_AND_ATTRIBUTION.md](docs/LEGAL_AND_ATTRIBUTION.md).
