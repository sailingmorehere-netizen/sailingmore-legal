#!/usr/bin/env python3
"""Compter les clics qui sortent vers les écoles — sans cookie, sans traceur, sans consentement.

Le problème : les pages de stages envoient le visiteur chez l'école, et rien ne dit combien de fois.
Sans ce chiffre, aucune école ne peut être facturée et aucune preuve ne peut lui être montrée.

La solution tient à trois morceaux, tous chez nous :

1. `go-liens.json` — la liste blanche : un identifiant court par lien, et l'adresse qu'il ouvre. Aucune
   adresse n'est acceptée si elle n'est pas dans cette liste, donc pas de redirection ouverte.
2. `go.php` — une page de notre hébergement qui note une ligne dans un fichier puis renvoie vers l'école
   par un 302. Rien n'est écrit dans le navigateur du visiteur : ni cookie, ni identifiant, ni adresse IP.
3. `clics-AAAAMM.tsv` — une ligne par clic : date, identifiant du lien, page d'où l'on part. C'est tout.
   Aucune donnée personnelle, donc aucune bannière de consentement à ajouter.

Ce que ça permet de dire à une école : « ton stage a été cliqué 37 fois depuis le 1er novembre ».

    python3 scripts/clics_sortants.py --carte      # reconstruit go-liens.json + go.php dans le site
    python3 scripts/clics_sortants.py --lire       # télécharge les compteurs et fait le tableau
    python3 scripts/clics_sortants.py --lire --json
"""
from __future__ import annotations

import json
import os
import sys
import zlib
from collections import Counter
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
SITE = Path(os.environ.get("SITE_PUBLIE", str(RACINE / "cache" / "rhum" / "site")))
DONNEES = RACINE / "projets" / "sailingmore"
IDENT = Path("/opt/data/credentials/ovh-ftp.txt")

GO_PHP = r"""<?php
// Compte un clic sortant puis renvoie vers l'école. Ni cookie, ni traceur, ni adresse IP enregistrée.
// Liste blanche : seule une adresse présente dans go-liens.json peut être ouverte.
$carte = json_decode(@file_get_contents(__DIR__ . '/go-liens.json'), true);
if (!is_array($carte)) { http_response_code(503); exit('carte absente'); }
$id = preg_replace('/[^0-9a-f]/', '', $_GET['id'] ?? '');
$page = preg_replace('/[^a-z0-9\-]/', '', $_GET['p'] ?? '');
$url = $carte[$id] ?? '';
if ($url === '') { http_response_code(404); exit('lien inconnu'); }
$dossier = __DIR__ . '/../donnees';
if (!is_dir($dossier)) { @mkdir($dossier, 0755, true); }
@file_put_contents($dossier . '/clics-' . date('Ym') . '.tsv',
    date('Y-m-d H:i') . "\t" . $id . "\t" . $page . "\n", FILE_APPEND | LOCK_EX);
header('Cache-Control: no-store');
header('Location: ' . $url, true, 302);
exit;
"""


def identifiant(url: str) -> str:
    """Identifiant court et stable d'une adresse (8 caractères hexadécimaux)."""
    return format(zlib.crc32(url.encode("utf-8")) & 0xFFFFFFFF, "08x")


def lien(url: str, page: str = "") -> str:
    """L'adresse à mettre dans un `href` : elle passe par go.php et sera comptée."""
    if not url:
        return url
    suffixe = f"&p={page}" if page else ""
    return f"go.php?id={identifiant(url)}{suffixe}"


def carte() -> dict:
    """Toutes les adresses sortantes connues : offres de stages, puis fiches d'écoles."""
    sortie: dict[str, str] = {}
    stages = DONNEES / "stages.json"
    if stages.exists():
        for o in json.loads(stages.read_text(encoding="utf8")).get("offres", []):
            u = (o.get("lien") or "").strip()
            if u.startswith("http"):
                sortie[identifiant(u)] = u
    ecoles = DONNEES / "ecoles.json"
    if ecoles.exists():
        for e in json.loads(ecoles.read_text(encoding="utf8")):
            for u in e.get("urls") or []:
                u = (u or "").strip()
                if u.startswith("http"):
                    sortie[identifiant(u)] = u
    # Les groupes Facebook de la bourse aux équipiers (26/11/2026) : sans eux dans la liste blanche,
    # `go.php` répondait 404 et les treize liens de la page ne s'ouvraient pas.
    bourses = DONNEES / "bourses.json"
    if bourses.exists():
        for b in json.loads(bourses.read_text(encoding="utf8")):
            u = (b.get("lien") or "").strip()
            if u.startswith("http"):
                sortie[identifiant(u)] = u
    return sortie


def ecrire(dossier: Path = SITE) -> dict:
    """Écrit go-liens.json et go.php dans le dossier publié. Rend le compte par école."""
    c = carte()
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "go-liens.json").write_text(json.dumps(c, ensure_ascii=False, sort_keys=True), encoding="utf8")
    (dossier / "go.php").write_text(GO_PHP, encoding="utf8")
    return c


def _ftp():
    from ftplib import FTP  # noqa: PLC0415

    cfg = dict(l.split("=", 1) for l in IDENT.read_text().splitlines() if "=" in l)
    f = FTP(cfg["hote"], timeout=30)
    f.login(cfg["utilisateur"], cfg["motdepasse"])
    return f, cfg["racine"]


def lire(par_ecole: bool = True) -> dict:
    """Télécharge les compteurs mensuels et agrège les clics."""
    from io import BytesIO  # noqa: PLC0415

    f, racine = _ftp()
    lignes: list[str] = []
    noms: list[str] = []
    try:
        f.cwd("/")
        try:
            f.cwd("donnees")
        except Exception:  # noqa: BLE001
            return {"clics": 0, "fichiers": [], "detail": {}}
        noms = [n for n in f.nlst() if n.startswith("clics-") and n.endswith(".tsv")]
        for n in noms:
            tampon = BytesIO()
            f.retrbinary(f"RETR {n}", tampon.write)
            lignes += [l for l in tampon.getvalue().decode("utf8", "replace").splitlines() if l.strip()]
    finally:
        try:
            f.quit()
        except Exception:  # noqa: BLE001
            pass

    ecole_par_id: dict[str, str] = {}
    stages = DONNEES / "stages.json"
    if stages.exists():
        for o in json.loads(stages.read_text(encoding="utf8")).get("offres", []):
            u = (o.get("lien") or "").strip()
            if u.startswith("http"):
                ecole_par_id[identifiant(u)] = o.get("ecole") or o.get("ecole_slug") or "?"
    compte = Counter()
    pages = Counter()
    for l in lignes:
        m = l.split("\t")
        if len(m) >= 3:
            compte[ecole_par_id.get(m[1], m[1])] += 1
            pages[m[2] or "(direct)"] += 1
    return {"clics": len(lignes), "fichiers": len(noms),
            "detail": dict(compte.most_common()) if par_ecole else {}, "pages": dict(pages.most_common())}


def main() -> int:
    a = sys.argv[1:]
    if "--carte" in a:
        c = ecrire()
        print(f"go-liens.json : {len(c)} adresses ; go.php écrit dans {SITE}")
        return 0
    if "--lire" in a:
        r = lire()
        if "--json" in a:
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0
        print(f"{r['clics']} clics sortants enregistrés")
        for e, n in r["detail"].items():
            print(f"  {n:4d}  {e}")
        return 0
    sys.exit("choisir --carte ou --lire")


if __name__ == "__main__":
    raise SystemExit(main())
