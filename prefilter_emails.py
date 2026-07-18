#!/usr/bin/env python3
"""Pre-filtre gratuit d'une liste d'emails avant verification payante.

Objectif : eliminer gratuitement, sans jamais faire de handshake SMTP
(uniquement resolution DNS/MX, inoffensive pour la reputation IP), les
emails clairement invalides ou indesirables, avant de payer un verificateur
tiers (NeverBounce/ZeroBounce/Reoon) sur les seuls survivants.

Usage:
    python3 prefilter_emails.py [--input emails_bruts.csv] [--email-column email]
                                 [--workers 20]

Entree : un CSV avec au minimum une colonne `email` (nom de colonne
configurable via --email-column). Toutes les autres colonnes du CSV
d'origine sont conservees telles quelles dans les fichiers de sortie.

Trois couches de filtrage, dans l'ordre :
1. Syntaxe (regex email valide, RFC-simplifie) -> rejet si invalide.
2. Type de domaine :
   - domaine personnel B2C connu (gmail.com, yahoo.fr, ...) -> flag
     seulement (colonne type_domaine="perso_b2c"), jamais rejete d'office :
     une adresse perso reste parfois la seule adresse d'un auto-entrepreneur.
   - domaine jetable connu (mailinator.com, yopmail.com, ...) -> rejet.
3. MX record (requete DNS uniquement, aucune connexion au serveur mail
   lui-meme) -> rejet si le domaine n'a aucun MX ; si la resolution DNS
   echoue par timeout/erreur reseau (pas de reponse ferme "pas de MX"),
   l'email est marque incertain mais GARDE, pas rejete par prudence.

Sortie :
- emails_a_verifier.csv : lignes conservees + colonnes type_domaine/statut_mx.
- emails_rejetes.csv : lignes rejetees + colonne raison_rejet.
- Resume affiche en console.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

import dns.exception
import dns.resolver
from tqdm import tqdm

# Regex email pragmatique (RFC 5322 simplifie) : suffisant pour rejeter les
# fautes de frappe/format grossierement invalide, sans viser une conformite
# RFC totale (inutilement stricte et source de faux rejets).
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

# Domaines personnels B2C courants en France -- flagues, jamais rejetes
# d'office (un auto-entrepreneur/artisan n'a parfois qu'une adresse perso).
PERSO_B2C_DOMAINS = {
    "gmail.com", "yahoo.fr", "yahoo.com", "hotmail.com", "hotmail.fr",
    "outlook.com", "outlook.fr", "orange.fr", "wanadoo.fr", "free.fr",
    "laposte.net", "sfr.fr", "live.fr", "icloud.com", "msn.com",
}

# Domaines jetables/temporaires connus -- rejetes, une adresse jetable ne
# sert a rien pour une campagne de prospection (boite ephemere ou publique).
DISPOSABLE_DOMAINS = {
    "mailinator.com", "yopmail.com", "yopmail.fr", "guerrillamail.com",
    "guerrillamail.info", "10minutemail.com", "10minutemail.net",
    "tempmail.com", "temp-mail.org", "throwawaymail.com", "trashmail.com",
    "getnada.com", "mohmal.com", "sharklasers.com",
}

_mx_cache: Dict[str, str] = {}
_mx_cache_lock = Lock()


def _domain_of(email: str) -> str:
    return email.rsplit("@", 1)[-1].strip().lower()


def _check_mx(domain: str, timeout: float = 5.0) -> str:
    """Retourne 'ok', 'absent', ou 'incertain' -- ne fait AUCUNE connexion
    au serveur mail, uniquement une requete DNS de type MX (query publique
    standard, sans impact sur la reputation d'envoi)."""
    with _mx_cache_lock:
        cached = _mx_cache.get(domain)
        if cached is not None:
            return cached

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, "MX")
        result = "ok" if len(answers) > 0 else "absent"
    except dns.resolver.NXDOMAIN:
        result = "absent"
    except dns.resolver.NoAnswer:
        result = "absent"
    except (dns.exception.Timeout, dns.resolver.NoNameservers, Exception):
        # Erreur reseau/timeout : on ne peut pas conclure a une absence
        # reelle de MX, donc on marque incertain plutot que de rejeter a
        # tort un domaine potentiellement valide.
        result = "incertain"

    with _mx_cache_lock:
        _mx_cache[domain] = result
    return result


def _classify_domain(domain: str) -> Optional[str]:
    """Retourne 'perso_b2c' si domaine personnel connu, sinon None. Ne
    gere pas les domaines jetables ici (traites separement car rejetes)."""
    if domain in PERSO_B2C_DOMAINS:
        return "perso_b2c"
    return None


def prefilter(
    input_path: Path,
    email_column: str = "email",
    workers: int = 20,
) -> None:
    output_dir = input_path.parent
    kept_path = output_dir / "emails_a_verifier.csv"
    rejected_path = output_dir / "emails_rejetes.csv"

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if email_column not in (reader.fieldnames or []):
            print(f"Erreur : colonne '{email_column}' absente de {input_path}. "
                  f"Colonnes trouvees : {reader.fieldnames}")
            sys.exit(1)
        rows = list(reader)
        original_fieldnames = reader.fieldnames or []

    total = len(rows)
    if total == 0:
        print(f"Fichier {input_path} vide, rien a faire.")
        return

    # Premiere passe (rapide, locale) : syntaxe + domaine jetable/perso.
    # On ne garde que les domaines a verifier via DNS pour la 2e passe.
    stage1_kept = []
    stage1_rejected = []
    domains_to_check = set()

    for row in rows:
        email = (row.get(email_column) or "").strip()
        if not email or not EMAIL_REGEX.match(email):
            row["raison_rejet"] = "syntaxe_invalide"
            stage1_rejected.append(row)
            continue

        domain = _domain_of(email)
        if domain in DISPOSABLE_DOMAINS:
            row["raison_rejet"] = "domaine_jetable"
            stage1_rejected.append(row)
            continue

        row["type_domaine"] = _classify_domain(domain) or "pro"
        domains_to_check.add(domain)
        stage1_kept.append(row)

    print(f"Etape 1/2 (syntaxe + domaine jetable) : {len(stage1_kept)} gardes, "
          f"{len(stage1_rejected)} rejetes sur {total}.")

    # Deuxieme passe : resolution MX en parallele, avec cache par domaine
    # (un meme domaine ne declenche qu'une seule requete DNS, meme si
    # plusieurs emails du meme domaine sont presents dans le fichier).
    print(f"Verification MX pour {len(domains_to_check)} domaines distincts "
          f"({workers} threads en parallele)...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_check_mx, d): d for d in domains_to_check}
        for _ in tqdm(as_completed(futures), total=len(futures), desc="MX lookup"):
            pass  # le resultat est deja cache dans _mx_cache par _check_mx

    kept_rows = []
    rejected_rows = list(stage1_rejected)

    for row in stage1_kept:
        domain = _domain_of((row.get(email_column) or "").strip())
        mx_status = _mx_cache.get(domain, "incertain")
        if mx_status == "absent":
            row["raison_rejet"] = "pas_de_mx"
            rejected_rows.append(row)
        else:
            row["statut_mx"] = mx_status  # "ok" ou "incertain"
            kept_rows.append(row)

    # Ecriture des fichiers de sortie.
    kept_fieldnames = list(dict.fromkeys(
        original_fieldnames + ["type_domaine", "statut_mx"]
    ))
    rejected_fieldnames = list(dict.fromkeys(
        original_fieldnames + ["type_domaine", "raison_rejet"]
    ))

    with kept_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=kept_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(kept_rows)

    with rejected_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rejected_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected_rows)

    # Resume console.
    reasons: Dict[str, int] = {}
    for row in rejected_rows:
        reasons[row.get("raison_rejet", "?")] = reasons.get(row.get("raison_rejet", "?"), 0) + 1
    perso_count = sum(1 for row in kept_rows if row.get("type_domaine") == "perso_b2c")
    incertain_count = sum(1 for row in kept_rows if row.get("statut_mx") == "incertain")

    print("\n=== Resume ===")
    print(f"Total traite       : {total}")
    print(f"Gardes             : {len(kept_rows)} -> {kept_path}")
    print(f"Rejetes            : {len(rejected_rows)} -> {rejected_path}")
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  - {reason}: {count}")
    print(f"Dont perso_b2c (flagues, gardes) : {perso_count}")
    print(f"Dont MX incertain (flagues, gardes) : {incertain_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default="emails_bruts.csv", help="CSV d'entree (defaut: emails_bruts.csv)")
    parser.add_argument("--email-column", default="email", help="Nom de la colonne email (defaut: email)")
    parser.add_argument("--workers", type=int, default=20, help="Threads paralleles pour les requetes MX (defaut: 20)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erreur : fichier introuvable : {input_path}")
        sys.exit(1)

    prefilter(input_path, email_column=args.email_column, workers=args.workers)


if __name__ == "__main__":
    main()
