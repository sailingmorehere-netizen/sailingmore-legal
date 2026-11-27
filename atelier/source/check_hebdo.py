#!/usr/bin/env python3
"""Check complet hebdomadaire de sailingmore.fr (tâche 53, demandé par Nicolas le 27/11/2026).

DIAGNOSTIQUE ET POSE DES TÂCHES. N'AGIT JAMAIS : aucune modification du site, pas de noindex,
pas de suppression, pas de réécriture. Réseau en lecture seule (GET/HEAD uniquement).

    python3 scripts/check_hebdo.py            # local + en ligne
    python3 scripts/check_hebdo.py --local    # fichiers seulement (réseau fermé)
    python3 scripts/check_hebdo.py --max-url 300

Livrables (écrits dans claude/) :
    claude/rapports-check/check-AAAA-MM-JJ.md   page de rapport datée
    claude/taches-check.json                    tâches proposées (une par famille de problème)
Code de sortie : 0 si rien de bloquant, 1 s'il y a au moins un point « critique ».
"""
import datetime
import glob
import html
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_DIR") or os.path.join(RACINE, "projets/sailingmore/site")
if not os.path.isdir(SITE):
    SITE = "/opt/data/projets/sailingmore/site"
BASE = "https://sailingmore.fr"
HOTE = "sailingmore.fr"
UA = "sailingmore-check-hebdo/1.0 (lecture seule)"
AUJ = datetime.date.today().isoformat()
SORTIE = os.path.join(RACINE, "claude", "rapports-check")
TACHES = os.path.join(RACINE, "claude", "taches-check.json")

LOCAL_SEULEMENT = "--local" in sys.argv
MAX_URL = 200
if "--max-url" in sys.argv:
    MAX_URL = int(sys.argv[sys.argv.index("--max-url") + 1])

# gravité : critique / important / a-voir / info
CONSTATS = []   # (famille, gravité, message)
MESURES = {}    # famille -> texte « mesuré : … » même quand tout va bien


def note(famille, gravite, msg):
    CONSTATS.append((famille, gravite, msg))


def mesure(famille, txt):
    MESURES[famille] = txt


def lire(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def get(url, methode="GET", timeout=20):
    """(code, en-têtes dict minuscule, corps str, durée s, erreur)"""
    req = urllib.request.Request(url, method=methode, headers={"User-Agent": UA})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            corps = r.read(2_000_000).decode("utf-8", "replace") if methode == "GET" else ""
            return r.status, {k.lower(): v for k, v in r.headers.items()}, corps, time.time() - t0, ""
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, "", time.time() - t0, ""
    except Exception as e:  # réseau fermé, DNS, TLS…
        return 0, {}, "", time.time() - t0, f"{type(e).__name__}: {e}"


# ------------------------------------------------------------------ LOCAL
PAGES = sorted(glob.glob(os.path.join(SITE, "*.html")))
PAGES = [p for p in PAGES if not os.path.basename(p).startswith("_")]


def meta(h, nom, attr="name"):
    m = re.search(r'<meta\s[^>]*%s="%s"[^>]*>' % (attr, re.escape(nom)), h, re.I)
    if not m:
        return None
    c = re.search(r'content="([^"]*)"', m.group(0), re.I)
    return html.unescape(c.group(1)) if c else ""


def _urls_sitemap():
    u = set()
    for sm in ("sitemap.xml", "sitemap-bateaux.xml"):
        p = os.path.join(SITE, sm)
        if os.path.exists(p):
            u |= set(re.findall(r"<loc>([^<]+)</loc>", lire(p)))
    return u


URLS_SITEMAP = _urls_sitemap()


def controle_pages_locales():
    titres, descs = defaultdict(list), defaultdict(list)
    n = 0
    for p in PAGES:
        nom = os.path.basename(p)
        h = lire(p)
        n += 1
        if h.lstrip().lower().startswith("<meta http-equiv=\"refresh\"") or len(h) < 300:
            continue
        m = re.search(r"<title>(.*?)</title>", h, re.S | re.I)
        t = html.unescape(m.group(1)).strip() if m else ""
        d = meta(h, "description") or ""
        rob = (meta(h, "robots") or "").lower()
        if "noindex" in rob:
            if BASE + "/" + nom in URLS_SITEMAP:
                note("noindex", "critique", f"{nom} : noindex ALORS QUE la page est dans le sitemap (« {rob} »)")
            else:
                note("noindex", "info", f"{nom} : noindex hors sitemap (« {rob} ») — cohérent")
        if not t:
            note("title", "critique", f"{nom} : pas de <title>")
        else:
            titres[t].append(nom)
            if not 15 <= len(t) <= 65:
                note("title", "a-voir", f"{nom} : title de {len(t)} car. (borne 15–65) « {t[:60]} »")
        if not d:
            note("description", "important", f"{nom} : pas de meta description")
        else:
            descs[d].append(nom)
            if not 70 <= len(d) <= 165:
                note("description", "a-voir", f"{nom} : description de {len(d)} car. (borne 70–165)")
        c = re.search(r'<link\s[^>]*rel="canonical"[^>]*href="([^"]+)"', h, re.I)
        if not c:
            note("canonical", "important", f"{nom} : pas de canonical")
        elif not c.group(1).startswith(BASE):
            note("canonical", "important", f"{nom} : canonical hors domaine {c.group(1)}")
        elif not nom.startswith(("index", "404")) and not c.group(1).endswith(nom) and nom.replace(".html", "") not in c.group(1):
            note("canonical", "a-voir", f"{nom} : canonical ne correspond pas au fichier ({c.group(1)})")
        # JSON-LD
        for i, bloc in enumerate(re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S | re.I)):
            try:
                json.loads(bloc)
            except Exception as e:
                note("jsonld", "important", f"{nom} : JSON-LD n°{i+1} invalide ({e})")
        # og
        img = meta(h, "og:image", "property")
        if not img:
            note("og", "a-voir", f"{nom} : pas d'og:image")
        else:
            if not meta(h, "og:image:alt", "property"):
                note("og", "a-voir", f"{nom} : og:image sans og:image:alt")
            loc = img.replace(BASE + "/", "")
            if img.startswith(BASE) and not os.path.exists(os.path.join(SITE, loc)):
                note("images", "important", f"{nom} : og:image introuvable ({loc})")
        # images annoncées introuvables
        for src in set(re.findall(r'<img\b[^>]*\bsrc="([^"#?]+)', h, re.I)):
            if src.startswith(("http", "data:", "//")):
                if src.startswith(BASE):
                    src = src[len(BASE) + 1:]
                else:
                    continue
            if not os.path.exists(os.path.join(SITE, src.lstrip("/"))):
                note("images", "important", f"{nom} : image absente {src}")
        # liens internes cassés
        for href in set(re.findall(r'<a\b[^>]*\bhref="([^"]+)"', h, re.I)):
            href = href.split("#")[0].split("?")[0]
            if href.startswith(BASE):
                href = href[len(BASE):]
            if not href or href.startswith(("http", "mailto:", "tel:", "javascript:", "//", "data:")):
                continue
            cible = href.lstrip("/") or "index.html"
            if cible.endswith("/"):
                cible += "index.html"
            if not os.path.exists(os.path.join(SITE, cible)) and not os.path.exists(os.path.join(SITE, cible + ".html")):
                note("liens", "important", f"{nom} : lien interne cassé → {href}")
    for t, noms in titres.items():
        if len(noms) > 1:
            note("title", "a-voir", f"title en doublon ×{len(noms)} « {t[:50]} » : {', '.join(noms[:4])}")
    for d, noms in descs.items():
        if len(noms) > 1:
            note("description", "a-voir", f"description en doublon ×{len(noms)} : {', '.join(noms[:4])}")
    mesure("pages", f"{n} pages .html à la racine du site examinées")


def controle_sitemap_local():
    urls = []
    for sm in ("sitemap.xml", "sitemap-bateaux.xml"):
        p = os.path.join(SITE, sm)
        if os.path.exists(p):
            urls += re.findall(r"<loc>([^<]+)</loc>", lire(p))
    absentes = 0
    for u in urls:
        rel = u.replace(BASE, "").lstrip("/")
        if rel and "." in rel.split("/")[-1] and not os.path.exists(os.path.join(SITE, rel)):
            absentes += 1
            if absentes <= 25:
                note("sitemap", "important", f"sitemap : {u} n'a pas de fichier dans la copie")
    if absentes > 25:
        note("sitemap", "important", f"sitemap : … et {absentes-25} autres absentes")
    mesure("sitemap", f"{len(urls)} URL dans sitemap.xml + sitemap-bateaux.xml, {absentes} sans fichier")
    return urls


def controle_robots_local():
    p = os.path.join(SITE, "robots.txt")
    if not os.path.exists(p):
        note("robots", "important", "robots.txt absent")
        return
    r = lire(p)
    if re.search(r"^\s*Disallow:\s*/\s*$", r, re.M):
        note("robots", "critique", "robots.txt contient « Disallow: / » : tout le site est fermé aux robots")
    if "sitemap" not in r.lower():
        note("robots", "a-voir", "robots.txt ne déclare aucun sitemap")


def controle_fichiers_sensibles_local():
    motifs = ["*.sqlite-journal", "*.bak", "*.bak-*", "*.old", "*.orig", "*~", "*.sql", "*.env", ".env*", "*.log", "*.swp"]
    trouves = []
    for m in motifs:
        trouves += glob.glob(os.path.join(SITE, m))
        trouves += glob.glob(os.path.join(SITE, "**", m), recursive=True)
    trouves = sorted(set(trouves))
    for t in trouves[:30]:
        note("sensibles", "important", f"fichier de sauvegarde dans le dossier publié : {os.path.relpath(t, SITE)} (servi s'il est publié)")
    if len(trouves) > 30:
        note("sensibles", "important", f"… {len(trouves)-30} autres sauvegardes")
    for d in (".git", ".env", ".htpasswd"):
        if os.path.exists(os.path.join(SITE, d)):
            note("sensibles", "critique", f"{d} présent dans le dossier du site")
    # ports.sqlite est publié volontairement ? on le signale en information
    if os.path.exists(os.path.join(SITE, "ports.sqlite")):
        note("sensibles", "info", "ports.sqlite est dans le dossier du site (base lisible si servie ; vérifier qu'elle est voulue publique)")
    ht = os.path.join(SITE, ".htaccess")
    if os.path.exists(ht):
        h = lire(ht)
        for en_tete in ("Strict-Transport-Security", "Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy"):
            if en_tete.lower() not in h.lower():
                note("entetes", "info", f".htaccess ne pose pas {en_tete} (peut venir du serveur — voir le contrôle en ligne)")
    else:
        note("entetes", "info", ".htaccess absent de la copie (l'hébergeur peut le gérer ailleurs)")


# ------------------------------------------------------------------ ORTHOGRAPHE (signalement seulement)
def texte_visible(h):
    h = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", h))


def controle_orthographe():
    depuis = time.time() - 7 * 86400
    recents = [p for p in PAGES if os.path.getmtime(p) >= depuis]
    # sur la copie de travail les mtime sont parfois tous récents : on plafonne
    if len(recents) > 150:
        note("orthographe", "info", f"{len(recents)} pages modifiées sur 7 jours (copie fraîche ?) : seules 150 examinées")
        recents = recents[:150]
    outil = shutil.which("hunspell") or shutil.which("aspell")
    doublons = 0
    for p in recents:
        nom = os.path.basename(p)
        t = texte_visible(lire(p))
        langue = re.search(r'<html[^>]*lang="([a-z]{2})', lire(p)[:600], re.I)
        langue = langue.group(1).lower() if langue else "fr"
        for m in re.finditer(r"\b([A-Za-zÀ-ÿ]{3,})\s+\1\b", t, re.I):
            doublons += 1
            if doublons <= 30:
                note("orthographe", "a-voir", f"{nom} : mot doublé « {m.group(0)} »")
        if re.search(r"\s[,;:.!?]{2,}|[a-zé]\.[A-ZÉ][a-zé]{2}|\s{3,}[a-z]", t) and langue == "fr":
            pass  # trop bruité pour être utile : on ne signale pas
        if outil and langue in ("fr", "en", "de", "it", "es", "pt", "pl"):
            try:
                r = subprocess.run([outil, "-l" if "aspell" in outil else "-l", "-d", langue],
                                   input=t, capture_output=True, text=True, timeout=30)
                mots = sorted(set(w for w in r.stdout.split() if len(w) > 4 and not w.isupper()))
                if 0 < len(mots) <= 40:
                    note("orthographe", "a-voir", f"{nom} ({langue}) : {', '.join(mots[:12])}")
            except Exception:
                pass
    mesure("orthographe", f"{len(recents)} pages récentes examinées ; correcteur {'' if outil else 'absent → seuls les mots doublés sont détectés'}{outil or ''}")


# ------------------------------------------------------------------ EN LIGNE
ENTETES_ATTENDUS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-content-type-options": "X-Content-Type-Options",
    "referrer-policy": "Referrer-Policy",
}


def controle_en_ligne(urls_sitemap):
    code, ent, corps, dt, err = get(BASE + "/")
    if code == 0:
        note("uptime", "info", f"réseau indisponible depuis cet environnement ({err}) : contrôles en ligne non faits — relancer depuis un poste avec réseau")
        mesure("en ligne", "NON MESURÉ (réseau fermé)")
        return
    mesure("uptime", f"accueil : HTTP {code} en {dt:.2f} s")
    if code >= 500:
        note("uptime", "critique", f"accueil en HTTP {code}")
    elif code != 200:
        note("uptime", "important", f"accueil en HTTP {code}")
    if dt > 3:
        note("uptime", "a-voir", f"accueil lent : {dt:.1f} s")
    manquants = [lib for h, lib in ENTETES_ATTENDUS.items() if h not in ent]
    for lib in manquants:
        note("entetes", "important", f"en-tête de sécurité absent : {lib}")
    # TLS
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((HOTE, 443), timeout=15) as s:
            with ctx.wrap_socket(s, server_hostname=HOTE) as ss:
                cert = ss.getpeercert()
        fin = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        reste = (fin - datetime.datetime.utcnow()).days
        mesure("tls", f"certificat valable jusqu'au {fin.date()} ({reste} jours)")
        if reste < 14:
            note("tls", "critique", f"certificat expire dans {reste} jours")
        elif reste < 30:
            note("tls", "important", f"certificat expire dans {reste} jours")
    except Exception as e:
        note("tls", "important", f"TLS non vérifié : {type(e).__name__}: {e}")
    # robots en ligne
    c, _, r, _, _ = get(BASE + "/robots.txt")
    if c != 200:
        note("robots", "important", f"robots.txt en ligne : HTTP {c}")
    elif re.search(r"^\s*Disallow:\s*/\s*$", r, re.M):
        note("robots", "critique", "robots.txt EN LIGNE contient « Disallow: / »")
    # fichiers sensibles : doivent être refusés (403/404), jamais 200
    for chemin in ("/.env", "/.git/config", "/.git/HEAD", "/.htaccess", "/ports.sqlite-journal",
                   "/backup.zip", "/backup.sql", "/site.zip", "/wp-config.php.bak", "/.DS_Store"):
        c, _, corps2, _, _ = get(BASE + chemin)
        if c == 200 and corps2.strip():
            note("sensibles", "critique", f"{chemin} est SERVI (HTTP 200)")
    # pages du sitemap : échantillon étalé
    cibles = [u for u in urls_sitemap if u.startswith(BASE)]
    if len(cibles) > MAX_URL:
        pas = len(cibles) / MAX_URL
        cibles = [cibles[int(i * pas)] for i in range(MAX_URL)]
    codes = defaultdict(list)
    lents = 0
    for u in cibles:
        c, e, _, d, _ = get(u, "HEAD")
        codes[c].append(u)
        if d > 4:
            lents += 1
    for c, us in sorted(codes.items()):
        if c == 200:
            continue
        gr = "critique" if c >= 500 or c == 0 else "important"
        for u in us[:10]:
            note("http", gr, f"HTTP {c} : {u}")
        if c >= 500:
            note("5xx", "critique", f"{len(us)} réponses 5xx dans l'échantillon")
    mesure("http", f"{len(cibles)} URL du sitemap testées en HEAD : " + ", ".join(f"{c}×{len(u)}" for c, u in sorted(codes.items())) + (f" ; {lents} lentes (>4 s)" if lents else ""))
    # PageSpeed (Core Web Vitals, API publique sans clé, peut être limitée)
    api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={BASE}/&strategy=mobile&category=performance"
    c, _, corps3, _, _ = get(api, timeout=60)
    if c == 200:
        try:
            j = json.loads(corps3)
            a = j["lighthouseResult"]["audits"]
            lcp = a["largest-contentful-paint"]["numericValue"] / 1000
            cls = a["cumulative-layout-shift"]["numericValue"]
            tbt = a["total-blocking-time"]["numericValue"]
            mesure("cwv", f"accueil mobile (laboratoire) : LCP {lcp:.1f} s, CLS {cls:.3f}, TBT {tbt:.0f} ms")
            if lcp > 4:
                note("cwv", "important", f"LCP {lcp:.1f} s (> 4 s)")
            elif lcp > 2.5:
                note("cwv", "a-voir", f"LCP {lcp:.1f} s (> 2,5 s)")
            if cls > 0.25:
                note("cwv", "important", f"CLS {cls:.2f} (> 0,25)")
        except Exception as e:
            note("cwv", "info", f"réponse PageSpeed illisible ({e})")
    else:
        note("cwv", "info", f"PageSpeed API indisponible (HTTP {c}) : Core Web Vitals non mesurés cette semaine")


def controle_indexation():
    """Search Console et Bing exigent un compte authentifié : on ne s'en sert pas d'ici
    (aucun identifiant, rien ne s'envoie). On pose donc une ligne de rappel, jamais un faux « OK »."""
    note("indexation", "info",
         "Couverture d'indexation Search Console + Bing NON MESURÉE par ce script (compte requis, interdit ici) : "
         "à relever à la main ou par l'export déposé dans claude/exports-indexation/ (le script le lit s'il existe).")
    dossier = os.path.join(RACINE, "claude", "exports-indexation")
    if os.path.isdir(dossier):
        fichiers = sorted(glob.glob(os.path.join(dossier, "*")))
        if fichiers:
            mesure("indexation", f"export le plus récent : {os.path.basename(fichiers[-1])} (lecture manuelle)")


# ------------------------------------------------------------------ RAPPORT
ORDRE = {"critique": 0, "important": 1, "a-voir": 2, "info": 3}
TITRES = {
    "uptime": "Disponibilité", "http": "Codes HTTP", "5xx": "Erreurs 5xx", "sitemap": "Pages du sitemap",
    "noindex": "noindex", "robots": "robots.txt", "title": "Titles", "description": "Descriptions",
    "canonical": "Canonical", "jsonld": "JSON-LD", "og": "og:image / alt", "liens": "Liens internes",
    "images": "Images", "orthographe": "Orthographe", "entetes": "En-têtes de sécurité",
    "sensibles": "Fichiers sensibles", "tls": "TLS", "indexation": "Indexation", "cwv": "Core Web Vitals",
}


def ecrire_rapport():
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, f"check-{AUJ}.md")
    par = defaultdict(list)
    for fam, gr, msg in CONSTATS:
        par[fam].append((gr, msg))
    crit = sum(1 for _, g, _ in CONSTATS if g == "critique")
    imp = sum(1 for _, g, _ in CONSTATS if g == "important")
    L = [f"# Check hebdomadaire sailingmore.fr — {AUJ}", "",
         f"Mode : {'local seulement' if LOCAL_SEULEMENT else 'local + en ligne'} · "
         f"**{crit} critique(s)**, {imp} important(s), {len(CONSTATS)} constats au total.",
         "Le script diagnostique seulement : rien n'a été modifié, noindexé ni supprimé.", "", "## Mesures", ""]
    for k, v in MESURES.items():
        L.append(f"- **{k}** : {v}")
    L.append("")
    for fam in sorted(par, key=lambda f: min(ORDRE[g] for g, _ in par[f])):
        L += [f"## {TITRES.get(fam, fam)} ({len(par[fam])})", ""]
        for gr, msg in sorted(par[fam], key=lambda x: ORDRE[x[0]])[:40]:
            L.append(f"- [{gr}] {msg}")
        if len(par[fam]) > 40:
            L.append(f"- … {len(par[fam])-40} autres")
        L.append("")
    if not CONSTATS:
        L.append("Aucun constat.")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    # tâches : une par famille ayant au moins un constat ≥ a-voir ; la gravité = la pire
    taches = []
    for fam, items in par.items():
        reels = [(g, m) for g, m in items if g != "info"]
        if not reels:
            continue
        pire = min((g for g, _ in reels), key=lambda g: ORDRE[g])
        taches.append({
            "date": AUJ, "famille": fam, "gravite": pire, "nombre": len(reels),
            "titre": f"Check {AUJ} — {TITRES.get(fam, fam)} : {len(reels)} point(s)",
            "criteres": f"relancer python3 scripts/check_hebdo.py : la famille « {fam} » ne rend plus de constat {pire}",
            "livrable": f"correction dans la copie (sans noindex, sans suppression) + détail dans {os.path.relpath(chemin, RACINE)}",
            "exemples": [m for _, m in reels[:5]],
        })
    taches.sort(key=lambda t: ORDRE[t["gravite"]])
    with open(TACHES, "w", encoding="utf-8") as f:
        json.dump({"date": AUJ, "rapport": os.path.relpath(chemin, RACINE), "taches": taches}, f, ensure_ascii=False, indent=1)
    return chemin, crit, len(taches)


def main():
    controle_pages_locales()
    urls = controle_sitemap_local()
    controle_robots_local()
    controle_fichiers_sensibles_local()
    controle_orthographe()
    if not LOCAL_SEULEMENT:
        controle_en_ligne(urls)
    controle_indexation()
    chemin, crit, nt = ecrire_rapport()
    print(f"rapport : {chemin}\ncritiques : {crit} · tâches proposées : {nt} · constats : {len(CONSTATS)}")
    return 1 if crit else 0


if __name__ == "__main__":
    sys.exit(main())
