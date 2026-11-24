#!/usr/bin/env python3
"""Les pavillons du Code international de signaux, dans les cours.

Nicolas, 24/11/2026 : « quand tu parles d'un pavillon il faut qu'il soit affiché », « des pages pour
chaque pavillon », « un chapitre pour les pavillons, un autre pour la régate », « un cours sur
l'alphabet marin », « un cours sur la VHF ».

Une seule source de données : `scripts/pavillons.json` (42 pavillons : 26 lettres, 10 chiffres,
3 substituts, le fanion de réponse, le noir et le rouge). Les images sont des SVG du domaine public
(Wikimedia Commons) posés dans `site/pavillons/<id>.svg` — 12 Ko pour les 42.

Ce module ne dessine rien lui-même : il pose du HTML à partir de cette source, et il génère une page
par pavillon (`pavillon-<id>.html`). `cours_page.py` l'appelle pour trois chapitres (pavillons,
signaux de course, VHF) et pour la notation `{pav:<id>}` dans les textes du cours.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

_SOURCE = Path(__file__).resolve().parent
# Rang du chapitre des pavillons dans le cours, posé par `cours_page` (le sommaire s'en sert).
CHAPITRE_PAVILLONS = 13
_donnees: dict | None = None


def donnees() -> dict:
    """Les 42 pavillons et les signaux de course, lus une seule fois."""
    global _donnees
    if _donnees is None:
        for p in (_SOURCE / "pavillons.json", Path("/opt/data/scripts/pavillons.json")):
            if p.exists():
                _donnees = json.loads(p.read_text(encoding="utf-8"))
                break
        else:
            raise FileNotFoundError("pavillons.json introuvable")
    return _donnees


def _par_id() -> dict:
    return {p["id"]: p for p in donnees()["pavillons"]}


def _e(s: str) -> str:
    return _html.escape(s, quote=False)


def _langue(texte: dict, lang: str) -> str:
    """Un champ bilingue de la source : la langue demandée, l'anglais à défaut."""
    if isinstance(texte, str):
        return texte
    return texte.get(lang) or texte.get("en") or texte.get("fr") or ""


# ── Le rendu d'un pavillon dans une phrase ────────────────────────────────────────────────────────────
_IDS = ("reponse", "substitut-1", "substitut-2", "substitut-3", "noir", "rouge")
_NOMS = ("Alfa", "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India",
         "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra",
         "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Xray", "Yankee", "Zulu")
_OTAN = {"Alfa": "a", "Alpha": "a", "X-ray": "x", "Xray": "x"}
for _i, _n in enumerate(["Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India",
                         "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec",
                         "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "Yankee", "Zulu"]):
    _OTAN[_n] = "bcdefghijklmnopqrstuvwyz"[_i]
_OTAN.update({"Noir": "noir", "noire": "noir", "Rouge": "rouge", "Réponse": "reponse", "Reponse": "reponse",
              "Premier Substitut": "substitut-1", "Deuxième Substitut": "substitut-2",
              "Troisième Substitut": "substitut-3"})
_NOMS_AUTO = "|".join(sorted(set(k for k in _OTAN if len(k) > 1) | set(_NOMS), key=len, reverse=True))

_AUTO = re.compile(rf"\b([Pp])avillons? (?:hisse[zr]? )?({_NOMS_AUTO}|[A-Z])\b")
_SANS_PAV = re.compile(r"\b(Premier|Deuxième|Troisième) Substitut\b")
_TOKEN = re.compile(r"\{pav:([a-z0-9-]+)(?:\|([^}]+))?\}")


def _id_auto(mot: str) -> str | None:
    if mot in _OTAN:
        return _OTAN[mot]
    if len(mot) == 1 and mot.isupper():
        return mot.lower()
    return None


def nom_affiche(p: dict) -> str:
    """« Pavillon Papa », mais « Pavillon noir » ne devient pas « Pavillon Pavillon noir »."""
    return p["otan"] if p["otan"].lower().startswith("pavillon") else f"Pavillon {p['otan']}"


def _img(pid: str, classe: str = "pav-inline") -> str:
    p = _par_id().get(pid)
    if not p:
        return ""
    nom = nom_affiche(p)
    return (f'<img class="{classe}" src="pavillons/{pid}.svg" width="40" height="27" '
            f'alt="{_e(nom)}" title="{_e(nom)}" loading="lazy">')


def _lien(pid: str, texte: str | None = None) -> str:
    p = _par_id().get(pid)
    if not p:
        return _e(texte or "")
    nom = nom_affiche(p)
    libelle = _e(texte) if texte else _e(p["code"])
    return (f'<a class="pav-mot" href="pavillon-{pid}.html" title="{_e(nom)}">'
            f'{_img(pid)}{libelle}</a>')


def baliser(texte: str) -> str:
    """Pose la notation `{pav:<id>}` et repère « pavillon X » dans un texte du cours.

    Appelée avant l'échappement HTML : elle ne pose que des marqueurs `{pav:…}` que `_txt` rend ensuite.
    """
    def _auto(m: re.Match) -> str:
        pid = _id_auto(m.group(2))
        if not pid:
            return m.group(0)
        # Le mot « pavillon » reste dans la phrase : seule la lettre devient l'image cliquable.
        prefixe = m.group(0)[: m.start(2) - m.start(0)]
        return f"{prefixe}{{pav:{pid}|{m.group(2)}}}"

    def _substitut(m: re.Match) -> str:
        pid = {"Premier": "substitut-1", "Deuxième": "substitut-2", "Troisième": "substitut-3"}[m.group(1)]
        return f"{{pav:{pid}|{m.group(0)}}}"

    texte = _SANS_PAV.sub(_substitut, texte)
    return _AUTO.sub(_auto, texte)


def rendre(texte: str) -> str:
    """Rend les marqueurs `{pav:…}` déjà échappés en images cliquables."""
    return _TOKEN.sub(lambda m: _lien(m.group(1), m.group(2)), texte)


def poser_textes(textes: dict) -> None:
    """Ajoute les trois chapitres (pavillons, signaux de course, VHF) à chaque langue du cours."""
    for lang, t in textes.items():
        for cid, bloc in CHAPITRES_TEXTE.items():
            if lang in bloc["langues"]:
                t["ch"][cid] = bloc["texte"][lang]


# ── Ce que chaque chapitre ajoute au corps ───────────────────────────────────────────────────────────
def bloc(chapitre: str, lang: str) -> str:
    if chapitre == "pavillons":
        return _grille(lang)
    if chapitre == "signaux_course":
        return _signaux(lang)
    if chapitre == "vhf":
        return _canaux(lang)
    return ""


def _grille(lang: str) -> str:
    groupes = [("Lettres", "lettre"), ("Chiffres", "chiffre"), ("Pavillons spéciaux", "special"),
               ("Substituts", "substitut")]
    en = lang != "fr"
    morceaux = []
    for titre, typ in groupes:
        items = [p for p in donnees()["pavillons"] if p["type"] == typ]
        if not items:
            continue
        cartes = "".join(
            f'<a class="pav-carte" href="pavillon-{p["id"]}.html">'
            f'{_img(p["id"], "pav-img")}'
            f'<b>{_e(p["code"])}</b><span>{_e(p["otan"])}</span></a>' for p in items)
        morceaux.append(f'<div class="pav-groupe"><h3>{titre if not en else _GR["en"][typ]}</h3>'
                        f'<div class="pav-grille">{cartes}</div></div>')
    return f'<div class="pav-grille-tout">{"".join(morceaux)}</div>'


_GR = {"en": {"lettre": "Letters", "chiffre": "Numerals", "special": "Special flags",
              "substitut": "Substitutes"}}


def _signaux(lang: str) -> str:
    lignes = []
    for s in donnees()["course"]:
        num = s["regle"]
        lignes.append(
            f'<li>{_img(s["pavillon"])}<span><b>{_e(nom_affiche(_par_id()[s["pavillon"]]))}</b> — '
            f'{_e(s.get(lang) or s["en"])} '
            f'<a class="regle" href="regles-de-course.html#r{num}">RRS {num}</a></span></li>')
    return f'<div class="pav-signaux"><ul>{"".join(lignes)}</ul></div>'


_CANAUX = [
    ("16", "Veille, détresse et appel", "Watch, distress and calling"),
    ("06", "Course et communications entre bateaux", "Racing and ship-to-ship"),
    ("09", "Ports de plaisance et marinas", "Marinas and harbours"),
    ("10", "Écluses et ponts", "Locks and bridges"),
    ("13", "Sécurité de la navigation (pont à pont)", "Navigation safety, bridge to bridge"),
    ("72", "Plaisance, course au large", "Leisure craft, offshore racing"),
    ("77", "Navires de commerce", "Commercial shipping"),
    ("70", "Appel sélectif numérique (ASN) — jamais de voix", "Digital selective calling — no voice"),
    ("31", "Clubs et stations de plaisance", "Yacht clubs and marinas"),
    ("M, M2", "Méditerranée intérieure (Belgique, Pays-Bas)", "Inland waters (Belgium, Netherlands)"),
]


def _canaux(lang: str) -> str:
    i = 1 if lang == "fr" else 2
    lignes = "".join(f'<tr><td class="canal">{_e(c[0])}</td><td>{_e(c[i])}</td></tr>' for c in _CANAUX)
    return (f'<div class="vhf-canaux"><table><thead><tr><th>Canal</th>'
            f'<th>{"Usage" if lang == "fr" else "Use"}</th></tr></thead><tbody>{lignes}</tbody></table></div>')


# ── Les textes des trois chapitres ───────────────────────────────────────────────────────────────────
CHAPITRES_TEXTE: dict[str, dict] = {}


def _poser(cid: str, langues: tuple, texte: dict) -> None:
    CHAPITRES_TEXTE[cid] = {"langues": langues, "texte": texte}


_poser("pavillons", ("fr", "en", "it", "es", "pt", "de"), {
    "fr": {"t": "Les pavillons et l'alphabet marin",
           "p": ["Chaque lettre a un pavillon et un nom : Alfa, Bravo, Charlie… C'est l'alphabet "
                 "phonétique de l'OTAN, celui qu'on prononce à la VHF pour épeler un nom de bateau, un "
                 "mot de passe ou un code de course.",
                 "Les mêmes pavillons forment le Code international de signaux : un pavillon seul a un "
                 "sens — le pavillon A dit « j'ai un plongeur en plongée » —, deux ou trois forment un "
                 "groupe, et les chiffres précisent une date, une heure, une latitude, une longitude. Le "
                 "fanion de réponse tient lieu de virgule décimale.",
                 "Les 42 pavillons sont ci-dessous, chacun avec sa page : sa forme, ses couleurs, son "
                 "sens dans le code, ce qu'il vaut en course. Une image s'affiche à chaque fois qu'un "
                 "pavillon est nommé dans ce cours."],
           "q": "Quel pavillon hissez-vous pour signaler qu'un plongeur est sous l'eau, et que dit un "
                "pavillon N hissé seul ?",
           "a": "Le pavillon A (Alfa, blanc et bleu, guidon fourchu). Le pavillon N seul dit « Non » "
                "(négatif)."},
    "en": {"t": "Flags and the marine alphabet",
           "p": ["Every letter has a flag and a name: Alfa, Bravo, Charlie… That is the NATO phonetic "
                 "alphabet, the one you speak on the VHF to spell a boat's name or a race code.",
                 "The same flags make up the International Code of Signals: a single flag has a meaning "
                 "— flag A means 'I have a diver down' — two or three make a group, and numerals give a "
                 "date, a time, a latitude, a longitude. The answering pennant stands for the decimal "
                 "point.",
                 "All 42 flags are below, each with its own page: shape, colours, meaning in the code, "
                 "and what it means in racing. A flag shows whenever one is named in this course."],
           "q": "Which flag do you hoist to show a diver is down, and what does a single flag N mean?",
           "a": "Flag A (Alfa, white and blue, swallowtailed). Flag N alone means 'No' (negative)."},
    "it": {"t": "Le bandiere e l'alfabeto marino",
           "p": ["Ogni lettera ha una bandiera e un nome: Alfa, Bravo, Charlie… È l'alfabeto fonetico "
                 "NATO, quello che si pronuncia in VHF per compitare il nome di una barca.",
                 "Le stesse bandiere formano il Codice internazionale dei segnali: una bandiera sola ha "
                 "un significato — la A dice «ho un palombaro in immersione» —, due o tre formano un "
                 "gruppo, e le cifre danno data, ora, latitudine, longitudine.",
                 "Tutte le 42 bandiere sono qui sotto, ognuna con la sua pagina: forma, colori, "
                 "significato nel codice e in regata."],
           "q": "Quale bandiera si issa per segnalare un palombaro in immersione, e cosa dice una "
                "bandiera N issata da sola?",
           "a": "La bandiera A (Alfa, bianca e blu, a coda di rondine). La N da sola dice «No»."},
    "es": {"t": "Las banderas y el alfabeto marino",
           "p": ["Cada letra tiene una bandera y un nombre: Alfa, Bravo, Charlie… Es el alfabeto "
                 "fonético de la OTAN, el que se pronuncia en la VHF para deletrear el nombre de un "
                 "barco.",
                 "Las mismas banderas forman el Código Internacional de Señales: una bandera sola tiene "
                 "un significado — la A dice «tengo un buceador sumergido» —, dos o tres forman un "
                 "grupo, y las cifras dan fecha, hora, latitud y longitud.",
                 "Las 42 banderas están abajo, cada una con su página: forma, colores, significado en el "
                 "código y en regata."],
           "q": "¿Qué bandera se iza para avisar de un buceador sumergido, y qué dice una bandera N "
                "izada sola?",
           "a": "La bandera A (Alfa, blanca y azul, de gallardete ahorquillado). La N sola dice «No»."},
    "pt": {"t": "As bandeiras e o alfabeto marítimo",
           "p": ["Cada letra tem uma bandeira e um nome: Alfa, Bravo, Charlie… É o alfabeto fonético da "
                 "OTAN, aquele que se pronuncia no VHF para soletrar o nome de um barco.",
                 "As mesmas bandeiras formam o Código Internacional de Sinais: uma bandeira só tem um "
                 "significado — a A diz «tenho um mergulhador na água» —, duas ou três formam um grupo, "
                 "e os algarismos dão data, hora, latitude e longitude.",
                 "As 42 bandeiras estão abaixo, cada uma com a sua página: forma, cores, significado no "
                 "código e em regata."],
           "q": "Que bandeira se ice para avisar de um mergulhador na água, e o que diz uma bandeira N "
                "içada sozinha?",
           "a": "A bandeira A (Alfa, branca e azul, de galhardete fendido). A N sozinha diz «Não»."},
    "de": {"t": "Die Flaggen und das marine Alphabet",
           "p": ["Jeder Buchstabe hat eine Flagge und einen Namen: Alfa, Bravo, Charlie… Das ist das "
                 "NATO-Alphabet, mit dem man über UKW einen Bootsnamen buchstabiert.",
                 "Dieselben Flaggen bilden den Internationalen Signalkodex: eine einzelne Flagge hat "
                 "eine Bedeutung — A heißt «Ich habe einen Taucher im Wasser» —, zwei oder drei bilden "
                 "eine Gruppe, und Ziffern geben Datum, Uhrzeit, Breite und Länge an.",
                 "Alle 42 Flaggen stehen unten, jede mit ihrer Seite: Form, Farben, Bedeutung im Kodex "
                 "und im Regattasport."],
           "q": "Welche Flagge setzt man für einen Taucher im Wasser, und was bedeutet eine einzelne "
                "Flagge N?",
           "a": "Flagge A (Alfa, weiß und blau, geschwalbt). Flagge N allein heißt «Nein»."},
})

_poser("signaux_course", ("fr", "en", "it", "es", "pt", "de"), {
    "fr": {"t": "Les pavillons de course",
           "p": ["Sur l'eau, le comité de course parle par pavillons. La séquence de départ est une "
                 "horloge : l'avertissement, le préparatoire quatre minutes plus tard, le retrait une "
                 "minute avant le départ, le départ.",
                 "Le préparatoire est le pavillon P ; à sa place, I, Z, U ou le noir durcissent la "
                 "règle du départ. En course, {pav:x|X} rappelle un bateau parti trop tôt, le {pav:substitut-1|premier substitut} "
                 "rappelle toute la flotte, {pav:n|N} annule, {pav:s|S} réduit le parcours, {pav:c|C} annonce "
                 "un changement de bord, {pav:m|M} remplace une marque manquante. {pav:y|Y} impose le gilet, "
                 "{pav:v|V} demande d'écouter la VHF pour un sauvetage, le {pav:rouge|rouge} signale une "
                 "réclamation.",
                 "Chaque signal renvoie à la règle qui le décrit : c'est elle qui fait foi, pas le "
                 "dessin."],
           "q": "Le comité hisse le pavillon X avec un coup de corne juste après le signal de départ. "
                "Que faites-vous ?",
           "a": "Rappel individuel : je repasse du côté avant-départ en passant par un prolongement de "
                "la ligne, puis je repars. Si je ne le fais pas, je suis classé OCS."},
    "en": {"t": "Racing flags",
           "p": ["On the water the race committee speaks with flags. The starting sequence is a clock: "
                 "warning, preparatory four minutes later, removal one minute before the start, start.",
                 "The preparatory flag is P; I, Z, U or the black flag may replace it and make the start "
                 "harder. In a race, X recalls one boat, the first substitute recalls the fleet, N "
                 "abandons, S shortens the course, C announces a change of leg, M replaces a missing "
                 "mark. Y requires life jackets, V asks you to listen on the VHF for a rescue, the red "
                 "flag signals a protest.",
                 "Every signal links to the rule that describes it: the rule prevails, not the drawing."],
           "q": "The committee hoists flag X with one sound just after the start. What do you do?",
           "a": "Individual recall: return to the pre-start side through an extension of the line, then "
                "start again. Otherwise you are scored OCS."},
    "it": {"t": "Le bandiere di regata",
           "p": ["In acqua il comitato di regata parla con le bandiere. La sequenza di partenza è un "
                 "orologio: avviso, preparatorio quattro minuti dopo, ammainata un minuto prima della "
                 "partenza, partenza.",
                 "Il preparatorio è la bandiera P; al suo posto I, Z, U o la nera rendono la partenza "
                 "più severa. In regata X richiama una barca, il primo sostituto richiama tutta la "
                 "flotta, N annulla, S riduce il percorso, C annuncia un cambio di lato, M sostituisce "
                 "una boa mancante. Y impone il giubbotto, V chiede di ascoltare il VHF, la rossa "
                 "segnala una protesta.",
                 "Ogni segnale rimanda alla regola che lo descrive: vale la regola, non il disegno."],
           "q": "Il comitato issa la bandiera X con un suono subito dopo la partenza. Cosa fate?",
           "a": "Richiamo individuale: torno dal lato pre-partenza passando per un prolungamento della "
                "linea e riparto. Altrimenti sono classificato OCS."},
    "es": {"t": "Las banderas de regata",
           "p": ["En el agua el comité de regatas habla con banderas. La secuencia de salida es un "
                 "reloj: aviso, preparatoria cuatro minutos después, arriado un minuto antes de la "
                 "salida, salida.",
                 "La preparatoria es la bandera P; en su lugar, I, Z, U o la negra endurecen la regla "
                 "de salida. En regata X llama a un barco, el primer sustituto llama a toda la flota, N "
                 "anula, S acorta el recorrido, C anuncia un cambio de bordo, M sustituye una baliza "
                 "perdida. Y impone el chaleco, V pide escuchar la VHF, la roja señala una protesta.",
                 "Cada señal remite a la regla que la describe: manda la regla, no el dibujo."],
           "q": "El comité iza la bandera X con una señal acústica justo después de la salida. ¿Qué "
                "hace?",
           "a": "Llamada individual: vuelvo al lado de pre-salida pasando por una prolongación de la "
                "línea y vuelvo a salir. Si no, quedo clasificado OCS."},
    "pt": {"t": "As bandeiras de regata",
           "p": ["Na água o comité de regatas fala com bandeiras. A sequência de partida é um relógio: "
                 "aviso, preparatória quatro minutos depois, arriada um minuto antes da partida, "
                 "partida.",
                 "A preparatória é a bandeira P; no seu lugar, I, Z, U ou a preta endurecem a regra de "
                 "partida. Em regata X chama um barco, o primeiro substituto chama toda a frota, N "
                 "anula, S reduz o percurso, C anuncia uma mudança de bordo, M substitui uma marca "
                 "em falta. Y impõe o colete, V pede para ouvir o VHF, a vermelha assinala um protesto.",
                 "Cada sinal remete para a regra que o descreve: vale a regra, não o desenho."],
           "q": "O comité ice a bandeira X com um sinal sonoro logo após a partida. O que faz?",
           "a": "Chamada individual: volto ao lado de pré-partida passando por um prolongamento da "
                "linha e parto de novo. Se não o fizer, fico classificado OCS."},
    "de": {"t": "Regattaflaggen",
           "p": ["Auf dem Wasser spricht die Wettfahrtleitung mit Flaggen. Die Startsequenz ist eine "
                 "Uhr: Ankündigung, vier Minuten später die Vorbereitungsflagge, eine Minute vor dem "
                 "Start deren Niederholen, dann der Start.",
                 "Die Vorbereitungsflagge ist P; an ihrer Stelle verschärfen I, Z, U oder die schwarze "
                 "Flagge den Start. Im Rennen ruft X ein Boot zurück, der erste Ersatz die ganze "
                 "Flotte, N bricht ab, S verkürzt den Kurs, C kündigt einen Schenkelwechsel an, M "
                 "ersetzt eine fehlende Tonne. Y verlangt Rettungswesten, V heißt UKW für eine Rettung "
                 "abhören, die rote Flagge zeigt einen Protest an.",
                 "Jedes Signal verweist auf die Regel, die es beschreibt: die Regel gilt, nicht das "
                 "Bild."],
           "q": "Die Leitung setzt direkt nach dem Start Flagge X mit einem Schallsignal. Was tun Sie?",
           "a": "Einzelrückruf: über eine Verlängerung der Linie auf die Vorstartseite zurück und neu "
                "starten. Sonst werde ich als OCS gewertet."},
})

_poser("vhf", ("fr", "en", "it", "es", "pt", "de"), {
    "fr": {"t": "La VHF : usage et canaux",
           "p": ["La VHF porte à vue : quelques milles, une vingtaine avec une bonne antenne en haut du "
                 "mât. Le canal 16 est le canal de veille, de détresse et d'appel. On y reste à "
                 "l'écoute, et on passe sur un canal de travail dès que l'appel est établi.",
                 "Un appel de détresse commence par « Mayday » trois fois, puis le nom du bateau et sa "
                 "position. Un danger grave sans danger vital, c'est « Pan pan » ; un avis de sécurité "
                 "(objet à la mer, essai radio), « Sécurité ». On ne parle jamais sur le canal 70 : il "
                 "est réservé à l'appel sélectif numérique.",
                 "Les canaux ont chacun leur usage, ci-dessous. Sur un bateau, la VHF fixe demande un "
                 "certificat restreint de radiotéléphoniste ; la veille sur le 16 ne se coupe pas quand "
                 "on double le canal de travail. On ne bavarde pas : la VHF n'est pas un téléphone, et "
                 "d'autres peuvent avoir besoin du 16."],
           "q": "Un bateau chavire à cinquante mètres et deux personnes sont à l'eau. Quel message, sur "
                "quel canal, et dans quel ordre ?",
           "a": "« Mayday, Mayday, Mayday », nom du bateau et de celui qui appelle, position, deux "
                "personnes à la mer, assistance immédiate requise — sur le canal 16. Puis suivre les "
                "instructions de la station de sauvetage."},
    "en": {"t": "VHF: use and channels",
           "p": ["VHF is line of sight: a few miles, twenty or so with a good aerial at the masthead. "
                 "Channel 16 is the watch, distress and calling channel. Stay listening there, and move "
                 "to a working channel once the call is established.",
                 "A distress call starts with 'Mayday' three times, then the boat's name and position. "
                 "Serious danger without danger to life is 'Pan pan'; a safety notice is 'Sécurité'. "
                 "Never speak on channel 70: it is reserved for digital selective calling.",
                 "Each channel has its use, below. On board, a fixed VHF requires a restricted "
                 "radiotelephone certificate; the watch on 16 keeps running while you talk on a working "
                 "channel. Do not chat: the VHF is not a telephone, and others may need 16."],
           "q": "A boat capsizes fifty metres away and two people are in the water. What message, on "
                "which channel, in what order?",
           "a": "'Mayday, Mayday, Mayday', name of the boat and of the caller, position, two people in "
                "the water, immediate assistance required — on channel 16. Then follow the rescue "
                "station's instructions."},
    "it": {"t": "Il VHF: uso e canali",
           "p": ["Il VHF va a vista: pochi miglia, una ventina con una buona antenna in testa d'albero. "
                 "Il canale 16 è il canale di ascolto, di soccorso e di chiamata; si passa a un canale "
                 "di lavoro appena la chiamata è stabilita.",
                 "Una chiamata di soccorso inizia con «Mayday» tre volte, poi il nome della barca e la "
                 "posizione. Un pericolo grave senza pericolo per la vita è «Pan pan»; un avviso di "
                 "sicurezza è «Sécurité». Sul canale 70 non si parla mai: è riservato al DSC.",
                 "Ogni canale ha il suo uso, qui sotto. A bordo il VHF fisso richiede il certificato "
                 "ristretto di radiotelefonista; l'ascolto sul 16 resta anche mentre si parla su un "
                 "canale di lavoro."],
           "q": "Una barca si capovolge a cinquanta metri e due persone sono in acqua. Quale messaggio, "
                "su quale canale, in che ordine?",
           "a": "«Mayday, Mayday, Mayday», nome della barca e di chi chiama, posizione, due persone in "
                "acqua, soccorso immediato — sul canale 16. Poi seguire le istruzioni della stazione di "
                "soccorso."},
    "es": {"t": "La VHF: uso y canales",
           "p": ["La VHF va a vista: pocas millas, una veintena con una buena antena en el palo. El "
                 "canal 16 es el de escucha, socorro y llamada; se pasa a un canal de trabajo en cuanto "
                 "la llamada queda establecida.",
                 "Una llamada de socorro empieza por «Mayday» tres veces, luego el nombre del barco y "
                 "la posición. Un peligro grave sin peligro para la vida es «Pan pan»; un aviso de "
                 "seguridad es «Sécurité». Por el canal 70 no se habla nunca: está reservado al DSC.",
                 "Cada canal tiene su uso, abajo. A bordo, la VHF fija exige un certificado restringido "
                 "de radiotelefonista; la escucha en el 16 sigue mientras se habla por un canal de "
                 "trabajo."],
           "q": "Un barco vuelca a cincuenta metros y dos personas están en el agua. ¿Qué mensaje, por "
                "qué canal y en qué orden?",
           "a": "«Mayday, Mayday, Mayday», nombre del barco y de quien llama, posición, dos personas en "
                "el agua, auxilio inmediato — por el canal 16. Después, seguir las instrucciones de la "
                "estación de salvamento."},
    "pt": {"t": "O VHF: uso e canais",
           "p": ["O VHF é de linha de vista: poucas milhas, umas vinte com uma boa antena no topo do "
                 "mastro. O canal 16 é o de escuta, socorro e chamada; passa-se a um canal de trabalho "
                 "logo que a chamada esteja estabelecida.",
                 "Uma chamada de socorro começa por «Mayday» três vezes, depois o nome do barco e a "
                 "posição. Um perigo grave sem perigo de vida é «Pan pan»; um aviso de segurança é "
                 "«Sécurité». No canal 70 nunca se fala: está reservado ao DSC.",
                 "Cada canal tem o seu uso, abaixo. A bordo, o VHF fixo exige um certificado restrito "
                 "de radiotelefonista; a escuta no 16 mantém-se enquanto se fala num canal de trabalho."],
           "q": "Um barco emborca a cinquenta metros e duas pessoas estão na água. Que mensagem, em que "
                "canal e por que ordem?",
           "a": "«Mayday, Mayday, Mayday», nome do barco e de quem chama, posição, duas pessoas na "
                "água, socorro imediato — no canal 16. Depois, seguir as instruções da estação de "
                "salvamento."},
    "de": {"t": "UKW: Gebrauch und Kanäle",
           "p": ["UKW reicht auf Sicht: wenige Meilen, mit guter Antenne im Masttopp etwa zwanzig. "
                 "Kanal 16 ist der Wach-, Not- und Anrufkanal; man bleibt dort auf Empfang und wechselt "
                 "auf einen Arbeitskanal, sobald der Anruf steht.",
                 "Ein Notruf beginnt dreimal mit «Mayday», dann Bootsname und Position. Schwere Gefahr "
                 "ohne Lebensgefahr ist «Pan pan»; eine Sicherheitsmeldung «Sécurité». Auf Kanal 70 "
                 "wird nie gesprochen: er ist dem digitalen Selektivruf vorbehalten.",
                 "Jeder Kanal hat seine Aufgabe, siehe unten. An Bord verlangt die feste UKW ein "
                 "beschränktes Funkzeugnis; die Wache auf 16 läuft weiter, während man auf einem "
                 "Arbeitskanal spricht."],
           "q": "Ein Boot kentert fünfzig Meter entfernt, zwei Personen sind im Wasser. Welche Meldung, "
                "auf welchem Kanal, in welcher Reihenfolge?",
           "a": "«Mayday, Mayday, Mayday», Name des Bootes und des Anrufers, Position, zwei Personen im "
                "Wasser, sofortige Hilfe erforderlich — auf Kanal 16. Danach die Anweisungen der "
                "Rettungsstelle befolgen."},
})


# ── Une page par pavillon ────────────────────────────────────────────────────────────────────────────
def _fiche(pid: str) -> str:
    p = _par_id()[pid]
    lignes = [f'<div class="pav-fiche"><img class="pav-grande" src="pavillons/{pid}.svg" width="240" '
              f'height="160" alt="{_e(nom_affiche(p))}">',
              f'<dl><dt>Code</dt><dd>{_e(p["code"])} — {_e(p["otan"])}</dd>',
              f'<dt>Forme</dt><dd>{_e(_langue(p.get("forme", {}), "fr"))}</dd>']
    if p.get("couleurs_en"):
        lignes.append(f'<dt>Dessin (source anglaise)</dt><dd>{_e(p["couleurs_en"])}</dd>')
    lignes.append(f'<dt>Sens dans le code</dt><dd>{_e(_langue(p["ics"], "fr"))}</dd>')
    if _langue(p.get("complement", {}), "fr"):
        lignes.append(f'<dt>Avec des chiffres</dt><dd>{_e(_langue(p["complement"], "fr"))}</dd>')
    if p.get("course"):
        lignes.append(f'<dt>En course</dt><dd>{_e(p["course"]["fr"])} '
                      f'<a class="regle" href="regles-de-course.html#r{p["course"]["regle"]}">'
                      f'RRS {p["course"]["regle"]}</a></dd>')
    lignes.append("</dl></div>")
    return "".join(lignes)


def _nav_pav(pid: str) -> str:
    ids = [p["id"] for p in donnees()["pavillons"]]
    i = ids.index(pid)
    prec = ids[i - 1] if i else None
    suiv = ids[i + 1] if i + 1 < len(ids) else None
    liens = []
    if prec:
        liens.append(f'<a href="pavillon-{prec}.html">← {_e(_par_id()[prec]["otan"])}</a>')
    liens.append(f'<a href="cours.html#ch{CHAPITRE_PAVILLONS}-fr">Tous les pavillons</a>')
    if suiv:
        liens.append(f'<a href="pavillon-{suiv}.html">{_e(_par_id()[suiv]["otan"])} →</a>')
    return f'<p class="pav-nav">{" · ".join(liens)}</p>'


def page_pavillon(pid: str, css: str = "") -> str:
    """La page d'un pavillon : son image, sa forme, son sens, son usage en course."""
    import site_blocks  # la barre du site et le menu : un seul endroit

    p = _par_id()[pid]
    titre = f"{nom_affiche(p)} ({p['code']})"
    desc = (f"Le pavillon {p['otan']} ({p['code']}) du Code international de signaux : forme, couleurs, "
            f"sens et usage en course.")
    texte_en = _langue(p["ics"], "en")
    return (f'<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{_e(titre)} — Sailing More</title>'
            f'<link rel="canonical" href="https://sailingmore.fr/pavillon-{pid}.html">'
            f'<meta name="description" content="{_e(desc)}">'
            # Page de référence courte (moins de 600 mots) : hors index tant que sa fiche n'est pas
            # écrite en entier, pour ne pas mettre 42 pages maigres dans Google.
            f'<meta name="robots" content="noindex,follow">'
            f'<style>{site_blocks.ENTETE_CSS}{css}{CSS}</style></head><body>\n'
            f'{site_blocks.entete_site("cours.html", ["fr"])}<div class="page">\n'
            f'<h1>{_e(titre)}</h1>{_fiche(pid)}'
            f'<p class="pav-en"><b>In English</b> — {_e(texte_en)}</p>'
            f'{_nav_pav(pid)}</div>\n</body></html>\n')


def ecrire_pages(dossier: Path, css: str = "") -> list[str]:
    """Écrit `pavillon-<id>.html` pour les 42 pavillons. Retourne la liste des fichiers."""
    dossier.mkdir(parents=True, exist_ok=True)
    noms = []
    for p in donnees()["pavillons"]:
        nom = f"pavillon-{p['id']}.html"
        (dossier / nom).write_text(page_pavillon(p["id"], css), encoding="utf-8")
        noms.append(nom)
    return noms


CSS = """
.pav-inline{vertical-align:-6px;margin:0 .12em;border:1px solid #c9c9c9;border-radius:2px}
.pav-mot{text-decoration:none;white-space:nowrap}
.pav-mot img{border:1px solid #c9c9c9;border-radius:2px;vertical-align:-6px;margin-right:.25em}
.pav-grille-tout{margin:1.2em 0}
.pav-groupe h3{margin:1.2em 0 .4em;font-size:1em;letter-spacing:.04em;text-transform:uppercase;color:#555}
.pav-grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(84px,1fr));gap:.5em}
.pav-carte{display:flex;flex-direction:column;align-items:center;gap:.15em;padding:.35em .2em;
  border:1px solid #e2e2e2;border-radius:4px;text-decoration:none;color:inherit;background:#fbfbfb}
.pav-carte:hover{border-color:#0a5;background:#f2fbf6}
.pav-carte img{width:100%;height:auto;max-height:56px;object-fit:contain}
.pav-carte b{font-size:.85em;color:#111}
.pav-carte span{font-size:.7em;color:#666;text-align:center;line-height:1.1}
.pav-signaux ul{list-style:none;padding:0;margin:1em 0}
.pav-signaux li{display:flex;gap:.6em;align-items:flex-start;margin:.6em 0}
.pav-signaux img{flex:0 0 40px;border:1px solid #c9c9c9;border-radius:2px}
.vhf-canaux table{border-collapse:collapse;margin:1em 0;font-size:.95em}
.vhf-canaux th,.vhf-canaux td{border-bottom:1px solid #e2e2e2;padding:.35em .8em .35em 0;text-align:left}
.vhf-canaux .canal{font-weight:700;white-space:nowrap}
.pav-fiche{display:flex;flex-wrap:wrap;gap:1.6em;align-items:flex-start;margin:1.2em 0}
.pav-fiche dl{margin:0;flex:1 1 22em;min-width:0;max-width:34em}
.pav-fiche dt{font-size:.75em;text-transform:uppercase;letter-spacing:.05em;color:#666;margin-top:.7em}
.pav-fiche dd{margin:.1em 0 0}
.pav-grande{border:1px solid #c9c9c9;border-radius:3px;max-width:100%;height:auto}
.pav-en{font-size:.9em;color:#444;border-top:1px solid #e2e2e2;padding-top:.8em;margin-top:1.6em}
.pav-nav{margin:1.8em 0;font-size:.95em}
.pav-nav a{color:inherit;opacity:.85}
.pav-nav a:hover{opacity:1}
.pav-fiche dt{font-weight:600}
"""
