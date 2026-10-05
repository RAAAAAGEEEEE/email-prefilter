# email-prefilter

Pré-filtre gratuit d'une liste d'emails (CSV) avant de payer un vérificateur tiers (NeverBounce, ZeroBounce, Reoon...), pour une campagne de prospection email BtoB. Skill Claude Code, utilisable aussi comme simple script Python.

## Comment ça marche

Pour un débutant, trois gestes, et aucun copier-coller du dépôt dans la conversation :

1. **Installer le skill une fois** : `git clone https://github.com/RAAAAAGEEEEE/email-prefilter ~/.claude/skills/email-prefilter`
   (disponible dans tous vos projets), ou le même clone dans `.claude/skills/email-prefilter` à la racine d'un
   projet (disponible dans ce projet seulement). Sous Windows PowerShell, remplacez `~` par
   `$env:USERPROFILE`. Détail : [docs/INSTALLATION.md](docs/INSTALLATION.md).
2. **Le demander** : dans une session Claude Code, écrivez simplement « nettoie cette liste de prospects avant que je paie un vérificateur » en indiquant votre CSV, ou tapez `/email-prefilter`.
3. **Se laisser guider** : Claude charge le skill d'après sa description, lance le script sur votre fichier et vous rend la liste triée (syntaxe, domaine, MX), sans aucun envoi SMTP.

C'est le fonctionnement de tous les skills Claude Code : un dossier avec un `SKILL.md` placé dans
`~/.claude/skills/<nom>/` (personnel) ou `.claude/skills/<nom>/` (projet) ; Claude le charge
automatiquement quand votre demande correspond à sa `description`, et `/<nom>` le lance à la main.
[officiel : [skills](https://code.claude.com/docs/en/skills#where-skills-live), page consultée le 2026-10-05]

## Le problème

Les vérificateurs d'email payants facturent à la vérification. Envoyer une liste brute (fautes de frappe, adresses jetables, domaines sans serveur mail) gaspille du budget sur des lignes qui échoueraient de toute façon.

## Pour qui

Les indépendants et petites équipes qui font de la prospection email BtoB et nettoient leurs listes avant envoi.

## Ce qu'il apporte

Il élimine gratuitement, en local, ce qui est détectable sans jamais se connecter au serveur mail cible, donc **sans aucun risque pour la réputation de l'IP d'envoi** :

1. **Syntaxe** : regex email pragmatique.
2. **Type de domaine** : les domaines personnels (gmail.com, wanadoo.fr...) sont **flagués, jamais rejetés d'office** ; les domaines jetables (mailinator.com, yopmail.com...) sont **rejetés**.
3. **MX** : requête DNS pure. Domaine sans MX ou « null MX » : rejeté. Erreur ou timeout DNS : gardé, marqué incertain.

Seuls les survivants passent ensuite au vérificateur payant.

## Statut

**Bêta, version 1.1.0** (2026-09-29). 25 tests hors ligne (DNS simulé) et 5 cas d'évaluation. Ce n'est pas un vérificateur d'email : il ne teste jamais l'existence d'une boîte. Voir [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Prérequis

- Python 3.10 ou plus récent.
- `dnspython` et `tqdm` (`scripts/requirements.txt`).
- Un accès DNS sortant.

## Démarrage

```bash
git clone https://github.com/RAAAAAGEEEEE/email-prefilter
cd email-prefilter
python3 -m venv venv
source venv/bin/activate   # venv\Scripts\activate sous Windows
pip install -r scripts/requirements.txt
python3 scripts/prefilter_emails.py --input emails_exemple.csv
```

Comme skill Claude Code : cloner dans `~/.claude/skills/email-prefilter`, puis « Nettoie cette liste de prospects avant que je paie un vérificateur » ([docs/INSTALLATION.md](docs/INSTALLATION.md)).

## Exemple minimal

Entrée (`emails_exemple.csv`, fictive) :

```
email,nom_entreprise
contact@exemple.fr,Mon Entreprise
jean@gmail.com,Artisan Solo
test@mailinator.com,Adresse jetable
```

Résumé affiché (sortie réelle du 2026-09-29, DNS réel ; le résultat MX dépend du DNS au moment de l'exécution) :

```
Etape 1/2 (syntaxe + domaine jetable) : 2 gardes, 1 rejetes sur 3.
Verification MX pour 2 domaines distincts (20 threads en parallele)...

=== Resume ===
Total traite       : 3
Gardes             : 1 -> emails_a_verifier.csv
Rejetes            : 2 -> emails_rejetes.csv
  - domaine_jetable: 1
  - pas_de_mx: 1
Dont perso_b2c (flagues, gardes) : 1
Dont MX incertain (flagues, gardes) : 0
```

Fichiers écrits à côté de l'entrée : `emails_a_verifier.csv` (colonnes ajoutées `type_domaine`, `statut_mx`) et `emails_rejetes.csv` (colonne ajoutée `raison_rejet` : `syntaxe_invalide`, `domaine_jetable` ou `pas_de_mx`).

## Architecture

Un script unique en trois passes (syntaxe et domaine en local, puis MX en parallèle avec un cache par domaine). `SKILL.md` en fait un skill Claude Code. Détail : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Configuration

Options `--input`, `--email-column`, `--workers`, `--delimiter` ; aucune variable d'environnement, aucune clé. Détail : [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Sécurité et confidentialité

Aucune connexion SMTP. Les adresses restent sur la machine ; seuls les noms de domaine sont envoyés au résolveur DNS. Une liste d'adresses est une donnée personnelle : ne jamais la committer. Détail : [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).

## Limites

- Ce n'est pas un vérificateur : il ne prouve pas qu'une boîte existe.
- Les listes de domaines personnels et jetables sont statiques et centrées sur la France.
- Pas de dédoublonnage ; les fichiers de sortie existants sont écrasés.
- Respectez la réglementation applicable (RGPD, opt-out) : ce script nettoie une liste, il ne rend pas légitime son utilisation.

Liste complète : [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Feuille de route (non contractuelle)

- Dédoublonnage optionnel des adresses.
- Listes de domaines personnels et jetables extensibles par fichier.

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

MIT, voir [LICENSE](LICENSE). Dépendances : voir [docs/LEGAL_AND_ATTRIBUTION.md](docs/LEGAL_AND_ATTRIBUTION.md).

## Documentation

- [SKILL.md](SKILL.md) : ce que lit Claude
- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/USAGE.md](docs/USAGE.md)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md)
- [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md)
- [docs/LEGAL_AND_ATTRIBUTION.md](docs/LEGAL_AND_ATTRIBUTION.md)
- [evals/README.md](evals/README.md) : cas d'évaluation
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
