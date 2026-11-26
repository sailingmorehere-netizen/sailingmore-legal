/* Traduction automatique du lexique — écrite par trad_auto.py, ne pas modifier ici. */
(function () {
  var SIX = ['fr', 'en', 'de', 'it', 'es', 'pt'];
  function param(n) {
    var m = new RegExp('[?&]' + n + '=([^&]*)').exec(location.search);
    return m ? decodeURIComponent(m[1]) : null;
  }
  var L = param('lg');
  if (!L) { try { L = localStorage.getItem('sm-langue'); } catch (e) { L = null; } }
  if (!L) { L = (navigator.language || navigator.userLanguage || 'fr'); }
  L = String(L).slice(0, 2).toLowerCase();
  if (SIX.indexOf(L) >= 0) { return; }              // langue écrite à la main : rien à traduire
  if (param('auto') === '0') { return; }

  var CLE = 'sm-trad-' + L, cache = {};
  try { cache = JSON.parse(localStorage.getItem(CLE) || '{}') || {}; } catch (e) { cache = {}; }
  var dernier = 0;
  function memo() {
    if (Date.now() - dernier < 3000) { return; }
    dernier = Date.now();
    try { localStorage.setItem(CLE, JSON.stringify(cache)); } catch (e) { /* plein : on continue sans */ }
  }

  document.documentElement.lang = L;

  var IGNORE = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, CODE: 1, PRE: 1, TEXTAREA: 1 };
  function noeuds(racine) {
    var out = [], w = document.createTreeWalker(racine, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = w.nextNode())) {
      var p = n.parentNode;
      if (!p || IGNORE[p.nodeName] || p.closest('#trad-auto')) { continue; }
      var t = n.nodeValue;
      if (!t || !t.trim() || t.trim().length < 2) { continue; }
      out.push(n);
    }
    return out;
  }

  function appliquer(n, trad) {
    var t = n.nodeValue, avant = t.match(/^\s*/)[0], apres = t.match(/\s*$/)[0];
    n.nodeValue = avant + trad + apres;
  }

  function poser(racine) {
    var liste = noeuds(racine), reste = [], sortie = {};
    liste.forEach(function (n) {
      var t = n.nodeValue.trim();
      if (cache[t] !== undefined) { appliquer(n, cache[t]); } else { reste.push(n); }
    });
    return reste;
  }

  var file = [], envoi = false;

  function decouper(lot) {
    var paquets = [], courant = [], taille = 0;
    lot.forEach(function (n) {
      var t = n.nodeValue.trim();
      if (courant.length >= 40 || taille + t.length > 1200) { paquets.push(courant); courant = []; taille = 0; }
      courant.push(n); taille += t.length;
    });
    if (courant.length) { paquets.push(courant); }
    return paquets;
  }

  function demander(textes) {
    var joint = textes.map(function (t, i) { return '⟦' + i + '⟧ ' + t; }).join(' ');
    var url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=' +
      encodeURIComponent(L) + '&dt=t&q=' + encodeURIComponent(joint);
    return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      var rendu = (d && d[0] ? d[0] : []).map(function (p) { return p[0] || ''; }).join('');
      var parts = rendu.split(/⟦\s*(\d+)\s*⟧/), trouves = {};
      for (var i = 1; i < parts.length; i += 2) { trouves[+parts[i]] = (parts[i + 1] || '').trim(); }
      return trouves;
    });
  }

  function envoyer(paquet) {
    var textes = paquet.map(function (n) { return n.nodeValue.trim(); });
    return demander(textes).then(function (trouves) {
      paquet.forEach(function (n, i) {
        var t = textes[i];
        if (trouves[i]) { cache[t] = trouves[i]; appliquer(n, trouves[i]); }
      });
      memo();
    }).catch(function () { /* moteur muet : la page reste en français, sans erreur */ });
  }

  function vider() {
    if (envoi || !file.length) { return; }
    envoi = true;
    var paquet = file.shift();
    envoyer(paquet).then(function () { envoi = false; if (file.length) { vider(); } else { memo(); } });
  }

  function traduire(racine) {
    var reste = poser(racine);
    if (!reste.length) { return; }
    decouper(reste).forEach(function (p) { file.push(p); });
    vider();
  }

  // Les blocs hors écran attendent leur tour : une page de 505 mots ne fait pas 500 requêtes d'un coup.
  var vu = (window.IntersectionObserver) ? new IntersectionObserver(function (entrees) {
    entrees.forEach(function (e) {
      if (!e.isIntersecting) { return; }
      vu.unobserve(e.target);
      traduire(e.target);
    });
  }, { rootMargin: '400px' }) : null;

  function surveiller(racine) {
    if (!vu) { traduire(racine); return; }
    racine.querySelectorAll('.terme, .bloc, .fil, h1, .chapo, .def, .entete').forEach(function (e) { vu.observe(e); });
  }

  function bandeau() {
    var d = document.createElement('div');
    d.id = 'trad-auto';
    d.setAttribute('style', 'position:fixed;left:0;right:0;bottom:0;z-index:80;display:flex;gap:.6rem;' +
      'align-items:center;justify-content:center;padding:.45rem .8rem;font-size:.72rem;' +
      'background:rgba(10,26,43,.96);color:#9db2c6;border-top:1px solid rgba(226,58,62,.45);' +
      'font-family:ui-sans-serif,system-ui,Arial,sans-serif');
    var t = document.createElement('span');
    t.textContent = 'Traduit automatiquement depuis le français';
    var a = document.createElement('a');
    a.href = location.pathname + '?auto=0';
    a.textContent = 'Voir en français';
    a.setAttribute('style', 'color:#e8eef4;border-bottom:1px solid rgba(226,58,62,.7)');
    d.appendChild(t); d.appendChild(a);
    document.body.appendChild(d);
    document.body.style.paddingBottom = '2.6rem';
    demander([t.textContent, a.textContent]).then(function (trouves) {
      if (trouves[0]) { t.textContent = trouves[0]; }
      if (trouves[1]) { a.textContent = trouves[1]; }
    }).catch(function () {});
  }

  function demarrer() {
    surveiller(document.body);
    bandeau();
    if (document.body) {
      traduire(document.querySelector('main') || document.body);
    }
    // Les cartes du lexique sont réécrites à chaque recherche : on réobserve les nouvelles.
    if (window.MutationObserver) {
      var mo = new MutationObserver(function (mutations) {
        mutations.forEach(function (m) {
          Array.prototype.forEach.call(m.addedNodes, function (n) {
            if (n.nodeType === 1) { surveiller(n); traduire(n); }
          });
        });
      });
      var cible = document.getElementById('liste-termes') || document.querySelector('main') || document.body;
      mo.observe(cible, { childList: true, subtree: true });
    }
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', demarrer); }
  else { demarrer(); }
})();
