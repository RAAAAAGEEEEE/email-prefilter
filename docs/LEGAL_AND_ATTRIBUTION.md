# Licences et attributions

## Ce dépôt

MIT, voir [../LICENSE](../LICENSE).

## Dépendances

Le script importe deux bibliothèques, installées séparément par `pip` (elles ne sont pas redistribuées dans ce dépôt). Licences relevées le 2026-09-29 dans les métadonnées des paquets installés :

| Bibliothèque | Version testée | Licence |
|---|---|---|
| [dnspython](https://github.com/rthalley/dnspython) | 2.8.0 | ISC |
| [tqdm](https://github.com/tqdm/tqdm) | 4.70.1 | MPL-2.0 et MIT |

## Standards cités

- RFC 7505, « A "Null MX" No Service Resource Record for Domains That Accept No Mail » : un « null MX » déclare qu'un domaine ne reçoit aucun courrier.
- RFC 5321, section 5.1 : repli sur l'enregistrement A en l'absence de MX (cité dans les limites, non appliqué).

Aucun texte tiers n'est reproduit dans ce dépôt.

Voir aussi : [LIMITATIONS.md](LIMITATIONS.md).
