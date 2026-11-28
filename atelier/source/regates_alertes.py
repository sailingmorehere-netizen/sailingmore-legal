#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Alertes régates par filtre : relais d'inscription + résumé du lundi.

Deux usages, une seule source pour les filtres (segment) et pour Brevo :

    python3 scripts/regates_alertes.py serveur             # relais HTTP : inscription, désinscription
    python3 scripts/regates_alertes.py lundi               # SIMULE le résumé du lundi (rien n'est envoyé ni écrit)
    python3 scripts/regates_alertes.py lundi --envoyer     # envoie vraiment, puis écrit l'état

Tout se règle par variables d'environnement — jamais de clé dans le code ni dans la page :
    BREVO_API_KEY            clé API créée par Nicolas (côté serveur seulement)
    BREVO_LISTE_ALERTES_ID   id numérique de la liste « alerte régates »   (nom provisoire : « Alertes régates »)
    BREVO_LISTE_PROMO_ID     id numérique de la liste « promo »            (nom provisoire : « Promo Sailing More »)
    BREVO_DOI_TEMPLATE       id du modèle de mail de confirmation (double opt-in) ; BREVO_DOI_TEMPLATE_DE, _EN… par langue
    ALERTES_SECRET           secret des liens de désinscription (HMAC)
    ALERTES_BASE_URL         URL publique du relais, ex. https://sailingmore.fr/api (sans « / » final)
    ALERTES_EXPEDITEUR       adresse d'expédition validée chez Brevo ; ALERTES_EXPEDITEUR_NOM (défaut « Sailing More »)
    ALERTES_MERCI_URL        page où Brevo renvoie après confirmation (défaut https://sailingmore.fr/merci.html)

La position du visiteur n'existe nulle part ici : le relais ne lit que les champs listés dans `lire_inscription`.
Le texte libre de la recherche n'est pas transmis non plus.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regates_classes  # noqa: E402
import regates_page  # noqa: E402

ICI = regates_page.ICI
ETAT = ICI / "projets/sailingmore/alertes_vus.json"  # clé d'épreuve → date de première vue
LANGUES = ("fr", "de", "en", "it", "es", "pt")
# Horizon : jours à partir d'aujourd'hui ; « tout » = toutes les épreuves à venir.
HORIZONS = {"30": 30, "90": 90, "365": 365, "tout": None}
API = "https://api.brevo.com/v3"


def env(nom: str, defaut: str = "") -> str:
    return os.environ.get(nom, defaut)


# ── Brevo ────────────────────────────────────────────────────────────────────
def brevo(methode: str, chemin: str, corps: dict | None = None) -> dict:
    cle = env("BREVO_API_KEY")
    if not cle:
        raise SystemExit("BREVO_API_KEY absente de l'environnement")
    req = urllib.request.Request(
        API + chemin, method=methode,
        data=json.dumps(corps).encode() if corps is not None else None,
        headers={"api-key": cle, "accept": "application/json", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        brut = r.read()
    return json.loads(brut) if brut else {}


# ── Le segment : un filtre = (région, type, classe, horizon), rien d'autre ───
def propre(v: str, autorises: tuple | None = None, defaut: str = "", maxi: int = 24) -> str:
    v = (v or "").strip()
    if autorises is not None:
        return v if v in autorises else defaut
    return v if re.fullmatch(r"[\w .+\-/']{1,%d}" % maxi, v) else defaut


def segment_de(attrs: dict) -> tuple[str, str, str, str]:
    return (propre(attrs.get("REGION", ""), regates_page.REGIONS),
            propre(attrs.get("TYPE", ""), regates_page.TYPES),
            "" if attrs.get("CLASSE") in ("tous", "tout") else propre(attrs.get("CLASSE", "")),
            propre(attrs.get("HORIZON", ""), tuple(HORIZONS), "tout"))


def correspond(e: dict, seg: tuple[str, str, str, str], aujourdhui: date) -> bool:
    """Même règle que `passe()` de la page : le mail n'annonce que ce que le filtre montrerait."""
    region, type_, classe, horizon = seg
    if region and e["region"] != region:
        return False
    if type_ and e["type"] != type_:
        return False
    if classe == "__inter":
        if not any(c.upper() in regates_classes.JAUGES for c in e["classes"]):
            return False
    elif classe and classe not in e["classes"]:
        return False
    jours = HORIZONS.get(horizon)
    if jours is not None and e["debut"] > (aujourdhui + timedelta(days=jours)).isoformat():
        return False
    return not e.get("annulee")


# ── Désinscription : lien signé, une liste à la fois ─────────────────────────
def jeton(email: str, liste: str) -> str:
    secret = env("ALERTES_SECRET")
    if not secret:
        raise SystemExit("ALERTES_SECRET absent de l'environnement")
    return hmac.new(secret.encode(), f"{email.lower()}|{liste}".encode(), hashlib.sha256).hexdigest()[:32]


def lien_desinscription(email: str, liste: str = "alertes") -> str:
    q = urllib.parse.urlencode({"e": email, "l": liste, "t": jeton(email, liste)})
    return f"{env('ALERTES_BASE_URL')}/desinscription?{q}"


# ── Le mail du lundi (six langues) ───────────────────────────────────────────
TXT = {
    "fr": ("Nouvelles régates cette semaine", "Voici les épreuves ajoutées au calendrier cette semaine, qui correspondent à votre alerte :",
           "Se désinscrire de ces alertes", "Votre alerte"),
    "de": ("Neue Regatten diese Woche", "Diese Regatten wurden diese Woche neu aufgenommen und passen zu Ihrem Filter:",
           "Diese Benachrichtigungen abbestellen", "Ihr Filter"),
    "en": ("New races this week", "These races were added to the calendar this week and match your alert:",
           "Unsubscribe from these alerts", "Your alert"),
    "it": ("Nuove regate questa settimana", "Queste regate sono state aggiunte questa settimana e corrispondono al tuo filtro:",
           "Annulla l'iscrizione a questi avvisi", "Il tuo avviso"),
    "es": ("Nuevas regatas esta semana", "Estas regatas se han añadido esta semana y coinciden con tu filtro:",
           "Darse de baja de estos avisos", "Tu alerta"),
    "pt": ("Novas regatas esta semana", "Estas regatas foram adicionadas esta semana e correspondem ao teu filtro:",
           "Cancelar estes alertas", "O teu alerta"),
}


def date_lisible(e: dict) -> str:
    d = date.fromisoformat(e["debut"])
    f = date.fromisoformat(e["fin"] or e["debut"])
    return f"{d.day}/{d.month}/{d.year}" + (f" → {f.day}/{f.month}" if f != d else "")


def corps_mail(langue: str, seg: tuple, epreuves: list[dict]) -> tuple[str, str]:
    sujet, intro, _, _ = TXT[langue]
    lignes = []
    for e in epreuves:
        lieu = " · ".join(x for x in (e["ville"], e["club"]) if x)
        nom = escape(e["nom"])
        if e["lien"]:
            nom = f'<a href="{escape(e["lien"], quote=True)}">{nom}</a>'
        lignes.append(f"<li><b>{escape(date_lisible(e))}</b> — {nom}"
                      + (f"<br><small>{escape(lieu)}</small>" if lieu else "") + "</li>")
    return (f"{sujet} ({len(epreuves)})",
            f"<p>{intro}</p><ul>{''.join(lignes)}</ul>")


DESINSCRIPTION_PROMO = {
    "fr": "Se désinscrire de l'actualité Sailing More", "de": "Neuigkeiten von Sailing More abbestellen",
    "en": "Unsubscribe from Sailing More news", "it": "Annulla l'iscrizione alle novità di Sailing More",
    "es": "Darse de baja de las novedades de Sailing More", "pt": "Cancelar as novidades da Sailing More",
}


def pied(langue: str, email: str, liste: str = "alertes") -> str:
    """Pied d'un envoi : le lien de désinscription de LA liste concernée (alertes ou promo).
    Les deux listes sont indépendantes : se désinscrire de l'une ne retire pas de l'autre.
    Le résumé du lundi passe « alertes » ; tout envoi promo doit passer « promo »."""
    texte = DESINSCRIPTION_PROMO[langue] if liste == "promo" else TXT[langue][2]
    return (f'<hr><p style="font-size:12px"><a href="{escape(lien_desinscription(email, liste), quote=True)}">'
            f"{texte}</a> — Sailing More</p>")


# ── Le lundi ─────────────────────────────────────────────────────────────────
def cle(e: dict) -> str:
    return f"{e['debut']}|{e['nom'].strip().lower()}|{(e['ville'] or '').strip().lower()}"


def contacts_liste(liste_id: str) -> list[dict]:
    out, offset = [], 0
    while True:
        r = brevo("GET", f"/contacts/lists/{liste_id}/contacts?limit=500&offset={offset}")
        lot = r.get("contacts", [])
        out += [c for c in lot if not c.get("emailBlacklisted")]
        offset += 500
        if len(lot) < 500:
            return out


def nouveautes(epreuves: list[dict], aujourdhui: date) -> tuple[list[dict], dict]:
    """Épreuves vues pour la première fois depuis sept jours. `regates.json` ne porte pas de date
    d'ajout : l'état `alertes_vus.json` la tient. Premier passage = on mémorise tout, on n'annonce rien
    (sinon 1 100 « nouveautés » le premier lundi)."""
    premier = not ETAT.exists()
    vus = {} if premier else json.loads(ETAT.read_text())
    iso = aujourdhui.isoformat()
    seuil = (aujourdhui - timedelta(days=7)).isoformat()
    for e in epreuves:
        vus.setdefault(cle(e), (seuil if premier else iso))
    neuves = [] if premier else [e for e in epreuves if vus[cle(e)] > seuil]
    return neuves, vus


def lundi(envoyer: bool) -> int:
    aujourdhui = date.today()
    epreuves = regates_page.epreuves_pour_page(regates_page.charger())
    neuves, vus = nouveautes(epreuves, aujourdhui)
    print(f"{len(neuves)} épreuve(s) ajoutée(s) depuis sept jours")
    if not neuves:
        if envoyer:
            ETAT.write_text(json.dumps(vus, ensure_ascii=False, indent=0))
        return 0  # aucune nouveauté = aucun envoi

    liste = env("BREVO_LISTE_ALERTES_ID")
    if not liste:
        raise SystemExit("BREVO_LISTE_ALERTES_ID absent de l'environnement")
    groupes: dict[tuple, list[str]] = {}
    for c in contacts_liste(liste):
        a = c.get("attributes") or {}
        langue = (a.get("LANGUE") or "fr").lower()
        langue = langue if langue in LANGUES else "fr"
        groupes.setdefault((langue,) + segment_de(a), []).append(c["email"])

    envoyes = 0
    for (langue, *seg), emails in sorted(groupes.items()):
        seg = tuple(seg)
        trouvees = [e for e in neuves if correspond(e, seg, aujourdhui)]
        print(f"  {langue} {seg} : {len(emails)} abonné(s), {len(trouvees)} épreuve(s)")
        if not trouvees:
            continue  # jamais de mail vide
        sujet, haut = corps_mail(langue, seg, trouvees)
        if envoyer:
            for i in range(0, len(emails), 500):
                lot = emails[i:i + 500]
                brevo("POST", "/smtp/email", {
                    "sender": {"email": env("ALERTES_EXPEDITEUR"), "name": env("ALERTES_EXPEDITEUR_NOM", "Sailing More")},
                    "subject": sujet,
                    "htmlContent": haut,
                    # une version par destinataire : personne ne voit les autres adresses
                    "messageVersions": [{"to": [{"email": m}], "htmlContent": haut + pied(langue, m)} for m in lot],
                })
        envoyes += len(emails)
    if envoyer:
        ETAT.write_text(json.dumps(vus, ensure_ascii=False, indent=0))
    print(f"{envoyes} mail(s) {'envoyé(s)' if envoyer else 'à envoyer (simulation)'}")
    return 0


# ── Le relais d'inscription ──────────────────────────────────────────────────
EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")
_essais: dict[str, list[float]] = {}


def lire_inscription(d: dict) -> dict | None:
    """Les seuls champs lus. Ni position, ni texte de recherche, ni rien d'autre."""
    email = str(d.get("email", "")).strip().lower()
    if not EMAIL.match(email) or d.get("site"):  # « site » = piège à robots, doit rester vide
        return None
    if d.get("alerte") is not True:  # le consentement alerte est obligatoire
        return None
    seg = segment_de({"REGION": d.get("region", ""), "TYPE": d.get("type", ""),
                      "CLASSE": d.get("classe", ""), "HORIZON": d.get("horizon", "")})
    langue = str(d.get("langue", "fr"))[:2]
    return {"email": email, "promo": d.get("promo") is True, "seg": seg,
            "langue": langue if langue in LANGUES else "fr"}


def inscrire(ins: dict) -> None:
    region, type_, classe, horizon = ins["seg"]
    liste_a, liste_p = env("BREVO_LISTE_ALERTES_ID"), env("BREVO_LISTE_PROMO_ID")
    ids = [int(liste_a)] + ([int(liste_p)] if ins["promo"] and liste_p else [])
    modele = env(f"BREVO_DOI_TEMPLATE_{ins['langue'].upper()}") or env("BREVO_DOI_TEMPLATE")
    brevo("POST", "/contacts/doubleOptinConfirmation", {
        "email": ins["email"],
        "attributes": {"REGION": region, "TYPE": type_, "CLASSE": classe, "HORIZON": horizon,
                       "PROMO": ins["promo"], "LANGUE": ins["langue"]},
        "includeListIds": ids,
        "templateId": int(modele),
        "redirectionUrl": env("ALERTES_MERCI_URL", "https://sailingmore.fr/merci.html"),
    })


def desinscrire(email: str, liste: str) -> None:
    cible = env("BREVO_LISTE_PROMO_ID") if liste == "promo" else env("BREVO_LISTE_ALERTES_ID")
    q = urllib.parse.quote(email, safe="")
    brevo("PUT", f"/contacts/{q}", {"unlinkListIds": [int(cible)]})
    if liste == "promo":
        brevo("PUT", f"/contacts/{q}", {"attributes": {"PROMO": False}})


class Relais(BaseHTTPRequestHandler):
    def _rep(self, code: int, corps: str = "", type_: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("content-type", type_ + "; charset=utf-8")
        self.send_header("access-control-allow-origin", "https://sailingmore.fr")
        self.send_header("access-control-allow-headers", "content-type")
        self.end_headers()
        self.wfile.write(corps.encode())

    def do_OPTIONS(self):  # noqa: N802
        self._rep(204)

    def do_POST(self):  # noqa: N802
        if self.path != "/inscription":
            return self._rep(404)
        ip = self.headers.get("x-forwarded-for", self.client_address[0]).split(",")[0].strip()
        recents = [t for t in _essais.get(ip, []) if t > time.time() - 3600]
        if len(recents) >= 5:
            return self._rep(429, '{"ok":false}')
        _essais[ip] = recents + [time.time()]
        try:
            n = min(int(self.headers.get("content-length", 0)), 4096)
            ins = lire_inscription(json.loads(self.rfile.read(n)))
        except (ValueError, TypeError):
            ins = None
        if not ins:
            return self._rep(400, '{"ok":false}')
        try:
            inscrire(ins)
        except (urllib.error.URLError, ValueError):
            return self._rep(502, '{"ok":false}')
        self._rep(200, '{"ok":true}')

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        if u.path != "/desinscription":
            return self._rep(404)
        q = urllib.parse.parse_qs(u.query)
        email, liste, t = (q.get(k, [""])[0] for k in ("e", "l", "t"))
        if liste not in ("alertes", "promo") or not hmac.compare_digest(t, jeton(email, liste)):
            return self._rep(400, "<p>Lien invalide.</p>", "text/html")
        try:
            desinscrire(email, liste)
        except urllib.error.URLError:
            return self._rep(502, "<p>Réessayez plus tard.</p>", "text/html")
        self._rep(200, "<p>Vous êtes désinscrit(e). / You are unsubscribed.</p>", "text/html")


def main(argv: list[str]) -> int:
    if argv[:1] == ["serveur"]:
        ThreadingHTTPServer(("127.0.0.1", int(env("ALERTES_PORT", "8765"))), Relais).serve_forever()
        return 0
    if argv[:1] == ["lundi"]:
        return lundi("--envoyer" in argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
