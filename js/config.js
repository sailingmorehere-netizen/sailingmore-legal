/* La ligne qui choisit où vivent les favoris : "local" (cet appareil, en service) ou "api" (comptes, plus tard).
   Contrat : hebergement/architecture-comptes-2026-11-24.md. Pour basculer, changer cette ligne et remplir js/favoris.js. */
window.SM_CONFIG = Object.assign({ comptes: "local" }, window.SM_CONFIG || {});
