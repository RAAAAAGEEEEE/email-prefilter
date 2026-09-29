# Installation

## Prérequis

- Python 3.10+ (`python3 --version`).
- Git pour cloner.
- Un accès DNS sortant (requêtes MX).
- Claude Code, seulement pour l'usage comme skill.

## Comme script

```bash
git clone https://github.com/RAAAAAGEEEEE/email-prefilter
cd email-prefilter
python3 -m venv venv
source venv/bin/activate   # venv\Scripts\activate sous Windows
pip install -r scripts/requirements.txt
```

## Comme skill Claude Code

Installation personnelle (macOS, Linux, Git Bash sous Windows) :

```bash
git clone https://github.com/RAAAAAGEEEEE/email-prefilter ~/.claude/skills/email-prefilter
cd ~/.claude/skills/email-prefilter
python3 -m venv venv && source venv/bin/activate && pip install -r scripts/requirements.txt
```

PowerShell :

```powershell
git clone https://github.com/RAAAAAGEEEEE/email-prefilter "$env:USERPROFILE\.claude\skills\email-prefilter"
```

Installation par projet : cloner dans `.claude/skills/email-prefilter` depuis la racine du projet. Le dossier doit s'appeler `email-prefilter` (le nom du skill dans `SKILL.md`).

## Vérifier

```bash
python -m unittest discover -s tests
```

Résultat attendu : `Ran 25 tests` puis `OK`. Les tests simulent le DNS et n'ont besoin d'aucun accès réseau.

Vérification faite le 2026-09-29 (version 1.1.0) : clone dans un dossier vide, création d'un venv, installation de `scripts/requirements.txt` (dnspython 2.8.0, tqdm 4.70.1), tests, puis exécution de `scripts/prefilter_emails.py` sur `emails_exemple.csv`, sous Windows 11 avec Python 3.11.

## Mettre à jour

```bash
git pull
```

## Désinstaller

Supprimer le dossier cloné (et son `venv`).

Voir aussi : [USAGE.md](USAGE.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
