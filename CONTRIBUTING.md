# Contribuer

Issues et pull requests bienvenues.

## Avant d'ouvrir une pull request

1. Installer les dépendances (`pip install -r scripts/requirements.txt`) puis `python -m unittest discover -s tests` passe. À la version 1.1.0, 25 tests hors ligne passent.
2. Tout changement de comportement du script a un test dans `tests/test_prefilter.py` (DNS simulé, jamais de vrai accès réseau dans les tests).
3. Un changement de comportement met à jour `SKILL.md`, `docs/`, `README.md` et `CHANGELOG.md` dans le même commit.
4. Un cas d'évaluation ajouté à `evals/evals.json` n'utilise que des adresses fictives en `.example` (ou les domaines publics déjà listés dans le script).
5. Aucune vraie adresse e-mail, aucune vraie liste : le `.gitignore` refuse `*.csv` sauf `emails_exemple.csv` et `evals/fixtures/*.csv`.
6. Aucune connexion SMTP, jamais : c'est la garantie du projet (un test le vérifie).

## Style

- Documentation en français ; code et noms de variables en anglais ou en français cohérent avec le fichier.
- Python 3.10+.
- Toute commande documentée a été exécutée.
