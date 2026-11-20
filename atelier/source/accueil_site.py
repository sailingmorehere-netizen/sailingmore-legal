"""La page d'accueil de sailingmore.fr — une vitrine, rien d'autre.

Nicolas, 18/11/2026 : « le but du site pour l'instant c'est de présenter Sailing More avec classe »,
même design partout, les réseaux en logos seuls et aux vraies couleurs, les grands chiffres encadrés,
un bandeau de citations de marins qui défile de droite à gauche, un bloc pour le jeu concours,
et une langue par pays qui nous suit.

Ce script fabrique `index.html` et `jeux.html` à partir de trois sources vivantes :
  `cache/rhum/chiffres-stats.json`      les chiffres d'audience (jamais saisis à la main)
  `cache/rhum/citations-marins.json`    les citations, avec leur époque et leur source
  `scripts/jeu_concours.py`             la prochaine date du jeu, calculée

Rien n'est envoyé sans `--publier`. Sans ce drapeau, seul `cache/rhum/site/` est écrit.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import shutil
import datetime
from pathlib import Path

import mer_louvoyage
import site_blocks

RACINE = Path(os.environ.get("SITE_ROOT", "/opt/data"))
CHIFFRES = RACINE / "cache/rhum/chiffres-stats.json"
CITATIONS = RACINE / "cache/rhum/citations-marins.json"
SORTIE = RACINE / "cache/rhum/site"

NUIT = "#08162a"
NUIT2 = "#0d2440"
EAU = "#8ad4d0"
CREME = "#f4efe4"
GRIS = "#c3d6e6"
ROUGE = "#e23a3e"
AMBRE = "#e8b04b"
TOILE = "#f2f7fb"

LANGUES = ["fr", "en", "it", "es", "pt", "de"]

TEXTES = {
    "fr": {
        "surtitre": "Le large, chaque soir.",
        "accroche": "Média <span class='rouge'>indépendant</span> de la voile et de la course au large, fait par des <span class='rouge'>passionnés</span>, pour des <span class='rouge'>passionnés</span>.",
        "chiffres": "Sailing More en chiffres",
        "reseaux": "Nos réseaux",
        "citations": "Ils l'ont dit avant nous",
        "concours_titre": "Le jeu concours",
        "concours_texte": "Un jeu pour un annonceur, six jours de stories, un tirage le dimanche. Prochain départ : mardi {date}.",
        "concours_bouton": "Voir le jeu",
        "abonnes": "abonnés",
        "contenus": "publications",
        "vues": "vues",
        "vues28": "vues, 28 derniers jours",
        "vuesfb": "vues sur Facebook",
        "bourse": "membres de la bourse aux équipiers",
        "auto": "Auto",
        "stories_titre": "Nos informations quotidiennes",
        "stories_note": "Nos six dernières stories",
        "reels_titre": "Les trois derniers reels du blog",
        "carte_titre": "Nos concentrations de voileux",
        "legende_bourses": "Trouvez un équipier — cliquez le bateau de votre océan.",
        "bulle_participants": "participants",
        "kit_titre": "Annonceurs",
        "bloc_nom": "Le bloc de lancement",
        "bloc_ce": "un mois, moitié jeu concours et moitié publications",
        "bloc_detail_titre": "Ce que le bloc contient",
        "bloc_detail": "1 jeu concours de 7 jours · sa feuille d'annonce · 1 story · 2 publications dédiées · le rapport de portée sous 72 h",
        "tarif_notes": "Prix en euros HT. Rapport de portée et d'interactions sous 72 h, chiffres de Meta à l'appui. Mention « Partenariat rémunéré » et contrat écrit. Aucune portée garantie : on la mesure, et on l'écrit avant la signature.",
        "kit_texte": "Un seul bloc pour commencer : un mois, moitié jeu concours et moitié publications, 500 €.",
        "kit_bouton": "Recevoir la grille",
        "kit_preuve": "Ces chiffres viennent de Meta, relevés ce mois-ci.",
        "kit_nom": "Votre nom",
        "kit_marque": "Marque ou activité",
        "kit_email": "Email",
        "kit_note": "Vos données servent seulement à vous répondre. Suppression sur demande.",
        "kit_ou": "Ou écrivez à",
        "kit_lien": "l'adresse du blog",
        "kit_rappel": "Annonceurs — recevoir la grille des tarifs",
        "hero_cta": "Annoncer sur Sailing More",
        "cookies_texte": "Aucun cookie de mesure ni de publicité : ce site n'en dépose aucun.",
        "cookies_lien": "En savoir plus",
        "cookies_bouton": "J'ai compris",
        "ann_intro": "Sailing More parle aux voileux chaque soir. Un bloc de lancement, un mois, moitié jeu concours et moitié publications : 500 €."
    },
    "en": {
        "surtitre": "The open sea, every evening.",
        "accroche": "An <span class='rouge'>independent</span> sailing and offshore racing outlet, made by <span class='rouge'>enthusiasts</span>, for <span class='rouge'>enthusiasts</span>.",
        "chiffres": "Sailing More in numbers",
        "reseaux": "Our channels",
        "citations": "They said it before us",
        "concours_titre": "The giveaway",
        "concours_texte": "One giveaway for an advertiser, six days of stories, a draw on Sunday. Next start: Tuesday {date}.",
        "concours_bouton": "See the giveaway",
        "abonnes": "followers",
        "contenus": "posts",
        "vues": "views",
        "vues28": "views, last 28 days",
        "vuesfb": "views on Facebook",
        "bourse": "crew-finder members",
        "auto": "Auto",
        "stories_titre": "Our daily news",
        "stories_note": "Our last six stories",
        "reels_titre": "The blog's last three reels",
        "carte_titre": "Where our sailors gather",
        "legende_bourses": "Find crew — click the boat for your ocean.",
        "bulle_participants": "members",
        "kit_titre": "Advertisers",
        "bloc_nom": "The launch block",
        "bloc_ce": "one month, half giveaway and half posts",
        "bloc_detail_titre": "What the block contains",
        "bloc_detail": "1 seven-day giveaway · its announcement sheet · 1 story · 2 dedicated posts · the reach report within 72 h",
        "tarif_notes": "Prices in EUR, excl. VAT. Reach and interaction report within 72 h, backed by Meta figures. “Paid partnership” label and written contract. No reach guaranteed: we measure it, and we say so before signing.",
        "kit_texte": "One block to start: a month, half giveaway and half posts, €500.",
        "kit_bouton": "Get the rate card",
        "kit_preuve": "Those figures come from Meta, measured this month.",
        "kit_nom": "Your name",
        "kit_marque": "Brand or business",
        "kit_email": "Email",
        "kit_note": "Your details are only used to reply to you. Deletion on request.",
        "kit_ou": "Or write to",
        "kit_lien": "the blog address",
        "kit_rappel": "Advertisers — get the rate card",
        "hero_cta": "Advertise on Sailing More",
        "cookies_texte": "No analytics or advertising cookies: this site sets none.",
        "cookies_lien": "Learn more",
        "cookies_bouton": "Got it",
        "ann_intro": "Sailing More speaks to sailors every evening. One launch block, a month, half giveaway and half posts: €500."
    },
    "it": {
        "surtitre": "Il largo, ogni sera.",
        "accroche": "Un media <span class='rouge'>indipendente</span> di vela e altura, fatto da <span class='rouge'>appassionati</span>, per <span class='rouge'>appassionati</span>.",
        "chiffres": "Sailing More in numeri",
        "reseaux": "I nostri canali",
        "citations": "L'hanno detto prima di noi",
        "concours_titre": "Il concorso",
        "concours_texte": "Un concorso per un inserzionista, sei giorni di storie, un sorteggio la domenica. Prossima partenza: martedì {date}.",
        "concours_bouton": "Vedi il concorso",
        "abonnes": "follower",
        "contenus": "pubblicazioni",
        "vues": "visualizzazioni",
        "vues28": "visualizzazioni, ultimi 28 giorni",
        "vuesfb": "visualizzazioni su Facebook",
        "bourse": "membri della borsa equipaggi",
        "auto": "Auto",
        "stories_titre": "Le nostre informazioni quotidiane",
        "stories_note": "Le nostre ultime sei storie",
        "reels_titre": "Gli ultimi tre reel del blog",
        "carte_titre": "Le nostre concentrazioni di velisti",
        "legende_bourses": "Trova un equipaggio — clicca la barca del tuo oceano.",
        "bulle_participants": "partecipanti",
        "kit_titre": "Inserzionisti",
        "bloc_nom": "Il blocco di lancio",
        "bloc_ce": "un mese, metà concorso e metà pubblicazioni",
        "bloc_detail_titre": "Cosa contiene il blocco",
        "bloc_detail": "1 concorso di 7 giorni · il suo foglio di annuncio · 1 story · 2 pubblicazioni dedicate · il rapporto di copertura entro 72 ore",
        "tarif_notes": "Prezzi in euro, IVA esclusa. Rapporto su copertura e interazioni entro 72 ore, con i dati di Meta. Dicitura «Collaborazione retribuita» e contratto scritto. Nessuna copertura garantita: la misuriamo e lo scriviamo prima della firma.",
        "kit_texte": "Un solo blocco per iniziare: un mese, metà concorso e metà pubblicazioni, 500 €.",
        "kit_bouton": "Ricevere le tariffe",
        "kit_preuve": "Questi numeri vengono da Meta, rilevati questo mese.",
        "kit_nom": "Il tuo nome",
        "kit_marque": "Marchio o attività",
        "kit_email": "Email",
        "kit_note": "I tuoi dati servono solo per risponderti. Cancellazione su richiesta.",
        "kit_ou": "Oppure scrivi a",
        "kit_lien": "l'indirizzo del blog",
        "kit_rappel": "Inserzionisti — ricevere il listino",
        "hero_cta": "Pubblicizza su Sailing More",
        "cookies_texte": "Nessun cookie di analisi né pubblicitario: questo sito non ne usa.",
        "cookies_lien": "Scopri di più",
        "cookies_bouton": "Ho capito",
        "ann_intro": "Sailing More parla ai velisti ogni sera. Un blocco di lancio, un mese, metà concorso e metà pubblicazioni: 500 €."
    },
    "es": {
        "surtitre": "El mar abierto, cada noche.",
        "accroche": "Un medio <span class='rouge'>independiente</span> de vela y regata oceánica, hecho por <span class='rouge'>aficionados</span>, para <span class='rouge'>aficionados</span>.",
        "chiffres": "Sailing More en cifras",
        "reseaux": "Nuestras redes",
        "citations": "Lo dijeron antes que nosotros",
        "concours_titre": "El sorteo",
        "concours_texte": "Un sorteo para un anunciante, seis días de historias, un sorteo el domingo. Próxima salida: martes {date}.",
        "concours_bouton": "Ver el sorteo",
        "abonnes": "seguidores",
        "contenus": "publicaciones",
        "vues": "visualizaciones",
        "vues28": "visualizaciones, últimos 28 días",
        "vuesfb": "visualizaciones en Facebook",
        "bourse": "miembros de la bolsa de tripulantes",
        "auto": "Auto",
        "stories_titre": "Nuestras informaciones diarias",
        "stories_note": "Nuestras seis últimas stories",
        "reels_titre": "Los tres últimos reels del blog",
        "carte_titre": "Nuestras concentraciones de regatistas",
        "legende_bourses": "Encuentre tripulación — haga clic en el barco de su océano.",
        "bulle_participants": "participantes",
        "kit_titre": "Anunciantes",
        "bloc_nom": "O bloco de lançamento",
        "bloc_ce": "um mês, metade passatempo e metade publicações",
        "bloc_detail_titre": "O que o bloco contém",
        "bloc_detail": "1 passatempo de 7 dias · a sua folha de anúncio · 1 story · 2 publicações dedicadas · o relatório de alcance em 72 h",
        "bloc_nom": "El bloque de lanzamiento",
        "bloc_ce": "un mes, mitad sorteo y mitad publicaciones",
        "bloc_detail_titre": "Qué contiene el bloque",
        "bloc_detail": "1 sorteo de 7 días · su hoja de anuncio · 1 story · 2 publicaciones dedicadas · el informe de alcance en 72 h",
        "tarif_notes": "Preços em euros, sem IVA. Relatório de alcance e interações em 72 h, com dados da Meta. Menção «Parceria paga» e contrato escrito. Sem alcance garantido: medimo-lo e dizemo-lo antes de assinar.",
        "tarif_notes": "Precios en euros, sin IVA. Informe de alcance e interacciones en 72 h, con datos de Meta. Mención «Colaboración remunerada» y contrato escrito. Sin alcance garantizado: lo medimos y lo decimos antes de firmar.",
        "kit_texte": "Un solo bloque para empezar: un mes, mitad sorteo y mitad publicaciones, 500 €.",
        "kit_bouton": "Recibir las tarifas",
        "kit_preuve": "Estas cifras vienen de Meta, medidas este mes.",
        "kit_nom": "Su nombre",
        "kit_marque": "Marca o actividad",
        "kit_email": "Correo",
        "kit_note": "Sus datos solo sirven para responderle. Supresión bajo petición.",
        "kit_ou": "O escriba a",
        "kit_lien": "la dirección del blog",
        "kit_rappel": "Anunciantes — recibir las tarifas",
        "hero_cta": "Anuncie en Sailing More",
        "cookies_texte": "Sin cookies de medición ni de publicidad: este sitio no instala ninguno.",
        "cookies_lien": "Saber más",
        "cookies_bouton": "Entendido",
        "ann_intro": "Sailing More habla con los navegantes cada noche. Un bloque de lanzamiento, un mes, mitad sorteo y mitad publicaciones: 500 €."
    },
    "pt": {
        "surtitre": "O largo, todas as noites.",
        "accroche": "Um meio <span class='rouge'>independente</span> de vela e regata oceânica, feito por <span class='rouge'>apaixonados</span>, para <span class='rouge'>apaixonados</span>.",
        "chiffres": "Sailing More em números",
        "reseaux": "As nossas redes",
        "citations": "Disseram-no antes de nós",
        "concours_titre": "O passatempo",
        "concours_texte": "Um passatempo para um anunciante, seis dias de stories, um sorteio ao domingo. Próxima partida: terça-feira {date}.",
        "concours_bouton": "Ver o passatempo",
        "abonnes": "seguidores",
        "contenus": "publicações",
        "vues": "visualizações",
        "vues28": "visualizações, últimos 28 dias",
        "vuesfb": "visualizações no Facebook",
        "bourse": "membros da bolsa de tripulantes",
        "auto": "Auto",
        "stories_titre": "As nossas informações diárias",
        "stories_note": "As nossas seis últimas stories",
        "reels_titre": "Os três últimos reels do blog",
        "carte_titre": "As nossas concentrações de velejadores",
        "legende_bourses": "Encontre tripulação — clique no barco do seu oceano.",
        "bulle_participants": "participantes",
        "kit_titre": "Anunciantes",
        "kit_texte": "Um só bloco para começar: um mês, metade passatempo e metade publicações, 500 €.",
        "kit_bouton": "Receber a tabela de preços",
        "kit_preuve": "Estes números vêm da Meta, medidos este mês.",
        "kit_nom": "O seu nome",
        "kit_marque": "Marca ou atividade",
        "kit_email": "Email",
        "kit_note": "Os seus dados servem apenas para lhe responder. Eliminação a pedido.",
        "kit_ou": "Ou escreva para",
        "kit_lien": "o endereço do blog",
        "kit_rappel": "Anunciantes — receber a tabela de preços",
        "hero_cta": "Anuncie na Sailing More",
        "cookies_texte": "Sem cookies de medição nem de publicidade: este site não instala nenhum.",
        "cookies_lien": "Saber mais",
        "cookies_bouton": "Entendi",
        "ann_intro": "A Sailing More fala com os velejadores todas as noites. Um bloco de lançamento, um mês, metade passatempo e metade publicações: 500 €."
    },
    "de": {
        "surtitre": "Die Weite, jeden Abend.",
        "accroche": "Ein <span class='rouge'>unabhängiges</span> Segel- und Hochseerenne-Medium, von <span class='rouge'>Begeisterten</span> für <span class='rouge'>Begeisterte</span>.",
        "chiffres": "Sailing More in Zahlen",
        "reseaux": "Unsere Kanäle",
        "citations": "Sie sagten es vor uns",
        "concours_titre": "Das Gewinnspiel",
        "concours_texte": "Ein Gewinnspiel für einen Werbepartner, sechs Tage Stories, Ziehung am Sonntag. Nächster Start: Dienstag, {date}.",
        "concours_bouton": "Zum Gewinnspiel",
        "abonnes": "Follower",
        "contenus": "Beiträge",
        "vues": "Aufrufe",
        "vues28": "Aufrufe, letzte 28 Tage",
        "vuesfb": "Aufrufe auf Facebook",
        "bourse": "Mitglieder der Crew-Börse",
        "auto": "Auto",
        "stories_titre": "Unsere täglichen Informationen",
        "stories_note": "Unsere sechs letzten Stories",
        "reels_titre": "Die drei letzten Reels des Blogs",
        "carte_titre": "Wo sich unsere Segler sammeln",
        "legende_bourses": "Crew finden — klicken Sie auf das Boot Ihres Ozeans.",
        "bulle_participants": "Teilnehmer",
        "kit_titre": "Werbekunden",
        "bloc_nom": "Das Startpaket",
        "bloc_ce": "ein Monat, halb Gewinnspiel und halb Beiträge",
        "bloc_detail_titre": "Was das Paket enthält",
        "bloc_detail": "1 Gewinnspiel über 7 Tage · sein Ankündigungsblatt · 1 Story · 2 eigene Beiträge · der Reichweitenbericht binnen 72 Stunden",
        "tarif_notes": "Preise in Euro zzgl. MwSt. Reichweiten- und Interaktionsbericht binnen 72 Stunden, mit Zahlen von Meta. Hinweis „Bezahlte Partnerschaft“ und schriftlicher Vertrag. Keine garantierte Reichweite: wir messen sie und sagen es vor der Unterschrift.",
        "kit_texte": "Ein Startpaket für den Anfang: ein Monat, halb Gewinnspiel und halb Beiträge, 500 €.",
        "kit_bouton": "Preisliste erhalten",
        "kit_preuve": "Diese Zahlen kommen von Meta, in diesem Monat erhoben.",
        "kit_nom": "Ihr Name",
        "kit_marque": "Marke oder Tätigkeit",
        "kit_email": "E-Mail",
        "kit_note": "Ihre Daten dienen nur der Antwort. Löschung auf Anfrage.",
        "kit_ou": "Oder schreiben Sie an",
        "kit_lien": "die Blog-Adresse",
        "kit_rappel": "Werbekunden — Preisliste erhalten",
        "hero_cta": "Werben auf Sailing More",
        "cookies_texte": "Keine Mess- oder Werbe-Cookies: diese Seite setzt keine.",
        "cookies_lien": "Mehr erfahren",
        "cookies_bouton": "Verstanden",
        "ann_intro": "Sailing More spricht jeden Abend mit Seglern. Ein Startpaket, ein Monat, halb Gewinnspiel und halb Beiträge: 500 €."
    }
}
MOIS = {
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
           "settembre", "ottobre", "novembre", "dicembre"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
           "septiembre", "octubre", "noviembre", "diciembre"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
           "setembro", "outubro", "novembro", "dezembro"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
           "September", "Oktober", "November", "Dezember"],
}


def espace(n: int) -> str:
    """Les grands chiffres en « K » (Nicolas, 19/11/2026 : « mets des K pour remplacer les milliers »).

    123 513 → « 123 K », 17 040 → « 17 K », 2 460 → « 2,5 K », 1 200 000 → « 1,2 M ». Sous mille, le nombre reste entier :
    écrire « 0,4 K » pour 412 abonnés serait une blague. La virgule décimale reste française, et la
    décimale disparaît quand elle ne dit rien (« 17,0 K » → « 17 K »)."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    if abs(n) < 1000:
        return f"{int(round(n)):,}".replace(",", "\u00a0")
    unite, part = ("M", 1_000_000) if abs(n) >= 1_000_000 else ("K", 1_000)
    valeur = n / part
    texte = f"{valeur:.1f}".rstrip("0").rstrip(".") if abs(valeur) < 10 else f"{valeur:.0f}"
    return texte.replace(".", ",") + "\u00a0" + unite


def chiffres() -> dict:
    d = json.loads(CHIFFRES.read_text())
    c = {x["cle"]: x["valeur"] for x in d["chiffres"]}
    c["maj"] = d.get("maj", "")
    return c


def citations() -> list[dict]:
    """Ordre de passage : une époque différente à chaque citation, un auteur
    différent à chaque retour dans la même époque. Le fichier reste la source,
    l'ordre est calculé ici — sinon trois Bougainville se suivent."""
    brutes = json.loads(CITATIONS.read_text())
    epogues = ["XVIIIe", "XIXe", "XXe", "XXIe"]
    files = []
    for ep in epogues:
        groupe = [c for c in brutes if c.get("epoque") == ep]
        par_auteur = {}
        for c in groupe:
            par_auteur.setdefault(c.get("auteur", ""), []).append(c)
        tour = []
        while any(par_auteur.values()):
            for auteur in list(par_auteur):
                if par_auteur[auteur]:
                    tour.append(par_auteur[auteur].pop(0))
        files.append(tour)
    reste = [c for c in brutes if c.get("epoque") not in epogues]
    sortie, i = [], 0
    while any(len(f) > i for f in files):
        for f in files:
            if len(f) > i:
                sortie.append(f[i])
        i += 1
    return sortie + reste


def prochain_jeu() -> str:
    sortie = subprocess.run([sys.executable, str(RACINE / "scripts/jeu_concours.py"), "--prochaine-date"],
                            capture_output=True, text=True, timeout=30)
    trouve = re.search(r"(\d{4}-\d{2}-\d{2})", sortie.stdout or "")
    return trouve.group(1) if trouve else ""


# Les quatre réseaux, aux vraies couleurs, sans cadre ni chiffre.
RESEAUX = [
    ("instagram", "https://www.instagram.com/sailingmorehere/",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
     '<stop offset="0" stop-color="#feda75"/><stop offset=".35" stop-color="#fa7e1e"/>'
     '<stop offset=".65" stop-color="#d62976"/><stop offset="1" stop-color="#962fbf"/></linearGradient></defs>'
     '<path fill="url(#ig)" fill-rule="evenodd" d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 1.9.3 2.4.5.6.2 1 .5 1.5 1 .5.5.8.9 1 1.5.2.5.4 1.2.5 2.4.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.3 1.9-.5 2.4-.2.6-.5 1-1 1.5-.5.5-.9.8-1.5 1-.5.2-1.2.4-2.4.5-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.9-.3-2.4-.5-.6-.2-1-.5-1.5-1-.5-.5-.8-.9-1-1.5-.2-.5-.4-1.2-.5-2.4C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.3-1.9.5-2.4.2-.6.5-1 1-1.5.5-.5.9-.8 1.5-1 .5-.2 1.2-.4 2.4-.5 1.3-.1 1.7-.1 4.9-.1zm0 3.2c-3.1 0-3.5 0-4.7.1-1 .1-1.4.2-1.7.4-.4.2-.7.4-1 .7-.3.3-.5.6-.7 1-.2.3-.3.7-.4 1.7-.1 1.2-.1 1.6-.1 4.7s0 3.5.1 4.7c.1 1 .2 1.4.4 1.7.2.4.4.7.7 1 .3.3.6.5 1 .7.3.2.7.3 1.7.4 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1-.1 1.4-.2 1.7-.4.4-.2.7-.4 1-.7.3-.3.5-.6.7-1 .2-.3.3-.7.4-1.7.1-1.2.1-1.6.1-4.7s0-3.5-.1-4.7c-.1-1-.2-1.4-.4-1.7-.2-.4-.4-.7-.7-1-.3-.3-.6-.5-1-.7-.3-.2-.7-.3-1.7-.4-1.2-.1-1.6-.1-4.7-.1zm0 3.1a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 3.2a2.3 2.3 0 1 0 0 4.6 2.3 2.3 0 0 0 0-4.6zm5.7-3.5a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6z"/></svg>'),
    ("facebook", "https://www.facebook.com/SailingMore",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#1877f2" d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.7-3.9 1.1 0 2.2.2 2.2.2v2.4h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg>'),
    ("youtube", "https://www.youtube.com/@SailingMore",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#ff0000" d="M23 7.5a3 3 0 0 0-2.1-2.1C19 4.9 12 4.9 12 4.9s-7 0-8.9.5A3 3 0 0 0 1 7.5 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.5a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 23.5 12 31 31 0 0 0 23 7.5zM9.8 15.4V8.6L15.7 12z"/></svg>'),
    ("telegram", "https://t.me/sailingmorehere",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#29a9eb" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm4.6 6.6-1.6 7.6c-.1.5-.4.6-.8.4l-2.3-1.7-1.1 1.1c-.1.1-.2.2-.4.2l.2-2.5 4.6-4.1c.2-.2 0-.3-.3-.1l-5.7 3.6-2.4-.8c-.5-.2-.5-.5.1-.7l9.4-3.6c.4-.2.8 0 .6.6z"/></svg>'),
    ("x", "https://x.com/SailingMore",
     '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#ffffff" d="M18.9 2H22l-6.8 7.8L23 22h-6.3l-4.9-6.4L6.2 22H3l7.3-8.3L2.4 2h6.4l4.5 5.9L18.9 2zm-1.1 18h1.7L7.4 3.7H5.6L17.8 20z"/></svg>'),
]
# Telegram passe à gauche d'Instagram (Nicolas, 19/11/2026) : on échange les deux entrées.
_i = next(k for k, r in enumerate(RESEAUX) if r[0] == "instagram")
_t = next(k for k, r in enumerate(RESEAUX) if r[0] == "telegram")
RESEAUX[_i], RESEAUX[_t] = RESEAUX[_t], RESEAUX[_i]


# Les cinq grands chiffres — ceux des feuilles et du kit annonceur.
# bourse aux équipiers : 347 287 membres (Nicolas, 19/11/2026 ; pas dans chiffres-stats.json)
BOURSE_EQUIPIERS = 347_287

GRANDS = [("abonnes", "abonnes", False), ("vues", "vues", True), ("contenus", "contenus", False),
          ("vues_28j", "vues28", True), (BOURSE_EQUIPIERS, "bourse", False)]


def bloc_citation(i: int, c: dict) -> str:
    """La citation part dans la langue de son auteur ; le français et les autres suivent ensuite."""
    import re as _re
    m = _re.search(r"\d{4}", str(c.get("annee") or ""))
    annee = int(m.group()) if m else 0
    # Le siècle se déduit de la date, pas d'une étiquette recopiée à la main : une citation de 1900
    # classée XIXe prenait le fond du XXe (Nicolas, 19/11/2026).
    if annee:
        epoque = ("XVIIIe" if annee < 1800 else "XIXe" if annee < 1900 else
                  "XXe" if annee < 2000 else "XXIe")
    else:
        epoque = c.get("epoque", "XXe")
    classe, teinte = {
        "XVIIIe": ("ep18", "ep-t18"), "XIXe": ("ep19", "ep-t19"),
        "XXe": ("ep20", "ep-t20"), "XXIe": ("ep21", "ep-t21"),
    }.get(epoque, ("ep20", "ep-t20"))
    return (
        f'<figure class="citation {classe} {teinte}" data-idx="{i}">'
        f'<blockquote>{c["texte"]}</blockquote>'
        f'<figcaption><strong>{c["auteur"]}<i class="voix">{("— " + c["voix"]) if c.get("voix") else ""}</i></strong>'
        f'<span>{c["oeuvre"]}, {c["annee"]}</span>'
        f'<span class="siecle">{epoque}</span></figcaption>'
        f"</figure>"
    )


def citations_pour_js(cites: list[dict]) -> str:
    """Un seul objet : pour chaque citation, son texte dans chacune des six langues."""
    sortie = []
    for c in cites:
        textes = {c.get("langue", "fr"): c["texte"]}
        voix = {c.get("langue", "fr"): c.get("voix", "")}
        for langue, tr in (c.get("traductions") or {}).items():
            textes[langue] = tr.get("texte", c["texte"])
            voix[langue] = tr.get("voix", c.get("voix", ""))
        sortie.append({"textes": textes, "voix": voix, "defaut": c.get("langue", "fr")})
    return json.dumps(sortie, ensure_ascii=False)



def _nouvel_onglet(html: str) -> str:
    """Tout lien du site s'ouvre dans un nouvel onglet, pages internes comprises.

    Les ancres internes (#) en sont exclues : elles font défiler la page courante.
    Un lien qui porte déjà sa cible n'est pas retouché.
    """
    def rempl(m):
        tag = m.group(0)
        if "target=" in tag:
            return tag
        h = re.search(r'href="([^"]*)"', tag)
        if not h or h.group(1).startswith("#"):
            return tag
        return tag[:-1].rstrip() + ' target="_blank" rel="noopener">'
    return re.sub(r"<a\b[^>]*>", rempl, html)


def page(jeu: str, blocs: str = "", carte: str = "", mer: str = "", kit: str = "") -> str:
    global NUIT, NUIT2, EAU, CREME, GRIS, ROUGE, AMBRE, TOILE
    c = chiffres()
    cites = citations()
    textes = json.dumps(TEXTES, ensure_ascii=False)
    jours = json.dumps(MOIS, ensure_ascii=False)

    icones = "".join(
        (f'<a class="reseau" href="{lien}" target="_blank" rel="noopener" aria-label="{nom}">{svg}</a>'
         if lien else f'<span class="reseau" aria-label="{nom}">{svg}</span>')
        for nom, lien, svg in RESEAUX)

    # Le rouge ne va qu'aux vues (Nicolas, 19/11/2026) : abonnés, publications et bourse restent blancs.
    rouges = {("vues", "vues"), ("vues_28j", "vues28")}
    grands = "".join(
        f'<div class="grand{" rouge" if (cle, lab) in rouges else ""}">'
        f'<b>{("≈\u2009" if estime else "")}{espace(cle if isinstance(cle, int) else c.get(cle, 0))}</b>'
        f'<span data-t="{lab}">{lab}</span></div>'
        for cle, lab, estime in GRANDS)

    # La mer prend tout l'écran du héros : plus de cadre, le bateau navigue sur la page.
    heros = mer_louvoyage.hero(f"""
  <h1>Sailing<span>More</span></h1>
  <div class="filet"></div>
  <p class="accroche" data-t="accroche">Média <span class='rouge'>indépendant</span> de la voile et de la course au large, fait par des <span class='rouge'>passionnés</span>, pour des <span class='rouge'>passionnés</span>.</p>
  <a class="bouton bouton-hero" href="annonceurs.html" target="_blank" rel="noopener"><span data-t="hero_cta">Annoncer sur Sailing More</span> <span class="fleche" aria-hidden="true">→</span></a>""")

    bandeau = "".join(bloc_citation(i, x) for i, x in enumerate(cites))
    cites_js = citations_pour_js(cites)

    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sailing More — la voile et la course au large, en images</title>
<meta name="description" content="Sailing More, média indépendant de voile et de course au large : stories quotidiennes, vidéos et régates, sur Instagram et Facebook.">
<meta property="og:title" content="Sailing More">
<meta property="og:description" content="La voile et la course au large, en images.">
<meta property="og:url" content="https://sailingmore.fr/">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Sailing More">
<meta property="og:image" content="https://sailingmore.fr/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Sailing More — la voile et la course au large, en images">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://sailingmore.fr/og-image.jpg">
<meta name="theme-color" content="#08162a">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="icon-512.png" sizes="512x512" type="image/png">
<link rel="apple-touch-icon" href="icon-180.png">
<style>
  :root{{--nuit:{NUIT};--nuit2:{NUIT2};--eau:{EAU};--creme:{CREME};--gris:{GRIS};--rouge:{ROUGE};
    --ambre:{AMBRE};--toile:{TOILE}}}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{margin:0;background:#071c31;
    color:var(--creme);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    -webkit-font-smoothing:antialiased;overflow-x:hidden}}
  a{{color:inherit;text-decoration:none}}
  .entete{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;
    padding:.7rem 1.2rem;background:rgba(6,16,32,.72);backdrop-filter:blur(10px);
    border-bottom:1px solid rgba(126,214,214,.14)}}
  .entete .nom{{font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:.82rem;color:var(--gris)}}
  .langues{{display:flex;gap:.15rem;align-items:center}}
  .langues button{{background:none;border:0;color:var(--gris);font:inherit;font-size:.76rem;
    letter-spacing:.09em;text-transform:uppercase;padding:.28rem .45rem;border-radius:.35rem;cursor:pointer}}
  .langues button[aria-pressed="true"]{{color:var(--nuit);background:var(--eau);font-weight:700}}
  section{{padding:0 1.4rem}}
  .hero{{padding:8.6rem 0 6.5rem;max-width:52rem;margin:0 auto;text-align:center}}
  h1{{font-size:clamp(3rem,12vw,6.4rem);line-height:.88;letter-spacing:-.03em;margin:0;
    text-transform:uppercase;font-weight:800}}
  h1 span{{display:block;color:var(--toile)}}
  .filet{{width:5rem;height:2px;background:var(--rouge);margin:2.2rem auto 2.2rem}}
  .surtitre{{margin:0 auto .85rem;font-size:clamp(1.5rem,5.4vw,2.5rem);line-height:1.12;
    max-width:32rem;font-weight:800;letter-spacing:-.022em;color:#fff;text-wrap:balance}}
  .accroche{{font-size:clamp(1.12rem,2.6vw,1.34rem);line-height:1.45;margin:0 auto;max-width:32rem;
    color:#f2f7fb;font-weight:500;letter-spacing:.01em;text-wrap:balance}}
  .accroche .rouge{{color:#e23a3e}}
  .sous{{color:var(--gris);margin:0;font-size:.93rem}}
  /* Nicolas, 20/11/2026 : « les logos touchent les bords sur mobile, diminuez les icônes et gardez
     centré ». Cinq icônes à 2,6 rem et 2,6 rem d'écart font 374 px : plus que les 345 px utiles d'un
     écran de 390. L'écart et la taille suivent maintenant la largeur, et le groupe passe à la ligne
     plutôt que de déborder. */
  .reseaux-barre{{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;
    gap:clamp(.6rem,3.2vw,2.6rem);margin:0}}
  .reseaux-apres{{max-width:52rem;margin:0 auto 6.5rem;padding:0 1.4rem;text-align:center}}
  .reseau svg{{width:clamp(2.4rem,6.4vw,3.4rem);height:clamp(2.4rem,6.4vw,3.4rem);display:block;
    filter:drop-shadow(0 6px 14px rgba(0,0,0,.45));transition:transform .18s ease}}
  .reseau:hover svg{{transform:translateY(-4px) scale(1.07)}}
  .chiffres{{max-width:52rem;margin:0 auto 6.5rem}}
  h2{{font-size:.76rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gris);
    font-weight:600;margin:0 0 1.4rem;text-align:center}}
  .cadre{{border:1px solid rgba(126,214,214,.3);border-radius:1.4rem;
    background:radial-gradient(120% 160% at 50% 0%,rgba(126,214,214,.10),transparent 60%),
      linear-gradient(160deg,rgba(14,44,72,.8),rgba(8,22,40,.92));
    padding:2.6rem 1.2rem;display:grid;grid-template-columns:repeat(5,1fr);gap:1.3rem .6rem;
    text-align:center;box-shadow:0 20px 60px -30px rgba(126,214,214,.35)}}
  .grand b{{display:block;font-size:clamp(1.05rem,2vw,1.7rem);font-weight:800;letter-spacing:-.02em;
    font-variant-numeric:tabular-nums;color:var(--ambre);white-space:nowrap;
    text-shadow:0 0 22px rgba(232,176,75,.18)}}
  .grand span{{display:block;margin-top:.4rem;font-size:.7rem;line-height:1.25;color:var(--gris);
    letter-spacing:.05em;text-transform:uppercase}}
  .citations{{position:relative;margin:0 auto;padding:6.5rem 0 6.5rem}}
  .titre-cit{{margin:0 auto 2.7rem;text-align:center;font-size:.76rem;letter-spacing:.36em;
    text-transform:uppercase;font-weight:600;color:rgba(195,214,230,.85)}}
  .fenetre{{overflow:hidden;cursor:grab;touch-action:pan-y;-webkit-user-select:none;user-select:none;
    -webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);
    mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}}
  .fenetre:active{{cursor:grabbing}}
  .piste{{display:flex;width:max-content;will-change:transform;align-items:stretch}}
  .citation{{--acc:#8ad4d0;flex:none;width:min(29rem,85vw);margin:0;padding:2.1rem 2.5rem 1.2rem;
    position:relative;border-left:1px solid rgba(244,239,228,.075)}}
  .citation:first-child{{border-left:0}}
  .citation::before{{content:"“";position:absolute;left:.7rem;top:.1rem;font-size:3.4rem;
    line-height:1;color:var(--acc);opacity:.3;font-family:Georgia,"Times New Roman",serif}}
  .citation blockquote{{margin:0 0 1.2rem;line-height:1.45}}
  .citation figcaption{{font-size:.78rem;color:var(--gris);display:flex;flex-direction:column;gap:.2rem}}
  .citation figcaption strong{{display:block;color:var(--acc);font-weight:600;letter-spacing:.09em;
    text-transform:uppercase;font-size:.66rem}}
  .siecle{{display:block;margin-top:.55rem;font-size:.56rem;letter-spacing:.3em;
    text-transform:uppercase;color:rgba(159,179,200,.4)}}
  /* XVIIIe — le récit de voyage gravé : centré, italique, très aéré, filets fins */
  .ep18{{--acc:#e3c98f}}
  .ep18 blockquote{{font-family:"Iowan Old Style","Apple Garamond",Garamond,Georgia,serif;
    font-style:italic;font-size:1.06rem;line-height:1.85;letter-spacing:.03em;color:#efe1c4;
    text-align:center;padding:.2rem .4rem;font-variant-ligatures:common-ligatures;
    border-top:1px solid rgba(244,239,228,.22);border-bottom:1px solid rgba(244,239,228,.22)}}
  .ep18 blockquote::before{{content:"❧";display:block;color:var(--rouge);font-size:1rem;
    font-style:normal;margin-bottom:.7rem}}
  .ep18 figcaption{{text-align:center;align-items:center}}
  .ep18 figcaption strong{{font-variant:small-caps;text-transform:none;letter-spacing:.13em;
    font-size:.76rem;color:#e8d6b0;font-weight:600}}

  /* XIXe — le roman victorien : justifié, lettrine immense */
  .ep19{{--acc:#8ad4d0}}
  .ep19 blockquote{{font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;
    font-size:1.2rem;line-height:1.6;color:#f7f0e0;text-align:justify;hyphens:auto;
    padding-right:.7rem}}
  .ep19 blockquote::first-letter{{font-size:3.6rem;line-height:.84;float:left;color:var(--eau);
    font-weight:700;margin:.16rem .5rem 0 0;letter-spacing:0}}
  .ep19 figcaption strong{{font-variant:small-caps;text-transform:none;letter-spacing:.16em;
    font-size:.84rem}}

  /* XXe — le carnet de bord dactylographié : monospace, à gauche, jamais justifié */
  .ep20{{--acc:#a9c1d4}}
  .ep20 blockquote{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,"Courier New",monospace;
    font-size:.96rem;line-height:1.8;letter-spacing:-.015em;color:#dfeae0;text-align:left;
    padding:.3rem .2rem .2rem .9rem;border-left:1px dotted rgba(169,193,212,.55)}}
  .ep20 blockquote::after{{content:none}}
  .ep20 figcaption{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.72rem;
    letter-spacing:.02em}}
  .ep20 figcaption strong{{letter-spacing:.02em;text-transform:none;font-size:.74rem}}

  /* XXIe — l'enseigne : capitales serrées, très gras, sans ornement */
  .ep21{{--acc:#e23a3e}}
  .ep21 blockquote{{font-family:ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;
    font-size:1.16rem;font-weight:900;letter-spacing:.002em;text-transform:uppercase;
    line-height:1.28;color:#fff;padding:.1rem 0 .1rem 1rem;border-left:6px solid var(--acc)}}
  .ep21 figcaption strong{{letter-spacing:.14em;font-size:.68rem;color:#fff}}
  .concours{{max-width:52rem;margin:6.5rem auto}}
  .carte-jeu{{border:1px solid rgba(126,214,214,.24);border-radius:1.3rem;padding:3rem 2.4rem;
    background:var(--nuit2)}}
  .carte-jeu h3{{margin:0 0 .7rem;font-size:clamp(1.5rem,4.4vw,2.1rem);letter-spacing:-.02em;font-weight:800}}
  .carte-jeu p{{margin:0 0 2rem;color:var(--gris);line-height:1.55;max-width:34rem}}
  /* Nicolas, 20/11/2026 : « les boutons, un peu moins droits, qu'il y ait un rectangle, peut-être mettre
     les lignes ». Le bouton perd son aplat plein et devient un rectangle qui respire : un filet rouge
     à la place du fond, un mot en capitales espacées, et une flèche qui avance au survol. Coins
     presque vifs (3 px) pour rester dans la charte Signal B, où le rouge souligne plus qu'il ne remplit. */
  .bouton{{display:inline-flex;align-items:center;gap:.8rem;padding:1rem 1.7rem;border-radius:3px;
    font-weight:600;font-size:.74rem;line-height:1.1;letter-spacing:.17em;text-transform:uppercase;
    font-family:inherit;cursor:pointer;text-decoration:none;
    color:#fff;background:transparent;border:1px solid rgba(226,58,62,.85);
    position:relative;overflow:hidden;isolation:isolate;transition:color .22s ease,border-color .22s ease}}
  /* la ligne qui monte du bas au survol : le rouge remplit le rectangle, lentement */
  .bouton::before{{content:"";position:absolute;inset:0;z-index:-1;background:#e23a3e;
    transform:translateY(101%);transition:transform .28s cubic-bezier(.4,0,.2,1)}}
  .bouton:hover{{color:#fff;border-color:#e23a3e}}
  .bouton:hover::before{{transform:translateY(0)}}
  .bouton:focus-visible{{outline:2px solid #a8ecec;outline-offset:4px}}
  .bouton .fleche{{display:inline-block;transition:transform .22s ease}}
  .bouton:hover .fleche{{transform:translateX(4px)}}
  .cookies{{position:fixed;left:1rem;right:1rem;bottom:1rem;z-index:9;max-width:62rem;margin:0 auto;
    display:flex;gap:1rem;align-items:center;justify-content:space-between;flex-wrap:wrap;
    background:rgba(10,26,46,.97);border:1px solid rgba(126,214,214,.24);border-radius:.9rem;
    padding:.8rem 1rem;font-size:.82rem;line-height:1.4;color:var(--gris);
    box-shadow:0 14px 40px rgba(0,0,0,.4)}}
  .cookies p{{margin:0}}
  .cookies a{{color:var(--eau);text-decoration:none;margin-left:.35rem}}
  .cookies button{{background:var(--eau);color:#06202a;border:0;border-radius:.55rem;
    padding:.45rem .85rem;font:inherit;font-weight:600;cursor:pointer;white-space:nowrap}}
  body:has(#cookies:not([hidden])) footer{{padding-bottom:6rem}}
  footer{{border-top:1px solid rgba(126,214,214,.14);margin-top:6.5rem;padding:2.4rem 1.4rem 2.4rem;
    display:flex;flex-wrap:wrap;gap:.6rem 1.3rem;justify-content:center;color:var(--gris);font-size:.84rem}}
  footer a{{border-bottom:1px dotted rgba(159,179,200,.45)}}
  footer a:hover{{color:var(--eau)}}
  @media (max-width:760px){{
    .cadre{{grid-template-columns:repeat(2,1fr);padding:1.8rem 1rem}}
    .grand:last-child{{grid-column:span 2}}
  }}
  @media (max-width:620px){{
    .citation{{width:86vw;padding:0 1.2rem}}
    .hero{{padding:3.6rem 0 3.2rem}}
    .siecle{{top:-1.2rem;right:1rem}}
  }}
{site_blocks.CSS}
</style>
</head>
<body>
{mer}
<div class="contenu">
<header class="entete">
  <span class="nom">Sailing More</span>
  <div class="langues" id="langues" aria-label="Language">
    <button data-lang="auto" aria-pressed="true">Auto</button>
    {"".join(f'<button data-lang="{l}" aria-pressed="false">{l.upper()}</button>' for l in LANGUES)}
  </div>
</header>

{heros}

<section class="chiffres">
  <h2 data-t="chiffres">Sailing More en chiffres</h2>
  <div class="cadre">{grands}</div>
</section>

<section class="reseaux-apres">
  <div class="reseaux-barre">{icones}</div>
</section>

{kit}

{carte}

<section class="citations">
  <h2 class="titre-cit" data-t="citations">Ils l'ont dit avant nous</h2>
  <div class="fenetre" id="fenetre">
    <div class="piste" id="piste">{bandeau}</div>
  </div>
</section>

{blocs}

<section class="concours">
  <style>/* même dessin que le bouton du formulaire : carré, rouge, capitales espacées */
</style>
  <div class="carte-jeu">
    <h3 data-t="concours_titre">Le jeu concours</h3>
    <p data-t="concours_texte">Un jeu par mois pour un annonceur.</p>
    <a class="bouton" href="jeux.html"><span data-t="concours_bouton">Voir le jeu</span> <span class="fleche" aria-hidden="true">→</span></a>
  </div>
</section>


<div class="cookies" id="cookies" hidden>
  <p><span data-t="cookies_texte">Aucun cookie de mesure ni de publicité : ce site n'en dépose aucun.</span>
  <a href="confidentialite.html" data-t="cookies_lien">En savoir plus</a></p>
  <button id="cookies-ok" data-t="cookies_bouton">J'ai compris</button>
</div>

<footer>
  <a href="mentions-legales.html">Mentions légales · Legal notice</a>
  <a href="confidentialite.html">Confidentialité · Privacy</a>
  <a href="delete.html">Suppression de données · Data deletion</a>
  <span>© 2026 Sailing More</span>
</footer>
</div>

<script>

// Le formulaire annonceurs trouve son adresse au chargement, jamais dans le HTML.
document.querySelectorAll('form.kit-form').forEach(f => {{
  if(f.dataset.a && f.dataset.b) f.action = 'https://formsubmit.co/' + f.dataset.a + '@' + f.dataset.b;
}});
// Les liens « courriel » ne contiennent pas l'adresse en clair : on la recompose au clic.
document.querySelectorAll('a.courriel').forEach(a => a.addEventListener('click', e => {{
  e.preventDefault();
  const adresse = a.dataset.a + '@' + a.dataset.b;
  let lien = 'mailto:' + adresse;
  const params = [];
  if (a.dataset.sujet) params.push('subject=' + encodeURIComponent(a.dataset.sujet));
  if (a.dataset.corps) params.push('body=' + encodeURIComponent(a.dataset.corps));
  if (params.length) lien += '?' + params.join('&');
  window.location.href = lien;
}}));

// Le site ne dépose aucun cookie : le bandeau le dit une fois, puis se tait.
(function () {{
  const b = document.getElementById('cookies');
  if (!b) return;
  const lire = () => {{ try {{ return localStorage.getItem('sm-cookies'); }} catch (e) {{ return null; }} }};
  if (!lire()) b.hidden = false;
  document.getElementById('cookies-ok').addEventListener('click', () => {{
    try {{ localStorage.setItem('sm-cookies', '1'); }} catch (e) {{ /* navigation privée : on range quand même */ }}
    b.setAttribute('hidden', '');   // l'attribut, pas la propriété : aucun style ne peut le réafficher
    b.style.display = 'none';
  }});
}})();

const T = {textes};
const CITES = {cites_js};
const MOIS = {jours};
const JEU = "{jeu}";

function choisir() {{
  const force = localStorage.getItem("sm-langue");
  if (force && force !== "auto") return force;
  const pref = (navigator.languages || [navigator.language || "en"]).map(x => String(x).toLowerCase());
  for (const p of pref) {{
    const base = p.slice(0, 2);
    if (Object.keys(T).includes(base)) return base;
  }}
  return "en";
}}

function appliquer(l) {{
  const d = T[l];
  document.documentElement.lang = l;
  document.querySelectorAll("[data-t]").forEach(el => {{
    const cle = el.dataset.t;
    if (!d[cle]) return;
    let v = d[cle];
    if (cle === "concours_texte" && /^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(JEU)) {{
      const [a, m, j] = JEU.split("-");
      v = v.replace("{{date}}", `${{parseInt(j, 10)}} ${{(MOIS[l] || MOIS.en)[parseInt(m, 10) - 1]}} ${{a}}`);
    }}
    // L'accroche du héros porte deux mots en rouge : elle s'écrit en HTML, les autres en texte.
    if (cle === "accroche") el.innerHTML = v; else el.textContent = v;
  }});
  document.querySelectorAll("#langues button").forEach(b =>
  b.setAttribute("aria-pressed", String(b.dataset.lang === (localStorage.getItem("sm-langue") || "auto"))));

  /* les citations suivent la langue : original de l'auteur si on est dans sa langue, sinon traduction */
  document.querySelectorAll(".citation").forEach(fig => {{
  const q = CITES[Number(fig.dataset.idx)];
  if (!q) return;
  const txt = q.textes[l] || q.textes[q.defaut] || q.textes.fr;
  fig.querySelector("blockquote").textContent = txt;
  const v = fig.querySelector(".voix");
  if (v) {{
    const voix = q.voix[l] || q.voix[q.defaut] || "";
    v.textContent = voix ? "— " + voix : "";
  }}
  }});
  }}

document.querySelectorAll("#langues button").forEach(b => b.addEventListener("click", () => {{
  localStorage.setItem("sm-langue", b.dataset.lang);
  appliquer(b.dataset.lang === "auto" ? choisir() : b.dataset.lang);
}}));

/* Le bandeau avance seul ; on peut l'arrêter et le pousser au doigt ou à la souris. */
const piste = document.getElementById("piste");
const fenetre = document.getElementById("fenetre");
let x = 0, enMarche = true, glisse = false, depart = 0, vitesse = 0, precedent = 0;
const VITESSE = 11;

function tiers() {{ return piste.scrollWidth / 2 || 1; }}

function recaler() {{
  const t2 = tiers();
  if (x <= -t2) x += t2;
  if (x > 0) x -= t2;
}}

function avancer(t) {{
  if (!precedent) precedent = t;
  const dt = Math.min((t - precedent) / 1000, 0.05);
  precedent = t;
  if (glisse) {{
    /* la position vient du doigt */
  }} else if (Math.abs(vitesse) > 0.4) {{
    x += vitesse; vitesse *= 0.93;          /* l'élan se perd tout seul */
  }} else if (enMarche) {{
    vitesse = 0;
    x -= VITESSE * dt;
  }}
  recaler();
  piste.style.transform = `translate3d(${{x}}px,0,0)`;
  requestAnimationFrame(avancer);
}}
requestAnimationFrame(avancer);

fenetre.addEventListener("pointerdown", e => {{
  glisse = true; depart = e.clientX; vitesse = 0;
  try {{ fenetre.setPointerCapture(e.pointerId); }} catch (_) {{}}
}});
fenetre.addEventListener("pointermove", e => {{
  if (!glisse) return;
  const dx = e.clientX - depart;
  depart = e.clientX;
  x += dx;
  vitesse = dx * 0.8;                        /* l'élan du geste, gardé pour le lâcher */
  recaler();
}});
function lacher() {{
  if (!glisse) return;
  glisse = false;
  setTimeout(() => {{ enMarche = true; }}, 900);   /* le défilement reprend après une courte pause */
}}
fenetre.addEventListener("pointerup", lacher);
fenetre.addEventListener("pointercancel", lacher);
fenetre.addEventListener("mouseenter", () => {{ if (!glisse) enMarche = false; }});
fenetre.addEventListener("mouseleave", () => {{ if (!glisse) enMarche = true; }});

appliquer(choisir());
</script>
"""
    return _nouvel_onglet(html)



MOIS_FR = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre")
JOURS_FR = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")


def date_longue(iso: str) -> str:
    """« 2026-12-08 » → « mardi 8 décembre 2026 »."""
    d = datetime.date.fromisoformat(iso)
    return f"{JOURS_FR[d.weekday()]} {d.day} {MOIS_FR[d.month - 1]} {d.year}"


def page_jeu(jeu: str) -> str:
    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Le jeu concours — Sailing More</title>
<meta name="description" content="Le jeu concours Sailing More : six jours de stories, un tirage le dimanche.">
<style>
  body{{margin:0;background:#071c31;
    color:{CREME};font-family:system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
    line-height:1.6;-webkit-font-smoothing:antialiased}}
  .page{{max-width:40rem;margin:0 auto;padding:3.6rem 1.4rem 4rem}}
  a.retour{{color:{GRIS};text-decoration:none;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;
    font-weight:500}}
  h1{{font-size:clamp(2rem,7vw,3rem);line-height:1.04;margin:1.6rem 0 .4rem;letter-spacing:-.01em;
    font-weight:300}}
  h1 span{{color:{TOILE}}}
  .filet{{width:3.4rem;height:3px;background:{ROUGE};margin:1.2rem 0 1.8rem}}
  .page .filet{{width:3.4rem;height:3px;background:{ROUGE};margin:1.2rem 0 1.8rem}}
  p{{color:{CREME}}}
  .date{{font-size:.64rem;letter-spacing:.22em;text-transform:uppercase;color:{ROUGE};margin-top:2.8rem;
    font-weight:500}}
  ul{{color:{CREME};padding-left:1.1rem}}
  li{{margin:.5rem 0;color:{CREME}}}
  a{{color:#fff;text-decoration:none}}
  a.courriel{{text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);
    text-decoration-thickness:1px;text-underline-offset:3px}}
  a.courriel:hover{{text-decoration-color:#e23a3e}}
</style>
</head>
<body>
<div class="page">
  <a class="retour" href="index.html">← Sailing More</a>
  <h1>Le jeu <span>concours</span></h1>
  <div class="filet"></div>
  <p>Un jeu par mois, offert à un annonceur : une place dans nos stories du soir pendant six jours,
  du mardi au samedi, puis un tirage le dimanche à 18&nbsp;h.</p>
  <p class="date">Prochain départ : {date_longue(jeu)}</p>
  <ul>
    <li>Le tirage se fait au sort, parmi les participations reçues avant la clôture du samedi, 23&nbsp;h&nbsp;59.</li>
    <li>Le gagnant est annoncé le dimanche à 18&nbsp;h, en story.</li>
    <li>La participation est gratuite et sans obligation d'achat.</li>
  </ul>
  <p>Écrire à <a class="courriel" href="mailto:hello.sailingmore@gmail.com" data-a="hello.sailingmore" data-b="gmail.com">hello.sailingmore@gmail.com</a>.</p>
</div>
<script>
document.querySelectorAll('a.courriel').forEach(a => a.addEventListener('click', e => {{
  e.preventDefault();
  window.location.href = 'mailto:' + a.dataset.a + '@' + a.dataset.b;
}}));
</script>
</body>
</html>
"""
    return _nouvel_onglet(html)


def publier(fichiers: list[str]) -> None:
    """Envoie les fichiers au dépôt Pages. Rien ne part sans `--publier`."""
    import base64
    import urllib.error
    import urllib.request

    jeton = (RACINE / "credentials/github-token.txt").read_text().strip()
    depot = "sailingmorehere-netizen/sailingmore-legal"

    def appel(chemin: str, methode: str = "GET", corps: dict | None = None):
        r = urllib.request.Request(
            f"https://api.github.com{chemin}",
            data=json.dumps(corps).encode() if corps is not None else None,
            method=methode,
            headers={"Authorization": f"token {jeton}", "Accept": "application/vnd.github+json",
                     "User-Agent": "hermes"})
        try:
            with urllib.request.urlopen(r, timeout=45) as rep:
                return rep.status, json.loads(rep.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:300]

    for nom in fichiers:
        chemin = SORTIE / nom
        brut = chemin.read_bytes() if chemin.suffix.lower() in {".jpg", ".jpeg", ".png"} else chemin.read_text().encode()
        s, d = appel(f"/repos/{depot}/contents/{nom}")
        sha = d["sha"] if s == 200 and isinstance(d, dict) else None
        corps = {"message": f"accueil : {nom}",
                 "content": base64.b64encode(brut).decode()}
        if sha:
            corps["sha"] = sha
        s2, r2 = appel(f"/repos/{depot}/contents/{nom}", "PUT", corps)
        print(f"{nom} → {s2}" + ("" if s2 < 300 else f" {r2}"))


def publier_en_un_seul_envoi(fichiers: list[str], message: str = "accueil : mise à jour") -> None:
    """Un commit pour tous les fichiers, et non un par fichier.

    GitHub Pages accepte dix constructions par heure : six fichiers poussés un par un en déclenchent
    six, et les constructions se marchent dessus (« Page build failed »). Un seul commit = une seule.
    """
    import base64
    import urllib.error
    import urllib.request

    jeton = (RACINE / "credentials/github-token.txt").read_text().strip()
    depot = "sailingmorehere-netizen/sailingmore-legal"

    def appel(chemin: str, methode: str = "GET", corps: dict | None = None):
        r = urllib.request.Request(
            f"https://api.github.com{chemin}",
            data=json.dumps(corps).encode() if corps is not None else None,
            method=methode,
            headers={"Authorization": f"token {jeton}", "Accept": "application/vnd.github+json",
                     "User-Agent": "hermes"})
        try:
            with urllib.request.urlopen(r, timeout=60) as rep:
                return rep.status, json.loads(rep.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:300]

    s, ref = appel(f"/repos/{depot}/git/ref/heads/main")
    if s != 200:
        print("référence illisible", s, ref)
        return
    tete = ref["object"]["sha"]
    s, commit = appel(f"/repos/{depot}/git/commits/{tete}")
    if s != 200:
        print("commit illisible", s, commit)
        return

    arbre = []
    for nom in fichiers:
        chemin = SORTIE / nom
        brut = chemin.read_bytes() if chemin.suffix.lower() in {".jpg", ".jpeg", ".png"} else chemin.read_text().encode()
        s, blob = appel(f"/repos/{depot}/git/blobs", "POST",
                        {"content": base64.b64encode(brut).decode(), "encoding": "base64"})
        if s not in (200, 201):
            print(nom, "→ blob refusé", s, blob)
            return
        arbre.append({"path": nom, "mode": "100644", "type": "blob", "sha": blob["sha"]})

    s, nouveau = appel(f"/repos/{depot}/git/trees", "POST",
                       {"base_tree": commit["tree"]["sha"], "tree": arbre})
    if s not in (200, 201):
        print("arbre refusé", s, nouveau)
        return
    if nouveau["sha"] == commit["tree"]["sha"]:
        print("rien de neuf : aucun commit, aucune construction")
        return
    s, c = appel(f"/repos/{depot}/git/commits", "POST",
                 {"message": message, "tree": nouveau["sha"], "parents": [tete]})
    if s not in (200, 201):
        print("commit refusé", s, c)
        return
    s, maj = appel(f"/repos/{depot}/git/refs/heads/main", "PATCH", {"sha": c["sha"]})
    print("commit", c["sha"][:8], "→", s, "·", len(arbre), "fichiers en un seul envoi")



SITE = RACINE / "projets/sailingmore/site"


def page_accueil(jeu: str, blocs: str = "") -> str:
    """L'accueil habillé, écrit d'un seul endroit : maquette Signal B, carte, mer et héros compris.

    Deux constructions écrivaient l'accueil le 20/11/2026 : `sortir_le_site()` celle-ci, et
    `site_story_du_jour.py` un `page()` **nu**, sans maquette ni mer. Ce second chemin remettait donc
    en ligne l'ancien design (page de 112 Ko) et effaçait les réglages du héros à chaque passage de la
    story du soir — deux commits « site : story du 2026-11-19 » ont ainsi annulé, à 16 h 22 et 16 h 26,
    des retouches publiées une minute plus tôt. Les deux appellent maintenant cette fonction.
    """
    m = MAQUETTES["signal-B-cap"]
    depart = {k: globals()[k] for k in ("NUIT", "NUIT2", "EAU", "CREME", "GRIS", "ROUGE", "AMBRE", "TOILE")}
    try:
        globals().update(
            NUIT=m["nuit"], NUIT2=m["nuit2"], EAU=m["eau"], CREME=m["creme"],
            GRIS=m["gris"], ROUGE=m["rouge"], AMBRE=m["ambre"], TOILE=m["toile"])
        return habillage(page(jeu, blocs, site_blocks.html_carte(), mer_louvoyage.html_fond()), m)
    finally:
        globals().update(depart)


def sortir_le_site(jeu: str, blocs: str) -> int:
    """Écrit le site complet dans projets/sailingmore/site, habillé en Signal B « CAP ».

    Le dossier cache/rhum/site — celui que la publication envoie — n'est pas touché : rien ne part
    tant que Nicolas ne l'a pas demandé.
    """
    m = MAQUETTES["signal-B-cap"]
    depart = {k: globals()[k] for k in ("NUIT", "NUIT2", "EAU", "CREME", "GRIS", "ROUGE", "AMBRE", "TOILE")}
    try:
        globals().update(
            NUIT=m["nuit"], NUIT2=m["nuit2"], EAU=m["eau"], CREME=m["creme"],
            GRIS=m["gris"], ROUGE=m["rouge"], AMBRE=m["ambre"], TOILE=m["toile"])
        # Le formulaire ne revit pas ici : le 20/11/2026 l'accueil du site portait encore un
        # `.kit-bloc` avec son `form.kit-form` en anglais (« Advertisers »), revenu par cette ligne
        # quand le chemin `page()` l'avait perdu. Un seul CTA par page : le bouton du héros renvoie
        # vers `annonceurs.html`, qui porte le formulaire.
        accueil = page_accueil(jeu, blocs)
        concours = habillage(page_jeu(jeu), m)
        merci = habillage(page_merci(), m)
        annonceurs = habillage(page_annonceurs(), m)
    finally:
        globals().update(depart)

    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(accueil)
    (SITE / "jeux.html").write_text(concours)
    (SITE / "merci.html").write_text(merci)
    (SITE / "annonceurs.html").write_text(annonceurs)
    for nom in ("mentions-legales.html", "confidentialite.html", "delete.html"):
        if (SORTIE / nom).exists():
            (SITE / nom).write_text(habillage_pages_legales((SORTIE / nom).read_text()))
    for nom in ("carte-monde.png", "favicon-32.png", "icon-180.png", "icon-512.png", "og-image.jpg"):
        if (SORTIE / nom).exists():
            shutil.copy2(SORTIE / nom, SITE / nom)
    for dossier in ("stories", "reels", "drapeaux"):
        src = SORTIE / dossier
        if not src.exists():
            continue
        (SITE / dossier).mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, SITE / dossier / f.name)
    n = poser_mer_partout()
    print(f"mer posée sur {n} page(s) supplémentaire(s)")
    print(f"site écrit dans {SITE} — {len(list(SITE.rglob('*')))} entrées")
    return 0


DECOR_MER = (
    '<div class="mer-fond" id="cadre" aria-hidden="true">'
    '<canvas id="mer"></canvas><div class="mer-ombre"></div></div>')


def _sans_commandes(html: str) -> str:
    """Retire tous les conteneurs `.mer-fond-commandes`, quelle que soit leur version passée.

    Une simple recherche du bloc courant ne suffit pas : la version d'avant le 20/11/2026 portait
    l'heure et la réglette Auto, et ces chaînes-là traînaient encore dans `404.html` (22 conteneurs
    empilés) et dans une page légale (4). On compte donc les `<div` ouverts pour retirer chaque
    conteneur entier, du `<div class="mer-fond mer-fond-commandes">` jusqu'à sa fermeture.
    """
    ouvre = '<div class="mer-fond mer-fond-commandes">'
    while ouvre in html:
        i = html.index(ouvre)
        j, prof = i + len(ouvre), 1
        while prof:
            a, b = html.find("<div", j), html.find("</div>", j)
            if b < 0:
                return html
            if 0 <= a < b:
                prof, j = prof + 1, a + 4
            else:
                prof, j = prof - 1, b + 6
        html = html[:i] + html[j:]
    return html


def poser_mer_partout() -> int:
    """Le bateau en fond sur toutes les pages, posé par la construction elle-même.

    Nicolas, 19/11/2026 : « faut que le bateau en fond soit sur toutes les pages du site, que tu
    mettes à jour automatiquement ». Chaque page écrite sans la mer la reçoit ici — y compris les
    pages legales et la 404 — et une page ajoutée demain l'aura sans qu'on y pense.
    """
    # html_fond() apporte la scène complète (canvas, CSS, script) : le moteur a besoin de ses
    # commandes dans la page pour tourner. Sur les pages autres que l'accueil, on les masque et la
    # mer passe derrière le contenu.
    # Le tableau de bord (heure, auto, choix du bateau) suit sur toutes les pages : il est sorti de
    # la couche du fond, sinon le z-index -1 le rendrait invisible et incliquable (Nicolas,
    # 19/11/2026 : « le tableau de bord du bateau qu'on a en haut du site il doit se répéter sur
    # toutes les autres pages »). Seuls le cadran de vent, la légende et le bouton Rejouer restent
    # sur l'accueil : ils parlent de la navigation, pas de la page.
    bloc = (mer_louvoyage.html_fond(commandes=False)
            + '<style>.mer-fond{z-index:-1}'
              '.mer-fond .vent,.mer-fond .legende,.mer-fond .rejouer,.mer-fond .geste{display:none!important}'
              # Sur téléphone le tableau de bord occupe les 370 px de large : on réserve sa hauteur
              # au-dessus du contenu, sinon il écrit par-dessus le titre de la page.
              '</style>')
    # Le tableau de bord est en flux, juste après <body> : il pousse le titre vers le bas au lieu
    # de flotter par-dessus le texte quand on défile.
    reserve = '<div class="mer-fond mer-fond-commandes">' + mer_louvoyage.COMMANDES + '</div>'
    bloc = "<!--mer-debut-->" + bloc + "<!--mer-fin-->"
    fait = 0
    for page in sorted(SITE.glob("*.html")):
        html = page.read_text()
        if page.name == "index.html" and "<!--mer-debut-->" not in html:
            continue
        if "<!--mer-debut-->" in html:      # on remplace le bloc précédent, sans l'empiler
            html = html.split("<!--mer-debut-->")[0] + html.split("<!--mer-fin-->")[-1]
        # Les conteneurs du tableau de bord sont tous retirés, y compris ceux des versions passées :
        # l'ancienne regex `.*?</div></div>` s'arrêtait au premier `</div></div>` imbriqué et laissait
        # une moitié derrière elle — la construction suivante la recopiait, et le 20/11/2026
        # `404.html` en portait 22, `concours.html` 3.
        html = _sans_commandes(html)
        html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + reserve, html, count=1)
        if "</body>" in html:
            html = html.replace("</body>", bloc + "\n</body>", 1)
        else:
            html += bloc
        page.write_text(html)
        fait += 1
    return fait


# Le style commun des boutons (Nicolas, 20/11/2026) : les pages annexes — annonceurs, merci, jeux —
# construisent leur HTML à part et n'héritaient donc pas du `.bouton` de `page()`. Elles recevaient le
# bouton par défaut du navigateur, gris sur gris. Ce bloc est réutilisable tel quel.
CSS_BOUTON = """
  .bouton{display:inline-flex;align-items:center;gap:.8rem;padding:1rem 1.7rem;border-radius:3px;
    font-weight:600;font-size:.74rem;line-height:1.1;letter-spacing:.17em;text-transform:uppercase;
    font-family:inherit;cursor:pointer;text-decoration:none;
    color:#fff;background:transparent;border:1px solid rgba(226,58,62,.85);
    position:relative;overflow:hidden;isolation:isolate;transition:color .22s ease,border-color .22s ease}
  .bouton::before{content:"";position:absolute;inset:0;z-index:-1;background:#e23a3e;
    transform:translateY(101%);transition:transform .28s cubic-bezier(.4,0,.2,1)}
  .bouton:hover{color:#fff;border-color:#e23a3e}
  .bouton:hover::before{transform:translateY(0)}
  .bouton:focus-visible{outline:2px solid #a8ecec;outline-offset:4px}
  .bouton .fleche{display:inline-block;transition:transform .22s ease}
  .bouton:hover .fleche{transform:translateX(4px)}
"""

CSS_LEGAL = """<style>
  /* Les pages annexes suivent la charte du site (projets/sailingmore/CHARTE-GRAPHIQUE.md) :
     le marine écrit, le rouge désigne, filets de 1 px, titres fins, aucun arrondi. */
  *{box-sizing:border-box}
  body{margin:0;background:#071c31;
    color:#eef3f7;font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
    line-height:1.7;-webkit-font-smoothing:antialiased}
  .page{max-width:44rem;margin:0 auto;padding:3.6rem 1.4rem 5rem}
  a.retour{color:#9db2c6;text-decoration:none;font-size:.64rem;letter-spacing:.14em;
    text-transform:uppercase;font-weight:500}
  a.retour:hover{color:#fff}
  h1{font-size:clamp(1.9rem,6vw,2.7rem);line-height:1.04;margin:1.6rem 0 0;letter-spacing:-.01em;
    color:#fff;font-weight:300;text-transform:uppercase}
  h1::after{content:"";display:block;width:3.4rem;height:3px;background:#e23a3e;margin:1.3rem 0 2.4rem}
  h2{font-size:.64rem;margin:2.8rem 0 .9rem;letter-spacing:.22em;text-transform:uppercase;
    color:#9db2c6;font-weight:500;padding-top:1.1rem;border-top:1px solid rgba(226,58,62,.22)}
  p,li{color:#eef3f7;font-size:.95rem;line-height:1.7}
  ul,ol{padding-left:1.1rem}
  small{color:#9db2c6;font-size:.78rem}
  a{color:#fff;text-decoration:underline;text-decoration-color:rgba(226,58,62,.7);
    text-decoration-thickness:1px;text-underline-offset:3px}
  a:hover{text-decoration-color:#e23a3e}
  hr{border:0;border-top:1px solid rgba(255,255,255,.09);margin:3rem 0}
  table{width:100%;border-collapse:collapse;font-size:.9rem}
  th,td{text-align:left;padding:.6rem 0;border-bottom:1px solid rgba(255,255,255,.09);vertical-align:top}
  th{color:#9db2c6;font-weight:500;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase}
  strong{color:#fff;font-weight:500}
</style>"""


def habillage_pages_legales(html: str) -> str:
    """Les pages légales passent au même marine que le site, sans toucher au texte.

    La passe est idempotente : elle déshabille d'abord ce qu'une construction précédente a posé,
    puis réhabille une fois. Sans cela le lien de retour se recopiait à chaque construction
    (« ← Sailing More » cinq fois en tête des mentions légales, 19/11/2026).
    """
    debut = html.find("<body>")
    if debut < 0:
        return html
    corps = html[debut + len("<body>"):]
    tete = html[:debut]
    tete = re.sub(r"<style>.*?</style>", CSS_LEGAL, tete, count=1, flags=re.S)
    corps = corps.replace("</body>", "").replace("</html>", "")
    corps = re.sub(r'<a class="retour"[^>]*>[^<]*</a>', "", corps)
    corps = corps.replace('<div class="page">', "")
    corps = corps.rstrip()
    while corps.endswith("</div>"):
        corps = corps[: -len("</div>")].rstrip()
    corps = ('\n<div class="page">\n<a class="retour" href="index.html">← Sailing More</a>\n'
             + corps.strip() + "\n</div>\n")
    return tete + "<body>" + corps + "</body>\n</html>\n"


def page_annonceurs() -> str:
    """La page que le bouton du héros ouvre dans un nouvel onglet : le formulaire seul, sans détour."""
    return ("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Annonceurs — Sailing More</title>"
            "<meta name=\"description\" content=\"Le bloc de lancement de Sailing More : un mois, moitie "
            "jeu concours et moitie publications, 500 EUR, rapport de portee sous 72 h.\">"
            + CSS_LEGAL.replace("</style>", site_blocks.CSS + CSS_BOUTON + "</style>"
                              + "<style>.page.page-annonceurs{max-width:64rem}"
                              # Nicolas, 20/11/2026 : les espaces de cette page sautaient de 15 px à
                              # 54 px. Un seul écart entre deux blocs : 1,6 rem, 3,2 avant la carte.
                              + ".page.page-annonceurs>*+*{margin-top:1.6rem}"
                              + ".page.page-annonceurs>.ann-carte{margin-top:3.2rem}"
                              + ".ann-carte{font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;"
                                "color:#9db2c6;margin:3.4rem 0 1rem}</style>") +
            "</head><body><div class=\"page page-annonceurs\"><a class=\"retour\" href=\"index.html\">← Sailing More</a>"
            "<h1 data-t=\"kit_titre\">Annonceurs</h1>"
            "<p data-t=\"ann_intro\">Sailing More parle aux voileux chaque soir. Un bloc de lancement, "
            "un mois, moitié jeu concours et moitié publications : 500 €.</p>"
            "<p class=\"kit-preuve\" data-t=\"kit_preuve\">Ces chiffres viennent de Meta, relevés ce "
            "mois-ci.</p>"
            "<div class=\"carte-kit\">"
            + site_blocks.tarifs() +
            site_blocks.formulaire_kit() +
            "</div>"
            "<p class=\"ann-carte\" data-t=\"ann_carte\">Où sont les lecteurs</p>"
            + site_blocks.html_carte() +
            "</div></body></html>\n")


def page_merci() -> str:
    """La page où FormSubmit renvoie après l'envoi du formulaire annonceurs."""
    return ("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Merci — Sailing More</title>"
            "<meta name=\"robots\" content=\"noindex\">"
            + CSS_LEGAL +
            "</head><body><div class=\"page\"><a class=\"retour\" href=\"index.html\">← Sailing More</a>"
            "<h1>Merci.</h1>"
            "<p>Votre demande est partie. Je réponds moi-même, sous 24 heures, du lundi au vendredi.</p>"
            "<p>En attendant, la grille est là : trois packs, du post seul au trimestre partenaire.</p>"
            "<p><a href=\"index.html#annonceurs\">Revenir à la page des annonceurs</a></p>"
            "</div></body></html>\n")


def main() -> int:
    jeu = prochain_jeu() or "2026-12-08"
    SORTIE.mkdir(parents=True, exist_ok=True)
    blocs = "".join([
        site_blocks.html_stories(site_blocks.stories(SORTIE)),
        # Ni les reels ni le rappel annonceurs ne sont sur l'accueil (Nicolas, 19/11/2026) : le
        # bouton du héros ouvre la page du formulaire, le reste de la page parle aux marins.
    ])
    # la carte passe après les chiffres, pas au milieu des stories (Nicolas, 19/11/2026)
    carte = site_blocks.html_carte()
    if "--site" in sys.argv:
        return sortir_le_site(jeu, blocs)
    (SORTIE / "index.html").write_text(page(jeu, blocs, carte, kit=site_blocks.html_kit()))
    (SORTIE / "jeux.html").write_text(page_jeu(jeu))
    print(f"écrit {SORTIE / 'index.html'} · {SORTIE / 'jeux.html'}")
    print(f"chiffres au {chiffres().get('maj')} · prochain jeu {jeu} · {len(citations())} citations")
    if "--publier" in sys.argv:
        images = [n for n in ("og-image.jpg", "icon-512.png", "icon-180.png", "favicon-32.png")
                  if (SORTIE / n).exists()]
        medias = sorted(str(p.relative_to(SORTIE)) for dossier in ("stories", "reels")
                        for p in (SORTIE / dossier).glob("*.jpg"))
        if (SORTIE / "carte-monde.png").exists():
            medias.append("carte-monde.png")
        pages = [n for n in ("mentions-legales.html", "confidentialite.html", "delete.html")
                 if (SORTIE / n).exists()]
        publier_en_un_seul_envoi(["index.html", "jeux.html", *pages, *images, *medias])
    return 0


# ---------------------------------------------------------------------------
# Habillage des maquettes : trois directions, même contenu, on ne touche qu'à
# la feuille de style. Rien n'est publié, la maquette sort dans maquettes/.
# ---------------------------------------------------------------------------
SIGNAL = dict(nuit="#07080a", nuit2="#101114", eau="#e8352e", creme="#eef1f4",
              gris="#8d9298", rouge="#e8352e", ambre="#eef1f4", toile="#ffffff")

CORRECTIFS = """

  /* ---- le cordage respire : la tresse glisse d'une tuile pile, lentement, chaque ligne à son rythme ---- */
  @keyframes corde168{from{background-position-x:0}to{background-position-x:168px}}
  @keyframes corde126{from{background-position-x:0}to{background-position-x:126px}}
  @keyframes corde220{from{background-position-x:0}to{background-position-x:220px}}
  @keyframes corde240{from{background-position-x:0}to{background-position-x:240px}}
  .entete{animation:corde168 110s linear infinite}
  .citation blockquote{animation:corde126 132s linear infinite}
  
  footer{animation:corde168 121s linear infinite;animation-delay:-23s}
  .cookies{animation:corde220 143s linear infinite;animation-delay:-61s}
  /* socle commun aux déclinaisons : grille tenue, citations de même hauteur */
  .chiffres{max-width:64rem}
  /* les blocs du site gardent leur géométrie ; chaque direction dessine ses cartes elle-même,
     sinon le socle repeint par-dessus et les cartes ne ressemblent plus au cadre des chiffres */
  .carte-kit p,.carte-jeu p{color:rgba(238,241,244,.72)}
  .planisphere{border-color:rgba(255,255,255,.14);background:rgba(15,36,56,.6)}

  .reel{border-color:rgba(255,255,255,.14);background:#0b0c0e}
  .pt-v i{box-shadow:none}
  .cadre{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;padding:1.4rem 0}
  .grand{min-width:0}
  .grand b{font-size:clamp(1.05rem,1.72vw,2.05rem);letter-spacing:-.03em;white-space:nowrap}
  .chiffres{margin-bottom:3.2rem}
  .citation{display:flex;flex-direction:column;min-height:15rem;overflow:hidden}
  .citation blockquote{overflow-wrap:break-word;hyphens:none;text-align:left}
  .ep19 blockquote::first-letter{font-size:inherit;float:none;margin:0;color:inherit;
    line-height:inherit;font-weight:inherit}
  .citation blockquote{flex:1 1 auto}
  .citation::before{content:none}
  .ep18 blockquote::before{content:none}
  @media(max-width:820px){
    .cadre{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:1.4rem}
    .citation{min-height:0}
  }
"""


# Trois mixes bleu marine + rouge : la mer comme fond, le rouge comme signal.
MARINE = dict(nuit="#0a1a2b", nuit2="#0f2438", eau="#e23a3e", creme="#eef3f7",
              gris="#9db2c6", rouge="#e23a3e", ambre="#eef3f7", toile="#ffffff")

MAQUETTES = {
    # A — MARÉE HAUTE : deux voix, marine profond pour la page, rouge pour le signal.
    "signal-A-maree-haute": dict(MARINE, nom="MARÉE HAUTE",
        corps="system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif", extra="""
  body{background:#0a1a2b}
  .entete{background:rgba(10,26,43,.94);border-bottom:1px solid rgba(255,255,255,.12)}
  h1{font-weight:900;letter-spacing:-.045em;line-height:.88;color:#fff}
  h1 span{color:#e23a3e}
  .filet{background:#e23a3e;width:3.4rem;height:3px}
  .surtitre{font-weight:900;letter-spacing:-.03em;text-transform:uppercase;color:#eef3f7}
  h2{color:#9db2c6;font-weight:700;letter-spacing:.3em}
  .cadre{border-radius:0;border:1px solid rgba(226,58,62,.4);background:rgba(15,36,56,.6);
    box-shadow:none;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;padding:0}
  .grand{padding:1.5rem 1.1rem;border-left:1px solid rgba(255,255,255,.12)}
  .grand:first-child{border-left:0}
  .grand b{color:#fff;font-weight:800;letter-spacing:-.03em;text-shadow:none}
  .grand span{color:#9db2c6;letter-spacing:.14em;font-size:.6rem}
  .titre-cit{color:#9db2c6;letter-spacing:.3em}
  .citation{--acc:#e23a3e;border-left:0;border-top:1px solid rgba(255,255,255,.14);
    background:rgba(15,36,56,.45)}
  .ep18 blockquote{color:#b8c9d8} .ep19 blockquote{color:#d6e2ec} .ep20 blockquote{color:#fff}
  .ep21 blockquote{color:#e23a3e} .ep21{--acc:#e23a3e}
  .citation figcaption strong{color:#fff}
  .citation figcaption span{color:#9db2c6}
  .siecle{color:rgba(157,178,198,.8);letter-spacing:.24em}
  .stories h2,.reels h2,.monde h2{color:#fff;text-transform:uppercase;letter-spacing:-.02em;
    white-space:normal;font-weight:900}
  .planisphere{border-radius:0;border-color:rgba(226,58,62,.35);background:#081521}
  .pt-v i{background:#e23a3e;box-shadow:0 0 10px 1px rgba(226,58,62,.5)}
  .carte-kit{border-radius:0;border-color:rgba(255,255,255,.18);background:rgba(15,36,56,.6)}
  .carte-jeu{background:rgba(15,36,56,.6);border-color:rgba(255,255,255,.18);border-radius:0}
  .reel{border-radius:0;border-color:rgba(255,255,255,.16)}
  footer{color:#9db2c6}
  .cookies{background:rgba(8,21,33,.98);border:1px solid rgba(226,58,62,.35);border-radius:0}
  .cookies button{background:#e23a3e;color:#fff;border-radius:0}
"""),

    # B — CAP : le rouge ne parle plus, il désigne. Le marine seul écrit.
    "signal-B-cap": dict(MARINE, nom="CAP",
        corps="system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif", extra="""
  body{background:#0a1a2b}
  .entete{background:rgba(10,26,43,.94);border-bottom:1px solid rgba(226,58,62,.5)}
  h1{font-weight:300;letter-spacing:-.01em;line-height:.94;color:#fff}
  h1 span{font-weight:300;color:#fff;letter-spacing:-.05em}
  .filet{background:linear-gradient(90deg,#e23a3e 0 34%,rgba(255,255,255,.18) 34% 100%);
    width:100%;max-width:16rem;height:1px}
  .surtitre{font-weight:300;letter-spacing:-.01em;color:#dbe6ef}
  h2{color:#9db2c6;font-weight:500;letter-spacing:.22em;font-size:.64rem}
  .cadre{border-radius:0;border:0;border-top:1px solid rgba(226,58,62,.45);border-bottom:1px solid rgba(255,255,255,.16);
    background:transparent;box-shadow:none;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));
    gap:0;padding:1.6rem 0}
  .grand{padding:0 1.1rem;border-left:1px solid rgba(255,255,255,.1)}
  .grand:first-child{border-left:0;padding-left:0}
  .grand b{color:#fff;font-weight:300;letter-spacing:-.02em;text-shadow:none}
  .grand:first-child b{color:#fff;font-weight:300}
  .grand span{color:#9db2c6;letter-spacing:.14em;font-size:.58rem}
  .titre-cit{color:#9db2c6;letter-spacing:.22em;font-size:.64rem}
  .citation{--acc:#e23a3e;border-left:0;border-top:1px solid rgba(255,255,255,.14);
    background:transparent;width:min(26rem,86vw)}
  .citation blockquote{color:#dbe6ef}
  .ep22{}
  .ep21 blockquote{color:#fff;font-weight:700}
  .citation figcaption strong{color:#fff} .citation figcaption span{color:#9db2c6}
  .siecle{color:#e23a3e;letter-spacing:.2em;font-size:.55rem}
  .stories h2,.reels h2,.monde h2{color:#fff;font-weight:300;letter-spacing:.02em;
    text-transform:uppercase;white-space:normal}
  .planisphere{border-radius:0;border-color:rgba(255,255,255,.14);background:#081521}
  .pt-v i{background:#e23a3e;box-shadow:none}
  .carte-kit{border-radius:0;border:0;border-top:1px solid rgba(226,58,62,.22);
    border-bottom:1px solid rgba(255,255,255,.09);background:transparent;box-shadow:none}
  .carte-jeu{background:transparent;border:0;border-top:1px solid rgba(226,58,62,.22);
    border-bottom:1px solid rgba(255,255,255,.09);border-radius:0;box-shadow:none}
  /* ---- les boutons deviennent des filets : un mot, un trait rouge dessous (Nicolas, 19/11/2026) ----
     « les boutons en dessous, essaye qu'ils soient un peu comme tes barres » */
  .reel{border-radius:0;border-color:rgba(255,255,255,.14);background:#0a1a2b}
  .reel img{background:#0a1a2b}
  .carte-reel{background:transparent}
  footer{color:#9db2c6}
  .cookies{background:rgba(8,21,33,.98);border:1px solid rgba(255,255,255,.18);border-radius:0}
  .cookies button{background:#e23a3e;color:#fff;border-radius:0}

  /* ---- en-tête sur téléphone : le nom tient sur une ligne, les langues respirent ---- */
  @media(max-width:600px){
    .entete{padding:.55rem .7rem;gap:.4rem}
    .entete .nom{font-size:.6rem;letter-spacing:.1em;white-space:nowrap}
    .langues{gap:0}
    .langues button{font-size:.56rem;padding:.15rem .26rem;letter-spacing:0}
    .langues button[aria-pressed="true"]{padding:.15rem .34rem}
  }

  /* ---- les traits droits : ni vague ni cordage (19/11/2026) ----
     Les douze lignes décoratives ont été retirées à la demande de Nicolas. Ce qui reste : les filets
     du cadre CAP d'origine — rouge au-dessus des chiffres, blanc cassé en dessous, un trait plein. */
  /* Nicolas, 20/11/2026 : « la barre doit être pile entre les deux, à la même distance ». Un interligne
     ne se mesure pas à l'œil : le titre est une colonne (`flex-direction:column`) avec un écart fixe de
     `.72rem`, et la barre se pose au milieu exact de cet écart (`top:calc(-.72rem / 2 - 1.5px)`, 1,5 px
     étant la moitié de ses 3 px). Distance égale par construction, quelle que soit la taille de police. */
  .hero h1{display:flex;flex-direction:column;align-items:center;row-gap:.72rem;
    margin-bottom:5rem;line-height:1.16;letter-spacing:-.035em}
  .hero .filet{display:none}
  .cadre{margin-top:3.2rem}
  .citation{padding-top:1.4rem}
  /* le filet fin de l'époque, hérité : on le retire, il est remplacé par la teinte du siècle */
  .ep20 blockquote{border-left:0}
  .ep20 blockquote::before{content:none}
  .citation blockquote{padding-bottom:.9rem}
  /* le fond suit le siècle : le bleu s'installe et se réchauffe au fil des années (19/11/2026).
     En 1771 presque rien, en 1840 un filet de brume, en 1906 le panneau, en 2026 le bleu de la nuit. */
  .citation:has(> blockquote){} 
  .citation>blockquote{padding:1.1rem 1.3rem}

  /* ---- chaque siècle a son fond ET sa typographie (Nicolas, 19/11/2026) : quatre matières, pas
     quatre teintes du même bleu. On doit reconnaître l'époque sans lire la date. ---- */
  .citation>blockquote{padding:1.1rem 1.3rem;border:0}

  /* XVIIIe — la page d'un livre ancien : papier verge, encre sépia, italique centrée, double filet */
  .citation.ep-t18>blockquote{
    background:
      repeating-linear-gradient(90deg,rgba(120,97,60,.05) 0 1px,transparent 1px 8px),
      linear-gradient(180deg,#e9dfc6,#e0d2b2);
    color:#3b2d17;font-family:"Iowan Old Style","Palatino Linotype",Palatino,Garamond,Georgia,serif;
    font-style:italic;font-size:1.02rem;line-height:1.82;letter-spacing:.01em;text-align:center;
    box-shadow:inset 0 0 0 1px rgba(92,71,38,.42),inset 0 0 0 4px #e9dfc6,inset 0 0 0 5px rgba(92,71,38,.26)}
  .citation.ep-t18>blockquote::before{content:"❧";display:block;color:#8f3a2c;font-style:normal;
    font-size:1.15rem;line-height:1;margin:0 0 .55rem}
  .citation.ep-t18 figcaption strong{color:#e8d6b0}

  /* XIXe — le livre relié du XIXe : papier ivoire, encre noire, lettrine rouge, filets d'encre */
  .citation.ep-t19>blockquote{
    background:linear-gradient(180deg,#f4eddc,#ece2cb);
    color:#1b1b17;font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;
    font-size:1.06rem;line-height:1.72;text-align:left;
    border-top:1px solid rgba(27,27,23,.6);border-bottom:1px solid rgba(27,27,23,.6);
    box-shadow:inset 0 4px 0 -3px rgba(27,27,23,.45),inset 0 -4px 0 -3px rgba(27,27,23,.45)}
  .citation.ep-t19>blockquote::first-letter{font-size:3.2rem;line-height:.78;float:left;
    color:#8c2b22;font-weight:700;margin:.12rem .5rem 0 0}
  .citation.ep-t19 figcaption strong{color:#e6dcc0}

  /* XXe — la feuille dactylographiée : papier bistre, encre bleu-noir, marge rouge, monospace */
  .citation.ep-t20>blockquote{
    background:
      linear-gradient(90deg,transparent 24px,rgba(168,58,48,.45) 24px 25px,transparent 25px),
      linear-gradient(180deg,#f0ebdf,#e4ddcd);
    color:#202a3a;font-family:ui-monospace,"Courier New",Courier,monospace;
    font-size:.9rem;line-height:1.75;letter-spacing:-.005em;text-align:left;padding-left:2.5rem;
    box-shadow:inset 0 0 0 1px rgba(60,58,48,.22),0 1px 0 rgba(0,0,0,.18)}
  .citation.ep-t20 figcaption{font-family:ui-monospace,"Courier New",monospace;color:#93a3ad}
  .citation.ep-t20 figcaption strong{color:#e2e8ec}

  /* XXIe — l'enseigne : aplat rouge plein, capitales serrées, blanc pur */
  .citation.ep-t21>blockquote{
    background:#e23a3e;color:#fff;
    font-family:ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;
    font-size:1rem;font-weight:800;letter-spacing:.005em;text-transform:uppercase;
    line-height:1.34;text-align:left;padding:1.25rem 1.35rem;
    box-shadow:inset 0 0 0 1px rgba(255,255,255,.22)}
  .citation.ep-t21 figcaption strong{color:#fff}

  /* ---- le filet au-dessus de chaque citation : plus fin, et la citation posée dessous (19/11/2026) ----
     Nicolas : « mettre un peu moins gras, et mettre une barre rouge, la barre rouge là qui est sur le MORE
     tout le long entre ces lignes, mais en plus fin ». La barre rouge du MORE court donc sur toute la
     largeur de l'écran, en 1 px, et chaque citation s'ouvre sur un filet fin qui reprend la teinte de son siècle. */
  .fenetre{padding-left:calc(max(1.2rem,(100vw - 64rem)/2))}
  .fenetre::before,.fenetre::after{content:"";position:absolute;left:0;right:0;height:1px;z-index:2;pointer-events:none}
  .fenetre::before{top:0;background:#e23a3e}
  .fenetre::after{bottom:0;background:rgba(255,255,255,.16)}
  .citation{border-top:1px solid rgba(255,255,255,.16);position:relative}
  .citation::after{content:"";position:absolute;left:0;right:0;top:-1px;height:1px;
    background:var(--teinte,rgba(255,255,255,.3))}

  /* ---- le fond change avec le siècle de la citation ---- */
  .ep-t18{--teinte:#5f7f9c}
  .ep-t19{--teinte:#9db2c6}
  .ep-t20{--teinte:#e23a3e}
  .ep-t21{--teinte:#8fd3e8}
  .titre-cit{
    color:#9db2c6;font-size:.64rem;letter-spacing:.22em;font-weight:500;text-transform:uppercase;
    max-width:64rem;margin:0 auto 1.5rem;padding:0 1.2rem;display:flex;align-items:center;gap:.9rem}
  .titre-cit::after{content:"";flex:1 1 auto;height:1px;
    background:linear-gradient(90deg,rgba(226,58,62,.75),rgba(226,58,62,0))}

  /* ---- les chiffres : le rouge sur les vues, le blanc sur les abonnés ---- */
  .grand b{font-weight:300;color:#fff}
  .grand.rouge b{color:#e23a3e;font-weight:500}

  /* ---- annonceurs et jeu concours prennent le cadre des chiffres ---- */
  /* le cadre des chiffres, repris tel quel : filet rouge en haut, filet blanc en bas, et l'échelle de la
     grille au lieu de la largeur que le bloc avait */
  section.concours{width:min(100% - 2.4rem,64rem) !important;margin:5.5rem auto}
  /* le cadre des chiffres : filet rouge franc en haut, filet clair en bas, la même colonne que la grille */
  section.concours,.kit-bloc{width:min(100% - 2.4rem,64rem) !important;margin:6.5rem auto !important;
    /* le même rythme que l'accueil vaut aussi pour le jeu et les pages légales */
    padding:0 !important;max-width:none !important}
  .kit-bloc .carte-kit,.carte-jeu{width:100%}
  .carte-kit,.carte-jeu{border-radius:0;border:0;border-top:1px solid rgba(226,58,62,.22);
    border-bottom:1px solid rgba(255,255,255,.09);background:transparent;box-shadow:none;
    padding:1.9rem 2rem;margin:0;width:auto}
  .kit-bloc{width:min(100% - 2.4rem,64rem) !important;margin:5.5rem auto !important;padding:0 !important;max-width:none !important}
  .kit-bloc .carte-kit{width:100%}
  .carte-kit h3,.carte-jeu h3{font-weight:300;letter-spacing:-.015em;font-size:clamp(1.5rem,3.4vw,2rem)}
  .titre-idee{display:flex;align-items:center;gap:.9rem;margin:0 0 1.5rem;padding:0 .2rem;
    color:#9db2c6;font-size:.58rem;letter-spacing:.2em;text-transform:uppercase}
  .titre-idee::after{content:"";flex:1 1 auto;height:1px;
    background:linear-gradient(90deg,rgba(226,58,62,.6),rgba(226,58,62,0))}

  /* ---- les reels un peu plus petits : ils prenaient toute la largeur ---- */
  .reels .trois{max-width:36rem;margin:0 auto;gap:.7rem}

  /* ---- la barre rouge passe entre SAILING et MORE, à la largeur du mot MORE (Nicolas, 19/11/2026) ----
     Le trait ne traverse plus la page : c'est la main courante du bloc, elle s'arrête au bord du MORE.
     Réglé sur .hero seulement : ailleurs (page du jeu, pages légales) un h1 porte un mot, pas un titre
     en deux lignes, et la barre y tombait au milieu du texte. */
  html{overflow-x:hidden}
  /* Nicolas, 20/11/2026 : « la barre doit être pile entre les deux, à la même distance ». Un interligne
     ne se mesure pas à l'œil : le titre est une colonne (`flex-direction:column`) avec un écart fixe de
     `.72rem`, et la barre se pose au milieu exact de cet écart (`top:calc(-.72rem / 2 - 1.5px)`, 1,5 px
     étant la moitié de ses 3 px). Distance égale par construction, quelle que soit la taille de police. */
  .hero h1{display:flex;flex-direction:column;align-items:center;row-gap:.72rem;
    margin-bottom:5rem;line-height:1.16;letter-spacing:-.035em}
  .hero h1 span{box-shadow:none;position:relative;display:block;width:max-content;max-width:100%;
    margin-inline:auto}
  /* Nicolas, 20/11/2026 (deux fois) : « la ligne rouge doit être entre sailing et more ». Ni un
     soulignement du mot, ni un trait dans les lettres : un séparateur court, centré, posé dans le blanc
     qui sépare les deux lignes. `top:-.30em` le met dans l'interligne, `left:50%` + `translateX(-50%)` le
     centre sur le titre — MORE étant centré lui aussi, le trait tombe juste entre les deux mots. */
  /* Le trait est centré sur l'écart de `.72rem` : moitié de l'écart, moins la moitié de ses 3 px, plus
     `0,95 px` de compensation — l'espace au-dessus d'une capitale n'est pas l'espace sous elle, et la
     mesure à l'écran donne 4,1 px de chaque côté à 48 px de corps, 4,1 et 4,2 à 102 px. Sans ce
     correctif, la barre penche vers MORE (5,2 au-dessus, 3,0 en dessous). */
  .hero h1 span::before{content:"";position:absolute;left:50%;transform:translateX(-50%);
    top:calc(-.72rem / 2 - 2.45px);width:5rem;height:3px;background:#e23a3e}
  .hero h1 span::after{content:none}
  /* les deux filets du cadre des chiffres étaient trop marqués : ils s'effacent presque */
  .cadre{border-top-color:rgba(226,58,62,.22) !important;border-bottom-color:rgba(255,255,255,.09) !important}
""",
        js=""""""),

    # C — BAIL : le rouge devient un aplat plein à côté du marine, deux blocs francs.
    "signal-C-bail": dict(MARINE, nom="BAIL",
        corps="system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif", extra="""
  body{background:#0a1a2b}
  .entete{background:#0a1a2b;border-bottom:0}
  .entete::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;
    background:linear-gradient(90deg,#e23a3e 0 50%,#0f2438 50% 100%)}
  .hero{background:linear-gradient(180deg,rgba(15,36,56,.9),rgba(10,26,43,1))}
  h1{font-weight:900;letter-spacing:-.05em;line-height:.86;color:#fff}
  h1 span{color:#e23a3e}
  .filet{background:#e23a3e;width:100%;max-width:24rem;height:10px}
  .surtitre{font-weight:900;letter-spacing:-.03em;text-transform:uppercase;color:#0a1a2b;
    background:#eef3f7;display:inline-block;padding:.2rem .6rem .3rem}
  h2{color:#9db2c6;font-weight:700;letter-spacing:.3em}
  .cadre{border-radius:0;border:0;background:transparent;box-shadow:none;padding:0;
    display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0}
  .grand{padding:1.6rem 1.1rem;background:#0f2438}
  .grand:nth-child(even){background:#e23a3e}
  .grand b{color:#fff;font-weight:900;letter-spacing:-.04em;text-shadow:none}
  .grand span{color:rgba(255,255,255,.75);letter-spacing:.14em;font-size:.58rem}
  .titre-cit{color:#9db2c6;letter-spacing:.3em}
  .citation{--acc:#0f2438;border-left:0;border-top:0;background:#0f2438;
    width:min(24rem,82vw);padding:1.5rem 1.8rem}
  .citation figcaption{border-top:3px solid #e23a3e;padding-top:.6rem;margin-top:.9rem}
  .citation blockquote{color:#eef3f7}
  .ep21 blockquote{color:#fff} .siecle{color:#e23a3e;letter-spacing:.22em}
  .stories h2,.reels h2,.monde h2{color:#fff;text-transform:uppercase;letter-spacing:-.02em;
    white-space:normal;font-weight:900}
  .planisphere{border-radius:0;border-color:rgba(255,255,255,.16);background:#081521}
  .pt-v i{background:#e23a3e;box-shadow:none}
  .carte-kit{border-radius:0;border:0;border-left:10px solid #e23a3e;background:#0f2438}
  .carte-jeu{background:#0f2438;border:0;border-left:10px solid #e23a3e;border-radius:0}
  .reel{border-radius:0;border-color:rgba(255,255,255,.16)}
  footer{color:#9db2c6}
  .cookies{background:#0f2438;border-top:3px solid #e23a3e;border-radius:0}
  .cookies button{background:#e23a3e;color:#fff;border-radius:0}
"""),
}



def habillage(html: str, m: dict) -> str:
    """Applique une direction (palette, corps de texte, feuille propre) à une page déjà construite."""
    html = html.replace(
        'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif',
        f'font-family:{m["corps"]}', 1)
    html = html.replace(
        '<meta name="theme-color" content="#08162a">',
        f'<meta name="theme-color" content="{m["nuit"]}">')
    html = html.replace("</style>", m["extra"] + CORRECTIFS + "\n</style>", 1)
    if m.get("js"):
        html = html.replace("</body>", f'<script>{m["js"]}</script>\n</body>', 1)
    return html


def maquette(nom: str) -> None:
    """Écrit la page complète dans maquettes/<nom>.html, jamais publiée."""
    from pathlib import Path as _P
    m = MAQUETTES[nom]

    m = dict(m)
    try:
        jeu = prochain_jeu()
    except Exception:
        jeu = ""          # pas de date inventée : le texte reste sans échéance
    blocs = (site_blocks.html_stories(site_blocks.stories(SORTIE))
             + site_blocks.html_reels(site_blocks.reels(SORTIE))
             )
    ancien = globals()
    depart = {k: ancien[k] for k in ("NUIT", "NUIT2", "EAU", "CREME", "GRIS", "ROUGE", "AMBRE", "TOILE")}
    try:
        globals().update(
            NUIT=m["nuit"], NUIT2=m["nuit2"], EAU=m["eau"], CREME=m["creme"],
            GRIS=m["gris"], ROUGE=m["rouge"], AMBRE=m["ambre"], TOILE=m["toile"])
        html = page(jeu, blocs, site_blocks.html_carte(), mer_louvoyage.html_fond())
    finally:
        globals().update(depart)
    html = habillage(html, m)
    html = html.replace("<title>Sailing More", "<title>[MAQUETTE %s] Sailing More" % nom, 1)
    sortie = RACINE / "projets/sailingmore/maquettes" / f"{nom}.html"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(html, encoding="utf-8")
    print(f"{sortie} · {len(html):,} car".replace(",", " "))


if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "--maquettes":
    for _n in MAQUETTES:
        maquette(_n)
    raise SystemExit(0)


if __name__ == "__main__":
    raise SystemExit(main())
