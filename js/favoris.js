/* favoris.js — LE module qui parle au stockage des favoris (contrat : hebergement/architecture-comptes-2026-11-24.md).
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
