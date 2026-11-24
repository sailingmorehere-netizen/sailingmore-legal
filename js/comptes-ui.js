/* comptes-ui.js — les écrans connexion / inscription / mon compte. Ne parle QU'À window.SMCompte (js/comptes.js)
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
    /* Une seule détection pour tout le site, dans le <head> (24/11/2026). */
    var d = (typeof window.smLangue === "function") ? window.smLangue()
            : (document.documentElement.getAttribute("lang") || "en").slice(0, 2);
    if(d === "bzh") d = "fr";
    return SIX.indexOf(d) >= 0 ? d : "en";
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
