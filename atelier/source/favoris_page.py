"""Favoris : la source unique de js/config.js, js/favoris.js, js/favoris-ui.js et de mes-favoris.html.

Nicolas, 24/11/2026 : le site est reconstruit depuis les générateurs et l'atelier republie toutes les
15 minutes ; un fichier écrit à la main dans site/ disparaît. Ce module est donc LA source : il écrit les
trois scripts et la page dans le dossier du site, et `accueil_site.sortir_le_site()` l'appelle.

Les balises <script> ne sont PAS dans la page ni posées page par page : `site_blocks.entete_site()` les
ajoute à la barre du site pour les pages de `site_blocks.PAGES_FAVORIS` (une seule liste).
Contrat de stockage : hebergement/architecture-comptes-2026-11-24.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

PAGE = "mes-favoris.html"

JS_CONFIG = r'''/* La ligne qui choisit où vivent les favoris : "local" (cet appareil, en service) ou "api" (comptes, plus tard).
   Contrat : hebergement/architecture-comptes-2026-11-24.md. Pour basculer, changer cette ligne et remplir js/favoris.js. */
window.SM_CONFIG = Object.assign({ comptes: "local" }, window.SM_CONFIG || {});
'''

JS_FAVORIS = r'''/* favoris.js — LE module qui parle au stockage des favoris (contrat : hebergement/architecture-comptes-2026-11-24.md).
   Aucune page, aucun bouton ne touche au stockage : tout passe par window.SMFav.
   Le stockage se choisit par une seule ligne :  window.SM_CONFIG = { comptes: "local" }   ("local" | "api").
   - "local" : localStorage du navigateur, aucune requête réseau. EN SERVICE.
   - "api"   : mêmes fonctions, en fetch vers les adresses du contrat. Écrit, JAMAIS appelé tant que le mode est "local".
   Toutes les fonctions renvoient une Promise, dans les deux modes : le jour de la bascule, rien d'autre ne change.
   Un favori = { type, id, ajoute (ISO), langue }.  Types : regle, bateau, port, stage. */
(function(){
  "use strict";
  var TYPES = ["regle", "bateau", "port", "stage"];
  var LANGUES = ["fr", "en", "it", "es", "pt", "de"];
  var CLE = "sm-favoris";
  var MAX = 2000;            /* plafond de la liste : un import ne peut pas remplir le stockage */
  var MAX_ID = 300;

  function cfg(){ return window.SM_CONFIG || {}; }
  function mode(){ return cfg().comptes === "api" ? "api" : "local"; }
  function base(){ return String(cfg().api || "https://api.sailingmore.fr").replace(/\/+$/, ""); }

  function langue(){
    var l = null;
    try{ l = localStorage.getItem("sm-langue"); }catch(e){}
    if(LANGUES.indexOf(l) >= 0) return l;
    var h = (document.documentElement.getAttribute("lang") || "").slice(0, 2).toLowerCase();
    return LANGUES.indexOf(h) >= 0 ? h : "fr";
  }

  /* Un favori valide, ou null. Tout ce qui vient d'un import est suspect : on ne garde que les quatre champs. */
  function propre(f){
    if(!f || typeof f !== "object") return null;
    var type = f.type, id = f.id;
    if(TYPES.indexOf(type) < 0) return null;
    if(typeof id === "number") id = String(id);
    if(typeof id !== "string") return null;
    id = id.trim();
    if(!id || id.length > MAX_ID) return null;
    var ajoute = (typeof f.ajoute === "string" && !isNaN(Date.parse(f.ajoute))) ? f.ajoute : new Date().toISOString();
    var lg = LANGUES.indexOf(f.langue) >= 0 ? f.langue : langue();
    return { type: type, id: id, ajoute: ajoute, langue: lg };
  }
  function cle(f){ return f.type + "\u0000" + f.id; }
  function sansDoublon(liste){
    var vu = {}, out = [];
    liste.forEach(function(f){ var p = propre(f); if(p && !vu[cle(p)]){ vu[cle(p)] = 1; out.push(p); } });
    return out.slice(0, MAX);
  }

  /* ---------- stockage « local » ---------- */
  var local = {
    lire: function(){
      try{ var v = JSON.parse(localStorage.getItem(CLE) || "[]"); return Array.isArray(v) ? sansDoublon(v) : []; }
      catch(e){ return []; }
    },
    ecrire: function(l){ try{ localStorage.setItem(CLE, JSON.stringify(l)); }catch(e){} return l; },
    lister: function(){ return Promise.resolve(local.lire()); },
    ajouter: function(type, id){
      var p = propre({ type: type, id: id }); if(!p) return local.lister();
      var l = local.lire();
      if(!l.some(function(f){ return cle(f) === cle(p); })) l.push(p);
      return Promise.resolve(local.ecrire(sansDoublon(l)));
    },
    retirer: function(type, id){
      var k = String(id);
      return Promise.resolve(local.ecrire(local.lire().filter(function(f){ return !(f.type === type && f.id === k); })));
    },
    vider: function(){ try{ localStorage.removeItem(CLE); }catch(e){} return Promise.resolve([]); }
  };

  /* ---------- stockage « api » (contrat) : écrit, jamais appelé en mode local ---------- */
  function appel(methode, chemin, corps){
    var o = { method: methode, credentials: "include", headers: {} };
    if(corps !== undefined){ o.headers["Content-Type"] = "application/json"; o.body = JSON.stringify(corps); }
    return fetch(base() + chemin, o).then(function(r){
      if(!r.ok) throw new Error("api " + r.status);
      return r.status === 204 ? null : r.json().catch(function(){ return null; });
    });
  }
  var api = {
    lister: function(){ return appel("GET", "/favoris").then(function(l){ return Array.isArray(l) ? sansDoublon(l) : []; }); },
    ajouter: function(type, id){ return appel("POST", "/favoris", { type: type, id: String(id) }).then(api.lister); },
    retirer: function(type, id){ return appel("DELETE", "/favoris", { type: type, id: String(id) }).then(api.lister); },
    vider: function(){
      return api.lister().then(function(l){
        return Promise.all(l.map(function(f){ return appel("DELETE", "/favoris", { type: f.type, id: f.id }); }));
      }).then(function(){ return []; });
    }
  };

  function st(){ return mode() === "api" ? api : local; }

  /* ---------- export / import : communs aux deux modes ---------- */
  function exporter(){
    return st().lister().then(function(l){
      return JSON.stringify({ format: "sailingmore-favoris", version: 1, exporte: new Date().toISOString(), favoris: l }, null, 2);
    });
  }
  /* importer(json) : chaîne JSON d'un export (ou simple tableau). Sans doublon, jamais d'écrasement.
     Renvoie { ajoutes, ignores, liste } ; rejette si le texte n'est pas un export lisible. */
  function importer(json){
    var d;
    try{ d = typeof json === "string" ? JSON.parse(json) : json; }
    catch(e){ return Promise.reject(new Error("json")); }
    var brut = Array.isArray(d) ? d : (d && Array.isArray(d.favoris) ? d.favoris : null);
    if(!brut) return Promise.reject(new Error("format"));
    var entrants = sansDoublon(brut);
    return st().lister().then(function(avant){
      var connus = {}; avant.forEach(function(f){ connus[cle(f)] = 1; });
      var nouveaux = entrants.filter(function(f){ return !connus[cle(f)]; });
      var suite = Promise.resolve();
      if(mode() === "api"){
        nouveaux.forEach(function(f){ suite = suite.then(function(){ return appel("POST", "/favoris", { type: f.type, id: f.id }); }); });
      }else{
        suite = suite.then(function(){ local.ecrire(sansDoublon(avant.concat(nouveaux))); });
      }
      return suite.then(function(){ return st().lister(); }).then(function(liste){
        return { ajoutes: nouveaux.length, ignores: brut.length - nouveaux.length, liste: liste };
      });
    });
  }

  window.SMFav = {
    TYPES: TYPES,
    mode: mode,
    lister: function(){ return st().lister(); },
    ajouter: function(type, id){ return st().ajouter(type, id); },
    retirer: function(type, id){ return st().retirer(type, id); },
    vider: function(){ return st().vider(); },
    exporter: exporter,
    importer: importer
  };
})();
'''

JS_FAVORIS_UI = r'''/* favoris-ui.js — boutons « enregistrer » et page « mes favoris ». Ne parle QU'À window.SMFav (js/favoris.js),
   jamais au stockage. Libellés dans les six langues du site. Aucune requête réseau en mode local. */
(function(){
  "use strict";
  var F = window.SMFav;
  if(!F) return;
  var SIX = ["fr", "en", "it", "es", "pt", "de"];

  var T = {
    fr: { enr: "Enregistrer", enrOk: "Enregistré", enrTitre: "Garder dans mes favoris", retTitre: "Retirer de mes favoris",
      titre: "Mes favoris", chapo: "Les règles, bateaux, ports et stages que vous avez gardés.",
      local: "Vos favoris restent sur cet appareil : aucune donnée ne le quitte. Exportez-les pour les emporter ailleurs.",
      api: "Connectez-vous pour retrouver vos favoris partout.",
      vide: "Aucun favori pour l'instant. Utilisez « Enregistrer » sur une règle, un bateau, un port ou un stage.",
      retirer: "Retirer", exporter: "Exporter en fichier JSON", importer: "Importer un fichier", vider: "Tout effacer",
      confirmer: "Effacer tous vos favoris ?", ajoute: "ajouté le", ouvrir: "Ouvrir",
      importOk: "{a} ajouté(s), {i} déjà présent(s) ou ignoré(s).", importKo: "Ce fichier n'est pas un export de favoris lisible.",
      regle: "Règles", bateau: "Bateaux", port: "Ports", stage: "Stages", regleU: "Règle", retour: "← Sailing More" },
    en: { enr: "Save", enrOk: "Saved", enrTitre: "Keep in my favourites", retTitre: "Remove from my favourites",
      titre: "My favourites", chapo: "The rules, boats, ports and courses you have kept.",
      local: "Your favourites stay on this device: no data leaves it. Export them to take them elsewhere.",
      api: "Sign in to find your favourites everywhere.",
      vide: "No favourites yet. Use “Save” on a rule, a boat, a port or a course.",
      retirer: "Remove", exporter: "Export as JSON file", importer: "Import a file", vider: "Clear all",
      confirmer: "Delete all your favourites?", ajoute: "added on", ouvrir: "Open",
      importOk: "{a} added, {i} already present or ignored.", importKo: "This file is not a readable favourites export.",
      regle: "Rules", bateau: "Boats", port: "Ports", stage: "Courses", regleU: "Rule", retour: "← Sailing More" },
    it: { enr: "Salva", enrOk: "Salvato", enrTitre: "Tieni nei miei preferiti", retTitre: "Togli dai miei preferiti",
      titre: "I miei preferiti", chapo: "Le regole, le barche, i porti e i corsi che hai tenuto.",
      local: "I tuoi preferiti restano su questo dispositivo: nessun dato lo lascia. Esportali per portarli altrove.",
      api: "Accedi per ritrovare i tuoi preferiti ovunque.",
      vide: "Nessun preferito per ora. Usa «Salva» su una regola, una barca, un porto o un corso.",
      retirer: "Togli", exporter: "Esporta come file JSON", importer: "Importa un file", vider: "Cancella tutto",
      confirmer: "Cancellare tutti i preferiti?", ajoute: "aggiunto il", ouvrir: "Apri",
      importOk: "{a} aggiunti, {i} già presenti o ignorati.", importKo: "Questo file non è un'esportazione di preferiti leggibile.",
      regle: "Regole", bateau: "Barche", port: "Porti", stage: "Corsi", regleU: "Regola", retour: "← Sailing More" },
    es: { enr: "Guardar", enrOk: "Guardado", enrTitre: "Conservar en mis favoritos", retTitre: "Quitar de mis favoritos",
      titre: "Mis favoritos", chapo: "Las reglas, barcos, puertos y cursos que ha guardado.",
      local: "Sus favoritos se quedan en este dispositivo: ningún dato sale de él. Expórtelos para llevarlos a otro lugar.",
      api: "Inicie sesión para encontrar sus favoritos en todas partes.",
      vide: "Aún no hay favoritos. Use «Guardar» en una regla, un barco, un puerto o un curso.",
      retirer: "Quitar", exporter: "Exportar como archivo JSON", importer: "Importar un archivo", vider: "Borrar todo",
      confirmer: "¿Borrar todos sus favoritos?", ajoute: "añadido el", ouvrir: "Abrir",
      importOk: "{a} añadidos, {i} ya presentes o ignorados.", importKo: "Este archivo no es una exportación de favoritos legible.",
      regle: "Reglas", bateau: "Barcos", port: "Puertos", stage: "Cursos", regleU: "Regla", retour: "← Sailing More" },
    pt: { enr: "Guardar", enrOk: "Guardado", enrTitre: "Manter nos meus favoritos", retTitre: "Remover dos meus favoritos",
      titre: "Os meus favoritos", chapo: "As regras, barcos, portos e cursos que guardou.",
      local: "Os seus favoritos ficam neste dispositivo: nenhum dado sai dele. Exporte-os para os levar para outro lado.",
      api: "Inicie sessão para encontrar os seus favoritos em qualquer lado.",
      vide: "Ainda sem favoritos. Use «Guardar» numa regra, num barco, num porto ou num curso.",
      retirer: "Remover", exporter: "Exportar como ficheiro JSON", importer: "Importar um ficheiro", vider: "Apagar tudo",
      confirmer: "Apagar todos os seus favoritos?", ajoute: "adicionado em", ouvrir: "Abrir",
      importOk: "{a} adicionados, {i} já presentes ou ignorados.", importKo: "Este ficheiro não é uma exportação de favoritos legível.",
      regle: "Regras", bateau: "Barcos", port: "Portos", stage: "Cursos", regleU: "Regra", retour: "← Sailing More" },
    de: { enr: "Merken", enrOk: "Gemerkt", enrTitre: "In meinen Favoriten behalten", retTitre: "Aus meinen Favoriten entfernen",
      titre: "Meine Favoriten", chapo: "Die Regeln, Boote, Häfen und Kurse, die Sie behalten haben.",
      local: "Ihre Favoriten bleiben auf diesem Gerät: keine Daten verlassen es. Exportieren Sie sie, um sie woanders zu nutzen.",
      api: "Melden Sie sich an, um Ihre Favoriten überall wiederzufinden.",
      vide: "Noch keine Favoriten. Nutzen Sie „Merken“ bei einer Regel, einem Boot, einem Hafen oder einem Kurs.",
      retirer: "Entfernen", exporter: "Als JSON-Datei exportieren", importer: "Datei importieren", vider: "Alles löschen",
      confirmer: "Alle Favoriten löschen?", ajoute: "hinzugefügt am", ouvrir: "Öffnen",
      importOk: "{a} hinzugefügt, {i} bereits vorhanden oder ignoriert.", importKo: "Diese Datei ist kein lesbarer Favoriten-Export.",
      regle: "Regeln", bateau: "Boote", port: "Häfen", stage: "Kurse", regleU: "Regel", retour: "← Sailing More" }
  };

  function lg(){
    var l = null;
    try{ l = localStorage.getItem("sm-langue"); }catch(e){}
    if(SIX.indexOf(l) >= 0) return l;
    var cand = (navigator.languages || [navigator.language || "fr"]);
    for(var i = 0; i < cand.length; i++){
      var b = String(cand[i]).toLowerCase().slice(0, 2);
      if(SIX.indexOf(b) >= 0) return b;
    }
    var h = (document.documentElement.getAttribute("lang") || "fr").slice(0, 2);
    return SIX.indexOf(h) >= 0 ? h : "fr";
  }
  function t(k){ return (T[lg()] || T.fr)[k] || T.fr[k] || k; }

  /* ---------- style : la charte du site (marine, filet rouge, aucun arrondi) ---------- */
  function style(){
    if(document.getElementById("fav-style")) return;
    var s = document.createElement("style"); s.id = "fav-style";
    s.textContent =
      ".fav-btn{font:inherit;font-size:.64rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;" +
      "background:transparent;color:#9db2c6;border:0;border-bottom:1px solid rgba(226,58,62,.45);border-radius:0;" +
      "padding:.2rem 0;margin:.4rem 0;cursor:pointer;min-height:1.6rem}" +
      ".fav-btn:hover,.fav-btn:focus-visible{color:#fff;border-bottom-color:#e23a3e}" +
      ".fav-btn[aria-pressed=true]{color:#fff;border-bottom-color:#e23a3e}" +
      "@media (pointer:coarse){.fav-btn{min-height:44px;padding:.5rem .2rem}}" +
      ".fav-page .fav-verite{color:#dbe6ef;border-top:1px solid rgba(226,58,62,.45);border-bottom:1px solid rgba(255,255,255,.16);padding:.9rem 0;margin:0 0 1.6rem}" +
      ".fav-page ul{list-style:none;padding:0;margin:0}" +
      ".fav-page li{display:flex;gap:1rem;align-items:baseline;justify-content:space-between;padding:.6rem 0;border-bottom:1px solid rgba(255,255,255,.09)}" +
      ".fav-page small{display:block}" +
      ".fav-actions{display:flex;flex-wrap:wrap;gap:1.4rem;margin:1.6rem 0}" +
      ".fav-msg{color:#9db2c6;font-size:.85rem;min-height:1.4rem}";
    document.head.appendChild(s);
  }

  /* ---------- le bouton : appelle SMFav, jamais le stockage ---------- */
  var connus = null;   /* clé type\0id → true, rafraîchie à chaque lecture de la liste */
  function maj(liste){
    connus = {};
    liste.forEach(function(f){ connus[f.type + "\u0000" + f.id] = true; });
    var bs = document.querySelectorAll(".fav-btn[data-fav-type]");
    for(var i = 0; i < bs.length; i++) habiller(bs[i]);
  }
  function habiller(b){
    var on = !!(connus && connus[b.getAttribute("data-fav-type") + "\u0000" + b.getAttribute("data-fav-id")]);
    b.setAttribute("aria-pressed", on ? "true" : "false");
    b.textContent = on ? t("enrOk") : t("enr");
    b.title = on ? t("retTitre") : t("enrTitre");
  }
  function bouton(type, id){
    var b = document.createElement("button");
    b.type = "button"; b.className = "fav-btn";
    b.setAttribute("data-fav-type", type); b.setAttribute("data-fav-id", id);
    b.addEventListener("click", function(){
      var on = b.getAttribute("aria-pressed") === "true";
      (on ? F.retirer(type, id) : F.ajouter(type, id)).then(maj).catch(function(){});
    });
    habiller(b);
    return b;
  }

  function enrichir(){
    var n = 0, i, el, id;
    /* règles : l'identifiant est celui de l'article (r12, rdef-overlap) — il ne change pas à la republication */
    var regles = document.querySelectorAll("article.regle[id]");
    for(i = 0; i < regles.length; i++){
      el = regles[i];
      if(el.querySelector(":scope > .fav-btn")) continue;
      var h = el.querySelector("h3"); if(!h) continue;
      h.insertAdjacentElement("afterend", bouton("regle", el.id)); n++;
    }
    /* fiche bateau : le slug est le nom du fichier (bateaux/<slug>.html) */
    var m = location.pathname.match(/\/bateaux\/([a-z0-9][a-z0-9-]*)\.html$/);
    var h1 = document.querySelector("h1");
    if(m && h1 && !document.querySelector("h1 + .fav-btn")){ h1.insertAdjacentElement("afterend", bouton("bateau", m[1])); n++; }
    /* stages : l'offre n'a pas d'identifiant propre — on prend l'adresse de l'offre (son lien), stable et unique */
    var offres = document.querySelectorAll("article.offre");
    for(i = 0; i < offres.length; i++){
      el = offres[i];
      if(el.querySelector(".fav-btn")) continue;
      var a = el.querySelector("a.lien[href]"); if(!a) continue;
      id = a.getAttribute("href");
      var zone = el.querySelector(".tete") || el;
      zone.appendChild(bouton("stage", id)); n++;
    }
    /* tout autre élément qui déclare data-fav-type + data-fav-id (ports, par ex.) reçoit son bouton */
    var libres = document.querySelectorAll("[data-fav-type][data-fav-id]:not(.fav-btn)");
    for(i = 0; i < libres.length; i++){
      el = libres[i];
      if(el.querySelector(".fav-btn")) continue;
      el.appendChild(bouton(el.getAttribute("data-fav-type"), el.getAttribute("data-fav-id"))); n++;
    }
    return n;
  }

  /* ---------- page « mes favoris » ---------- */
  function sur(url){ return /^https?:\/\//i.test(url); }
  function cible(f){
    if(f.type === "regle") return { href: "regles-de-course.html#" + encodeURIComponent(f.id),
      nom: /^r\d+$/.test(f.id) ? t("regleU") + " " + f.id.slice(1) : f.id };
    if(f.type === "bateau") return { href: "bateaux/" + encodeURIComponent(f.id) + ".html", nom: f.id.replace(/-/g, " ") };
    if(f.type === "stage") return { href: sur(f.id) ? f.id : null, nom: f.id.replace(/^https?:\/\/(www\.)?/i, "") };
    return { href: "carte.html", nom: f.id };
  }
  function el(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; }

  function page(racine){
    racine.classList.add("fav-page");
    var verite = el("p", "fav-verite"), liste = el("div"), actions = el("div", "fav-actions"), msg = el("p", "fav-msg");
    msg.setAttribute("role", "status");
    var bExp = el("button", "fav-btn"), bImp = el("button", "fav-btn"), bVid = el("button", "fav-btn");
    [bExp, bImp, bVid].forEach(function(b){ b.type = "button"; b.removeAttribute("title"); });
    var fic = el("input"); fic.type = "file"; fic.accept = "application/json,.json"; fic.hidden = true;
    actions.append(bExp, bImp, bVid, fic);
    racine.append(verite, liste, actions, msg);

    function libeller(){
      var h1 = document.querySelector("h1[data-fav-titre]"); if(h1) h1.textContent = t("titre");
      var ch = document.querySelector("[data-fav-chapo]"); if(ch) ch.textContent = t("chapo");
      var r = document.querySelector("[data-fav-retour]"); if(r) r.textContent = t("retour");
      document.title = t("titre") + " — Sailing More";
      document.documentElement.setAttribute("lang", lg());
      verite.textContent = F.mode() === "api" ? t("api") : t("local");
      bExp.textContent = t("exporter"); bImp.textContent = t("importer"); bVid.textContent = t("vider");
    }
    function dessiner(l){
      liste.textContent = "";
      if(!l.length){ liste.appendChild(el("p", null, t("vide"))); bExp.hidden = bVid.hidden = true; return; }
      bExp.hidden = bVid.hidden = false;
      F.TYPES.forEach(function(type){
        var groupe = l.filter(function(f){ return f.type === type; });
        if(!groupe.length) return;
        liste.appendChild(el("h2", null, t(type)));
        var ul = el("ul");
        groupe.forEach(function(f){
          var c = cible(f), li = el("li"), g = el("div");
          if(c.href){ var a = el("a", null, c.nom); a.href = c.href; if(sur(c.href)){ a.rel = "noopener nofollow"; a.target = "_blank"; } g.appendChild(a); }
          else g.appendChild(el("span", null, c.nom));
          var d = new Date(f.ajoute);
          g.appendChild(el("small", null, t("ajoute") + " " + (isNaN(d) ? "" : d.toLocaleDateString(lg()))));
          var r = el("button", "fav-btn", t("retirer")); r.type = "button";
          r.addEventListener("click", function(){ F.retirer(f.type, f.id).then(dessiner); });
          li.append(g, r); ul.appendChild(li);
        });
        liste.appendChild(ul);
      });
    }
    function tout(){ libeller(); F.lister().then(dessiner); }

    bExp.addEventListener("click", function(){
      F.exporter().then(function(txt){
        var u = URL.createObjectURL(new Blob([txt], { type: "application/json" }));
        var a = document.createElement("a");
        a.href = u; a.download = "sailingmore-favoris-" + new Date().toISOString().slice(0, 10) + ".json";
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function(){ URL.revokeObjectURL(u); }, 1000);
      });
    });
    bImp.addEventListener("click", function(){ fic.click(); });
    fic.addEventListener("change", function(){
      var f = fic.files && fic.files[0]; if(!f) return;
      var rd = new FileReader();
      rd.onload = function(){
        F.importer(String(rd.result)).then(function(r){
          msg.textContent = t("importOk").replace("{a}", r.ajoutes).replace("{i}", r.ignores);
          dessiner(r.liste);
        }).catch(function(){ msg.textContent = t("importKo"); });
        fic.value = "";
      };
      rd.readAsText(f);
    });
    bVid.addEventListener("click", function(){ if(confirm(t("confirmer"))) F.vider().then(dessiner); });
    document.addEventListener("click", function(e){ if(e.target.closest && e.target.closest("[data-lang],#langues")) setTimeout(tout, 60); });
    var sel = document.getElementById("langue-sel"); if(sel) sel.addEventListener("change", function(){ setTimeout(tout, 60); });
    tout();
  }

  function demarrer(){
    style();
    var racine = document.getElementById("mes-favoris");
    if(racine) page(racine);
    if(enrichir() || document.querySelector(".fav-btn") || document.getElementById("liste")){
      F.lister().then(maj).catch(function(){});
    }
    /* les offres de stages et les menus de langue se redessinent : on regarde, sans polling */
    var obs = new MutationObserver(function(){
      if(enrichir()) F.lister().then(maj).catch(function(){});
    });
    var cibleObs = document.getElementById("liste") || document.querySelector("main") || document.body;
    obs.observe(cibleObs, { childList: true, subtree: true });
    document.addEventListener("click", function(e){
      if(e.target.closest && e.target.closest("[data-lang]")) setTimeout(function(){ if(connus) maj(Object.keys(connus).map(function(k){ var p = k.split("\u0000"); return { type: p[0], id: p[1] }; })); }, 60);
    });
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", demarrer); else demarrer();
})();
'''

HTML_PAGE = r'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mes favoris — Sailing More</title><meta name="robots" content="noindex"><style>
  /* Charte du site : le marine écrit, le rouge désigne, filets de 1 px, titres fins, aucun arrondi. */
  *{box-sizing:border-box}
  body{margin:0;background:#0a1a2b;color:#eef3f7;font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
    line-height:1.7;-webkit-font-smoothing:antialiased}
  .page{max-width:44rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
  a.retour{color:#9db2c6;text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:500}
  a.retour:hover{color:#fff}
  h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.6rem 0 0;letter-spacing:-.01em;color:#fff;font-weight:300;text-transform:uppercase}
  h1::after{content:"";display:block;width:3.4rem;height:3px;background:#e23a3e;margin:1.3rem 0 1.6rem}
  h2{font-size:.64rem;margin:2.2rem 0 .6rem;letter-spacing:.22em;text-transform:uppercase;color:#9db2c6;font-weight:500;padding-top:1.1rem;border-top:1px solid rgba(226,58,62,.22)}
  p,li{color:#eef3f7;font-size:.95rem;line-height:1.7}
  small{color:#9db2c6;font-size:.78rem}
  a{color:#fff;text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);text-decoration-thickness:1px;text-underline-offset:3px}
  a:hover{text-decoration-color:#e23a3e}
</style></head><body>
<div class="page">
<a class="retour" href="/" data-fav-retour>← Sailing More</a>
<h1 data-fav-titre>Mes favoris</h1>
<p data-fav-chapo>Les règles, bateaux, ports et stages que vous avez gardés.</p>
<div id="mes-favoris"></div>
<noscript><p>Cette page a besoin de JavaScript : les favoris sont gardés dans votre navigateur.</p></noscript>
</div>
</body></html>
'''


def ecrire_page(site: Path) -> str:
    """Écrit js/config.js, js/favoris.js, js/favoris-ui.js et mes-favoris.html dans `site`."""
    site = Path(site)
    (site / "js").mkdir(parents=True, exist_ok=True)
    for nom, texte in (("config.js", JS_CONFIG), ("favoris.js", JS_FAVORIS), ("favoris-ui.js", JS_FAVORIS_UI)):
        (site / "js" / nom).write_text(texte, encoding="utf-8")
    (site / PAGE).write_text(HTML_PAGE, encoding="utf-8")
    return f"{PAGE} + 3 scripts"


if __name__ == "__main__":
    print(ecrire_page(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sortie-test")))
