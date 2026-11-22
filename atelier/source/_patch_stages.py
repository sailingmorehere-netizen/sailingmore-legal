"""Patch unique (nuit du 22/11) : la carte sur stages_page.py. Peut être supprimé après lecture."""
from pathlib import Path

p = Path(__file__).resolve().parent / "stages_page.py"
s = p.read_text(encoding="utf-8")

# 1. Coordonnées : déduites du lieu par la table des ports de regates_page (une seule table), sans toucher stages.json.
s = s.replace(
    "    offres = [o for o in d.get(\"offres\", []) if affichable(o)]\n",
    "    offres = [o for o in d.get(\"offres\", []) if affichable(o)]\n"
    "    offres = [_avec_position(o) for o in offres]\n", 1)
s = s.replace(
    "def construire(d: dict | None = None) -> str:",
    '''def _avec_position(o: dict) -> dict:
    """Ajoute lat/lon (et precision='pays' si c'est le centre du pays) quand le lieu est connu. Sans position,
    l'offre reste dans la liste et n'a simplement pas de pastille."""
    if o.get("lat") is not None and o.get("lon") is not None:
        return o
    import regates_page  # import tardif : la table des ports pèse, et stages n'en a besoin qu'ici
    pos = regates_page.position({"ville": o.get("lieu") or "", "pays": o.get("pays") or ""})
    if not pos:
        return o
    return {**o, "lat": pos[0], "lon": pos[1], **({"precision": "pays"} if pos[2] else {})}


def construire(d: dict | None = None) -> str:''', 1)

# 2. CSS + HTML + JS.
s = s.replace('@media(max-width:560px){input[type=search]', '.carte-regates h2{font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--doux);font-weight:400;margin:0 0 .5rem}\n__CARTE_CSS__\n@media(max-width:560px){input[type=search]', 1)
s = s.replace('CSS = """\n:root', 'CSS = """\n:root', 1)
s = s.replace('JS = r"""\nvar D=', 'CSS = CSS.replace("__CARTE_CSS__", carte_epreuves.CSS)\n\nJS = r"""\nvar D=', 1)
s = s.replace('             "<p class=\\"compte\\" id=\\"compte\\"></p>',
              '             + carte_epreuves.html() +\n             "<p class=\\"compte\\" id=\\"compte\\"></p>', 1)
s = s.replace('+ "</script><script>" + JS + "</script></body></html>")',
              '+ "</script><script>" + carte_epreuves.js() + JS + "</script></body></html>")', 1)
s = s.replace("import json\n", "import json\nimport sys\n", 1) if "import sys" not in s else s
s = s.replace("\nJSON = ICI", "\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nimport carte_epreuves  # noqa: E402\n\nJSON = ICI", 1)

# 3. JS : après le tracé de la liste, la carte reçoit les offres filtrées.
s = s.replace(
    "  var ne=new Set(vus.map(",
    """  var MT={fr:{groupe:'{n} offres à cet endroit',aide:"Touchez une pastille pour voir l'offre ; un rond numéroté regroupe plusieurs offres.",compte:'{n} sur la carte, {m} sans position (elles figurent dans la liste ci-dessous).',titre:'Les stages sur la carte'},
    en:{groupe:'{n} offers at this place',aide:'Tap a dot to see the offer; a numbered circle groups several offers.',compte:'{n} on the map, {m} without a position (they are in the list below).',titre:'Courses on the map',plus:'and {n} more'},
    de:{groupe:'{n} Angebote an diesem Ort',aide:'Punkt antippen, um das Angebot zu sehen; ein nummerierter Kreis fasst mehrere zusammen.',compte:'{n} auf der Karte, {m} ohne Position (sie stehen in der Liste unten).',titre:'Die Kurse auf der Karte'},
    it:{groupe:'{n} offerte in questo luogo',aide:"Tocca un punto per vedere l'offerta; un cerchio numerato ne raggruppa più d'una.",compte:"{n} sulla mappa, {m} senza posizione (sono nell'elenco qui sotto).",titre:'I corsi sulla mappa'},
    es:{groupe:'{n} ofertas en este lugar',aide:'Toca un punto para ver la oferta; un círculo numerado agrupa varias.',compte:'{n} en el mapa, {m} sin posición (están en la lista de abajo).',titre:'Los cursos en el mapa'},
    pt:{groupe:'{n} ofertas neste local',aide:'Toca num ponto para ver a oferta; um círculo numerado agrupa várias.',compte:'{n} no mapa, {m} sem posição (estão na lista abaixo).',titre:'Os cursos no mapa'}};
  if(!window.carteStages)window.carteStages=CarteEpreuves.creer({textes:MT});
  var dlong=function(s){try{return new Intl.DateTimeFormat(L,{day:'numeric',month:'long',year:'numeric'}).format(new Date(s+'T12:00:00'))}catch(x){return s}};
  window.carteStages.montre(vus.filter(function(o){return o.lat!=null&&o.lon!=null}).map(function(o){
    var dates=!o.debut?t('dates_ecole'):(o.fin&&o.fin!==o.debut?t('du')+' '+dt(o.debut)+' '+t('au')+' '+dt(o.fin):dt(o.debut));
    var ou=o.lieu?(o.lieu===o.pays_nom?o.lieu:o.lieu+' · '+o.pays_nom):(o.region||o.pays_nom);
    return {lat:o.lat,lon:o.lon,ap:o.precision==='pays',champ:false,
      label:o.titre+', '+(o.lieu||o.pays_nom||'')+(o.debut?', '+dlong(o.debut):''),
      html:'<b>'+esc(o.titre)+'</b> — '+esc(ou)+' · '+dates+(o.prix!=null?' · '+o.prix.toLocaleString(L)+' '+sym(o.devise):'')
        +' · <a href="'+esc(o.lien)+'" rel="noopener nofollow" target="_blank">'+t('voir')+'</a>'};
  }),vus.length);
  var ne=new Set(vus.map(""", 1)
p.write_text(s, encoding="utf-8")
print("ok")
