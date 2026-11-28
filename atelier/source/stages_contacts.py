#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Récolte les adresses publiées par les écoles de stages.

    python3 scripts/stages_contacts.py [racine] [--max N]

Pour chaque école de projets/sailingmore/stages.json sans adresse dans
projets/sailingmore/ecoles-contacts.json : ouvre la page d'accueil, puis les
pages contact / mentions légales trouvées dans ses liens, lit les `mailto:` et
les adresses écrites en clair. Aucune adresse n'est devinée ni reconstruite :
sans page source, pas de ligne. Lecture seule (GET), robots.txt respecté,
1 s entre deux requêtes au même domaine. Aucun envoi, aucun formulaire.
"""
import datetime
import json
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from html import unescape
from pathlib import Path

UA = "sailingmore-contacts/1.0 (lecture seule)"
PAUSE = 1.0
MAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
MAILTO = re.compile(r'mailto:([^"\'?\s>]+)', re.I)
LIENS = re.compile(r'href=["\']([^"\']+)["\']', re.I)
MOTS_PAGE = re.compile(r"contact|kontakt|impressum|mentions|legal|imprint|about|"
                       r"contatt|contacto|contato|colofon|privacy", re.I)
GENERIQUES = ("info", "contact", "reservation", "reservations", "booking", "bookings",
              "office", "kontakt", "mail", "hello", "secretariat", "accueil", "stages",
              "inscription", "anmeldung", "segreteria", "reservas", "contacto")
RESERV = ("reservation", "reservations", "booking", "bookings", "reservas", "anmeldung",
          "inscription")
EXT_BAD = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")
DERNIER = {}
ROBOTS = {}


def robots_ok(url):
    p = urllib.parse.urlsplit(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.set_url(base + "/robots.txt")
            rp.read()
        except Exception:  # noqa: BLE001
            rp = None
        ROBOTS[base] = rp
    rp = ROBOTS[base]
    return True if rp is None else rp.can_fetch(UA, url)


def lire(url):
    """GET poli. Renvoie le texte, ou None (refus robots / erreur)."""
    if not robots_ok(url):
        return "ROBOTS"
    dom = urllib.parse.urlsplit(url).netloc
    attente = DERNIER.get(dom, 0) + PAUSE - time.time()
    if attente > 0:
        time.sleep(attente)
    DERNIER[dom] = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            if "html" not in r.headers.get("Content-Type", "html"):
                return None
            return r.read(600_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


def adresses(html):
    html = unescape(html)
    trouvees = [m.group(1) for m in MAILTO.finditer(html)]
    trouvees += MAIL.findall(re.sub(r"<[^>]+>", " ", html))
    out = []
    for a in trouvees:
        a = urllib.parse.unquote(a).strip(".,;:").lower()
        if MAIL.fullmatch(a) and not a.endswith(EXT_BAD) and a not in out \
                and not re.search(r"@(sentry|example|domain|email)\.", a):
            out.append(a)
    return out


def type_de(a):
    loc = a.split("@")[0]
    if loc in RESERV:
        return "réservation"
    return "générique" if loc in GENERIQUES else "contact"


def domaine_repond(mail):
    try:
        socket.getaddrinfo(mail.split("@")[1], None)
        return True
    except OSError:
        return False


def pages_contact(html, base):
    vus = []
    for h in LIENS.findall(html):
        u = urllib.parse.urljoin(base, h.split("#")[0])
        if urllib.parse.urlsplit(u).netloc == urllib.parse.urlsplit(base).netloc \
                and MOTS_PAGE.search(u) and u not in vus and u != base:
            vus.append(u)
    return vus[:4]


def une_ecole(site):
    """-> (mail, source, type) ou (None, motif, None)."""
    motif = "page sans adresse"
    pages = [site]
    i = 0
    while i < len(pages) and i < 5:
        url = pages[i]
        i += 1
        html = lire(url)
        if html == "ROBOTS":
            motif = "robots.txt"
            continue
        if html is None:
            if i == 1:
                return None, "site injoignable", None
            continue
        if i == 1:
            pages += pages_contact(html, url)
        liste = adresses(html)
        if not liste:
            continue
        dom = urllib.parse.urlsplit(site).netloc.lower().removeprefix("www.")
        liste.sort(key=lambda a: (a.split("@")[0] not in GENERIQUES,
                                  dom not in a.split("@")[1]))
        for a in liste:
            if domaine_repond(a):
                return a, url, type_de(a)
    return None, motif, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = Path(args[0] if args else ".")
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 10**6
    stages = json.loads((base / "projets/sailingmore/stages.json").read_text(encoding="utf-8"))
    f = base / "projets/sailingmore/ecoles-contacts.json"
    cur = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"ecoles": []}
    lignes = cur["ecoles"] if isinstance(cur, dict) else cur
    connues = {e["ecole"] for e in lignes if e.get("mail")}
    pris = {str(e["mail"]).lower() for e in lignes if e.get("mail")}
    sites = {}
    for o in stages["offres"]:
        e = o["ecole"]
        if e in connues or e in sites:
            continue
        p = urllib.parse.urlsplit(o.get("site") or o["lien"])
        sites[e] = (o["pays"], f"{p.scheme}://{p.netloc}/")
    refus = {}
    auj = datetime.date.today().isoformat()
    for n, (e, (pays, site)) in enumerate(sites.items()):
        if n >= mx:
            break
        mail, src, typ = une_ecole(site)
        if mail and mail not in pris:
            pris.add(mail)
            lignes = [x for x in lignes if x.get("ecole") != e]
            lignes.append({"ecole": e, "pays": pays, "site": site, "mail": mail,
                           "source": src, "releve": auj, "type": typ})
        else:
            refus[src if not mail else "doublon"] = refus.get(src if not mail else "doublon", 0) + 1
    f.write_text(json.dumps({"maj": auj, "ecoles": lignes}, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    print(f"{sum(1 for e in lignes if e.get('mail'))} adresses · refus : {refus}")


if __name__ == "__main__":
    main()
