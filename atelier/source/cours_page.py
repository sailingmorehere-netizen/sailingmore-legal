#!/usr/bin/env python3
"""Construit la page `cours.html` : un cours théorique de voile, progressif, en six langues.

Source unique du contenu : ce fichier (plan CHAPITRES + textes par langue). Rien n'est écrit à la main
dans cours.html. Les schémas ne sont pas redessinés : ils viennent de `regles.json` via
`regles_page.schema_statique()` (même dessin, mêmes légendes six langues que la page des règles).
Les liens vers le lexique (`lexique.html#<id>`) et vers les règles (`regles-de-course.html#r<numéro>`)
sont posés par le code, à partir de la notation `{id|texte}` dans les textes.

Règle de la page : une règle n'est citée que par son numéro et son intitulé exacts (RRS 2025-2028,
intitulés repris de regles.json ; COLREG 1972, intitulés du texte anglais officiel de l'OMI).

    python3 scripts/cours_page.py --ecrire    # écrit projets/sailingmore/site/cours.html
"""
from __future__ import annotations

import html as _html
import os
import re
import sys
from pathlib import Path

RACINE = Path(os.environ.get("SITE_ROOT", str(Path(__file__).resolve().parent.parent)))
SITE = RACINE / "projets" / "sailingmore" / "site"
sys.path.insert(0, str(Path(__file__).resolve().parent))

LANGUES = ["fr", "en", "it", "es", "pt", "de"]
URL_RRS = "https://sailing.org/inside-world-sailing/rules-regulations/racingrules/"

# ── Le plan : l'ordre est la progression. Chaque chapitre ne suppose que les précédents. ──────────────
# regles : clés "rrs:<numéro>" ou "col:<numéro>", rendues avec leur numéro et leur intitulé exacts.
# schemas : clés (cle) de regles.json dont on injecte le schéma, via regles_page.schema_statique().
CHAPITRES = [
    {"id": "vocabulaire", "schemas": [], "regles": []},
    {"id": "vent", "schemas": [], "regles": []},
    {"id": "manoeuvres", "schemas": [], "regles": []},
    {"id": "cap", "schemas": [], "regles": []},
    {"id": "marees", "schemas": [], "regles": []},
    {"id": "meteo", "schemas": [], "regles": []},
    {"id": "balisage", "schemas": [], "regles": ["col:25"]},
    {"id": "abordage", "schemas": [], "regles": ["col:5", "col:7", "col:8", "col:12", "col:13", "col:14",
                                                  "col:15", "col:16", "col:17", "col:18"]},
    {"id": "depart", "schemas": [], "regles": ["rrs:26", "rrs:29", "rrs:30", "rrs:28", "rrs:31"]},
    {"id": "priorites", "schemas": ["10", "11", "12"],
     "regles": ["rrs:10", "rrs:11", "rrs:12", "rrs:13", "rrs:14", "rrs:15", "rrs:16", "rrs:17"]},
    {"id": "marques", "schemas": ["18", "44"], "regles": ["rrs:18", "rrs:19", "rrs:20", "rrs:44", "rrs:2"]},
    {"id": "securite", "schemas": [], "regles": ["rrs:1"]},
]

# Intitulés RRS 2025-2028 : repris de regles.json (ordre : fr, en, it, es, pt, de).
RRS_T = {
    "1": ("Sécurité", "Safety", "Sicurezza", "Seguridad", "Segurança", "Sicherheit"),
    "2": ("Esprit sportif et fair-play", "Fair Sailing", "Correttezza sportiva", "Navegación leal", "Navegação leal", "Faires Segeln"),
    "10": ("Sur des amures opposées", "On Opposite Tacks", "Su mure opposte", "En bordos opuestos", "Em amuras opostas", "Auf entgegengesetztem Bug"),
    "11": ("Sur la même amure, engagés", "On the Same Tack, Overlapped", "Sulla stessa mura, in overlap", "En el mismo bordo, con overlap", "Na mesma amura, com sobreposição", "Auf demselben Bug, überlappend"),
    "12": ("Sur la même amure, non engagés", "On the Same Tack, Not Overlapped", "Sulla stessa mura, non in overlap", "En el mismo bordo, sin overlap", "Na mesma amura, sem sobreposição", "Auf demselben Bug, nicht überlappend"),
    "13": ("En virant de bord", "While Tacking", "Durante la virata", "Mientras vira por avante", "Durante a viragem", "Beim Wenden"),
    "14": ("Éviter le contact", "Avoiding Contact", "Evitare il contatto", "Evitar el contacto", "Evitar o contacto", "Kontakt vermeiden"),
    "15": ("Acquérir la priorité", "Acquiring Right of Way", "Acquisire il diritto di rotta", "Adquirir el derecho de paso", "Adquirir o direito de passagem", "Wegerecht erwerben"),
    "16": ("Changer de route", "Changing Course", "Cambiare rotta", "Cambiar de rumbo", "Mudar de rumo", "Kursänderung"),
    "17": ("Sur la même amure ; route normale", "On the Same Tack; Proper Course", "Sulla stessa mura; rotta propria", "En el mismo bordo; rumbo propio", "Na mesma amura; rumo próprio", "Auf demselben Bug; Raumkurs"),
    "18": ("Place à la marque", "Mark-Room", "Spazio alla boa", "Espacio en la baliza", "Espaço na marca", "Raum an der Tonne"),
    "19": ("Place pour passer un obstacle", "Room to Pass an Obstruction", "Spazio per passare un ostacolo", "Espacio para pasar un obstáculo", "Espaço para passar um obstáculo", "Raum zum Passieren eines Hindernisses"),
    "20": ("Place pour virer à un obstacle", "Room to Tack at an Obstruction", "Spazio per virare a un ostacolo", "Espacio para virar en un obstáculo", "Espaço para virar num obstáculo", "Raum zum Wenden an einem Hindernis"),
    "26": ("Départ des courses", "Starting Races", "Partenza delle regate", "Salida de las regatas", "Partida das regatas", "Starten von Wettfahrten"),
    "28": ("Suivre le parcours", "Sailing the Course", "Seguire il percorso", "Navegar el recorrido", "Navegar o percurso", "Den Kurs segeln"),
    "29": ("Rappels", "Recalls", "Richiami", "Llamadas", "Chamadas", "Rückrufe"),
    "30": ("Pénalités au départ", "Starting Penalties", "Penalità di partenza", "Penalizaciones de salida", "Penalizações de partida", "Startstrafen"),
    "31": ("Toucher une marque", "Touching a Mark", "Toccare una boa", "Tocar una baliza", "Tocar numa marca", "Eine Tonne berühren"),
    "44": ("Pénalités au moment de l'incident", "Penalties at the Time of an Incident", "Penalità al momento dell'incidente", "Penalizaciones en el momento del incidente", "Penalizações no momento do incidente", "Strafen zum Zeitpunkt des Vorfalls"),
}
# Libellé affiché pour RRS : "RRS <n>" ; sous-alinéa quand la phrase ne porte que sur lui.
RRS_LIB = {"1": "1.1", "18": "18.2", "44": "44.1"}

# COLREG 1972 : intitulés du texte anglais officiel (OMI), identiques dans toutes les langues.
COL_T = {
    "5": "Look-out", "7": "Risk of Collision", "8": "Action to Avoid Collision", "12": "Sailing Vessels",
    "13": "Overtaking", "14": "Head-on Situation", "15": "Crossing Situation",
    "16": "Action by Give-way Vessel", "17": "Action by Stand-on Vessel",
    "18": "Responsibilities Between Vessels", "25": "Sailing Vessels Underway and Vessels Under Oars",
}
COL_LIB = {"12": "12 a)", "13": "13 a)", "14": "14 a)", "15": "15 a)", "17": "17 a)", "18": "18 a)", "25": "25 a)"}

# ── Les textes. Notation {id|texte} = lien vers lexique.html#id. ───────────────────────────────────────
TEXTES = {}

TEXTES["fr"] = {
    "titre": "Cours théoriques de voile",
    "desc": "Un cours de voile théorique, gratuit, en {n} chapitres : vocabulaire, allures, cap, marées, météo, balisage, RIPAM/COLREG et règles de course (RRS 2025-2028), avec exercices corrigés.",
    "h1": "Cours théoriques de voile",
    "intro": "Un cours complet et gratuit, du vocabulaire du bateau jusqu'aux notions de base du permis côtier, en {n} chapitres. Chaque chapitre ne suppose que les précédents : lisez-les dans l'ordre. Chaque règle est citée par son numéro et son intitulé exacts, avec ce qu'elle oblige ; chaque chapitre se termine par un exercice corrigé, et le cours par quatre questions de révision. Aucune inscription n'est demandée.",
    "sommaire": "Sommaire — {n} chapitres", "chap": "Chapitre", "regles": "Règles citées", "exo": "Exercice", "corr": "Correction",
    "haut": "↑ Sommaire", "rev": "Révision du cours", "rev_intro": "Quatre questions qui reprennent l'ensemble du cours.", "schema": "Schémas",
    "note": "Sources : Racing Rules of Sailing 2025-2028 (World Sailing, {lien}) ; COLREG 1972 (OMI), appliqué en France sous le nom de RIPAM, dont les intitulés sont ceux du texte anglais officiel ; balisage AISM/IALA, région A. Ces résumés ne remplacent pas les textes, qui font foi ; les cas particuliers ne sont pas traités, et le cours ne remplace ni une formation pratique ni l'examen.",
    "regles_texte": {
        "rrs:10": "Quand deux bateaux sont sur des amures opposées, le bateau bâbord amures s'écarte du bateau tribord amures.",
        "rrs:11": "Quand deux bateaux sont sur la même amure et engagés, le bateau au vent s'écarte du bateau sous le vent.",
        "rrs:12": "Quand deux bateaux sont sur la même amure et non engagés, le bateau qui est derrière s'écarte du bateau qui est devant.",
        "rrs:13": "Après être passé face au vent, un bateau s'écarte des autres jusqu'à ce qu'il soit au plus près ; pendant ce temps, les règles 10, 11 et 12 ne s'appliquent pas à lui.",
        "rrs:14": "Un bateau évite le contact avec un autre si c'est raisonnablement possible ; même prioritaire, il doit agir dès qu'il est clair que l'autre ne s'écarte pas.",
        "rrs:15": "Quand un bateau acquiert la priorité, il laisse d'abord à l'autre la place de s'écarter, sauf si c'est l'action de l'autre qui la lui donne.",
        "rrs:16": "Quand un bateau prioritaire change de route, il laisse à l'autre la place de s'écarter.",
        "rrs:17": "Si un bateau qui était derrière devient engagé à moins de deux longueurs de coque sous le vent d'un bateau sur la même amure, il ne doit pas naviguer plus haut que sa route normale, sauf s'il passe promptement derrière l'autre.",
        "rrs:18": "Quand des bateaux doivent laisser une marque du même côté et que l'un d'eux est dans la zone (trois longueurs de coque), le bateau extérieur, s'ils sont engagés, donne la place à la marque au bateau intérieur.",
        "rrs:19": "Quand des bateaux engagés passent un obstacle, le bateau extérieur donne au bateau intérieur la place de passer entre lui et l'obstacle.",
        "rrs:20": "Un bateau qui approche d'un obstacle peut héler pour avoir la place de virer ; le bateau hélé répond en virant aussitôt ou en disant « Vire », puis il laisse cette place.",
        "rrs:44": "Un bateau qui a peut-être enfreint une règle de la partie 2 ou la règle 31 peut s'exonérer en effectuant promptement une pénalité d'un tour (un virement et un empannage) après s'être écarté des autres ; en cas de dommage grave ou d'avantage significatif, la pénalité est l'abandon.",
        "rrs:2": "Les bateaux et leurs propriétaires s'affrontent selon les principes reconnus de sportivité et de franc-jeu ; un bateau n'est pénalisé sur ce fondement que s'il est clairement établi qu'il les a enfreints.",
        "rrs:1": "Un bateau ou un concurrent apporte toute l'aide possible à toute personne ou tout navire en danger.",
        "rrs:26": "Le départ suit une séquence de signaux : avertissement cinq minutes avant le signal de départ, préparatoire quatre minutes avant, retrait du pavillon préparatoire une minute avant, départ à zéro ; ce sont les signaux visuels qui font foi, pas le son.",
        "rrs:29": "Si un bateau est du côté parcours de la ligne au signal, le comité hisse le pavillon X (rappel individuel) ; s'il ne peut pas identifier les bateaux ou si la procédure est fautive, il hisse le Premier Substitut (rappel général).",
        "rrs:30": "Quand le pavillon I est envoyé, un bateau qui, pendant la dernière minute avant son signal de départ, a une partie de sa coque, de son équipage ou de son équipement du côté parcours de la ligne, doit repasser côté avant-départ par un prolongement de la ligne avant de partir.",
        "rrs:28": "Un bateau part, suit le parcours décrit dans les instructions de course, puis finit.",
        "rrs:31": "Pendant la course, un bateau ne touche pas une marque de départ avant son départ, une marque qui commence, délimite ou termine le bord sur lequel il navigue, ni une marque d'arrivée après avoir fini.",
        "col:5": "Tout navire maintient en permanence une veille appropriée, visuelle et auditive, par tous les moyens disponibles.",
        "col:7": "Un navire utilise tous les moyens disponibles pour déterminer s'il y a risque d'abordage ; en cas de doute, ce risque est réputé exister, notamment si le relèvement d'un navire qui approche ne change pas de façon appréciable.",
        "col:8": "Une manœuvre pour éviter l'abordage est franche, faite largement à temps et assez ample pour être vue de l'autre navire ; on évite une succession de petits changements.",
        "col:12": "Deux voiliers : s'ils reçoivent le vent de bords différents, celui qui le reçoit par bâbord s'écarte de la route de l'autre ; s'ils le reçoivent du même bord, le voilier au vent s'écarte de la route du voilier sous le vent.",
        "col:13": "Tout navire qui en rattrape un autre s'écarte de sa route ; est rattrapant celui qui arrive de plus de 22,5° sur l'arrière du travers de l'autre.",
        "col:14": "Deux navires à propulsion mécanique qui se présentent debout à debout modifient chacun leur route sur tribord et se croisent bâbord contre bâbord.",
        "col:15": "Deux navires à propulsion mécanique dont les routes se croisent : celui qui voit l'autre sur tribord s'écarte et évite, si possible, de passer devant lui.",
        "col:16": "Le navire qui doit s'écarter de la route d'un autre agit le plus tôt possible et franchement pour passer bien à l'écart.",
        "col:17": "Le navire qui n'a pas à s'écarter conserve cap et vitesse ; il peut manœuvrer dès qu'il est évident que l'autre ne s'écarte pas, et il doit le faire si l'abordage ne peut plus être évité par la seule manœuvre de l'autre.",
        "col:18": "Un navire à propulsion mécanique faisant route s'écarte de la route d'un navire à voile (ainsi que d'un navire qui ne gouverne pas, à capacité de manœuvre restreinte ou qui pêche).",
        "col:25": "Un navire à voile faisant route montre des feux de côté (rouge à bâbord, vert à tribord) et un feu de poupe blanc.",
    },
    "ch": {
        "vocabulaire": {
            "t": "Le bateau et son vocabulaire",
            "p": ["Un voilier se décrit par ses parties. La {coque|coque} est le corps du bateau ; l'{etrave|étrave} en est l'avant, l'{etambot|étambot} l'arrière. Le {pont|pont} la recouvre, et le {cockpit|cockpit} est l'espace où l'on s'installe pour barrer.",
                  "Quand on regarde vers l'avant, {babord|bâbord} est à gauche (feu rouge, la nuit) et {tribord|tribord} à droite (feu vert).",
                  "Le {mat|mât} porte les voiles : la {grand-voile|grand-voile}, fixée au mât et à la {bome|bôme}, et, à l'avant, le {foc|foc} ou le {genois|génois}. On les monte avec les {drisse|drisses} et on les règle avec les {ecoute|écoutes}. À bord, une corde s'appelle un {bout|bout}.",
                  "Sous l'eau, la {quille|quille} limite la dérive et son {lest|lest} redresse le bateau ; le {safran|safran}, commandé par la {barre|barre}, le dirige."],
            "q": "Vous êtes à la barre et regardez vers l'étrave. De quel côté est tribord, et quelle couleur de feu y est placée la nuit ?",
            "a": "À droite ; le feu de tribord est vert (bâbord, à gauche, porte le feu rouge).",
        },
        "vent": {
            "t": "Le vent et les allures",
            "p": ["Le vent se nomme d'après le point d'où il vient : un vent du nord souffle vers le sud. Le côté d'où il vient se dit {au-vent|au vent} ; le côté opposé, {sous-le-vent|sous le vent}.",
                  "Un voilier ne peut pas avancer face au vent : de part et d'autre de cette direction, sur environ 45 degrés, s'étend la {zone-de-non-vent|zone de non-vent}. Il avance dans toutes les autres directions, appelées {allure|allures}.",
                  "De la plus proche du vent à la plus éloignée : le {pres|près} (environ 45° du vent), le {bon-plein|bon plein}, le {travers|travers} (90°), le {largue|largue} (environ 120° à 135°) et le {vent-arriere|vent arrière} (180°).",
                  "L'amure dit de quel côté le vent arrive : {tribord-amures|tribord amures} s'il arrive par la droite du bateau, {babord-amures|bâbord amures} par la gauche.",
                  "À bord, on sent le {vent-apparent|vent apparent}, somme du {vent-reel|vent réel} et du vent créé par l'avancée du bateau ; il semble venir plus de l'avant que le vent réel."],
            "q": "Le vent arrive de la droite, perpendiculairement à l'axe du bateau. Quelle allure, quelle amure ?",
            "a": "Le travers, tribord amures (le vent arrive par tribord).",
        },
        "manoeuvres": {
            "t": "Régler les voiles et manœuvrer",
            "p": ["On règle les voiles selon l'allure : on {border|borde} (on tire l'écoute) pour aller vers le vent, on {choquer|choque} (on relâche) pour s'en éloigner. Une voile qui {faseyer|fasaye}, c'est-à-dire qui bat, est trop choquée.",
                  "Pour changer de direction : {lofer|lofer}, c'est se rapprocher du vent ; {abattre|abattre}, c'est s'en éloigner.",
                  "{virer|Virer} de bord, c'est faire passer l'avant du bateau face au vent ; on prévient l'équipage par « {pare-a-virer|pare à virer} ». {empanner|Empanner}, c'est faire passer l'arrière dans l'axe du vent : la bôme traverse le bateau d'un bord à l'autre, ce qui est dangereux ; on annonce « {pare-a-empanner|pare à empanner} » et on respecte la consigne {attention-a-la-bome|attention à la bôme}.",
                  "Quand le vent forcit, le bateau {gite|gîte} davantage : on choque les écoutes, on lofe doucement, ou l'on {prendre-un-ris|prend un ris}, c'est-à-dire que l'on réduit la surface de la grand-voile."],
            "q": "Le vent forcit et le bateau gîte trop. Citez deux gestes pour le soulager.",
            "a": "Choquer les écoutes (surtout la grand-voile) et prendre un ris ; on peut aussi lofer un peu pour que les voiles portent moins.",
        },
        "cap": {
            "t": "Cap, distance et carte",
            "p": ["Le {cap|cap} est la direction du bateau, en degrés de 0 à 360 à partir du nord : 090° est plein est, 180° plein sud, 270° plein ouest.",
                  "Le {noeud-vitesse|nœud} est l'unité de vitesse : un mille nautique par heure. Un mille vaut 1 852 mètres, soit une minute de latitude, que l'on lit sur l'échelle verticale de la carte. Distance = vitesse × temps.",
                  "Le compas donne le cap compas. Corrigé de la déviation (propre au bateau), il donne le cap magnétique ; corrigé de la déclinaison (écart entre nord magnétique et nord vrai, indiquée sur la carte), il donne le cap vrai, celui que l'on trace sur la carte. Une déclinaison ouest se compte en négatif : cap vrai = cap magnétique + déclinaison.",
                  "Le vent et le courant écartent le bateau de sa trajectoire : c'est la {derive|dérive}. La {route-fond|route fond} est la route réellement suivie sur le fond, différente du cap."],
            "q": "Vous naviguez à 6 nœuds. En combien de temps parcourez-vous 15 milles ?",
            "a": "15 ÷ 6 = 2,5 heures, soit 2 h 30.",
        },
        "marees": {
            "t": "Marées et courants",
            "p": ["La {maree|marée} est la montée et la descente de la mer, deux fois par jour environ. La mer monte pendant le {flot|flot} jusqu'à la {pleine-mer|pleine mer}, puis descend pendant le {jusant|jusant} jusqu'à la {basse-mer|basse mer}. Il s'écoule environ six heures entre une pleine mer et une basse mer.",
                  "Le {marnage|marnage} est la différence de hauteur entre pleine mer et basse mer. À l'{etale|étale}, au moment de la renverse, il n'y a presque pas de {courant|courant} de marée.",
                  "La règle des douzièmes estime la hauteur en cours de marée : sur le marnage, l'eau monte de 1/12 la première heure, 2/12 la deuxième, 3/12 la troisième, 3/12 la quatrième, 2/12 la cinquième, 1/12 la sixième.",
                  "Le courant de marée porte le bateau : favorable, il aide ; contraire, il freine. Quand le courant est contre le vent, la mer devient plus courte et plus creuse."],
            "q": "Le marnage est de 6 m. De combien l'eau est-elle montée après deux heures de flot ?",
            "a": "1/12 + 2/12 = 3/12, soit 1/4 de 6 m : 1,5 m.",
        },
        "meteo": {
            "t": "La météo",
            "p": ["L'échelle de {beaufort|Beaufort} classe le vent de 0 à 12 : force 4 = 11 à 16 nœuds, force 6 = 22 à 27 nœuds, force 8 = 34 à 40 nœuds (coup de vent). Au-delà de force 6, la navigation demande de l'expérience.",
                  "Un {anticyclone|anticyclone} est une zone de hautes pressions (au-dessus d'environ 1 013 hPa) : temps stable, vent faible. Une {depression|dépression} est une zone de basses pressions : nuages, pluie, vent plus fort. Dans l'hémisphère nord, le vent tourne autour d'un anticyclone dans le sens des aiguilles d'une montre, autour d'une dépression dans le sens inverse.",
                  "Avant de partir, on lit le {bulletin-meteo|bulletin météo} : vent moyen, {rafale|rafales}, état de la mer. Un {grain|grain} est un coup de vent bref accompagné de pluie ; l'{orage|orage} impose de rentrer.",
                  "Près des côtes, en été, la {brise-de-mer|brise de mer} souffle l'après-midi vers la terre ; la {brise-de-terre|brise de terre} souffle la nuit vers le large. La {houle|houle} est une vague longue venue de loin ; le {clapot|clapot}, une mer courte et désordonnée."],
            "q": "Le bulletin annonce « vent de force 6, rafales à 8 ». Convertissez la force 6 en nœuds et dites ce que signifie la force 8.",
            "a": "Force 6 : 22 à 27 nœuds. Force 8 : 34 à 40 nœuds, un coup de vent — à éviter pour un équipage débutant.",
        },
        "balisage": {
            "t": "Balisage et feux",
            "p": ["Le balisage guide et prévient des dangers. En Europe, on suit le système AISM/IALA, région A. Les marques latérales bordent un chenal ; on les décrit dans le sens conventionnel, quand on entre dans un port en venant du large.",
                  "Marque de bâbord : rouge, cylindrique (on la laisse à bâbord). Marque de tribord : verte, conique (on la laisse à tribord). En rentrant, on voit donc rouge à gauche et vert à droite ; en sortant, c'est l'inverse.",
                  "Une marque cardinale porte le nom du côté où se trouve l'eau saine : une cardinale Nord se passe au nord d'elle. Nord : noire au-dessus, jaune en dessous ; Sud : jaune au-dessus, noire en dessous ; Est : noir-jaune-noir ; Ouest : jaune-noir-jaune.",
                  "Une {bouee|bouée} noire à bandes rouges marque un danger isolé (on l'évite largement) ; une bouée à bandes verticales rouges et blanches, des eaux saines ; une marque jaune, une zone spéciale.",
                  "De nuit, un voilier faisant route à la voile porte un feu rouge à bâbord, un feu vert à tribord et un feu blanc à l'arrière ; sous moteur, il ajoute un feu blanc de tête de mât."],
            "q": "Vous rentrez au port, venant du large, et voyez une bouée rouge cylindrique. De quel côté la laissez-vous ?",
            "a": "À bâbord (rouge à gauche en entrant).",
        },
        "abordage": {
            "t": "Éviter l'abordage en mer (RIPAM / COLREG)",
            "p": ["Le RIPAM (en anglais COLREG) est le règlement international de 1972 pour prévenir les abordages en mer. Il s'applique à tous les navires, voiliers compris ; pendant une régate, ce sont les règles de course qui régissent les concurrents entre eux (chapitres 9 à 11).",
                  "Trois devoirs précèdent toute règle de priorité : veiller (règle 5), reconnaître le risque d'abordage — si le relèvement d'un navire qui approche ne change pas, le risque existe (règle 7) — et agir tôt et franchement (règle 8).",
                  "Retenez deux rôles : le navire qui doit s'écarter manœuvre tôt et nettement ; l'autre conserve cap et vitesse tant que le premier agit.",
                  "En résumé, à voile : vent de bords différents, c'est celui qui reçoit le vent par bâbord qui s'écarte ; du même bord, celui qui est au vent s'écarte ; qui rattrape s'écarte ; un bateau à moteur s'écarte d'un voilier."],
            "q": "Deux voiliers se croisent en mer, hors régate. Le premier reçoit le vent par tribord, le second par bâbord. Lequel s'écarte, et selon quelle règle ?",
            "a": "Celui qui reçoit le vent par bâbord s'écarte (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Régate : le départ et le parcours",
            "p": ["Une régate est organisée par le {comite-de-course|comité de course}, qui installe depuis son {bateau-comite|bateau} la {ligne-de-depart|ligne de départ} : l'espace entre le bateau comité et une {marque-de-depart|marque de départ} (une bouée). Avant le {signal-de-depart|signal de départ}, on reste du côté « avant-départ » de la ligne.",
                  "Si un bateau est du côté parcours de la ligne au signal, c'est un {faux-depart|faux départ} : il doit revenir et repartir. Si le comité ne peut pas identifier les fautifs, il annule le départ par un {rappel-general|rappel général}.",
                  "Le {parcours|parcours}, décrit dans les instructions de course, enchaîne en général : départ, remontée jusqu'à la {bouee-au-vent|bouée au vent}, descente vers la {bouee-sous-le-vent|bouée sous le vent} ou une {porte|porte}, parfois plusieurs tours, puis {arrivee|arrivée} sur la {ligne-d-arrivee|ligne d'arrivée}."],
            "q": "À votre départ, le comité hisse le pavillon X avec un son. Que signifie-t-il pour vous, et que faites-vous ?",
            "a": "C'est un rappel individuel (RRS 29) : au signal, une partie de votre bateau était du côté parcours. Vous revenez entièrement du côté avant-départ, puis vous franchissez la ligne ; tant que vous ne l'avez pas fait, vous n'avez pas pris le départ.",
        },
        "priorites": {
            "t": "Régate : les priorités",
            "p": ["En régate, la partie 2 des {regles-de-course|règles de course} dit qui doit s'écarter de qui. Deux notions suffisent pour la lire : l'amure (chapitre 2) et l'engagement. Un bateau est « derrière » l'autre quand sa coque est entièrement en arrière d'une ligne perpendiculaire à l'axe de l'autre, passant par le point le plus arrière de celui-ci ; sinon, les bateaux sont engagés.",
                  "On lit les règles dans l'ordre : amures opposées (10) ; même amure, engagés (11) ou non engagés (12). Le virement de bord (13) passe en premier. Les règles 14 à 17 limitent les droits que donnent les règles 10 à 13.",
                  "Un bateau qui a la {priorite|priorité} peut garder sa route, mais ne doit pas la changer sans laisser à l'autre la place de s'écarter. Si l'on pense qu'une règle a été enfreinte, on peut la signaler : c'est la {protestation|protestation}."],
            "q": "A est tribord amures, B bâbord amures ; leurs routes convergent. B voit qu'A ne change pas de route. Qui s'écarte, selon quelle règle ? Que doit faire A s'il voit que B ne s'écarte pas ?",
            "a": "B s'écarte (RRS 10). A, bien que prioritaire, doit éviter le contact dès qu'il est clair que B ne s'écarte pas (RRS 14).",
        },
        "marques": {
            "t": "Régate : marques, obstacles et pénalités",
            "p": ["Aux marques, le jeu se resserre. La zone est le cercle de trois longueurs de coque autour de la marque. Quand deux bateaux doivent laisser la marque du même côté et que l'un est dans la zone, la règle 18 s'applique.",
                  "La place à la marque, c'est la place de naviguer jusqu'à la marque, puis de la contourner du côté requis. Les obstacles (rocher, bateau au mouillage…) ont leurs règles propres (19 et 20).",
                  "Un bateau qui pense avoir enfreint une règle peut s'exonérer sur l'eau, sans attendre : il effectue une {penalite|pénalité} d'un {tour-de-penalite|tour}. Sinon, l'autre bateau peut protester et un {jury|jury} tranche après la course.",
                  "Quelle que soit la règle, l'esprit sportif prime : on ne gagne pas en trichant."],
            "q": "Deux bateaux engagés arrivent à une marque à laisser à bâbord ; A est à l'intérieur, B à l'extérieur, et l'un d'eux est dans la zone. Qui doit donner la place à la marque ?",
            "a": "B, le bateau extérieur, donne à A, intérieur, la place à la marque (RRS 18).",
        },
        "securite": {
            "t": "Sécurité en mer",
            "p": ["Avant de partir : lire le {bulletin-meteo|bulletin météo}, vérifier le matériel, donner l'heure de retour prévue à un proche. À bord, chaque personne a un gilet de sauvetage adapté, que l'on porte dès que les conditions l'imposent.",
                  "Trois niveaux d'appel à la VHF, sur le canal 16 (veille de détresse) : MAYDAY (dit trois fois) pour un danger grave et imminent ; PAN PAN pour une urgence sans danger immédiat ; SÉCURITÉ pour un avertissement de navigation ou de météo.",
                  "En France, les secours en mer sont coordonnés par les CROSS, joignables sur le canal 16 ou, depuis un téléphone portable, au 196.",
                  "{homme-a-la-mer|Homme à la mer} : crier « homme à la mer », lui lancer une bouée, désigner une personne qui ne le quitte jamais des yeux, puis lancer l'alerte. Il existe plusieurs méthodes de récupération : apprenez-en une en pratique, avec un moniteur."],
            "q": "Quand utilise-t-on MAYDAY, et quand PAN PAN ?",
            "a": "MAYDAY : danger grave et imminent pour une personne ou le bateau. PAN PAN : urgence sans danger immédiat, par exemple une avarie dont on maîtrise la situation.",
        },
    },
    "revision": [
        ("Vous faites route au 270° (plein ouest) avec un vent du nord. Quelle allure, quelle amure ?", "Le nord est à votre droite : le vent arrive par tribord, perpendiculairement — c'est le travers, tribord amures."),
        ("Le marnage est de 8 m. De combien l'eau monte-t-elle pendant la troisième heure du flot ?", "3/12 de 8 m = 2 m."),
        ("Deux voiliers sont sur la même amure ; A est au vent de B. Qui s'écarte, en mer hors course puis en régate ?", "A, dans les deux cas : COLREG 12 a) ii) en mer, RRS 11 en régate (bateaux engagés)."),
        ("Quelle marque latérale laisse-t-on à tribord en entrant au port ? Et que dit-on à la VHF pour un danger grave et imminent ?", "La verte, conique. « MAYDAY », trois fois, sur le canal 16."),
    ],
}

TEXTES["en"] = {
    "titre": "Sailing theory course",
    "desc": "A free sailing theory course in {n} chapters: vocabulary, points of sail, course, tides, weather, buoyage, COLREG and the Racing Rules of Sailing (RRS 2025-2028), with worked exercises.",
    "h1": "Sailing theory course",
    "intro": "A complete, free course from the vocabulary of the boat to the basic notions of a coastal licence, in {n} chapters. Each chapter assumes only the previous ones: read them in order. Every rule is cited by its exact number and title, with what it requires; each chapter ends with a corrected exercise, and the course with four review questions. No sign-up is asked.",
    "sommaire": "Contents — {n} chapters", "chap": "Chapter", "regles": "Rules cited", "exo": "Exercise", "corr": "Answer",
    "haut": "↑ Contents", "rev": "Course review", "rev_intro": "Four questions covering the whole course.", "schema": "Diagrams",
    "note": "Sources: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO), titles as in the official English text; IALA buoyage, region A. These summaries do not replace the texts, which prevail; special cases are not covered, and the course replaces neither practical training nor the exam.",
    "regles_texte": {
        "rrs:10": "When boats are on opposite tacks, a port-tack boat keeps clear of a starboard-tack boat.",
        "rrs:11": "When boats are on the same tack and overlapped, a windward boat keeps clear of a leeward boat.",
        "rrs:12": "When boats are on the same tack and not overlapped, a boat clear astern keeps clear of a boat clear ahead.",
        "rrs:13": "After a boat passes head to wind, she keeps clear of other boats until she is on a close-hauled course; during that time rules 10, 11 and 12 do not apply to her.",
        "rrs:14": "A boat avoids contact with another boat if reasonably possible; even with right of way, she must act as soon as it is clear that the other boat is not keeping clear.",
        "rrs:15": "When a boat acquires right of way, she first gives the other boat room to keep clear, unless she acquires it through the other boat's actions.",
        "rrs:16": "When a right-of-way boat changes course, she gives the other boat room to keep clear.",
        "rrs:17": "If a boat clear astern becomes overlapped within two hull lengths to leeward of a boat on the same tack, she must not sail above her proper course, unless she promptly sails astern of the other boat.",
        "rrs:18": "When boats must leave a mark on the same side and one of them is in the zone (three hull lengths), the outside boat, if they are overlapped, gives the inside boat mark-room.",
        "rrs:19": "When overlapped boats pass an obstruction, the outside boat gives the inside boat room to pass between her and the obstruction.",
        "rrs:20": "A boat approaching an obstruction may hail for room to tack; the hailed boat either tacks at once or replies “You tack”, and then gives that room.",
        "rrs:44": "A boat that may have broken a rule of Part 2 or rule 31 may exonerate herself by promptly taking a One-Turn Penalty (one tack and one gybe) after clearing other boats; if she caused serious damage or gained a significant advantage, her penalty is to retire.",
        "rrs:2": "Boats and their owners compete under recognized principles of sportsmanship and fair play; a boat is penalized under this rule only if it is clearly established that she broke them.",
        "rrs:1": "A boat or competitor gives all possible help to any person or vessel in danger.",
        "rrs:26": "The start follows a sequence of signals: warning five minutes before the starting signal, preparatory four minutes before, preparatory flag removed one minute before, start at zero; times are taken from the visual signals, not the sound.",
        "rrs:29": "If a boat is on the course side of the line at her starting signal, the committee displays flag X (individual recall); if it cannot identify the boats or the procedure is wrong, it displays First Substitute (general recall).",
        "rrs:30": "When flag I is displayed, a boat that has any part of her hull, crew or equipment on the course side of the line during the last minute before her starting signal must sail back across an extension of the line to the pre-start side before starting.",
        "rrs:28": "A boat starts, sails the course described in the sailing instructions, and finishes.",
        "rrs:31": "While racing, a boat does not touch a starting mark before starting, a mark that begins, bounds or ends the leg she is sailing, or a finishing mark after finishing.",
        "col:5": "Every vessel at all times maintains a proper look-out by sight and hearing and by all available means.",
        "col:7": "A vessel uses all available means to determine whether risk of collision exists; in case of doubt such risk is deemed to exist, notably if the bearing of an approaching vessel does not appreciably change.",
        "col:8": "Action to avoid collision is positive, made in ample time and large enough to be readily apparent to the other vessel; a succession of small alterations is avoided.",
        "col:12": "Two sailing vessels: when each has the wind on a different side, the one with the wind on the port side keeps out of the way of the other; when both have it on the same side, the windward vessel keeps out of the way of the leeward vessel.",
        "col:13": "Any vessel overtaking another keeps out of the way of the vessel being overtaken; a vessel is overtaking when coming up from more than 22.5 degrees abaft the other's beam.",
        "col:14": "Two power-driven vessels meeting head-on each alter course to starboard and pass port side to port side.",
        "col:15": "Two power-driven vessels crossing: the vessel which has the other on her starboard side keeps out of the way and, if possible, avoids crossing ahead of her.",
        "col:16": "The vessel required to keep out of the way acts as early as possible and substantially, to keep well clear.",
        "col:17": "The vessel not required to keep out of the way keeps her course and speed; she may act as soon as it is apparent that the other is not keeping clear, and must do so if collision can no longer be avoided by the other's action alone.",
        "col:18": "A power-driven vessel underway keeps out of the way of a sailing vessel (and of a vessel not under command, restricted in her ability to manoeuvre, or fishing).",
        "col:25": "A sailing vessel underway shows sidelights (red to port, green to starboard) and a white sternlight.",
    },
    "ch": {
        "vocabulaire": {
            "t": "The boat and its vocabulary",
            "p": ["A sailboat is described by its parts. The {coque|hull} is the body of the boat; the {etrave|bow} is its front, the {etambot|stern} its back. The {pont|deck} covers it, and the {cockpit|cockpit} is where you sit to steer.",
                  "Looking forward, {babord|port} is on the left (red light at night) and {tribord|starboard} on the right (green light).",
                  "The {mat|mast} carries the sails: the {grand-voile|mainsail}, attached to the mast and to the {bome|boom}, and at the front the {foc|jib} or the {genois|genoa}. They are hoisted with {drisse|halyards} and trimmed with {ecoute|sheets}. On board, a rope is called a {bout|line}.",
                  "Underwater, the {quille|keel} limits leeway and its {lest|ballast} rights the boat; the {safran|rudder}, moved by the {barre|tiller or wheel}, steers it."],
            "q": "You are steering, looking toward the bow. Which side is starboard, and what colour of light is there at night?",
            "a": "The right; the starboard light is green (port, on the left, carries the red light).",
        },
        "vent": {
            "t": "The wind and the points of sail",
            "p": ["The wind is named after where it comes from: a north wind blows toward the south. The side it comes from is the {au-vent|windward} side; the opposite side is {sous-le-vent|leeward}.",
                  "A sailboat cannot sail straight into the wind: on each side of that direction, over about 45 degrees, lies the {zone-de-non-vent|no-go zone}. It sails in all other directions, called {allure|points of sail}.",
                  "From closest to the wind to farthest: {pres|close-hauled} (about 45° from the wind), the {bon-plein|close reach}, the {travers|beam reach} (90°), the {largue|broad reach} (about 120° to 135°) and the {vent-arriere|run} (180°).",
                  "The tack says which side the wind comes from: {tribord-amures|starboard tack} if it comes over the right side of the boat, {babord-amures|port tack} over the left.",
                  "On board you feel the {vent-apparent|apparent wind}, the sum of the {vent-reel|true wind} and the wind created by the boat's motion; it seems to come more from ahead than the true wind."],
            "q": "The wind comes from the right, perpendicular to the boat's axis. Which point of sail, which tack?",
            "a": "A beam reach, starboard tack (the wind comes over the starboard side).",
        },
        "manoeuvres": {
            "t": "Trimming the sails and manoeuvring",
            "p": ["Sails are set according to the point of sail: you {border|sheet in} (pull the sheet) to go toward the wind, you {choquer|ease} (let it out) to go away from it. A sail that {faseyer|flaps} is eased too much.",
                  "To change direction: to {lofer|luff up} is to turn toward the wind; to {abattre|bear away} is to turn away from it.",
                  "To {virer|tack} is to bring the bow through the wind; the crew is warned with “{pare-a-virer|ready about}”. To {empanner|gybe} is to bring the stern through the wind: the boom swings across the boat, which is dangerous; you call “{pare-a-empanner|ready to gybe}” and heed {attention-a-la-bome|mind the boom}.",
                  "When the wind rises, the boat {gite|heels} more: you ease the sheets, luff gently, or {prendre-un-ris|reef}, that is, reduce the area of the mainsail."],
            "q": "The wind is rising and the boat heels too much. Name two actions to relieve it.",
            "a": "Ease the sheets (especially the mainsail) and take a reef; you can also luff up a little so the sails pull less.",
        },
        "cap": {
            "t": "Course, distance and chart",
            "p": ["The {cap|heading} is the direction of the boat, in degrees from 0 to 360 from north: 090° is due east, 180° due south, 270° due west.",
                  "The {noeud-vitesse|knot} is the unit of speed: one nautical mile per hour. A mile is 1,852 metres, one minute of latitude, read on the chart's vertical scale. Distance = speed × time.",
                  "The compass gives the compass heading. Corrected for deviation (specific to the boat) it gives the magnetic heading; corrected for variation (the gap between magnetic and true north, given on the chart) it gives the true heading, the one you plot on the chart. West variation counts as negative: true = magnetic + variation.",
                  "Wind and current push the boat off its track: that is {derive|leeway and drift}. The {route-fond|course over the ground} is the route actually followed over the seabed, different from the heading."],
            "q": "You sail at 6 knots. How long does it take to cover 15 miles?",
            "a": "15 ÷ 6 = 2.5 hours, i.e. 2 h 30.",
        },
        "marees": {
            "t": "Tides and currents",
            "p": ["The {maree|tide} is the rise and fall of the sea, about twice a day. The sea rises during the {flot|flood} up to {pleine-mer|high water}, then falls during the {jusant|ebb} to {basse-mer|low water}. About six hours pass between high and low water.",
                  "The {marnage|tidal range} is the height difference between high and low water. At {etale|slack water}, at the turn, there is almost no tidal {courant|current}.",
                  "The rule of twelfths estimates the height during the tide: of the range, the water rises 1/12 in the first hour, 2/12 in the second, 3/12 in the third, 3/12 in the fourth, 2/12 in the fifth, 1/12 in the sixth.",
                  "The tidal current carries the boat: fair, it helps; foul, it slows. When current runs against wind, the sea becomes shorter and steeper."],
            "q": "The tidal range is 6 m. How far has the water risen after two hours of flood?",
            "a": "1/12 + 2/12 = 3/12, i.e. 1/4 of 6 m: 1.5 m.",
        },
        "meteo": {
            "t": "Weather",
            "p": ["The {beaufort|Beaufort} scale ranks wind from 0 to 12: force 4 = 11 to 16 knots, force 6 = 22 to 27 knots, force 8 = 34 to 40 knots (gale). Beyond force 6, sailing takes experience.",
                  "An {anticyclone|anticyclone} is a high-pressure area (above about 1,013 hPa): stable weather, light wind. A {depression|depression} is a low-pressure area: clouds, rain, stronger wind. In the northern hemisphere, the wind circles clockwise around a high and anticlockwise around a low.",
                  "Before leaving, read the {bulletin-meteo|weather forecast}: mean wind, {rafale|gusts}, sea state. A {grain|squall} is a brief burst of wind with rain; a {orage|thunderstorm} means heading in.",
                  "Near the coast in summer, the {brise-de-mer|sea breeze} blows toward land in the afternoon; the {brise-de-terre|land breeze} blows toward the sea at night. {houle|Swell} is a long wave from far away; {clapot|chop} is a short, disordered sea."],
            "q": "The forecast says “wind force 6, gusts 8”. Convert force 6 to knots and say what force 8 means.",
            "a": "Force 6: 22 to 27 knots. Force 8: 34 to 40 knots, a gale — to be avoided by a beginner crew.",
        },
        "balisage": {
            "t": "Buoyage and lights",
            "p": ["Buoyage guides and warns of dangers. In Europe we follow the IALA system, region A. Lateral marks line a channel; they are described in the conventional direction, when entering a harbour from seaward.",
                  "Port-hand mark: red, cylindrical (left on your port side). Starboard-hand mark: green, conical (left on your starboard side). Entering, you see red to the left and green to the right; leaving, it is the opposite.",
                  "A cardinal mark is named after the side where the safe water lies: a North cardinal is passed to the north of it. North: black above, yellow below; South: yellow above, black below; East: black-yellow-black; West: yellow-black-yellow.",
                  "A black {bouee|buoy} with red bands marks an isolated danger (stay well clear); a buoy with red and white vertical stripes, safe water; a yellow mark, a special area.",
                  "At night, a sailing boat under sail shows a red light to port, a green light to starboard and a white light at the stern; under engine she adds a white masthead light."],
            "q": "You are entering harbour from seaward and see a red cylindrical buoy. Which side do you leave it?",
            "a": "To port (red to the left when entering).",
        },
        "abordage": {
            "t": "Avoiding collisions at sea (COLREG)",
            "p": ["COLREG is the 1972 international regulation for preventing collisions at sea (RIPAM in French). It applies to all vessels, sailboats included; during a race, the racing rules govern competitors among themselves (chapters 9 to 11).",
                  "Three duties come before any right-of-way rule: keep a look-out (rule 5), recognise risk of collision — if the bearing of an approaching vessel does not change, risk exists (rule 7) — and act early and clearly (rule 8).",
                  "Remember two roles: the vessel that must keep out of the way acts early and clearly; the other keeps course and speed as long as the first acts.",
                  "In short, under sail: wind on different sides, the one with wind on the port side gives way; same side, the windward boat gives way; the overtaking boat gives way; a power boat gives way to a sailboat."],
            "q": "Two sailboats cross at sea, outside a race. The first has the wind on starboard, the second on port. Which gives way, and under which rule?",
            "a": "The one with the wind on port gives way (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Racing: the start and the course",
            "p": ["A race is run by the {comite-de-course|race committee}, which sets, from its {bateau-comite|committee boat}, the {ligne-de-depart|starting line}: the space between the committee boat and a {marque-de-depart|starting mark} (a buoy). Before the {signal-de-depart|starting signal}, you stay on the pre-start side of the line.",
                  "If a boat is on the course side of the line at the signal, it is an {faux-depart|early start}: she must return and start again. If the committee cannot identify the boats, it abandons the start with a {rappel-general|general recall}.",
                  "The {parcours|course}, described in the sailing instructions, generally goes: start, beat to the {bouee-au-vent|windward mark}, run to the {bouee-sous-le-vent|leeward mark} or a {porte|gate}, sometimes several laps, then {arrivee|finish} on the {ligne-d-arrivee|finishing line}."],
            "q": "At your start, the committee displays flag X with one sound. What does it mean for you, and what do you do?",
            "a": "It is an individual recall (RRS 29): at the signal, part of your boat was on the course side. You sail back entirely to the pre-start side, then cross the line; until you have, you have not started.",
        },
        "priorites": {
            "t": "Racing: right of way",
            "p": ["In a race, Part 2 of the {regles-de-course|racing rules} says who keeps clear of whom. Two notions are enough to read it: the tack (chapter 2) and overlap. A boat is “clear astern” of another when her hull is entirely behind a line abeam of the other's aftermost point; otherwise the boats are overlapped.",
                  "Read the rules in order: opposite tacks (10); same tack, overlapped (11) or not overlapped (12). A boat that is tacking (13) comes first. Rules 14 to 17 limit the rights that rules 10 to 13 give.",
                  "A boat with {priorite|right of way} may hold her course, but must not change it without giving the other room to keep clear. If you think a rule was broken, you can report it: that is a {protestation|protest}."],
            "q": "A is on starboard tack, B on port tack; their courses converge. B sees A is not altering course. Who keeps clear, under which rule? What must A do if she sees B is not keeping clear?",
            "a": "B keeps clear (RRS 10). A, though she has right of way, must avoid contact as soon as it is clear B is not keeping clear (RRS 14).",
        },
        "marques": {
            "t": "Racing: marks, obstructions and penalties",
            "p": ["At marks, things tighten. The zone is the circle of three hull lengths around the mark. When two boats must leave the mark on the same side and one is in the zone, rule 18 applies.",
                  "Mark-room is room to sail to the mark, then to round it on the required side. Obstructions (a rock, an anchored boat…) have their own rules (19 and 20).",
                  "A boat that thinks she broke a rule can exonerate herself on the water, without waiting: she takes a one-turn {penalite|penalty} ({tour-de-penalite|turn}). Otherwise the other boat may protest and a {jury|jury} decides after the race.",
                  "Whatever the rule, sportsmanship comes first: you do not win by cheating."],
            "q": "Two overlapped boats reach a mark to be left to port; A is inside, B outside, and one is in the zone. Who must give mark-room?",
            "a": "B, the outside boat, gives A, the inside boat, mark-room (RRS 18).",
        },
        "securite": {
            "t": "Safety at sea",
            "p": ["Before leaving: read the {bulletin-meteo|weather forecast}, check the equipment, tell someone your expected return time. On board, everyone has a suitable lifejacket, worn whenever conditions require.",
                  "Three levels of VHF call, on channel 16 (distress watch): MAYDAY (said three times) for grave and imminent danger; PAN PAN for urgency without immediate danger; SÉCURITÉ for a navigational or weather warning.",
                  "In France, sea rescue is coordinated by the CROSS, reachable on channel 16 or, from a mobile phone, on 196.",
                  "{homme-a-la-mer|Man overboard}: shout “man overboard”, throw a lifebuoy, point someone who never loses sight of the person, then raise the alarm. There are several recovery methods: learn one in practice, with an instructor."],
            "q": "When do you use MAYDAY, and when PAN PAN?",
            "a": "MAYDAY: grave and imminent danger to a person or the boat. PAN PAN: urgency without immediate danger, for example a breakdown you have under control.",
        },
    },
    "revision": [
        ("You head 270° (due west) with a north wind. Which point of sail, which tack?", "North is on your right: the wind comes over the starboard side, at right angles — a beam reach, starboard tack."),
        ("The tidal range is 8 m. How much does the water rise during the third hour of the flood?", "3/12 of 8 m = 2 m."),
        ("Two sailboats are on the same tack; A is to windward of B. Who gives way, at sea outside a race and then in a race?", "A, in both cases: COLREG 12 a) ii) at sea, RRS 11 in a race (overlapped boats)."),
        ("Which lateral mark do you leave to starboard when entering harbour? And what do you say on VHF for grave and imminent danger?", "The green, conical one. “MAYDAY”, three times, on channel 16."),
    ],
}

TEXTES["it"] = {
    "titre": "Corso teorico di vela",
    "desc": "Un corso teorico di vela gratuito in {n} capitoli: vocabolario, andature, rotta, maree, meteo, segnalamento, COLREG e regole di regata (RRS 2025-2028), con esercizi corretti.",
    "h1": "Corso teorico di vela",
    "intro": "Un corso completo e gratuito, dal vocabolario della barca alle nozioni di base della patente costiera, in {n} capitoli. Ogni capitolo suppone solo i precedenti: leggili in ordine. Ogni regola è citata con il suo numero e titolo esatti, con ciò che impone; ogni capitolo termina con un esercizio corretto, il corso con quattro domande di ripasso. Nessuna iscrizione richiesta.",
    "sommaire": "Indice — {n} capitoli", "chap": "Capitolo", "regles": "Regole citate", "exo": "Esercizio", "corr": "Soluzione",
    "haut": "↑ Indice", "rev": "Ripasso del corso", "rev_intro": "Quattro domande che riprendono tutto il corso.", "schema": "Schemi",
    "note": "Fonti: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO), con i titoli del testo inglese ufficiale; segnalamento IALA, regione A. Questi riassunti non sostituiscono i testi, che fanno fede; i casi particolari non sono trattati e il corso non sostituisce né una formazione pratica né l'esame.",
    "regles_texte": {
        "rrs:10": "Quando due barche sono con mure opposte, la barca con mure a sinistra lascia strada alla barca con mure a dritta.",
        "rrs:11": "Quando due barche sono con la stessa mura e in ingaggio, la barca sopravento lascia strada a quella sottovento.",
        "rrs:12": "Quando due barche sono con la stessa mura e non in ingaggio, la barca che è a poppavia lascia strada a quella che è a prua.",
        "rrs:13": "Dopo aver superato la prua al vento, una barca lascia strada alle altre finché non è di bolina; in quel frattempo le regole 10, 11 e 12 non si applicano a lei.",
        "rrs:14": "Una barca evita il contatto con un'altra se ragionevolmente possibile; anche con diritto di rotta, deve agire appena è chiaro che l'altra non lascia strada.",
        "rrs:15": "Quando una barca acquisisce il diritto di rotta, deve prima lasciare all'altra lo spazio per allontanarsi, salvo che lo acquisisca per azione dell'altra.",
        "rrs:16": "Quando una barca con diritto di rotta cambia rotta, lascia all'altra lo spazio per allontanarsi.",
        "rrs:17": "Se una barca che era a poppavia diventa in ingaggio a meno di due lunghezze di scafo sottovento a una barca sulla stessa mura, non deve navigare più alta della sua rotta propria, salvo passare subito a poppa dell'altra.",
        "rrs:18": "Quando delle barche devono lasciare una boa dallo stesso lato e una è nella zona (tre lunghezze di scafo), la barca esterna, se sono in ingaggio, dà spazio alla boa a quella interna.",
        "rrs:19": "Quando barche in ingaggio passano un ostacolo, la barca esterna dà a quella interna lo spazio di passare tra sé e l'ostacolo.",
        "rrs:20": "Una barca che si avvicina a un ostacolo può chiamare per avere lo spazio di virare; la barca chiamata vira subito o risponde «Vira», poi lascia quello spazio.",
        "rrs:44": "Una barca che può aver infranto una regola della parte 2 o la regola 31 può esonerarsi eseguendo subito una penalità di un giro (una virata e un'abbattuta) dopo essersi allontanata dalle altre; in caso di danno grave o vantaggio significativo la penalità è il ritiro.",
        "rrs:2": "Le barche e i loro armatori gareggiano secondo i principi riconosciuti di sportività e correttezza; una barca è penalizzata in base a questa regola solo se è chiaramente stabilito che li ha violati.",
        "rrs:1": "Una barca o un concorrente dà ogni aiuto possibile a ogni persona o nave in pericolo.",
        "rrs:26": "La partenza segue una sequenza di segnali: avviso cinque minuti prima del segnale di partenza, preparatorio quattro minuti prima, bandiera preparatoria ammainata un minuto prima, partenza a zero; fanno fede i segnali visivi, non il suono.",
        "rrs:29": "Se una barca è sul lato percorso della linea al segnale, il comitato espone la bandiera X (richiamo individuale); se non può identificare le barche o la procedura è errata, espone il Primo Sostituto (richiamo generale).",
        "rrs:30": "Quando è issata la bandiera I, una barca che nell'ultimo minuto prima del suo segnale di partenza ha una parte di scafo, equipaggio o attrezzatura sul lato percorso della linea deve tornare sul lato pre-partenza attraverso un prolungamento della linea prima di partire.",
        "rrs:28": "Una barca parte, segue il percorso descritto nelle istruzioni di regata e arriva.",
        "rrs:31": "In regata, una barca non tocca una boa di partenza prima di partire, una boa che inizia, delimita o termina il lato che sta percorrendo, né una boa d'arrivo dopo aver tagliato il traguardo.",
        "col:5": "Ogni nave mantiene in ogni momento una vigilanza appropriata, visiva e auditiva, con tutti i mezzi disponibili.",
        "col:7": "Una nave usa tutti i mezzi disponibili per stabilire se c'è rischio di collisione; nel dubbio il rischio si ritiene esistente, in particolare se il rilevamento di una nave che si avvicina non cambia sensibilmente.",
        "col:8": "Una manovra per evitare la collisione è decisa, fatta con ampio anticipo e abbastanza ampia da essere vista dall'altra nave; si evita una serie di piccoli cambiamenti.",
        "col:12": "Due barche a vela: se ciascuna riceve il vento da lati diversi, quella che lo riceve da sinistra si tiene fuori rotta dall'altra; se lo ricevono dallo stesso lato, quella sopravento si tiene fuori rotta da quella sottovento.",
        "col:13": "Ogni nave che ne raggiunge un'altra si tiene fuori rotta da quella che sta raggiungendo; raggiunge chi arriva da più di 22,5° a poppavia del traverso dell'altra.",
        "col:14": "Due navi a propulsione meccanica che si presentano prua contro prua cambiano ciascuna rotta a dritta e si incrociano sinistra contro sinistra.",
        "col:15": "Due navi a propulsione meccanica con rotte che si incrociano: quella che vede l'altra a dritta si tiene fuori rotta e, se possibile, evita di passarle davanti.",
        "col:16": "La nave che deve tenersi fuori rotta agisce il più presto possibile e in modo deciso per passare ben al largo.",
        "col:17": "La nave che non deve tenersi fuori rotta mantiene rotta e velocità; può manovrare appena è evidente che l'altra non si scosta, e deve farlo se la collisione non può più essere evitata dalla sola manovra dell'altra.",
        "col:18": "Una nave a propulsione meccanica in navigazione si tiene fuori rotta da una nave a vela (e da una nave non governata, con capacità di manovra limitata o che pesca).",
        "col:25": "Una nave a vela in navigazione mostra fanali di via (rosso a sinistra, verde a dritta) e un fanale di poppa bianco.",
    },
    "ch": {
        "vocabulaire": {
            "t": "La barca e il suo vocabolario",
            "p": ["Una barca a vela si descrive con le sue parti. Lo {coque|scafo} è il corpo della barca; la {etrave|prua} è la parte anteriore, la {etambot|poppa} quella posteriore. Il {pont|ponte} lo copre, e il {cockpit|pozzetto} è dove ci si siede a timonare.",
                  "Guardando verso prua, la {babord|sinistra} (babordo) è a sinistra (luce rossa, di notte) e la {tribord|dritta} (tribordo) a destra (luce verde).",
                  "L'{mat|albero} porta le vele: la {grand-voile|randa}, fissata all'albero e al {bome|boma}, e a prua il {foc|fiocco} o il {genois|genoa}. Si alzano con le {drisse|drizze} e si regolano con le {ecoute|scotte}. A bordo una corda si chiama {bout|cima}.",
                  "Sott'acqua la {quille|deriva} limita lo scarroccio e il suo {lest|zavorra} raddrizza la barca; il {safran|timone}, comandato dalla {barre|barra}, la dirige."],
            "q": "Siete al timone e guardate verso prua. Da che parte è la dritta, e che colore di luce vi è di notte?",
            "a": "A destra; la luce di dritta è verde (la sinistra porta la luce rossa).",
        },
        "vent": {
            "t": "Il vento e le andature",
            "p": ["Il vento prende il nome da dove viene: un vento del nord soffia verso sud. Il lato da cui viene è {au-vent|sopravento}; il lato opposto è {sous-le-vent|sottovento}.",
                  "Una barca a vela non può avanzare contro vento: ai due lati di quella direzione, per circa 45 gradi, c'è la {zone-de-non-vent|zona di non-vento}. Avanza in tutte le altre direzioni, dette {allure|andature}.",
                  "Dalla più vicina al vento alla più lontana: la {pres|bolina} (circa 45° dal vento), il {bon-plein|bolina larga}, il {travers|traverso} (90°), il {largue|lasco} (circa 120°–135°) e la {vent-arriere|poppa} (180°).",
                  "La mura dice da che lato arriva il vento: {tribord-amures|mure a dritta} se arriva dal lato destro, {babord-amures|mure a sinistra} da quello sinistro.",
                  "A bordo si sente il {vent-apparent|vento apparente}, somma del {vent-reel|vento reale} e del vento creato dal moto della barca; sembra venire più da prua del vento reale."],
            "q": "Il vento arriva da destra, perpendicolare all'asse della barca. Quale andatura, quale mura?",
            "a": "Il traverso, mure a dritta (il vento arriva da dritta).",
        },
        "manoeuvres": {
            "t": "Regolare le vele e manovrare",
            "p": ["Le vele si regolano secondo l'andatura: si {border|cazza} (si tira la scotta) per andare verso il vento, si {choquer|lasca} (si molla) per allontanarsene. Una vela che {faseyer|sbatte} è lascata troppo.",
                  "Per cambiare direzione: {lofer|orzare} è avvicinarsi al vento; {abattre|poggiare} è allontanarsene.",
                  "{virer|Virare} è far passare la prua attraverso il vento; si avvisa l'equipaggio con «{pare-a-virer|pronti a virare}». {empanner|Abbattere} (strambare) è far passare la poppa nell'asse del vento: il boma attraversa la barca, ed è pericoloso; si annuncia «{pare-a-empanner|pronti a strambare}» e si bada alla consegna {attention-a-la-bome|attenzione al boma}.",
                  "Quando il vento rinforza, la barca {gite|sbanda} di più: si lascano le scotte, si orza piano, oppure si {prendre-un-ris|prende una mano di terzaroli}, cioè si riduce la superficie della randa."],
            "q": "Il vento rinforza e la barca sbanda troppo. Citate due gesti per alleggerirla.",
            "a": "Lascare le scotte (soprattutto della randa) e prendere una mano di terzaroli; si può anche orzare un poco perché le vele portino meno.",
        },
        "cap": {
            "t": "Rotta, distanza e carta",
            "p": ["La {cap|prua bussola} (rotta) è la direzione della barca, in gradi da 0 a 360 dal nord: 090° è est, 180° sud, 270° ovest.",
                  "Il {noeud-vitesse|nodo} è l'unità di velocità: un miglio nautico all'ora. Un miglio vale 1 852 metri, cioè un primo di latitudine, che si legge sulla scala verticale della carta. Distanza = velocità × tempo.",
                  "La bussola dà la rotta bussola. Corretta per la deviazione (propria della barca) dà la rotta magnetica; corretta per la declinazione (scarto tra nord magnetico e nord vero, indicata sulla carta) dà la rotta vera, quella che si traccia sulla carta. Una declinazione ovest è negativa: vera = magnetica + declinazione.",
                  "Vento e corrente scostano la barca dalla sua traiettoria: è lo {derive|scarroccio e deriva}. La {route-fond|rotta sul fondo} è la rotta realmente seguita sul fondo, diversa dalla prua."],
            "q": "Navigate a 6 nodi. In quanto tempo percorrete 15 miglia?",
            "a": "15 ÷ 6 = 2,5 ore, cioè 2 h 30.",
        },
        "marees": {
            "t": "Maree e correnti",
            "p": ["La {maree|marea} è la salita e la discesa del mare, circa due volte al giorno. Il mare sale durante il {flot|flusso} fino all'{pleine-mer|alta marea}, poi scende durante il {jusant|riflusso} fino alla {basse-mer|bassa marea}. Passano circa sei ore tra alta e bassa marea.",
                  "L'{marnage|escursione di marea} è la differenza di altezza tra alta e bassa marea. Alla {etale|stanca}, al momento dell'inversione, non c'è quasi {courant|corrente} di marea.",
                  "La regola dei dodicesimi stima l'altezza durante la marea: dell'escursione, l'acqua sale di 1/12 la prima ora, 2/12 la seconda, 3/12 la terza, 3/12 la quarta, 2/12 la quinta, 1/12 la sesta.",
                  "La corrente di marea porta la barca: favorevole aiuta, contraria frena. Quando la corrente è contro vento, il mare diventa più corto e ripido."],
            "q": "L'escursione di marea è 6 m. Di quanto è salita l'acqua dopo due ore di flusso?",
            "a": "1/12 + 2/12 = 3/12, cioè 1/4 di 6 m: 1,5 m.",
        },
        "meteo": {
            "t": "Il meteo",
            "p": ["La scala {beaufort|Beaufort} classifica il vento da 0 a 12: forza 4 = 11–16 nodi, forza 6 = 22–27 nodi, forza 8 = 34–40 nodi (burrasca). Oltre la forza 6 la navigazione richiede esperienza.",
                  "Un {anticyclone|anticiclone} è una zona di alta pressione (sopra circa 1 013 hPa): tempo stabile, vento debole. Una {depression|depressione} è una zona di bassa pressione: nuvole, pioggia, vento più forte. Nell'emisfero nord il vento gira in senso orario attorno a un anticiclone, antiorario attorno a una depressione.",
                  "Prima di partire si legge il {bulletin-meteo|bollettino meteo}: vento medio, {rafale|raffiche}, stato del mare. Un {grain|groppo} è una raffica breve con pioggia; il {orage|temporale} impone di rientrare.",
                  "Vicino alla costa, d'estate, la {brise-de-mer|brezza di mare} soffia il pomeriggio verso terra; la {brise-de-terre|brezza di terra} soffia la notte verso il largo. L'{houle|onda lunga} (mare lungo) viene da lontano; il {clapot|moto ondoso corto} è un mare corto e disordinato."],
            "q": "Il bollettino annuncia «vento forza 6, raffiche a 8». Convertite la forza 6 in nodi e dite cosa significa la forza 8.",
            "a": "Forza 6: 22–27 nodi. Forza 8: 34–40 nodi, una burrasca — da evitare per un equipaggio principiante.",
        },
        "balisage": {
            "t": "Segnalamento e fanali",
            "p": ["Il segnalamento guida e avverte dei pericoli. In Europa si segue il sistema IALA, regione A. I segnali laterali bordano un canale; si descrivono nel senso convenzionale, entrando in un porto dal largo.",
                  "Segnale di sinistra: rosso, cilindrico (si lascia a sinistra). Segnale di dritta: verde, conico (si lascia a dritta). Entrando si vede rosso a sinistra e verde a destra; uscendo è il contrario.",
                  "Un segnale cardinale porta il nome del lato dove si trova l'acqua sicura: un cardinale Nord si passa a nord di esso. Nord: nero sopra, giallo sotto; Sud: giallo sopra, nero sotto; Est: nero-giallo-nero; Ovest: giallo-nero-giallo.",
                  "Una {bouee|boa} nera con bande rosse segna un pericolo isolato (si evita ampiamente); una boa a bande verticali rosse e bianche, acque sicure; un segnale giallo, una zona speciale.",
                  "Di notte una barca a vela in navigazione porta una luce rossa a sinistra, una verde a dritta e una bianca a poppa; a motore aggiunge un fanale bianco di testa d'albero."],
            "q": "Rientrate in porto dal largo e vedete una boa rossa cilindrica. Da che lato la lasciate?",
            "a": "A sinistra (rosso a sinistra entrando).",
        },
        "abordage": {
            "t": "Evitare l'abbordaggio in mare (COLREG)",
            "p": ["Il COLREG è il regolamento internazionale del 1972 per prevenire gli abbordi in mare (RIPAM in francese). Si applica a tutte le navi, barche a vela comprese; durante una regata le regole di regata governano i concorrenti tra loro (capitoli da 9 a 11).",
                  "Tre doveri precedono ogni regola di precedenza: vigilare (regola 5), riconoscere il rischio di collisione — se il rilevamento di una nave che si avvicina non cambia, il rischio esiste (regola 7) — e agire presto e con decisione (regola 8).",
                  "Ricordate due ruoli: la nave che deve tenersi fuori rotta manovra presto e con decisione; l'altra mantiene rotta e velocità finché la prima agisce.",
                  "In sintesi, a vela: vento da lati diversi, lascia strada chi lo riceve da sinistra; dallo stesso lato, chi è sopravento; chi raggiunge lascia strada; una barca a motore lascia strada a una a vela."],
            "q": "Due barche a vela si incrociano in mare, fuori regata. La prima riceve il vento da dritta, la seconda da sinistra. Quale lascia strada, secondo quale regola?",
            "a": "Quella che riceve il vento da sinistra lascia strada (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Regata: la partenza e il percorso",
            "p": ["Una regata è organizzata dal {comite-de-course|comitato di regata}, che dalla sua {bateau-comite|barca comitato} dispone la {ligne-de-depart|linea di partenza}: lo spazio tra la barca comitato e una {marque-de-depart|boa di partenza}. Prima del {signal-de-depart|segnale di partenza} si resta sul lato pre-partenza della linea.",
                  "Se una barca è sul lato percorso della linea al segnale, è una {faux-depart|partenza anticipata}: deve tornare e ripartire. Se il comitato non può identificare le barche, annulla la partenza con un {rappel-general|richiamo generale}.",
                  "Il {parcours|percorso}, descritto nelle istruzioni di regata, in genere è: partenza, risalita fino alla {bouee-au-vent|boa di bolina}, discesa verso la {bouee-sous-le-vent|boa di poppa} o una {porte|porta}, a volte più giri, poi {arrivee|arrivo} sulla {ligne-d-arrivee|linea d'arrivo}."],
            "q": "Alla vostra partenza il comitato issa la bandiera X con un suono. Cosa significa per voi e cosa fate?",
            "a": "È un richiamo individuale (RRS 29): al segnale una parte della barca era sul lato percorso. Tornate interamente sul lato pre-partenza e poi attraversate la linea; finché non l'avete fatto, non siete partiti.",
        },
        "priorites": {
            "t": "Regata: le precedenze",
            "p": ["In regata la parte 2 delle {regles-de-course|regole di regata} dice chi deve lasciare strada a chi. Bastano due nozioni: la mura (capitolo 2) e l'ingaggio. Una barca è «a poppavia» dell'altra quando il suo scafo è interamente dietro una linea perpendicolare all'asse dell'altra, passante per il suo punto più arretrato; altrimenti le barche sono in ingaggio.",
                  "Si leggono le regole in ordine: mure opposte (10); stessa mura, in ingaggio (11) o no (12). La virata (13) viene prima. Le regole da 14 a 17 limitano i diritti delle regole da 10 a 13.",
                  "Una barca con {priorite|diritto di rotta} può tenere la rotta, ma non deve cambiarla senza lasciare all'altra lo spazio per allontanarsi. Se si ritiene che una regola sia stata infranta, si può segnalarlo: è la {protestation|protesta}."],
            "q": "A è con mure a dritta, B con mure a sinistra; le rotte convergono. B vede che A non cambia rotta. Chi lascia strada, secondo quale regola? Cosa deve fare A se vede che B non si scosta?",
            "a": "B lascia strada (RRS 10). A, pur con diritto di rotta, deve evitare il contatto appena è chiaro che B non si scosta (RRS 14).",
        },
        "marques": {
            "t": "Regata: boe, ostacoli e penalità",
            "p": ["Alle boe il gioco si stringe. La zona è il cerchio di tre lunghezze di scafo attorno alla boa. Quando due barche devono lasciare la boa dallo stesso lato e una è nella zona, si applica la regola 18.",
                  "Lo spazio alla boa è lo spazio per navigare fino alla boa e poi girarla dal lato richiesto. Gli ostacoli (uno scoglio, una barca all'ancora…) hanno regole proprie (19 e 20).",
                  "Una barca che pensa di aver infranto una regola può esonerarsi in acqua, senza attendere: esegue una {penalite|penalità} di un {tour-de-penalite|giro}. Altrimenti l'altra barca può protestare e una {jury|giuria} decide dopo la regata.",
                  "Qualunque sia la regola, prevale lo spirito sportivo: non si vince barando."],
            "q": "Due barche in ingaggio arrivano a una boa da lasciare a sinistra; A è all'interno, B all'esterno, e una è nella zona. Chi deve dare spazio alla boa?",
            "a": "B, la barca esterna, dà ad A, interna, lo spazio alla boa (RRS 18).",
        },
        "securite": {
            "t": "Sicurezza in mare",
            "p": ["Prima di partire: leggere il {bulletin-meteo|bollettino meteo}, controllare il materiale, dire a qualcuno l'ora prevista di rientro. A bordo ognuno ha un giubbotto di salvataggio adatto, indossato quando le condizioni lo richiedono.",
                  "Tre livelli di chiamata VHF, sul canale 16 (ascolto di soccorso): MAYDAY (detto tre volte) per un pericolo grave e imminente; PAN PAN per un'urgenza senza pericolo immediato; SÉCURITÉ per un avviso di navigazione o meteo.",
                  "In Francia il soccorso in mare è coordinato dai CROSS, raggiungibili sul canale 16 o, da un cellulare, al 196.",
                  "{homme-a-la-mer|Uomo a mare}: gridare «uomo a mare», lanciargli un salvagente, indicare una persona che non lo perda mai di vista, poi dare l'allarme. Esistono più metodi di recupero: impararne uno in pratica, con un istruttore."],
            "q": "Quando si usa MAYDAY, e quando PAN PAN?",
            "a": "MAYDAY: pericolo grave e imminente per una persona o la barca. PAN PAN: urgenza senza pericolo immediato, ad esempio un'avaria di cui si ha il controllo.",
        },
    },
    "revision": [
        ("Fate rotta al 270° (ovest) con vento da nord. Quale andatura, quale mura?", "Il nord è alla vostra destra: il vento arriva da dritta, perpendicolare — è il traverso, mure a dritta."),
        ("L'escursione di marea è 8 m. Di quanto sale l'acqua durante la terza ora di flusso?", "3/12 di 8 m = 2 m."),
        ("Due barche a vela sono sulla stessa mura; A è sopravento a B. Chi lascia strada, in mare fuori regata e poi in regata?", "A, in entrambi i casi: COLREG 12 a) ii) in mare, RRS 11 in regata (barche in ingaggio)."),
        ("Quale segnale laterale si lascia a dritta entrando in porto? E cosa si dice in VHF per un pericolo grave e imminente?", "Quello verde, conico. «MAYDAY», tre volte, sul canale 16."),
    ],
}

TEXTES["es"] = {
    "titre": "Curso teórico de vela",
    "desc": "Un curso teórico de vela gratuito en {n} capítulos: vocabulario, rumbos, derrota, mareas, meteorología, balizamiento, COLREG y reglas de regata (RRS 2025-2028), con ejercicios corregidos.",
    "h1": "Curso teórico de vela",
    "intro": "Un curso completo y gratuito, del vocabulario del barco a las nociones básicas de una titulación costera, en {n} capítulos. Cada capítulo solo supone los anteriores: léelos en orden. Cada regla se cita con su número y título exactos, con lo que obliga; cada capítulo termina con un ejercicio corregido, y el curso con cuatro preguntas de repaso. No se pide ninguna inscripción.",
    "sommaire": "Índice — {n} capítulos", "chap": "Capítulo", "regles": "Reglas citadas", "exo": "Ejercicio", "corr": "Corrección",
    "haut": "↑ Índice", "rev": "Repaso del curso", "rev_intro": "Cuatro preguntas que retoman todo el curso.", "schema": "Esquemas",
    "note": "Fuentes: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (OMI), con los títulos del texto inglés oficial; balizamiento AISM/IALA, región A. Estos resúmenes no sustituyen a los textos, que prevalecen; los casos particulares no se tratan y el curso no sustituye ni una formación práctica ni el examen.",
    "regles_texte": {
        "rrs:10": "Cuando dos barcos están en amuras opuestas, el barco de amura de babor se mantiene separado del barco de amura de estribor.",
        "rrs:11": "Cuando dos barcos están en la misma amura y con solape, el barco de barlovento se mantiene separado del de sotavento.",
        "rrs:12": "Cuando dos barcos están en la misma amura y sin solape, el barco que está por la popa se mantiene separado del que está por delante.",
        "rrs:13": "Tras pasar por la proa al viento, un barco se mantiene separado de los demás hasta que navega de ceñida; durante ese tiempo no se le aplican las reglas 10, 11 y 12.",
        "rrs:14": "Un barco evita el contacto con otro si es razonablemente posible; aunque tenga derecho de paso, debe actuar en cuanto sea claro que el otro no se mantiene separado.",
        "rrs:15": "Cuando un barco adquiere el derecho de paso, primero deja al otro espacio para mantenerse separado, salvo que lo adquiera por una acción del otro.",
        "rrs:16": "Cuando un barco con derecho de paso cambia de rumbo, deja al otro espacio para mantenerse separado.",
        "rrs:17": "Si un barco que estaba por la popa pasa a tener solape a menos de dos esloras a sotavento de un barco en la misma amura, no debe navegar más alto que su rumbo propio, salvo que pase prontamente por la popa del otro.",
        "rrs:18": "Cuando los barcos deben dejar una baliza por el mismo lado y uno de ellos está en la zona (tres esloras), el barco exterior, si tienen solape, da espacio en la baliza al interior.",
        "rrs:19": "Cuando barcos con solape pasan un obstáculo, el barco exterior da al interior espacio para pasar entre él y el obstáculo.",
        "rrs:20": "Un barco que se acerca a un obstáculo puede llamar para tener espacio para virar; el barco llamado vira enseguida o responde «Vira», y luego deja ese espacio.",
        "rrs:44": "Un barco que pueda haber infringido una regla de la parte 2 o la regla 31 puede exonerarse haciendo prontamente una penalización de un giro (una virada y una trasluchada) tras separarse de los demás; si causó daño grave u obtuvo una ventaja significativa, la penalización es retirarse.",
        "rrs:2": "Los barcos y sus propietarios compiten según los principios reconocidos de deportividad y juego limpio; un barco solo es penalizado por esta regla si queda claramente establecido que los infringió.",
        "rrs:1": "Un barco o competidor presta toda la ayuda posible a toda persona o buque en peligro.",
        "rrs:26": "La salida sigue una secuencia de señales: atención cinco minutos antes de la señal de salida, preparación cuatro minutos antes, retirada de la bandera de preparación un minuto antes, salida a cero; valen las señales visuales, no el sonido.",
        "rrs:29": "Si un barco está en el lado del recorrido de la línea en su señal de salida, el comité iza la bandera X (llamada individual); si no puede identificar a los barcos o el procedimiento es erróneo, iza el Primer Sustituto (llamada general).",
        "rrs:30": "Cuando se ha izado la bandera I, un barco que durante el último minuto antes de su señal de salida tenga parte del casco, la tripulación o el equipo en el lado del recorrido de la línea debe volver al lado de pre-salida por una prolongación de la línea antes de salir.",
        "rrs:28": "Un barco sale, navega el recorrido descrito en las instrucciones de regata y llega.",
        "rrs:31": "Durante la regata, un barco no toca una baliza de salida antes de salir, una baliza que empieza, limita o termina el tramo que navega, ni una baliza de llegada después de llegar.",
        "col:5": "Todo buque mantendrá en todo momento una vigilancia adecuada, visual y auditiva, por todos los medios disponibles.",
        "col:7": "Un buque empleará todos los medios disponibles para determinar si existe riesgo de abordaje; en caso de duda se considerará que existe, en particular si la demora de un buque que se aproxima no varía apreciablemente.",
        "col:8": "Una maniobra para evitar el abordaje será franca, hecha con amplia antelación y suficientemente grande para ser vista por el otro buque; se evitará una serie de pequeños cambios.",
        "col:12": "Dos veleros: si cada uno recibe el viento por una banda distinta, el que lo recibe por babor se mantiene apartado de la derrota del otro; si ambos lo reciben por la misma banda, el de barlovento se mantiene apartado del de sotavento.",
        "col:13": "Todo buque que alcance a otro se mantendrá apartado de su derrota; alcanza el que llega desde más de 22,5° por detrás del través del otro.",
        "col:14": "Dos buques de propulsión mecánica que se encuentran de proa cambian cada uno su rumbo a estribor y se cruzan por babor.",
        "col:15": "Dos buques de propulsión mecánica con rumbos que se cruzan: el que ve al otro por su costado de estribor se mantiene apartado y, si es posible, evita cruzar por delante de él.",
        "col:16": "El buque que debe mantenerse apartado actúa lo antes posible y con decisión para pasar bien separado.",
        "col:17": "El buque que no debe apartarse mantiene su rumbo y velocidad; puede maniobrar en cuanto sea evidente que el otro no se aparta, y debe hacerlo si el abordaje ya no puede evitarse solo con la maniobra del otro.",
        "col:18": "Un buque de propulsión mecánica en navegación se mantiene apartado de la derrota de un buque de vela (y de un buque sin gobierno, con capacidad de maniobra restringida o que pesca).",
        "col:25": "Un buque de vela en navegación muestra luces de costado (roja a babor, verde a estribor) y una luz de alcance blanca.",
    },
    "ch": {
        "vocabulaire": {
            "t": "El barco y su vocabulario",
            "p": ["Un velero se describe por sus partes. El {coque|casco} es el cuerpo del barco; la {etrave|proa} es su parte delantera, la {etambot|popa} la trasera. La {pont|cubierta} lo cubre, y la {cockpit|bañera} es donde uno se sienta para gobernar.",
                  "Mirando hacia proa, {babord|babor} está a la izquierda (luz roja, de noche) y {tribord|estribor} a la derecha (luz verde).",
                  "El {mat|mástil} lleva las velas: la {grand-voile|mayor}, fijada al mástil y a la {bome|botavara}, y a proa el {foc|foque} o el {genois|génova}. Se izan con las {drisse|drizas} y se regulan con las {ecoute|escotas}. A bordo, una cuerda se llama {bout|cabo}.",
                  "Bajo el agua, la {quille|quilla} limita la deriva y su {lest|lastre} endereza el barco; el {safran|timón}, accionado por la {barre|caña}, lo dirige."],
            "q": "Estás al timón y miras hacia la proa. ¿De qué lado está estribor y qué color de luz lleva de noche?",
            "a": "A la derecha; la luz de estribor es verde (babor, a la izquierda, lleva la luz roja).",
        },
        "vent": {
            "t": "El viento y los rumbos",
            "p": ["El viento se nombra por el punto de donde viene: un viento del norte sopla hacia el sur. El lado de donde viene es {au-vent|barlovento}; el lado opuesto, {sous-le-vent|sotavento}.",
                  "Un velero no puede avanzar de cara al viento: a cada lado de esa dirección, unos 45 grados, se extiende la {zone-de-non-vent|zona sin viento}. Avanza en todas las demás direcciones, llamadas {allure|rumbos}.",
                  "Del más cercano al viento al más alejado: la {pres|ceñida} (unos 45° del viento), el {bon-plein|ceñida holgada}, el {travers|descuartelar o través} (90°), el {largue|largo} (unos 120° a 135°) y el {vent-arriere|empopada} (180°).",
                  "La amura dice por qué lado llega el viento: {tribord-amures|amura de estribor} si llega por la derecha del barco, {babord-amures|amura de babor} por la izquierda.",
                  "A bordo se siente el {vent-apparent|viento aparente}, suma del {vent-reel|viento real} y del viento creado por el avance del barco; parece venir más de proa que el real."],
            "q": "El viento llega por la derecha, perpendicular al eje del barco. ¿Qué rumbo y qué amura?",
            "a": "El través, amura de estribor (el viento llega por estribor).",
        },
        "manoeuvres": {
            "t": "Regular las velas y maniobrar",
            "p": ["Las velas se regulan según el rumbo: se {border|cazan} (se tira de la escota) para ir hacia el viento, se {choquer|lascan} (se suelta) para alejarse. Una vela que {faseyer|flamea} está demasiado lascada.",
                  "Para cambiar de dirección: {lofer|orzar} es acercarse al viento; {abattre|arribar} es alejarse.",
                  "{virer|Virar} por avante es hacer pasar la proa por el viento; se avisa a la tripulación con «{pare-a-virer|listos para virar}». {empanner|Trasluchar} es hacer pasar la popa por el viento: la botavara cruza el barco, y es peligroso; se avisa «{pare-a-empanner|listos para trasluchar}» y se atiende a {attention-a-la-bome|cuidado con la botavara}.",
                  "Cuando el viento aumenta, el barco {gite|escora} más: se lascan las escotas, se orza suavemente, o se {prendre-un-ris|toma un rizo}, es decir, se reduce la superficie de la mayor."],
            "q": "El viento aumenta y el barco escora demasiado. Cita dos acciones para aliviarlo.",
            "a": "Lascar las escotas (sobre todo la de la mayor) y tomar un rizo; también se puede orzar un poco para que las velas trabajen menos.",
        },
        "cap": {
            "t": "Rumbo, distancia y carta",
            "p": ["El {cap|rumbo} es la dirección del barco, en grados de 0 a 360 desde el norte: 090° es este, 180° sur, 270° oeste.",
                  "El {noeud-vitesse|nudo} es la unidad de velocidad: una milla náutica por hora. Una milla son 1 852 metros, un minuto de latitud, que se lee en la escala vertical de la carta. Distancia = velocidad × tiempo.",
                  "La aguja da el rumbo de aguja. Corregido del desvío (propio del barco) da el rumbo magnético; corregido de la declinación (diferencia entre norte magnético y norte verdadero, indicada en la carta) da el rumbo verdadero, el que se traza en la carta. Una declinación oeste cuenta como negativa: verdadero = magnético + declinación.",
                  "El viento y la corriente apartan al barco de su trayectoria: es la {derive|deriva}. La {route-fond|derrota sobre el fondo} es la ruta realmente seguida sobre el fondo, distinta del rumbo."],
            "q": "Navegas a 6 nudos. ¿Cuánto tardas en recorrer 15 millas?",
            "a": "15 ÷ 6 = 2,5 horas, es decir 2 h 30.",
        },
        "marees": {
            "t": "Mareas y corrientes",
            "p": ["La {maree|marea} es la subida y bajada del mar, unas dos veces al día. El mar sube durante el {flot|flujo} hasta la {pleine-mer|pleamar}, luego baja durante el {jusant|reflujo} hasta la {basse-mer|bajamar}. Pasan unas seis horas entre pleamar y bajamar.",
                  "La {marnage|amplitud de marea} es la diferencia de altura entre pleamar y bajamar. En la {etale|estoa}, en el momento del cambio, casi no hay {courant|corriente} de marea.",
                  "La regla de los doceavos estima la altura durante la marea: de la amplitud, el agua sube 1/12 la primera hora, 2/12 la segunda, 3/12 la tercera, 3/12 la cuarta, 2/12 la quinta, 1/12 la sexta.",
                  "La corriente de marea lleva al barco: favorable, ayuda; contraria, frena. Cuando la corriente va contra el viento, el mar se vuelve más corto y picado."],
            "q": "La amplitud es de 6 m. ¿Cuánto ha subido el agua tras dos horas de flujo?",
            "a": "1/12 + 2/12 = 3/12, es decir 1/4 de 6 m: 1,5 m.",
        },
        "meteo": {
            "t": "La meteorología",
            "p": ["La escala de {beaufort|Beaufort} clasifica el viento de 0 a 12: fuerza 4 = 11 a 16 nudos, fuerza 6 = 22 a 27 nudos, fuerza 8 = 34 a 40 nudos (temporal). Más allá de fuerza 6, navegar requiere experiencia.",
                  "Un {anticyclone|anticiclón} es una zona de altas presiones (sobre unos 1 013 hPa): tiempo estable, viento flojo. Una {depression|depresión} es una zona de bajas presiones: nubes, lluvia, viento más fuerte. En el hemisferio norte el viento gira en sentido horario alrededor de un anticiclón y antihorario alrededor de una depresión.",
                  "Antes de salir se lee el {bulletin-meteo|parte meteorológico}: viento medio, {rafale|rachas}, estado de la mar. Un {grain|chubasco} es una racha breve con lluvia; la {orage|tormenta} obliga a volver.",
                  "Cerca de la costa, en verano, la {brise-de-mer|brisa de mar} sopla por la tarde hacia tierra; la {brise-de-terre|brisa de tierra} sopla de noche hacia el mar. La {houle|mar de fondo} es una ola larga venida de lejos; el {clapot|mar picada} es una mar corta y desordenada."],
            "q": "El parte anuncia «viento fuerza 6, rachas a 8». Convierte la fuerza 6 a nudos y di qué significa la fuerza 8.",
            "a": "Fuerza 6: 22 a 27 nudos. Fuerza 8: 34 a 40 nudos, un temporal — a evitar para una tripulación principiante.",
        },
        "balisage": {
            "t": "Balizamiento y luces",
            "p": ["El balizamiento guía y advierte de peligros. En Europa se sigue el sistema AISM/IALA, región A. Las marcas laterales bordean un canal; se describen en el sentido convencional, al entrar en un puerto desde la mar.",
                  "Marca de babor: roja, cilíndrica (se deja a babor). Marca de estribor: verde, cónica (se deja a estribor). Al entrar se ve rojo a la izquierda y verde a la derecha; al salir, al revés.",
                  "Una marca cardinal lleva el nombre del lado donde está el agua segura: una cardinal Norte se pasa al norte de ella. Norte: negra arriba, amarilla abajo; Sur: amarilla arriba, negra abajo; Este: negro-amarillo-negro; Oeste: amarillo-negro-amarillo.",
                  "Una {bouee|boya} negra con bandas rojas marca un peligro aislado (se evita ampliamente); una boya de franjas verticales rojas y blancas, aguas navegables; una marca amarilla, una zona especial.",
                  "De noche, un velero a vela lleva una luz roja a babor, una verde a estribor y una blanca a popa; a motor añade una luz blanca de tope."],
            "q": "Entras en puerto desde la mar y ves una boya roja cilíndrica. ¿Por qué lado la dejas?",
            "a": "Por babor (rojo a la izquierda al entrar).",
        },
        "abordage": {
            "t": "Evitar el abordaje en el mar (COLREG)",
            "p": ["El COLREG es el reglamento internacional de 1972 para prevenir los abordajes en el mar (RIPA en español). Se aplica a todos los buques, veleros incluidos; durante una regata, las reglas de regata rigen entre los competidores (capítulos 9 a 11).",
                  "Tres deberes preceden a toda regla de paso: vigilar (regla 5), reconocer el riesgo de abordaje — si la demora de un buque que se aproxima no cambia, el riesgo existe (regla 7) — y actuar pronto y con decisión (regla 8).",
                  "Recuerda dos papeles: el buque que debe apartarse maniobra pronto y con decisión; el otro mantiene rumbo y velocidad mientras el primero actúa.",
                  "En resumen, a vela: viento por bandas distintas, se aparta el que lo recibe por babor; por la misma banda, el de barlovento; el que alcanza se aparta; un barco a motor se aparta de un velero."],
            "q": "Dos veleros se cruzan en el mar, fuera de regata. El primero recibe el viento por estribor, el segundo por babor. ¿Cuál se aparta y según qué regla?",
            "a": "El que recibe el viento por babor se aparta (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Regata: la salida y el recorrido",
            "p": ["Una regata la organiza el {comite-de-course|comité de regata}, que desde su {bateau-comite|barco del comité} coloca la {ligne-de-depart|línea de salida}: el espacio entre el barco del comité y una {marque-de-depart|baliza de salida}. Antes de la {signal-de-depart|señal de salida} se permanece en el lado de pre-salida de la línea.",
                  "Si un barco está en el lado del recorrido en la señal, es una {faux-depart|salida anticipada}: debe volver y salir de nuevo. Si el comité no puede identificar a los barcos, anula la salida con una {rappel-general|llamada general}.",
                  "El {parcours|recorrido}, descrito en las instrucciones de regata, suele ser: salida, ceñida hasta la {bouee-au-vent|baliza de barlovento}, descenso hacia la {bouee-sous-le-vent|baliza de sotavento} o una {porte|puerta}, a veces varias vueltas, y {arrivee|llegada} en la {ligne-d-arrivee|línea de llegada}."],
            "q": "En tu salida, el comité iza la bandera X con un sonido. ¿Qué significa para ti y qué haces?",
            "a": "Es una llamada individual (RRS 29): en la señal, parte de tu barco estaba en el lado del recorrido. Vuelves por completo al lado de pre-salida y luego cruzas la línea; hasta entonces no has salido.",
        },
        "priorites": {
            "t": "Regata: las prioridades",
            "p": ["En regata, la parte 2 de las {regles-de-course|reglas de regata} dice quién debe mantenerse separado de quién. Bastan dos nociones: la amura (capítulo 2) y el solape. Un barco está «por la popa» de otro cuando su casco queda enteramente detrás de una línea perpendicular al eje del otro que pasa por su punto más a popa; si no, los barcos tienen solape.",
                  "Se leen las reglas en orden: amuras opuestas (10); misma amura, con solape (11) o sin solape (12). La virada (13) va primero. Las reglas 14 a 17 limitan los derechos de las reglas 10 a 13.",
                  "Un barco con {priorite|derecho de paso} puede mantener su rumbo, pero no debe cambiarlo sin dejar al otro espacio para mantenerse separado. Si se cree que se ha infringido una regla, se puede señalar: es la {protestation|protesta}."],
            "q": "A va en amura de estribor, B en amura de babor; sus rumbos convergen. B ve que A no cambia de rumbo. ¿Quién se mantiene separado, según qué regla? ¿Qué debe hacer A si ve que B no se aparta?",
            "a": "B se mantiene separado (RRS 10). A, aunque tenga derecho de paso, debe evitar el contacto en cuanto sea claro que B no se aparta (RRS 14).",
        },
        "marques": {
            "t": "Regata: balizas, obstáculos y penalizaciones",
            "p": ["En las balizas el juego se estrecha. La zona es el círculo de tres esloras alrededor de la baliza. Cuando dos barcos deben dejar la baliza por el mismo lado y uno está en la zona, se aplica la regla 18.",
                  "El espacio en la baliza es el espacio para navegar hasta la baliza y luego rodearla por el lado requerido. Los obstáculos (una roca, un barco fondeado…) tienen sus propias reglas (19 y 20).",
                  "Un barco que cree haber infringido una regla puede exonerarse en el agua, sin esperar: hace una {penalite|penalización} de un {tour-de-penalite|giro}. Si no, el otro barco puede protestar y un {jury|jurado} decide tras la regata.",
                  "Sea cual sea la regla, prima la deportividad: no se gana haciendo trampa."],
            "q": "Dos barcos con solape llegan a una baliza que se deja a babor; A está por dentro, B por fuera, y uno está en la zona. ¿Quién debe dar espacio en la baliza?",
            "a": "B, el barco exterior, da a A, el interior, espacio en la baliza (RRS 18).",
        },
        "securite": {
            "t": "Seguridad en el mar",
            "p": ["Antes de salir: leer el {bulletin-meteo|parte meteorológico}, revisar el material, decir a alguien la hora prevista de regreso. A bordo, cada persona tiene un chaleco salvavidas adecuado, que se lleva puesto cuando las condiciones lo exigen.",
                  "Tres niveles de llamada por VHF, en el canal 16 (escucha de socorro): MAYDAY (dicho tres veces) para un peligro grave e inminente; PAN PAN para una urgencia sin peligro inmediato; SÉCURITÉ para un aviso de navegación o meteorológico.",
                  "En Francia, el socorro en el mar lo coordinan los CROSS, localizables en el canal 16 o, desde un móvil, en el 196.",
                  "{homme-a-la-mer|Hombre al agua}: gritar «hombre al agua», lanzarle un aro salvavidas, designar a una persona que no lo pierda nunca de vista y dar la alarma. Hay varios métodos de recuperación: aprende uno en la práctica, con un monitor."],
            "q": "¿Cuándo se usa MAYDAY y cuándo PAN PAN?",
            "a": "MAYDAY: peligro grave e inminente para una persona o el barco. PAN PAN: urgencia sin peligro inmediato, por ejemplo una avería que se controla.",
        },
    },
    "revision": [
        ("Navegas al 270° (oeste) con viento del norte. ¿Qué rumbo y qué amura?", "El norte está a tu derecha: el viento llega por estribor, perpendicular — es el través, amura de estribor."),
        ("La amplitud de marea es de 8 m. ¿Cuánto sube el agua durante la tercera hora del flujo?", "3/12 de 8 m = 2 m."),
        ("Dos veleros van en la misma amura; A está a barlovento de B. ¿Quién se aparta, en el mar fuera de regata y luego en regata?", "A, en ambos casos: COLREG 12 a) ii) en el mar, RRS 11 en regata (barcos con solape)."),
        ("¿Qué marca lateral se deja a estribor al entrar en puerto? ¿Y qué se dice por VHF ante un peligro grave e inminente?", "La verde, cónica. «MAYDAY», tres veces, en el canal 16."),
    ],
}

TEXTES["pt"] = {
    "titre": "Curso teórico de vela",
    "desc": "Um curso teórico de vela gratuito em {n} capítulos: vocabulário, andamentos, rumo, marés, meteorologia, balizagem, COLREG e regras de regata (RRS 2025-2028), com exercícios corrigidos.",
    "h1": "Curso teórico de vela",
    "intro": "Um curso completo e gratuito, do vocabulário do barco às noções básicas de uma carta costeira, em {n} capítulos. Cada capítulo só pressupõe os anteriores: leia-os por ordem. Cada regra é citada com o seu número e título exatos, com o que obriga; cada capítulo termina com um exercício corrigido, e o curso com quatro perguntas de revisão. Não é pedida nenhuma inscrição.",
    "sommaire": "Índice — {n} capítulos", "chap": "Capítulo", "regles": "Regras citadas", "exo": "Exercício", "corr": "Correção",
    "haut": "↑ Índice", "rev": "Revisão do curso", "rev_intro": "Quatro perguntas que retomam todo o curso.", "schema": "Esquemas",
    "note": "Fontes: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (OMI), com os títulos do texto inglês oficial; balizagem AISM/IALA, região A. Estes resumos não substituem os textos, que prevalecem; os casos particulares não são tratados e o curso não substitui nem uma formação prática nem o exame.",
    "regles_texte": {
        "rrs:10": "Quando dois barcos estão em amuras opostas, o barco com amura a bombordo mantém-se afastado do barco com amura a estibordo.",
        "rrs:11": "Quando dois barcos estão na mesma amura e sobrepostos, o barco de barlavento mantém-se afastado do de sotavento.",
        "rrs:12": "Quando dois barcos estão na mesma amura e sem sobreposição, o barco que está atrás mantém-se afastado do que está à frente.",
        "rrs:13": "Depois de passar com a proa ao vento, um barco mantém-se afastado dos outros até estar de bolina; durante esse tempo não lhe são aplicáveis as regras 10, 11 e 12.",
        "rrs:14": "Um barco evita o contacto com outro se for razoavelmente possível; mesmo com prioridade, deve agir logo que seja claro que o outro não se afasta.",
        "rrs:15": "Quando um barco adquire prioridade, deixa primeiro ao outro espaço para se afastar, salvo se a adquirir por ação do outro.",
        "rrs:16": "Quando um barco com prioridade muda de rumo, deixa ao outro espaço para se afastar.",
        "rrs:17": "Se um barco que estava atrás fica sobreposto a menos de dois comprimentos de casco a sotavento de um barco na mesma amura, não deve navegar acima do seu rumo próprio, salvo se passar prontamente por trás do outro.",
        "rrs:18": "Quando os barcos devem deixar uma marca do mesmo lado e um deles está na zona (três comprimentos de casco), o barco exterior, se estão sobrepostos, dá espaço na marca ao interior.",
        "rrs:19": "Quando barcos sobrepostos passam um obstáculo, o barco exterior dá ao interior espaço para passar entre si e o obstáculo.",
        "rrs:20": "Um barco que se aproxima de um obstáculo pode chamar para ter espaço para virar; o barco chamado vira logo ou responde «Vira», e depois deixa esse espaço.",
        "rrs:44": "Um barco que possa ter infringido uma regra da parte 2 ou a regra 31 pode exonerar-se fazendo prontamente uma penalização de uma volta (uma viragem e uma cambada) depois de se afastar dos outros; se causou dano grave ou obteve vantagem significativa, a penalização é a desistência.",
        "rrs:2": "Os barcos e os seus proprietários competem segundo os princípios reconhecidos de desportivismo e jogo limpo; um barco só é penalizado por esta regra se ficar claramente estabelecido que os infringiu.",
        "rrs:1": "Um barco ou concorrente presta toda a ajuda possível a qualquer pessoa ou embarcação em perigo.",
        "rrs:26": "A partida segue uma sequência de sinais: atenção cinco minutos antes do sinal de partida, preparação quatro minutos antes, retirada da bandeira de preparação um minuto antes, partida a zero; valem os sinais visuais, não o som.",
        "rrs:29": "Se um barco está do lado do percurso da linha no sinal de partida, a comissão iça a bandeira X (chamada individual); se não consegue identificar os barcos ou o procedimento está errado, iça o Primeiro Substituto (chamada geral).",
        "rrs:30": "Quando a bandeira I foi içada, um barco que no último minuto antes do seu sinal de partida tenha parte do casco, da tripulação ou do equipamento do lado do percurso da linha deve voltar ao lado de pré-partida por um prolongamento da linha antes de partir.",
        "rrs:28": "Um barco parte, navega o percurso descrito nas instruções de regata e termina.",
        "rrs:31": "Durante a regata, um barco não toca numa marca de partida antes de partir, numa marca que inicia, delimita ou termina o troço que navega, nem numa marca de chegada depois de terminar.",
        "col:5": "Qualquer embarcação mantém em permanência uma vigilância adequada, visual e auditiva, por todos os meios disponíveis.",
        "col:7": "Uma embarcação usa todos os meios disponíveis para determinar se existe risco de abalroamento; em caso de dúvida considera-se que existe, nomeadamente se a marcação de uma embarcação que se aproxima não varia sensivelmente.",
        "col:8": "Uma manobra para evitar o abalroamento é franca, feita com ampla antecedência e suficientemente grande para ser vista pela outra embarcação; evita-se uma série de pequenas alterações.",
        "col:12": "Dois veleiros: se cada um recebe o vento por um bordo diferente, o que o recebe por bombordo afasta-se da rota do outro; se ambos o recebem pelo mesmo bordo, o de barlavento afasta-se do de sotavento.",
        "col:13": "Qualquer embarcação que alcance outra afasta-se da rota desta; alcança a que chega de mais de 22,5° por ante-a-ré do través da outra.",
        "col:14": "Duas embarcações de propulsão mecânica que se encontram de proa cada uma altera o rumo para estibordo e cruzam-se por bombordo.",
        "col:15": "Duas embarcações de propulsão mecânica com rotas que se cruzam: a que vê a outra por estibordo afasta-se e, se possível, evita passar-lhe pela proa.",
        "col:16": "A embarcação que deve afastar-se age o mais cedo possível e com decisão para passar bem afastada.",
        "col:17": "A embarcação que não tem de se afastar mantém rumo e velocidade; pode manobrar logo que seja evidente que a outra não se afasta, e deve fazê-lo se o abalroamento já não puder ser evitado só pela manobra da outra.",
        "col:18": "Uma embarcação de propulsão mecânica em marcha afasta-se da rota de uma embarcação à vela (e de uma embarcação sem governo, com capacidade de manobra restrita ou que pesca).",
        "col:25": "Uma embarcação à vela em marcha mostra luzes de bordo (vermelha a bombordo, verde a estibordo) e uma luz de popa branca.",
    },
    "ch": {
        "vocabulaire": {
            "t": "O barco e o seu vocabulário",
            "p": ["Um veleiro descreve-se pelas suas partes. O {coque|casco} é o corpo do barco; a {etrave|proa} é a frente, a {etambot|popa} a traseira. O {pont|convés} cobre-o, e o {cockpit|cockpit} é onde se senta para governar.",
                  "Olhando para a proa, {babord|bombordo} fica à esquerda (luz vermelha, de noite) e {tribord|estibordo} à direita (luz verde).",
                  "O {mat|mastro} leva as velas: a {grand-voile|grande}, presa ao mastro e à {bome|retranca}, e à frente o {foc|estai} ou a {genois|genoa}. Içam-se com as {drisse|adriças} e regulam-se com as {ecoute|escotas}. A bordo, uma corda chama-se {bout|cabo}.",
                  "Debaixo de água, a {quille|quilha} limita o abatimento e o seu {lest|lastro} endireita o barco; o {safran|leme}, comandado pela {barre|cana}, dirige-o."],
            "q": "Está ao leme a olhar para a proa. De que lado fica estibordo, e que cor de luz leva à noite?",
            "a": "À direita; a luz de estibordo é verde (bombordo, à esquerda, leva a luz vermelha).",
        },
        "vent": {
            "t": "O vento e os andamentos",
            "p": ["O vento nomeia-se pelo ponto de onde vem: um vento de norte sopra para sul. O lado de onde vem diz-se {au-vent|barlavento}; o lado oposto, {sous-le-vent|sotavento}.",
                  "Um veleiro não pode avançar contra o vento: de cada lado dessa direção, cerca de 45 graus, estende-se a {zone-de-non-vent|zona sem vento}. Avança em todas as outras direções, chamadas {allure|andamentos}.",
                  "Do mais próximo do vento ao mais afastado: a {pres|bolina} (cerca de 45° do vento), a {bon-plein|bolina folgada}, o {travers|través} (90°), o {largue|largo} (cerca de 120° a 135°) e a {vent-arriere|popa} (180°).",
                  "A amura diz por que lado chega o vento: {tribord-amures|amura a estibordo} se chega pela direita do barco, {babord-amures|amura a bombordo} pela esquerda.",
                  "A bordo sente-se o {vent-apparent|vento aparente}, soma do {vent-reel|vento real} e do vento criado pelo avanço do barco; parece vir mais de proa do que o real."],
            "q": "O vento chega pela direita, perpendicular ao eixo do barco. Que andamento, que amura?",
            "a": "O través, amura a estibordo (o vento chega por estibordo).",
        },
        "manoeuvres": {
            "t": "Regular as velas e manobrar",
            "p": ["As velas regulam-se conforme o andamento: {border|caça-se} (puxa-se a escota) para ir para o vento, {choquer|folga-se} (larga-se) para se afastar. Uma vela que {faseyer|bate} está demasiado folgada.",
                  "Para mudar de direção: {lofer|orçar} é aproximar-se do vento; {abattre|arribar} é afastar-se.",
                  "{virer|Virar} é fazer passar a proa pelo vento; avisa-se a tripulação com «{pare-a-virer|pronto a virar}». {empanner|Cambar} é fazer passar a popa pelo vento: a retranca atravessa o barco, o que é perigoso; anuncia-se «{pare-a-empanner|pronto a cambar}» e respeita-se o aviso {attention-a-la-bome|cuidado com a retranca}.",
                  "Quando o vento aumenta, o barco {gite|adorna} mais: folgam-se as escotas, orça-se suavemente, ou {prendre-un-ris|tira-se um rizo}, isto é, reduz-se a superfície da grande."],
            "q": "O vento aumenta e o barco adorna demais. Indique dois gestos para o aliviar.",
            "a": "Folgar as escotas (sobretudo a da grande) e tirar um rizo; também se pode orçar um pouco para que as velas trabalhem menos.",
        },
        "cap": {
            "t": "Rumo, distância e carta",
            "p": ["O {cap|rumo} é a direção do barco, em graus de 0 a 360 a partir do norte: 090° é este, 180° sul, 270° oeste.",
                  "O {noeud-vitesse|nó} é a unidade de velocidade: uma milha náutica por hora. Uma milha vale 1 852 metros, um minuto de latitude, que se lê na escala vertical da carta. Distância = velocidade × tempo.",
                  "A agulha dá o rumo da agulha. Corrigido do desvio (próprio do barco) dá o rumo magnético; corrigido da declinação (diferença entre norte magnético e norte verdadeiro, indicada na carta) dá o rumo verdadeiro, o que se traça na carta. Uma declinação oeste conta-se negativa: verdadeiro = magnético + declinação.",
                  "O vento e a corrente afastam o barco da sua trajetória: é a {derive|deriva}. A {route-fond|derrota no fundo} é a rota realmente seguida sobre o fundo, diferente do rumo."],
            "q": "Navega a 6 nós. Em quanto tempo percorre 15 milhas?",
            "a": "15 ÷ 6 = 2,5 horas, isto é, 2 h 30.",
        },
        "marees": {
            "t": "Marés e correntes",
            "p": ["A {maree|maré} é a subida e a descida do mar, cerca de duas vezes por dia. O mar sobe durante a {flot|enchente} até à {pleine-mer|preia-mar}, depois desce durante a {jusant|vazante} até à {basse-mer|baixa-mar}. Passam cerca de seis horas entre preia-mar e baixa-mar.",
                  "A {marnage|amplitude da maré} é a diferença de altura entre preia-mar e baixa-mar. Na {etale|estofa}, no momento da inversão, quase não há {courant|corrente} de maré.",
                  "A regra dos duodécimos estima a altura durante a maré: da amplitude, a água sobe 1/12 na primeira hora, 2/12 na segunda, 3/12 na terceira, 3/12 na quarta, 2/12 na quinta, 1/12 na sexta.",
                  "A corrente de maré leva o barco: favorável, ajuda; contrária, trava. Quando a corrente vai contra o vento, o mar fica mais curto e encapelado."],
            "q": "A amplitude é de 6 m. Quanto subiu a água após duas horas de enchente?",
            "a": "1/12 + 2/12 = 3/12, isto é, 1/4 de 6 m: 1,5 m.",
        },
        "meteo": {
            "t": "A meteorologia",
            "p": ["A escala de {beaufort|Beaufort} classifica o vento de 0 a 12: força 4 = 11 a 16 nós, força 6 = 22 a 27 nós, força 8 = 34 a 40 nós (temporal). Acima da força 6, navegar exige experiência.",
                  "Um {anticyclone|anticiclone} é uma zona de altas pressões (acima de cerca de 1 013 hPa): tempo estável, vento fraco. Uma {depression|depressão} é uma zona de baixas pressões: nuvens, chuva, vento mais forte. No hemisfério norte, o vento gira no sentido horário à volta de um anticiclone e no sentido anti-horário à volta de uma depressão.",
                  "Antes de partir lê-se o {bulletin-meteo|boletim meteorológico}: vento médio, {rafale|rajadas}, estado do mar. Um {grain|aguaceiro} é uma rajada breve com chuva; a {orage|trovoada} obriga a regressar.",
                  "Perto da costa, no verão, a {brise-de-mer|brisa marítima} sopra à tarde para terra; a {brise-de-terre|brisa terrestre} sopra de noite para o largo. A {houle|ondulação} é uma onda longa vinda de longe; o {clapot|mar picado} é um mar curto e desordenado."],
            "q": "O boletim anuncia «vento de força 6, rajadas a 8». Converta a força 6 em nós e diga o que significa a força 8.",
            "a": "Força 6: 22 a 27 nós. Força 8: 34 a 40 nós, um temporal — a evitar por uma tripulação principiante.",
        },
        "balisage": {
            "t": "Balizagem e luzes",
            "p": ["A balizagem guia e avisa dos perigos. Na Europa segue-se o sistema AISM/IALA, região A. As marcas laterais ladeiam um canal; descrevem-se no sentido convencional, ao entrar num porto vindo do largo.",
                  "Marca de bombordo: vermelha, cilíndrica (deixa-se a bombordo). Marca de estibordo: verde, cónica (deixa-se a estibordo). Ao entrar vê-se vermelho à esquerda e verde à direita; ao sair, o contrário.",
                  "Uma marca cardinal tem o nome do lado onde está a água segura: uma cardinal Norte passa-se a norte dela. Norte: preta em cima, amarela em baixo; Sul: amarela em cima, preta em baixo; Este: preto-amarelo-preto; Oeste: amarelo-preto-amarelo.",
                  "Uma {bouee|bóia} preta com faixas vermelhas marca um perigo isolado (evita-se largamente); uma bóia de listas verticais vermelhas e brancas, águas navegáveis; uma marca amarela, uma zona especial.",
                  "De noite, um veleiro a navegar à vela mostra uma luz vermelha a bombordo, uma verde a estibordo e uma branca à popa; a motor acrescenta uma luz branca de topo."],
            "q": "Entra no porto vindo do largo e vê uma bóia vermelha cilíndrica. Por que lado a deixa?",
            "a": "A bombordo (vermelho à esquerda ao entrar).",
        },
        "abordage": {
            "t": "Evitar o abalroamento no mar (COLREG)",
            "p": ["O COLREG é o regulamento internacional de 1972 para evitar abalroamentos no mar (RIEAM em português). Aplica-se a todas as embarcações, veleiros incluídos; durante uma regata, as regras de regata regem os concorrentes entre si (capítulos 9 a 11).",
                  "Três deveres precedem qualquer regra de prioridade: vigiar (regra 5), reconhecer o risco de abalroamento — se a marcação de uma embarcação que se aproxima não muda, o risco existe (regra 7) — e agir cedo e com decisão (regra 8).",
                  "Retenha dois papéis: a embarcação que deve afastar-se manobra cedo e com decisão; a outra mantém rumo e velocidade enquanto a primeira age.",
                  "Em resumo, à vela: vento por bordos diferentes, afasta-se o que o recebe por bombordo; pelo mesmo bordo, o de barlavento; quem alcança afasta-se; um barco a motor afasta-se de um veleiro."],
            "q": "Dois veleiros cruzam-se no mar, fora de regata. O primeiro recebe o vento por estibordo, o segundo por bombordo. Qual se afasta e segundo que regra?",
            "a": "O que recebe o vento por bombordo afasta-se (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Regata: a partida e o percurso",
            "p": ["Uma regata é organizada pela {comite-de-course|comissão de regata}, que, do seu {bateau-comite|barco da comissão}, coloca a {ligne-de-depart|linha de partida}: o espaço entre o barco da comissão e uma {marque-de-depart|marca de partida}. Antes do {signal-de-depart|sinal de partida} fica-se do lado de pré-partida da linha.",
                  "Se um barco está do lado do percurso no sinal, é uma {faux-depart|partida antecipada}: deve voltar e partir de novo. Se a comissão não consegue identificar os barcos, anula a partida com uma {rappel-general|chamada geral}.",
                  "O {parcours|percurso}, descrito nas instruções de regata, costuma ser: partida, bolina até à {bouee-au-vent|marca de barlavento}, descida para a {bouee-sous-le-vent|marca de sotavento} ou uma {porte|porta}, por vezes várias voltas, e {arrivee|chegada} na {ligne-d-arrivee|linha de chegada}."],
            "q": "Na sua partida, a comissão iça a bandeira X com um som. O que significa para si e o que faz?",
            "a": "É uma chamada individual (RRS 29): no sinal, parte do seu barco estava do lado do percurso. Volta por inteiro ao lado de pré-partida e depois cruza a linha; até o fazer, não partiu.",
        },
        "priorites": {
            "t": "Regata: as prioridades",
            "p": ["Em regata, a parte 2 das {regles-de-course|regras de regata} diz quem deve afastar-se de quem. Bastam duas noções: a amura (capítulo 2) e a sobreposição. Um barco está «atrás» de outro quando o seu casco fica inteiramente atrás de uma linha perpendicular ao eixo do outro que passa pelo seu ponto mais à ré; senão, os barcos estão sobrepostos.",
                  "Leem-se as regras por ordem: amuras opostas (10); mesma amura, sobrepostos (11) ou sem sobreposição (12). A viragem (13) vem primeiro. As regras 14 a 17 limitam os direitos das regras 10 a 13.",
                  "Um barco com {priorite|prioridade} pode manter o rumo, mas não deve mudá-lo sem deixar ao outro espaço para se afastar. Se se julga que uma regra foi infringida, pode assinalar-se: é o {protestation|protesto}."],
            "q": "A está com amura a estibordo, B a bombordo; os rumos convergem. B vê que A não muda de rumo. Quem se afasta, segundo que regra? Que deve fazer A se vir que B não se afasta?",
            "a": "B afasta-se (RRS 10). A, embora com prioridade, deve evitar o contacto logo que seja claro que B não se afasta (RRS 14).",
        },
        "marques": {
            "t": "Regata: marcas, obstáculos e penalizações",
            "p": ["Nas marcas o jogo aperta-se. A zona é o círculo de três comprimentos de casco à volta da marca. Quando dois barcos devem deixar a marca do mesmo lado e um está na zona, aplica-se a regra 18.",
                  "O espaço na marca é o espaço para navegar até à marca e depois contorná-la pelo lado exigido. Os obstáculos (um rochedo, um barco fundeado…) têm regras próprias (19 e 20).",
                  "Um barco que julga ter infringido uma regra pode exonerar-se na água, sem esperar: faz uma {penalite|penalização} de uma {tour-de-penalite|volta}. Senão, o outro barco pode protestar e um {jury|júri} decide depois da regata.",
                  "Seja qual for a regra, prima o desportivismo: não se ganha a fazer batota."],
            "q": "Dois barcos sobrepostos chegam a uma marca a deixar a bombordo; A está por dentro, B por fora, e um está na zona. Quem deve dar espaço na marca?",
            "a": "B, o barco exterior, dá a A, o interior, espaço na marca (RRS 18).",
        },
        "securite": {
            "t": "Segurança no mar",
            "p": ["Antes de partir: ler o {bulletin-meteo|boletim meteorológico}, verificar o material, dizer a alguém a hora prevista de regresso. A bordo, cada pessoa tem um colete de salvação adequado, que se veste quando as condições o exigem.",
                  "Três níveis de chamada em VHF, no canal 16 (escuta de socorro): MAYDAY (dito três vezes) para um perigo grave e iminente; PAN PAN para uma urgência sem perigo imediato; SÉCURITÉ para um aviso de navegação ou meteorológico.",
                  "Em França, o socorro no mar é coordenado pelos CROSS, contactáveis no canal 16 ou, de um telemóvel, no 196.",
                  "{homme-a-la-mer|Homem ao mar}: gritar «homem ao mar», lançar-lhe uma bóia, designar uma pessoa que nunca o perca de vista e dar o alarme. Há vários métodos de recuperação: aprenda um na prática, com um monitor."],
            "q": "Quando se usa MAYDAY e quando PAN PAN?",
            "a": "MAYDAY: perigo grave e iminente para uma pessoa ou o barco. PAN PAN: urgência sem perigo imediato, por exemplo uma avaria que se controla.",
        },
    },
    "revision": [
        ("Navega ao 270° (oeste) com vento de norte. Que andamento, que amura?", "O norte está à sua direita: o vento chega por estibordo, perpendicular — é o través, amura a estibordo."),
        ("A amplitude da maré é de 8 m. Quanto sobe a água durante a terceira hora da enchente?", "3/12 de 8 m = 2 m."),
        ("Dois veleiros estão na mesma amura; A está a barlavento de B. Quem se afasta, no mar fora de regata e depois em regata?", "A, nos dois casos: COLREG 12 a) ii) no mar, RRS 11 em regata (barcos sobrepostos)."),
        ("Que marca lateral se deixa a estibordo ao entrar no porto? E o que se diz em VHF perante um perigo grave e iminente?", "A verde, cónica. «MAYDAY», três vezes, no canal 16."),
    ],
}

TEXTES["de"] = {
    "titre": "Segel-Theoriekurs",
    "desc": "Ein kostenloser Segel-Theoriekurs in {n} Kapiteln: Vokabular, Kurse zum Wind, Kurs und Distanz, Gezeiten, Wetter, Betonnung, KVR/COLREG und Wettsegelbestimmungen (RRS 2025-2028), mit korrigierten Übungen.",
    "h1": "Segel-Theoriekurs",
    "intro": "Ein vollständiger, kostenloser Kurs, vom Vokabular des Bootes bis zu den Grundkenntnissen eines Küstenpatents, in {n} Kapiteln. Jedes Kapitel setzt nur die vorherigen voraus: lies sie der Reihe nach. Jede Regel wird mit ihrer genauen Nummer und Überschrift zitiert, mit dem, was sie verlangt; jedes Kapitel endet mit einer korrigierten Übung, der Kurs mit vier Wiederholungsfragen. Keine Anmeldung nötig.",
    "sommaire": "Inhalt — {n} Kapitel", "chap": "Kapitel", "regles": "Zitierte Regeln", "exo": "Übung", "corr": "Lösung",
    "haut": "↑ Inhalt", "rev": "Wiederholung des Kurses", "rev_intro": "Vier Fragen, die den ganzen Kurs aufgreifen.", "schema": "Schemata",
    "note": "Quellen: Racing Rules of Sailing 2025-2028 (World Sailing, {lien}); COLREG 1972 (IMO), mit den Überschriften des offiziellen englischen Textes; Betonnung IALA, Region A. Diese Zusammenfassungen ersetzen die Texte nicht, die maßgeblich sind; Sonderfälle werden nicht behandelt, und der Kurs ersetzt weder eine praktische Ausbildung noch die Prüfung.",
    "regles_texte": {
        "rrs:10": "Wenn Boote auf entgegengesetzten Bugen segeln, muss ein Boot auf Backbordbug einem Boot auf Steuerbordbug ausweichen.",
        "rrs:11": "Wenn Boote auf gleichem Bug und überlappend segeln, muss das Luvboot dem Leeboot ausweichen.",
        "rrs:12": "Wenn Boote auf gleichem Bug und nicht überlappend segeln, muss das achtern befindliche Boot dem voraus befindlichen Boot ausweichen.",
        "rrs:13": "Nach dem Durchgang durch den Wind weicht ein Boot den anderen aus, bis es hoch am Wind segelt; währenddessen gelten für es die Regeln 10, 11 und 12 nicht.",
        "rrs:14": "Ein Boot vermeidet Kontakt mit einem anderen, wenn es vernünftigerweise möglich ist; auch mit Wegerecht muss es handeln, sobald klar ist, dass das andere nicht ausweicht.",
        "rrs:15": "Erwirbt ein Boot Wegerecht, gibt es dem anderen zunächst Raum zum Ausweichen, es sei denn, es erwirbt es durch Handlungen des anderen.",
        "rrs:16": "Ändert ein Boot mit Wegerecht seinen Kurs, gibt es dem anderen Raum zum Ausweichen.",
        "rrs:17": "Wird ein achteres Boot innerhalb von zwei Rumpflängen in Lee eines Bootes auf demselben Bug überlappend, darf es nicht über seinen Raumkurs hinaus anluven, es sei denn, es passiert umgehend achtern das andere.",
        "rrs:18": "Müssen Boote eine Marke auf derselben Seite lassen und ist eines in der Zone (drei Rumpflängen), gibt das äußere Boot, wenn sie überlappen, dem inneren Raum an der Tonne.",
        "rrs:19": "Passieren überlappende Boote ein Hindernis, gibt das äußere Boot dem inneren Raum, zwischen ihm und dem Hindernis durchzufahren.",
        "rrs:20": "Ein Boot, das sich einem Hindernis nähert, kann um Raum zum Wenden rufen; das gerufene Boot wendet sofort oder antwortet „Wende“ und gibt dann diesen Raum.",
        "rrs:44": "Ein Boot, das eine Regel von Teil 2 oder Regel 31 verletzt haben könnte, kann sich entlasten, indem es nach Freikommen von den anderen umgehend eine Ein-Drehung-Strafe (eine Wende und eine Halse) ausführt; bei schwerem Schaden oder erheblichem Vorteil ist die Strafe die Aufgabe.",
        "rrs:2": "Boote und ihre Eigner segeln nach den anerkannten Grundsätzen der Sportlichkeit und Fairness; ein Boot wird nach dieser Regel nur bestraft, wenn eindeutig feststeht, dass es sie verletzt hat.",
        "rrs:1": "Ein Boot oder Wettfahrtteilnehmer leistet jeder Person oder jedem Fahrzeug in Gefahr jede mögliche Hilfe.",
        "rrs:26": "Der Start folgt einer Signalfolge: Ankündigung fünf Minuten vor dem Startsignal, Vorbereitung vier Minuten vorher, Vorbereitungsflagge eine Minute vorher nieder, Start bei null; maßgeblich sind die optischen Signale, nicht der Ton.",
        "rrs:29": "Ist ein Boot beim Startsignal auf der Kursseite der Linie, setzt der Wettfahrtausschuss die Flagge X (Einzelrückruf); kann er die Boote nicht erkennen oder ist das Verfahren fehlerhaft, setzt er den Ersatzwimpel (Allgemeiner Rückruf).",
        "rrs:30": "Ist die Flagge I gesetzt, muss ein Boot, das in der letzten Minute vor seinem Startsignal mit einem Teil von Rumpf, Besatzung oder Ausrüstung auf der Kursseite der Linie war, vor dem Start über eine Verlängerung der Linie auf die Vorstartseite zurückkehren.",
        "rrs:28": "Ein Boot startet, segelt den in den Segelanweisungen beschriebenen Kurs und geht durchs Ziel.",
        "rrs:31": "Während der Wettfahrt berührt ein Boot keine Startmarke vor dem Start, keine Marke, die die Strecke beginnt, begrenzt oder beendet, und keine Zielmarke nach dem Zieldurchgang.",
        "col:5": "Jedes Fahrzeug hält jederzeit durch Sehen und Hören sowie mit allen verfügbaren Mitteln gehörigen Ausguck.",
        "col:7": "Ein Fahrzeug nutzt alle verfügbaren Mittel, um festzustellen, ob Kollisionsgefahr besteht; im Zweifel gilt sie als gegeben, insbesondere wenn sich die Peilung eines sich nähernden Fahrzeugs nicht merklich ändert.",
        "col:8": "Ein Manöver zur Kollisionsverhütung ist entschlossen, rechtzeitig und so groß, dass das andere Fahrzeug es erkennt; eine Folge kleiner Änderungen wird vermieden.",
        "col:12": "Zwei Segelfahrzeuge: Hat jedes den Wind von einer anderen Seite, muss das mit Wind von Backbord dem anderen ausweichen; haben beide ihn von derselben Seite, muss das Luvfahrzeug dem Leefahrzeug ausweichen.",
        "col:13": "Jedes Fahrzeug, das ein anderes überholt, muss dem überholten aus dem Weg gehen; überholend ist, wer sich von mehr als 22,5° achterlicher als querab nähert.",
        "col:14": "Begegnen sich zwei Maschinenfahrzeuge auf entgegengesetzten Kursen, ändert jedes seinen Kurs nach Steuerbord und sie passieren Backbord an Backbord.",
        "col:15": "Kreuzen sich die Kurse zweier Maschinenfahrzeuge, muss dasjenige, das das andere an seiner Steuerbordseite hat, ausweichen und möglichst nicht vor dessen Bug kreuzen.",
        "col:16": "Das ausweichpflichtige Fahrzeug handelt so früh wie möglich und entschlossen, um weit genug freizubleiben.",
        "col:17": "Das nicht ausweichpflichtige Fahrzeug behält Kurs und Geschwindigkeit bei; es darf manövrieren, sobald klar ist, dass das andere nicht ausweicht, und muss es, wenn die Kollision nicht mehr allein durch das Manöver des anderen vermieden werden kann.",
        "col:18": "Ein Maschinenfahrzeug in Fahrt muss einem Segelfahrzeug aus dem Weg gehen (und einem manövrierunfähigen, manövrierbehinderten oder fischenden Fahrzeug).",
        "col:25": "Ein Segelfahrzeug in Fahrt führt Seitenlichter (rot an Backbord, grün an Steuerbord) und ein weißes Hecklicht.",
    },
    "ch": {
        "vocabulaire": {
            "t": "Das Boot und sein Vokabular",
            "p": ["Eine Segelyacht wird durch ihre Teile beschrieben. Der {coque|Rumpf} ist der Körper des Bootes; der {etrave|Bug} ist sein vorderes, das {etambot|Heck} sein hinteres Ende. Das {pont|Deck} bedeckt ihn, und die {cockpit|Plicht} ist der Platz zum Steuern.",
                  "Blickt man nach vorn, ist {babord|Backbord} links (rotes Licht, nachts) und {tribord|Steuerbord} rechts (grünes Licht).",
                  "Der {mat|Mast} trägt die Segel: das {grand-voile|Großsegel}, am Mast und am {bome|Baum} befestigt, und vorn die {foc|Fock} oder die {genois|Genua}. Man setzt sie mit den {drisse|Fallen} und stellt sie mit den {ecoute|Schoten} ein. An Bord heißt ein Tau {bout|Leine}.",
                  "Unter Wasser begrenzt der {quille|Kiel} die Abdrift und sein {lest|Ballast} richtet das Boot auf; das {safran|Ruder}, bedient von der {barre|Pinne oder dem Rad}, lenkt es."],
            "q": "Du steuerst und blickst zum Bug. Auf welcher Seite ist Steuerbord, und welche Lichtfarbe führt sie nachts?",
            "a": "Rechts; das Steuerbordlicht ist grün (Backbord, links, führt das rote Licht).",
        },
        "vent": {
            "t": "Wind und Kurse zum Wind",
            "p": ["Der Wind wird nach der Richtung benannt, aus der er kommt: Nordwind weht nach Süden. Die Seite, von der er kommt, heißt {au-vent|Luv}; die gegenüberliegende {sous-le-vent|Lee}.",
                  "Eine Segelyacht kann nicht gegen den Wind fahren: beidseits dieser Richtung, auf etwa 45 Grad, liegt die {zone-de-non-vent|Segelverbotszone}. Sie fährt in allen anderen Richtungen, den {allure|Kursen zum Wind}.",
                  "Vom windnächsten zum windfernsten: {pres|hoch am Wind} (etwa 45° zum Wind), {bon-plein|angeluvter Halbwind}, {travers|Halbwind} (90°), {largue|raumer Wind} (etwa 120° bis 135°) und {vent-arriere|Vorwind} (180°).",
                  "Der Bug sagt, von welcher Seite der Wind kommt: {tribord-amures|Steuerbordbug}, wenn er von rechts kommt, {babord-amures|Backbordbug}, wenn von links.",
                  "An Bord spürt man den {vent-apparent|scheinbaren Wind}, die Summe aus dem {vent-reel|wahren Wind} und dem durch die Fahrt erzeugten Wind; er scheint mehr von vorn zu kommen als der wahre."],
            "q": "Der Wind kommt von rechts, senkrecht zur Bootsachse. Welcher Kurs, welcher Bug?",
            "a": "Halbwind, Steuerbordbug (der Wind kommt von Steuerbord).",
        },
        "manoeuvres": {
            "t": "Segel trimmen und manövrieren",
            "p": ["Die Segel werden nach dem Kurs eingestellt: man {border|holt dicht} (zieht die Schot an), um zum Wind zu gehen, man {choquer|fiert} (gibt Schot), um sich zu entfernen. Ein Segel, das {faseyer|killt}, ist zu weit gefiert.",
                  "Zum Richtungswechsel: {lofer|Anluven} heißt zum Wind drehen; {abattre|Abfallen} heißt vom Wind wegdrehen.",
                  "{virer|Wenden} heißt, den Bug durch den Wind zu führen; die Crew wird mit „{pare-a-virer|klar zur Wende}“ gewarnt. {empanner|Halsen} heißt, das Heck durch den Wind zu führen: der Baum schlägt über das Boot, was gefährlich ist; man ruft „{pare-a-empanner|klar zur Halse}“ und beachtet {attention-a-la-bome|Achtung, Baum}.",
                  "Frischt der Wind auf, {gite|krängt} das Boot stärker: man fiert die Schoten, luvt behutsam an oder {prendre-un-ris|reffte}, das heißt, man verkleinert die Fläche des Großsegels."],
            "q": "Der Wind frischt auf und das Boot krängt zu stark. Nenne zwei Maßnahmen zur Entlastung.",
            "a": "Schoten fieren (vor allem das Groß) und ein Reff einbinden; man kann auch etwas anluven, damit die Segel weniger ziehen.",
        },
        "cap": {
            "t": "Kurs, Distanz und Karte",
            "p": ["Der {cap|Kurs} ist die Richtung des Bootes, in Grad von 0 bis 360 ab Nord: 090° ist Ost, 180° Süd, 270° West.",
                  "Der {noeud-vitesse|Knoten} ist die Geschwindigkeitseinheit: eine Seemeile pro Stunde. Eine Seemeile sind 1 852 Meter, eine Breitenminute, die man am senkrechten Maßstab der Karte abliest. Distanz = Geschwindigkeit × Zeit.",
                  "Der Kompass gibt den Kompasskurs. Um die Ablenkung (bootsspezifisch) korrigiert ergibt er den missweisenden Kurs; um die Missweisung (Abweichung zwischen magnetisch Nord und rechtweisend Nord, in der Karte angegeben) korrigiert den rechtweisenden Kurs, den man in die Karte einträgt. Westliche Missweisung zählt negativ: rechtweisend = missweisend + Missweisung.",
                  "Wind und Strom versetzen das Boot von seinem Kurs: das ist die {derive|Abdrift}. Der {route-fond|Kurs über Grund} ist der tatsächlich über Grund gefahrene Weg, verschieden vom Kurs."],
            "q": "Du fährst 6 Knoten. Wie lange brauchst du für 15 Seemeilen?",
            "a": "15 ÷ 6 = 2,5 Stunden, also 2 h 30.",
        },
        "marees": {
            "t": "Gezeiten und Strömungen",
            "p": ["Die {maree|Tide} ist das Steigen und Fallen des Meeres, etwa zweimal am Tag. Das Wasser steigt während der {flot|Flut} bis zum {pleine-mer|Hochwasser}, dann fällt es während der {jusant|Ebbe} bis zum {basse-mer|Niedrigwasser}. Zwischen Hoch- und Niedrigwasser vergehen etwa sechs Stunden.",
                  "Der {marnage|Tidenhub} ist der Höhenunterschied zwischen Hoch- und Niedrigwasser. Zur {etale|Stauwasserzeit}, beim Kentern, gibt es fast keinen Gezeiten{courant|strom}.",
                  "Die Zwölftelregel schätzt die Höhe im Tidenverlauf: vom Tidenhub steigt das Wasser in der ersten Stunde 1/12, in der zweiten 2/12, in der dritten 3/12, in der vierten 3/12, in der fünften 2/12, in der sechsten 1/12.",
                  "Der Gezeitenstrom trägt das Boot: mitlaufend hilft er, gegenan bremst er. Läuft der Strom gegen den Wind, wird die See kürzer und steiler."],
            "q": "Der Tidenhub beträgt 6 m. Wie weit ist das Wasser nach zwei Stunden Flut gestiegen?",
            "a": "1/12 + 2/12 = 3/12, also 1/4 von 6 m: 1,5 m.",
        },
        "meteo": {
            "t": "Das Wetter",
            "p": ["Die {beaufort|Beaufort}-Skala stuft den Wind von 0 bis 12 ein: Stärke 4 = 11 bis 16 Knoten, Stärke 6 = 22 bis 27 Knoten, Stärke 8 = 34 bis 40 Knoten (Sturm). Ab Stärke 6 braucht das Segeln Erfahrung.",
                  "Ein {anticyclone|Hoch} ist ein Hochdruckgebiet (über etwa 1 013 hPa): stabiles Wetter, schwacher Wind. Ein {depression|Tief} ist ein Tiefdruckgebiet: Wolken, Regen, stärkerer Wind. Auf der Nordhalbkugel dreht der Wind im Uhrzeigersinn um ein Hoch und gegen den Uhrzeigersinn um ein Tief.",
                  "Vor dem Auslaufen liest man den {bulletin-meteo|Wetterbericht}: mittlerer Wind, {rafale|Böen}, Seegang. Eine {grain|Regenbö} ist ein kurzer Windstoß mit Regen; bei einem {orage|Gewitter} läuft man ein.",
                  "In Küstennähe weht im Sommer die {brise-de-mer|Seebrise} nachmittags zum Land; die {brise-de-terre|Landbrise} nachts aufs Meer. Die {houle|Dünung} ist eine lange, weither kommende Welle; der {clapot|Kabbelsee} ist eine kurze, ungeordnete See."],
            "q": "Der Bericht meldet „Wind Stärke 6, Böen 8“. Rechne Stärke 6 in Knoten um und sage, was Stärke 8 bedeutet.",
            "a": "Stärke 6: 22 bis 27 Knoten. Stärke 8: 34 bis 40 Knoten, ein Sturm — für eine Anfängercrew zu meiden.",
        },
        "balisage": {
            "t": "Betonnung und Lichter",
            "p": ["Die Betonnung führt und warnt vor Gefahren. In Europa gilt das IALA-System, Region A. Seitenzeichen säumen eine Fahrrinne; sie werden in der Betonnungsrichtung beschrieben, beim Einlaufen vom Meer in einen Hafen.",
                  "Backbordtonne: rot, zylindrisch (an Backbord gelassen). Steuerbordtonne: grün, kegelförmig (an Steuerbord gelassen). Beim Einlaufen sieht man Rot links und Grün rechts; beim Auslaufen umgekehrt.",
                  "Ein Kardinalzeichen trägt den Namen der Seite, auf der das sichere Wasser liegt: ein Nord-Kardinalzeichen passiert man nördlich. Nord: schwarz oben, gelb unten; Süd: gelb oben, schwarz unten; Ost: schwarz-gelb-schwarz; West: gelb-schwarz-gelb.",
                  "Eine schwarze {bouee|Tonne} mit roten Bändern bezeichnet eine Einzelgefahr (weiträumig meiden); eine Tonne mit senkrechten roten und weißen Streifen sicheres Wasser; ein gelbes Zeichen ein Sondergebiet.",
                  "Nachts führt eine Segelyacht unter Segeln ein rotes Licht an Backbord, ein grünes an Steuerbord und ein weißes am Heck; unter Motor kommt ein weißes Topplicht hinzu."],
            "q": "Du läufst vom Meer in den Hafen ein und siehst eine rote zylindrische Tonne. An welcher Seite lässt du sie?",
            "a": "An Backbord (Rot links beim Einlaufen).",
        },
        "abordage": {
            "t": "Kollisionen auf See vermeiden (KVR / COLREG)",
            "p": ["Die KVR (englisch COLREG) sind die internationalen Regeln von 1972 zur Verhütung von Zusammenstößen auf See. Sie gelten für alle Fahrzeuge, Segelboote eingeschlossen; während einer Wettfahrt regeln die Wettsegelbestimmungen das Verhältnis der Teilnehmer untereinander (Kapitel 9 bis 11).",
                  "Drei Pflichten gehen jeder Vorfahrtsregel voraus: Ausguck halten (Regel 5), Kollisionsgefahr erkennen — ändert sich die Peilung eines sich nähernden Fahrzeugs nicht, besteht sie (Regel 7) — und früh und entschlossen handeln (Regel 8).",
                  "Merke zwei Rollen: Das ausweichpflichtige Fahrzeug manövriert früh und deutlich; das andere behält Kurs und Geschwindigkeit bei, solange das erste handelt.",
                  "Kurz, unter Segeln: Wind von verschiedenen Seiten, weicht das mit Wind von Backbord aus; von derselben Seite, das Luvboot; wer überholt, weicht aus; ein Motorboot weicht einem Segelboot aus."],
            "q": "Zwei Segelboote kreuzen sich auf See, außerhalb einer Wettfahrt. Das erste hat den Wind von Steuerbord, das zweite von Backbord. Welches weicht aus, nach welcher Regel?",
            "a": "Das mit Wind von Backbord weicht aus (COLREG 12 a) i)).",
        },
        "depart": {
            "t": "Wettfahrt: Start und Kurs",
            "p": ["Eine Wettfahrt wird vom {comite-de-course|Wettfahrtausschuss} ausgerichtet, der von seinem {bateau-comite|Startschiff} die {ligne-de-depart|Startlinie} legt: der Raum zwischen Startschiff und einer {marque-de-depart|Startmarke}. Vor dem {signal-de-depart|Startsignal} bleibt man auf der Vorstartseite der Linie.",
                  "Ist ein Boot beim Signal auf der Kursseite der Linie, ist das ein {faux-depart|Fehlstart}: es muss zurück und neu starten. Kann der Ausschuss die Boote nicht erkennen, bricht er den Start mit einem {rappel-general|Allgemeinen Rückruf} ab.",
                  "Der {parcours|Kurs}, in den Segelanweisungen beschrieben, verläuft meist: Start, Kreuz zur {bouee-au-vent|Luvtonne}, Vorwindstrecke zur {bouee-sous-le-vent|Leetonne} oder einem {porte|Tor}, manchmal mehrere Runden, dann {arrivee|Ziel} an der {ligne-d-arrivee|Ziellinie}."],
            "q": "Bei deinem Start setzt der Ausschuss die Flagge X mit einem Ton. Was bedeutet das für dich, und was tust du?",
            "a": "Es ist ein Einzelrückruf (RRS 29): beim Signal war ein Teil deines Bootes auf der Kursseite. Du kehrst vollständig auf die Vorstartseite zurück und kreuzt dann die Linie; bis dahin bist du nicht gestartet.",
        },
        "priorites": {
            "t": "Wettfahrt: die Vorfahrt",
            "p": ["In der Wettfahrt sagt Teil 2 der {regles-de-course|Wettsegelbestimmungen}, wer wem ausweichen muss. Zwei Begriffe genügen: der Bug (Kapitel 2) und die Überlappung. Ein Boot ist „achtern frei“ von einem anderen, wenn sein Rumpf ganz hinter einer Querlinie durch den hintersten Punkt des anderen liegt; sonst überlappen die Boote.",
                  "Die Regeln liest man der Reihe nach: entgegengesetzte Bugs (10); gleicher Bug, überlappend (11) oder nicht überlappend (12). Das Wenden (13) kommt zuerst. Die Regeln 14 bis 17 begrenzen die Rechte der Regeln 10 bis 13.",
                  "Ein Boot mit {priorite|Wegerecht} darf seinen Kurs halten, ihn aber nicht ändern, ohne dem anderen Raum zum Ausweichen zu geben. Glaubt man, eine Regel sei verletzt worden, kann man das melden: das ist der {protestation|Protest}."],
            "q": "A ist auf Steuerbordbug, B auf Backbordbug; die Kurse laufen zusammen. B sieht, dass A den Kurs nicht ändert. Wer weicht aus, nach welcher Regel? Was muss A tun, wenn er sieht, dass B nicht ausweicht?",
            "a": "B weicht aus (RRS 10). A muss trotz Wegerecht den Kontakt vermeiden, sobald klar ist, dass B nicht ausweicht (RRS 14).",
        },
        "marques": {
            "t": "Wettfahrt: Marken, Hindernisse und Strafen",
            "p": ["An den Marken wird es eng. Die Zone ist der Kreis von drei Rumpflängen um die Marke. Müssen zwei Boote die Marke auf derselben Seite lassen und ist eines in der Zone, gilt Regel 18.",
                  "Raum an der Tonne ist der Raum, bis zur Marke zu segeln und sie dann auf der vorgeschriebenen Seite zu runden. Hindernisse (ein Fels, ein ankerndes Boot …) haben eigene Regeln (19 und 20).",
                  "Ein Boot, das eine Regel verletzt zu haben glaubt, kann sich auf dem Wasser sofort entlasten: es führt eine {penalite|Strafe} von einer {tour-de-penalite|Drehung} aus. Sonst kann das andere Boot protestieren, und ein {jury|Schiedsgericht} entscheidet nach der Wettfahrt.",
                  "Welche Regel auch gilt, Sportlichkeit geht vor: man gewinnt nicht durch Betrug."],
            "q": "Zwei überlappende Boote erreichen eine Marke, die an Backbord zu lassen ist; A ist innen, B außen, und eines ist in der Zone. Wer muss Raum an der Tonne geben?",
            "a": "B, das äußere Boot, gibt A, dem inneren, Raum an der Tonne (RRS 18).",
        },
        "securite": {
            "t": "Sicherheit auf See",
            "p": ["Vor dem Auslaufen: den {bulletin-meteo|Wetterbericht} lesen, die Ausrüstung prüfen, jemandem die geplante Rückkehrzeit nennen. An Bord hat jeder eine passende Rettungsweste, die getragen wird, sobald die Bedingungen es verlangen.",
                  "Drei Stufen des UKW-Anrufs, auf Kanal 16 (Notruf-Hörwache): MAYDAY (dreimal gesagt) bei ernster und unmittelbarer Gefahr; PAN PAN bei Dringlichkeit ohne unmittelbare Gefahr; SÉCURITÉ bei einer Navigations- oder Wetterwarnung.",
                  "In Frankreich wird die Seenotrettung von den CROSS koordiniert, erreichbar auf Kanal 16 oder vom Mobiltelefon unter 196.",
                  "{homme-a-la-mer|Mann über Bord}: „Mann über Bord“ rufen, ihm einen Rettungsring zuwerfen, eine Person bestimmen, die ihn nie aus den Augen verliert, dann Alarm schlagen. Es gibt mehrere Bergemethoden: lerne eine praktisch, mit einem Ausbilder."],
            "q": "Wann benutzt man MAYDAY, und wann PAN PAN?",
            "a": "MAYDAY: ernste und unmittelbare Gefahr für eine Person oder das Boot. PAN PAN: Dringlichkeit ohne unmittelbare Gefahr, zum Beispiel eine Panne, die man im Griff hat.",
        },
    },
    "revision": [
        ("Du fährst Kurs 270° (West) bei Nordwind. Welcher Kurs zum Wind, welcher Bug?", "Nord liegt rechts von dir: der Wind kommt von Steuerbord, senkrecht — Halbwind, Steuerbordbug."),
        ("Der Tidenhub beträgt 8 m. Wie viel steigt das Wasser in der dritten Flutstunde?", "3/12 von 8 m = 2 m."),
        ("Zwei Segelboote sind auf demselben Bug; A liegt in Luv von B. Wer weicht aus, auf See außerhalb einer Wettfahrt und dann in der Wettfahrt?", "A, in beiden Fällen: COLREG 12 a) ii) auf See, RRS 11 in der Wettfahrt (überlappende Boote)."),
        ("Welches Seitenzeichen lässt man beim Einlaufen an Steuerbord? Und was sagt man per UKW bei ernster und unmittelbarer Gefahr?", "Das grüne, kegelförmige. „MAYDAY“, dreimal, auf Kanal 16."),
    ],
}

# ── Rendu ──────────────────────────────────────────────────────────────────────────────────────────────
CSS = """
body{margin:0;background:#071c31;color:#eef3f7;font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
:root{--panneau:#0f2438;--ivoire:#eef3f7;--gris:#9db2c6;--rouge:#e23a3e}
.page{max-width:48rem;margin:0 auto;padding:2rem 1.4rem 5rem}
h1{font-size:2rem;margin:1rem 0 .4rem}
h2{font-size:1.2rem;margin:0 0 .6rem}
h3{font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gris);margin:1.1rem 0 .4rem;font-weight:600}
.intro,.note,.rev-intro{color:var(--gris)}
.sommaire{background:var(--panneau);border-left:3px solid var(--rouge);padding:1rem 1.2rem;margin:1.4rem 0;border-radius:3px}
.sommaire ol{margin:.4rem 0 0;padding-left:1.4rem}
.sommaire li{margin:.15rem 0}
.chap{background:var(--panneau);border-left:3px solid var(--rouge);padding:1rem 1.2rem;margin:1.6rem 0;border-radius:3px;scroll-margin-top:4.5rem}
.chap .no{display:inline-block;min-width:1.8rem;color:var(--rouge);font-weight:700}
.chap p{margin:.5rem 0}
.regles ul{list-style:none;margin:0;padding:0}
.regles li{margin:.45rem 0}
a.regle,span.regle{display:inline-block;font-size:.74rem;letter-spacing:.05em;color:var(--ivoire);border:1px solid #27425b;border-radius:3px;padding:0 .4rem;margin-right:.3rem;white-space:nowrap;text-decoration:none}
a.regle:hover{border-color:var(--rouge)}
.exo{border-top:1px dashed #27425b;margin-top:1rem}
details{margin:.4rem 0}
summary{cursor:pointer;color:var(--gris)}
a.haut-lien{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--gris);text-decoration:none}
.chap a:not(.regle):not(.haut-lien),.sommaire a{color:var(--ivoire);text-decoration:underline;text-decoration-color:#27425b;text-underline-offset:3px}
.note{font-size:.85rem;margin-top:2rem}
.note a{color:var(--ivoire)}
.schemas{margin-top:.6rem}
"""

JS = """
(function(){
  var L=["fr","en","it","es","pt","de"];
  function auto(){var n=(navigator.language||"fr").slice(0,2);return L.indexOf(n)>=0?n:"en"}
  var s=null,a=true;
  try{s=localStorage.getItem("sm-langue")}catch(e){}
  if(L.indexOf(s)>=0){a=false}else{s=auto()}
  function set(l,saved){
    document.documentElement.lang=l;
    [].forEach.call(document.querySelectorAll("[data-l]"),function(e){e.hidden=e.getAttribute("data-l")!==l});
    [].forEach.call(document.querySelectorAll("#langues button"),function(b){
      var d=b.getAttribute("data-lang");
      b.setAttribute("aria-pressed",saved?(d===l):(d==="auto"))});
  }
  [].forEach.call(document.querySelectorAll("#langues button"),function(b){
    b.addEventListener("click",function(){
      var d=b.getAttribute("data-lang");
      if(d==="auto"){try{localStorage.removeItem("sm-langue")}catch(e){} set(auto(),false)}
      else{try{localStorage.setItem("sm-langue",d)}catch(e){} set(d,true)}
    });
  });
  set(s,!a);
  if(location.hash){var t=document.getElementById(location.hash.slice(1));if(t&&!t.closest("[hidden]")){t.scrollIntoView()}}
})();
"""

_LEX = re.compile(r"\{([a-z0-9-]+)\|([^}]+)\}")
_donnees_regles = None


def _e(s: str) -> str:
    return _html.escape(s, quote=False)


def _txt(s: str) -> str:
    """Échappe le texte, puis pose les liens lexique : {id|mot} -> <a href="lexique.html#id">mot</a>."""
    return _LEX.sub(lambda m: f'<a href="lexique.html#{m.group(1)}">{m.group(2)}</a>', _e(s))


def _brut(s: str) -> str:
    """Texte sans balisage lexique (titres, attributs)."""
    return _LEX.sub(lambda m: m.group(2), s)


def verifier() -> None:
    """Le plan et les six langues doivent se correspondre exactement : sinon la page ne se construit pas."""
    ids = [c["id"] for c in CHAPITRES]
    cles = {k for c in CHAPITRES for k in c["regles"]}
    for k in cles:
        genre, num = k.split(":")
        if genre == "rrs" and num not in RRS_T:
            raise ValueError(f"intitulé RRS manquant : {num}")
        if genre == "col" and num not in COL_T:
            raise ValueError(f"intitulé COLREG manquant : {num}")
    for lang in LANGUES:
        t = TEXTES[lang]
        manque = [i for i in ids if i not in t["ch"]] + [f"regle {k}" for k in cles if k not in t["regles_texte"]]
        if manque:
            raise ValueError(f"{lang} : incomplet ({manque})")
        if len(t["ch"]) != len(ids):
            raise ValueError(f"{lang} : {len(t['ch'])} chapitres pour {len(ids)} au plan")
        if len(t["revision"]) != 4:
            raise ValueError(f"{lang} : {len(t['revision'])} questions de révision au lieu de 4")
        for i in ids:
            c = t["ch"][i]
            if not (c.get("t") and c.get("p") and c.get("q") and c.get("a")):
                raise ValueError(f"{lang}/{i} : champ vide")


def _regles_json() -> dict:
    global _donnees_regles
    if _donnees_regles is None:
        import regles_page
        _donnees_regles = {r["cle"]: r for r in regles_page.charger()["regles"] if r.get("schema")}
    return _donnees_regles


def _schemas(cles: list, lang: str) -> str:
    """Les schémas viennent de regles.json (une seule source), rendus par regles_page.schema_statique()."""
    import regles_page
    sortie = []
    for cle in cles:
        r = _regles_json().get(cle)
        if r:
            sortie.append(regles_page.schema_statique(r, lang))
    return f'<div class="schemas">{"".join(sortie)}</div>' if sortie else ""


def _css_schemas() -> str:
    import regles_page
    css = regles_page.CSS
    try:
        i = css.index(".regle .schema{")
        j = css.index(".sc .sc-fant")
        j = css.index("\n", j)
        return css[i:j]
    except ValueError:
        return ""


def _lib_regle(k: str, lang: str) -> tuple[str, str, str]:
    """(libellé, intitulé exact, lien ou '') pour une clé 'rrs:10' / 'col:13'."""
    genre, num = k.split(":")
    if genre == "rrs":
        return (f"RRS {RRS_LIB.get(num, num)}", RRS_T[num][LANGUES.index(lang)], f"regles-de-course.html#r{num}")
    return (f"COLREG {COL_LIB.get(num, num)}", COL_T[num], "")


def _chapitre(n: int, ch: dict, lang: str) -> str:
    t = TEXTES[lang]
    c = t["ch"][ch["id"]]
    corps = "".join(f"<p>{_txt(p)}</p>" for p in c["p"])
    regles = ""
    if ch["regles"]:
        items = []
        for k in ch["regles"]:
            lib, titre, lien = _lib_regle(k, lang)
            puce = (f'<a class="regle" href="{lien}">{_e(lib)}</a>' if lien else f'<span class="regle">{_e(lib)}</span>')
            items.append(f'<li>{puce}<b>{_e(titre)}</b> — {_txt(t["regles_texte"][k])}</li>')
        regles = f'<div class="regles"><h3>{_e(t["regles"])}</h3><ul>{"".join(items)}</ul></div>'
    schemas = _schemas(ch["schemas"], lang) if ch["schemas"] else ""
    exo = (f'<div class="exo"><h3>{_e(t["exo"])}</h3><p>{_txt(c["q"])}</p>'
           f'<details><summary>{_e(t["corr"])}</summary><p>{_txt(c["a"])}</p></details></div>')
    return (f'<section class="chap" id="ch{n}-{lang}"><h2><span class="no">{n}</span>{_e(_brut(c["t"]))}</h2>'
            f'{corps}{regles}{schemas}{exo}'
            f'<p><a class="haut-lien" href="#sommaire-{lang}">{_e(t["haut"])}</a></p></section>')


def _langue(lang: str) -> str:
    t = TEXTES[lang]
    n = len(CHAPITRES)
    cache = "" if lang == "fr" else " hidden"
    lien = f'<a href="{URL_RRS}" rel="noopener">sailing.org</a>'
    lis = "".join(f'<li><a href="#ch{i}-{lang}">{_e(_brut(t["ch"][c["id"]]["t"]))}</a></li>' for i, c in enumerate(CHAPITRES, 1))
    lis += f'<li><a href="#revision-{lang}">{_e(t["rev"])}</a></li>'
    chapitres = "\n".join(_chapitre(i, c, lang) for i, c in enumerate(CHAPITRES, 1))
    rev = "".join(f"<p><b>{i}.</b> {_txt(q)}</p><details><summary>{_e(t['corr'])}</summary><p>{_txt(a)}</p></details>"
                  for i, (q, a) in enumerate(t["revision"], 1))
    return (f'<div data-l="{lang}"{cache}>\n<h1>{_e(t["h1"])}</h1>\n<p class="intro">{_e(t["intro"].replace("{n}", str(n)))}</p>\n'
            f'<nav class="sommaire" id="sommaire-{lang}" aria-label="{_e(t["sommaire"].replace("{n}", str(n)))}">'
            f'<h2>{_e(t["sommaire"].replace("{n}", str(n)))}</h2><ol>{lis}</ol></nav>\n{chapitres}\n'
            f'<section class="chap" id="revision-{lang}"><h2>{_e(t["rev"])}</h2><p class="rev-intro">{_e(t["rev_intro"])}</p>{rev}'
            f'<p><a class="haut-lien" href="#sommaire-{lang}">{_e(t["haut"])}</a></p></section>\n'
            f'<p class="note">{_e(t["note"]).replace("{lien}", lien)}</p>\n</div>')


def _ld_cours(desc: str) -> str:
    """JSON-LD : fil d'Ariane + Course (nom, description, fournisseur). Ni prix, ni note."""
    import jsonld
    cours = {"@type": "Course", "name": TEXTES["fr"]["titre"], "description": desc, "inLanguage": "fr",
             "url": f"{jsonld.SITE}/cours.html", "provider": {"@id": jsonld.ORG_ID}}
    return jsonld.bloc(jsonld.fil("cours.html", TEXTES["fr"]["titre"]), cours, jsonld.organisation())


def page_cours() -> str:
    import regles_page
    import site_blocks  # la barre du site et le menu : un seul endroit
    verifier()
    corps = "\n\n".join(_langue(l) for l in LANGUES)
    n = len(CHAPITRES)
    desc = TEXTES["fr"]["desc"].replace("{n}", str(n))
    return (f'<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{TEXTES["fr"]["titre"]} — Sailing More</title>'
            f'<link rel="canonical" href="https://sailingmore.fr/cours.html">'
            f'{_ld_cours(desc)}'
            f'<meta name="description" content="{_html.escape(desc)}">'
            f'<style>{site_blocks.ENTETE_CSS}{CSS}{_css_schemas()}</style></head><body>\n'
            f'{site_blocks.entete_site("cours.html", LANGUES)}{regles_page.SPRITE}\n<div class="page">\n{corps}\n</div>\n'
            f'<script>{JS}</script>\n</body></html>\n')


def ecrire_page(dossier: Path = SITE) -> str:
    """Écrit `cours.html` dans `dossier` — appelé par `accueil_site.sortir_le_site`."""
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "cours.html").write_text(page_cours(), encoding="utf-8")
    return "cours.html"


def main() -> int:
    if "--ecrire" not in sys.argv:
        print(__doc__)
        return 0
    ecrire_page(SITE)
    print(f"{SITE / 'cours.html'} · {len(CHAPITRES)} chapitres · {len(LANGUES)} langues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
