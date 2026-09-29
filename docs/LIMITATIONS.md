# Limites

- **Ce n'est pas un vérificateur d'email.** Il ne teste jamais l'existence d'une boîte au niveau SMTP, seulement des signaux gratuits et sans risque (syntaxe, domaine, MX). L'objectif est de réduire le volume à envoyer à un service de vérification payant, pas de le remplacer.
- **Listes de domaines statiques.** `PERSO_B2C_DOMAINS` et `DISPOSABLE_DOMAINS` sont courtes et centrées sur des fournisseurs français. Un domaine jetable absent de la liste passe.
- **MX seulement.** Un domaine sans MX mais avec un enregistrement A peut recevoir du courrier (RFC 5321, section 5.1) : le script le rejette, par choix. Un domaine avec MX peut avoir une boîte inexistante : seule la vérification payante le voit.
- **Dépend du DNS du moment.** Le résultat MX peut changer d'une exécution à l'autre ; une erreur réseau donne « incertain », pas un rejet.
- **Pas de dédoublonnage.** Deux lignes identiques restent deux lignes.
- **Sorties écrasées.** Les deux CSV de sortie sont réécrits à chaque exécution.
- **Pas d'envoi, pas de consentement.** Respecter le RGPD et l'opt-out reste à votre charge : nettoyer une liste ne rend pas son usage légitime. Ce dépôt ne donne pas de conseil juridique.
- **Pas de mesure d'économie.** Aucun pourcentage d'adresses éliminées n'est annoncé : il dépend entièrement de votre liste.
- **Tests hors ligne.** Le DNS est simulé dans les tests ; le comportement sur le DNS réel a été vérifié à la main sur `emails_exemple.csv` (voir [INSTALLATION.md](INSTALLATION.md)).

Voir aussi : [USAGE.md](USAGE.md), [PRIVACY_AND_SECURITY.md](PRIVACY_AND_SECURITY.md).
