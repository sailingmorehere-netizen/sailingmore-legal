/* comptes.js — la couche d'appel des comptes (contrat : hebergement/architecture-comptes-2026-11-24.md).
   Écrite, testable, JAMAIS appelée tant que window.SM_CONFIG.comptes vaut "local" : chaque fonction refuse
   avant tout fetch. Le mot de passe n'existe que le temps de l'appel : il n'est écrit nulle part
   (aucun stockage du navigateur, aucun cookie), seul le serveur le garde (haché, chez lui).
   Chaque fonction renvoie une Promise ; en cas d'échec elle rejette une Error dont .code est l'un de :
   fermes, email, court, prise, identifiants, expire, trop, reseau, serveur. */
(function(){
  "use strict";
  var MIN = 10;   /* longueur minimale du mot de passe ; le serveur reste juge, ceci évite un aller-retour */

  function cfg(){ return window.SM_CONFIG || {}; }
  function ouvert(){ return cfg().comptes === "api"; }
  function base(){ return String(cfg().api || "https://api.sailingmore.fr").replace(/\/+$/, ""); }
  function echec(code){ var e = new Error(code); e.code = code; return Promise.reject(e); }

  function emailValide(a){ return typeof a === "string" && a.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(a.trim()); }
  function mdpValide(m){ return typeof m === "string" && m.length >= MIN && m.length <= 200; }

  /* Le serveur dit {erreur: "<code>"} ; à défaut, le statut HTTP. Rien d'autre ne sort d'ici. */
  var CODES = { email: 1, court: 1, prise: 1, identifiants: 1, expire: 1, trop: 1 };
  function codeDe(statut, corps){
    if(corps && typeof corps.erreur === "string" && CODES[corps.erreur]) return corps.erreur;
    if(statut === 409) return "prise";
    if(statut === 401) return "identifiants";
    if(statut === 410) return "expire";
    if(statut === 429) return "trop";
    if(statut === 400 || statut === 422) return "court";
    return "serveur";
  }

  function appel(methode, chemin, corps){
    if(!ouvert()) return echec("fermes");           /* l'interrupteur : aucune requête en mode local */
    var o = { method: methode, credentials: "include", headers: { "Accept": "application/json" } };
    if(corps !== undefined){ o.headers["Content-Type"] = "application/json"; o.body = JSON.stringify(corps); }
    return fetch(base() + chemin, o).then(function(r){
      return r.json().catch(function(){ return null; }).then(function(j){
        if(!r.ok){ var e = new Error("api " + r.status); e.code = codeDe(r.status, j); throw e; }
        return j;
      });
    }, function(){ return echec("reseau"); });
  }

  window.SMCompte = {
    MIN: MIN,
    ouvert: ouvert,
    emailValide: emailValide,
    mdpValide: mdpValide,
    /* POST /comptes/inscription {email, motDePasse} */
    inscrire: function(email, mdp){
      if(!ouvert()) return echec("fermes");
      if(!emailValide(email)) return echec("email");
      if(!mdpValide(mdp)) return echec("court");
      return appel("POST", "/comptes/inscription", { email: email.trim(), motDePasse: mdp });
    },
    /* POST /comptes/connexion {email, motDePasse} (adresse du contrat d'architecture ; la tâche écrivait « /connexion ») */
    connecter: function(email, mdp){
      if(!ouvert()) return echec("fermes");
      if(!emailValide(email)) return echec("email");
      if(typeof mdp !== "string" || !mdp) return echec("identifiants");
      return appel("POST", "/comptes/connexion",{ email: email.trim(), motDePasse: mdp });
    },
    /* POST /comptes/mot-de-passe {email} : demande d'un lien par e-mail */
    demanderLien: function(email){
      if(!ouvert()) return echec("fermes");
      if(!emailValide(email)) return echec("email");
      return appel("POST", "/comptes/mot-de-passe", { email: email.trim() });
    },
    /* POST /comptes/mot-de-passe {jeton, motDePasse} : choisir le nouveau mot de passe (lien reçu) */
    changerMotDePasse: function(jeton, mdp){
      if(!ouvert()) return echec("fermes");
      if(typeof jeton !== "string" || !jeton) return echec("expire");
      if(!mdpValide(mdp)) return echec("court");
      return appel("POST", "/comptes/mot-de-passe", { jeton: jeton, motDePasse: mdp });
    },
    /* GET /comptes : qui est connecté, selon le SERVEUR (jamais selon le navigateur). {email} ou rejet "identifiants". */
    moi: function(){ return appel("GET", "/comptes"); },
    /* DELETE /comptes : supprime le compte et ses favoris (RGPD) */
    supprimer: function(){ return appel("DELETE", "/comptes"); }
  };
})();
