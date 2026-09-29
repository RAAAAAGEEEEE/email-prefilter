# Évaluations

`evals.json` décrit 5 cas fictifs : entreprises et adresses sont inventées (domaines en `.example`). Chaque cas donne un `prompt`, la sortie attendue en une phrase et des assertions.

| `type` | Sens | Contrôle |
|---|---|---|
| `pipeline` | Le script est lancé sur `input_file` avec `cli` ; le DNS est simulé par `mx_stub` | Automatique : `tests/test_evals.py` compare `expected_kept` et `expected_rejected` |
| `cli-error` | Le script doit échouer avec `expected_exit_code` et un message | Automatique : `tests/test_evals.py` |
| `comportement` | Attente sur ce que fait Claude (refus, périmètre) | À la lecture |

`should_trigger: false` marque un cas où le skill ne doit pas s'appliquer (envoi de campagne). Les assertions de `kind` `humain` se jugent à la lecture de la sortie de Claude.

## Ce qui est automatique

```bash
python -m unittest tests.test_evals
```

Nécessite les dépendances (`pip install -r scripts/requirements.txt`) ; aucun accès réseau.

## Rejouer un cas à la main

1. Ouvrir une session Claude Code avec le skill installé.
2. Coller le `prompt` (les fichiers `input_file` sont dans `evals/fixtures/`).
3. Comparer la sortie à `expected_output` et cocher chaque assertion.

Un cas échoue si une seule assertion échoue. Aucun score n'est publié : ces cas n'ont pas été rejoués en série sur plusieurs modèles.

Voir aussi : [../docs/USAGE.md](../docs/USAGE.md), [../CONTRIBUTING.md](../CONTRIBUTING.md).
