# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Carte des épreuves — la brique commune aux pages `regates.html` et `stages.html`.

Une seule source : le CSS, le bloc HTML et le JS vivent ici, les deux pages les recopient (inline,
aucun fichier de plus à publier). La page fournit des points ; la carte fait le reste :

- fond : le tracé des côtes `scripts/carte_cotes.txt` s'il existe (voir `carte_cotes_gen.py`), sinon la
  grille de points `carte-monde.png` déjà publiée, plus un quadrillage tous les 30° ;
- pastilles de 12 px à l'écran mais zone de toucher de 44 px (rayon 22), quel que soit le zoom ;
- regroupement : des pastilles voisines (moins de 44 px à l'écran) deviennent un rond avec le nombre ;
  un toucher zoome, ou — si elles sont au même endroit — liste les épreuves ;
- clavier : seules les pastilles se tabulent (tabindex sur le <g>, jamais sur le fond) ;
- nom lisible sur chaque pastille : « nom, lieu, date longue » (date dans la langue de la page).

Un point : {lat, lon, ap (position approximative), champ (mis en avant), label (nom accessible),
html (ligne affichée au toucher)}.
"""
from __future__ import annotations

import json
from pathlib import Path

ICI = Path(__file__).resolve().parent
COTES = ICI / "carte_cotes.txt"

CSS = """
.carte-regates{margin:.8rem 0 .4rem;position:relative}
.carte-regates svg{display:block;width:100%;height:auto;aspect-ratio:2/1;background:#071c31;
  border:1px solid rgba(255,255,255,.09);touch-action:manipulation}
.carte-regates .terre{fill:#16405f;stroke:#2f6a93;stroke-width:.25;stroke-linejoin:round}
.carte-regates .grille{fill:none;stroke:#fff;stroke-opacity:.07;stroke-width:.2}
.carte-regates .pt{cursor:pointer;outline:none}
.carte-regates .pt .hit{fill:transparent}
.carte-regates .pt .dot{fill:#e23a3e;fill-opacity:.85;stroke:#fff;stroke-opacity:.9}
.carte-regates .pt.champ .dot{fill:#e8c468}
.carte-regates .pt.ap .dot{fill-opacity:.4}
.carte-regates .pt.groupe .dot{fill:#0f2438;stroke:#e23a3e;stroke-opacity:1}
.carte-regates .pt text{fill:#fff;text-anchor:middle;pointer-events:none;font-family:inherit}
.carte-regates .pt:hover .dot,.carte-regates .pt.sel .dot{fill:#fff}
.carte-regates .pt:focus-visible .hit{stroke:#fff;stroke-width:.4;stroke-dasharray:1.2 1}
.carte-regates .pt.sel text{fill:#0a1a2b}
.carte-reset{position:absolute;top:.5rem;right:.5rem;min-width:44px;min-height:44px;background:#0f2438;
  color:#fff;border:1px solid rgba(255,255,255,.25);border-radius:3px;font:inherit;font-size:.72rem;
  cursor:pointer;padding:0 .7rem}
.carte-reset[hidden]{display:none}
.carte-info{min-height:2.6rem;margin:.5rem 0 0;font-size:.78rem;color:#9db2c6}
.carte-info b{color:#fff;font-weight:500}
.carte-info a{text-decoration:underline;text-decoration-color:rgba(226,58,62,.6);display:inline-block;padding:.35rem 0}
.carte-info ul{margin:.3rem 0 0;padding-left:1.1rem}
.carte-info li{margin:.15rem 0}
.carte-note{margin:.2rem 0 0;font-size:.72rem;color:#6f8598}
"""

# Textes : fr/de/en/it/es/pt. {n} = nombre sur la carte, {m} = nombre sans position, {t} = total.
TEXTES = {
    "fr": {"aide": "Touchez une pastille pour voir l'épreuve ; un rond numéroté regroupe plusieurs épreuves.",
           "ap": "position approximative (centre du pays)", "sans": "Aucune position à afficher.",
           "reset": "Tout voir", "carte": "Carte", "titre": "Les épreuves sur la carte",
           "compte": "{n} sur la carte, {m} sans position (elles figurent dans la liste ci-dessous).",
           "groupe": "{n} épreuves à cet endroit", "plus": "et {n} autres"},
    "de": {"aide": "Punkt antippen, um die Veranstaltung zu sehen; ein nummerierter Kreis fasst mehrere zusammen.",
           "ap": "ungefähre Position (Landesmitte)", "sans": "Keine Position anzuzeigen.",
           "reset": "Alles zeigen", "carte": "Karte", "titre": "Die Veranstaltungen auf der Karte",
           "compte": "{n} auf der Karte, {m} ohne Position (sie stehen in der Liste unten).",
           "groupe": "{n} Veranstaltungen an diesem Ort", "plus": "und {n} weitere"},
    "en": {"aide": "Tap a dot to see the race; a numbered circle groups several races.",
           "ap": "approximate position (country centre)", "sans": "No position to show.",
           "reset": "Show all", "carte": "Map", "titre": "Races on the map",
           "compte": "{n} on the map, {m} without a position (they are in the list below).",
           "groupe": "{n} races at this place", "plus": "and {n} more"},
    "it": {"aide": "Tocca un punto per vedere la regata; un cerchio numerato ne raggruppa più d'una.",
           "ap": "posizione approssimativa (centro del paese)", "sans": "Nessuna posizione da mostrare.",
           "reset": "Mostra tutto", "carte": "Mappa", "titre": "Le regate sulla mappa",
           "compte": "{n} sulla mappa, {m} senza posizione (sono nell'elenco qui sotto).",
           "groupe": "{n} regate in questo luogo", "plus": "e altre {n}"},
    "es": {"aide": "Toca un punto para ver la regata; un círculo numerado agrupa varias.",
           "ap": "posición aproximada (centro del país)", "sans": "Ninguna posición que mostrar.",
           "reset": "Ver todo", "carte": "Mapa", "titre": "Las regatas en el mapa",
           "compte": "{n} en el mapa, {m} sin posición (están en la lista de abajo).",
           "groupe": "{n} regatas en este lugar", "plus": "y {n} más"},
    "pt": {"aide": "Toca num ponto para ver a regata; um círculo numerado agrupa várias.",
           "ap": "posição aproximada (centro do país)", "sans": "Nenhuma posição a mostrar.",
           "reset": "Ver tudo", "carte": "Mapa", "titre": "As regatas no mapa",
           "compte": "{n} no mapa, {m} sem posição (estão na lista abaixo).",
           "groupe": "{n} regatas neste local", "plus": "e mais {n}"},
}

GRILLE = ("M0 30H360M0 60H360M0 90H360M0 120H360M0 150H360"
          "M30 0V180M60 0V180M90 0V180M120 0V180M150 0V180M180 0V180M210 0V180M240 0V180"
          "M270 0V180M300 0V180M330 0V180")


def fond_svg() -> str:
    """Marque SVG du fond (repère x = lon + 180, y = 90 - lat) : côtes si le tracé existe, sinon la grille
    de points déjà publiée. Le quadrillage est toujours là : on lit une échelle (30° entre deux traits)."""
    grille = f'<path class="grille" d="{GRILLE}"/>'
    if COTES.exists():
        d = COTES.read_text(encoding="utf-8").strip()
        return f'<path class="terre" d="{d}"/>' + grille
    return ('<image href="carte-monde.png" x="0" y="0" width="360" height="180" preserveAspectRatio="none"/>'
            + grille)


def html(titre_id: str = "carte-titre") -> str:
    return ('<div class="carte-regates"><h2 id="' + titre_id + '" class="etiq">Les épreuves sur la carte</h2>'
            '<svg id="carte-svg" viewBox="0 0 360 180" role="group" aria-label="Carte"></svg>'
            '<button class="carte-reset" id="carte-reset" type="button" hidden></button>'
            '<p class="carte-info" id="carte-info" role="status" aria-live="polite"></p>'
            '<p class="carte-note" id="carte-note"></p></div>')


JS = r"""
// ── Carte des épreuves (brique carte_epreuves.py). Repère : x = lon + 180, y = 90 - lat.
var CarteEpreuves = (function(){
  var NS = 'http://www.w3.org/2000/svg';
  var FOND = __FOND__;
  var TX = __TEXTES__;
  function creer(cfg){
    var C = {};
    // Textes dans la langue courante de la page (relue à chaque tracé : stages.html change de langue sans recharger).
    function maj(){
      var l = (document.documentElement.lang || 'fr').slice(0,2), b = TX[l] || TX.fr;
      var o = (cfg.textes && (cfg.textes[l] || cfg.textes.fr)) || {};
      C = {};
      for(var k in b) C[k] = o[k] || b[k];
    }
    maj();
    var svg = document.getElementById('carte-svg'), info = document.getElementById('carte-info');
    var note = document.getElementById('carte-note'), reset = document.getElementById('carte-reset');
    var pts = [], vue = {x:0, y:0, w:360, h:180}, groupes = [], total = 0, zoome = false;
    svg.setAttribute('aria-label', C.carte);
    reset.textContent = C.reset;
    function px(n){ var l = svg.getBoundingClientRect().width || 320; return n * vue.w / l; }
    function cadre(liste){
      var x0 = 0, y0 = 0, w = 360, h = 180;
      if(liste.length){
        var la = liste.map(function(e){return e.lat;}), lo = liste.map(function(e){return e.lon;});
        var mnLa = Math.min.apply(null,la), mxLa = Math.max.apply(null,la);
        var mnLo = Math.min.apply(null,lo), mxLo = Math.max.apply(null,lo);
        w = Math.max((mxLo - mnLo) * 1.3, 8); h = Math.max((mxLa - mnLa) * 1.3, 4);
        if(w < 2*h) w = 2*h; else h = w/2;
        if(w > 360){ w = 360; h = 180; }
        x0 = Math.min(Math.max((mnLo + mxLo)/2 + 180 - w/2, 0), 360 - w);
        y0 = Math.min(Math.max(90 - (mnLa + mxLa)/2 - h/2, 0), 180 - h);
      }
      return {x:x0, y:y0, w:w, h:h};
    }
    function el(nom, attrs){
      var n = document.createElementNS(NS, nom);
      for(var k in attrs) n.setAttribute(k, attrs[k]);
      return n;
    }
    function regroupe(){
      var cell = px(44), cases = {}, out = [];
      pts.forEach(function(e){
        var k = Math.floor((e.lon + 180) / cell) + ',' + Math.floor((90 - e.lat) / cell);
        (cases[k] = cases[k] || []).push(e);
      });
      for(var k in cases){
        var m = cases[k], sx = 0, sy = 0;
        m.forEach(function(e){ sx += e.lon + 180; sy += 90 - e.lat; });
        out.push({x: sx / m.length, y: sy / m.length, membres: m});
      }
      return out;
    }
    function dessine(){
      svg.setAttribute('viewBox', vue.x + ' ' + vue.y + ' ' + vue.w + ' ' + vue.h);
      svg.innerHTML = FOND;
      var fond = svg.querySelector('image'); if(fond) fond.setAttribute('aria-hidden', 'true');
      groupes = regroupe();
      groupes.forEach(function(g, i){
        var seul = g.membres.length === 1, e = g.membres[0];
        var cls = 'pt' + (seul ? (e.champ ? ' champ' : '') + (e.ap ? ' ap' : '') : ' groupe');
        var n = el('g', {'class': cls, 'data-g': i, tabindex: 0, role: 'button',
          'aria-label': seul ? e.label : C.groupe.replace('{n}', g.membres.length)});
        n.appendChild(el('circle', {'class': 'hit', cx: g.x, cy: g.y, r: px(22)}));
        n.appendChild(el('circle', {'class': 'dot', cx: g.x, cy: g.y, r: px(seul ? 6 : 11), 'stroke-width': px(1.5)}));
        if(!seul){
          var t = el('text', {x: g.x, y: g.y, dy: '.35em', 'font-size': px(11), 'aria-hidden': 'true'});
          t.textContent = g.membres.length;
          n.appendChild(t);
        }
        svg.appendChild(n);
      });
      reset.hidden = !zoome;
    }
    function ligne(e){ return e.html; }
    function choisit(n){
      var g = groupes[parseInt(n.getAttribute('data-g'), 10)];
      if(!g) return;
      Array.prototype.forEach.call(svg.querySelectorAll('.sel'), function(x){ x.classList.remove('sel'); });
      n.classList.add('sel');
      var m = g.membres;
      if(m.length === 1){
        info.innerHTML = ligne(m[0]) + (m[0].ap ? ' <i>(' + C.ap + ')</i>' : '');
        return;
      }
      var c = cadre(m);
      // Zoom seulement s'il sépare quelque chose ; au même endroit, on liste.
      var etendue = Math.max.apply(null, m.map(function(e){return e.lon;})) - Math.min.apply(null, m.map(function(e){return e.lon;}))
        + Math.max.apply(null, m.map(function(e){return e.lat;})) - Math.min.apply(null, m.map(function(e){return e.lat;}));
      if(etendue > 0.05 && c.w < vue.w * 0.9){
        vue = c; zoome = true; dessine();
        info.textContent = C.aide;
        var b = svg.querySelector('.pt'); if(b) b.focus();
        return;
      }
      var s = '<b>' + C.groupe.replace('{n}', m.length) + '</b><ul>';
      m.slice(0, 8).forEach(function(e){ s += '<li>' + ligne(e) + '</li>'; });
      if(m.length > 8) s += '<li>' + C.plus.replace('{n}', m.length - 8) + '</li>';
      info.innerHTML = s + '</ul>';
    }
    function sur(ev){ var n = ev.target; while(n && n !== svg){ if(n.classList && n.classList.contains('pt')) return n; n = n.parentNode; } return null; }
    svg.addEventListener('click', function(ev){ var n = sur(ev); if(n) choisit(n); });
    svg.addEventListener('keydown', function(ev){
      if(ev.key === 'Enter' || ev.key === ' '){ var n = sur(ev); if(n){ ev.preventDefault(); choisit(n); } }
    });
    reset.addEventListener('click', function(){ vue = cadre(pts); zoome = false; dessine(); info.textContent = C.aide; });
    var minuteur = null;
    window.addEventListener('resize', function(){ clearTimeout(minuteur); minuteur = setTimeout(dessine, 150); });
    var aZoome = false;
    var api = {
      // zoom sur la position du visiteur : 100 km autour (26/11/2026), une seule fois par page.
      zoomSur: function(lat, lon, km){
        km = km || 100;
        var dl = km / 111.32, w = Math.max(4 * dl, 2 * dl / Math.max(Math.cos(lat * Math.PI / 180), 0.2)), h = w / 2;
        vue = {x: Math.min(Math.max(lon + 180 - w / 2, 0), 360 - w), y: Math.min(Math.max(90 - lat - h / 2, 0), 180 - h), w: w, h: h};
        zoome = true; aZoome = true; dessine();
      },
      // liste = points affichables ; nTotal = nombre d'éléments de la liste sous la carte.
      montre: function(liste, nTotal){
        maj(); svg.setAttribute('aria-label', C.carte); reset.textContent = C.reset;
        var h = document.getElementById('carte-titre'); if(h) h.textContent = C.titre;
        pts = liste; total = nTotal;
        vue = cadre(pts); zoome = false;
        dessine();
        if(!aZoome && window.smGeo && window.smGeo.get()){ var g0 = window.smGeo.get(); api.zoomSur(g0.lat, g0.lon, 100); }
        info.textContent = pts.length ? C.aide : C.sans;
        note.textContent = C.compte.replace('{n}', pts.length).replace('{m}', Math.max(nTotal - pts.length, 0));
      },
      titre: C.carte
    };
    return api;
  }
  return {creer: creer};
})();
"""


def js() -> str:
    return (JS.replace("__FOND__", json.dumps(fond_svg()))
              .replace("__TEXTES__", json.dumps(TEXTES, ensure_ascii=False, separators=(",", ":"))))
