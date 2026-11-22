"""Patch unique (nuit du 22/11) : remplace la carte maison de regates_page.py par la brique carte_epreuves.
Peut être supprimé après lecture."""
from pathlib import Path

p = Path(__file__).resolve().parent / "regates_page.py"
s = p.read_text(encoding="utf-8")

# 1. JS : du commentaire « Carte : » jusqu'au listener keydown inclus.
a = s.index("  // ── Carte : les épreuves filtrées posées sur carte-monde.png")
fin_marq = "  // Fuseau horaire → pays (codes de regates.json)."
b = s.index(fin_marq)
nouveau = r"""  // ── Carte : brique commune carte_epreuves.py (côtes, pastilles de 44 px, regroupement, clavier).
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
"""
s = s[:a] + nouveau + s[b:]

# 2. HTML du bloc carte.
vieux = s[s.index("        '<div class=\"carte-regates\">"):s.index("        '<div id=\"liste\"></div>'")]
s = s.replace(vieux, "        + carte_epreuves.html() +\n")

# 3. CSS et JS : la brique est collée devant le JS de la page.
s = s.replace('JS = r"""\n(function(){', 'CSS = CSS.replace("__CARTE_CSS__", carte_epreuves.CSS)\n\nJS = r"""\n(function(){', 1)
s = s.replace('"</script><script>" + JS + "</script>"', '"</script><script>" + carte_epreuves.js() + JS + "</script>"', 1)
p.write_text(s, encoding="utf-8")
print("ok")
