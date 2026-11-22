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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regates_classes  # noqa: E402  (table sigle → nom, jauges « tout bateau »)
import regates_drapeaux  # noqa: E402  (drapeaux SVG, noms de pays en six langues)

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

JS = r"""
(function(){
  var data = JSON.parse(document.getElementById('donnees').textContent);
  var champ = document.getElementById('q');
  var compte = document.getElementById('compte');
  var liste = document.getElementById('liste');
  var menus = Array.prototype.slice.call(document.querySelectorAll('select[data-groupe]'));
  var effacer = document.getElementById('effacer');
  var etat = {region:'tout', type:'tout', quand:'venir', texte:'', classe:'tous'};

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
    var groupes = [], vus = {};
    gardes.forEach(function(e){
      var k = moisCle(e.debut);
      if(!vus[k]){vus[k]=[];groupes.push(k);}
      vus[k].push(e);
    });
    var html = '';
    groupes.forEach(function(k){
      var l = vus[k];
      html += '<section class="mois"><h2>' + moisLisible(k) + ' <span>' + l.length + (l.length>1?' épreuves':' épreuve') + '</span></h2>';
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
        html += '<article class="epreuve ' + (CADRE[e.type] || '') + '">'
             + '<div class="quand"><span class="j">' + dates + '</span></div>'
             + '<div><div class="titre">' + casse(e.nom) + '</div>'
             + ((dr || lieu) ? '<div class="ou">' + dr + (lieu ? '<span class="vil">' + casse(lieu) + '</span>' : '') + '</div>' : '')
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
  dessineClasses();
  champ.addEventListener('input', function(){ etat.texte = champ.value; dessine(); });
  effacer.addEventListener('click', function(){
    etat = {region:'tout', type:'tout', quand:'venir', texte:'', classe:'tous'};
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
        c1:'Je veux recevoir un résumé chaque lundi des nouvelles épreuves correspondant à ce filtre.', c2:'Je veux aussi recevoir les offres de Sailing More (facultatif).',
        ok:'Envoyer', recu:'Un e-mail de confirmation vous a été envoyé : cliquez sur le lien pour activer l\'alerte.', err:'Échec de l\'envoi, réessayez plus tard.', pour:'Alerte pour :'},
    de:{btn:'Für diesen Filter benachrichtigen', tout:'alle Filter', email:'Ihre E-Mail', h:'Zeitraum', h30:'1 Monat', h90:'3 Monate', h365:'1 Jahr', htout:'alle kommenden Regatten',
        c1:'Ich möchte jeden Montag eine Zusammenfassung neuer Regatten zu diesem Filter erhalten.', c2:'Ich möchte außerdem Angebote von Sailing More erhalten (freiwillig).',
        ok:'Senden', recu:'Eine Bestätigungs-E-Mail wurde gesendet: Klicken Sie auf den Link, um die Benachrichtigung zu aktivieren.', err:'Senden fehlgeschlagen, bitte später erneut versuchen.', pour:'Benachrichtigung für:'},
    en:{btn:'Alert me for this filter', tout:'all filters', email:'Your email', h:'Horizon', h30:'1 month', h90:'3 months', h365:'1 year', htout:'all upcoming races',
        c1:'I want a Monday summary of new races matching this filter.', c2:'I also want to receive Sailing More offers (optional).',
        ok:'Send', recu:'A confirmation email has been sent: click the link to activate the alert.', err:'Sending failed, please try again later.', pour:'Alert for:'},
    it:{btn:'Avvisami per questo filtro', tout:'tutti i filtri', email:'La tua e-mail', h:'Orizzonte', h30:'1 mese', h90:'3 mesi', h365:'1 anno', htout:'tutte le regate in programma',
        c1:'Voglio ricevere ogni lunedì un riepilogo delle nuove regate che corrispondono a questo filtro.', c2:'Voglio ricevere anche le offerte di Sailing More (facoltativo).',
        ok:'Invia', recu:'Ti abbiamo inviato un\'e-mail di conferma: clicca sul link per attivare l\'avviso.', err:'Invio non riuscito, riprova più tardi.', pour:'Avviso per:'},
    es:{btn:'Avisarme para este filtro', tout:'todos los filtros', email:'Tu correo', h:'Horizonte', h30:'1 mes', h90:'3 meses', h365:'1 año', htout:'todas las regatas próximas',
        c1:'Quiero recibir cada lunes un resumen de las nuevas regatas que coincidan con este filtro.', c2:'También quiero recibir las ofertas de Sailing More (opcional).',
        ok:'Enviar', recu:'Te hemos enviado un correo de confirmación: haz clic en el enlace para activar el aviso.', err:'Error al enviar, inténtalo más tarde.', pour:'Aviso para:'},
    pt:{btn:'Avisar-me para este filtro', tout:'todos os filtros', email:'O teu e-mail', h:'Horizonte', h30:'1 mês', h90:'3 meses', h365:'1 ano', htout:'todas as regatas futuras',
        c1:'Quero receber à segunda-feira um resumo das novas regatas que correspondem a este filtro.', c2:'Quero também receber as ofertas da Sailing More (opcional).',
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
        '<div class="groupe"><span class="etiq" id="etiq-classe">Bateau</span>'
        '<select class="menu" id="classe" data-groupe="classe" data-defaut="tous"'
        ' aria-label="Classe de bateau"></select></div>'
        '<div class="groupe"><span class="etiq">Quand</span>'
        + menu("quand", "Quand", [("venir", "À venir"), ("tout", "Toutes les dates")], "venir")
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
        "<style>" + CSS + "</style></head><body>" + sprite +
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
    # Un pays sans drapeau dans la table : la carte n'a rien (voulu), mais on le dit pour l'ajouter.
    sans_drapeau: dict[str, int] = {}
    for e in epreuves:
        if e["pays"] and e["pays"] not in regates_drapeaux.DRAPEAUX:
            sans_drapeau[e["pays"]] = sans_drapeau.get(e["pays"], 0) + 1
    if sans_drapeau and avertissements is not None:
        avertissements.append("pays sans drapeau : " + ", ".join(f"{c} {n}" for c, n in sorted(sans_drapeau.items())))
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
