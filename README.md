# email-prefilter

Pré-filtre gratuit d'une liste d'emails (CSV) avant de payer un vérificateur
tiers (NeverBounce, ZeroBounce, Reoon...) — pensé pour une campagne de
prospection email BtoB, mais utilisable pour n'importe quelle liste
d'emails à nettoyer avant envoi.

## Pourquoi

Les vérificateurs d'email payants facturent à la vérification. Envoyer une
liste brute (fautes de frappe, adresses jetables, domaines sans serveur
mail) gaspille du budget sur des lignes qui échoueraient de toute façon.
Ce script élimine gratuitement, en local, tout ce qui est détectable sans
jamais se connecter au serveur mail cible (donc **sans aucun risque pour
la réputation de l'IP d'envoi**) :

1. **Syntaxe** — regex email pragmatique.
2. **Type de domaine** — domaines personnels B2C connus (gmail.com,
   wanadoo.fr, yahoo.fr...) sont **flagués, jamais rejetés d'office** (une
   petite structure n'a parfois qu'une adresse perso). Domaines
   jetables/temporaires (mailinator.com, yopmail.com...) sont **rejetés**.
3. **MX record** — requête DNS pure (aucune connexion SMTP). Domaine sans
   MX : rejeté. Erreur/timeout DNS : gardé mais marqué incertain (principe
   de prudence, on ne rejette jamais un domaine potentiellement valide sur
   la seule base d'un problème réseau transitoire).

Seuls les emails survivants doivent ensuite passer par un vérificateur
payant — la facture s'en trouve réduite au strict nécessaire.

## Installation

```bash
git clone https://github.com/<votre-compte>/email-prefilter.git
cd email-prefilter
python3 -m venv venv
source venv/bin/activate   # venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Usage

```bash
python3 prefilter_emails.py --input emails_bruts.csv
```

Options :
- `--input` : chemin du CSV d'entrée (défaut : `emails_bruts.csv`)
- `--email-column` : nom de la colonne email (défaut : `email`)
- `--workers` : threads parallèles pour les requêtes MX (défaut : 20)

Le CSV d'entrée doit avoir au minimum une colonne `email`. Toutes les
autres colonnes sont conservées telles quelles dans les fichiers de
sortie.

### Sorties

- `emails_a_verifier.csv` — emails conservés, avec deux colonnes
  ajoutées : `type_domaine` (`pro` ou `perso_b2c`) et `statut_mx` (`ok`
  ou `incertain`).
- `emails_rejetes.csv` — emails rejetés, avec `raison_rejet`
  (`syntaxe_invalide`, `domaine_jetable`, ou `pas_de_mx`).
- Un résumé chiffré est affiché dans la console.

### Exemple

```
email,nom_entreprise
contact@exemple.fr,Mon Entreprise
jean@gmail.com,Artisan Solo
test@mailinator.com,Adresse jetable
```

```
$ python3 prefilter_emails.py --input exemple.csv

Etape 1/2 (syntaxe + domaine jetable) : 2 gardes, 1 rejetes sur 3.
Verification MX pour 2 domaines distincts (20 threads en parallele)...
MX lookup: 100%|##########| 2/2

=== Resume ===
Total traite       : 3
Gardes             : 2 -> emails_a_verifier.csv
Rejetes            : 1 -> emails_rejetes.csv
  - domaine_jetable: 1
Dont perso_b2c (flagues, gardes) : 1
Dont MX incertain (flagues, gardes) : 0
```

## Limites à connaître

- **Ce n'est pas un vérificateur d'email.** Il ne teste jamais l'existence
  réelle d'une boîte au niveau SMTP — seulement des signaux gratuits et
  sans risque (syntaxe, domaine, MX). L'objectif est de réduire le volume
  à envoyer à un vrai service de vérification payant, pas de le remplacer.
- Les listes de domaines personnels/jetables sont statiques dans le
  script, centrées sur des fournisseurs français — à étendre selon vos
  besoins (voir `PERSO_B2C_DOMAINS` et `DISPOSABLE_DOMAINS` dans le code).
- Le cache MX est en mémoire, propre à chaque exécution (pas de
  persistance entre deux lancements du script).
- Respectez la réglementation applicable (RGPD, opt-out) pour l'usage
  final de la liste — ce script nettoie une liste, il ne rend pas
  légitime son utilisation.

## Licence

MIT — voir [LICENSE](LICENSE).
