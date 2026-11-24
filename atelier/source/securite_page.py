#!/usr/bin/env python3
"""Page `securite-obligatoire.html` : matériel de sécurité exigé selon pavillon, distance d'un abri, équipage.

Tâche 30 (24/11/2026). **Aucune exigence n'est écrite ici ni de mémoire** : les règles viennent de
`projets/sailingmore/securite-obligatoire.json` (clé `regles`), chacune avec source_url (https), source_article,
source_date, et ne sont publiées qu'avec valide_par_nicolas = true. Les règles non validées n'apparaissent que
dans `securite-obligatoire-apercu.html` (noindex). Un lien d'affiliation n'est rendu que si `prix_verifie` est
une date AAAA-MM-JJ et `lien_affilie` un https.
Réutilise le CSS et les aides de equivalences_page.py (une seule source).

    python3 scripts/securite_page.py --verifier
    python3 scripts/securite_page.py --ecrire
Racine : variable SAILINGMORE_RACINE (défaut /opt/data).
"""
from __future__ import annotations
import html as H, json, os, re, sys
from datetime import date
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE") or Path(__file__).resolve().parents[1])
sys.path.insert(0, str(Path(__file__).resolve().parent))
import equivalences_page as EQ  # noqa: E402

DONNEES = ICI / "projets/sailingmore/securite-obligatoire.json"
SITE = ICI / "projets/sailingmore/site"
URL, PAGE, APERCU = "https://sailingmore.fr", "securite-obligatoire.html", "securite-obligatoire-apercu.html"
PAVILLONS = ("FR", "GB", "US", "CH", "DE")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHAMPS = ("pavillon", "zone", "distance_min_milles", "distance_max_milles", "equipiers_min", "equipiers_max",
          "materiel", "quantite", "quantite_par_equipier", "source_url", "source_article", "source_date",
          "prix_verifie", "lien_affilie", "valide_par_nicolas")

UI = {
 "fr": {"titre": "Équipement de sécurité obligatoire par pavillon et par zone",
        "chapo": "Indiquez le pavillon du bateau, la distance à un abri et le nombre d'équipiers : la liste du matériel exigé s'affiche, avec le texte officiel et sa date. Aucune règle n'est publiée sans source.",
        "pavillon": "Pavillon", "distance": "Distance d'un abri (milles)", "equipiers": "Équipiers",
        "materiel": "Matériel exigé", "quantite": "Quantité", "source": "Source", "date": "texte du",
        "prix": "prix vérifié le", "acheter": "voir chez le revendeur", "pub": "lien d'affiliation",
        "vide": "Les règles sont en cours de vérification sur les textes officiels. Elles apparaîtront ici une par une, chacune avec sa source et sa date.",
        "aucune": "Aucune règle publiée pour cette combinaison. Cela ne veut pas dire qu'aucun matériel n'est exigé : consultez l'autorité du pavillon.",
        "avert": "Information indicative : seul le texte officiel fait foi, et il peut avoir changé depuis la date indiquée.",
        "par_equ": "par équipier", "stages": "Voir les stages de voile →"},
 "en": {"titre": "Mandatory safety equipment by flag and by zone",
        "chapo": "Enter the boat's flag, the distance from shelter and the crew size: the required equipment is listed with the official text and its date. No rule is published without a source.",
        "pavillon": "Flag", "distance": "Distance from shelter (nm)", "equipiers": "Crew",
        "materiel": "Required equipment", "quantite": "Quantity", "source": "Source", "date": "text dated",
        "prix": "price checked on", "acheter": "see at the chandler", "pub": "affiliate link",
        "vide": "The rules are being checked against the official texts. They will appear here one by one, each with its source and date.",
        "aucune": "No rule published for this combination. That does not mean no equipment is required: check with the flag authority.",
        "avert": "Indicative only: the official text prevails and may have changed since the date shown.",
        "par_equ": "per crew member", "stages": "See sailing courses →"},
 "de": {"titre": "Vorgeschriebene Sicherheitsausrüstung nach Flagge und Fahrtgebiet",
        "chapo": "Geben Sie Flagge, Entfernung zum Schutzhafen und Crewgröße ein: Die vorgeschriebene Ausrüstung erscheint mit amtlichem Text und Datum. Keine Regel ohne Quelle.",
        "pavillon": "Flagge", "distance": "Entfernung zum Schutz (sm)", "equipiers": "Crew",
        "materiel": "Vorgeschriebene Ausrüstung", "quantite": "Menge", "source": "Quelle", "date": "Text vom",
        "prix": "Preis geprüft am", "acheter": "beim Händler ansehen", "pub": "Affiliate-Link",
        "vide": "Die Vorschriften werden anhand der amtlichen Texte geprüft. Sie erscheinen hier nach und nach, jede mit Quelle und Datum.",
        "aucune": "Für diese Kombination ist keine Regel veröffentlicht. Das heißt nicht, dass nichts vorgeschrieben ist: Fragen Sie die Behörde der Flagge.",
        "avert": "Unverbindlich: maßgeblich ist der amtliche Text, der sich seit dem genannten Datum geändert haben kann.",
        "par_equ": "pro Crewmitglied", "stages": "Segelkurse ansehen →"},
 "it": {"titre": "Dotazioni di sicurezza obbligatorie per bandiera e zona",
        "chapo": "Indica bandiera, distanza da un riparo e numero di persone a bordo: appare l'elenco del materiale richiesto, con il testo ufficiale e la sua data. Nessuna regola senza fonte.",
        "pavillon": "Bandiera", "distance": "Distanza da un riparo (miglia)", "equipiers": "Equipaggio",
        "materiel": "Dotazione richiesta", "quantite": "Quantità", "source": "Fonte", "date": "testo del",
        "prix": "prezzo verificato il", "acheter": "vedi dal rivenditore", "pub": "link di affiliazione",
        "vide": "Le regole sono in corso di verifica sui testi ufficiali. Appariranno qui una alla volta, ciascuna con fonte e data.",
        "aucune": "Nessuna regola pubblicata per questa combinazione. Non significa che non serva nulla: consulta l'autorità della bandiera.",
        "avert": "Indicativo: fa fede il testo ufficiale, che può essere cambiato dopo la data indicata.",
        "par_equ": "per persona", "stages": "Vedi i corsi di vela →"},
 "es": {"titre": "Equipo de seguridad obligatorio por bandera y zona",
        "chapo": "Indique la bandera, la distancia a un abrigo y el número de tripulantes: se muestra el material exigido con el texto oficial y su fecha. Ninguna norma sin fuente.",
        "pavillon": "Bandera", "distance": "Distancia a un abrigo (millas)", "equipiers": "Tripulantes",
        "materiel": "Material exigido", "quantite": "Cantidad", "source": "Fuente", "date": "texto del",
        "prix": "precio comprobado el", "acheter": "ver en la tienda", "pub": "enlace de afiliación",
        "vide": "Las normas se están comprobando en los textos oficiales. Aparecerán aquí una a una, cada una con su fuente y fecha.",
        "aucune": "No hay normas publicadas para esta combinación. No significa que no se exija nada: consulte a la autoridad de la bandera.",
        "avert": "Orientativo: prevalece el texto oficial, que pudo cambiar desde la fecha indicada.",
        "par_equ": "por tripulante", "stages": "Ver los cursos de vela →"},
 "pt": {"titre": "Equipamento de segurança obrigatório por bandeira e zona",
        "chapo": "Indique a bandeira, a distância a um abrigo e o número de tripulantes: aparece o material exigido, com o texto oficial e a sua data. Nenhuma regra sem fonte.",
        "pavillon": "Bandeira", "distance": "Distância a um abrigo (milhas)", "equipiers": "Tripulantes",
        "materiel": "Material exigido", "quantite": "Quantidade", "source": "Fonte", "date": "texto de",
        "prix": "preço verificado em", "acheter": "ver no revendedor", "pub": "ligação de afiliação",
        "vide": "As regras estão a ser verificadas nos textos oficiais. Vão aparecer aqui uma a uma, cada uma com fonte e data.",
        "aucune": "Nenhuma regra publicada para esta combinação. Não significa que nada seja exigido: consulte a autoridade da bandeira.",
        "avert": "Indicativo: vale o texto oficial, que pode ter mudado desde a data indicada.",
        "par_equ": "por tripulante", "stages": "Ver os cursos de vela →"},
}

JS = r"""
(function(){
var D=JSON.parse(document.getElementById('se-donnees').textContent),L='fr';
function choisir(){var v='auto';try{v=localStorage.getItem('sm-langue')||'auto'}catch(e){}
  if(v==='auto'){v=(navigator.language||'fr').slice(0,2);if(v==='br')v='fr'}return D.ui[v]?v:'en'}
function t(k){return (D.ui[L]||D.ui.en)[k]||D.ui.fr[k]||k}
function tx(v){if(v&&typeof v==='object'){return v[L]||v.en||v.fr||''}return v||''}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function ok(r,p,d,n){
  if(r.pavillon!==p)return false;
  if(r.distance_min_milles!=null&&d<r.distance_min_milles)return false;
  if(r.distance_max_milles!=null&&d>r.distance_max_milles)return false;
  if(r.equipiers_min!=null&&n<r.equipiers_min)return false;
  if(r.equipiers_max!=null&&n>r.equipiers_max)return false;return true}
function rendre(){
  document.documentElement.lang=L;
  document.querySelectorAll('[data-tl]').forEach(function(e){e.textContent=t(e.getAttribute('data-tl'))});
  var p=document.getElementById('f-pav').value,d=parseFloat(document.getElementById('f-dist').value),
      n=parseInt(document.getElementById('f-equ').value,10);
  var tab=document.getElementById('se-table'),vide=document.getElementById('se-vide'),corps=document.getElementById('se-corps');
  if(!D.regles.length){tab.hidden=true;vide.hidden=false;vide.textContent=t('vide');return}
  if(!(d>=0)||!(n>=1)){tab.hidden=true;vide.hidden=true;return}
  var rs=D.regles.filter(function(r){return ok(r,p,d,n)});
  if(!rs.length){tab.hidden=true;vide.hidden=false;vide.textContent=t('aucune');return}
  tab.hidden=false;vide.hidden=true;
  corps.innerHTML=rs.map(function(r){
    var q=tx(r.quantite)||'';
    if(r.quantite_par_equipier)q=(q?q+' ':'')+'('+t('par_equ')+' : '+n+')';
    var src='<a href="'+esc(r.source_url)+'" rel="noopener" target="_blank">'+esc(r.source_article||r.source_url)+'</a>'
      +'<span class="niv">'+esc(t('date'))+' '+esc(r.source_date)+'</span>';
    var ach=(r.lien_affilie&&r.prix_verifie)?'<span class="niv"><a href="'+esc(r.lien_affilie)+'" rel="sponsored nofollow noopener" target="_blank">'
      +esc(t('acheter'))+'</a> ('+esc(t('pub'))+' · '+esc(t('prix'))+' '+esc(r.prix_verifie)+')</span>':'';
    return '<tr class="'+(r.valide?'':'non-valide')+'"><td data-l="'+esc(t('materiel'))+'"><span class="ref">'+esc(tx(r.materiel))+'</span>'
      +(r.valide?'':'<span class="badge">?</span>')+ach+'</td><td data-l="'+esc(t('quantite'))+'">'+esc(q||'—')
      +'</td><td data-l="'+esc(t('source'))+'">'+src+'</td></tr>'}).join('')}
L=choisir();rendre();
['f-pav','f-dist','f-equ'].forEach(function(i){var e=document.getElementById(i);e.addEventListener('change',rendre);e.addEventListener('input',rendre)});
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('#langues button[data-lang]');if(!b)return;
  var v=b.getAttribute('data-lang');try{localStorage.setItem('sm-langue',v)}catch(_){}
  document.querySelectorAll('#langues button[data-lang]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
  L=choisir();rendre()});
})();
"""
CSS_PLUS = ".filtres{grid-template-columns:1fr 1fr 1fr}.filtres input{font:inherit;font-size:1rem;min-height:44px;padding:.4rem .5rem;background:var(--carte);color:var(--encre);border:1px solid var(--trait);border-radius:0}@media (max-width:640px){.filtres{grid-template-columns:1fr}}"


def charger() -> dict:
    return json.loads(DONNEES.read_text(encoding="utf-8"))


def publiable(x: dict) -> bool:
    return (isinstance(x, dict) and x.get("valide_par_nicolas") is True and EQ._source_ok(x)
            and bool(DATE.match(str(x.get("source_date", "")))) and bool(x.get("source_article"))
            and bool(x.get("materiel")) and x.get("pavillon") in PAVILLONS)


def verifier(d: dict) -> list[str]:
    pb, rs = [], d.get("regles")
    if not isinstance(rs, list):
        return ["`regles` doit être une liste"]
    for i, x in enumerate(rs, 1):
        if not isinstance(x, dict):
            pb.append(f"règle {i} : pas un objet")
            continue
        m = [c for c in CHAMPS if c not in x]
        if m:
            pb.append(f"règle {i} : champ(s) absent(s) {', '.join(m)}")
        if x.get("pavillon") not in PAVILLONS:
            pb.append(f"règle {i} : pavillon hors {PAVILLONS}")
        for a, b in (("distance_min_milles", "distance_max_milles"), ("equipiers_min", "equipiers_max")):
            lo, hi = x.get(a), x.get(b)
            if lo is not None and hi is not None and lo > hi:
                pb.append(f"règle {i} : {a} > {b}")
        if x.get("source_date") and not DATE.match(str(x["source_date"])):
            pb.append(f"règle {i} : source_date doit être AAAA-MM-JJ")
        if x.get("lien_affilie") and not DATE.match(str(x.get("prix_verifie", ""))):
            pb.append(f"règle {i} : lien d'affiliation sans prix_verifie daté — non rendu")
        if x.get("valide_par_nicolas") is True and not publiable(x):
            pb.append(f"règle {i} : validée mais incomplète (source https, article, date, matériel) — non publiée")
    return pb


def lignes(d: dict, apercu: bool) -> list[dict]:
    out = []
    for x in d.get("regles") or []:
        if not isinstance(x, dict) or (not apercu and not publiable(x)):
            continue
        aff = x.get("lien_affilie") if (str(x.get("lien_affilie", "")).startswith("https://")
                                        and DATE.match(str(x.get("prix_verifie", "")))) else ""
        out.append({**{k: x.get(k) for k in CHAMPS if k not in ("lien_affilie", "prix_verifie", "valide_par_nicolas")},
                    "lien_affilie": aff, "prix_verifie": x.get("prix_verifie", "") if aff else "",
                    "valide": publiable(x)})
    return out


def construire(d: dict, apercu: bool = False) -> str:
    import jsonld
    fr = UI["fr"]
    brut = json.dumps({"ui": UI, "regles": lignes(d, apercu)}, ensure_ascii=False,
                      separators=(",", ":")).replace("</", "<\\/")
    tete = ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{H.escape(fr['titre'])} — Sailing More</title>"
            f"<meta name=\"description\" content=\"{H.escape(fr['chapo'], quote=True)}\">")
    tete += ("<meta name=\"robots\" content=\"noindex,nofollow\">" if apercu else
             f"<link rel=\"canonical\" href=\"{URL}/{PAGE}\">" + jsonld.page_simple(PAGE, fr["titre"])
             + jsonld.social(PAGE, f"{fr['titre']} — Sailing More", fr["chapo"]))
    opts = "".join(f"<option>{p}</option>" for p in PAVILLONS)
    ent = "".join(f'<th data-tl="{k}">{H.escape(fr[k])}</th>' for k in ("materiel", "quantite", "source"))
    corps = (f"<style>{EQ.CSS}{CSS_PLUS}</style></head><body><main class=\"page\">"
             + ("<p class=\"vide\">Aperçu non publié : toutes les règles, y compris celles à vérifier.</p>" if apercu else "")
             + f"<h1 data-tl=\"titre\">{H.escape(fr['titre'])}</h1><p class=\"chapo\" data-tl=\"chapo\">{H.escape(fr['chapo'])}</p>"
             "<div class=\"filtres\">"
             f"<label><span data-tl=\"pavillon\">{fr['pavillon']}</span><select id=\"f-pav\">{opts}</select></label>"
             f"<label><span data-tl=\"distance\">{H.escape(fr['distance'])}</span><input id=\"f-dist\" type=\"number\" min=\"0\" step=\"any\" inputmode=\"decimal\" value=\"6\"></label>"
             f"<label><span data-tl=\"equipiers\">{fr['equipiers']}</span><input id=\"f-equ\" type=\"number\" min=\"1\" step=\"1\" inputmode=\"numeric\" value=\"2\"></label>"
             "</div>"
             f"<p class=\"vide\" id=\"se-vide\" hidden>{H.escape(fr['vide'])}</p>"
             f"<table class=\"eq\" id=\"se-table\" hidden><thead><tr>{ent}</tr></thead><tbody id=\"se-corps\"></tbody></table>"
             f"<noscript><p class=\"vide\">{H.escape(fr['vide'])}</p></noscript>"
             f"<p class=\"pied\" data-tl=\"avert\">{H.escape(fr['avert'])}</p>"
             f"<p><a class=\"lien-stages\" href=\"stages.html\" data-tl=\"stages\">{H.escape(fr['stages'])}</a></p>"
             f"</main><script type=\"application/json\" id=\"se-donnees\">{brut}</script><script>{JS}</script></body></html>\n")
    return tete + corps


def maj_sitemap(dossier: Path) -> bool:
    f = dossier / "sitemap.xml"
    if not f.exists():
        return False
    x = re.sub(r"\s*<url><loc>https://sailingmore\.fr/securite-obligatoire\.html</loc>.*?</url>", "",
               f.read_text(encoding="utf-8"), flags=re.S)
    x = x.replace("</urlset>", f"\n  <url><loc>{URL}/{PAGE}</loc><lastmod>{date.today().isoformat()}</lastmod>"
                  "<changefreq>monthly</changefreq><priority>0.6</priority></url>\n</urlset>", 1)
    f.write_text(x, encoding="utf-8")
    return True


def ecrire_page(dossier: Path = SITE) -> str:
    d = charger()
    pb = verifier(d)
    nb = sum(1 for x in d.get("regles") or [] if publiable(x))
    # Aucune règle validée : la page publique n'est pas écrite (ni au sitemap) — une page vide ne s'indexe pas.
    (dossier / APERCU).write_text(construire(d, True), encoding="utf-8")
    if nb:
        (dossier / PAGE).write_text(construire(d), encoding="utf-8")
        maj_sitemap(dossier)
    return (f"{nb} règle(s) publiée(s) sur {len(d.get('regles') or [])} · {len(pb)} problème(s) · "
            f"page publique {'écrite' if nb else 'NON écrite (aucune règle validée)'}")


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        p = verifier(charger())
        print("\n".join(p) if p else "données conformes")
        raise SystemExit(1 if p else 0)
    if "--ecrire" in sys.argv:
        print(ecrire_page())
    else:
        print("--verifier ou --ecrire")
