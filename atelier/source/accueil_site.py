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

import accueil_2026
import marque
import mer_louvoyage
import site_blocks

# Fourchette de prix des formules, lue dans `marque.py` (jamais écrite à la main dans les textes).
# Espace ordinaire, comme dans les textes validés ; l'anglais met la virgule.
_PMIN = f"{marque.PRIX_MIN:,}".replace(",", " ")
_PMAX = f"{marque.PRIX_MAX:,}".replace(",", " ")
_PMIN_EN = f"{marque.PRIX_MIN:,}"
_PMAX_EN = f"{marque.PRIX_MAX:,}"

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

LANGUES = site_blocks.LANGUES      # une seule liste, celle de site_blocks (le breton s'y ajoute au sélecteur)

TEXTES = {
    "fr": {
        "surtitre": "Le large, chaque soir.",
        "accroche": "Média <span class='rouge'>indépendant</span> de la voile et de la course au large, fait par des <span class='rouge'>passionnés</span>, pour des <span class='rouge'>passionnés</span>.",
        "chiffres": "Sailing More en chiffres",
        "reseaux": "Nos réseaux",
        "citations": "Ils l'ont dit avant nous",
        "concours_titre": "Le jeu concours",
        "concours_texte": "Un jeu pour un annonceur, cinq jours de stories, du mardi au samedi, un tirage le dimanche. Prochain départ : mardi {date}.",
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
        "p1_nom": "Essai une semaine",
        "p1_ce": "2 publications · 1 concours",
        "p2_nom": "Présence un mois",
        "p2_ce": "4 publications · 2 concours",
        "p3_nom": "Parité un mois",
        "p3_ce": "5 publications · 2 concours",
        "p4_nom": "Trimestre",
        "p4_ce": "12 publications · 6 concours",
        "d1": "Publications dédiées, Facebook et Instagram",
        "d2": "Jeux concours de 7 jours, avec votre lot et votre logo sur l'affiche",
        "d3": "Stories pour annoncer le concours",
        "d4": "Tirage au sort, et le gagnant annoncé",
        "d5": "Rapport de portée sous 72 h, chiffres Meta",
        "d6": "La mention « partenariat rémunéré »",
        "d7": "Durée du pack",
        "d8": "Une parution en plus, à l'unité",
        "d_legende": "Une publication dédiée, c'est un post Facebook et un post Instagram sur votre marque, avec votre visuel et le lien que vous voulez. Le concours met votre lot en jeu, sur une affiche qui porte votre logo. La coche veut dire que c'est compris. Les images sont les nôtres ou les vôtres ; celle d'un tiers, seulement avec son accord écrit. Et le lot du concours vient de vous.",
        "det_titre": "Le détail, formule par formule",
        "h_titre": "Au-delà des quatre formules",
        "h_intro": "Plus gros budget, saison entière, ou votre nom sur une série : dites la période et l'objectif, réponse chiffrée sous 48 h.",
        "h2_nom": "Douze mois",
        "h2_ce": "l'année entière, concours et publications répartis",
        "h3_nom": "Sur mesure",
        "h3_ce": "un budget plus gros, ou un événement : on écrit la formule ensemble",
        "h4_nom": "Sponsoring d'un format",
        "h4_ce": "votre nom sur une série qu'on produit, avec nos images ou les vôtres",
        "h_note": "Prix avant signature. Prix HT.",
        "bloc_detail_titre": "Chaque formule comprend",
        "bloc_detail": "Dans chaque formule : le concours, son affiche, une story, et le rapport de portée sous 72 h.",
        "tarif_notes": "Prix HT. Aucune portée garantie : on la mesure, et on l'écrit avant de signer.",
        "kit_texte": "Quatre formules, du test d'une semaine au trimestre. Prix HT.",
        "kit_bouton": "Recevoir la grille",
        "kit_preuve": "Ces chiffres viennent de Meta, relevés ce mois-ci.",
        "kit_nom": "Votre nom",
        "kit_marque": "Marque ou activité",
        "kit_email": "Email",
        "kit_note": "Vos données servent seulement à vous répondre. Suppression sur demande.",
        "kit_ou": "Ou écrivez à",
        "kit_lien": "notre adresse",
        "kit_rappel": "Annonceurs — recevoir la grille des tarifs",
        "hero_cta": "Annoncer sur Sailing More",
        "cookies_texte": "Aucun cookie de mesure ni de publicité. Les vidéos YouTube ne se chargent qu'au clic.",
        "cookies_lien": "En savoir plus",
        "cookies_bouton": "J'ai compris",
        "ann_intro": f"Sailing More publie tous les soirs à 18 h : les courses en cours, puis une vidéo un soir sur deux. Quatre formules pour y mettre votre marque : de {_PMIN} à {_PMAX} €, jeu concours compris.",
    },
    "en": {
        "surtitre": "The open sea, every evening.",
        "accroche": "An <span class='rouge'>independent</span> sailing and offshore racing outlet, made by <span class='rouge'>enthusiasts</span>, for <span class='rouge'>enthusiasts</span>.",
        "chiffres": "Sailing More in numbers",
        "reseaux": "Our channels",
        "citations": "They said it before us",
        "concours_titre": "The giveaway",
        "concours_texte": "One giveaway for an advertiser, five days of stories, Tuesday to Saturday, a draw on Sunday. Next start: Tuesday {date}.",
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
        "p1_nom": "One-week trial",
        "p1_ce": "2 posts · 1 giveaway",
        "p2_nom": "One-month presence",
        "p2_ce": "4 posts · 2 giveaways",
        "p3_nom": "One-month parity",
        "p3_ce": "5 posts · 2 giveaways",
        "p4_nom": "Quarter",
        "p4_ce": "12 posts · 6 giveaways",
        "d1": "Dedicated posts, Facebook and Instagram",
        "d2": "Seven-day giveaways, with your prize and your logo on the sheet",
        "d3": "Stories to announce the giveaway",
        "d4": "The draw, and the winner announced",
        "d5": "Reach report within 72 h, Meta figures",
        "d6": "The “paid partnership” line",
        "d7": "How long the package runs",
        "d8": "One extra post, priced alone",
        "d_legende": "A dedicated post is one on Facebook and one on Instagram about your brand, with your visual and whatever link you want. The giveaway puts your prize up, on a sheet that carries your logo. The tick means it comes with the package. The footage is ours or yours; anyone else's only with their written permission. And the prize comes from you.",
        "det_titre": "The detail, package by package",
        "h_titre": "Beyond the four packages",
        "h_intro": "Bigger spend, a whole season, or your name on a series: tell us the dates and what you are after, a priced answer comes back within 48 h.",
        "h2_nom": "Twelve months",
        "h2_ce": "the whole year, giveaways and posts spread out",
        "h3_nom": "Custom",
        "h3_ce": "bigger spend, a run of giveaways, an event: we write the package together",
        "h4_nom": "Sponsoring a format",
        "h4_ce": "your name on a series we make, with our footage or yours",
        "h_note": "Price before signature. Prices excl. VAT.",
        "bloc_detail_titre": "Every option includes",
        "bloc_detail": "Every package has the giveaway, its announcement sheet, a story, and the reach report within 72 h.",
        "tarif_notes": "Prices excl. VAT. No guaranteed reach: we measure it, and we write that down before you sign.",
        "kit_texte": "Four packages, from a one-week trial to a quarter. Prices excl. VAT.",
        "kit_bouton": "Get the rate card",
        "kit_preuve": "Those figures come from Meta, measured this month.",
        "kit_nom": "Your name",
        "kit_marque": "Brand or business",
        "kit_email": "Email",
        "kit_note": "Your details are only used to reply to you. Deletion on request.",
        "kit_ou": "Or write to",
        "kit_lien": "our address",
        "kit_rappel": "Advertisers — get the rate card",
        "hero_cta": "Advertise on Sailing More",
        "cookies_texte": "No analytics or advertising cookies. YouTube videos only load when you click play.",
        "cookies_lien": "Learn more",
        "cookies_bouton": "Got it",
        "ann_intro": f"Sailing More posts every evening at 6 pm: the races under way, then a video every other evening. Four packages to put your brand in front of it: €{_PMIN_EN} to €{_PMAX_EN}, giveaway included.",
    },
    "it": {
        "surtitre": "Il largo, ogni sera.",
        "accroche": "Un media <span class='rouge'>indipendente</span> di vela e altura, fatto da <span class='rouge'>appassionati</span>, per <span class='rouge'>appassionati</span>.",
        "chiffres": "Sailing More in numeri",
        "reseaux": "I nostri canali",
        "citations": "L'hanno detto prima di noi",
        "concours_titre": "Il concorso",
        "concours_texte": "Un concorso per un inserzionista, cinque giorni di storie, dal martedì al sabato, un sorteggio la domenica. Prossima partenza: martedì {date}.",
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
        "p1_nom": "Prova una settimana",
        "p1_ce": "2 pubblicazioni · 1 concorso",
        "p2_nom": "Presenza un mese",
        "p2_ce": "4 pubblicazioni · 2 concorsi",
        "p3_nom": "Parità un mese",
        "p3_ce": "5 pubblicazioni · 2 concorsi",
        "p4_nom": "Trimestre",
        "p4_ce": "12 pubblicazioni · 6 concorsi",
        "d1": "Pubblicazioni dedicate, Facebook e Instagram",
        "d2": "Concorsi di 7 giorni, con il vostro premio e il vostro logo sul foglio",
        "d3": "Story per annunciare il concorso",
        "d4": "L'estrazione, e il vincitore annunciato",
        "d5": "Rapporto di copertura entro 72 ore, numeri di Meta",
        "d6": "La menzione «partnership retribuita»",
        "d7": "Quanto dura la formula",
        "d8": "Una pubblicazione in più, da sola",
        "d_legende": "Una pubblicazione dedicata è un post su Facebook e uno su Instagram sul vostro marchio, con il vostro visual e il link che preferite. Il concorso mette in palio il vostro premio, su un foglio che porta il vostro logo. La spunta vuol dire che è compreso. Le immagini sono le nostre o le vostre; quelle di altri solo con il loro consenso scritto. E il premio del concorso viene da voi.",
        "det_titre": "Il dettaglio, formula per formula",
        "h_titre": "Oltre le quattro formule",
        "h_intro": "Budget più grande, una stagione intera, o il vostro nome su una serie: dite il periodo e l'obiettivo, risposta con i prezzi entro 48 ore.",
        "h2_nom": "Dodici mesi",
        "h2_ce": "l'anno intero, concorsi e pubblicazioni distribuiti",
        "h3_nom": "Su misura",
        "h3_ce": "budget più grande, serie di concorsi, evento: scriviamo la formula insieme",
        "h4_nom": "Sponsorizzazione di un formato",
        "h4_ce": "il vostro nome su una serie che produciamo, con le nostre immagini o le vostre",
        "h_note": "Prezzo prima della firma. Prezzi IVA esclusa.",
        "bloc_detail_titre": "Ogni formula comprende",
        "bloc_detail": "In ogni formula: il concorso, il suo foglio di annuncio, una story e il rapporto di copertura entro 72 ore.",
        "tarif_notes": "Prezzi IVA esclusa. Nessuna copertura garantita: la misuriamo, e lo mettiamo per iscritto prima della firma.",
        "kit_texte": "Quattro formule, dalla prova di una settimana al trimestre. Prezzi IVA esclusa.",
        "kit_bouton": "Ricevere le tariffe",
        "kit_preuve": "Questi numeri vengono da Meta, rilevati questo mese.",
        "kit_nom": "Il tuo nome",
        "kit_marque": "Marchio o attività",
        "kit_email": "Email",
        "kit_note": "I tuoi dati servono solo per risponderti. Cancellazione su richiesta.",
        "kit_ou": "Oppure scrivi a",
        "kit_lien": "il nostro indirizzo",
        "kit_rappel": "Inserzionisti — ricevere il listino",
        "hero_cta": "Pubblicizza su Sailing More",
        "cookies_texte": "Nessun cookie di analisi né pubblicitario. I video YouTube si caricano solo al clic.",
        "cookies_lien": "Scopri di più",
        "cookies_bouton": "Ho capito",
        "ann_intro": f"Sailing More pubblica ogni sera alle 18: le regate in corso, poi un video una sera su due. Quattro formule per mettere il vostro marchio lì davanti: da {_PMIN} a {_PMAX} €, concorso incluso.",
    },
    "es": {
        "surtitre": "El mar abierto, cada noche.",
        "accroche": "Un medio <span class='rouge'>independiente</span> de vela y regata oceánica, hecho por <span class='rouge'>aficionados</span>, para <span class='rouge'>aficionados</span>.",
        "chiffres": "Sailing More en cifras",
        "reseaux": "Nuestras redes",
        "citations": "Lo dijeron antes que nosotros",
        "concours_titre": "El sorteo",
        "concours_texte": "Un sorteo para un anunciante, cinco días de historias, de martes a sábado, un sorteo el domingo. Próxima salida: martes {date}.",
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
        "p1_nom": "Prueba una semana",
        "p1_ce": "2 publicaciones · 1 sorteo",
        "p2_nom": "Presencia un mes",
        "p2_ce": "4 publicaciones · 2 sorteos",
        "p3_nom": "Paridad un mes",
        "p3_ce": "5 publicaciones · 2 sorteos",
        "p4_nom": "Trimestre",
        "p4_ce": "12 publicaciones · 6 sorteos",
        "d1": "Publicaciones dedicadas, Facebook e Instagram",
        "d2": "Sorteos de 7 días, con tu premio y tu logo en la hoja",
        "d3": "Stories para anunciar el sorteo",
        "d4": "El sorteo, y el ganador anunciado",
        "d5": "Informe de alcance en 72 h, cifras de Meta",
        "d6": "La mención «colaboración pagada»",
        "d7": "Cuánto dura la fórmula",
        "d8": "Una publicación más, suelta",
        "d_legende": "Una publicación dedicada es un post en Facebook y otro en Instagram sobre tu marca, con tu visual y el enlace que quieras. El sorteo pone en juego tu premio, en una hoja que lleva tu logo. La marca de visto significa que va incluido. Las imágenes son nuestras o tuyas; las de un tercero solo con su permiso escrito. Y el premio del sorteo viene de ti.",
        "det_titre": "El detalle, fórmula por fórmula",
        "h_titre": "Más allá de las cuatro fórmulas",
        "h_intro": "Más presupuesto, una temporada entera, o tu nombre en una serie: dime las fechas y el objetivo, respuesta con precios en 48 h.",
        "h2_nom": "Doce meses",
        "h2_ce": "el año entero, sorteos y publicaciones repartidos",
        "h3_nom": "A medida",
        "h3_ce": "más presupuesto, una serie de sorteos, un evento: escribimos la fórmula juntos",
        "h4_nom": "Patrocinio de un formato",
        "h4_ce": "tu nombre en una serie que producimos, con nuestras imágenes o las tuyas",
        "h_note": "Precio antes de firmar. Precios sin IVA.",
        "bloc_detail_titre": "Cada fórmula incluye",
        "bloc_detail": "En cada fórmula: el sorteo, su hoja de anuncio, una story y el informe de alcance en 72 h.",
        "tarif_notes": "Precios sin IVA. No garantizamos alcance: lo medimos, y lo dejamos por escrito antes de firmar.",
        "kit_texte": "Cuatro fórmulas, de la prueba de una semana al trimestre. Precios sin IVA.",
        "kit_bouton": "Recibir las tarifas",
        "kit_preuve": "Estas cifras vienen de Meta, medidas este mes.",
        "kit_nom": "Su nombre",
        "kit_marque": "Marca o actividad",
        "kit_email": "Correo",
        "kit_note": "Sus datos solo sirven para responderle. Supresión bajo petición.",
        "kit_ou": "O escriba a",
        "kit_lien": "nuestra dirección",
        "kit_rappel": "Anunciantes — recibir las tarifas",
        "hero_cta": "Anuncie en Sailing More",
        "cookies_texte": "Sin cookies de medición ni de publicidad. Los vídeos de YouTube solo se cargan al hacer clic.",
        "cookies_lien": "Saber más",
        "cookies_bouton": "Entendido",
        "ann_intro": f"Sailing More publica cada noche a las 18 h: las regatas en curso, y un vídeo una noche de cada dos. Cuatro fórmulas para poner tu marca delante: de {_PMIN} a {_PMAX} €, sorteo incluido.",
    },
    "pt": {
        "surtitre": "O largo, todas as noites.",
        "accroche": "Um meio <span class='rouge'>independente</span> de vela e regata oceânica, feito por <span class='rouge'>apaixonados</span>, para <span class='rouge'>apaixonados</span>.",
        "chiffres": "Sailing More em números",
        "reseaux": "As nossas redes",
        "citations": "Disseram-no antes de nós",
        "concours_titre": "O passatempo",
        "concours_texte": "Um passatempo para um anunciante, cinco dias de stories, de terça a sábado, um sorteio ao domingo. Próxima partida: terça-feira {date}.",
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
        "p1_nom": "Teste uma semana",
        "p1_ce": "2 publicações · 1 passatempo",
        "p2_nom": "Presença um mês",
        "p2_ce": "4 publicações · 2 passatempos",
        "p3_nom": "Paridade um mês",
        "p3_ce": "5 publicações · 2 passatempos",
        "p4_nom": "Trimestre",
        "p4_ce": "12 publicações · 6 passatempos",
        "d1": "Publicações dedicadas, Facebook e Instagram",
        "d2": "Passatempos de 7 dias, com o seu prémio e o seu logótipo na folha",
        "d3": "Stories para anunciar o passatempo",
        "d4": "O sorteio, e o vencedor anunciado",
        "d5": "Relatório de alcance em 72 h, números da Meta",
        "d6": "A menção «parceria paga»",
        "d7": "Quanto dura a fórmula",
        "d8": "Uma publicação a mais, avulsa",
        "d_legende": "Uma publicação dedicada é um post no Facebook e outro no Instagram sobre a sua marca, com o seu visual e o link que quiser. O passatempo põe o seu prémio em jogo, numa folha que leva o seu logótipo. O visto quer dizer que vem incluído. As imagens são nossas ou suas; as de terceiros só com autorização escrita. E o prémio do passatempo vem de si.",
        "det_titre": "O detalhe, fórmula a fórmula",
        "h_titre": "Para lá das quatro fórmulas",
        "h_intro": "Orçamento maior, uma época inteira, ou o seu nome numa série: diga as datas e o objectivo, resposta com preços em 48 h.",
        "h2_nom": "Doze meses",
        "h2_ce": "o ano inteiro, passatempos e publicações distribuídos",
        "h3_nom": "Por medida",
        "h3_ce": "orçamento maior, série de passatempos, evento: escrevemos a fórmula juntos",
        "h4_nom": "Patrocínio de um formato",
        "h4_ce": "o seu nome numa série que produzimos, com as nossas imagens ou as suas",
        "h_note": "Preço antes da assinatura. Preços sem IVA.",
        "bloc_detail_titre": "Cada fórmula inclui",
        "bloc_detail": "Em cada fórmula: o passatempo, a sua folha de anúncio, uma story e o relatório de alcance em 72 h.",
        "tarif_notes": "Preços sem IVA. Não garantimos alcance: medimo-lo, e escrevemo-lo antes de assinar.",
        "kit_texte": "Quatro fórmulas, do teste de uma semana ao trimestre. Preços sem IVA.",
        "kit_bouton": "Receber a tabela de preços",
        "kit_preuve": "Estes números vêm da Meta, medidos este mês.",
        "kit_nom": "O seu nome",
        "kit_marque": "Marca ou atividade",
        "kit_email": "Email",
        "kit_note": "Os seus dados servem apenas para lhe responder. Eliminação a pedido.",
        "kit_ou": "Ou escreva para",
        "kit_lien": "o nosso endereço",
        "kit_rappel": "Anunciantes — receber a tabela de preços",
        "hero_cta": "Anuncie na Sailing More",
        "cookies_texte": "Sem cookies de medição nem de publicidade. Os vídeos do YouTube só carregam ao clicar.",
        "cookies_lien": "Saber mais",
        "cookies_bouton": "Entendi",
        "ann_intro": f"A Sailing More publica todas as noites às 18 h: as regatas em curso e, uma noite sim, uma noite não, um vídeo. Quatro fórmulas para pôr a sua marca à frente: de {_PMIN} a {_PMAX} €, passatempo incluído.",
    },
    "de": {
        "surtitre": "Die Weite, jeden Abend.",
        "accroche": "Ein <span class='rouge'>unabhängiges</span> Segel- und Hochseerenne-Medium, von <span class='rouge'>Begeisterten</span> für <span class='rouge'>Begeisterte</span>.",
        "chiffres": "Sailing More in Zahlen",
        "reseaux": "Unsere Kanäle",
        "citations": "Sie sagten es vor uns",
        "concours_titre": "Das Gewinnspiel",
        "concours_texte": "Ein Gewinnspiel für einen Werbepartner, fünf Tage Stories von Dienstag bis Samstag, Ziehung am Sonntag. Nächster Start: Dienstag, {date}.",
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
        "p1_nom": "Probewoche",
        "p1_ce": "2 Beiträge · 1 Gewinnspiel",
        "p2_nom": "Präsenz einen Monat",
        "p2_ce": "4 Beiträge · 2 Gewinnspiele",
        "p3_nom": "Parität einen Monat",
        "p3_ce": "5 Beiträge · 2 Gewinnspiele",
        "p4_nom": "Quartal",
        "p4_ce": "12 Beiträge · 6 Gewinnspiele",
        "d1": "Eigene Beiträge, Facebook und Instagram",
        "d2": "Gewinnspiele über 7 Tage, Ihr Preis und Ihr Logo auf dem Blatt",
        "d3": "Stories, die das Gewinnspiel ankündigen",
        "d4": "Die Auslosung, und der Gewinner wird bekannt gegeben",
        "d5": "Reichweitenbericht binnen 72 Stunden, Meta-Zahlen",
        "d6": "Der Hinweis «bezahlte Partnerschaft»",
        "d7": "Wie lange das Paket läuft",
        "d8": "Ein Beitrag extra, einzeln",
        "d_legende": "Ein eigener Beitrag ist ein Post auf Facebook und einer auf Instagram über Ihre Marke, mit Ihrem Motiv und dem Link, den Sie wollen. Das Gewinnspiel spielt Ihren Preis aus, auf einem Blatt mit Ihrem Logo. Das Häkchen heißt: ist dabei. Das Material ist unseres oder Ihres; fremdes nur mit schriftlicher Erlaubnis. Und der Gewinn kommt von Ihnen.",
        "det_titre": "Das Detail, Paket für Paket",
        "h_titre": "Über die vier Pakete hinaus",
        "h_intro": "Mehr Budget, eine ganze Saison, oder Ihr Name auf einer Serie: nennen Sie Zeitraum und Ziel, Antwort mit Preis binnen 48 Stunden.",
        "h2_nom": "Zwölf Monate",
        "h2_ce": "das ganze Jahr, Gewinnspiele und Beiträge verteilt",
        "h3_nom": "Nach Maß",
        "h3_ce": "mehr Budget, eine Gewinnspielserie, ein Event: wir schreiben das Paket zusammen",
        "h4_nom": "Sponsoring eines Formats",
        "h4_ce": "Ihr Name auf einer Serie, die wir machen, mit unserem Material oder Ihrem",
        "h_note": "Preis vor der Unterschrift. Preise ohne MwSt.",
        "bloc_detail_titre": "Jedes Paket enthält",
        "bloc_detail": "In jedem Paket: das Gewinnspiel, sein Ankündigungsblatt, eine Story und der Reichweitenbericht binnen 72 Stunden.",
        "tarif_notes": "Preise ohne MwSt. Keine garantierte Reichweite: wir messen sie und schreiben das vor der Unterschrift hin.",
        "kit_texte": "Vier Pakete, von der Probewoche bis zum Quartal. Preise ohne MwSt.",
        "kit_bouton": "Preisliste erhalten",
        "kit_preuve": "Diese Zahlen kommen von Meta, in diesem Monat erhoben.",
        "kit_nom": "Ihr Name",
        "kit_marque": "Marke oder Tätigkeit",
        "kit_email": "E-Mail",
        "kit_note": "Ihre Daten dienen nur der Antwort. Löschung auf Anfrage.",
        "kit_ou": "Oder schreiben Sie an",
        "kit_lien": "unsere Adresse",
        "kit_rappel": "Werbekunden — Preisliste erhalten",
        "hero_cta": "Werben auf Sailing More",
        "cookies_texte": "Keine Mess- oder Werbe-Cookies. YouTube-Videos laden erst beim Klick.",
        "cookies_lien": "Mehr erfahren",
        "cookies_bouton": "Verstanden",
        "ann_intro": f"Sailing More veröffentlicht jeden Abend um 18 Uhr: die laufenden Regatten, dazu jeden zweiten Abend ein Video. Vier Pakete, um Ihre Marke davorzusetzen: {_PMIN} bis {_PMAX} €, Gewinnspiel inklusive.",
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
# Les données viennent de `marque.RESEAUX` ; ici on ne garde que l'ordre d'affichage du site.
# Telegram passe à gauche d'Instagram (Nicolas, 19/11/2026) : l'ordre du site est donc
# Telegram, Facebook, YouTube, Instagram, X (celui des feuilles : Facebook, Instagram, YouTube, Telegram, X).
# Le format (clé, lien, svg) reste celui que lit `logos_reseaux.py`.
_ORDRE_SITE = ["telegram", "facebook", "youtube", "instagram", "x"]
_PAR_CLE = {r["cle"]: r for r in marque.RESEAUX}
RESEAUX = [(_PAR_CLE[c]["cle"], _PAR_CLE[c]["url"], _PAR_CLE[c]["svg"]) for c in _ORDRE_SITE]


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
    """Seuls les liens externes s'ouvrent dans un nouvel onglet (audit 24/11, correction 3).

    Les liens internes et les ancres restent dans l'onglet courant : le bouton retour doit marcher.
    Un lien qui porte déjà sa cible n'est pas retouché.
    """
    def rempl(m):
        tag = m.group(0)
        if "target=" in tag:
            return tag
        h = re.search(r'href="([^"]*)"', tag)
        if not h or not h.group(1).startswith(("http://", "https://", "//")) or "sailingmore.fr" in h.group(1):
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
        f'<span data-t="{lab}">{TEXTES["fr"].get(lab, lab)}</span></div>'
        for cle, lab, estime in GRANDS)

    # La mer prend tout l'écran du héros : plus de cadre, le bateau navigue sur la page.
    heros = mer_louvoyage.hero(f"""
  <h1>Sailing<span>More</span></h1>
  <div class="filet"></div>
  <p class="accroche" data-t="accroche">Média <span class='rouge'>indépendant</span> de la voile et de la course au large, fait par des <span class='rouge'>passionnés</span>, pour des <span class='rouge'>passionnés</span>.</p>
  <a class="bouton bouton-hero" href="annonceurs.html"><span data-t="hero_cta">Annoncer sur Sailing More</span> <span class="fleche" aria-hidden="true">→</span></a>""")

    bandeau = "".join(bloc_citation(i, x) for i, x in enumerate(cites))
    cites_js = citations_pour_js(cites)
    # Toutes les pages dans un seul panneau qui descend (voir site_blocks.menu_site).
    menu = site_blocks.menu_site()

    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sailing More — la voile et la course au large, en images</title>
<meta name="description" content="Sailing More, média indépendant de voile et de course au large : stories quotidiennes, vidéos et régates, sur Instagram et Facebook.">
<meta property="og:title" content="Sailing More">
<meta property="og:description" content="La voile et la course au large, en images.">
<link rel="canonical" href="https://sailingmore.fr/">
{__import__("jsonld").bloc(__import__("jsonld").site_web(), __import__("jsonld").organisation())}
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
    -webkit-font-smoothing:antialiased;overflow-x:clip}}
  a{{color:inherit;text-decoration:none}}
  .entete{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;
    padding:.7rem 1.2rem;background:rgba(6,16,32,.72);backdrop-filter:blur(10px);
    border-bottom:1px solid rgba(126,214,214,.14)}}
  .entete .nom{{font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:.82rem;color:var(--gris)}}
  .entete .menu{{margin-left:auto;margin-right:1.1rem;font-size:.78rem;letter-spacing:.09em;
    text-transform:uppercase;color:var(--creme);border-bottom:1px solid rgba(226,58,62,.55);
    padding-bottom:1px}}
  .entete .menu:hover{{color:#fff;border-bottom-color:var(--rouge)}}
  @media (max-width:520px){{.entete .menu{{font-size:.7rem;margin-right:.6rem}}}}
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
  .bouton::before{{content:"";position:absolute;inset:0;z-index:-1;background:#c62a2e;
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
  body #cookies[hidden]{{display:none!important}}
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
{site_blocks.entete_site("index.html", LANGUES)}

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
  <p><span data-t="cookies_texte">Aucun cookie de mesure ni de publicité. Les vidéos YouTube ne se chargent qu'au clic.</span>
  <a href="confidentialite.html" data-t="cookies_lien">En savoir plus</a></p>
  <button id="cookies-ok" data-t="cookies_bouton">J'ai compris</button>
</div>

<footer>
  <a href="regates.html">Régates · Regattas</a>
  <a href="regles-de-course.html">Règles · Rules</a>
  <a href="stages.html">Stages · Courses</a>
  <a href="cours.html">Cours · Lessons</a>
  <a href="lexique.html">Lexique · Glossary</a>
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
  // Une seule détection, faite dans le <head> avant le premier pixel (24/11/2026).
  const l = (typeof window.smLangue === "function") ? window.smLangue() : "en";
  if (l === "bzh") return "fr";
  return Object.keys(T).includes(l) ? l : "en";
}}

function appliquer(l) {{
  const d = T[l];
  document.documentElement.lang = l;
  // Titre et description suivent la langue, à partir des chaînes déjà dans T (surtitre, accroche).
  const md = document.querySelector('meta[name="description"]');
  window.__fr = window.__fr || {{ t: document.title, d: md ? md.getAttribute("content") : "" }};
  if (l === "fr") {{
    document.title = window.__fr.t;
    if (md) md.setAttribute("content", window.__fr.d);
  }} else if (d.surtitre) {{
    document.title = "Sailing More — " + d.surtitre;
    if (md && d.accroche) md.setAttribute("content", "Sailing More — " + d.accroche.replace(/<[^>]+>/g, ""));
  }}
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
<link rel="canonical" href="https://sailingmore.fr/jeux.html">
{__import__("jsonld").page_simple("jeux.html", "Le jeu concours")}
<meta name="description" content="Le jeu concours Sailing More : cinq jours de stories, du mardi au samedi, un tirage le dimanche.">
{__import__("jsonld").social("jeux.html", "Le jeu concours — Sailing More", "Le jeu concours Sailing More : cinq jours de stories, du mardi au samedi, un tirage le dimanche.")}
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
  <a class="retour" href="/">← Sailing More</a>
  <h1>Le jeu <span>concours</span></h1>
  <div class="filet"></div>
  <p>Un jeu par mois, offert à un annonceur : une place dans nos stories du soir pendant cinq jours,
  du mardi au samedi, puis un tirage le dimanche à 18&nbsp;h.</p>
  <p class="date">Prochain départ : {date_longue(jeu)}</p>
  <ul>
    <li>Le tirage se fait au sort, parmi les participations reçues avant la clôture du samedi, 23&nbsp;h&nbsp;59.</li>
    <li>Le gagnant est annoncé le dimanche à 18&nbsp;h, en story.</li>
    <li>La participation est gratuite et sans obligation d'achat.</li>
  </ul>
  <p>Écrire à <a class="courriel" href="mailto:[secret-masqué]" data-a="hello.sailingmore" data-b="gmail.com">[secret-masqué]</a>.</p>
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
        brut = lire_brut(chemin)
        s, d = appel(f"/repos/{depot}/contents/{nom}")
        sha = d["sha"] if s == 200 and isinstance(d, dict) else None
        corps = {"message": f"accueil : {nom}",
                 "content": base64.b64encode(brut).decode()}
        if sha:
            corps["sha"] = sha
        s2, r2 = appel(f"/repos/{depot}/contents/{nom}", "PUT", corps)
        print(f"{nom} → {s2}" + ("" if s2 < 300 else f" {r2}"))


BINAIRES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".woff", ".woff2",
            ".mp4", ".mov", ".webm", ".pdf", ".zip"}


def lire_brut(chemin):
    """Le contenu d'un fichier tel quel : le texte en UTF-8, le reste en octets.

    Corrigé le 20/11/2026 : une police `.woff` était lue comme du texte et son premier octet non UTF-8
    cassait l'envoi (« UnicodeDecodeError: 0xc9 »), après la préparation des 73 fichiers. La liste des
    binaires est explicite, et un fichier texte qui ne se décode pas passe quand même en octets plutôt
    que d'arrêter la publication.
    """
    if chemin.suffix.lower() in BINAIRES:
        return chemin.read_bytes()
    try:
        return chemin.read_text(encoding="utf-8").encode()
    except UnicodeDecodeError:
        return chemin.read_bytes()


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

    if "--repetition" in sys.argv:
        total = sum((SORTIE / n).stat().st_size for n in fichiers)
        for n in fichiers:
            print(f"répétition · {n} · {(SORTIE / n).stat().st_size} o")
        print(f"répétition : {len(fichiers)} fichier(s), {total} octets — rien n'a été envoyé")
        return

    arbre = []
    for nom in fichiers:
        chemin = SORTIE / nom
        brut = lire_brut(chemin)
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



def fichiers_a_publier() -> list[str]:
    """Ce que le site envoie, à un seul endroit.

    Deux listes pour un même site, c'est ce qui a ramené l'ancien gabarit en ligne le 20/11 : la
    génération et la publication doivent lire la même liste, et elle est ici.
    """
    # `carte.html` est une page du site comme les autres : elle part avec elles, sinon le fichier
    # publié reste celui d'hier (23/11/2026, la carte à deux modes).
    pages = [n for n in ("index.html", "carte.html", "jeux.html", "annonceurs.html", "merci.html",
                         "regates.html", "regles-de-course.html", "lexique.html", "stages.html", "comparatif-stages.html",
                         "equivalences.html", "cours.html", "bateaux.html", "bateaux.json", "stages-proches.json", "404.html", "mentions-legales.html",
                         "confidentialite.html", "delete.html", "sitemap.xml", "feed.xml")
             if (SITE / n).exists()]
    # Une page par pavillon (24/11/2026, chapitre des pavillons du cours) : 42 pages `pavillon-<id>.html`.
    # Elles se publient avec les autres, sinon elles restent locales et les liens du cours mènent à un 404.
    pages += sorted(p.name for p in SITE.glob("pavillon-*.html"))
    images = [n for n in ("og-image.jpg", "icon-512.png", "icon-180.png", "favicon-32.png",
                          "carte-monde.png") if (SITE / n).exists()]
    medias = sorted(p.relative_to(SITE).as_posix() for d in ("stories", "reels", "drapeaux")
                    for p in (SITE / d).glob("*") if p.suffix.lower() in {".jpg", ".png"})
    # Les 42 SVG des pavillons du Code international de signaux (12 Ko en tout), avec leur dossier.
    medias += sorted(p.relative_to(SITE).as_posix() for p in (SITE / "pavillons").glob("*.svg"))
    polices = sorted(p.relative_to(SITE).as_posix() for p in (SITE / "fonts").glob("*.woff"))
    # Les neuf images WebP de la nomenclature des bateaux (rendues par Hermes depuis images-src/bateaux/*.svg,
    # voir bateaux-images.json) : stables, à `images/bateaux/sailingmore-nomenclature-<sujet>.webp`.
    medias += sorted(p.relative_to(SITE).as_posix() for p in (SITE / "images" / "bateaux").glob("*.webp"))
    # Le JavaScript des pages : un fichier à part vit à côté du HTML, il doit donc partir avec lui
    # (sans lui, le filtre par classe du calendrier reste muet à l'écran).
    js = sorted(p.relative_to(SITE).as_posix() for p in SITE.glob("*.js"))
    return [*pages, *images, *medias, *polices, *js]


def miroir_vers_sortie(liste: list[str] | None = None) -> int:
    """Copie dans `cache/rhum/site` ce que le site publie — la publication ne lit que là.

    C'est la pièce qui manquait le 20/11 : `--site` écrivait le bon site dans `projets/…/site` et
    la publication envoyait l'ancien `cache/rhum/site`, resté en arrière. Les deux sortent
    maintenant de la même génération, à l'octet près.
    """
    liste = liste or fichiers_a_publier()
    for nom in liste:
        dst = SORTIE / nom
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SITE / nom, dst)
    return len(liste)


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
        # Accueil 2026 (tâche 47) : le gabarit reste, tout le corps vient de `accueil_2026.py`.
        return accueil_2026.refondre(habillage(page(jeu, blocs, site_blocks.html_carte(), mer_louvoyage.html_fond()), m), RACINE)
    finally:
        globals().update(depart)


def sortir_le_site(jeu: str, blocs: str, miroir_complet: bool = True) -> int:
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
    # La carte du Léman vient de son propre atelier (`carte-leman/build5.py`), pas d'ici : on la
    # recopie à chaque construction pour qu'il n'y ait jamais deux versions en circulation
    # (23/11/2026 : la version à deux modes est restée dans le dossier du projet pendant que le
    # site publiait celle de la veille).
    carte_src = ICI.parent / "projets" / "sailingmore" / "carte-leman" / "carte-leman-modes.html"
    if carte_src.exists():
        import shutil as _sh  # noqa: PLC0415
        _sh.copy2(carte_src, SITE / "carte.html")
        print(f"carte : {carte_src.name} recopiée dans {SITE.name}/carte.html")
    # Pages entières écrites par Claude, jamais publiées jusqu'au 24/11/2026 : elles vivaient dans
    # sa copie de travail et le générateur ne les connaissait pas. Elles sont recopiées depuis
    # `projets/sailingmore/pages/` (RACINE, donc aussi `donnees/` dans l'atelier), et la barre du
    # site leur est posée par `poser_entete_partout()` comme à toute page du dossier.
    pages_src = RACINE / "projets" / "sailingmore" / "pages"
    if pages_src.is_dir():
        import shutil as _sh2  # noqa: PLC0415
        for _p in sorted(pages_src.glob("*.html")):
            _sh2.copy2(_p, SITE / _p.name)
        print(f"pages écrites par Claude : {len(list(pages_src.glob('*.html')))} recopiée(s)")
    (SITE / "index.html").write_text(accueil)
    (SITE / "jeux.html").write_text(concours)
    (SITE / "merci.html").write_text(merci)
    (SITE / "annonceurs.html").write_text(annonceurs)
    # Le calendrier des régates suit le même chemin que les autres pages (21/11/2026) : il est
    # construit ici, avant la mer et l'équilibre, sinon une reconstruction du site l'effacerait.
    try:
        import regates_page
        print(f"calendrier des régates : {regates_page.ecrire_page(SITE)} épreuves")
    except SystemExit as e:
        print(f"calendrier des régates non écrit : {e}")
    # Règles de course (22/11/2026) : même chemin ; ecrire_page() rend 0 sans rien écrire tant que
    # regles.json n'est pas « complet » et validé (voir regles_page.py --verifier).
    try:
        import regles_page
        print(f"règles de course : {regles_page.ecrire_page(SITE)} entrées")
    except SystemExit as e:
        print(f"règles de course non écrites : {e}")
    # Stages et cours de voile (22/11/2026) : même chemin que le calendrier, jamais d'écriture à la main.
    try:
        import stages_page
        print(f"stages et cours : {stages_page.ecrire_page(SITE)} offre(s) publiable(s)")
    except Exception as e:  # noqa: BLE001
        print(f"stages et cours non écrits : {e}")
    # Comparatif des stages (tâche n°70, 25/11/2026) : mêmes données que stages.html, lues par le même module.
    try:
        import comparatif_stages_page
        print(f"comparatif des stages : {comparatif_stages_page.ecrire_page(SITE)} offre(s) comparée(s)")
    except Exception as e:  # noqa: BLE001
        print(f"comparatif des stages non écrit : {e}")
    # Équivalences des diplômes (23/11/2026) : même chemin ; equivalences_page.py est la source unique.
    # Seules les lignes validées par Nicolas et sourcées sont publiées ; l'aperçu (non publié) montre tout.
    try:
        import equivalences_page
        print(f"équivalences : {equivalences_page.ecrire_page(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"équivalences non écrites : {e}")
    # Chants de marins (24/11/2026) : même chemin ; chants_page.py est la source unique, chants-de-marin.json
    # les données. Elle refuse d'écrire si les décisions de Nicolas (6 fiches, 4 lecteurs…) ne tiennent pas.
    try:
        import chants_page
        print(f"chants de marins : {chants_page.ecrire_page(SITE)}")
    except (Exception, SystemExit) as e:  # noqa: BLE001
        print(f"chants de marins non écrits : {e}")
    # Cours théoriques (22/11/2026) : même chemin ; cours_page.py est la source unique, rien à la main.
    try:
        import cours_page
        print(f"cours théoriques : {cours_page.ecrire_page(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"cours théoriques non écrits : {e}")
    # Nomenclature des bateaux (22/11/2026) : même chemin ; bateaux_page.py écrit la page, bateaux.json (lu par
    # lexique_page.py), les sources SVG des images et le sitemap. Les mots ajoutés au lexique y sont rangés d'abord.
    try:
        import bateaux_page
        print(f"nomenclature des bateaux : {bateaux_page.ecrire_page(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"nomenclature des bateaux non écrite : {e}")
    # Favoris (24/11/2026) : favoris_page.py est la source unique des trois scripts et de mes-favoris.html.
    # Les balises <script> viennent de site_blocks.entete_site() (liste PAGES_FAVORIS), posée plus bas
    # par poser_entete_partout() : mes-favoris.html reçoit ainsi la barre du site comme les autres.
    try:
        import favoris_page
        print(f"favoris : {favoris_page.ecrire_page(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"favoris non écrits : {e}")
    # Comptes (24/11/2026) : écrans + couche d'appel, inertes tant que SM_CONFIG.comptes vaut « local ».
    # Scripts posés par site_blocks.balises_comptes() ; aucun lien dans le menu, noindex, hors sitemap.
    try:
        import comptes_page
        print(f"comptes : {comptes_page.ecrire_page(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"comptes non écrits : {e}")
    for nom in ("mentions-legales.html", "confidentialite.html", "delete.html"):
        if (SORTIE / nom).exists():
            brut = (SORTIE / nom).read_text()
            if nom == "confidentialite.html":
                brut = avec_section_alertes(brut)
            (SITE / nom).write_text(tete_pages_legales(nom, habillage_pages_legales(brut)))
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
    print(f"canonique posée sur {poser_canoniques()} page(s)")
    # Bloc « stages près de chez vous » (22/11/2026) : posé quand toutes les pages sont écrites, une seule fois par page.
    try:
        import stages_page
        print(f"stages près de chez vous posé sur : {stages_page.injecter_bloc(SITE)}")
    except Exception as e:  # noqa: BLE001
        print(f"bloc stages non posé : {e}")
    # La mer d'abord, la barre ensuite : la barre s'insère juste après `<body>` et passe donc
    # au-dessus du tableau de bord du bateau, qui sinon s'affiche avant elle (23/11/2026).
    n = poser_mer_partout()
    print(f"mer posée sur {n} page(s) supplémentaire(s)")
    print(f"barre du site posée sur {poser_entete_partout()} page(s)")
    print(f"lien du flux posé sur {poser_flux_partout()} page(s)")
    # Le sitemap est reconstruit ici, après toutes les pages : c'est le seul écrivain de la liste
    # (24/11/2026). `ports.html` et `simulateur.html` n'y figuraient jamais — publiées, jamais
    # déclarées, donc jamais envoyées à Bing par IndexNow. Les générateurs qui ajoutaient leur
    # entrée (chants, bateaux) restent idempotents et ne créent pas de doublon.
    try:
        import sitemap_site
        print(f"sitemap.xml reconstruit : {sitemap_site.fusionner(SITE)} adresse(s)")
    except Exception as e:  # noqa: BLE001
        print(f"sitemap non reconstruit : {e}")
    # Le flux RSS lit les pages qui viennent d'être écrites (feed_rss.py, 24/11/2026) : il passe donc
    # après elles, et son entrée est dans `fichiers_a_publier()` comme tout le reste.
    try:
        import feed_rss
        print(f"flux RSS écrit : {feed_rss.ecrire(SITE)} entrée(s)")
    except Exception as e:  # noqa: BLE001
        print(f"flux RSS non écrit : {e}")
    print(f"équilibre posé sur {poser_equilibre(SITE)} page(s)")
    # Le détecteur passe en dernier : plusieurs pages (régates, chants, jeux, annonceurs) sont
    # écrites plus loin dans la chaîne, et une page réécrite après lui perdait son bloc (24/11/2026).
    print(f"détecteur de langue posé sur {poser_langue_partout()} page(s)")
    print(f"site écrit dans {SITE} — {len(list(SITE.rglob('*')))} entrées")
    liste = fichiers_a_publier()
    # `--page` ne recopie que la page demandée : recopier tout `cache/rhum/site` depuis un cron
    # faisait croire à l'atelier que chaque fichier avait changé, et il republiait le site entier
    # reconstruit par ce cron — c'est le chemin qui a effacé les correctifs du 20/11.
    if miroir_complet:
        print(f"{miroir_vers_sortie(liste)} fichier(s) prêts pour l'envoi")
    if "--publier" in sys.argv:
        publier_en_un_seul_envoi(liste, "accueil : le site du jour")
    return 0


# ---------------------------------------------------------------------------
# Rééquilibrage design (20/11/2026, validé par Nicolas : « fais les modifications pour tout
# rééquilibrer »). Une seule feuille, `equilibre.css`, posée en dernier dans le <head> de chaque
# page : police Inter hébergée sur le site, couleurs et coins de la charte, rien sous 12 px,
# bandeau cookies qui ne cache plus les chiffres. Pour revenir en arrière : vider equilibre.css.
# ---------------------------------------------------------------------------
ICI = Path(__file__).resolve().parent
EQUILIBRE = ICI / "equilibre.css"
POLICES = ICI / "fonts"


def poser_equilibre(dossier: Path) -> int:
    """Pose la feuille d'équilibre dans chaque page du dossier et y copie les polices."""
    if not EQUILIBRE.exists():
        return 0
    css = EQUILIBRE.read_text(encoding="utf-8")
    bloc = '<style id="equilibre">\n' + css + '</style>'
    fait = 0
    for page in sorted(dossier.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        html = re.sub(r'<style id="equilibre">.*?</style>\n?', "", html, flags=re.S)
        if "</head>" not in html:
            continue
        page.write_text(html.replace("</head>", bloc + "\n</head>", 1), encoding="utf-8")
        fait += 1
    if POLICES.exists():
        (dossier / "fonts").mkdir(parents=True, exist_ok=True)
        for f in POLICES.glob("*.woff"):
            shutil.copy2(f, dossier / "fonts" / f.name)
    return fait


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


# Le lexique commande le bateau en fond (Nicolas, 22/11/2026). Un clic sur une entrée = UN appel à
# `window.merManoeuvre` (mer_louvoyage.py) : l'état change une fois, aucun calcul par image, aucun
# observateur de défilement. Les entrées absentes de la table ne déclenchent rien (nœuds : schémas,
# pas de bateau). a = allure en degrés au vent ('P' = au plus près), flip = changer d'amure.
LEXIQUE_MANOEUVRES = {
    "virer": {"flip": 1, "k": "virer"}, "pare-a-virer": {"flip": 1, "k": "virer"},
    "bord": {"flip": 1, "k": "virer"},
    "louvoyer": {"flip": 1, "a": "P", "k": "pres"},
    "empanner": {"flip": 1, "a": 150, "k": "empanner"}, "pare-a-empanner": {"flip": 1, "a": 150, "k": "empanner"},
    "attention-a-la-bome": {"a": 150, "k": "empanner"},
    "lofer": {"a": "P", "k": "pres"}, "pres": {"a": "P", "k": "pres"}, "ardent": {"a": "P", "k": "pres"},
    "au-vent": {"a": "P", "k": "pres"}, "zone-de-non-vent": {"a": "P", "k": "pres"},
    "vent-debout": {"a": "P", "k": "pres"}, "faseyer": {"a": "P", "k": "pres"},
    "decrochage": {"a": "P", "k": "pres"}, "mettre-en-panne": {"a": "P", "k": "pres"},
    "border": {"a": "P", "k": "pres"}, "gite": {"a": "P", "k": "gite"},
    "mouiller": {"a": "P", "k": "ancre"}, "ancre": {"a": "P", "k": "ancre"},
    "bon-plein": {"a": 60, "k": "bonplein"}, "travers": {"a": 90, "k": "travers"},
    "largue": {"a": 120, "k": "largue"}, "choquer": {"a": 120, "k": "largue"},
    "abattre": {"a": 130, "k": "largue"}, "refuser": {"a": 130, "k": "largue"},
    "vent-arriere": {"a": 150, "k": "arriere"}, "spinnaker": {"a": 150, "k": "spi"},
}
LEXIQUE_LEGENDES = {
    "virer": {"fr": "Le bateau vire de bord : l'avant passe face au vent.", "en": "The boat tacks: the bow turns through the wind.",
              "de": "Das Boot wendet: der Bug geht durch den Wind.", "it": "La barca vira: la prua passa attraverso il vento.",
              "es": "El barco vira: la proa pasa por el viento.", "pt": "O barco vira: a proa passa pelo vento."},
    "empanner": {"fr": "Empannage : l'arrière passe dans le vent, la bôme change de côté.", "en": "Gybe: the stern passes through the wind, the boom swings across.",
                 "de": "Halse: das Heck geht durch den Wind, der Baum schlägt über.", "it": "Abbattuta: la poppa passa nel vento, il boma cambia lato.",
                 "es": "Trasluchada: la popa pasa por el viento, la botavara cambia de lado.", "pt": "Jibe: a popa passa pelo vento, a retranca muda de lado."},
    "pres": {"fr": "Au plus près : le bateau remonte vers le vent, voiles bordées.", "en": "Close-hauled: the boat points as high as it can, sails sheeted in.",
             "de": "Am Wind: das Boot läuft so hoch wie möglich, Segel dicht.", "it": "Di bolina: la barca stringe il vento, vele cazzate.",
             "es": "De ceñida: el barco navega lo más cerca del viento, velas cazadas.", "pt": "De bolina: o barco navega o mais junto ao vento, velas cingidas."},
    "gite": {"fr": "La gîte : au plus près, le bateau penche le plus.", "en": "Heel: close-hauled, the boat leans the most.",
             "de": "Krängung: am Wind neigt sich das Boot am stärksten.", "it": "Sbandamento: di bolina la barca si inclina di più.",
             "es": "Escora: de ceñida el barco se inclina más.", "pt": "Adernamento: de bolina o barco inclina-se mais."},
    "ancre": {"fr": "Vent debout, bateau qui ralentit — comme avant de mouiller. L'ancre elle-même n'est pas dessinée.", "en": "Head to wind, boat slowing — as before anchoring. The anchor itself is not drawn.",
              "de": "Gegen den Wind, das Boot wird langsamer — wie vor dem Ankern. Der Anker selbst ist nicht gezeichnet.", "it": "Prua al vento, la barca rallenta — come prima di ancorare. L'ancora non è disegnata.",
              "es": "Proa al viento, el barco frena — como antes de fondear. El ancla no está dibujada.", "pt": "Proa ao vento, o barco abranda — como antes de fundear. A âncora não está desenhada."},
    "bonplein": {"fr": "Bon plein : un peu plus ouvert que le près.", "en": "Close reach: a little freer than close-hauled.",
                 "de": "Raumer Wind: etwas offener als am Wind.", "it": "Bolina larga: un po' più aperta della bolina.",
                 "es": "Ceñida abierta: algo más abierto que de ceñida.", "pt": "Bolina folgada: um pouco mais aberta que a bolina."},
    "travers": {"fr": "Au travers : le vent vient de côté.", "en": "Beam reach: the wind comes from the side.",
                "de": "Halbwind: der Wind kommt von der Seite.", "it": "Al traverso: il vento arriva di lato.",
                "es": "Al largo: el viento viene de costado.", "pt": "Través: o vento vem de lado."},
    "largue": {"fr": "Le bateau s'écarte du vent : voiles choquées.", "en": "The boat bears away: sails eased.",
               "de": "Das Boot fällt ab: Segel gefiert.", "it": "La barca poggia: vele lasche.",
               "es": "El barco se abre del viento: velas amolladas.", "pt": "O barco arriba: velas folgadas."},
    "arriere": {"fr": "Vent arrière : le vent vient de derrière.", "en": "Running: the wind comes from astern.",
                "de": "Vor dem Wind: der Wind kommt von achtern.", "it": "In poppa: il vento arriva da dietro.",
                "es": "Viento en popa: el viento viene de detrás.", "pt": "Vento em popa: o vento vem de trás."},
    "spi": {"fr": "Allure de spi (vent arrière). Le spi n'est montré que si le modèle du bateau en porte un.", "en": "Spinnaker point of sail (running). The spinnaker shows only if the boat model carries one.",
            "de": "Spi-Kurs (vor dem Wind). Der Spi erscheint nur, wenn das Bootsmodell einen hat.", "it": "Andatura da spi (in poppa). Lo spi si vede solo se il modello lo ha.",
            "es": "Rumbo de spi (en popa). El spi sólo se ve si el modelo del barco lo lleva.", "pt": "Rumo de spi (em popa). O spi só aparece se o modelo do barco o tiver."},
}
SCRIPT_LEXIQUE = """<script>(function(){
var M=%s, L=%s, T=null, el=null;
function lg(){ var l=(document.documentElement.lang||'fr').slice(0,2); return /^(fr|en|de|it|es|pt)$/.test(l)?l:'fr' }
function dire(k){
  if(!el){ el=document.createElement('div'); el.setAttribute('role','status'); el.setAttribute('aria-live','polite');
    el.style.cssText='position:fixed;left:50%%;bottom:1.2rem;transform:translateX(-50%%);max-width:min(32rem,92vw);padding:.7rem 1.1rem;background:rgba(10,26,43,.94);color:#eef3f7;border-left:3px solid #e23a3e;font-size:.85rem;line-height:1.4;z-index:50;opacity:0;transition:opacity .25s;pointer-events:none';
    document.body.appendChild(el) }
  el.textContent=L[k][lg()]; el.style.opacity=1; clearTimeout(T); T=setTimeout(function(){ el.style.opacity=0 },5200);
}
var liste=document.getElementById('liste-termes'); if(!liste) return;
liste.addEventListener('click',function(e){
  var a=e.target.closest&&e.target.closest('article.terme'); if(!a) return;
  var m=M[a.id]; if(!m||!window.merManoeuvre) return;
  if(window.merManoeuvre(m)) dire(m.k);
});
})();</script>"""


def poser_langue_partout() -> int:
    """Le détecteur unique de langue dans le `<head>` de chaque page (24/11/2026).

    Une seule fonction pour tout le site : `?lang=` → choix du visiteur → français (25/11/2026 :
    plus de détection par le navigateur). Posée **dans la tête**, donc exécutée avant le premier pixel : le visiteur allemand voit
    l'allemand d'emblée, sans le clignotement français → allemand qu'on avait avec treize détecteurs
    recopiés qui tournaient chacun à la fin de leur page.

    Idempotent : le bloc est encadré par deux marqueurs et remplacé à chaque construction, jamais
    empilé. Les pages sans menu de langues (`carte.html`, `simulateur.html`) n'ont qu'un jeu de
    textes français : leur poser un détecteur mettrait `lang="de"` sur du français — on les laisse.
    """
    bloc = "<!--langue-debut-->" + site_blocks.script_langue() + "<!--langue-fin-->"
    fait = 0
    for page in sorted(SITE.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        avant = html
        if "<!--langue-debut-->" in html:
            html = re.sub(r"<!--langue-debut-->.*?<!--langue-fin-->", lambda m: bloc, html, count=1, flags=re.S)
        elif ('data-lang="fr"' in html or 'data-l="' in html) and re.search(r"<head[^>]*>", html):
            html = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + bloc, html, count=1)
        if html != avant:
            page.write_text(html, encoding="utf-8")
            fait += 1
    return fait


def poser_flux_partout() -> int:
    """Le lien vers `feed.xml` dans la tête de chaque page (24/11/2026).

    Un flux unique pour le site, mais un lien dans chaque page : c'est ce qui permet à un lecteur
    ou à un robot qui arrive sur `stages.html` de trouver le flux sans deviner `/feed.xml`.
    Idempotent : le lien est reconnu à son `type="application/rss+xml"`, on ne l'empile pas.
    """
    lien = ('<link rel="alternate" type="application/rss+xml" title="Sailing More" '
            'href="https://sailingmore.fr/feed.xml">')
    fait = 0
    for page in sorted(SITE.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        if 'type="application/rss+xml"' in html or "</head>" not in html:
            continue
        html = html.replace("</head>", "  " + lien + "\n</head>", 1)
        page.write_text(html, encoding="utf-8")
        fait += 1
    return fait


def poser_entete_partout() -> int:
    """La barre du site sur toutes les pages, y compris légales, 404 et le calendrier.

    Nicolas, 23/11/2026 : « 1 sur toutes les pages maintenant note en règle ». Même bloc que
    `site_blocks.entete_site()` — nom, menu, langues — posé juste après `<body>` : un
    `position:sticky` ne colle que dans son parent, et la barre doit tenir en haut de chaque page.
    Idempotent : le bloc précédent est retiré avant d'être reposé, une construction ne l'empile pas.
    Deux pages n'ont pas le menu des langues dans la barre : la carte du Léman (tout en français,
    plein écran) et les stages (leur propre menu, qui pilote le contenu de la page).
    """
    fait = 0
    for page in sorted(SITE.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        avant = html
        if "<!--entete-debut-->" in html:
            tete, _, reste = html.partition("<!--entete-debut-->")
            _, _, queue = reste.partition("<!--entete-fin-->")
            html = tete + queue
        if 'class="entete"' in html:
            if html != avant:
                page.write_text(html, encoding="utf-8")
            continue
        langues, auto = LANGUES, True
        # Pas de second `#langues` : une page qui a déjà son propre sélecteur garde le sien,
        # la barre lui apporte le nom et le menu (regles-apercu, par exemple).
        # La carte du Léman n'est qu'en français : sa barre porte le nom et le menu, sans menu de
        # langue. Les stages, eux, gardent le leur (celui de la page filtre les offres).
        if page.name == "carte.html" or page.name == "stages.html" or \
                'id="lng-sel"' in html or 'id="langues"' in html:
            langues, auto = [], False
        bloc = ("<!--entete-debut-->" + site_blocks.barre_autonome(page.name, langues, auto)
                + "<!--entete-fin-->")
        html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + bloc, html, count=1)
        page.write_text(html, encoding="utf-8")
        fait += 1
    return fait


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
        # La carte est un instrument plein écran, pas une page de lecture : le tableau de bord du
        # bateau y masquait le coin haut-gauche et débordait de 20 px en largeur (23/11/2026).
        # On lui retire le bloc, y compris celui qu'une construction passée y avait laissé.
        if page.name == "carte.html":
            if "<!--mer-debut-->" in html:
                html = html.split("<!--mer-debut-->")[0] + html.split("<!--mer-fin-->")[-1]
                page.write_text(_sans_commandes(html))
            continue
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
        bloc_page = bloc
        if page.name == "lexique.html":
            import json
            bloc_page = bloc.replace("<!--mer-fin-->", SCRIPT_LEXIQUE % (
                json.dumps(LEXIQUE_MANOEUVRES, ensure_ascii=False),
                json.dumps(LEXIQUE_LEGENDES, ensure_ascii=False)) + "<!--mer-fin-->")
        if "</body>" in html:
            html = html.replace("</body>", bloc_page + "\n</body>", 1)
        else:
            html += bloc_page
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
  .bouton::before{content:"";position:absolute;inset:0;z-index:-1;background:#c62a2e;
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


SECTION_ALERTES = """<!--alertes-regates-->
<h2>Alertes régates et actualité · Race alerts and news</h2>
<p><b>Finalités.</b> Si vous saisissez votre e-mail dans le calendrier des régates, vous cochez
deux cases distinctes, jamais pré-cochées : (1) <i>être alerté des nouvelles régates</i>, obligatoire
pour s'inscrire ; (2) <i>recevoir aussi l'actualité de Sailing More</i>, facultative. Votre adresse
n'est utilisée que pour ces finalités.</p>
<p><b>Données.</b> Votre adresse e-mail, la langue de la page, le filtre choisi (lieu, type, classe,
horizon), vos deux choix de consentement et la date de confirmation. Votre position n'est jamais
collectée : « près de moi » se calcule dans votre navigateur, et le texte de votre recherche n'est pas transmis.</p>
<p><b>Base légale.</b> Votre consentement (art. 6.1.a RGPD), confirmé par un e-mail de validation
(double opt-in) ; sans clic sur le lien, l'adresse n'est pas inscrite.</p>
<p><b>Prestataire.</b> L'envoi est assuré par Brevo (Sendinblue SAS, France), sous-traitant au sens du RGPD,
avec hébergement dans l'Union européenne. <b>Durée.</b> Jusqu'à votre désinscription, puis suppression
sous 30 jours ; une liste inactive depuis trois ans est purgée.</p>
<p><b>Désinscription.</b> Chaque envoi contient, en pied, le lien de désinscription de sa liste. Les deux
listes sont indépendantes : quitter l'actualité ne vous retire pas des alertes, et l'inverse. Vous pouvez aussi
demander l'accès, la rectification ou l'effacement de vos données via la page « Suppression de données ».</p>
<p><b>Cartographie.</b> Les coordonnées des villes proviennent d'OpenStreetMap (Nominatim), interrogé une
fois par ville lors de la mise à jour du calendrier, jamais depuis votre navigateur. © contributeurs OpenStreetMap, licence ODbL.</p>
<p lang="en"><b>English.</b> If you enter your email in the race calendar you tick two separate, unticked-by-default
boxes: (1) be alerted to new races (required), (2) also receive Sailing More news (optional). Double opt-in by email;
processed by Brevo (EU). Every email has an unsubscribe link for its own list; the two lists are independent.
Your location never leaves your browser. Contact us via the data deletion page for access, correction or erasure.</p>
"""


def avec_section_alertes(html: str) -> str:
    """Ajoute à la politique de confidentialité la section sur les alertes (une seule fois)."""
    if "<!--alertes-regates-->" in html:
        return html
    fin = html.rfind("</body>")
    i = html.rfind("</div>", 0, fin if fin >= 0 else len(html))  # avant le </div> de fermeture de la page
    if i < 0:
        i = fin if fin >= 0 else len(html)
    return html[:i] + SECTION_ALERTES + html[i:]


def poser_canoniques() -> int:
    """Contrôle du 25/11/2026 : `carte.html` (recopiée de son atelier) et les pages `stories/AAAA-MM-JJ.html`
    (copiées de la sortie) étaient indexables sans `<link rel="canonical">`. Posé ici, juste après leur copie,
    sur toute page qui n'est pas `noindex` et qui n'en a pas. Idempotent. Rend le nombre de pages modifiées."""
    cibles = [SITE / "carte.html", *sorted((SITE / "stories").glob("*.html"))]
    n = 0
    for f in cibles:
        if not f.exists():
            continue
        h = f.read_text(encoding="utf-8")
        if 'rel="canonical"' in h or re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', h, re.I):
            continue
        rel = f.relative_to(SITE).as_posix()
        h = h.replace("</head>", f'<link rel="canonical" href="https://sailingmore.fr/{rel}">\n</head>', 1)
        f.write_text(h, encoding="utf-8")
        n += 1
    return n


_DESC_LEGALES = {
    "mentions-legales.html": "Éditeur, hébergeur et conditions d'utilisation du site Sailing More.",
    "confidentialite.html": "Les données que Sailing More collecte, ce qu'il en fait et comment exercer vos droits.",
    "delete.html": "Demander la suppression de vos données sur Sailing More.",
}


def tete_pages_legales(nom: str, html: str) -> str:
    """Audit SEO du 24/11/2026, correction 4 : description et canonique propres aux trois pages légales,
    `lang="fr"` sur delete.html (la page est bilingue, le français est la langue du HTML). Idempotent."""
    d = _DESC_LEGALES.get(nom)
    if not d:
        return html
    if 'rel="canonical"' not in html:
        html = html.replace("</head>", f'<link rel="canonical" href="https://sailingmore.fr/{nom}"></head>', 1)
    if 'name="description"' not in html:
        html = html.replace("</head>", f'<meta name="description" content="{d}"></head>', 1)
    if nom == "delete.html":
        html = html.replace('<html lang="en"', '<html lang="fr"', 1)
    return html


def _sans_onglet_interne(html: str) -> str:
    """Retire target="_blank" rel="noopener" des liens internes (audit 24/11, correction 3)."""
    def rempl(m):
        tag = m.group(0)
        h = re.search(r'href="([^"]*)"', tag)
        if "_blank" not in tag or (h and h.group(1).startswith(("http://", "https://", "//"))
                                   and "sailingmore.fr" not in h.group(1)):
            return tag
        return re.sub(r'\s+(?:target="_blank"|rel="noopener")', "", tag)
    return re.sub(r"<a\b[^>]*>", rempl, html)


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
    corps = ('\n<div class="page">\n<a class="retour" href="/">← Sailing More</a>\n'
             + corps.strip() + "\n</div>\n")
    return tete + "<body>" + _sans_onglet_interne(corps) + "</body>\n</html>\n"


def page_annonceurs() -> str:
    """La page que le bouton du héros ouvre dans un nouvel onglet : le formulaire seul, sans détour."""
    return ("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Publicité voile : formules annonceurs | Sailing More</title>"
            "<link rel=\"canonical\" href=\"https://sailingmore.fr/annonceurs.html\">"
            # Audit SEO du 24/11/2026, correction 4. Le « 141 000 abonnés » du texte de l'audit n'est PAS repris :
            # le total ne vient d'aucune donnée de ce script (relevé Meta fait ailleurs). Prix : _PMIN/_PMAX.
            f"<meta name=\"description\" content=\"Touchez les abonnés voile de Sailing More sur Facebook et "
            f"Instagram : formules de {_PMIN} à {_PMAX} € HT, jeu concours compris, rapport de portée sous 72 h.\">"
            + __import__("jsonld").social(
                "annonceurs.html", "Publicité voile : formules annonceurs | Sailing More",
                f"Touchez les abonnés voile de Sailing More sur Facebook et Instagram : formules de {_PMIN} à "
                f"{_PMAX} € HT, jeu concours compris, rapport de portée sous 72 h.")
            + CSS_LEGAL.replace("</style>", site_blocks.CSS + CSS_BOUTON + "</style>"
                              + "<style>.page.page-annonceurs{max-width:64rem}"
                              # Nicolas, 20/11/2026 : les espaces de cette page sautaient de 15 px à
                              # 54 px. Un seul écart entre deux blocs : 1,6 rem, 3,2 avant la carte.
                              + ".page.page-annonceurs>*+*{margin-top:1.6rem}"
                              + ".page.page-annonceurs>.ann-carte{margin-top:3.2rem}"
                              + ".ann-carte{font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;"
                                "color:#9db2c6;margin:3.4rem 0 1rem}</style>") +
            "</head><body><div class=\"page page-annonceurs\"><a class=\"retour\" href=\"/\">← Sailing More</a>"
            "<h1 data-t=\"kit_titre\">Annonceurs</h1>"
            + f"<p data-t=\"ann_intro\">{TEXTES['fr']['ann_intro']}</p>"
            "<div class=\"carte-kit\">"
            + site_blocks.tarifs(TEXTES['fr']) +
            site_blocks.hors_grille(TEXTES['fr']) +
            site_blocks.formulaire_kit() +
            "</div>"
            '<details class="plis plis-carte"><summary data-t="ann_carte">Où sont les lecteurs</summary>'
            + site_blocks.html_carte() +
            "<p class=\"kit-preuve\" data-t=\"kit_preuve\">Ces chiffres viennent de Meta, relevés ce "
            "mois-ci.</p></details>"
            "</div>" + _script_langue_annonceurs() + "</body></html>\n")


def _script_langue_annonceurs() -> str:
    """La page portait 56 `data-t` sans aucune table ni script : elle restait en français pour tous.
    Mesure du 22/11/2026 (scripts/etude_six_langues.py). On reprend les chaînes déjà dans TEXTES (celles
    de l'accueil), même choix de langue que l'accueil (sm-langue, sinon français), et le
    titre et la description suivent la langue à partir de `kit_titre` et `ann_intro`."""
    table = json.dumps(TEXTES, ensure_ascii=False)
    return ("<script>(function(){var T=" + table + ";"
            "function choisir(){var l=(typeof window.smLangue==='function')?window.smLangue():'en';"
            "if(l==='bzh')return 'fr';return T[l]?l:'en'}"
            "var l=choisir();if(l==='fr')return;var d=T[l];document.documentElement.lang=l;"
            "document.querySelectorAll('[data-t]').forEach(function(el){var v=d[el.dataset.t];if(v)el.textContent=v});"
            "if(d.kit_titre)document.title=d.kit_titre+' \\u2014 Sailing More';"
            "var m=document.querySelector('meta[name=\"description\"]');"
            "if(m&&d.ann_intro)m.setAttribute('content',d.ann_intro)})();</script>")


def page_merci() -> str:
    """La page où FormSubmit renvoie après l'envoi du formulaire annonceurs."""
    return ("<!doctype html>\n<html lang=\"fr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Merci — Sailing More</title>"
            "<meta name=\"robots\" content=\"noindex\">"
            + CSS_LEGAL +
            "</head><body><div class=\"page\"><a class=\"retour\" href=\"/\">← Sailing More</a>"
            "<h1>Merci.</h1>"
            "<p>Votre demande est partie. Je réponds moi-même, sous 24 heures, du lundi au vendredi.</p>"
            "<p>En attendant, la grille est là : quatre formules, de l'essai d'une semaine au trimestre.</p>"
            "<p><a href=\"/#annonceurs\">Revenir à la page des annonceurs</a></p>"
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
    # Un seul chemin : ce qui part est ce que `--site` vient d'écrire, et rien d'autre. Sans cette
    # ligne, `--publier` seul reprenait l'ancien gabarit resté dans SORTIE et l'envoyait — le retour
    # en arrière du 20/11 à 17 h 20, et le motif du cron `site_du_jour` qui ne publiait plus rien
    # (`--site` sortait avant la publication).
    if "--page" in sys.argv:
        nom = sys.argv[sys.argv.index("--page") + 1]
        sortir_le_site(jeu, blocs, miroir_complet=False)
        if not (SITE / nom).exists():
            print(f"page absente après génération : {nom}")
            return 1
        print(f"{miroir_vers_sortie([nom])} page copiée dans {SORTIE} : {nom}")
        return 0
    if "--site" in sys.argv or "--publier" in sys.argv:
        return sortir_le_site(jeu, blocs)
    (SORTIE / "index.html").write_text(accueil_2026.refondre(page(jeu, blocs, carte, kit=site_blocks.html_kit(fr=TEXTES['fr'])), RACINE))
    (SORTIE / "jeux.html").write_text(page_jeu(jeu))
    print(f"écrit {SORTIE / 'index.html'} · {SORTIE / 'jeux.html'}")
    print(f"chiffres au {chiffres().get('maj')} · prochain jeu {jeu} · {len(citations())} citations")
    poser_equilibre(SORTIE)
    if "--publier" in sys.argv:
        images = [n for n in ("og-image.jpg", "icon-512.png", "icon-180.png", "favicon-32.png")
                  if (SORTIE / n).exists()]
        medias = sorted(str(p.relative_to(SORTIE)) for dossier in ("stories", "reels")
                        for p in (SORTIE / dossier).glob("*.jpg"))
        if (SORTIE / "carte-monde.png").exists():
            medias.append("carte-monde.png")
        pages = [n for n in ("mentions-legales.html", "confidentialite.html", "delete.html")
                 if (SORTIE / n).exists()]
        polices = sorted(str(p.relative_to(SORTIE)) for p in (SORTIE / "fonts").glob("*.woff"))
        publier_en_un_seul_envoi(["index.html", "jeux.html", *pages, *images, *medias, *polices])
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
  .cookies button{background:#e23a3e;color:#000;border-radius:0}
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
  .siecle{color:#f05a5e;letter-spacing:.2em;font-size:.55rem}
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
  .cookies button{background:#e23a3e;color:#000;border-radius:0}

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
  html{overflow-x:clip}
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
  .ep21 blockquote{color:#fff} .siecle{color:#f05a5e;letter-spacing:.22em}
  .stories h2,.reels h2,.monde h2{color:#fff;text-transform:uppercase;letter-spacing:-.02em;
    white-space:normal;font-weight:900}
  .planisphere{border-radius:0;border-color:rgba(255,255,255,.16);background:#081521}
  .pt-v i{background:#e23a3e;box-shadow:none}
  .carte-kit{border-radius:0;border:0;border-left:10px solid #e23a3e;background:#0f2438}
  .carte-jeu{background:#0f2438;border:0;border-left:10px solid #e23a3e;border-radius:0}
  .reel{border-radius:0;border-color:rgba(255,255,255,.16)}
  footer{color:#9db2c6}
  .cookies{background:#0f2438;border-top:3px solid #e23a3e;border-radius:0}
  .cookies button{background:#e23a3e;color:#000;border-radius:0}
"""),

    # C — LARGE (23/11/2026) : même charte, même mise en page, la forme seule est reprise.
    # Ce qui change : une seule échelle typographique en clamp() (plus de tailles en dur), une pile
    # système qui commence par Inter au lieu de system-ui nu, des chiffres à chasse fixe dans le
    # tableau de bord, les titres qui s'équilibrent sur deux lignes, et un contour de focus visible.
    # Rien de ce qui est mesuré ne bouge : ni la barre du titre, ni la grille du cadre, ni les
    # quatre matières des citations.
    "signal-C-large": dict(MARINE, nom="LARGE",
        corps="Inter,Roboto,'Helvetica Neue','Arial Nova','Nimbus Sans',Arial,sans-serif", extra="""
  body{background:#0a1a2b;-webkit-font-smoothing:antialiased;font-kerning:normal;
    font-variant-ligatures:common-ligatures}
  :root{--t-1:clamp(.68rem,.63rem + .16vw,.78rem);--t-2:clamp(.88rem,.83rem + .18vw,.96rem);
    --t-3:clamp(1.02rem,.97rem + .24vw,1.12rem);--t-4:clamp(1.24rem,1.12rem + .6vw,1.6rem);
    --e-2:clamp(1.4rem,1.1rem + 1.4vw,2.4rem)}
  /* le héros n'est pas retouché : sa hauteur est déjà réglée et le titre y est centré par le
     gabarit. On ne touche qu'à la forme du texte. */
  h1{font-size:clamp(2.9rem,10.5vw,6.2rem);font-weight:300;letter-spacing:-.035em;
    text-wrap:balance}
  h1 span{letter-spacing:-.045em}
  .surtitre{font-size:clamp(1.35rem,4.4vw,2.2rem);line-height:1.18;letter-spacing:-.015em;
    text-wrap:balance;color:#eef3f7}
  .accroche{font-size:var(--t-3);line-height:1.62;max-width:34rem;color:#9db2c6;text-wrap:pretty}
  h2{font-size:var(--t-1);letter-spacing:.24em;font-weight:500;color:#9db2c6}
  .cadre{margin-top:var(--e-2);padding:1.9rem 0;border-top-color:rgba(226,58,62,.55)}
  .grand{padding:0 clamp(.7rem,1.6vw,1.35rem)}
  .grand b{font-variant-numeric:tabular-nums;letter-spacing:-.025em}
  .grand span{font-size:clamp(.54rem,.5rem + .12vw,.62rem);letter-spacing:.16em}
  .citation blockquote{font-size:var(--t-4);line-height:1.55;text-wrap:pretty}
  .carte-kit p,.carte-jeu p{font-size:var(--t-3);line-height:1.6}
  a:focus-visible,button:focus-visible,select:focus-visible,summary:focus-visible{
    outline:2px solid #e23a3e;outline-offset:3px}
  .entete{background:rgba(10,26,43,.96);border-bottom:1px solid rgba(226,58,62,.55)}
"""),

    # D — ATELIER (23/11/2026) : la même charte poussée plus loin dans le rythme, pas dans la
    # couleur. Le héros et sa barre ne bougent pas (mesure du 20/11). Ce qui change : les sections
    # s'ouvrent par un numéro rouge de service, les filets portent la structure à la place des
    # encadrés, et les grands chiffres deviennent le point d'ancrage de la page.
    "signal-D-atelier": dict(MARINE, nom="ATELIER",
        corps="Inter,Roboto,'Helvetica Neue','Arial Nova','Nimbus Sans',Arial,sans-serif", extra="""
  body{background:#0a1a2b;-webkit-font-smoothing:antialiased;font-kerning:normal}
  h1{font-size:clamp(2.9rem,10.5vw,6.2rem);font-weight:300;letter-spacing:-.035em;text-wrap:balance}
  h1 span{letter-spacing:-.045em}
  .surtitre{font-size:clamp(1.3rem,4.2vw,2.1rem);line-height:1.2;letter-spacing:-.015em;
    text-wrap:balance;color:#eef3f7}
  .accroche{font-size:clamp(1.02rem,.97rem + .24vw,1.12rem);line-height:1.62;max-width:34rem;
    color:#9db2c6;text-wrap:pretty}
  /* le libellé de section devient un numéro de service : rouge, numéroté par CSS, jamais écrit.
     Seules les sections qui portent un titre sont comptées, sinon la numérotation saute. */
  section:has(>h2){counter-increment:atelier}
  h2{font-size:clamp(.66rem,.62rem + .14vw,.74rem);letter-spacing:.26em;font-weight:600;
    color:#9db2c6;display:flex;align-items:baseline;gap:.7rem}
  /* le rouge marque un chiffre, la charte l'autorise ; mais un rouge à 4,11:1 ne passe AA qu'en
     grand texte : le numéro est donc à 20 px, pas à 8 px comme un libellé. */
  h2::before{content:counter(atelier,decimal-leading-zero);color:#e23a3e;font-weight:600;
    letter-spacing:.02em;font-variant-numeric:tabular-nums;font-size:1.25rem;line-height:1}
  .cadre{margin-top:clamp(1.4rem,1.1rem + 1.4vw,2.4rem);padding:2.1rem 0;
    border-top:2px solid #e23a3e;border-bottom:1px solid rgba(255,255,255,.14)}
  .grand{border-left:1px solid rgba(255,255,255,.13)}
  .grand b{font-size:clamp(1.25rem,2.6vw,2.3rem);font-weight:300;letter-spacing:-.035em;
    font-variant-numeric:tabular-nums;line-height:1}
  .grand span{font-size:clamp(.52rem,.48rem + .12vw,.6rem);letter-spacing:.18em;color:#9db2c6}
  .citation blockquote{font-size:clamp(1.2rem,1.08rem + .55vw,1.55rem);line-height:1.58}
  a:focus-visible,button:focus-visible,select:focus-visible,summary:focus-visible{
    outline:2px solid #e23a3e;outline-offset:3px}
  .entete{background:rgba(10,26,43,.96);border-bottom:1px solid rgba(226,58,62,.55)}
  /* les icônes de réseaux suivent le bord des chiffres, au lieu de flotter au centre sous un
     libellé aligné à gauche */
  .reseaux-apres{max-width:64rem;margin:0 auto 6.5rem;padding:1.4rem;text-align:left}
  .reseaux-barre{justify-content:flex-start}
  @media(max-width:760px){h2::before{font-size:.8em}}
"""),
}

# C et D ne sont pas des chartes neuves : elles reprennent le bloc structurel de B — angles droits,
# aucune ombre, la barre du titre à sa mesure du 20/11 — et n'y ajoutent que la forme. Sans cette
# reprise, une maquette perdait les coins carrés et la barre du héros : constaté au premier rendu.
for _n in ("signal-C-large", "signal-D-atelier"):
    MAQUETTES[_n]["extra"] = MAQUETTES["signal-B-cap"]["extra"] + MAQUETTES[_n]["extra"]

# E — la proposition : la forme de C (échelle unique, chasse fixe) posée sur la structure de D
# (numéros de section, filets porteurs). C seule ne se voit pas ; D seule perd la finesse du texte.
MAQUETTES["signal-E-atelier-large"] = dict(
    MAQUETTES["signal-D-atelier"], nom="ATELIER LARGE",
    extra=MAQUETTES["signal-C-large"]["extra"] + MAQUETTES["signal-D-atelier"]["extra"][len(MAQUETTES["signal-B-cap"]["extra"]):])



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
