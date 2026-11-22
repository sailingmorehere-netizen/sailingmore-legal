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
from datetime import date, datetime
from pathlib import Path

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
           "GRE": "Grèce", "CRO": "Croatie", "POL": "Pologne", "IRL": "Irlande"}

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
.filtres{display:flex;flex-direction:column;gap:.42rem;margin-top:.7rem}
.filtres .groupe{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
.filtres .etiq{font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#6f8598;
  margin-right:.2rem}
.puce{font:inherit;font-size:.72rem;letter-spacing:.04em;color:var(--gris);background:none;
  border:1px solid rgba(255,255,255,.16);border-radius:2px;padding:.28rem .6rem;cursor:pointer;
  transition:color .15s,border-color .15s,background .15s}
.puce:hover{color:#fff;border-color:rgba(255,255,255,.4)}
.puce[aria-pressed="true"]{color:#fff;border-color:var(--rouge);background:rgba(226,58,62,.14)}
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
.vide{padding:3rem 0;color:var(--gris);font-size:.9rem}
.pied{margin-top:3.6rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,.09);
  color:#6f8598;font-size:.72rem;line-height:1.8}
.pied a{color:var(--gris);text-decoration:underline;text-decoration-color:rgba(226,58,62,.5)}

@media (max-width:640px){
  .page{padding:2.4rem 1rem 4rem}
  .epreuve{grid-template-columns:1fr;gap:.15rem}
  .quand{margin-bottom:.1rem}
  .cles{justify-content:flex-start;margin-top:.3rem}
  .recherche{padding:.7rem 0 .8rem}
  .filtres{gap:.3rem}
  .filtres .etiq{width:100%}
}
"""

JS = r"""
(function(){
  var data = JSON.parse(document.getElementById('donnees').textContent);
  var champ = document.getElementById('q');
  var compte = document.getElementById('compte');
  var liste = document.getElementById('liste');
  var boutons = Array.prototype.slice.call(document.querySelectorAll('.puce'));
  var effacer = document.getElementById('effacer');
  var etat = {region:'tout', type:'tout', quand:'venir', texte:''};

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
    if(etat.quand === 'venir' && e.debut < data.aujourdhui) return false;
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
    var groupes = [], vus = {};
    gardes.forEach(function(e){
      var k = moisCle(e.debut);
      if(!vus[k]){vus[k]=[];groupes.push(k);}
      vus[k].push(e);
    });
    var html = '';
    groupes.forEach(function(k){
      var l = vus[k];
      html += '<section class="mois"><h2>' + moisLisible(k) + '<span>' + l.length + (l.length>1?' épreuves':' épreuve') + '</span></h2>';
      l.forEach(function(e){
        var an = e.debut.slice(0,4) !== data.aujourdhui.slice(0,4) || etat.quand === 'tout';
        var dates = (e.fin && e.fin !== e.debut) ? jour(e.debut, an) + ' → ' + jour(e.fin, an) : jour(e.debut, an);
        var lieu = [e.ville, e.club].filter(Boolean).join(' · ') || e.pays_fr;
        var tags = '';
        if(e.region === 'Léman') tags += '<span class="tag leman">Léman</span>';
        else if(e.region) tags += '<span class="tag">' + e.region + '</span>';
        if(e.classes && e.classes.length) tags += '<span class="tag">' + e.classes.slice(0,4).join(' · ') + '</span>';
        if(e.type === 'championnat') tags += '<span class="tag rouge">Championnat</span>';
        if(e.annulee) tags += '<span class="tag rouge">Annulée</span>';
        html += '<article class="epreuve">'
             + '<div class="quand"><span class="j">' + dates + '</span></div>'
             + '<div><div class="titre">' + casse(e.nom) + '</div>'
             + (lieu ? '<div class="ou"><span class="vil">' + casse(lieu) + '</span></div>' : '')
             + (tags ? '<div class="tags">' + tags + '</div>' : '')
             + '</div>'
             + '<div class="cles">' + (e.lien ? '<a href="' + e.lien + '" target="_blank" rel="noopener">' + (e.lien_quoi||'site') + ' →</a>' : '') + '</div>'
             + '</article>';
      });
      html += '</section>';
    });
    liste.innerHTML = html || '<p class="vide">Aucune épreuve ne correspond à ces filtres.</p>';
    compte.innerHTML = '<span><b>' + gardes.length + '</b> épreuve' + (gardes.length>1?'s':'') + '</span>'
      + (etat.quand==='venir' && gardes.length ? '<span>la prochaine : <b>' + casse(gardes[0].nom) + '</b></span>' : '');
  }

  boutons.forEach(function(b){
    b.addEventListener('click', function(){
      var g = b.dataset.groupe, v = b.dataset.valeur;
      etat[g] = v;
      document.querySelectorAll('.puce[data-groupe="'+g+'"]').forEach(function(x){
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      dessine();
    });
  });
  champ.addEventListener('input', function(){ etat.texte = champ.value; dessine(); });
  effacer.addEventListener('click', function(){
    etat = {region:'tout', type:'tout', quand:'venir', texte:''};
    champ.value = '';
    document.querySelectorAll('.puce').forEach(function(x){
      x.setAttribute('aria-pressed', x.dataset.valeur === (x.dataset.groupe==='quand'?'venir':'tout') ? 'true':'false');
    });
    dessine();
  });
  dessine();
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
    return len(epreuves_pour_page(d))


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
        out.append({
            "nom": e["nom"],
            "debut": e["debut"],
            "fin": e["fin"],
            "ville": e["ville"],
            "club": e["club"],
            "classes": e["classes"][:6],
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


def construire(d: dict) -> str:
    epreuves = epreuves_pour_page(d)
    regions = [r for r in REGIONS if any(e["region"] == r for e in epreuves)]
    types = [t for t in TYPES if any(e["type"] == t for e in epreuves)]
    prochaine = epreuves[0]["nom"] if epreuves else ""
    donnees = {
        "aujourdhui": date.today().isoformat(),
        "mois": MOIS_FR[1:],
        "epreuves": epreuves,
        "prochaine": prochaine,
    }

    def puces(groupe, valeurs, defaut):
        return "".join(
            f'<button class="puce" data-groupe="{groupe}" data-valeur="{v}" '
            f'aria-pressed="{"true" if v == defaut else "false"}">{libelle}</button>'
            for v, libelle in valeurs)

    filtres = (
        '<div class="filtres">'
        '<div class="groupe"><span class="etiq">Lieu</span>'
        + puces("region", [("tout", "Tout")] + [(r, r) for r in regions], "tout")
        + "</div>"
        '<div class="groupe"><span class="etiq">Type</span>'
        + puces("type", [("tout", "Tout")] + [(t, t.capitalize()) for t in types], "tout")
        + "</div>"
        '<div class="groupe"><span class="etiq">Quand</span>'
        + puces("quand", [("venir", "À venir"), ("tout", "Tout")], "venir")
        + "</div></div>"
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
        '<meta name="description" content="Toutes les régates de voile : Léman, France, Suisse et '
        'monde. Dates, lieux, clubs, classes, inscriptions. Recherche et filtres.">'
        "<style>" + CSS + "</style></head><body>"
        '<div class="page">'
        '<a class="retour" href="index.html">← Sailing More</a>'
        "<h1>Calendrier des régates</h1>"
        f'<p class="chapo">Toutes les régates de voile, du Léman au large : '
        # Le compteur de la page compte les cartes affichées, y compris les épreuves en cours
        # (commencées il y a deux jours, qui finissent dimanche). Le chapô doit dire le même
        # chiffre : deux nombres différents sur la même page donnent l'impression que l'un ment
        # (corrigé une première fois le 21/11, revenu par le filtre des trois jours).
        f'{len(epreuves)} épreuves '
        "à venir, relevées chez les organisateurs et les fédérations. "
        "Recherchez par nom, par lieu, par classe — ou filtrez.</p>"
        '<div class="panneau">'
        '<div class="recherche">'
        '<div class="champ">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<circle cx="7" cy="7" r="5" stroke="#eef3f7" stroke-width="1.4"/>'
        '<path d="M10.6 10.6 14 14" stroke="#eef3f7" stroke-width="1.4"/></svg>'
        '<input id="q" type="search" placeholder="Une régate, un port, un club, une classe…" '
        'aria-label="Rechercher une épreuve" autocomplete="off">'
        "</div>"
        + filtres +
        "</div>"
        '<div class="compte"><span id="compte"></span>'
        '<button class="lien-effacer" id="effacer" type="button">Tout effacer</button></div>'
        '<div id="liste"></div>'
        "</div>"
        '<p class="pied">Calendrier relevé le ' + (maj_lisible or "—") + " depuis "
        + ", ".join(noms_source.get(s, s) for s in sources) + ". "
        "Une épreuve peut apparaître plusieurs fois chez les organisateurs : "
        "les doublons sont fusionnés, pas recopiés. "
        '<a href="annonceurs.html">Un événement à signaler&nbsp;?</a></p>'
        "</div>"
        '<script type="application/json" id="donnees">'
        + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
        + "</script><script>" + JS + "</script>"
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
        puces = set(re.findall(rf'data-groupe="{groupe}" data-valeur="([^"]*)"', html)) - {"tout"}
        if puces != voulues:
            problemes.append(f"puces « {groupe} » : {sorted(puces)} au lieu de {sorted(voulues)}")
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
