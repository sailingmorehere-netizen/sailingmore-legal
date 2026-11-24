"""Comptes : la source unique de js/comptes.js, js/comptes-ui.js, connexion.html, inscription.html, mon-compte.html.

Nicolas, 24/11/2026 : « il peut coder les comptes sans changement d'hébergement en attendant ? » — oui pour
tout ce qui est écran, non pour ce qui garde les mots de passe. Ce module écrit les écrans et la couche
d'appel ; le serveur (api.sailingmore.fr, hachage, e-mails) reste chez Nicolas.

L'INTERRUPTEUR : `window.SM_CONFIG.comptes` (js/config.js, écrit par favoris_page.py), « local » par défaut.
  - « local » : les pages s'affichent avec une seule phrase vraie (« les comptes ouvrent le 1er décembre »).
    Il n'y a AUCUN <form> et AUCUN <input> : ni dans le HTML, ni créé par le script. Aucune requête ne part.
    Pas de lien dans le menu (site_blocks.MENU_PAGES n'a pas ces pages), `noindex`, hors sitemap.
  - « api » : le script construit les formulaires et appelle js/comptes.js.
INTERDITS (tests : scripts/test_comptes_page.py) : stocker un mot de passe (localStorage, sessionStorage,
cookie, IndexedDB), afficher « connecté » ou « compte créé » sans réponse 2xx du serveur.
Les balises <script> viennent de `site_blocks.balises_comptes()` (liste PAGES_COMPTES), comme les favoris.
Contrat : hebergement/architecture-comptes-2026-11-24.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

PAGES = {
    "connexion.html": ("connexion", "Connexion — Sailing More"),
    "inscription.html": ("inscription", "Créer un compte — Sailing More"),
    "mon-compte.html": ("compte", "Mon compte — Sailing More"),
}

JS_COMPTES = r'''/* comptes.js — la couche d'appel des comptes (contrat : hebergement/architecture-comptes-2026-11-24.md).
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
'''

JS_COMPTES_UI = r'''/* comptes-ui.js — les écrans connexion / inscription / mon compte. Ne parle QU'À window.SMCompte (js/comptes.js)
   et window.SMFav (export des favoris). Libellés : six langues ; le breton s'affiche sur le texte français.
   Mode "local" : une phrase, aucun formulaire, aucune requête. Mode "api" : les formulaires sont construits ici. */
(function(){
  "use strict";
  var C = window.SMCompte;
  var SIX = ["fr", "en", "it", "es", "pt", "de"];

  var T = {
    fr: { retour: "← Sailing More", ferme: "Les comptes ouvrent le 1er décembre. D'ici là, rien n'est enregistré ici : vos favoris restent sur cet appareil.",
      favoris: "Voir mes favoris", co: "Connexion", ins: "Créer un compte", cpt: "Mon compte",
      chapoCo: "Retrouvez vos favoris sur tous vos appareils.", chapoIns: "Une adresse e-mail et un mot de passe suffisent.", chapoCpt: "Votre adresse, vos données, votre compte.",
      email: "Adresse e-mail", mdp: "Mot de passe", mdpAide: "Au moins {n} caractères.", nouveau: "Nouveau mot de passe",
      seConnecter: "Se connecter", creer: "Créer mon compte", oublie: "Mot de passe oublié", lien: "Envoyer le lien", valider: "Enregistrer le nouveau mot de passe",
      pasDeCompte: "Pas encore de compte ?", dejaCompte: "Déjà un compte ?", attente: "Un instant…",
      lienEnvoye: "Si un compte existe pour cette adresse, un lien vient d'y être envoyé.", mdpChange: "Mot de passe changé. Vous pouvez vous connecter.",
      inscrit: "Votre compte est créé.", connecte: "Vous êtes connecté.", connecteAs: "Connecté en tant que",
      export: "Exporter mes données", exportAide: "Un fichier JSON : votre adresse et vos favoris.", suppr: "Supprimer mon compte",
      supprAide: "Supprime votre compte et vos favoris enregistrés sur le serveur. Irréversible.", confirmer: "Supprimer définitivement votre compte et vos favoris ?",
      supprOk: "Votre compte a été supprimé.", nonConnecte: "Vous n'êtes pas connecté.",
      e_email: "Cette adresse e-mail n'est pas valable.", e_court: "Mot de passe trop court : {n} caractères au minimum.",
      e_prise: "Cette adresse est déjà utilisée.", e_identifiants: "Adresse ou mot de passe incorrect.",
      e_expire: "Ce lien a expiré. Demandez-en un nouveau.", e_trop: "Trop de tentatives. Réessayez dans quelques minutes.",
      e_reseau: "Le serveur est injoignable. Rien n'a été modifié.", e_serveur: "Une erreur est survenue. Rien n'a été modifié.", e_fermes: "Les comptes ne sont pas ouverts." },
    en: { retour: "← Sailing More", ferme: "Accounts open on 1 December. Until then nothing is saved here: your favourites stay on this device.",
      favoris: "See my favourites", co: "Sign in", ins: "Create an account", cpt: "My account",
      chapoCo: "Find your favourites on all your devices.", chapoIns: "An e-mail address and a password are enough.", chapoCpt: "Your address, your data, your account.",
      email: "E-mail address", mdp: "Password", mdpAide: "At least {n} characters.", nouveau: "New password",
      seConnecter: "Sign in", creer: "Create my account", oublie: "Forgot password", lien: "Send the link", valider: "Save the new password",
      pasDeCompte: "No account yet?", dejaCompte: "Already have an account?", attente: "One moment…",
      lienEnvoye: "If an account exists for this address, a link has just been sent to it.", mdpChange: "Password changed. You can now sign in.",
      inscrit: "Your account has been created.", connecte: "You are signed in.", connecteAs: "Signed in as",
      export: "Export my data", exportAide: "A JSON file: your address and your favourites.", suppr: "Delete my account",
      supprAide: "Deletes your account and the favourites stored on the server. Irreversible.", confirmer: "Permanently delete your account and favourites?",
      supprOk: "Your account has been deleted.", nonConnecte: "You are not signed in.",
      e_email: "This e-mail address is not valid.", e_court: "Password too short: at least {n} characters.",
      e_prise: "This address is already in use.", e_identifiants: "Wrong address or password.",
      e_expire: "This link has expired. Request a new one.", e_trop: "Too many attempts. Try again in a few minutes.",
      e_reseau: "The server cannot be reached. Nothing was changed.", e_serveur: "An error occurred. Nothing was changed.", e_fermes: "Accounts are not open." },
    it: { retour: "← Sailing More", ferme: "Gli account aprono il 1° dicembre. Fino ad allora qui non viene salvato nulla: i tuoi preferiti restano su questo dispositivo.",
      favoris: "Vedi i miei preferiti", co: "Accedi", ins: "Crea un account", cpt: "Il mio account",
      chapoCo: "Ritrova i tuoi preferiti su tutti i dispositivi.", chapoIns: "Bastano un indirizzo e-mail e una password.", chapoCpt: "Il tuo indirizzo, i tuoi dati, il tuo account.",
      email: "Indirizzo e-mail", mdp: "Password", mdpAide: "Almeno {n} caratteri.", nouveau: "Nuova password",
      seConnecter: "Accedi", creer: "Crea il mio account", oublie: "Password dimenticata", lien: "Invia il link", valider: "Salva la nuova password",
      pasDeCompte: "Non hai ancora un account?", dejaCompte: "Hai già un account?", attente: "Un momento…",
      lienEnvoye: "Se esiste un account per questo indirizzo, un link è appena stato inviato.", mdpChange: "Password cambiata. Ora puoi accedere.",
      inscrit: "Il tuo account è stato creato.", connecte: "Hai effettuato l'accesso.", connecteAs: "Accesso effettuato come",
      export: "Esporta i miei dati", exportAide: "Un file JSON: il tuo indirizzo e i tuoi preferiti.", suppr: "Elimina il mio account",
      supprAide: "Elimina il tuo account e i preferiti salvati sul server. Irreversibile.", confirmer: "Eliminare definitivamente account e preferiti?",
      supprOk: "Il tuo account è stato eliminato.", nonConnecte: "Non hai effettuato l'accesso.",
      e_email: "Questo indirizzo e-mail non è valido.", e_court: "Password troppo corta: almeno {n} caratteri.",
      e_prise: "Questo indirizzo è già in uso.", e_identifiants: "Indirizzo o password errati.",
      e_expire: "Questo link è scaduto. Richiedine uno nuovo.", e_trop: "Troppi tentativi. Riprova tra qualche minuto.",
      e_reseau: "Il server non è raggiungibile. Nulla è stato modificato.", e_serveur: "Si è verificato un errore. Nulla è stato modificato.", e_fermes: "Gli account non sono aperti." },
    es: { retour: "← Sailing More", ferme: "Las cuentas abren el 1 de diciembre. Hasta entonces aquí no se guarda nada: sus favoritos se quedan en este dispositivo.",
      favoris: "Ver mis favoritos", co: "Iniciar sesión", ins: "Crear una cuenta", cpt: "Mi cuenta",
      chapoCo: "Encuentre sus favoritos en todos sus dispositivos.", chapoIns: "Basta una dirección de correo y una contraseña.", chapoCpt: "Su dirección, sus datos, su cuenta.",
      email: "Correo electrónico", mdp: "Contraseña", mdpAide: "Al menos {n} caracteres.", nouveau: "Nueva contraseña",
      seConnecter: "Iniciar sesión", creer: "Crear mi cuenta", oublie: "Contraseña olvidada", lien: "Enviar el enlace", valider: "Guardar la nueva contraseña",
      pasDeCompte: "¿Aún no tiene cuenta?", dejaCompte: "¿Ya tiene cuenta?", attente: "Un momento…",
      lienEnvoye: "Si existe una cuenta para esta dirección, se le acaba de enviar un enlace.", mdpChange: "Contraseña cambiada. Ya puede iniciar sesión.",
      inscrit: "Su cuenta ha sido creada.", connecte: "Ha iniciado sesión.", connecteAs: "Sesión iniciada como",
      export: "Exportar mis datos", exportAide: "Un archivo JSON: su dirección y sus favoritos.", suppr: "Eliminar mi cuenta",
      supprAide: "Elimina su cuenta y los favoritos guardados en el servidor. Irreversible.", confirmer: "¿Eliminar definitivamente su cuenta y sus favoritos?",
      supprOk: "Su cuenta ha sido eliminada.", nonConnecte: "No ha iniciado sesión.",
      e_email: "Este correo electrónico no es válido.", e_court: "Contraseña demasiado corta: al menos {n} caracteres.",
      e_prise: "Esta dirección ya está en uso.", e_identifiants: "Dirección o contraseña incorrectas.",
      e_expire: "Este enlace ha caducado. Solicite uno nuevo.", e_trop: "Demasiados intentos. Vuelva a intentarlo en unos minutos.",
      e_reseau: "No se puede contactar con el servidor. No se ha modificado nada.", e_serveur: "Se ha producido un error. No se ha modificado nada.", e_fermes: "Las cuentas no están abiertas." },
    pt: { retour: "← Sailing More", ferme: "As contas abrem a 1 de dezembro. Até lá, nada é guardado aqui: os seus favoritos ficam neste dispositivo.",
      favoris: "Ver os meus favoritos", co: "Iniciar sessão", ins: "Criar uma conta", cpt: "A minha conta",
      chapoCo: "Encontre os seus favoritos em todos os dispositivos.", chapoIns: "Basta um endereço de e-mail e uma palavra-passe.", chapoCpt: "O seu endereço, os seus dados, a sua conta.",
      email: "Endereço de e-mail", mdp: "Palavra-passe", mdpAide: "Pelo menos {n} caracteres.", nouveau: "Nova palavra-passe",
      seConnecter: "Iniciar sessão", creer: "Criar a minha conta", oublie: "Palavra-passe esquecida", lien: "Enviar a ligação", valider: "Guardar a nova palavra-passe",
      pasDeCompte: "Ainda sem conta?", dejaCompte: "Já tem conta?", attente: "Um momento…",
      lienEnvoye: "Se existir uma conta para este endereço, acabámos de enviar-lhe uma ligação.", mdpChange: "Palavra-passe alterada. Já pode iniciar sessão.",
      inscrit: "A sua conta foi criada.", connecte: "Sessão iniciada.", connecteAs: "Sessão iniciada como",
      export: "Exportar os meus dados", exportAide: "Um ficheiro JSON: o seu endereço e os seus favoritos.", suppr: "Eliminar a minha conta",
      supprAide: "Elimina a sua conta e os favoritos guardados no servidor. Irreversível.", confirmer: "Eliminar definitivamente a conta e os favoritos?",
      supprOk: "A sua conta foi eliminada.", nonConnecte: "Não tem sessão iniciada.",
      e_email: "Este endereço de e-mail não é válido.", e_court: "Palavra-passe demasiado curta: pelo menos {n} caracteres.",
      e_prise: "Este endereço já está em uso.", e_identifiants: "Endereço ou palavra-passe incorretos.",
      e_expire: "Esta ligação expirou. Peça uma nova.", e_trop: "Demasiadas tentativas. Tente novamente dentro de alguns minutos.",
      e_reseau: "Não foi possível contactar o servidor. Nada foi alterado.", e_serveur: "Ocorreu um erro. Nada foi alterado.", e_fermes: "As contas não estão abertas." },
    de: { retour: "← Sailing More", ferme: "Die Konten öffnen am 1. Dezember. Bis dahin wird hier nichts gespeichert: Ihre Favoriten bleiben auf diesem Gerät.",
      favoris: "Meine Favoriten ansehen", co: "Anmelden", ins: "Konto erstellen", cpt: "Mein Konto",
      chapoCo: "Finden Sie Ihre Favoriten auf allen Geräten wieder.", chapoIns: "Eine E-Mail-Adresse und ein Passwort genügen.", chapoCpt: "Ihre Adresse, Ihre Daten, Ihr Konto.",
      email: "E-Mail-Adresse", mdp: "Passwort", mdpAide: "Mindestens {n} Zeichen.", nouveau: "Neues Passwort",
      seConnecter: "Anmelden", creer: "Mein Konto erstellen", oublie: "Passwort vergessen", lien: "Link senden", valider: "Neues Passwort speichern",
      pasDeCompte: "Noch kein Konto?", dejaCompte: "Schon ein Konto?", attente: "Einen Moment …",
      lienEnvoye: "Falls für diese Adresse ein Konto besteht, wurde ihr soeben ein Link gesendet.", mdpChange: "Passwort geändert. Sie können sich jetzt anmelden.",
      inscrit: "Ihr Konto wurde erstellt.", connecte: "Sie sind angemeldet.", connecteAs: "Angemeldet als",
      export: "Meine Daten exportieren", exportAide: "Eine JSON-Datei: Ihre Adresse und Ihre Favoriten.", suppr: "Mein Konto löschen",
      supprAide: "Löscht Ihr Konto und die auf dem Server gespeicherten Favoriten. Nicht umkehrbar.", confirmer: "Konto und Favoriten endgültig löschen?",
      supprOk: "Ihr Konto wurde gelöscht.", nonConnecte: "Sie sind nicht angemeldet.",
      e_email: "Diese E-Mail-Adresse ist ungültig.", e_court: "Passwort zu kurz: mindestens {n} Zeichen.",
      e_prise: "Diese Adresse wird bereits verwendet.", e_identifiants: "Adresse oder Passwort falsch.",
      e_expire: "Dieser Link ist abgelaufen. Fordern Sie einen neuen an.", e_trop: "Zu viele Versuche. Versuchen Sie es in einigen Minuten erneut.",
      e_reseau: "Der Server ist nicht erreichbar. Es wurde nichts geändert.", e_serveur: "Ein Fehler ist aufgetreten. Es wurde nichts geändert.", e_fermes: "Die Konten sind nicht geöffnet." }
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
  function t(k){
    var s = (T[lg()] || T.fr)[k] || T.fr[k] || k;
    return s.replace("{n}", C ? C.MIN : 10);
  }
  function el(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; }

  function style(){
    if(document.getElementById("cpt-style")) return;
    var s = document.createElement("style"); s.id = "cpt-style";
    s.textContent =
      ".cpt-page .cpt-verite{color:#dbe6ef;border-top:1px solid rgba(226,58,62,.45);border-bottom:1px solid rgba(255,255,255,.16);padding:.9rem 0;margin:0 0 1.6rem}" +
      ".cpt-page form{display:grid;gap:1.1rem;max-width:26rem}" +
      ".cpt-page label{display:grid;gap:.3rem;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;color:#9db2c6;font-weight:500}" +
      ".cpt-page input{font:inherit;font-size:1rem;letter-spacing:0;text-transform:none;color:#fff;background:transparent;border:0;border-bottom:1px solid rgba(255,255,255,.4);border-radius:0;padding:.5rem 0;min-height:2.4rem}" +
      ".cpt-page input:focus{outline:0;border-bottom-color:#e23a3e}" +
      ".cpt-page small{color:#9db2c6;text-transform:none;letter-spacing:0}" +
      ".cpt-btn{font:inherit;font-size:.64rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;background:transparent;color:#fff;border:0;border-bottom:1px solid #e23a3e;border-radius:0;padding:.5rem 0;margin:.4rem 0;cursor:pointer;justify-self:start;min-height:2.4rem}" +
      ".cpt-btn:disabled{opacity:.5;cursor:default}" +
      ".cpt-msg{min-height:1.4rem;color:#9db2c6;font-size:.9rem}.cpt-msg.err{color:#ffb3b5}" +
      ".cpt-bloc{padding:1rem 0;border-top:1px solid rgba(255,255,255,.12);margin-top:1.4rem}" +
      "@media (pointer:coarse){.cpt-btn{min-height:44px}}";
    document.head.appendChild(s);
  }

  function champ(type, id, libelle, auto, aide){
    var l = el("label", null, libelle), i = el("input");
    i.type = type; i.id = id; i.required = true; i.autocomplete = auto;
    if(type === "email"){ i.inputMode = "email"; i.autocapitalize = "off"; i.spellcheck = false; }
    if(type === "password"){ i.minLength = C.MIN; i.maxLength = 200; }
    l.appendChild(i);
    if(aide) l.appendChild(el("small", null, aide));
    return { label: l, input: i };
  }
  function lien(href, txt){ var a = el("a", null, txt); a.href = href; return a; }

  /* Le message de retour : écrit seulement après la réponse du serveur (succès) ou l'échec (code d'erreur). */
  function dire(msg, texte, erreur){ msg.textContent = texte; msg.className = "cpt-msg" + (erreur ? " err" : ""); }
  function erreur(msg, e){ dire(msg, t("e_" + ((e && e.code) || "serveur")), true); }
  function occupe(btn, oui){ btn.disabled = !!oui; }

  /* Le formulaire. Au submit : preventDefault, validation, appel, puis on vide le champ mot de passe. */
  function formulaire(champs, bouton, action){
    var f = el("form"), msg = el("p", "cpt-msg"); msg.setAttribute("role", "status");
    f.noValidate = false; f.setAttribute("autocomplete", "on");
    champs.forEach(function(c){ f.appendChild(c.label); });
    var b = el("button", "cpt-btn", bouton); b.type = "submit";
    f.append(b, msg);
    f.addEventListener("submit", function(ev){
      ev.preventDefault();
      if(!C || !C.ouvert()) return;                       /* mode local : rien ne part, jamais */
      dire(msg, t("attente")); occupe(b, true);
      var fin = function(){ occupe(b, false); champs.forEach(function(c){ if(c.input.type === "password") c.input.value = ""; }); };
      action(msg).then(fin, function(e){ fin(); erreur(msg, e); });
    });
    return f;
  }

  function ecranConnexion(zone){
    var p = new URLSearchParams(location.search), jeton = p.get("jeton");
    zone.appendChild(el("p", null, t("chapoCo")));
    if(jeton){                                             /* lien de réinitialisation reçu par e-mail */
      var nv = champ("password", "cpt-nv", t("nouveau"), "new-password", t("mdpAide"));
      zone.appendChild(formulaire([nv], t("valider"), function(msg){
        return C.changerMotDePasse(jeton, nv.input.value).then(function(){ dire(msg, t("mdpChange")); });
      }));
      return;
    }
    var em = champ("email", "cpt-email", t("email"), "email"), pw = champ("password", "cpt-mdp", t("mdp"), "current-password");
    zone.appendChild(formulaire([em, pw], t("seConnecter"), function(msg){
      /* « connecté » ne s'écrit que si le serveur répond 2xx */
      return C.connecter(em.input.value, pw.input.value).then(function(){ dire(msg, t("connecte")); location.href = "mon-compte.html"; });
    }));
    var em2 = champ("email", "cpt-email2", t("oublie"), "email");
    var bloc = el("div", "cpt-bloc");
    bloc.appendChild(formulaire([em2], t("lien"), function(msg){
      return C.demanderLien(em2.input.value).then(function(){ dire(msg, t("lienEnvoye")); });
    }));
    zone.appendChild(bloc);
    var pied = el("p"); pied.append(t("pasDeCompte") + " ", lien("inscription.html", t("ins")));
    zone.appendChild(pied);
  }

  function ecranInscription(zone){
    zone.appendChild(el("p", null, t("chapoIns")));
    var em = champ("email", "cpt-email", t("email"), "email"), pw = champ("password", "cpt-mdp", t("mdp"), "new-password", t("mdpAide"));
    zone.appendChild(formulaire([em, pw], t("creer"), function(msg){
      /* « compte créé » ne s'écrit que si le serveur répond 2xx */
      return C.inscrire(em.input.value, pw.input.value).then(function(){ dire(msg, t("inscrit")); });
    }));
    var pied = el("p"); pied.append(t("dejaCompte") + " ", lien("connexion.html", t("co")));
    zone.appendChild(pied);
  }

  function telecharger(nom, texte){
    var u = URL.createObjectURL(new Blob([texte], { type: "application/json" }));
    var a = document.createElement("a"); a.href = u; a.download = nom;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){ URL.revokeObjectURL(u); }, 1000);
  }

  function ecranCompte(zone){
    var msg = el("p", "cpt-msg"); msg.setAttribute("role", "status");
    C.moi().then(function(m){
      /* connecté = le serveur le dit, rien d'autre */
      if(!m || typeof m.email !== "string") throw Object.assign(new Error("identifiants"), { code: "identifiants" });
      var qui = el("p"); qui.append(t("connecteAs") + " ", el("strong", null, m.email));
      zone.appendChild(qui);
      var ex = el("div", "cpt-bloc"), bEx = el("button", "cpt-btn", t("export")); bEx.type = "button";
      ex.append(bEx, el("p", null, t("exportAide")));
      bEx.addEventListener("click", function(){
        var fav = window.SMFav ? window.SMFav.lister() : Promise.resolve([]);
        fav.then(function(l){
          telecharger("sailingmore-compte-" + new Date().toISOString().slice(0, 10) + ".json",
            JSON.stringify({ format: "sailingmore-compte", version: 1, exporte: new Date().toISOString(), email: m.email, favoris: l }, null, 2));
        }).catch(function(e){ erreur(msg, e); });
      });
      var su = el("div", "cpt-bloc"), bSu = el("button", "cpt-btn", t("suppr")); bSu.type = "button";
      su.append(bSu, el("p", null, t("supprAide")));
      bSu.addEventListener("click", function(){
        if(!confirm(t("confirmer"))) return;
        occupe(bSu, true);
        C.supprimer().then(function(){ dire(msg, t("supprOk")); ex.hidden = su.hidden = qui.hidden = true; },
          function(e){ occupe(bSu, false); erreur(msg, e); });
      });
      zone.append(ex, su, msg);
    }).catch(function(e){
      zone.appendChild(el("p", null, e && e.code === "identifiants" ? t("nonConnecte") : t("e_" + ((e && e.code) || "serveur"))));
      zone.appendChild(lien("connexion.html", t("co")));
    });
  }

  function demarrer(){
    var racine = document.getElementById("comptes"); if(!racine) return;
    style();
    var ecran = racine.getAttribute("data-ecran");
    var titre = { connexion: "co", inscription: "ins", compte: "cpt" }[ecran] || "co";
    var h1 = document.querySelector("h1[data-cpt-titre]"); if(h1) h1.textContent = t(titre);
    var r = document.querySelector("[data-cpt-retour]"); if(r) r.textContent = t("retour");
    document.title = t(titre) + " — Sailing More";
    document.documentElement.setAttribute("lang", lg());
    racine.classList.add("cpt-page");
    racine.textContent = "";
    if(!C || !C.ouvert()){
      /* L'interrupteur est sur « local » : la vérité, et rien d'autre. Aucun champ, aucune requête. */
      racine.appendChild(el("p", "cpt-verite", t("ferme")));
      racine.appendChild(lien("mes-favoris.html", t("favoris")));
      return;
    }
    if(ecran === "inscription") ecranInscription(racine);
    else if(ecran === "compte") ecranCompte(racine);
    else ecranConnexion(racine);
  }
  /* un changement de langue redessine l'écran (sans mot de passe à conserver : tout est reconstruit vide) */
  function relancer(){ setTimeout(demarrer, 60); }
  document.addEventListener("click", function(e){ if(e.target.closest && e.target.closest("[data-lang],#langues")) relancer(); });
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", demarrer); else demarrer();
})();
'''

HTML_PAGE = r'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>@TITRE@</title><meta name="robots" content="noindex,nofollow"><style>
  /* Charte du site : le marine écrit, le rouge désigne, filets de 1 px, titres fins, aucun arrondi. */
  *{box-sizing:border-box}
  body{margin:0;background:#0a1a2b;color:#eef3f7;font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
    line-height:1.7;-webkit-font-smoothing:antialiased}
  .page{max-width:44rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
  a.retour{color:#9db2c6;text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;font-weight:500}
  a.retour:hover{color:#fff}
  h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.6rem 0 0;letter-spacing:-.01em;color:#fff;font-weight:300;text-transform:uppercase}
  h1::after{content:"";display:block;width:3.4rem;height:3px;background:#e23a3e;margin:1.3rem 0 1.6rem}
  p,li{color:#eef3f7;font-size:.95rem;line-height:1.7}
  a{color:#fff;text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);text-decoration-thickness:1px;text-underline-offset:3px}
  a:hover{text-decoration-color:#e23a3e}
</style></head><body>
<div class="page">
<a class="retour" href="index.html" data-cpt-retour>← Sailing More</a>
<h1 data-cpt-titre>@H1@</h1>
<div id="comptes" data-ecran="@ECRAN@"><p>Les comptes ouvrent le 1er décembre. D'ici là, rien n'est enregistré ici : vos favoris restent sur cet appareil.</p></div>
<noscript><p>Cette page a besoin de JavaScript.</p></noscript>
</div>
</body></html>
'''

_H1 = {"connexion": "Connexion", "inscription": "Créer un compte", "compte": "Mon compte"}


def page_html(ecran: str, titre: str) -> str:
    return HTML_PAGE.replace("@TITRE@", titre).replace("@H1@", _H1[ecran]).replace("@ECRAN@", ecran)


def ecrire_page(site: Path) -> str:
    """Écrit js/comptes.js, js/comptes-ui.js et les trois pages dans `site`."""
    site = Path(site)
    (site / "js").mkdir(parents=True, exist_ok=True)
    (site / "js" / "comptes.js").write_text(JS_COMPTES, encoding="utf-8")
    (site / "js" / "comptes-ui.js").write_text(JS_COMPTES_UI, encoding="utf-8")
    for nom, (ecran, titre) in PAGES.items():
        (site / nom).write_text(page_html(ecran, titre), encoding="utf-8")
    return ", ".join(PAGES) + " + 2 scripts"


if __name__ == "__main__":
    print(ecrire_page(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sortie-test")))
