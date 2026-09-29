# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Versions selon [SemVer](https://semver.org/lang/fr/).

## [1.1.0] - 2026-09-29

### Ajouté
- `SKILL.md` : le script devient un skill Claude Code (front-matter portable, périmètre, replis, exemples).
- Option `--delimiter` (export Excel français avec `;`) ; lecture des CSV avec BOM UTF-8.
- Un « null MX » (RFC 7505) est désormais traité comme un domaine sans MX (`pas_de_mx`).
- 25 tests hors ligne (DNS simulé) et 5 cas d'évaluation dans `evals/`.
- Documentation complète (`docs/`, `CONTRIBUTING.md`, `SECURITY.md`).

### Modifié
- Le script et ses dépendances sont dans `scripts/` (`scripts/prefilter_emails.py`, `scripts/requirements.txt`) ; la commande de démarrage change en conséquence.
- Une exception inattendue dans un thread de résolution n'est plus avalée silencieusement.
- `LICENSE` porte le nom complet du titulaire du droit d'auteur.

## [1.0.0] - 2026-07-18

Première version : syntaxe, type de domaine, MX.
