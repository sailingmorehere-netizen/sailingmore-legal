#!/usr/bin/env python3
"""Construit la page `regates.html` du site : le calendrier des régates, avec recherche et filtres.

Entrée  : `projets/sailingmore/regates.json`, écrit par `regates_collecte.py`.
Sortie  : `projets/sailingmore/site/regates.html` (et la copie de publication quand demandée).

    python3 scripts/regates_page.py --ecrire         # écrit la page de travail
    python3 scripts/regates_page.py --verifier       # contrôle compteurs, filtres, dates — lecture seule

Sans drapeau, rien n'est écrit. `--verifier` sort en 1 si un contrôle échoue.
Rien n'est publié ici. La page est autonome : les données sont embarquées dans la page,
en JSON, donc la recherche fonctionne sans appel réseau et sans CORS.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regates_classes  # noqa: E402  (table sigle → nom, jauges « tout bateau »)
import regates_drapeaux  # noqa: E402  (drapeaux SVG, noms de pays en six langues)
import carte_epreuves  # noqa: E402  (la carte, commune aux régates et aux stages)

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
JSON = ICI / "projets/sailingmore/regates.json"
SORTIE = ICI / "projets/sailingmore/site"

# Les valeurs que les puces de filtre savent proposer : partagées par `construire` et `verifier`
# pour qu'un nouveau type ou une nouvelle région ne soit pas ajouté à un seul des deux.
REGIONS = ("Léman", "Haute-Savoie", "Savoie", "Ain", "France", "Suisse", "Océan", "Monde")
TYPES = ("régate", "championnat", "club", "course au large")

MOIS_FR = ["","janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
PAYS_FR = {"FRA": "France", "SUI": "Suisse", "ITA": "Italie", "GER": "Allemagne",
           "ESP": "Espagne", "BEL": "Belgique", "NED": "Pays-Bas", "GBR": "Royaume-Uni",
           "USA": "États-Unis", "POR": "Portugal", "DEN": "Danemark", "SWE": "Suède",
           "NOR": "Norvège", "FIN": "Finlande", "AUT": "Autriche", "MON": "Monaco",
           "AUS": "Australie", "NZL": "Nouvelle-Zélande", "JPN": "Japon", "CHN": "Chine",
           "CAN": "Canada", "BRA": "Brésil", "ARG": "Argentine", "TUR": "Turquie",
           "GRE": "Grèce", "CRO": "Croatie", "POL": "Pologne", "IRL": "Irlande",
           # Les pays que les sources citent sans qu'ils aient de drapeau : sans nom français,
           # la carte afficherait le code (« HKG ») au lieu du pays (24/11/2026).
           "HKG": "Hong Kong", "THA": "Thaïlande", "CHI": "Chili", "HUN": "Hongrie",
           "SGP": "Singapour", "UAE": "Émirats arabes unis", "MEX": "Mexique", "MAR": "Maroc",
           "BER": "Bermudes", "CZE": "Tchéquie", "SLO": "Slovénie", "MLT": "Malte",
           "PER": "Pérou", "RSA": "Afrique du Sud", "MAS": "Malaisie", "IND": "Inde",
           "VEN": "Venezuela", "ANT": "Antilles néerlandaises", "BAR": "Barbade",
           "GRN": "Grenade", "IVB": "Îles Vierges britanniques", "SXM": "Saint-Martin",
           "TTO": "Trinité-et-Tobago", "EST": "Estonie", "LAT": "Lettonie", "LTU": "Lituanie",
           "LUX": "Luxembourg", "MNE": "Monténégro", "ROU": "Roumanie", "SEN": "Sénégal",
           "TAH": "Tahiti"}

# ── Position des épreuves, pour « près de moi » ─────────────────────────────────────────────────
# regates.json ne porte pas de coordonnées : on les déduit ici de la ville (table ci-dessous), à
# défaut du centre du pays (marqué approximatif, « ~ » dans la page). Une ville inconnue n'a pas
# de position : l'épreuve reste dans la liste, sans distance. Pour ajouter un port : une entrée
# « nom lat lon » (nom sans accent, en minuscules).
_LIEUX_TXT = """
nyon 46.383 6.239;rolle 46.459 6.337;cully 46.488 6.727;la tour-de-peilz 46.452 6.857;lausanne 46.519 6.633;
villeneuve 46.397 6.927;morges 46.508 6.498;pully 46.510 6.665;cologny 46.216 6.187;geneve 46.204 6.143;
clarens 46.435 6.893;montreux 46.433 6.911;vevey 46.463 6.843;evian 46.401 6.589;thonon 46.371 6.479;
thun 46.758 7.628;spiez 46.686 7.680;oberhofen 46.732 7.667;neuchatel 46.992 6.931;la neuveville 47.066 7.091;
twann 47.093 7.160;biel 47.137 7.247;zurich 47.376 8.541;thalwil 47.294 8.565;stafa 47.239 8.727;
nuolen 47.200 8.870;arbon 47.516 9.434;kreuzlingen 47.650 9.178;bottighofen 47.636 9.231;steckborn 47.669 8.980;
radolfzell 47.742 8.968;singen 47.759 8.840;friedrichshafen 47.654 9.479;lugano 46.004 8.953;ascona 46.157 8.772;
brissago 46.121 8.718;stansstad 46.977 8.340;beinwil 47.275 8.200;annecy 45.899 6.129;aix-les-bains 45.689 5.915;
cannes 43.552 7.017;concarneau 47.875 -3.920;la trinite-sur-mer 47.586 -3.030;lorient 47.748 -3.366;
saint raphael 43.425 6.768;saint-tropez 43.272 6.640;marseille 43.296 5.370;la rochelle 46.160 -1.151;
brest 48.390 -4.486;moisson 49.070 1.680;lubeck 53.866 10.687;travemunde 53.960 10.870;berlin 52.520 13.405;
munchen 48.137 11.575;kiel 54.323 10.123;starnberg 47.994 11.340;diessen 47.950 11.103;hamburg 53.551 9.994;
bremen 53.079 8.802;bremerhaven 53.540 8.581;dusseldorf 51.228 6.774;essen 51.456 7.012;krefeld 51.339 6.585;
frankfurt 50.110 8.682;nurnberg 49.452 11.077;stuttgart 48.776 9.183;tegernsee 47.710 11.758;prien 47.856 12.346;
chiemsee 47.870 12.400;bernau 47.805 12.373;breitbrunn 47.880 12.410;tutzing 47.909 11.277;herrsching 47.994 11.178;
utting 48.000 11.070;inning 48.030 11.120;potsdam 52.396 13.058;magdeburg 52.131 11.639;munster 51.961 7.628;
steinhude 52.450 9.340;wunstorf 52.420 9.440;damme 52.520 8.200;bad zwischenahn 53.190 8.000;duisburg 51.435 6.763;
bochum 51.482 7.216;hagen 51.360 7.470;erfurt 50.978 11.029;attendorn 51.120 7.900;huckeswagen 51.150 7.340;
kempen 51.365 6.419;dormagen 51.095 6.840;bautzen 51.180 14.420;ribnitz-damgarten 54.240 12.450;
mohnesee 51.490 8.140;worth am rhein 49.050 8.260;bobenheim-roxheim 49.620 8.370;biblis 49.700 8.470;
langen 50.000 8.660;hochheim am main 50.000 8.350;brandenburg 52.410 12.560;zeuthen 52.350 13.620;
furstenwalde 52.360 14.060;arendsee 52.860 11.470;edertal 51.180 9.070;hungen 50.470 8.900;lemwerder 53.170 8.620;
borgwedel 54.500 9.600;nohfelden 49.580 7.130;elchesheim-illingen 48.900 8.300;wackersdorf 49.320 12.150;
simssee 47.870 12.250;dorf mecklenburg 53.820 11.500;hohen viecheln 53.800 11.600;am mellensee 52.200 13.400;
zulpich 50.700 6.650;erftstadt 50.810 6.800;haltern 51.740 7.180;delft 52.011 4.358;oslo 59.913 10.752;
moss 59.430 10.660;sandefjord 59.130 10.220;gressvik 59.250 10.980;porsgrunn 59.140 9.660;grimstad 58.340 8.590;
arendal 58.460 8.770;hundvag 58.990 5.760;hjellestad 60.300 5.300;asgardstrand 59.350 10.460;
skovshoved 55.760 12.590;vedbaek 55.850 12.560;hellerup 55.730 12.570;rungsted 55.890 12.540;niva 55.930 12.500;
aarhus 56.157 10.211;kerteminde 55.450 10.660;kolding 55.490 9.470;horsens 55.860 9.850;djursholm 59.400 18.090;
uppsala 59.858 17.639;vasteras 59.610 16.550;huskvarna 57.790 14.300;tampere 61.498 23.760;helsinki 60.170 24.940;
tallinn 59.437 24.754;vosu 59.580 26.050;antwerpen 51.220 4.400;ranst 51.190 4.570;mechelen 51.030 4.480;
hombeek 51.000 4.500;zemst 50.980 4.460;heusden 51.030 5.280;harelbeke 50.860 3.310;froidchapelle 50.200 4.300;
roelofarendsveen 52.200 4.630;ter aar 52.170 4.720;loosdrecht 52.200 5.070;muiden 52.330 5.070;warmond 52.200 4.500;
sneek 53.030 5.660;medemblik 52.770 5.110;lelystad 52.520 5.470;reeuwijk 52.050 4.730;vinkeveen 52.200 4.930;
ouddorp 51.810 3.930;naples 40.850 14.270;napoli 40.850 14.270;malcesine 45.760 10.810;arco 45.920 10.890;
torbole 45.870 10.870;nago-torbole 45.870 10.870;cremia 46.100 9.280;cesenatico 44.200 12.400;
riva di traiano 42.100 11.800;portoroz 45.510 13.590;punat 45.020 14.630;cowes 50.760 -1.300;
barcelona 41.385 2.170;garraf 41.260 1.900;mar menor 37.700 -0.800;lanzarote 29.000 -13.600;
antigua 17.070 -61.800;english harbour 17.000 -61.760;dubai 25.200 55.270;perth -31.950 115.860;
auckland -36.850 174.760;sydney -33.870 151.210;manly -33.800 151.290;hong kong 22.320 114.170;
rio de janeiro -22.900 -43.200;arue -17.530 -149.500
"""
# Centre approximatif des pays, quand la ville est absente de la table. Marqué « ~ » dans la page.
_PAYS_CENTRE = {"FRA": (46.6, 2.5), "SUI": (46.8, 8.2), "ITA": (42.5, 12.5), "GER": (51.0, 10.3),
                "ESP": (40.2, -3.7), "BEL": (50.6, 4.6), "NED": (52.2, 5.3), "GBR": (53.0, -1.5),
                "POR": (39.6, -8.0), "DEN": (56.0, 10.0), "SWE": (60.0, 15.0), "NOR": (60.5, 8.5),
                "FIN": (62.5, 26.0), "AUT": (47.5, 14.5), "MON": (43.74, 7.42), "CRO": (45.1, 15.2),
                "GRE": (39.0, 22.0), "IRL": (53.3, -8.0), "POL": (52.0, 19.0), "TUR": (39.0, 35.0)}


def _sans_accent(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower().replace("ß", "ss").replace("ø", "o").replace("æ", "ae"))
    return "".join(c for c in s if not unicodedata.combining(c))


_LIEUX = {}
for _e in _LIEUX_TXT.replace("\n", "").split(";"):
    if _e.strip():
        _n, _la, _lo = _e.strip().rsplit(" ", 2)
        _LIEUX[_n] = (float(_la), float(_lo))
_LIEUX_RE = re.compile(r"(?<![a-z])(" + "|".join(re.escape(k) for k in sorted(_LIEUX, key=len, reverse=True)) + r")(?![a-z])")


_COORDS_OSM: dict | None = None


def regates_lieux_cle(ville: str) -> str:
    """Même clé que `regates_lieux.cle` : minuscules, sans accent, espaces simples."""
    return " ".join(_sans_accent(ville or "").split())


def _coords_osm() -> dict:
    """Coordonnées géocodées à la collecte (Nominatim, une requête par ville) et lues dans le cache
    du projet. La page ne contacte jamais Nominatim : elle ne fait que lire ce fichier."""
    global _COORDS_OSM
    if _COORDS_OSM is None:
        try:
            d = json.loads((ICI / "cache/rhum/villes-pays.json").read_text())
            _COORDS_OSM = {k: v for k, v in (d.get("coords") or {}).items() if len(v) == 2}
        except Exception:  # noqa: BLE001 — pas de cache = table locale seulement
            _COORDS_OSM = {}
    return _COORDS_OSM


def position(e: dict) -> tuple[float, float, bool] | None:
    """(lat, lon, approximative) d'une épreuve, ou None. Ville connue = précis ; sinon centre du pays."""
    m = _LIEUX_RE.search(_sans_accent(e.get("ville", "")))
    if m:
        return (*_LIEUX[m.group(1)], False)
    c = _coords_osm().get(regates_lieux_cle(e.get("ville", "")))
    if c:
        return (c[0], c[1], False)
    c = _PAYS_CENTRE.get(e.get("pays") or "")
    return (*c, True) if c else None


CSS = """
:root{--nuit:#0a1a2b;--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
*{box-sizing:border-box}
body{margin:0;background:#071c31;color:var(--ivoire);
  font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased}
.page{max-width:64rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
a.retour{color:var(--gris);text-decoration:none;font-size:.64rem;letter-spacing:.14em;
  text-transform:uppercase;font-weight:500}
a.retour:hover{color:#fff}
h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.6rem 0 0;letter-spacing:-.01em;
  color:#fff;font-weight:300;text-transform:uppercase}
h1::after{content:"";display:block;width:3.4rem;height:3px;background:var(--rouge);margin:1.3rem 0 1.6rem}
.chapo{color:var(--gris);font-size:.95rem;max-width:34rem;margin:0 0 2.2rem}
a{color:#fff;text-decoration:none}

/* ── la barre de recherche ─────────────────────────────────────────── */
.panneau{background:#0a1f33;border:1px solid rgba(255,255,255,.09);border-radius:2px;
  padding:0 1.2rem 1.4rem;margin:0 0 1rem;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.recherche{position:sticky;top:0;z-index:20;background:#0a1f33;
  padding:.9rem 1.2rem 1rem;margin:0 -1.2rem .4rem}
.champ{display:flex;align-items:center;gap:.6rem;background:var(--panneau);
  border:1px solid rgba(255,255,255,.13);border-radius:3px;padding:.62rem .8rem}
.champ:focus-within{border-color:rgba(226,58,62,.7)}
.champ input{flex:1;background:none;border:0;color:var(--ivoire);font-size:.95rem;outline:none;
  font-family:inherit}
.champ input::placeholder{color:#6f8598}
.champ svg{flex:0 0 auto;opacity:.55}
.filtres{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem 1.15rem;margin-top:.7rem}
.filtres .groupe{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;min-width:0}
.filtres .etiq{font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#6f8598;
  margin-right:.2rem}
.menu{font:inherit;font-size:.72rem;letter-spacing:.04em;color:#fff;background-color:var(--panneau);
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.34rem 1.7rem .34rem .55rem;
  cursor:pointer;appearance:none;-webkit-appearance:none;max-width:19rem;
  background-image:url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='%23c9d6e2' stroke-width='1.4'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right .6rem center}
.menu:hover{border-color:rgba(255,255,255,.4);color:#fff}
.menu:focus{outline:none;border-color:rgba(226,58,62,.7);box-shadow:0 0 0 2px rgba(226,58,62,.18)}
.menu option,.menu optgroup{background:#0a1f33;color:#fff}
.menu.actif{border-color:var(--rouge);background-color:rgba(226,58,62,.14)}
.compte{color:var(--gris);font-size:.72rem;letter-spacing:.06em;margin:.9rem 0 .2rem;
  display:flex;justify-content:space-between;align-items:baseline;gap:1.2rem;flex-wrap:wrap}
.compte b{color:#fff;font-weight:500}
#compte{display:flex;gap:1.2rem;flex-wrap:wrap;align-items:baseline}
.lien-effacer{background:none;border:0;color:var(--gris);font:inherit;font-size:.72rem;
  cursor:pointer;text-decoration:underline;text-decoration-color:rgba(226,58,62,.6)}
.lien-effacer:hover{color:#fff}

/* ── la liste ──────────────────────────────────────────────────────── */
.mois{margin:0 0 2.4rem}
.mois h2{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gris);
  font-weight:500;margin:0 0 .2rem;padding-top:1rem;border-top:1px solid rgba(226,58,62,.22)}
.mois h2 span{color:#6f8598;letter-spacing:.1em;margin-left:.5rem}
.epreuve{display:grid;grid-template-columns:7.6rem 1fr auto;gap:.2rem 1.1rem;align-items:baseline;
  padding:.85rem 0;border-bottom:1px solid rgba(255,255,255,.07)}
.epreuve:hover{background:rgba(255,255,255,.025)}
.quand{color:var(--gris);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;
  white-space:nowrap}
.quand .j{color:#fff}
.titre{font-size:.98rem;color:#fff;line-height:1.35}
.titre .finesse{color:var(--gris);font-weight:400}
.ou{color:var(--gris);font-size:.78rem;margin-top:.15rem}
.ou .vil{color:#c9d6e2}
.tags{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.4rem}
.tag{font-size:.56rem;letter-spacing:.14em;text-transform:uppercase;color:#8ea4b8;
  border:1px solid rgba(255,255,255,.13);border-radius:2px;padding:.08rem .38rem}
.tag.rouge{color:#f0a6a8;border-color:rgba(226,58,62,.45)}
.tag.leman{color:#fff;border-color:rgba(226,58,62,.7);background:rgba(226,58,62,.16)}
.cles{display:flex;gap:.5rem;align-items:center;justify-content:flex-end}
.cles a{font-size:.64rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gris);
  border-bottom:1px solid rgba(226,58,62,.55);padding-bottom:1px}
.cles a:hover{color:#fff}
.btn-ics{font:inherit;font-size:.64rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gris);
  background:none;border:0;border-bottom:1px solid rgba(226,58,62,.55);padding:0 0 1px;cursor:pointer}
.btn-ics:hover{color:#fff}
.vide{padding:3rem 0;color:var(--gris);font-size:.9rem}
.pied{margin-top:3.6rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.09);
  color:#6f8598;font-size:.72rem;line-height:1.8}
.pied a{color:var(--gris);text-decoration:underline;text-decoration-color:rgba(226,58,62,.5)}

/* ── un cadre par type de course (le type est toujours aussi écrit : pictogramme + mot) ── */
.epreuve{padding-left:.8rem;border-left:2px solid transparent}
.t-club{border-left-color:rgba(255,255,255,.10)}
.t-regate{border-left-color:rgba(255,255,255,.26)}
.t-champ{border-left:3px solid #e8c468;background:rgba(232,196,104,.06);
  box-shadow:inset 0 0 0 1px rgba(232,196,104,.22)}
.t-large{border-left-color:rgba(255,255,255,.26);background:rgba(0,0,0,.34)}
.tag.type{display:inline-flex;align-items:center;gap:.3rem;color:#c9d6e2;border-color:rgba(255,255,255,.22)}
.tag.type svg{width:.8rem;height:.8rem;flex:0 0 auto;fill:none;stroke:currentColor;stroke-width:1.4;
  stroke-linecap:round;stroke-linejoin:round}
.tag.type.champ{color:#e8c468;border-color:rgba(232,196,104,.6)}
.dr{display:inline-block;width:1.1rem;height:.74rem;vertical-align:-.08rem;margin-right:.45rem;
  box-shadow:0 0 0 1px rgba(255,255,255,.4)}
.sans-classe{font-size:.68rem;font-style:italic;color:#8196a9;letter-spacing:.02em}

/* ── alerte par filtre ─────────────────────────────────────────────── */
.ligne-recherche{display:flex;gap:.6rem;align-items:stretch}
.ligne-recherche .champ{flex:1}
.btn-alerte{font:inherit;font-size:.72rem;letter-spacing:.04em;color:#fff;background:rgba(226,58,62,.14);
  border:1px solid var(--rouge);border-radius:3px;padding:0 .9rem;cursor:pointer;white-space:nowrap}
.btn-alerte:hover{background:rgba(226,58,62,.3)}
.alerte{margin-top:.8rem;padding:.9rem 1rem;background:var(--panneau);border:1px solid rgba(255,255,255,.13);
  border-radius:3px;font-size:.78rem;color:var(--gris)}
.alerte[hidden]{display:none}
.alerte .resume{color:#fff;margin:0 0 .6rem}
.alerte input[type=email]{width:100%;font:inherit;font-size:.9rem;color:var(--ivoire);background:#0a1f33;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.5rem .6rem;margin:.2rem 0 .6rem}
.alerte label.case{display:flex;gap:.5rem;align-items:flex-start;margin:.35rem 0;line-height:1.4;cursor:pointer}
.alerte select{font:inherit;font-size:.78rem;color:var(--ivoire);background:#0a1f33;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.2rem .4rem}
.alerte .hp{position:absolute;left:-9999px;height:0;overflow:hidden}
.alerte button[type=submit]{font:inherit;font-size:.78rem;color:#fff;background:var(--rouge);border:0;
  border-radius:2px;padding:.5rem 1rem;margin-top:.5rem;cursor:pointer}
.alerte .msg{margin:.6rem 0 0;color:#fff}
.alerte .note{font-size:.68rem;color:#8196a9;margin:.5rem 0 0;line-height:1.5}
.alerte .note a{text-decoration:underline;color:var(--gris)}

/* ── près de moi ───────────────────────────────────────────────────── */
.btn-proche{font:inherit;font-size:.72rem;letter-spacing:.04em;color:#fff;background:var(--panneau);
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.34rem .7rem;cursor:pointer}
.btn-proche:hover{border-color:rgba(255,255,255,.4)}
.btn-proche.actif{border-color:var(--rouge);background:rgba(226,58,62,.14)}
.proche-msg{margin:.6rem 0 0;font-size:.74rem;color:var(--gris)}
.proche-msg[hidden]{display:none}
.proche-msg b{color:#fff;font-weight:500}
.dist{display:block;color:#fff;font-size:.68rem;letter-spacing:.06em;margin-top:.15rem;white-space:nowrap}

/* ── la carte des épreuves : brique commune, voir carte_epreuves.py ── */
.carte-regates h2{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gris);
  font-weight:500;margin:0 0 .5rem}
__CARTE_CSS__
@media (max-width:640px){
  .ligne-recherche{flex-direction:column}
  .btn-alerte{padding:.5rem .9rem}
  .page{padding:2.4rem 1rem 4rem}
  .epreuve{grid-template-columns:1fr;gap:.15rem}
  .quand{margin-bottom:.1rem}
  .cles{justify-content:flex-start;margin-top:.3rem}
  .recherche{padding:.7rem 0 .8rem}
  .filtres{gap:.3rem}
  .filtres .etiq{width:100%}
}
"""

CSS = CSS.replace("__CARTE_CSS__", carte_epreuves.CSS)

JS = r"""
(function(){
  var data = JSON.parse(document.getElementById('donnees').textContent);
  // La date du jour est celle du navigateur (date locale), pas celle de la génération : la page reste juste
  // entre deux publications. La valeur du JSON ne sert que de repli si l'horloge est absurde.
  (function(){ var d = new Date(), p = function(n){ return ('0'+n).slice(-2); };
    var j = d.getFullYear() + '-' + p(d.getMonth()+1) + '-' + p(d.getDate());
    if(d.getFullYear() >= +data.aujourdhui.slice(0,4)) data.aujourdhui = j; })();
  var champ = document.getElementById('q');
  var compte = document.getElementById('compte');
  var liste = document.getElementById('liste');
  var menus = Array.prototype.slice.call(document.querySelectorAll('select[data-groupe]'));
  var effacer = document.getElementById('effacer');
  var etat = {region:'tout', type:'tout', quand:'venir', texte:'', classe:'tous', pays:'tous', moi:null};

  // Les mots ajoutés par ce chantier existent dans les six langues ; la langue est celle de <html lang>.
  var T = {
    fr:{tous:'Toutes', inter:'Tout bateau', bateau:'Bateau', chercher:'Chercher une classe…', sans:'classe non précisée', aucune:'Aucune classe ne correspond.',
        t:{'régate':'Régate','championnat':'Championnat','club':'Club','course au large':'Course au large'}},
    de:{tous:'Alle', inter:'Alle Boote', bateau:'Bootsklasse', chercher:'Klasse suchen…', sans:'Klasse nicht angegeben', aucune:'Keine Klasse gefunden.',
        t:{'régate':'Regatta','championnat':'Meisterschaft','club':'Verein','course au large':'Hochseeregatta'}},
    en:{tous:'All', inter:'All boats', bateau:'Boat class', chercher:'Search a class…', sans:'class not specified', aucune:'No class matches.',
        t:{'régate':'Race','championnat':'Championship','club':'Club','course au large':'Offshore race'}},
    it:{tous:'Tutte', inter:'Tutte le barche', bateau:'Classe', chercher:'Cerca una classe…', sans:'classe non indicata', aucune:'Nessuna classe trovata.',
        t:{'régate':'Regata','championnat':'Campionato','club':'Club','course au large':'Regata d\'altura'}},
    es:{tous:'Todas', inter:'Todos los barcos', bateau:'Clase', chercher:'Buscar una clase…', sans:'clase no indicada', aucune:'Ninguna clase coincide.',
        t:{'régate':'Regata','championnat':'Campeonato','club':'Club','course au large':'Regata de altura'}},
    pt:{tous:'Todas', inter:'Todos os barcos', bateau:'Classe', chercher:'Procurar uma classe…', sans:'classe não indicada', aucune:'Nenhuma classe encontrada.',
        t:{'régate':'Regata','championnat':'Campeonato','club':'Clube','course au large':'Regata de alto mar'}}
  };
  var lang = (document.documentElement.lang || 'fr').slice(0,2);
  var L = T[lang] || T.fr;
  // « Près de moi » : textes dans les six langues. {n} = nom de l'épreuve, {d} = distance.
  var GT = {
    fr:{btn:'Près de moi', stop:'Quitter « près de moi »', tri:'Du plus proche au plus lointain', attente:'Recherche de votre position…',
        plus:'La plus proche : {n}, à {d} km.', aucune:'Aucune épreuve avec une position ne correspond à ces filtres.',
        refus:'Position refusée ou indisponible : la liste reste par date.', note:'Votre position reste dans votre navigateur ; elle n\'est ni envoyée ni enregistrée. « ~ » = distance approximative (centre du pays).'},
    de:{btn:'In meiner Nähe', stop:'« In meiner Nähe » beenden', tri:'Vom nächsten zum entferntesten', attente:'Standort wird ermittelt…',
        plus:'Am nächsten: {n}, {d} km entfernt.', aucune:'Keine Veranstaltung mit Standort passt zu diesen Filtern.',
        refus:'Standort verweigert oder nicht verfügbar: die Liste bleibt nach Datum sortiert.', note:'Ihr Standort bleibt in Ihrem Browser; er wird weder gesendet noch gespeichert. „~“ = ungefähre Entfernung (Landesmitte).'},
    en:{btn:'Near me', stop:'Leave “near me”', tri:'Nearest first', attente:'Finding your position…',
        plus:'Nearest: {n}, {d} km away.', aucune:'No race with a known position matches these filters.',
        refus:'Position denied or unavailable: the list stays in date order.', note:'Your position stays in your browser; it is neither sent nor stored. “~” = approximate distance (country centre).'},
    it:{btn:'Vicino a me', stop:'Esci da «vicino a me»', tri:'Dal più vicino al più lontano', attente:'Ricerca della tua posizione…',
        plus:'La più vicina: {n}, a {d} km.', aucune:'Nessuna regata con posizione nota corrisponde a questi filtri.',
        refus:'Posizione negata o non disponibile: l\'elenco resta in ordine di data.', note:'La tua posizione resta nel tuo browser; non viene inviata né salvata. «~» = distanza approssimativa (centro del paese).'},
    es:{btn:'Cerca de mí', stop:'Salir de «cerca de mí»', tri:'De la más cercana a la más lejana', attente:'Buscando tu posición…',
        plus:'La más cercana: {n}, a {d} km.', aucune:'Ninguna regata con posición conocida coincide con estos filtros.',
        refus:'Posición denegada o no disponible: la lista sigue por fecha.', note:'Tu posición se queda en tu navegador; no se envía ni se guarda. «~» = distancia aproximada (centro del país).'},
    pt:{btn:'Perto de mim', stop:'Sair de «perto de mim»', tri:'Da mais próxima à mais distante', attente:'A procurar a tua posição…',
        plus:'A mais próxima: {n}, a {d} km.', aucune:'Nenhuma regata com posição conhecida corresponde a estes filtros.',
        refus:'Posição recusada ou indisponível: a lista continua por data.', note:'A tua posição fica no teu navegador; não é enviada nem guardada. «~» = distância aproximada (centro do país).'}
  };
  var G = GT[lang] || GT.fr;
  function km(a, b){
    var R = 6371, r = Math.PI / 180;
    var dl = (b.lat - a.lat) * r, dn = (b.lon - a.lon) * r;
    var h = Math.sin(dl/2) * Math.sin(dl/2) + Math.cos(a.lat*r) * Math.cos(b.lat*r) * Math.sin(dn/2) * Math.sin(dn/2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  var CADRE = {'régate':'t-regate','championnat':'t-champ','club':'t-club','course au large':'t-large'};
  var ICONE = {'régate':'i-regate','championnat':'i-champ','club':'i-club','course au large':'i-large'};
  var jauges = data.jauges;
  function interSerie(e){
    return (e.classes||[]).some(function(c){ return jauges.indexOf(c.toUpperCase()) > -1; });
  }
  function nomClasse(c){ return data.noms[c.toUpperCase()] || c; }
  function drapeau(e){
    if(!e.pays || data.pays[e.pays] === undefined) return '';
    var n = data.pays[e.pays][lang] || data.pays[e.pays].fr;
    return '<svg class="dr" role="img" aria-label="' + n + '" preserveAspectRatio="none"><title>' + n + '</title><use href="#f-' + e.pays + '"/></svg>';
  }

  function normalise(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}

  // Une épreuve saisie tout en capitales chez l'organisateur se lit mal : on la remet en
  // casse de phrase. Les mots de 2 à 4 lettres restent en capitales — ce sont des sigles
  // (J70, IRC, SNR, CVSQ, TF35) et les casser rendrait le club méconnaissable.
  function casse(s){
    if(!s) return '';
    if(s !== s.toUpperCase()) return s.charAt(0).toUpperCase() + s.slice(1);
    return s.split(/(\s+)/).map(function(mot){
      var net = mot.replace(/[^A-Za-z0-9À-ÿ]/g,'');
      if(net.length >= 2 && net.length <= 6) return mot;
      return mot.charAt(0).toUpperCase() + mot.slice(1).toLowerCase();
    }).join('');
  }

  function passe(e){
    var q = normalise(etat.texte);
    if(q){
      var foin = normalise([e.nom,e.ville,e.club,(e.classes||[]).join(' '),e.pays_fr,e.region,e.ligue].join(' '));
      // « tf35 » doit trouver « TF 35 » : on compare aussi sans les espaces.
      if(foin.indexOf(q) === -1 && foin.replace(/\s+/g,'').indexOf(q.replace(/\s+/g,'')) === -1) return false;
    }
    if(etat.region !== 'tout' && e.region !== etat.region) return false;
    if(etat.type !== 'tout' && e.type !== etat.type) return false;
    // Pays : le code du pays de l'épreuve (le lieu « Suisse » ne couvre pas les épreuves suisses du Léman).
    if(etat.pays !== 'tous' && e.pays !== etat.pays) return false;
    // « tous » ne filtre rien (sans classe comprises) ; toute autre entrée écarte les épreuves sans classe.
    if(etat.classe === '__inter'){ if(!interSerie(e)) return false; }
    else if(etat.classe !== 'tous' && (e.classes||[]).indexOf(etat.classe) === -1) return false;
    if(etat.quand === 'venir' && e.fin < data.aujourdhui) return false;
    return true;
  }

  function jour(d, avecAn){
    var t = d.split('-');
    var j = t[2].replace(/^0/,'') + '/' + t[1].replace(/^0/,'');
    return (avecAn && t[0] !== data.aujourdhui.slice(0,4)) ? j + '/' + t[0].slice(2) : j;
  }

  function moisCle(d){ return d.slice(0,7); }
  function moisLisible(k){
    var t = k.split('-'); var m = parseInt(t[1],10); var a = t[0];
    var nom = data.mois[m-1];
    return nom + ' ' + a;
  }

  function dessine(){
    var gardes = data.epreuves.filter(passe);
    // « Près de moi » : la position reste dans le navigateur (jamais envoyée, jamais stockée) ;
    // la liste passe en ordre de distance, les épreuves sans position à la fin.
    if(etat.moi){
      gardes.forEach(function(e){ e.km = (e.lat === undefined) ? null : km(etat.moi, e); });
      gardes = gardes.slice().sort(function(a,b){
        if(a.km === null) return b.km === null ? 0 : 1;
        if(b.km === null) return -1;
        return a.km - b.km;
      });
    }
    var groupes = [], vus = {};
    gardes.forEach(function(e){
      var k = etat.moi ? 'proche' : moisCle(e.debut);
      if(!vus[k]){vus[k]=[];groupes.push(k);}
      vus[k].push(e);
    });
    gardesCourantes = gardes;
    var html = '';
    groupes.forEach(function(k){
      var l = vus[k];
      html += '<section class="mois"><h2>' + (etat.moi ? G.tri : moisLisible(k)) + ' <span>' + l.length + (l.length>1?' épreuves':' épreuve') + '</span></h2>';
      l.forEach(function(e){
        var an = e.debut.slice(0,4) !== data.aujourdhui.slice(0,4) || etat.quand === 'tout';
        var dates = (e.fin && e.fin !== e.debut) ? jour(e.debut, an) + ' → ' + jour(e.fin, an) : jour(e.debut, an);
        var lieu = [e.ville, e.club].filter(Boolean).join(' · ') || e.pays_fr;
        var tags = '';
        if(e.region === 'Léman') tags += '<span class="tag leman">Léman</span>';
        else if(e.region) tags += '<span class="tag">' + e.region + '</span>';
        if(ICONE[e.type]) tags += '<span class="tag type' + (e.type === 'championnat' ? ' champ' : '') + '"><svg viewBox="0 0 16 16" aria-hidden="true"><use href="#' + ICONE[e.type] + '"/></svg>' + (L.t[e.type] || e.type) + '</span>';
        if(e.classes && e.classes.length) tags += '<span class="tag">' + e.classes.slice(0,4).map(nomClasse).join(' · ') + '</span>';
        else tags += '<span class="sans-classe">' + L.sans + '</span>';
        if(e.annulee) tags += '<span class="tag rouge">Annulée</span>';
        var dr = drapeau(e);
        var dist = (etat.moi && e.km !== null && e.km !== undefined) ? '<span class="dist">' + (e.ap ? '~' : '') + Math.round(e.km) + ' km</span>' : '';
        html += '<article class="epreuve ' + (CADRE[e.type] || '') + '">'
             + '<div class="quand"><span class="j">' + dates + '</span>' + dist + '</div>'
             + '<div><div class="titre">' + casse(e.nom) + '</div>'
             + ((dr || lieu) ? '<div class="ou">' + dr + (lieu ? '<span class="vil">' + casse(lieu) + '</span>' : '') + '</div>' : '')
             + (tags ? '<div class="tags">' + tags + '</div>' : '')
             + '</div>'
             + '<div class="cles"><button class="btn-ics" type="button" data-ics="' + gardesCourantes.indexOf(e) + '" title="' + echappe(I.titre) + '">+ ' + I.un + '</button>' + (e.lien ? '<a href="' + e.lien + '" target="_blank" rel="noopener">' + (e.lien_quoi||'site') + ' →</a>' : '') + '</div>'
             + '</article>';
      });
      html += '</section>';
    });
    liste.innerHTML = html || '<p class="vide">Aucune épreuve ne correspond à ces filtres. <button class="lien-effacer" type="button" id="vide-effacer">Tout effacer</button></p>';
    var ve = document.getElementById('vide-effacer');
    if(ve) ve.addEventListener('click', function(){ effacer.click(); });
    ecrireUrl();
    dessineCarte(gardes);
    var nIcs = gardes.filter(function(e){ return !e.annulee; }).length;
    btnIcsTout.hidden = !nIcs;
    btnIcsTout.textContent = I.tout + ' · ' + nIcs;
    compte.innerHTML = '<span><b>' + gardes.length + '</b> épreuve' + (gardes.length>1?'s':'') + '</span>'
      + (etat.quand==='venir' && gardes.length && !etat.moi ? '<span>la prochaine : <b>' + casse(gardes[0].nom) + '</b></span>' : '');
    if(etat.moi){
      var p = gardes[0];
      msgProche.hidden = false;
      msgProche.innerHTML = (p && p.km !== null)
        ? G.plus.replace('{n}', '<b>' + echappe(casse(p.nom)) + '</b>').replace('{d}', (p.ap ? '~' : '') + Math.round(p.km)) + ' <span>' + G.note + '</span>'
        : G.aucune + ' <span>' + G.note + '</span>';
    }
  }
  // ── Carte : brique commune carte_epreuves.py (côtes, pastilles de 44 px, regroupement, clavier).
  var carte = CarteEpreuves.creer({});
  document.getElementById('carte-titre').textContent = carte.titre;
  var dateLongue = function(d){
    try { return new Intl.DateTimeFormat(lang, {day:'numeric', month:'long', year:'numeric'}).format(new Date(d + 'T12:00:00')); }
    catch(x){ return d; }
  };
  function dessineCarte(liste){
    var pts = liste.filter(function(e){ return e.lat !== undefined; }).map(function(e){
      var an = e.debut.slice(0,4) !== data.aujourdhui.slice(0,4);
      var dates = (e.fin && e.fin !== e.debut) ? jour(e.debut, an) + ' → ' + jour(e.fin, an) : jour(e.debut, an);
      return {
        lat: e.lat, lon: e.lon, ap: e.ap, champ: e.type === 'championnat',
        label: casse(e.nom) + (e.ville ? ', ' + casse(e.ville) : '') + ', ' + dateLongue(e.debut),
        html: '<b>' + echappe(casse(e.nom)) + '</b> — ' + dates
          + (e.ville ? ' · ' + echappe(casse(e.ville)) : '')
          + (e.lien ? ' · <a href="' + echappe(e.lien) + '" target="_blank" rel="noopener">' + echappe(e.lien_quoi || 'site') + ' →</a>' : '')
      };
    });
    carte.montre(pts, liste.length);
  }
  // Fuseau horaire → pays (codes de regates.json). Seulement ce que le navigateur sait déjà : aucun envoi.
  var FUSEAU = {'Europe/Paris':'FRA','Europe/Zurich':'SUI','Europe/Rome':'ITA','Europe/Berlin':'GER','Europe/Madrid':'ESP',
    'Europe/Brussels':'BEL','Europe/Amsterdam':'NED','Europe/London':'GBR','Europe/Lisbon':'POR','Europe/Copenhagen':'DEN',
    'Europe/Stockholm':'SWE','Europe/Oslo':'NOR','Europe/Helsinki':'FIN','Europe/Vienna':'AUT','Europe/Monaco':'MON',
    'Europe/Zagreb':'CRO','Europe/Athens':'GRE','Europe/Dublin':'IRL','Europe/Warsaw':'POL','Europe/Istanbul':'TUR'};
  var FZ = {
    fr:'Position estimée d\'après votre fuseau horaire (pays) ; précisez avec le menu « Lieu ».',
    de:'Standort aus Ihrer Zeitzone geschätzt (Land); verfeinern Sie mit dem Menü „Lieu“.',
    en:'Position estimated from your time zone (country); refine with the “Lieu” (place) menu.',
    it:'Posizione stimata dal tuo fuso orario (paese); affina con il menu «Lieu».',
    es:'Posición estimada por tu zona horaria (país); afina con el menú «Lieu».',
    pt:'Posição estimada pelo teu fuso horário (país); afina com o menu «Lieu».'
  };
  function paysDuFuseau(){
    try { return FUSEAU[Intl.DateTimeFormat().resolvedOptions().timeZone] || ''; } catch(x){ return ''; }
  }
  var msgProche = document.getElementById('proche-msg');
  var btnProche = document.getElementById('btn-proche');
  function quitteProche(){
    etat.moi = null;
    msgProche.hidden = true;
    btnProche.classList.remove('actif');
    btnProche.textContent = G.btn;
  }
  // Le navigateur ne demande la position que sur clic : c'est l'accord du visiteur.
  if(btnProche && 'geolocation' in navigator){
    btnProche.hidden = false;
    btnProche.textContent = G.btn;
    btnProche.addEventListener('click', function(){
      if(etat.moi){ quitteProche(); dessine(); return; }
      btnProche.disabled = true;
      msgProche.hidden = false;
      msgProche.textContent = G.attente;
      navigator.geolocation.getCurrentPosition(function(pos){
        btnProche.disabled = false;
        etat.moi = {lat: pos.coords.latitude, lon: pos.coords.longitude};
        btnProche.classList.add('actif');
        btnProche.textContent = G.stop;
        dessine();
      }, function(){
        btnProche.disabled = false;
        // Position refusée : le pays se déduit du fuseau horaire (rien ne sort du navigateur) ;
        // le resserrage fin se fait avec le menu « Lieu ».
        var c = paysDuFuseau();
        if(c && data.centres[c]){
          etat.moi = {lat: data.centres[c][0], lon: data.centres[c][1]};
          btnProche.classList.add('actif');
          btnProche.textContent = G.stop;
          dessine();
          msgProche.innerHTML += ' <span>' + (FZ[lang] || FZ.fr) + '</span>';
        } else msgProche.textContent = G.refus;
      }, {enableHighAccuracy:false, timeout:15000, maximumAge:600000});
    });
  }

  // Filtres : quatre menus déroulants (lieu, type, bateau, quand). Le bateau est rempli ici parce
  // que ses options portent leur nombre d'épreuves : « Toutes » (ne filtre rien), « Tout bateau »
  // (jauges inter-séries), puis chaque classe par nombre d'épreuves décroissant, sigle brut si le
  // nom manque. Le sigle est aussi la valeur du menu, comme l'était la puce.
  var selClasse = document.getElementById('classe');
  document.getElementById('etiq-classe').textContent = L.bateau;
  var nInter = data.epreuves.filter(interSerie).length;
  function echappe(s){
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function dessineClasses(){
    var h = '<option value="tous">' + L.tous + ' (' + data.epreuves.length + ')</option>'
          + '<option value="__inter">' + L.inter + ' (' + nInter + ')</option>';
    data.classes.forEach(function(c){
      h += '<option value="' + echappe(c.s) + '">' + echappe(c.n || c.s) + ' (' + c.c + ')</option>';
    });
    selClasse.innerHTML = h;
    selClasse.value = etat.classe;
  }
  // Un menu qui filtre vraiment prend la couleur de l'accent : on voit d'un coup d'œil ce qui est actif.
  function marque(){
    menus.forEach(function(m){
      var g = m.dataset.groupe;
      m.value = etat[g];
      m.classList.toggle('actif', etat[g] !== (m.dataset.defaut || 'tout'));
    });
    selClasse.classList.toggle('actif', etat.classe !== 'tous');
  }
  // Pays : un menu rempli ici, avec le nombre d'épreuves de chaque pays (seuls les pays qui ont des épreuves).
  var selPays = document.getElementById('pays');
  var LIBPAYS = {fr:'Pays', de:'Land', en:'Country', it:'Paese', es:'País', pt:'País'};
  var TOUSPAYS = {fr:'Tous les pays', de:'Alle Länder', en:'All countries', it:'Tutti i paesi', es:'Todos los países', pt:'Todos os países'};
  document.getElementById('etiq-pays').textContent = LIBPAYS[lang] || LIBPAYS.fr;
  selPays.setAttribute('aria-label', LIBPAYS[lang] || LIBPAYS.fr);
  function dessinePays(){
    var n = {};
    data.epreuves.forEach(function(e){ if(e.pays && data.pays[e.pays] !== undefined) n[e.pays] = (n[e.pays]||0) + 1; });
    var nom = function(c){ return data.pays[c][lang] || data.pays[c].fr; };
    var codes = Object.keys(n).sort(function(a,b){ return n[b] - n[a] || (nom(a) < nom(b) ? -1 : 1); });
    selPays.innerHTML = '<option value="tous">' + (TOUSPAYS[lang] || TOUSPAYS.fr) + '</option>'
      + codes.map(function(c){ return '<option value="' + c + '">' + echappe(nom(c)) + ' (' + n[c] + ')</option>'; }).join('');
  }
  // État dans l'adresse : ?lieu=Suisse&pays=SUI&type=régate&bateau=OSIR&quand=tout&q=…
  // Seules les valeurs qui diffèrent du défaut s'écrivent ; une valeur inconnue est ignorée.
  var CLES_URL = {region:'lieu', pays:'pays', type:'type', classe:'bateau', quand:'quand', texte:'q'};
  function lireUrl(){
    var p;
    try { p = new URLSearchParams(location.search); } catch(x){ return; }
    Object.keys(CLES_URL).forEach(function(g){
      var v = p.get(CLES_URL[g]);
      if(v === null || v === '') return;
      if(g === 'texte'){ etat.texte = v.slice(0, 80); return; }
      var m = g === 'classe' ? selClasse : g === 'pays' ? selPays : document.querySelector('select[data-groupe="' + g + '"]');
      if(m && Array.prototype.some.call(m.options, function(o){ return o.value === v; })) etat[g] = v;
    });
    champ.value = etat.texte;
  }
  function ecrireUrl(){
    var p = [];
    Object.keys(CLES_URL).forEach(function(g){
      var m = g === 'classe' ? selClasse : g === 'pays' ? selPays : document.querySelector('select[data-groupe="' + g + '"]');
      var def = g === 'texte' ? '' : m.dataset.defaut;
      if(etat[g] !== def && etat[g] !== '') p.push(CLES_URL[g] + '=' + encodeURIComponent(etat[g]));
    });
    try { history.replaceState(null, '', location.pathname + (p.length ? '?' + p.join('&') : '') + location.hash); } catch(x){}
  }
  menus.forEach(function(m){
    m.addEventListener('change', function(){
      etat[m.dataset.groupe] = m.value;
      marque();
      dessine();
    });
  });
  selClasse.addEventListener('change', function(){
    etat.classe = selClasse.value;
    marque();
    dessine();
  });
  // ── Export agenda (.ics) ─────────────────────────────────────────────────────
  // Fichier fabriqué dans le navigateur à partir des données embarquées : rien n'est envoyé.
  // Épreuve = événement « journée entière » (dates du calendrier, sans heure inventée).
  // Mention Sailing More : seulement le PRODID (invisible) et une dernière ligne de la description
  // (« Via sailingmore.fr ») ; jamais dans le titre ni le lieu, que l'internaute garde propre.
  var IC = {
    fr:{un:'Agenda', tout:'Tout ajouter à mon agenda (.ics)', titre:'Ajouter cette épreuve à mon agenda (fichier .ics)', via:'Via'},
    de:{un:'Kalender', tout:'Alle in meinen Kalender (.ics)', titre:'Diese Veranstaltung in meinen Kalender übernehmen (.ics-Datei)', via:'Über'},
    en:{un:'Calendar', tout:'Add all to my calendar (.ics)', titre:'Add this race to my calendar (.ics file)', via:'Via'},
    it:{un:'Agenda', tout:'Aggiungi tutte alla mia agenda (.ics)', titre:'Aggiungi questa regata alla mia agenda (file .ics)', via:'Tramite'},
    es:{un:'Agenda', tout:'Añadir todas a mi agenda (.ics)', titre:'Añadir esta regata a mi agenda (archivo .ics)', via:'Vía'},
    pt:{un:'Agenda', tout:'Adicionar todas à minha agenda (.ics)', titre:'Adicionar esta regata à minha agenda (ficheiro .ics)', via:'Via'}
  };
  var I = IC[lang] || IC.fr;
  var gardesCourantes = [];
  function icsTexte(s){ return String(s||'').replace(/\\/g,'\\\\').replace(/;/g,'\\;').replace(/,/g,'\\,').replace(/\r?\n/g,'\\n'); }
  function icsPlie(l){
    var out = [];
    while(l.length > 70){ out.push(l.slice(0,70)); l = ' ' + l.slice(70); }
    out.push(l);
    return out.join('\r\n');
  }
  function icsJour(d){ return d.replace(/-/g,''); }
  function icsLendemain(d){
    var t = d.split('-'), x = new Date(Date.UTC(+t[0], +t[1]-1, +t[2]+1));
    return x.getUTCFullYear() + ('0'+(x.getUTCMonth()+1)).slice(-2) + ('0'+x.getUTCDate()).slice(-2);
  }
  function icsEvt(e, stamp){
    var fin = e.fin || e.debut;
    var lieu = [e.ville, e.club, e.pays_fr].filter(Boolean).join(', ');
    var desc = [];
    if(e.classes && e.classes.length) desc.push(e.classes.slice(0,4).map(nomClasse).join(' · '));
    if(e.lien) desc.push(e.lien);
    desc.push(I.via + ' sailingmore.fr/regates.html');
    var uid = normalise(e.nom + '-' + e.debut).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'') + '@sailingmore.fr';
    var l = ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp,
      'DTSTART;VALUE=DATE:' + icsJour(e.debut), 'DTEND;VALUE=DATE:' + icsLendemain(fin),
      'SUMMARY:' + icsTexte(casse(e.nom))];
    if(lieu) l.push('LOCATION:' + icsTexte(casse(lieu)));
    l.push('DESCRIPTION:' + icsTexte(desc.join('\n')));
    if(e.lien) l.push('URL:' + e.lien);
    if(e.annulee) l.push('STATUS:CANCELLED');
    l.push('END:VEVENT');
    return l.map(icsPlie).join('\r\n');
  }
  function icsTelecharge(liste, nom){
    var d = new Date(), p = function(n){ return ('0'+n).slice(-2); };
    var stamp = d.getUTCFullYear() + p(d.getUTCMonth()+1) + p(d.getUTCDate()) + 'T' + p(d.getUTCHours()) + p(d.getUTCMinutes()) + p(d.getUTCSeconds()) + 'Z';
    var txt = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Sailing More//Calendrier des regates//FR\r\n[secret-masqué]\r\n'
      + liste.map(function(e){ return icsEvt(e, stamp); }).join('\r\n') + '\r\nEND:VCALENDAR\r\n';
    var blob = new Blob([txt], {type:'text/calendar;charset=utf-8'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = nom + '.ics';
    document.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }
  liste.addEventListener('click', function(ev){
    var b = ev.target.closest ? ev.target.closest('button[data-ics]') : null;
    if(!b) return;
    var e = gardesCourantes[parseInt(b.getAttribute('data-ics'), 10)];
    if(e) icsTelecharge([e], normalise(e.nom).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,60) || 'regate');
  });
  var btnIcsTout = document.getElementById('btn-ics-tout');
  btnIcsTout.addEventListener('click', function(){
    var l = gardesCourantes.filter(function(e){ return !e.annulee; });
    if(l.length) icsTelecharge(l, 'regates-sailingmore');
  });
  dessineClasses();
  dessinePays();
  lireUrl();
  marque();
  champ.addEventListener('input', function(){ etat.texte = champ.value; dessine(); });
  effacer.addEventListener('click', function(){
    etat = {region:'tout', type:'tout', quand:'venir', texte:'', classe:'tous', pays:'tous', moi:null};
    if(btnProche) quitteProche();
    champ.value = '';
    marque();
    dessine();
  });
  dessine();

  // ── Alerte par filtre ────────────────────────────────────────────────────────
  // Le bouton n'existe que si le relais est configuré (data.alertes_url). Ne part vers le relais
  // que : e-mail, deux consentements, région, type, classe, horizon, langue. Jamais la position,
  // jamais le texte tapé dans la recherche.
  var A = {
    fr:{btn:'M\'alerter pour ce filtre', tout:'tous les filtres', email:'Votre e-mail', h:'Horizon', h30:'1 mois', h90:'3 mois', h365:'1 an', htout:'toutes les épreuves à venir',
        c1:'Être alerté des nouvelles régates (obligatoire)', c2:'Recevoir aussi l\'actualité de Sailing More (facultatif)',
        note:'Chaque envoi contient un lien de désinscription pour chacune de ces deux listes, indépendantes l\'une de l\'autre. Un e-mail de confirmation vous sera envoyé.', conf:'Confidentialité',
        ok:'Envoyer', recu:'Un e-mail de confirmation vous a été envoyé : cliquez sur le lien pour activer l\'alerte.', err:'Échec de l\'envoi, réessayez plus tard.', pour:'Alerte pour :'},
    de:{btn:'Für diesen Filter benachrichtigen', tout:'alle Filter', email:'Ihre E-Mail', h:'Zeitraum', h30:'1 Monat', h90:'3 Monate', h365:'1 Jahr', htout:'alle kommenden Regatten',
        c1:'Über neue Regatten benachrichtigt werden (erforderlich)', c2:'Außerdem Neuigkeiten von Sailing More erhalten (freiwillig)',
        note:'Jede Sendung enthält einen Abmeldelink für jede dieser beiden voneinander unabhängigen Listen. Sie erhalten eine Bestätigungs-E-Mail.', conf:'Datenschutz',
        ok:'Senden', recu:'Eine Bestätigungs-E-Mail wurde gesendet: Klicken Sie auf den Link, um die Benachrichtigung zu aktivieren.', err:'Senden fehlgeschlagen, bitte später erneut versuchen.', pour:'Benachrichtigung für:'},
    en:{btn:'Alert me for this filter', tout:'all filters', email:'Your email', h:'Horizon', h30:'1 month', h90:'3 months', h365:'1 year', htout:'all upcoming races',
        c1:'Be alerted to new races (required)', c2:'Also receive Sailing More news (optional)',
        note:'Every email carries an unsubscribe link for each of these two independent lists. A confirmation email will be sent to you.', conf:'Privacy',
        ok:'Send', recu:'A confirmation email has been sent: click the link to activate the alert.', err:'Sending failed, please try again later.', pour:'Alert for:'},
    it:{btn:'Avvisami per questo filtro', tout:'tutti i filtri', email:'La tua e-mail', h:'Orizzonte', h30:'1 mese', h90:'3 mesi', h365:'1 anno', htout:'tutte le regate in programma',
        c1:'Essere avvisato delle nuove regate (obbligatorio)', c2:'Ricevere anche le novità di Sailing More (facoltativo)',
        note:'Ogni invio contiene un link di annullamento per ciascuna di queste due liste indipendenti. Riceverai un\'e-mail di conferma.', conf:'Privacy',
        ok:'Invia', recu:'Ti abbiamo inviato un\'e-mail di conferma: clicca sul link per attivare l\'avviso.', err:'Invio non riuscito, riprova più tardi.', pour:'Avviso per:'},
    es:{btn:'Avisarme para este filtro', tout:'todos los filtros', email:'Tu correo', h:'Horizonte', h30:'1 mes', h90:'3 meses', h365:'1 año', htout:'todas las regatas próximas',
        c1:'Recibir avisos de nuevas regatas (obligatorio)', c2:'Recibir también las novedades de Sailing More (opcional)',
        note:'Cada envío incluye un enlace de baja para cada una de estas dos listas independientes. Recibirás un correo de confirmación.', conf:'Privacidad',
        ok:'Enviar', recu:'Te hemos enviado un correo de confirmación: haz clic en el enlace para activar el aviso.', err:'Error al enviar, inténtalo más tarde.', pour:'Aviso para:'},
    pt:{btn:'Avisar-me para este filtro', tout:'todos os filtros', email:'O teu e-mail', h:'Horizonte', h30:'1 mês', h90:'3 meses', h365:'1 ano', htout:'todas as regatas futuras',
        c1:'Ser avisado das novas regatas (obrigatório)', c2:'Receber também as novidades da Sailing More (opcional)',
        note:'Cada envio inclui um link de cancelamento para cada uma destas duas listas independentes. Receberás um e-mail de confirmação.', conf:'Privacidade',
        ok:'Enviar', recu:'Foi enviado um e-mail de confirmação: clica no link para ativar o alerta.', err:'Falha no envio, tenta mais tarde.', pour:'Alerta para:'}
  };
  var AL = A[lang] || A.fr;
  var btnA = document.getElementById('btn-alerte');
  var formA = document.getElementById('alerte');
  if(data.alertes_url && btnA && formA){
    btnA.hidden = false;
    btnA.textContent = AL.btn;
    function filtreCourant(){
      return {region: etat.region === 'tout' ? '' : etat.region,
              type: etat.type === 'tout' ? '' : etat.type,
              classe: etat.classe === 'tous' ? '' : etat.classe};
    }
    function libelleFiltre(f){
      var p = [];
      if(f.region) p.push(f.region);
      if(f.type) p.push(L.t[f.type] || f.type);
      if(f.classe) p.push(f.classe === '__inter' ? L.inter : nomClasse(f.classe));
      return p.length ? p.join(' · ') : AL.tout;
    }
    formA.innerHTML = '<p class="resume" id="al-resume"></p>'
      + '<label>' + AL.email + '<input type="email" name="email" required autocomplete="email"></label>'
      + '<label>' + AL.h + ' <select name="horizon"><option value="tout">' + AL.htout + '</option><option value="30">' + AL.h30 + '</option><option value="90">' + AL.h90 + '</option><option value="365">' + AL.h365 + '</option></select></label>'
      + '<label class="case"><input type="checkbox" name="alerte" required><span>' + AL.c1 + '</span></label>'
      + '<label class="case"><input type="checkbox" name="promo"><span>' + AL.c2 + '</span></label>'
      + '<input class="hp" type="text" name="site" tabindex="-1" autocomplete="off" aria-hidden="true">'
      + '<p class="note">' + AL.note + ' <a href="confidentialite.html">' + AL.conf + '</a></p>'
      + '<button type="submit">' + AL.ok + '</button><p class="msg" id="al-msg" role="status"></p>';
    btnA.addEventListener('click', function(){
      formA.hidden = !formA.hidden;
      document.getElementById('al-resume').textContent = AL.pour + ' ' + libelleFiltre(filtreCourant());
    });
    // Le résumé suit le filtre tant que le formulaire est ouvert.
    document.addEventListener('click', function(){
      if(!formA.hidden) document.getElementById('al-resume').textContent = AL.pour + ' ' + libelleFiltre(filtreCourant());
    });
    formA.addEventListener('submit', function(ev){
      ev.preventDefault();
      var f = filtreCourant(), m = document.getElementById('al-msg');
      var corps = {email: formA.email.value.trim(), alerte: formA.alerte.checked, promo: formA.promo.checked,
                   region: f.region, type: f.type, classe: f.classe, horizon: formA.horizon.value,
                   langue: lang, site: formA.site.value};
      fetch(data.alertes_url + '/inscription', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(corps)})
        .then(function(r){ if(!r.ok) throw 0; m.textContent = AL.recu; formA.querySelector('button[type=submit]').disabled = true; })
        .catch(function(){ m.textContent = AL.err; });
    });
  }
})();
"""


def charger() -> dict:
    if not JSON.exists():
        raise SystemExit(f"{JSON} absent : lancer scripts/regates_collecte.py d'abord")
    return json.loads(JSON.read_text())


def ecrire_page(dossier: Path) -> int:
    """Écrit le calendrier dans `dossier` — le seul chemin de sortie de cette page.

    Appelée par `accueil_site.sortir_le_site()`, donc la page passe par le même pipeline que
    le reste du site (mer en fond, équilibre, miroir de publication) et ne peut pas être
    écrasée par une reconstruction de l'accueil.
    """
    d = charger()
    (dossier / "regates.html").write_text(construire(d), encoding="utf-8")
    epreuves = epreuves_pour_page(d)
    ld = ld_epreuves(epreuves)
    ans = sorted({e["debut"][:4] for e in ld})
    print(f"balisage Google des régates : {len(ld)} épreuve(s) sur {len(epreuves)} à venir "
          f"(douze mois glissants, plafond {LD_MAX}) · "
          + (f"du {ld[0]['debut']} au {ld[-1]['debut']} · années {', '.join(ans)}" if ld else "aucune"))
    return len(epreuves)


def affichable(e: dict) -> bool:
    """Le tri de `epreuves_pour_page`, seul, pour que `verifier` compte sur les mêmes épreuves."""
    aujourdhui = date.today().isoformat()
    try:
        date.fromisoformat(e["debut"])
    except Exception:  # noqa: BLE001
        return False
    fin = e.get("fin") or e["debut"]
    # Une épreuve en cours (commencée vendredi, qui finit dimanche) reste dans le
    # calendrier ; une « saison » ouverte depuis deux mois n'est plus une épreuve à venir.
    if fin < aujourdhui or e["debut"] < date.fromordinal(
            date.today().toordinal() - 3).isoformat():
        return False
    # FFVoile publie des « saisons » qui courent sur six mois : ce ne sont pas des régates
    # datées, et elles viendraient en tête de liste. Au-delà de deux mois, on écarte.
    if (date.fromisoformat(fin) - date.fromisoformat(e["debut"])).days > 60:
        return False
    return e["type"] != "hors-regate"


def epreuves_pour_page(d: dict) -> list[dict]:
    """Ne garde que ce qui se lit : le futur proche et tout ce qui est daté après hier.
    Le passé n'a pas sa place dans un calendrier — il reste dans le JSON."""
    out = []
    for e in d["regates"]:
        if not affichable(e):
            continue
        lien_quoi = "inscription" if "manage2sail" in e.get("lien", "") else "site"
        pos = position(e)
        out.append({
            # Position pour « près de moi » : lat/lon arrondis, `ap` = centre du pays faute de ville connue.
            **({"lat": round(pos[0], 2), "lon": round(pos[1], 2), "ap": pos[2]} if pos else {}),
            "nom": e["nom"],
            "debut": e["debut"],
            "fin": e["fin"],
            "ville": e["ville"],
            "club": e["club"],
            # Liste complète : le filtre de classe doit voir OSIR/IRC même en 7e position.
            # La carte, elle, n'en affiche que quatre.
            "classes": list(e["classes"]),
            "pays": e.get("pays") or "",
            "region": e["region"],
            "type": e["type"],
            "pays_fr": PAYS_FR.get(e["pays"], e["pays"]),
            "ligue": e.get("ligue", ""),
            "lien": e.get("lien", ""),
            "lien_quoi": lien_quoi,
            "annulee": e.get("annulee", False),
        })
    out.sort(key=lambda x: (x["debut"], x["nom"].lower()))
    return out


LD_MAX = 100  # plafond de l'ItemList : au-delà, le bloc pèse plus que la page n'y gagne
LD_JOURS = 365  # fenêtre glissante du balisage : les douze mois à venir, pas l'année civile


def ld_epreuves(epreuves: list[dict]) -> list[dict]:
    """Les épreuves balisées : les LD_MAX **prochaines** par date dans les douze mois à venir,
    non annulées, avec un lieu.

    Jusqu'au 23/11/2026 le filtre était l'année civile du jour : en novembre il ne restait que
    54 épreuves balisées sur 1 004 à venir (dont 661 en 2027) — Google ne voyait presque rien au
    moment où se prépare la saison suivante. `epreuves` arrive déjà trié par date
    (`epreuves_pour_page`), on prend donc les premières."""
    limite = date.fromordinal(date.today().toordinal() + LD_JOURS).isoformat()
    out = []
    for e in epreuves:
        if e["debut"] > limite or e["annulee"] or not e["ville"]:
            continue
        out.append(e)
        if len(out) >= LD_MAX:
            break
    return out


def _ld_regates(epreuves: list[dict]) -> str:
    """JSON-LD : fil d'Ariane + ItemList des LD_MAX prochaines épreuves des douze mois à venir
    (voir `ld_epreuves`). Aucun prix, aucune note."""
    import jsonld
    items = []
    for e in ld_epreuves(epreuves):
        ev = {"@type": "SportsEvent", "name": e["nom"], "startDate": e["debut"],
              "endDate": e["fin"] or e["debut"],
              "location": {"@type": "Place", "name": e["ville"],
                           "address": {"@type": "PostalAddress", "addressLocality": e["ville"],
                                       "addressCountry": e["pays_fr"] or e["pays"]}}}
        if e["club"]:
            ev["organizer"] = {"@type": "Organization", "name": e["club"]}
        if e["lien"]:
            ev["url"] = e["lien"]
        items.append(ev)
    liste = {"@type": "ItemList", "name": "Régates des douze mois à venir",
             "numberOfItems": len(items),
             "itemListElement": [{"@type": "ListItem", "position": i, "item": ev}
                                 for i, ev in enumerate(items, 1)]}
    return jsonld.bloc(jsonld.fil("regates.html", "Calendrier des régates"), liste)


def construire(d: dict) -> str:
    epreuves = epreuves_pour_page(d)
    regions = [r for r in REGIONS if any(e["region"] == r for e in epreuves)]
    types = [t for t in TYPES if any(e["type"] == t for e in epreuves)]
    prochaine = epreuves[0]["nom"] if epreuves else ""
    # Filtre de classe : sigles par nombre d'épreuves décroissant (puis ordre alphabétique).
    # Une épreuve sans classe n'est comptée dans aucun sigle.
    compte_classes: dict[str, int] = {}
    for e in epreuves:
        for s in {c.strip() for c in e["classes"] if c and c.strip()}:
            compte_classes[s] = compte_classes.get(s, 0) + 1
    classes = [{"s": s, "n": regates_classes.nom(s), "c": n}
               for s, n in sorted(compte_classes.items(), key=lambda kv: (-kv[1], kv[0].lower()))]
    codes_pays = {e["pays"] for e in epreuves if e["pays"] in regates_drapeaux.DRAPEAUX}
    donnees = {
        "aujourdhui": date.today().isoformat(),
        # URL publique du relais d'alertes ; vide = le bouton « m'alerter » reste caché.
        "alertes_url": os.environ.get("ALERTES_BASE_URL", ""),
        "centres": {c: list(v) for c, v in _PAYS_CENTRE.items()},
        "mois": MOIS_FR[1:],
        "epreuves": epreuves,
        "prochaine": prochaine,
        "classes": classes,
        "jauges": list(regates_classes.JAUGES),
        "noms": regates_classes.NOMS,
        "pays": {c: regates_drapeaux.NOMS_PAYS[c] for c in sorted(codes_pays)},
    }
    # Pictogrammes des types : tracés au trait, couleur = celle du texte voisin (jamais seuls : le mot suit).
    icones = (
        '<symbol id="i-regate" viewBox="0 0 16 16"><path d="M8 2v10M8 2l5 9H8M3 12h10l-1.5 2h-7z"/></symbol>'
        '<symbol id="i-champ" viewBox="0 0 16 16"><path d="M5 2h6v4a3 3 0 0 1-6 0zM5 3.5H3v1.2a2 2 0 0 0 2 2M11 3.5h2v1.2a2 2 0 0 1-2 2M8 9v3M5.5 14h5"/></symbol>'
        '<symbol id="i-club" viewBox="0 0 16 16"><path d="M2 8l6-5 6 5M4 7.5V13h8V7.5M7 13v-3h2v3"/></symbol>'
        '<symbol id="i-large" viewBox="0 0 16 16"><path d="M1.5 6c1.5-1.6 3-1.6 4.5 0s3 1.6 4.5 0 3-1.6 4.5 0M1.5 10c1.5-1.6 3-1.6 4.5 0s3 1.6 4.5 0 3-1.6 4.5 0"/></symbol>'
    )
    sprite = (
        '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
        + icones + regates_drapeaux.sprite(codes_pays) + "</svg>"
    )

    def menu(groupe, etiquette, valeurs, defaut):
        """Un menu déroulant de filtre ; l'option par défaut est retenue et servira à marquer l'état."""
        options = "".join(
            f'<option value="{v}"{" selected" if v == defaut else ""}>{libelle}</option>'
            for v, libelle in valeurs)
        return (f'<select class="menu" data-groupe="{groupe}" data-defaut="{defaut}" '
                f'aria-label="{etiquette}">{options}</select>')

    filtres = (
        '<div class="filtres">'
        '<div class="groupe"><span class="etiq">Lieu</span>'
        + menu("region", "Lieu", [("tout", "Tous les lieux")] + [(r, r) for r in regions], "tout")
        + "</div>"
        '<div class="groupe"><span class="etiq">Type</span>'
        + menu("type", "Type de course", [("tout", "Tous les types")]
               + [(t, t.capitalize()) for t in types], "tout")
        + "</div>"
        '<div class="groupe"><span class="etiq" id="etiq-pays">Pays</span>'
        '<select class="menu" id="pays" data-groupe="pays" data-defaut="tous"'
        ' aria-label="Pays"></select></div>'
        '<div class="groupe"><span class="etiq" id="etiq-classe">Bateau</span>'
        '<select class="menu" id="classe" data-groupe="classe" data-defaut="tous"'
        ' aria-label="Classe de bateau"></select></div>'
        '<div class="groupe"><span class="etiq">Quand</span>'
        + menu("quand", "Quand", [("venir", "À venir"), ("tout", "Toutes les dates")], "venir")
        + "</div>"
        # Le bouton est caché sans navigateur capable de géolocaliser ; le texte est posé par le JS (six langues).
        '<div class="groupe"><button class="btn-proche" id="btn-proche" type="button" hidden></button></div>'
        '</div><p class="proche-msg" id="proche-msg" role="status" hidden></p>'
    )

    maj = d.get("maj", "")[:10]
    maj_lisible = ""
    if maj:
        j = date.fromisoformat(maj)
        maj_lisible = f"{JOURS_FR[j.weekday()]} {j.day} {MOIS_FR[j.month]} {j.year}"

    sources = sorted({s for e in d["regates"] for s in e.get("sources", [])})
    noms_source = {
        "manage2sail": "Manage2Sail", "ffvoile": "FFVoile", "acvl": "ACVL",
        "worldsailing": "World Sailing", "spencer": "Spencer", "fonds-propre": "Sailing More",
        "majeures": "les sites des organisateurs",
    }

    return (
        '<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Calendrier des régates — Sailing More</title>"
        '<link rel="canonical" href="https://sailingmore.fr/regates.html">'
        + _ld_regates(epreuves) +
        '<meta name="description" content="Toutes les régates de voile : Léman, France, Suisse et '
        'monde. Dates, lieux, clubs, classes, inscriptions. Recherche et filtres.">'
        "<style>" + CSS + "</style></head><body>" + sprite +
        '<div class="page">'
        '<a class="retour" href="index.html">← Sailing More</a>'
        # Plus de ligne de liens ici : la barre du site porte le menu sur toutes les pages
        # (Nicolas, 23/11/2026), une seconde liste ne servait qu'à l'alourdir.
        +
        "<h1>Calendrier des régates</h1>"
        f'<p class="chapo">Toutes les régates de voile, du Léman au large : '
        # Le compteur de la page compte les cartes affichées, y compris les épreuves en cours
        # (commencées il y a deux jours, qui finissent dimanche). Le chapô doit dire le même
        # chiffre : deux nombres différents sur la même page donnent l'impression que l'un ment
        # (corrigé une première fois le 21/11, revenu par le filtre des trois jours).
        f'{len(epreuves)} épreuves '
        "à venir, relevées chez les organisateurs et les fédérations.</p>"
        '<div class="panneau">'
        '<div class="recherche">'
        '<div class="ligne-recherche"><div class="champ">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<circle cx="7" cy="7" r="5" stroke="#eef3f7" stroke-width="1.4"/>'
        '<path d="M10.6 10.6 14 14" stroke="#eef3f7" stroke-width="1.4"/></svg>'
        '<input id="q" type="search" placeholder="Une régate, un port, un club, une classe…" '
        'aria-label="Rechercher une épreuve" autocomplete="off">'
        "</div>"
        '<button class="btn-alerte" id="btn-alerte" type="button" hidden></button></div>'
        + filtres +
        '<form class="alerte" id="alerte" hidden></form>'
        "</div>"
        '<div class="compte"><span id="compte" role="status" aria-live="polite"></span>'
        '<span><button class="lien-effacer" id="btn-ics-tout" type="button" hidden></button> '
        '<button class="lien-effacer" id="effacer" type="button">Tout effacer</button></span></div>'
        + carte_epreuves.html() +
        '<div id="liste"></div>'
        "</div>"
        '<p class="pied">Calendrier relevé le ' + (maj_lisible or "—") + " depuis "
        + ", ".join(noms_source.get(s, s) for s in sources) + ". "
        "Une épreuve peut apparaître plusieurs fois chez les organisateurs : "
        "les doublons sont fusionnés, pas recopiés. "
        '<a href="annonceurs.html">Un événement à signaler&nbsp;?</a> '
        'Positions des villes : données © <a href="https://www.openstreetmap.org/copyright" '
        'target="_blank" rel="noopener">OpenStreetMap</a> contributors (ODbL).</p>'
        "</div>"
        '<script type="application/json" id="donnees">'
        + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
        + "</script><script>" + carte_epreuves.js() + JS + "</script>"
        "</body></html>\n"
    )


def verifier(d: dict, avertissements: list[str] | None = None) -> list[str]:
    """Contrôle en lecture seule : renvoie les défauts trouvés (liste vide = tout va bien).

    `avertissements`, si fourni, reçoit ce qui doit être dit sans faire échouer le contrôle
    (aujourd'hui : les épreuves repliées vers « France » faute de puce, décision du 21/11).

    Rien n'est écrit : la page est construite en mémoire seulement, pour comparer ce que
    l'internaute verrait (chapô, données embarquées, puces de filtre) à ce que le JSON contient.
    """
    problemes: list[str] = []
    regates = d.get("regates")
    if not isinstance(regates, list):
        return ["le JSON n'a pas de liste « regates »"]

    if d.get("total") != len(regates):
        problemes.append(f"compteur « total » : {d.get('total')} annoncé, {len(regates)} présentes")

    # « a_venir » est figé à la date de la collecte : on le recompte à cette date-là, pas à
    # aujourd'hui, sinon un JSON de la veille serait déclaré faux alors qu'il est juste.
    jour_maj = (d.get("maj") or "")[:10]
    if jour_maj:
        attendu = sum(1 for e in regates if str(e.get("debut", ""))[:10] >= jour_maj)
        if d.get("a_venir") != attendu:
            problemes.append(f"compteur « a_venir » : {d.get('a_venir')} annoncé, {attendu} recomptées au {jour_maj}")
    else:
        problemes.append("pas de date « maj » dans le JSON")

    # Dates : `epreuves_pour_page` lit `fin` sans garde-fou et lèverait une exception sur une
    # date impossible ; on les repère donc d'abord, sans jamais l'appeler sur des données douteuses.
    invalides = []
    for e in regates:
        for champ in ("debut", "fin"):
            try:
                date.fromisoformat(e[champ])
            except Exception:  # noqa: BLE001
                invalides.append(f"{e.get('nom', '?')[:40]} ({champ}={e.get(champ)!r})")
        try:
            if date.fromisoformat(e["fin"]) < date.fromisoformat(e["debut"]):
                invalides.append(f"{e.get('nom', '?')[:40]} (fin avant début)")
        except Exception:  # noqa: BLE001
            pass
    if invalides:
        problemes.append(f"{len(invalides)} date(s) invalide(s), ex. : " + " ; ".join(invalides[:3]))
        return problemes  # la suite suppose des dates lisibles

    epreuves = epreuves_pour_page(d)
    if not epreuves:
        problemes.append("aucune épreuve à venir : la page serait vide")

    # Filtres : une épreuve dont la région ou le type n'a pas de puce n'est atteignable que par
    # « Tout » ; la somme des puces doit donc retomber sur le total.
    for libelle, valeurs, cle in (("région", REGIONS, "region"), ("type", TYPES, "type")):
        hors = sorted({e[cle] for e in epreuves if e[cle] not in valeurs})
        if hors:
            problemes.append(f"{libelle} sans puce de filtre : {', '.join(map(repr, hors))}")
    # Un département sans puce est replié vers « France » par la collecte : ce n'est pas un
    # défaut, mais il ne doit jamais passer en silence. Compté sur les épreuves de la page.
    replis: dict[str, int] = {}
    for e in regates:
        rep = e.get("region_repliee")
        if rep and affichable(e):
            replis[rep] = replis.get(rep, 0) + 1
    if replis and avertissements is not None:
        n = sum(replis.values())
        s = "s" if n > 1 else ""
        detail = ", ".join(f"{r} {k}" for r, k in sorted(replis.items()))
        avertissements.append(f"{n} épreuve{s} repliée{s} vers « France » faute de puce ({detail})")
    # Un pays sans drapeau dans la table : la carte n'a rien (voulu), mais on le dit pour l'ajouter.
    sans_drapeau: dict[str, int] = {}
    for e in epreuves:
        if e["pays"] and e["pays"] not in regates_drapeaux.DRAPEAUX:
            sans_drapeau[e["pays"]] = sans_drapeau.get(e["pays"], 0) + 1
    if sans_drapeau and avertissements is not None:
        avertissements.append("pays sans drapeau : " + ", ".join(f"{c} {n}" for c, n in sorted(sans_drapeau.items())))
    # Le drapeau doit s'accorder avec ce que l'épreuve dit d'elle-même : « Championnat du Monde
    # Dragon HONG KONG » portait un drapeau français (24/11/2026). Deux contrôles, de force
    # différente : une épreuve située hors de France et étiquetée « FRA » est une faute (le
    # défaut fédéral d'avant), tandis qu'un nom de pays dans l'intitulé n'est qu'un indice —
    # « Guyader Bermudes 1000 Race » part de Lorient, « Macao Match Cup » se court à Macao.
    # Le second est donc signalé, jamais bloquant.
    import regates_lieux as _lieux
    incoherentes = [e for e in regates if e.get("etranger") and e["pays"] == "FRA"]
    if incoherentes:
        problemes.append(f"{len(incoherentes)} épreuve(s) situées hors de France et étiquetées FRA : "
                         + " · ".join(f"{e['nom'][:40]} ({e['club'][:18]})" for e in incoherentes[:4]))
    douteux = []
    for e in regates:
        vus = _lieux.pays_du_texte(" ".join((e["nom"], e["ville"]))) or _lieux.pays_du_texte(e["club"])
        if len(vus) == 1 and e["pays"] != next(iter(vus)):
            douteux.append(f"{e['nom'][:40]} — {e['pays'] or 'aucun pays'} alors que le texte dit "
                           f"{next(iter(vus))}")
    if douteux and avertissements is not None:
        avertissements.append(f"{len(douteux)} pays contredits par le nom ou le club, à vérifier : "
                              + " · ".join(douteux[:4]))
    aujourdhui = date.today().isoformat()
    if any(e["type"] == "hors-regate" for e in epreuves):
        problemes.append("des épreuves « hors-regate » sont dans la page")
    if any(e["fin"] < aujourdhui for e in epreuves):
        problemes.append("des épreuves déjà terminées sont dans la page")

    # Ce que la page dit d'elle-même : chapô, données embarquées et puces doivent s'accorder.
    html = construire(d)
    m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', html, re.S)
    embarquees = json.loads(m.group(1))["epreuves"] if m else None
    if embarquees is None:
        problemes.append("données embarquées introuvables dans la page")
    elif len(embarquees) != len(epreuves):
        problemes.append(f"{len(embarquees)} épreuves embarquées pour {len(epreuves)} attendues")
    c = re.search(r"(\d+) épreuves à venir", html)
    if not c or int(c.group(1)) != len(epreuves):
        problemes.append(f"chapô : {c.group(1) if c else 'absent'} contre {len(epreuves)} épreuves")
    for groupe, valeurs, cle in (("region", REGIONS, "region"), ("type", TYPES, "type")):
        presentes = {e[cle] for e in epreuves}
        voulues = {v for v in valeurs if v in presentes}
        bloc = re.search(rf'<select class="menu" data-groupe="{groupe}".*?</select>', html, re.S)
        options = set(re.findall(r'<option value="([^"]*)"', bloc.group(0))) - {"tout"} if bloc else set()
        if options != voulues:
            problemes.append(f"menu « {groupe} » : {sorted(options)} au lieu de {sorted(voulues)}")
    # Le menu « bateau » est rempli par le navigateur : ce qui compte, c'est que les données
    # embarquées portent bien toutes les classes (sans elles, le menu serait vide).
    if "id=\"classe\"" not in html:
        problemes.append("menu « bateau » absent de la page")
    elif not (embarquees and any(e.get("classes") for e in embarquees)):
        problemes.append("aucune classe dans les données embarquées : le menu « bateau » serait vide")
    return problemes


def main() -> int:
    ecrire = "--ecrire" in sys.argv
    controle = "--verifier" in sys.argv
    if not (ecrire or controle):
        # Sans drapeau on n'écrit rien : l'ancienne version écrivait la page de travail sans
        # la charte, même quand on ne demandait qu'un contrôle.
        print("Rien à faire : indiquer --verifier (lecture seule) ou --ecrire (écrit la page).",
              file=sys.stderr)
        return 2
    d = charger()

    if controle:
        avertissements: list[str] = []
        problemes = verifier(d, avertissements)
        n = len(d["regates"]) if isinstance(d.get("regates"), list) else 0
        for a in avertissements:
            print("AVERTISSEMENT · " + a)  # dit, sans changer le code de sortie
        if problemes:
            for p in problemes:
                print("ÉCHEC · " + p)
            print(f"{len(problemes)} contrôle(s) en échec sur {n} épreuves au total")
            return 1
        print(f"OK · {len(epreuves_pour_page(d))} épreuves à venir, {n} au total dans le JSON")
        return 0

    html = construire(d)
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "regates.html").write_text(html, encoding="utf-8")
    print(f"{SORTIE/'regates.html'} · {len(html):,} car".replace(",", " "))
    epreuves = epreuves_pour_page(d)
    print(f"{len(epreuves)} épreuves embarquées · {len(d['regates'])} au total dans le JSON")
    if epreuves:
        print(f"première : {epreuves[0]['debut']} {epreuves[0]['nom']} "
              f"({epreuves[0]['region']})")
        print(f"dernière : {epreuves[-1]['debut']} {epreuves[-1]['nom']}")
    from collections import Counter
    print("régions :", dict(Counter(e["region"] for e in epreuves)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
