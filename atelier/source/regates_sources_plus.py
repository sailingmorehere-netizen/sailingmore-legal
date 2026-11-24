#!/usr/bin/env python3
"""Sources supplémentaires du calendrier (tâche 52, 24/11/2026) : classes et plateformes.

    python3 scripts/regates_sources_plus.py [base]      # base = racine de la copie (défaut « . »)

Lit en lecture seule trois calendriers publics à dates exactes, puis les ajoute à
`projets/sailingmore/regates.json` sans changer le format :
  * ILCA     https://events.ilcasailing.org/site/event-list   (dates en toutes lettres)
  * 49er     https://49er.org/events/                         (Start/End Date ISO)
  * ORC      https://orc.org/sailors/events-2026 et -2027     (jour.mois ; l'année est celle de l'URL)
Et convertit les anciens noms de source (« acvl », « ffvoile »…) en URL exacte.
Une ligne déjà connue (même nom normalisé, même début) reçoit l'URL en plus dans `sources` ; une
date floue ou absente n'entre pas. Chaque ligne ajoutée porte `lu` : la date de lecture.
"""
from __future__ import annotations

import html as H
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (compatible; SailingMore/1.0; +https://sailingmore.fr)"}
AUJOURDHUI = date.today().isoformat()
MOIS_EN = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
PAYS = {
    "AUSTRALIA": "AUS", "FRANCE": "FRA", "ITALY": "ITA", "SPAIN": "ESP", "PORTUGAL": "POR",
    "GERMANY": "GER", "NETHERLANDS": "NED", "GREAT BRITAIN": "GBR", "UNITED KINGDOM": "GBR",
    "IRELAND": "IRL", "DENMARK": "DEN", "SWEDEN": "SWE", "NORWAY": "NOR", "FINLAND": "FIN",
    "POLAND": "POL", "GREECE": "GRE", "CROATIA": "CRO", "TURKEY": "TUR", "TURKIYE": "TUR",
    "UNITED STATES": "USA", "USA": "USA", "CANADA": "CAN", "BRAZIL": "BRA", "ARGENTINA": "ARG",
    "NEW ZEALAND": "NZL", "JAPAN": "JPN", "CHINA": "CHN", "HONG KONG": "HKG", "SINGAPORE": "SGP",
    "SWITZERLAND": "SUI", "AUSTRIA": "AUT", "BELGIUM": "BEL", "HUNGARY": "HUN", "SLOVENIA": "SLO",
    "ESTONIA": "EST", "LATVIA": "LAT", "LITHUANIA": "LTU", "MALTA": "MLT", "MEXICO": "MEX",
    "SOUTH AFRICA": "RSA", "OMAN": "OMA", "UNITED ARAB EMIRATES": "UAE", "THAILAND": "THA",
    "BERMUDA": "BER", "BAHAMAS": "BAH", "CZECH REPUBLIC": "CZE", "CZECHIA": "CZE",
    "MONACO": "MON", "CYPRUS": "CYP", "ISRAEL": "ISR", "CHILE": "CHI", "PERU": "PER",
}
ANCIENNES = {  # nom historique -> URL exacte de la lecture
    "acvl": "https://www.acvl.ch/association/calendrier-des-regates/",
    "worldsailing": "https://datafeed.sailing.org/stats/api/regatta",
    "spencer": "https://www.spencer.club/en-US/calendar",
}


def lit(u: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", "ignore")


def txt(s: str) -> str:
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def cle(t: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", t.lower())


def ligne(nom, debut, fin, ville, pays, club, classes, lien, source, niveau=""):
    pays = (pays or "").upper()
    nl = nom.lower()
    return {
        "nom": nom, "debut": debut, "fin": fin if fin >= debut else debut, "ville": ville,
        "pays": pays, "club": club, "classes": classes, "lien": lien, "resultats": "",
        "niveau": niveau, "connue": "", "annulee": False, "ocean": False, "departement": "",
        "ligue": "", "sources": [source], "region_repliee": "",
        "region": "France" if pays == "FRA" else ("Suisse" if pays == "SUI" else "Monde"),
        "type": "championnat" if any(k in nl for k in ("championship", "world", "cup", "trophy", "europeans"))
        else "régate",
        "lu": AUJOURDHUI,
    }


def ilca() -> list[dict]:
    src = "https://events.ilcasailing.org/site/event-list"
    out = []
    for bloc in lit(src).split('<div class="well ilcaWell">')[1:]:
        m = re.search(r"eventListTitle\">(.*?)</div>", bloc, re.S)
        d = re.search(r"<b>\s*\w+day (\d{1,2}) (\w+) (\d{4})(?: - \w+day (\d{1,2}) (\w+) (\d{4}))?\s*<br>\s*([^<]*)</b>", bloc)
        if not m or not d:
            continue
        mois1, mois2 = MOIS_EN.get(d.group(2).lower()), MOIS_EN.get((d.group(5) or d.group(2)).lower())
        if not mois1 or not mois2:
            continue
        deb = date(int(d.group(3)), mois1, int(d.group(1))).isoformat()
        fin = date(int(d.group(6) or d.group(3)), mois2, int(d.group(4) or d.group(1))).isoformat()
        lieu = txt(d.group(7))
        pays_n, _, ville = lieu.partition(",")
        a = re.search(r"href='([^']+)'", m.group(1))
        out.append(ligne(txt(m.group(1)), deb, fin, ville.strip(), PAYS.get(pays_n.strip().upper(), ""),
                         "", ["ILCA"], a.group(1) if a else src, src, "classe"))
    return out


def f49() -> list[dict]:
    src = "https://49er.org/events/"
    h = lit(src)
    out = []
    for t, a, b, rest in re.findall(
            r'<h3 class="elementor-heading-title[^>]*>(.*?)</h3>.*?Start Date : (\d{4}-\d{2}-\d{2}).*?'
            r'End Date : (\d{4}-\d{2}-\d{2})(.*?)(?=<h3 class="elementor-heading-title|$)', h, re.S):
        nom = txt(t)
        lien = re.search(r'href="(https?://[^"]+)"', rest)
        ville, pays = "", ""
        if "," in nom:
            fin_nom = nom.rsplit(",", 1)[1].strip().upper()
            if fin_nom in PAYS:
                pays = PAYS[fin_nom]
                ville = nom.rsplit(",", 1)[0].split("–")[-1].strip()
        out.append(ligne(nom, a, b, ville, pays, "", ["49er", "49erFX"], lien.group(1) if lien else src,
                         src, "classe"))
    return out


def orc(annee: int) -> list[dict]:
    src = f"https://orc.org/sailors/events-{annee}"
    out = []
    for tr in re.findall(r"(?s)<tr>(.*?)</tr>", lit(src)):
        tds = re.findall(r"(?s)<td[^>]*>(.*?)</td>", tr)
        dm = re.search(r'data-date="(\d{2})\.(\d{2})(?: - (\d{2})\.(\d{2}))?"', tr)
        a = re.search(r'<a[^>]*href="([^"]+)"[^>]*>\s*<span>(.*?)</span>', tr, re.S)
        if len(tds) < 5 or not dm or not a:
            continue
        j1, m1 = dm.group(1), dm.group(2)
        j2, m2 = dm.group(3) or j1, dm.group(4) or m1
        try:
            deb, fin = date(annee, int(m1), int(j1)).isoformat(), date(annee, int(m2), int(j2)).isoformat()
        except ValueError:
            continue
        pays = txt(tds[3]).split(" ")[0]
        out.append(ligne(txt(a.group(2)), deb, fin, txt(tds[2]), pays if len(pays) == 3 else "", "",
                         [c for c in [txt(tds[4])] if c], a.group(1), src, "classe ORC"))
    return out


def main() -> int:
    base = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    f = base / "projets/sailingmore/regates.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    r = d["regates"]
    # 1. anciens noms de source -> URL exacte
    for x in r:
        nouv = []
        for s in x.get("sources") or []:
            if s.startswith("http"):
                nouv.append(s)
            elif s == "manage2sail":
                nouv.append(f"https://www.manage2sail.com/en-US/search?filterYear={x['debut'][:4]}")
            elif s == "ffvoile":
                nouv.append(f"https://regates.ffvoile.fr/api/competitions?dateDebutMin={x['debut'][:4]}-01-01"
                            f"&dateDebutMax={x['debut'][:4]}-12-31")
            elif s in ANCIENNES:
                nouv.append(ANCIENNES[s])
            elif s in ("majeures", "fonds-propre") and str(x.get("lien", "")).startswith("http"):
                nouv.append(x["lien"])
        x["sources"] = list(dict.fromkeys(nouv))
    # 2. lignes sans aucune URL : n'entrent pas
    avant = len(r)
    r = [x for x in r if x["sources"]]
    retirees = avant - len(r)
    # 3. nouvelles sources
    index = {(cle(x["nom"]), x["debut"]): x for x in r}
    compte, fusion = {}, {}
    for nom, fn in (("ilca", ilca), ("49er", f49), ("orc-2026", lambda: orc(2026)), ("orc-2027", lambda: orc(2027))):
        try:
            lignes = fn()
        except Exception as e:  # noqa: BLE001
            print(f"  {nom} : ÉCHEC {type(e).__name__} {e}")
            continue
        compte[nom] = len(lignes)
        for n in lignes:
            if len(n["debut"]) != 10 or not n["nom"]:
                continue
            k = (cle(n["nom"]), n["debut"])
            if k in index:
                g = index[k]
                g["sources"] = list(dict.fromkeys(g["sources"] + n["sources"]))
                fusion[nom] = fusion.get(nom, 0) + 1
            else:
                index[k] = n
                r.append(n)
    # 4. dédoublonnage (nom, début, club), garde la première (la plus ancienne dans le fichier)
    vus, sortie = {}, []
    for x in r:
        k = (x["nom"].strip().lower(), x["debut"], (x.get("club") or "").strip().lower())
        if k in vus:
            vus[k]["sources"] = list(dict.fromkeys(vus[k]["sources"] + x["sources"]))
            continue
        vus[k] = x
        sortie.append(x)
    sortie.sort(key=lambda x: (x["debut"], cle(x["nom"])))
    av = [x for x in sortie if x["debut"] >= AUJOURDHUI]
    d.update({"maj": date.today().isoformat() + "T05:00:00", "total": len(sortie), "a_venir": len(av),
              "regates": sortie})
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("relevés :", compte, "· déjà connues (URL ajoutée) :", fusion, "· sans URL retirées :", retirees)
    print(f"{len(sortie)} épreuves, {len(av)} à venir")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
