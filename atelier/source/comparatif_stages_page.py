#!/usr/bin/env python3
"""Construit `comparatif-stages.html` : les stages à prix publié, côte à côte, classés par prix au jour.

Entrée : `projets/sailingmore/stages.json` (même source que `stages_page.py`, mêmes filtres de fraîcheur
         et de « n'est pas un stage » : on ne recompte rien soi-même).
Sortie : `comparatif-stages.html` dans le dossier du site (appelé par `accueil_site.sortir_le_site`).

Règles (tâche n°70, 25/11/2026) :
  - seules les offres avec un prix publié entrent dans le tableau ; les autres sont comptées en tête de
    page et renvoient à stages.html, elles ne se mêlent jamais au classement ;
  - le prix est affiché dans sa devise d'origine ; l'équivalent en euros est une seconde ligne, étiquetée
    « ≈ … € (taux du <date>) », jamais substituée au prix de l'école ;
  - classement par défaut : prix par jour (prix_eur / duree_jours) ; une offre sans durée connue passe
    après toutes les autres (« durée non publiée »), sans prix au jour inventé.
Le tableau est écrit en HTML dans la page (lisible sans JavaScript) ; le script ne fait que trier et masquer.
"""
from __future__ import annotations

import html as H
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stages_page as SP  # noqa: E402

PAGE = "comparatif-stages.html"
DUREES = [("1", 1, 1), ("2-3", 2, 3), ("4-7", 4, 7), ("8+", 8, 9999)]

UI = {
 "fr": {"titre": "Comparatif des stages de voile", "retour": "← Sailing More",
        "chapo": "Les stages dont l'école publie le prix, classés par prix au jour. Le prix est celui de l'école, dans sa devise ; l'équivalent en euros est indicatif. Chaque ligne renvoie à la fiche de l'école, qui fait foi.",
        "pays": "Destination", "langue": "Langue", "niveau": "Niveau", "duree": "Durée", "tri": "Classer par",
        "tous": "Tous", "t_jour": "Prix au jour", "t_total": "Prix total", "t_duree": "Durée",
        "col_stage": "Stage", "col_prix": "Prix", "col_jour": "Par jour", "col_duree": "Durée", "col_niv": "Niveau",
        "col_lang": "Langue", "col_pays": "Destination", "j": "j", "jours": "jours", "nd": "durée non publiée",
        "compte": "{n} offres affichées sur {t}", "aucune": "Aucune offre ne répond à ces filtres.",
        "taux": "≈ {x} € (taux du {d})", "voir": "Voir →", "sans_prix": "{n} autres offres n'affichent pas de prix : elles sont sur la page Stages, hors de ce classement.",
        "stages": "Toutes les offres, avec ou sans prix →",
        "pied": "Prix relevés sur les fiches des écoles le {d}. Un prix a changé ou un stage manque ? L'école fait foi."},
 "en": {"titre": "Sailing course comparison", "retour": "← Sailing More",
        "chapo": "Courses whose school publishes a price, ranked by price per day. The price is the school's, in its own currency; the euro equivalent is indicative. Each row links to the school's page, which is the authority.",
        "pays": "Destination", "langue": "Language", "niveau": "Level", "duree": "Length", "tri": "Rank by",
        "tous": "All", "t_jour": "Price per day", "t_total": "Total price", "t_duree": "Length",
        "col_stage": "Course", "col_prix": "Price", "col_jour": "Per day", "col_duree": "Length", "col_niv": "Level",
        "col_lang": "Language", "col_pays": "Destination", "j": "d", "jours": "days", "nd": "length not published",
        "compte": "{n} offers shown of {t}", "aucune": "No offer matches these filters.",
        "taux": "≈ {x} € (rate of {d})", "voir": "See →", "sans_prix": "{n} other offers show no price: they are on the Courses page, outside this ranking.",
        "stages": "All offers, with or without price →",
        "pied": "Prices read off the schools' pages on {d}. A price changed or a course missing? The school is the authority."},
 "de": {"titre": "Segelkurse im Vergleich", "retour": "← Sailing More",
        "chapo": "Kurse, deren Schule den Preis veröffentlicht, nach Tagespreis sortiert. Der Preis ist der der Schule, in ihrer Währung; der Eurobetrag ist ein Richtwert. Jede Zeile führt zur Seite der Schule, die massgebend ist.",
        "pays": "Ziel", "langue": "Sprache", "niveau": "Niveau", "duree": "Dauer", "tri": "Sortieren nach",
        "tous": "Alle", "t_jour": "Preis pro Tag", "t_total": "Gesamtpreis", "t_duree": "Dauer",
        "col_stage": "Kurs", "col_prix": "Preis", "col_jour": "Pro Tag", "col_duree": "Dauer", "col_niv": "Niveau",
        "col_lang": "Sprache", "col_pays": "Ziel", "j": "T", "jours": "Tage", "nd": "Dauer nicht veröffentlicht",
        "compte": "{n} von {t} Angeboten angezeigt", "aucune": "Kein Angebot mit diesen Filtern.",
        "taux": "≈ {x} € (Kurs vom {d})", "voir": "Ansehen →", "sans_prix": "{n} weitere Angebote zeigen keinen Preis: sie stehen auf der Kursseite, ausserhalb dieser Rangliste.",
        "stages": "Alle Angebote, mit oder ohne Preis →",
        "pied": "Preise von den Seiten der Schulen am {d} gelesen. Preis geändert oder Kurs fehlt? Die Schule ist massgebend."},
 "it": {"titre": "Confronto dei corsi di vela", "retour": "← Sailing More",
        "chapo": "I corsi di cui la scuola pubblica il prezzo, ordinati per prezzo al giorno. Il prezzo è quello della scuola, nella sua valuta; l'equivalente in euro è indicativo. Ogni riga rimanda alla pagina della scuola, che fa fede.",
        "pays": "Destinazione", "langue": "Lingua", "niveau": "Livello", "duree": "Durata", "tri": "Ordina per",
        "tous": "Tutti", "t_jour": "Prezzo al giorno", "t_total": "Prezzo totale", "t_duree": "Durata",
        "col_stage": "Corso", "col_prix": "Prezzo", "col_jour": "Al giorno", "col_duree": "Durata", "col_niv": "Livello",
        "col_lang": "Lingua", "col_pays": "Destinazione", "j": "g", "jours": "giorni", "nd": "durata non pubblicata",
        "compte": "{n} offerte mostrate su {t}", "aucune": "Nessuna offerta con questi filtri.",
        "taux": "≈ {x} € (cambio del {d})", "voir": "Vedi →", "sans_prix": "Altre {n} offerte non mostrano il prezzo: sono nella pagina dei corsi, fuori da questa classifica.",
        "stages": "Tutte le offerte, con o senza prezzo →",
        "pied": "Prezzi letti dalle pagine delle scuole il {d}. Un prezzo è cambiato o manca un corso? Fa fede la scuola."},
 "es": {"titre": "Comparativa de cursos de vela", "retour": "← Sailing More",
        "chapo": "Los cursos cuya escuela publica el precio, ordenados por precio al día. El precio es el de la escuela, en su moneda; el equivalente en euros es indicativo. Cada fila remite a la ficha de la escuela, que es la que manda.",
        "pays": "Destino", "langue": "Idioma", "niveau": "Nivel", "duree": "Duración", "tri": "Ordenar por",
        "tous": "Todos", "t_jour": "Precio al día", "t_total": "Precio total", "t_duree": "Duración",
        "col_stage": "Curso", "col_prix": "Precio", "col_jour": "Por día", "col_duree": "Duración", "col_niv": "Nivel",
        "col_lang": "Idioma", "col_pays": "Destino", "j": "d", "jours": "días", "nd": "duración no publicada",
        "compte": "{n} ofertas mostradas de {t}", "aucune": "Ninguna oferta con estos filtros.",
        "taux": "≈ {x} € (cambio del {d})", "voir": "Ver →", "sans_prix": "Otras {n} ofertas no muestran precio: están en la página de cursos, fuera de esta clasificación.",
        "stages": "Todas las ofertas, con o sin precio →",
        "pied": "Precios leídos en las fichas de las escuelas el {d}. ¿Ha cambiado un precio o falta un curso? Manda la escuela."},
 "pt": {"titre": "Comparação de cursos de vela", "retour": "← Sailing More",
        "chapo": "Os cursos cuja escola publica o preço, ordenados por preço por dia. O preço é o da escola, na sua moeda; o equivalente em euros é indicativo. Cada linha remete para a página da escola, que é quem decide.",
        "pays": "Destino", "langue": "Idioma", "niveau": "Nível", "duree": "Duração", "tri": "Ordenar por",
        "tous": "Todos", "t_jour": "Preço por dia", "t_total": "Preço total", "t_duree": "Duração",
        "col_stage": "Curso", "col_prix": "Preço", "col_jour": "Por dia", "col_duree": "Duração", "col_niv": "Nível",
        "col_lang": "Idioma", "col_pays": "Destino", "j": "d", "jours": "dias", "nd": "duração não publicada",
        "compte": "{n} ofertas mostradas de {t}", "aucune": "Nenhuma oferta com estes filtros.",
        "taux": "≈ {x} € (câmbio de {d})", "voir": "Ver →", "sans_prix": "Outras {n} ofertas não mostram preço: estão na página de cursos, fora desta classificação.",
        "stages": "Todas as ofertas, com ou sem preço →",
        "pied": "Preços lidos nas páginas das escolas a {d}. Mudou um preço ou falta um curso? A escola é quem decide."},
}

CSS = """
:root{--fond:#0a1a2b;--carte:#0f2438;--trait:#1d3549;--encre:#e8eef5;--doux:#9db2c7;--accent:#5fd3c4}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--encre);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:inherit}
.page{max-width:72rem;margin:0 auto;padding:2rem 1.2rem 5rem}
h1{font-size:clamp(1.6rem,4vw,2.4rem);margin:.2rem 0 .6rem;letter-spacing:-.02em}
.chapo{color:var(--doux);max-width:46rem;margin:0 0 1.2rem}
.retour{display:inline-block;color:var(--doux);text-decoration:none;font-size:.9rem;margin-bottom:.6rem}
.filtres{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.7rem;background:var(--carte);border:1px solid var(--trait);border-radius:14px;padding:.9rem;margin-bottom:1rem}
label{display:flex;flex-direction:column;gap:.25rem;font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux)}
select{background:#0b1e30;color:var(--encre);border:1px solid var(--trait);border-radius:9px;padding:.5rem .55rem;font:inherit;font-size:.92rem;min-width:0}
.compte,.sans-prix{color:var(--doux);font-size:.9rem;margin:.2rem 0 .8rem}
.tab{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th,td{text-align:left;padding:.55rem .6rem;border-bottom:1px solid var(--trait);vertical-align:top}
th{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);font-weight:400;white-space:nowrap}
td.n{white-space:nowrap}
td small{display:block;color:var(--doux);font-size:.78rem}
td.stage strong{font-weight:600}
td a{color:var(--accent);text-decoration:none}
.pied{margin-top:2rem;color:var(--doux);font-size:.82rem;border-top:1px solid var(--trait);padding-top:1rem}
.aucune{color:var(--doux);padding:1.5rem 0}
"""

JS = r"""
var D=JSON.parse(document.getElementById('donnees').textContent),U=D.ui,L='fr';
try{L=(window.smLangue?window.smLangue():'fr')}catch(e){}
if(!U[L])L='en';
function t(k){return (U[L]&&U[L][k])||U.fr[k]||k}
var T=document.getElementById('tb'),R=[].slice.call(T.rows);
function num(r,k){var v=r.getAttribute('data-'+k);return v===''?Infinity:parseFloat(v)}
function remplir(id,liste){var s=document.getElementById(id),v=s.value;
  s.innerHTML='<option value="">'+t('tous')+'</option>'+liste.map(function(o){return '<option value="'+o[0]+'">'+o[1]+'</option>'}).join('');s.value=v}
function textes(){
  [].forEach.call(document.querySelectorAll('[data-t]'),function(e){var k=e.getAttribute('data-t');
    var s=(e.getAttribute('data-sub')||'').split('|');
    e.textContent=t(k).replace('{n}',s[0]).replace('{d}',s[1])});
  [].forEach.call(document.querySelectorAll('[data-niv]'),function(e){e.textContent=(D.niv[e.getAttribute('data-niv')]||{})[L]||(D.niv[e.getAttribute('data-niv')]||{}).fr||''});
  [].forEach.call(document.querySelectorAll('[data-nd]'),function(e){e.textContent=t('nd')});
  [].forEach.call(document.querySelectorAll('[data-taux]'),function(e){var p=e.getAttribute('data-taux').split('|');e.textContent=t('taux').replace('{x}',p[0]).replace('{d}',p[1])});
  [].forEach.call(document.querySelectorAll('[data-voir]'),function(e){e.textContent=t('voir')});
  var o=[['jour',t('t_jour')],['total',t('t_total')],['duree',t('t_duree')]];
  var s=document.getElementById('f-tri'),v=s.value||'jour';
  s.innerHTML=o.map(function(x){return '<option value="'+x[0]+'">'+x[1]+'</option>'}).join('');s.value=v;
  remplir('f-pays',D.pays);remplir('f-langue',D.langues.map(function(c){return [c,D.noms[c]||c]}));
  remplir('f-niveau',D.niveaux.map(function(n){return [n,(D.niv[n][L]||D.niv[n].fr)]}));
  remplir('f-duree',D.durees.map(function(d){return [d[0],d[0]+' '+t('jours')]}));
}
function appliquer(){
  var f={pays:g('f-pays'),langue:g('f-langue'),niveau:g('f-niveau'),duree:g('f-duree')},tri=g('f-tri')||'jour',n=0,l=[];
  function g(i){return document.getElementById(i).value}
  R.forEach(function(r){
    var ok=(!f.pays||r.getAttribute('data-pays')===f.pays)&&(!f.langue||r.getAttribute('data-langue')===f.langue)
      &&(!f.niveau||r.getAttribute('data-niveau')===f.niveau)&&(!f.duree||r.getAttribute('data-duree-c')===f.duree);
    r.hidden=!ok;if(ok)n++});
  var k={jour:'jour',total:'total',duree:'duree'}[tri];
  R.sort(function(a,b){var x=num(a,k),y=num(b,k);return x===y?num(a,'total')-num(b,'total'):x-y});
  R.forEach(function(r){T.appendChild(r)});
  document.getElementById('compte').textContent=t('compte').replace('{n}',n).replace('{t}',R.length);
  document.getElementById('aucune').hidden=n>0;
}
textes();
[].forEach.call(document.querySelectorAll('.filtres select'),function(s){s.addEventListener('change',appliquer)});
appliquer();
"""


def _classe_duree(j):
    if not j:
        return ""
    for nom, a, b in DUREES:
        if a <= j <= b:
            return nom
    return ""


def _prix_txt(o: dict) -> str:
    p = o["prix"]
    return (f"{p:,.0f}".replace(",", " ") if float(p).is_integer() else f"{p:,.2f}".replace(",", " "))


def lignes(d: dict | None = None):
    """(offres_avec_prix, nombre_sans_prix) — filtres de fraîcheur et de « stage » identiques à stages.html."""
    d = d if d is not None else SP.charger()
    ok = [o for o in d.get("offres", []) if SP.affichable(o) and not SP.non_stage(o.get("titre"), o.get("prix_eur"))]
    ok = [SP.avec_niveau(o) for o in ok]
    avec = [o for o in ok if o.get("prix_publie") and o.get("prix_eur") is not None and o.get("prix") is not None]
    for o in avec:
        j = o.get("duree_jours") or 0
        o["_jour"] = round(o["prix_eur"] / j, 2) if j > 0 else None
    avec.sort(key=lambda o: (o["_jour"] is None, o["_jour"] if o["_jour"] is not None else 0, o["prix_eur"]))
    return avec, len(ok) - len(avec), d


def construire(d: dict | None = None) -> str:
    import site_blocks
    avec, sans, d = lignes(d)
    taux_date = d.get("releve") or d.get("maj") or ""
    niv_noms = {n: {lg: SP.LIBELLES_NIVEAU.get(lg, SP.LIBELLES_NIVEAU["en"])[n] for lg in UI}
                for n in SP.NIVEAUX if n in SP.LIBELLES_NIVEAU["fr"]}
    trs = []
    for o in avec:
        j = o.get("duree_jours") or 0
        dev = o.get("devise") or "EUR"
        prix = f"{_prix_txt(o)} {H.escape(dev)}"
        if dev != "EUR":
            eq = (f"<small data-taux=\"{o['prix_eur']:.0f}|{H.escape(taux_date)}\">≈ {o['prix_eur']:.0f} € "
                  f"(taux du {H.escape(taux_date)})</small>")
        else:
            eq = ""
        jour = (f"{o['_jour']:.0f} €" if o["_jour"] is not None else "—")
        duree = (f"{j}&nbsp;j" if j else "<span data-nd>durée non publiée</span>")
        niv = o.get("niveau") or ""
        niv_cell = f"<span data-niv=\"{H.escape(niv)}\">{H.escape(niv_noms.get(niv, {}).get('fr', ''))}</span>" if niv else "—"
        lien = o.get("lien") or ""
        trs.append(
            f"<tr data-pays=\"{H.escape(o.get('pays') or '')}\" data-langue=\"{H.escape(o.get('langue') or '')}\" "
            f"data-niveau=\"{H.escape(niv)}\" data-duree-c=\"{_classe_duree(j)}\" "
            f"data-jour=\"{o['_jour'] if o['_jour'] is not None else ''}\" data-total=\"{o['prix_eur']}\" "
            f"data-duree=\"{j or ''}\">"
            f"<td class=\"stage\"><strong>{H.escape(o.get('titre') or '')}</strong>"
            f"<small>{H.escape(o.get('ecole') or '')} · {H.escape(o.get('lieu') or '')}</small></td>"
            f"<td class=\"n\">{prix}{eq}</td><td class=\"n\">{jour}</td><td class=\"n\">{duree}</td>"
            f"<td>{niv_cell}</td><td>{H.escape(LANG(o))}</td><td>{H.escape(o.get('pays_nom') or '')}</td>"
            f"<td><a href=\"{H.escape(lien, quote=True)}\" rel=\"nofollow noopener\" data-voir>Voir →</a></td></tr>")
    donnees = {
        "ui": UI, "niv": niv_noms, "noms": SP.LANGUES,
        "pays": sorted({(o["pays"], o["pays_nom"]) for o in avec if o.get("pays")}, key=lambda x: x[1]),
        "langues": sorted({o["langue"] for o in avec if o.get("langue")}),
        "niveaux": [n for n in SP.NIVEAUX if any(o.get("niveau") == n for o in avec)],
        "durees": [[n, a, b] for n, a, b in DUREES if any(_classe_duree(o.get("duree_jours")) == n for o in avec)],
    }
    f = UI["fr"]
    seo_titre = "Comparatif des stages de voile : prix au jour, durée, langue | Sailing More"
    seo_desc = (f"{len(avec)} stages de voile à prix publié, classés par prix au jour. Filtrez par pays, "
                "langue, niveau et durée ; prix dans la devise de l'école.")
    jld = __import__("jsonld")
    sel = lambda i, k: (f"<label><span data-t=\"{k}\">{H.escape(f[k])}</span><select id=\"{i}\"></select></label>")
    return ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{H.escape(seo_titre)}</title>"
            f"<link rel=\"canonical\" href=\"https://sailingmore.fr/{PAGE}\">"
            f"{jld.page_simple(PAGE, f['titre'])}"
            f"<meta name=\"description\" content=\"{H.escape(seo_desc, quote=True)}\">"
            f"{jld.social(PAGE, seo_titre, seo_desc)}"
            f"<style>{site_blocks.ENTETE_CSS}{CSS}</style></head><body>\n"
            f"{site_blocks.entete_site(PAGE, site_blocks.LANGUES)}\n<main class=\"page\">"
            f"<a class=\"retour\" href=\"stages.html\" data-t=\"retour\">{H.escape(f['retour'])}</a>"
            f"<h1 data-t=\"titre\">{H.escape(f['titre'])}</h1>"
            f"<p class=\"chapo\" data-t=\"chapo\">{H.escape(f['chapo'])}</p>"
            "<section class=\"filtres\">"
            + sel("f-pays", "pays") + sel("f-langue", "langue") + sel("f-niveau", "niveau")
            + sel("f-duree", "duree") + sel("f-tri", "tri") +
            "</section>"
            "<p class=\"compte\" id=\"compte\" role=\"status\" aria-live=\"polite\">"
            f"{len(avec)} offres</p>"
            "<div class=\"tab\"><table><thead><tr>"
            + "".join(f"<th data-t=\"{k}\">{H.escape(f[k])}</th>"
                      for k in ("col_stage", "col_prix", "col_jour", "col_duree", "col_niv", "col_lang", "col_pays"))
            + "<th></th></tr></thead><tbody id=\"tb\">" + "".join(trs) + "</tbody></table></div>"
            "<p class=\"aucune\" id=\"aucune\" hidden data-t=\"aucune\">" + H.escape(f["aucune"]) + "</p>"
            f"<p class=\"sans-prix\" data-t=\"sans_prix\" data-sub=\"{sans}|\">{H.escape(f['sans_prix'].format(n=sans))}</p>"
            f"<p class=\"pied\"><a href=\"stages.html\" data-t=\"stages\">{H.escape(f['stages'])}</a></p>"
            f"<p class=\"pied\" data-t=\"pied\" data-sub=\"|{H.escape(taux_date)}\">{H.escape(f['pied'].format(d=taux_date))}</p>"
            "</main><script id=\"donnees\" type=\"application/json\">"
            + json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
            + "</script><script>" + JS + "</script></body></html>")


def LANG(o: dict) -> str:
    return SP.LANGUES.get(o.get("langue") or "", o.get("langue") or "—")


def ecrire_page(dossier: Path) -> int:
    dossier.mkdir(parents=True, exist_ok=True)
    avec, _, d = lignes()
    (dossier / PAGE).write_text(construire(d), encoding="utf-8")
    return len(avec)


if __name__ == "__main__":
    site = SP.ICI / "projets/sailingmore/site"
    print(ecrire_page(site), "offre(s) comparées")
