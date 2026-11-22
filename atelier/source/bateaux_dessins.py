"""Les dessins de la page des bateaux : formes, pièces, fiches. Première moitié (voiliers à coque).

Repère local : x de 0 à 480, y de 0 à `h` ; l'étrave est à droite. Chaque forme dessinée porte le mot du
lexique (`mot`) de la pièce qu'elle représente : c'est elle qui brille quand la page reçoit `?mot=`.
Une pièce (`A`) donne son ancre — un point SUR la pièce, sur son bord extérieur — et son niveau :
'e' = essentiel (une douzaine), 't' = visible seulement en « tout ».
La mise en page (côté de l'étiquette, trait, numéro de repli) est calculée par bateaux_page.py : ici on
ne place aucune étiquette.

Classes de forme : c coque, s voile, m mât, l trait fort, f gréement fin, e bord de voile, n filet/zone,
r gréeur (silhouette), h harnais, o pièce sombre.
"""
from __future__ import annotations


def P(mot, pts, cls="c"):
    return {"k": "p", "mot": mot, "subs": [pts], "cls": cls}


def L(mot, *subs, cls="f"):
    return {"k": "l", "mot": mot, "subs": [list(s) for s in subs], "cls": cls}


def E(mot, cx, cy, rx, ry, cls="c"):
    return {"k": "e", "mot": mot, "ell": (cx, cy, rx, ry), "cls": cls, "subs": []}


def A(mot, niv, ax, ay, **opts):
    d = {"mot": mot, "niv": niv, "ax": ax, "ay": ay}
    d.update(opts)
    return d


# ───────────────────────────────────────────────────────────────────────────── X35
X35 = {
    "id": "x35", "cat": "habitable", "nom": "Voilier Habitable X35", "h": 520,
    "slug": "voilier-habitable-x35",
    "ins": (62, 378, 15), "vs": (218, 306),
    "eau": 396,
    "shapes": [
        P("coque", [(50, 350), (250, 362), (352, 349), (455, 336), (451, 358), (430, 392), (392, 410), (330, 418),
                    (250, 420), (160, 416), (95, 404), (60, 388), (50, 362)]),
        P("quille", [(238, 418), (298, 418), (286, 492), (260, 492)], "c"),
        E("lest", 273, 500, 40, 11, "c"),
        P("safran", [(88, 408), (106, 408), (103, 462), (90, 466)], "c"),
        P("cockpit", [(66, 344), (160, 344), (160, 352), (66, 352)], "c"),
        P(None, [(150, 360), (185, 336), (325, 332), (352, 350), (352, 360)], "c"),
        P("capot", [(262, 326), (300, 326), (300, 333), (262, 333)], "o"),
        E("hublot", 214, 349, 11, 4, "o"), E("hublot", 252, 349, 11, 4, "o"),
        P("dorade", [(188, 332), (204, 332), (204, 322), (188, 322)], "o"),
        P("mat", [(229, 336), (235, 336), (235, 42), (229, 42)], "m"),
        P("grand-voile", [(236, 62), (196, 134), (158, 200), (122, 262), (94, 314), (236, 320)], "s"),
        L("latte", [(196, 134), (233, 141)], [(158, 200), (233, 208)], [(122, 262), (233, 270)], cls="f"),
        L("guindant", [(239, 66), (239, 316)], cls="e"),
        L("chute", [(236, 62), (196, 134), (158, 200), (122, 262), (94, 314)], cls="e"),
        L("bordure", [(94, 314), (236, 320)], cls="e"),
        L("bome", [(233, 325), (92, 318)], cls="l"),
        L("hale-bas", [(233, 334), (170, 319)], cls="f"),
        L("ecoute", [(130, 318), (132, 344)], cls="f"),
        P("foc", [(252, 111), (471, 323), (302, 318), (272, 214)], "s"),
        L("etai", [(232, 92), (478, 330)], cls="f"),
        L("hauban", [(232, 100), (268, 354)], cls="f"),
        L("barre-de-fleche", [(222, 168), (246, 160)], cls="l"),
        L("pataras", [(232, 44), (64, 350)], cls="f"),
        L("bastaque", [(232, 70), (150, 344)], cls="f"),
        L("bout-dehors", [(446, 340), (478, 330)], cls="l"),
        L("sous-barbe", [(478, 331), (436, 394)], cls="f"),
        P("guindeau", [(366, 339), (384, 339), (384, 346), (366, 346)], "o"),
        P("chaumard", [(66, 345), (78, 345), (78, 352), (66, 352)], "o"),
        L("balcon-avant", [(446, 336), (442, 311), (412, 314), (410, 338)], cls="f"),
        P("taquet", [(330, 340), (344, 340), (344, 346), (330, 346)], "o"),
        E("winch", 148, 340, 8, 5, "o"),
        L("barre", [(97, 352), (150, 334)], cls="l"),
        L("etrave", [(455, 336), (451, 358), (430, 392)], cls="e"),
        L("etambot", [(50, 350), (50, 362), (60, 388)], cls="e"),
        L("pont", [(50, 350), (250, 362), (352, 349), (455, 336)], cls="e"),
    ],
    "parts": [
        A("mat", "e", 232, 46), A("grand-voile", "e", 160, 198), A("bome", "e", 100, 318), A("foc", "e", 390, 250, side="r"),
        A("etai", "e", 400, 280, side="r"), A("hauban", "e", 236, 130), A("pataras", "e", 100, 280),
        A("coque", "e", 100, 396, side="l"), A("quille", "e", 282, 470), A("safran", "e", 94, 440, side="l"),
        A("barre", "e", 120, 342, side="l"), A("cockpit", "e", 66, 346, side="l"),
        A("etrave", "t", 454, 342, side="r"), A("etambot", "t", 50, 356, side="l"), A("winch", "t", 148, 335),
        A("taquet", "t", 337, 346), A("balcon-avant", "t", 442, 311, side="r"), A("lest", "t", 304, 505, side="r"),
        A("barre-de-fleche", "t", 222, 168, side="l"), A("hale-bas", "t", 200, 325), A("ecoute", "t", 131, 335),
        A("latte", "t", 158, 200, side="l"), A("guindant", "t", 239, 200), A("chute", "t", 122, 262, side="l"),
        A("bordure", "t", 160, 317), A("bastaque", "t", 150, 344, side="l"), A("bout-dehors", "t", 478, 330, side="r"),
        A("sous-barbe", "t", 450, 365, side="r"), A("guindeau", "t", 375, 339), A("chaumard", "t", 72, 345, side="l"),
        A("dorade", "t", 196, 322), A("capot", "t", 281, 326), A("hublot", "t", 252, 349), A("pont", "t", 300, 355),
    ],
    "alt_mots": ["grand-voile", "bome", "quille", "safran", "barre-de-fleche"],
    "fiche": {"long": "10,6", "crew": "plus",
              "rig": {"fr": "sloop fractionné, grand-voile et foc",
                      "en": "fractional sloop, mainsail and jib", "it": "sloop frazionato, randa e fiocco",
                      "es": "balandro fraccionado, mayor y foque", "pt": "sloop fracionado, vela grande e estai",
                      "de": "Slup mit Fraktionalrigg, Groß und Fock"},
              "serie": {"fr": "dessinée en 2005, lancée en 2006 ; monotype reconnu par World Sailing",
                        "en": "designed in 2005, launched in 2006; one-design recognised by World Sailing",
                        "it": "progettata nel 2005, varata nel 2006; monotipo riconosciuto da World Sailing",
                        "es": "diseñada en 2005, botada en 2006; monotipo reconocido por World Sailing",
                        "pt": "desenhada em 2005, lançada em 2006; monotipo reconhecido pela World Sailing",
                        "de": "2005 entworfen, 2006 vorgestellt; von World Sailing anerkannte Einheitsklasse"}},
    "desc": {"fr": "du voilier habitable X35", "en": "of the X35 cruiser-racer", "it": "della barca X35",
             "es": "del velero X35", "pt": "do veleiro X35", "de": "der Yacht X35"},
}

# ───────────────────────────────────────────────────────────────────────────── Hobie 16
HOBIE = {
    "id": "hobie16", "cat": "multicoque", "nom": "Catamaran Hobie 16 avec spi", "h": 480,
    "slug": "catamaran-hobie-16",
    "ins": (70, 358, 14), "vs": (232, 274),
    "eau": 360,
    "shapes": [
        P("coque", [(56, 308), (166, 314), (316, 312), (406, 298), (460, 270), (456, 280), (446, 310), (411, 338),
                    (346, 352), (236, 356), (136, 352), (76, 342), (56, 325)], "n"),
        P("coque", [(40, 328), (150, 334), (300, 332), (390, 318), (444, 290), (430, 330), (395, 358), (330, 372),
                    (220, 376), (120, 372), (60, 362), (40, 345)]),
        P("trampoline", [(150, 334), (300, 332), (380, 321), (396, 291), (316, 302), (166, 304)], "n"),
        L("traverse", [(330, 332), (346, 302)], [(170, 334), (186, 304)], cls="l"),
        P("mat", [(247, 318), (253, 318), (253, 52), (247, 52)], "m"),
        P("grand-voile", [(253, 66), (205, 128), (160, 190), (124, 242), (100, 276), (253, 282)], "s"),
        L("latte", [(205, 128), (251, 136)], [(160, 190), (251, 200)], [(124, 242), (251, 252)], cls="f"),
        L("guindant", [(256, 70), (256, 278)], cls="e"),
        L("chute", [(253, 66), (205, 128), (160, 190), (124, 242), (100, 276)], cls="e"),
        L("bordure", [(100, 276), (253, 282)], cls="e"),
        L("bome", [(251, 286), (98, 280)], cls="l"),
        L("ecoute", [(104, 281), (110, 326)], cls="f"),
        P("foc", [(285, 84), (434, 278), (330, 292), (300, 190)], "s"),
        L("etai", [(250, 58), (444, 290)], cls="f"),
        P("spinnaker", [(256, 56), (340, 48), (412, 80), (460, 146), (476, 226), (452, 286), (444, 290), (392, 268),
                        (338, 238), (306, 170), (280, 104)], "sn"),
        L("hauban", [(253, 112), (300, 330)], cls="f"),
        L("trapeze", [(253, 118), (290, 178)], cls="l"),
        L("safran", [(56, 330), (50, 372), (64, 396), (74, 380), (70, 340)], cls="l"),
        L("barre-franche", [(58, 322), (100, 312)], cls="l"),
        L("barre-d-accouplement", [(86, 306), (90, 330)], cls="l"),
        P("taquet", [(150, 322), (162, 322), (162, 328), (150, 328)], "o"),
        E("poulie", 120, 322, 6, 6, "o"),
        L("etrave", [(444, 290), (430, 330), (395, 358)], cls="e"),
        L("drisse", [(256, 60), (270, 150), (270, 304)], cls="f"),
    ],
    "parts": [
        A("mat", "e", 250, 40, side="l"), A("grand-voile", "e", 140, 215), A("foc", "e", 410, 262, side="r"),
        A("spinnaker", "e", 476, 226, side="r"), A("bome", "e", 98, 280, side="l"), A("hauban", "e", 272, 200),
        A("etai", "e", 340, 206, side="r"), A("coque", "e", 100, 366, side="l"), A("traverse", "e", 186, 304, side="l"),
        A("trampoline", "e", 166, 304, side="l"), A("safran", "e", 62, 388, side="l"), A("trapeze", "e", 270, 146),
        A("etrave", "t", 440, 304, side="r"), A("barre-franche", "t", 80, 318, side="l"),
        A("barre-d-accouplement", "t", 88, 316, side="l"), A("drisse", "t", 270, 120), A("ecoute", "t", 107, 312, side="l"),
        A("latte", "t", 124, 242, side="l"), A("guindant", "t", 256, 190), A("chute", "t", 160, 190, side="l"),
        A("bordure", "t", 180, 280), A("taquet", "t", 156, 328), A("poulie", "t", 120, 316),
    ],
    "alt_mots": ["grand-voile", "spinnaker", "trampoline", "traverse", "safran"],
    "fiche": {"long": "5,05", "crew": "2",
              "rig": {"fr": "catamaran à trapèzes ; grand-voile, foc, spinnaker en option",
                      "en": "trapeze catamaran; mainsail, jib, optional spinnaker",
                      "it": "catamarano con trapezio; randa, fiocco, spinnaker opzionale",
                      "es": "catamarán con trapecio; mayor, foque, spinnaker opcional",
                      "pt": "catamarã com trapézio; vela grande, estai, spinnaker opcional",
                      "de": "Trapez-Katamaran; Groß, Fock, Spinnaker als Option"},
              "serie": {"fr": "premiers bateaux en 1969 ; le spi est un kit hors jauge de la série",
                        "en": "first boats in 1969; the spinnaker is an optional kit outside the class rules",
                        "it": "primi esemplari nel 1969; lo spinnaker è un kit fuori dalla regola di classe",
                        "es": "primeros barcos en 1969; el spinnaker es un kit fuera del reglamento de la clase",
                        "pt": "primeiros barcos em 1969; o spinnaker é um kit fora das regras da classe",
                        "de": "erste Boote 1969; der Spinnaker ist ein Zusatzkit außerhalb der Klassenregeln"}},
    "desc": {"fr": "du catamaran Hobie 16", "en": "of the Hobie 16 catamaran", "it": "del catamarano Hobie 16",
             "es": "del catamarán Hobie 16", "pt": "do catamarã Hobie 16", "de": "des Katamarans Hobie 16"},
}

# ───────────────────────────────────────────────────────────────────────────── Laser
LASER = {
    "id": "laser", "cat": "deriveur", "nom": "Dériveur Laser", "h": 460,
    "slug": "deriveur-laser",
    "ins": (96, 352, 14), "vs": (264, 276),
    "eau": 372,
    "shapes": [
        P("coque", [(60, 330), (250, 338), (440, 314), (436, 330), (410, 350), (330, 366), (230, 372), (130, 368),
                    (80, 356), (60, 344)]),
        P("derive-mobile", [(258, 368), (296, 368), (300, 436), (262, 440)], "c"),
        P("safran", [(52, 340), (70, 340), (66, 418), (48, 414)], "c"),
        L("barre-franche", [(58, 330), (150, 318)], cls="l"),
        L("rallonge-de-barre", [(150, 318), (205, 300)], cls="l"),
        P("mat", [(272, 332), (278, 332), (278, 58), (272, 58)], "m"),
        P("grand-voile", [(278, 64), (240, 140), (200, 205), (160, 250), (128, 278), (278, 284)], "s"),
        L("latte", [(240, 140), (276, 146)], [(200, 205), (276, 213)], [(160, 250), (276, 258)], cls="f"),
        L("guindant", [(281, 68), (281, 280)], cls="e"),
        L("chute", [(278, 64), (240, 140), (200, 205), (160, 250), (128, 278)], cls="e"),
        L("bordure", [(128, 278), (278, 284)], cls="e"),
        L("bome", [(276, 287), (128, 280)], cls="l"),
        L("hale-bas", [(276, 328), (200, 283)], cls="f"),
        L("cunningham", [(282, 268), (292, 324)], cls="f"),
        L("ecoute", [(130, 282), (136, 334)], cls="f"),
        P("taquet", [(160, 328), (172, 328), (172, 335), (160, 335)], "o"),
        L("sangle-de-rappel", [(150, 336), (160, 326), (215, 328), (226, 337)], cls="l"),
        L("etrave", [(440, 314), (436, 330), (410, 350)], cls="e"),
        L("etambot", [(60, 330), (60, 344)], cls="e"),
        L("pont", [(60, 330), (250, 338), (440, 314)], cls="e"),
    ],
    "parts": [
        A("grand-voile", "e", 170, 235, side="l"), A("mat", "e", 275, 60, side="l"), A("bome", "e", 128, 280, side="l"),
        A("derive-mobile", "e", 299, 420, side="r"), A("safran", "e", 52, 400, side="l"),
        A("barre-franche", "e", 100, 324, side="l"), A("rallonge-de-barre", "e", 205, 300, side="l"),
        A("coque", "e", 150, 366, side="l"),
        A("etrave", "e", 432, 332, side="r"), A("cunningham", "e", 292, 324, side="r"),
        A("hale-bas", "t", 230, 305), A("taquet", "t", 166, 333), A("ecoute", "t", 133, 308, side="l"),
        A("latte", "t", 160, 250, side="l"), A("guindant", "t", 281, 200),
        A("chute", "t", 200, 205, side="l"), A("bordure", "t", 210, 283), A("sangle-de-rappel", "t", 190, 327, side="l"),
        A("etambot", "t", 60, 337, side="l"), A("pont", "t", 350, 326, side="r"),
    ],
    "alt_mots": ["grand-voile", "bome", "derive-mobile", "safran", "barre-franche"],
    "fiche": {"long": "4,2", "crew": "1",
              "rig": {"fr": "une seule voile, sans foc ni spinnaker",
                      "en": "one sail only, no jib and no spinnaker", "it": "una sola vela, senza fiocco né spinnaker",
                      "es": "una sola vela, sin foque ni spinnaker", "pt": "uma só vela, sem estai nem spinnaker",
                      "de": "nur ein Segel, ohne Fock und Spinnaker"},
              "serie": {"fr": "dessiné en 1970 ; voile de 7,06 m² pour le gréement standard (ILCA 7)",
                        "en": "designed in 1970; 7.06 m² sail for the standard rig (ILCA 7)",
                        "it": "progettato nel 1970; vela di 7,06 m² per l'armo standard (ILCA 7)",
                        "es": "diseñado en 1970; vela de 7,06 m² en el aparejo estándar (ILCA 7)",
                        "pt": "desenhado em 1970; vela de 7,06 m² no aparelho padrão (ILCA 7)",
                        "de": "1970 entworfen; 7,06 m² Segel im Standardrigg (ILCA 7)"}},
    "desc": {"fr": "du dériveur Laser", "en": "of the Laser dinghy", "it": "del dinghy Laser",
             "es": "de la deriva Laser", "pt": "do dinghy Laser", "de": "der Jolle Laser"},
}

# ───────────────────────────────────────────────────────────────────────────── 49er
S49 = {
    "id": "49er", "cat": "skiff", "nom": "Skiff 49er", "h": 460,
    "slug": "skiff-49er",
    "ins": (96, 360, 14), "vs": (222, 288),
    "eau": 378,
    "shapes": [
        P("coque", [(40, 336), (240, 344), (440, 326), (446, 336), (420, 358), (330, 372), (220, 376), (110, 372),
                    (60, 360), (40, 350)]),
        P("aile-de-rappel", [(150, 332), (330, 336), (344, 320), (166, 316)], "o"),
        P("derive-mobile", [(236, 372), (270, 372), (274, 436), (240, 440)], "c"),
        P("safran", [(30, 346), (48, 346), (44, 418), (28, 414)], "c"),
        L("barre-franche", [(38, 336), (120, 322)], cls="l"),
        L("rallonge-de-barre", [(120, 322), (176, 304)], cls="l"),
        P("mat", [(232, 334), (238, 334), (238, 46), (232, 46)], "m"),
        P("grand-voile", [(236, 62), (198, 130), (158, 196), (118, 252), (90, 288), (236, 292)], "s"),
        L("latte", [(198, 130), (234, 136)], [(158, 196), (234, 204)], [(118, 252), (234, 260)], cls="f"),
        L("guindant", [(239, 66), (239, 288)], cls="e"),
        L("chute", [(236, 62), (198, 130), (158, 196), (118, 252), (90, 288)], cls="e"),
        L("bordure", [(90, 288), (236, 292)], cls="e"),
        L("bome", [(236, 294), (88, 290)], cls="l"),
        L("ecoute", [(92, 291), (100, 326)], cls="f"),
        P("foc", [(251, 100), (435, 314), (310, 300), (278, 200)], "s"),
        L("etai", [(236, 84), (446, 326)], cls="f"),
        L("hauban", [(236, 100), (262, 322)], cls="f"),
        L("trapeze", [(240, 116), (262, 306)], cls="l"),
        L("bout-dehors", [(440, 328), (478, 304)], cls="l"),
        P("taquet", [(130, 326), (142, 326), (142, 332), (130, 332)], "o"),
        L("etrave", [(446, 336), (440, 326), (420, 358)], cls="e"),
        L("drisse", [(240, 70), (246, 160), (246, 330)], cls="f"),
    ],
    "parts": [
        A("mat", "e", 235, 90, side="l"), A("grand-voile", "e", 150, 210, side="l"), A("foc", "e", 400, 260, side="r"),
        A("bome", "e", 130, 292, side="l"), A("bout-dehors", "e", 478, 304, side="r"), A("trapeze", "e", 262, 306),
        A("aile-de-rappel", "e", 166, 316, side="l"), A("coque", "e", 100, 368, side="l"),
        A("safran", "e", 34, 400, side="l"), A("barre-franche", "e", 70, 330, side="l"),
        A("etrave", "e", 446, 336, side="r"), A("derive-mobile", "e", 272, 420, side="r"),
        A("etai", "t", 340, 214, side="r"), A("hauban", "t", 262, 322), A("drisse", "t", 246, 240),
        A("ecoute", "t", 96, 310, side="l"), A("latte", "t", 118, 252, side="l"), A("guindant", "t", 239, 190),
        A("chute", "t", 158, 196, side="l"), A("bordure", "t", 170, 291), A("rallonge-de-barre", "t", 176, 304, side="l"),
        A("taquet", "t", 136, 330),
    ],
    "alt_mots": ["grand-voile", "foc", "aile-de-rappel", "trapeze", "bout-dehors"],
    "fiche": {"long": "4,99", "crew": "2",
              "rig": {"fr": "skiff à deux trapèzes ; grand-voile, foc et spinnaker asymétrique sur bout-dehors",
                      "en": "two-trapeze skiff; mainsail, jib and asymmetric spinnaker on a bowsprit",
                      "it": "skiff a due trapezi; randa, fiocco e spinnaker asimmetrico su bompresso",
                      "es": "skiff con dos trapecios; mayor, foque y spinnaker asimétrico en bauprés",
                      "pt": "skiff com dois trapézios; vela grande, estai e spinnaker assimétrico em gurupés",
                      "de": "Skiff mit zwei Trapezen; Groß, Fock und asymmetrischer Spinnaker am Bugspriet"},
              "serie": {"fr": "classe olympique depuis les Jeux de Sydney, en 2000",
                        "en": "Olympic class since the Sydney Games in 2000",
                        "it": "classe olimpica dai Giochi di Sydney, nel 2000",
                        "es": "clase olímpica desde los Juegos de Sídney, en 2000",
                        "pt": "classe olímpica desde os Jogos de Sydney, em 2000",
                        "de": "olympische Klasse seit den Spielen von Sydney 2000"}},
    "desc": {"fr": "du skiff 49er", "en": "of the 49er skiff", "it": "dello skiff 49er",
             "es": "del skiff 49er", "pt": "do skiff 49er", "de": "des 49er-Skiffs"},
}

BATEAUX_1 = [X35, HOBIE, LASER, S49]
