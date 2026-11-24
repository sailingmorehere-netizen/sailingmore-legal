#!/usr/bin/env python3
"""Page `equivalences.html` : à quel niveau d'un autre référentiel mène un stage (RYA, ICC, FFVoile, DSV…).

Sprint 1 (23/11/2026) : **la structure seulement.** Aucune correspondance n'est écrite ici ni dans les
données : le contenu sera rempli depuis les documents officiels, ligne par ligne, et validé par Nicolas.

Entrée  : `projets/sailingmore/equivalences.json` — créé vide (squelette) s'il n'existe pas, jamais
          écrasé ensuite. Une entrée par couple de référentiels :
              de, vers               référentiel de départ / d'arrivée (« RYA », « FFVoile »…)
              niveau_source          le niveau dans `de` (« Day Skipper »…)
              niveau_cible           le niveau équivalent dans `vers`
              prerequis              ce qu'il faut en plus (texte, ou {"fr": …, "en": …, …})
              passerelle             la démarche pour obtenir le niveau cible (même forme)
              source_url             le document officiel qui l'établit (https://…)
              valide_par_nicolas     faux par défaut
Sorties : `site/equivalences.html` (publiée) et `site/equivalences-apercu.html` (non publiée, noindex),
          l'entrée de la page dans `site/sitemap.xml`.

Les lignes non validées : **absentes de la page publique**, visibles seulement dans l'aperçu avec la
mention « à vérifier ». Raison : une équivalence sert à décider d'un stage payé ; affichée même avec
un avertissement, une ligne fausse serait lue comme une réponse — et c'est la crédibilité du site sur
son différenciateur. L'aperçu sert à relire avant de cocher `valide_par_nicolas`.
Une ligne validée **sans** `source_url` en https n'est pas publiée non plus : pas de fédération citée
sans source.

    python3 scripts/equivalences_page.py --verifier   # contrôle les données, n'écrit rien
    python3 scripts/equivalences_page.py --ecrire     # écrit les deux pages et le sitemap
"""
from __future__ import annotations

import html as H
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", "/opt/data"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

DONNEES = ICI / "projets/sailingmore/equivalences.json"
SITE = ICI / "projets/sailingmore/site"
URL = "https://sailingmore.fr"
PAGE = "equivalences.html"
APERCU = "equivalences-apercu.html"
CHAMPS = ("de", "vers", "niveau_source", "niveau_cible", "prerequis", "passerelle", "source_url",
          "valide_par_nicolas")
from site_blocks import LANGUES as _LANGUES_SITE  # noqa: E402  (une seule liste pour toutes les pages)
LANGUES = tuple(_LANGUES_SITE)

SQUELETTE = {
    "maj": "",
    "note": ("Une entrée par couple de référentiels. Ne rien écrire de mémoire : chaque ligne vient d'un "
             "document officiel (source_url) et n'est publiée qu'avec valide_par_nicolas = true. "
             "prerequis et passerelle : texte simple, ou {\"fr\": ..., \"en\": ...} pour traduire."),
    "modele": {"de": "", "vers": "", "niveau_source": "", "niveau_cible": "", "prerequis": "",
               "passerelle": "", "source_url": "", "valide_par_nicolas": False},
    "correspondances": [],
}

UI = {
    "fr": {"titre": "Équivalences des diplômes de voile",
           "chapo": "Ce stage RYA en Grèce mène à quel niveau FFVoile, SKS ou ICC ? Chaque correspondance de cette page vient d'un document officiel, cité en lien, et a été relue par un moniteur avant d'être publiée.",
           "de": "Référentiel de départ", "vers": "Référentiel visé", "tous": "Tous",
           "niveau_source": "Niveau détenu", "niveau_cible": "Niveau équivalent",
           "prerequis": "Prérequis", "passerelle": "Démarche", "source": "Source", "voir_source": "document officiel",
           "vide": "Les correspondances sont en cours de vérification sur les documents officiels. Elles apparaîtront ici une par une, chacune avec sa source.",
           "aucune": "Aucune correspondance publiée pour ce couple de référentiels.",
           "a_verifier": "à vérifier", "compte": "{n} correspondance(s) publiée(s)",
           "pied": "Une équivalence vous semble fausse, ou un document officiel a changé ? Écrivez-nous : la ligne est retirée le temps de la vérifier.",
           "stages": "Voir les stages de voile →"},
    "en": {"titre": "Sailing qualification equivalences",
           "chapo": "Which FFVoile, SKS or ICC level does this RYA course in Greece lead to? Every equivalence on this page comes from an official document, linked, and has been checked by an instructor before publication.",
           "de": "From scheme", "vers": "To scheme", "tous": "All",
           "niveau_source": "Level held", "niveau_cible": "Equivalent level",
           "prerequis": "Prerequisites", "passerelle": "How to get it", "source": "Source", "voir_source": "official document",
           "vide": "The equivalences are being checked against the official documents. They will appear here one by one, each with its source.",
           "aucune": "No equivalence published for this pair of schemes.",
           "a_verifier": "to be checked", "compte": "{n} equivalence(s) published",
           "pied": "An equivalence looks wrong, or an official document has changed? Tell us: the line is withdrawn while we check it.",
           "stages": "See sailing courses →"},
    "it": {"titre": "Equivalenze dei brevetti di vela",
           "chapo": "Questo corso RYA in Grecia a quale livello FFVoile, SKS o ICC porta? Ogni equivalenza di questa pagina viene da un documento ufficiale, citato con il link, ed è stata riletta da un istruttore prima della pubblicazione.",
           "de": "Sistema di partenza", "vers": "Sistema di arrivo", "tous": "Tutti",
           "niveau_source": "Livello posseduto", "niveau_cible": "Livello equivalente",
           "prerequis": "Prerequisiti", "passerelle": "Procedura", "source": "Fonte", "voir_source": "documento ufficiale",
           "vide": "Le equivalenze sono in corso di verifica sui documenti ufficiali. Appariranno qui una alla volta, ciascuna con la sua fonte.",
           "aucune": "Nessuna equivalenza pubblicata per questa coppia di sistemi.",
           "a_verifier": "da verificare", "compte": "{n} equivalenza/e pubblicata/e",
           "pied": "Un'equivalenza ti sembra sbagliata, o un documento ufficiale è cambiato? Scrivici: la riga viene ritirata il tempo di verificarla.",
           "stages": "Vedi i corsi di vela →"},
    "es": {"titre": "Equivalencias de titulaciones de vela",
           "chapo": "¿A qué nivel FFVoile, SKS o ICC lleva este curso RYA en Grecia? Cada equivalencia de esta página procede de un documento oficial, enlazado, y ha sido revisada por un instructor antes de publicarse.",
           "de": "Sistema de origen", "vers": "Sistema de destino", "tous": "Todos",
           "niveau_source": "Nivel que tienes", "niveau_cible": "Nivel equivalente",
           "prerequis": "Requisitos previos", "passerelle": "Cómo obtenerlo", "source": "Fuente", "voir_source": "documento oficial",
           "vide": "Las equivalencias se están comprobando en los documentos oficiales. Aparecerán aquí una a una, cada una con su fuente.",
           "aucune": "No hay equivalencias publicadas para este par de sistemas.",
           "a_verifier": "por verificar", "compte": "{n} equivalencia(s) publicada(s)",
           "pied": "¿Una equivalencia parece errónea, o ha cambiado un documento oficial? Escríbenos: la línea se retira mientras se comprueba.",
           "stages": "Ver los cursos de vela →"},
    "pt": {"titre": "Equivalências de cartas de vela",
           "chapo": "A que nível FFVoile, SKS ou ICC leva este curso RYA na Grécia? Cada equivalência desta página vem de um documento oficial, com ligação, e foi revista por um instrutor antes de ser publicada.",
           "de": "Sistema de origem", "vers": "Sistema de destino", "tous": "Todos",
           "niveau_source": "Nível que tem", "niveau_cible": "Nível equivalente",
           "prerequis": "Pré-requisitos", "passerelle": "Como obter", "source": "Fonte", "voir_source": "documento oficial",
           "vide": "As equivalências estão a ser verificadas nos documentos oficiais. Vão aparecer aqui uma a uma, cada uma com a sua fonte.",
           "aucune": "Nenhuma equivalência publicada para este par de sistemas.",
           "a_verifier": "por verificar", "compte": "{n} equivalência(s) publicada(s)",
           "pied": "Uma equivalência parece errada, ou um documento oficial mudou? Escreva-nos: a linha é retirada enquanto a verificamos.",
           "stages": "Ver os cursos de vela →"},
    "de": {"titre": "Gleichwertigkeit von Segelscheinen",
           "chapo": "Zu welchem FFVoile-, SKS- oder ICC-Niveau führt dieser RYA-Kurs in Griechenland? Jede Gleichwertigkeit auf dieser Seite stammt aus einem verlinkten amtlichen Dokument und wurde vor der Veröffentlichung von einem Ausbilder geprüft.",
           "de": "Ausgangssystem", "vers": "Zielsystem", "tous": "Alle",
           "niveau_source": "Vorhandenes Niveau", "niveau_cible": "Gleichwertiges Niveau",
           "prerequis": "Voraussetzungen", "passerelle": "Weg dorthin", "source": "Quelle", "voir_source": "amtliches Dokument",
           "vide": "Die Gleichwertigkeiten werden anhand der amtlichen Dokumente geprüft. Sie erscheinen hier nach und nach, jede mit ihrer Quelle.",
           "aucune": "Für dieses Systempaar ist keine Gleichwertigkeit veröffentlicht.",
           "a_verifier": "zu prüfen", "compte": "{n} Gleichwertigkeit(en) veröffentlicht",
           "pied": "Eine Gleichwertigkeit scheint falsch, oder ein amtliches Dokument hat sich geändert? Schreiben Sie uns: die Zeile wird bis zur Prüfung entfernt.",
           "stages": "Segelkurse ansehen →"},
}

CSS = """
:root{--fond:#0a1a2b;--carte:#0f2438;--trait:#1d3549;--encre:#e8eef5;--doux:#9db2c7;--rouge:#e23a3e}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--encre);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:inherit}
.page{max-width:60rem;margin:0 auto;padding:2rem 1rem 5rem}
h1{font-size:clamp(1.5rem,5vw,2.3rem);margin:.2rem 0 .6rem;letter-spacing:-.02em;line-height:1.15}
.chapo{color:var(--doux);margin:0 0 1.4rem;max-width:46rem}
.filtres{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin:0 0 1rem}
.filtres label{display:flex;flex-direction:column;gap:.25rem;font-size:.8rem;color:var(--doux)}
.filtres select{font:inherit;font-size:1rem;min-height:44px;padding:.4rem .5rem;background:var(--carte);color:var(--encre);
  border:1px solid var(--trait);border-radius:0}
.compte{font-size:.85rem;color:var(--doux);margin:.2rem 0 .8rem}
.vide{background:var(--carte);border-left:3px solid var(--rouge);padding:1rem 1.1rem;margin:1rem 0}
table.eq{width:100%;border-collapse:collapse;font-size:.95rem}
table.eq th{text-align:left;font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);
  border-bottom:1px solid var(--rouge);padding:.5rem .5rem}
table.eq td{border-bottom:1px solid var(--trait);padding:.6rem .5rem;vertical-align:top}
.ref{font-weight:700}
.niv{display:block;color:var(--doux);font-size:.9rem}
.badge{display:inline-block;margin-left:.4rem;padding:.05rem .4rem;font-size:.72rem;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;background:var(--rouge);color:#fff}
tr.non-valide td{opacity:.85}
.pied{color:var(--doux);font-size:.85rem;margin-top:2rem}
.lien-stages{display:inline-block;margin-top:1rem}
/* Téléphone : chaque correspondance devient une fiche, le libellé de colonne passe devant la valeur. */
@media (max-width:640px){
  .filtres{grid-template-columns:1fr}
  table.eq thead{display:none}
  table.eq,table.eq tbody,table.eq tr,table.eq td{display:block;width:100%}
  table.eq tr{background:var(--carte);border-left:3px solid var(--rouge);margin:0 0 .8rem;padding:.4rem .2rem}
  table.eq td{border:0;padding:.35rem .7rem}
  table.eq td::before{content:attr(data-l);display:block;font-size:.72rem;letter-spacing:.06em;
    text-transform:uppercase;color:var(--doux)}
}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById('eq-donnees').textContent),L='fr';
/* Une seule détection pour tout le site, faite dans le <head> (24/11/2026). */
function choisir(){var v=(typeof window.smLangue==='function')?window.smLangue():'en';
  if(v==='bzh')v='fr';return D.ui[v]?v:'en'}
function t(k){return (D.ui[L]||D.ui.en)[k]||D.ui.fr[k]||k}
function tx(v){if(v&&typeof v==='object'){return v[L]||v.en||v.fr||''}return v||''}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function options(id,vals){var s=document.getElementById(id),cur=s.value;
  s.innerHTML='<option value="">'+esc(t('tous'))+'</option>'+vals.map(function(v){return '<option>'+esc(v)+'</option>'}).join('');
  s.value=vals.indexOf(cur)>=0?cur:''}
function rendre(){
  document.documentElement.lang=L;
  ['titre','chapo','pied','stages'].forEach(function(k){var e=document.querySelector('[data-t="'+k+'"]');if(e)e.textContent=t(k)});
  document.querySelectorAll('[data-tl]').forEach(function(e){e.textContent=t(e.getAttribute('data-tl'))});
  options('f-de',D.de);options('f-vers',D.vers);
  var de=document.getElementById('f-de').value,vers=document.getElementById('f-vers').value;
  var lignes=D.lignes.filter(function(x){return (!de||x.de===de)&&(!vers||x.vers===vers)});
  var corps=document.getElementById('eq-corps'),vide=document.getElementById('eq-vide'),tab=document.getElementById('eq-table');
  document.getElementById('eq-compte').textContent=t('compte').replace('{n}',lignes.length);
  if(!D.lignes.length){tab.hidden=true;vide.hidden=false;vide.textContent=t('vide');return}
  if(!lignes.length){tab.hidden=true;vide.hidden=false;vide.textContent=t('aucune');return}
  tab.hidden=false;vide.hidden=true;
  corps.innerHTML=lignes.map(function(x){
    var b=x.valide?'':'<span class="badge">'+esc(t('a_verifier'))+'</span>';
    var src=x.source_url?'<a href="'+esc(x.source_url)+'" rel="noopener" target="_blank">'+esc(t('voir_source'))+'</a>':'—';
    return '<tr class="'+(x.valide?'':'non-valide')+'">'
      +'<td data-l="'+esc(t('niveau_source'))+'"><span class="ref">'+esc(x.de)+'</span>'+b+'<span class="niv">'+esc(tx(x.niveau_source))+'</span></td>'
      +'<td data-l="'+esc(t('niveau_cible'))+'"><span class="ref">'+esc(x.vers)+'</span><span class="niv">'+esc(tx(x.niveau_cible))+'</span></td>'
      +'<td data-l="'+esc(t('prerequis'))+'">'+esc(tx(x.prerequis)||'—')+'</td>'
      +'<td data-l="'+esc(t('passerelle'))+'">'+esc(tx(x.passerelle)||'—')+'</td>'
      +'<td data-l="'+esc(t('source'))+'">'+src+'</td></tr>'}).join('')}
L=choisir();rendre();
['f-de','f-vers'].forEach(function(i){document.getElementById(i).addEventListener('change',rendre)});
/* La barre du site pose ses boutons de langue (#langues button[data-lang]) après coup : on écoute au niveau du document. */
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('#langues button[data-lang]');if(!b)return;
  var v=b.getAttribute('data-lang');try{localStorage.setItem('sm-langue',v)}catch(_){}
  document.querySelectorAll('#langues button[data-lang]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
  L=choisir();rendre()});
})();
"""


# --------------------------------------------------------------------------- données

def charger() -> dict:
    """Les données ; le squelette est créé s'il n'existe pas encore (jamais écrasé ensuite)."""
    if not DONNEES.exists():
        DONNEES.parent.mkdir(parents=True, exist_ok=True)
        DONNEES.write_text(json.dumps(SQUELETTE, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return json.loads(DONNEES.read_text(encoding="utf-8"))


def _texte(v) -> bool:
    return isinstance(v, str) or (isinstance(v, dict) and all(isinstance(x, str) for x in v.values()))


def verifier(d: dict) -> list[str]:
    """Problèmes de forme, ligne par ligne. Ne juge pas le fond : c'est le travail de la validation."""
    pb = []
    lignes = d.get("correspondances")
    if not isinstance(lignes, list):
        return ["`correspondances` doit être une liste"]
    for i, x in enumerate(lignes, 1):
        if not isinstance(x, dict):
            pb.append(f"ligne {i} : pas un objet")
            continue
        manque = [c for c in CHAMPS if c not in x]
        if manque:
            pb.append(f"ligne {i} : champ(s) absent(s) {', '.join(manque)}")
        for c in ("de", "vers", "source_url"):
            if c in x and not isinstance(x[c], str):
                pb.append(f"ligne {i} : `{c}` doit être un texte")
        for c in ("niveau_source", "niveau_cible", "prerequis", "passerelle"):
            if c in x and not _texte(x[c]):
                pb.append(f"ligne {i} : `{c}` doit être un texte ou {{langue: texte}}")
        if "valide_par_nicolas" in x and not isinstance(x["valide_par_nicolas"], bool):
            pb.append(f"ligne {i} : `valide_par_nicolas` doit être true ou false")
        if x.get("de") and x.get("de") == x.get("vers"):
            pb.append(f"ligne {i} : `de` et `vers` identiques")
        if x.get("valide_par_nicolas") is True and not _source_ok(x):
            pb.append(f"ligne {i} : validée mais sans source https — non publiée")
    return pb


def _source_ok(x: dict) -> bool:
    return isinstance(x.get("source_url"), str) and x["source_url"].startswith("https://")


def publiable(x: dict) -> bool:
    return isinstance(x, dict) and x.get("valide_par_nicolas") is True and _source_ok(x) \
        and bool(x.get("de")) and bool(x.get("vers"))


def lignes_page(d: dict, apercu: bool) -> list[dict]:
    out = []
    for x in d.get("correspondances") or []:
        if not isinstance(x, dict):
            continue
        if not apercu and not publiable(x):
            continue
        out.append({"de": x.get("de", ""), "vers": x.get("vers", ""),
                    "niveau_source": x.get("niveau_source", ""), "niveau_cible": x.get("niveau_cible", ""),
                    "prerequis": x.get("prerequis", ""), "passerelle": x.get("passerelle", ""),
                    "source_url": x.get("source_url", "") if _source_ok(x) else "",
                    "valide": publiable(x)})
    out.sort(key=lambda x: (x["de"].lower(), x["vers"].lower()))
    return out


# --------------------------------------------------------------------------- page

def construire(d: dict, apercu: bool = False) -> str:
    import jsonld
    lignes = lignes_page(d, apercu)
    donnees = {"ui": UI, "lignes": lignes,
               "de": sorted({x["de"] for x in lignes if x["de"]}),
               "vers": sorted({x["vers"] for x in lignes if x["vers"]})}
    fr = UI["fr"]
    brut = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tete = ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{H.escape(fr['titre'])} — Sailing More</title>"
            f"<meta name=\"description\" content=\"{H.escape(fr['chapo'], quote=True)}\">")
    if apercu:
        tete += "<meta name=\"robots\" content=\"noindex,nofollow\">"
    else:
        tete += (f"<link rel=\"canonical\" href=\"{URL}/{PAGE}\">"
                 + jsonld.page_simple(PAGE, fr["titre"])
                 + jsonld.social(PAGE, f"{fr['titre']} — Sailing More", fr["chapo"]))
    entetes = "".join(f'<th data-tl="{k}">{H.escape(fr[k])}</th>'
                      for k in ("niveau_source", "niveau_cible", "prerequis", "passerelle", "source"))
    corps = (f"<style>{CSS}</style></head><body><main class=\"page\">"
             + ("<p class=\"vide\">Aperçu non publié : toutes les lignes, y compris celles à vérifier.</p>"
                if apercu else "")
             + f"<h1 data-t=\"titre\">{H.escape(fr['titre'])}</h1>"
             f"<p class=\"chapo\" data-t=\"chapo\">{H.escape(fr['chapo'])}</p>"
             "<div class=\"filtres\">"
             f"<label><span data-tl=\"de\">{H.escape(fr['de'])}</span><select id=\"f-de\"></select></label>"
             f"<label><span data-tl=\"vers\">{H.escape(fr['vers'])}</span><select id=\"f-vers\"></select></label>"
             "</div>"
             "<p class=\"compte\" id=\"eq-compte\" aria-live=\"polite\"></p>"
             f"<p class=\"vide\" id=\"eq-vide\" hidden>{H.escape(fr['vide'])}</p>"
             f"<table class=\"eq\" id=\"eq-table\" hidden><thead><tr>{entetes}</tr></thead>"
             "<tbody id=\"eq-corps\"></tbody></table>"
             # Sans JavaScript, le message d'attente reste lisible.
             f"<noscript><p class=\"vide\">{H.escape(fr['vide'])}</p></noscript>"
             f"<p><a class=\"lien-stages\" href=\"stages.html\" data-t=\"stages\">{H.escape(fr['stages'])}</a></p>"
             f"<p class=\"pied\" data-t=\"pied\">{H.escape(fr['pied'])}</p>"
             "</main>"
             f"<script type=\"application/json\" id=\"eq-donnees\">{brut}</script>"
             f"<script>{JS}</script></body></html>\n")
    return tete + corps


def maj_sitemap(dossier: Path) -> bool:
    """Ajoute (ou rafraîchit) l'entrée de la page dans sitemap.xml. Idempotent. L'aperçu n'y est jamais."""
    f = dossier / "sitemap.xml"
    if not f.exists():
        return False
    x = f.read_text(encoding="utf-8")
    x = re.sub(r"\s*<url><loc>https://sailingmore\.fr/equivalences\.html</loc>.*?</url>", "", x, flags=re.S)
    ligne = (f"\n  <url><loc>{URL}/{PAGE}</loc><lastmod>{date.today().isoformat()}</lastmod>"
             "<changefreq>monthly</changefreq><priority>0.7</priority></url>")
    x = x.replace("</urlset>", ligne + "\n</urlset>", 1)
    f.write_text(x, encoding="utf-8")
    return True


def ecrire_page(dossier: Path = SITE) -> str:
    """Écrit la page publique, l'aperçu et l'entrée du sitemap — appelé par `accueil_site.sortir_le_site`."""
    d = charger()
    pb = verifier(d)
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / PAGE).write_text(construire(d), encoding="utf-8")
    (dossier / APERCU).write_text(construire(d, apercu=True), encoding="utf-8")
    sm = maj_sitemap(dossier)
    toutes = [x for x in d.get("correspondances") or [] if isinstance(x, dict)]
    pub = sum(1 for x in toutes if publiable(x))
    return (f"{pub} correspondance(s) publiée(s) sur {len(toutes)} · {len(toutes) - pub} à vérifier"
            f" · {len(pb)} problème(s) de forme · sitemap {'à jour' if sm else 'absent'}")


def main() -> int:
    if "--verifier" in sys.argv:
        d = charger()
        pb = verifier(d)
        print("\n".join(pb) if pb else "données conformes")
        return 1 if pb else 0
    if "--ecrire" in sys.argv:
        print(f"{PAGE} : {ecrire_page()}")
        return 0
    print("Rien à faire : --verifier (lecture seule) ou --ecrire.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
