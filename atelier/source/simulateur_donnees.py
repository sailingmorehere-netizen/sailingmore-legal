# © 2026 Sailing More — tous droits réservés. All rights reserved.
# Données du simulateur de priorités : 50 scénarios, textes en six langues.
# Convention : vent venant du haut (nord) ; cap 0 = vers le haut, en degrés, sens horaire ;
# x vers la droite, y vers le bas ; bateau long de 8 unités, zone des trois longueurs = rayon 24.
# Bord : cap entre 0 et 180 (exclus) = bâbord amures ; entre 180 et 360 = tribord amures.
import math

LANGS = ["fr", "en", "de", "it", "es", "pt"]


def toward(p, h, d):
    """Point de départ d'un bateau de cap h qui atteint p après la distance d."""
    r = math.radians(h)
    return (round(p[0] - d * math.sin(r), 1), round(p[1] + d * math.cos(r), 1))


def B(i, k, x, y, h, tag=None):
    d = {"id": i, "k": k, "x": x, "y": y, "h": h}
    if tag:
        d["tag"] = tag
    return d


def cross(p, ka, ha, da, kb, hb, db, tagA=None, tagB=None):
    a = toward(p, ha, da)
    b = toward(p, hb, db)
    return [B("A", ka, a[0], a[1], ha, tagA), B("B", kb, b[0], b[1], hb, tagB)]


def perp(x, y, h, d):
    """Point décalé de d vers la droite du cap h (côté tribord)."""
    r = math.radians(h)
    return (round(x + d * math.cos(r), 1), round(y + d * math.sin(r), 1))


def S(id_, fam, rule, reason, boats, ans, ref, **kw):
    s = {"id": id_, "fam": fam, "reason": reason, "boats": boats, "ans": ans, "ref": ref,
         "rule": rule, "wind": kw.pop("wind", True), "night": kw.pop("night", False)}
    s.update(kw)
    return s


SC = []
add = SC.append
# ---- Règles de course (RRS) : 30 -----------------------------------------
add(S(1, "rrs", 10, "r10", cross((50, 45), "s", 315, 34, "s", 45, 34), "B", "10"))
add(S(2, "rrs", 10, "r10", cross((50, 45), "s", 45, 34, "s", 315, 34), "A", "10"))
add(S(3, "rrs", 10, "r10", cross((50, 60), "s", 225, 30, "s", 135, 30), "B", "10"))
add(S(4, "rrs", 10, "r10", [B("A", "s", 20, 50, 90), B("B", "s", 80, 52, 270)], "A", "10"))
add(S(5, "rrs", 10, "r10", cross((55, 50), "s", 60, 30, "s", 280, 30), "A", "10"))
add(S(6, "rrs", 10, "r10", cross((55, 45), "s", 270, 28, "s", 60, 35), "B", "10"))
add(S(7, "rrs", 11, "r11", [B("A", "s", 35, 38, 90), B("B", "s", 38, 49, 90)], "A", "11"))
add(S(8, "rrs", 11, "r11", [B("A", "s", 60, 52, 270), B("B", "s", 57, 41, 270)], "B", "11"))
_a = (45, 38)
_b = perp(_a[0], _a[1], 120, 10)
add(S(9, "rrs", 11, "r11", [B("A", "s", _a[0], _a[1], 120), B("B", "s", _b[0], _b[1], 120)], "A", "11"))
add(S(10, "rrs", 11, "r11", [B("A", "s", 40, 40, 45), B("B", "s", 47, 47, 45)], "A", "11"))
add(S(11, "rrs", 11, "r11", [B("A", "s", 50, 50, 315), B("B", "s", 57, 43, 315)], "B", "11"))
add(S(12, "rrs", 12, "r12", [B("A", "s", 25, 50, 90), B("B", "s", 58, 52, 90)], "A", "12"))
add(S(13, "rrs", 12, "r12", [B("A", "s", 30, 50, 270), B("B", "s", 66, 48, 270)], "B", "12"))
add(S(14, "rrs", 12, "r12", [B("A", "s", 36, 40, 90), B("B", "s", 50, 52, 90)], "A", "12",
      paths={"A": [[40, 40], [58, 40], [70, 42]]}))
add(S(15, "rrs", 13, "r13", [B("A", "s", 72, 50, 270), B("B", "s", 40, 52, 0, "tk")], "B", "13",
      paths={"B": [[40, 52], [40, 44], [34, 38]]}))
add(S(16, "rrs", 13, "r13", [B("A", "s", 20, 45, 90), B("B", "s", 58, 47, 0, "tk")], "B", "13",
      paths={"B": [[58, 47], [58, 39], [52, 33]]}))
add(S(17, "rrs", 15, "r15", [B("A", "s", 28, 52, 90), B("B", "s", 55, 57, 315, "ctk")], "B", "15"))
_g = toward((50, 60), 225, 25)
_h = toward((50, 60), 135, 25)
add(S(18, "rrs", 15, "r15", [B("A", "s", _g[0], _g[1], 225, "gy"), B("B", "s", _h[0], _h[1], 135)], "A", "15"))
add(S(19, "rrs", 16, "r16a", [B("A", "s", 70, 45, 270, "alt"), B("B", "s", 28, 62, 75)], "A", "16.1",
      paths={"A": [[70, 45], [56, 45], [44, 58]]}))
add(S(20, "rrs", 16, "r16b", [B("A", "s", 60, 50, 270), B("B", "s", 38, 72, 45)], "A", "16.2"))
add(S(21, "rrs", 14, "r14", [B("A", "s", 60, 50, 270), B("B", "s", 36, 50, 90, "late")], "A", "14"))
add(S(22, "rrs", 23, "r23", [B("A", "s", 72, 50, 270), B("B", "c", 38, 50, 90, "cap")], "A", "23.1"))
add(S(23, "rrs", 18, "r18o", [B("A", "s", 45, 56, 170), B("B", "s", 37, 56, 170)], "B", "18.2",
      marks=[[50, 80]], zone=[[50, 80, 24]]))
add(S(24, "rrs", 18, "r18b", [B("A", "s", 46, 38, 170), B("B", "s", 42, 56, 170)], "A", "18.2",
      marks=[[50, 80]], zone=[[50, 80, 24]]))
add(S(25, "rrs", 18, "r18o", [B("A", "s", 30, 58, 90), B("B", "s", 30, 49, 90)], "B", "18.2",
      marks=[[62, 62]], zone=[[62, 62, 24]]))
_p = cross((50, 30), "s", 315, 26, "s", 45, 26)
add(S(26, "rrs", 18, "r10b", _p, "B", "10", marks=[[50, 20]], zone=[[50, 20, 24]]))
add(S(27, "rrs", 19, "r19", [B("A", "s", 28, 46, 90), B("B", "s", 28, 38, 90)], "B", "19.2",
      obst=[[[58, 56], [80, 56], [80, 72], [58, 72]]]))
add(S(28, "rrs", 20, "r20", [B("A", "s", 40, 48, 45, "hail"), B("B", "s", 33.6, 41.6, 45)], "B", "20",
      obst=[[[58, 14], [78, 14], [78, 30], [58, 30]]]))
add(S(29, "rrs", 10, "r10", cross((50, 58), "s", 315, 26, "s", 45, 26), "B", "10",
      line=[[20, 58], [80, 58]]))
add(S(30, "rrs", 11, "r11", [B("A", "s", 40, 70, 45), B("B", "s", 47, 77, 45)], "A", "11",
      line=[[20, 58], [80, 58]]))
# ---- RIPAM, de jour : 13 --------------------------------------------------
add(S(31, "col", None, "c12a", cross((50, 50), "s", 300, 28, "s", 60, 28), "B", "12"))
add(S(32, "col", None, "c12b", [B("A", "s", 58, 50, 270), B("B", "s", 60, 40, 270)], "B", "12"))
add(S(33, "col", None, "c13", [B("A", "s", 60, 50, 90), B("B", "m", 25, 53, 90)], "B", "13"))
add(S(34, "col", None, "c13", [B("A", "s", 68, 47, 270), B("B", "m", 35, 50, 270)], "A", "13"))
add(S(35, "col", None, "c14", [B("A", "m", 45, 80, 0), B("B", "m", 55, 15, 180)], "AB", "14", wind=False))
add(S(36, "col", None, "c15", cross((50, 50), "m", 0, 26, "m", 270, 26), "A", "15", wind=False))
add(S(37, "col", None, "c18a", cross((60, 50), "s", 90, 30, "m", 0, 28), "B", "18"))
add(S(38, "col", None, "c18f", cross((45, 48), "s", 270, 30, "f", 0, 18), "A", "18"))
add(S(39, "col", None, "c9", [B("A", "s", 72, 62, 270), B("B", "g", 50, 30, 180)], "A", "9",
      walls=[[[35, 0], [35, 100]], [[65, 0], [65, 100]]]))
add(S(40, "col", None, "c9", [B("A", "s", 47, 20, 170), B("B", "g", 50, 85, 0)], "A", "9",
      walls=[[[38, 100], [38, 62], [20, 62]], [[62, 100], [62, 62], [80, 62]]]))
add(S(41, "col", None, "c9d", [B("A", "m", 42, 20, 180), B("B", "m", 58, 80, 0)], "AB", "9", wind=False,
      walls=[[[30, 0], [30, 100]], [[70, 0], [70, 100]]]))
add(S(42, "col", None, "c13", [B("A", "m", 50, 20, 180), B("B", "s", 50, 50, 170)], "A", "13",
      walls=[[[34, 0], [34, 100]], [[66, 0], [66, 100]]]))
add(S(43, "col", None, "c25", [B("A", "u", 50, 76, 0), B("B", "s", 24, 50, 90)], "A", "3, 18"))
# ---- RIPAM, feux de nuit : 7 ----------------------------------------------
add(S(44, "luc", None, "lred", [B("A", "m", 50, 76, 0), B("B", "m", 76, 50, 270)], "A", "15, 21",
      wind=False, night=True))
add(S(45, "luc", None, "lgreen", [B("A", "m", 50, 76, 0), B("B", "m", 24, 50, 90)], "B", "15, 17",
      wind=False, night=True))
add(S(46, "luc", None, "lhead", [B("A", "m", 50, 80, 0), B("B", "m", 52, 20, 180)], "AB", "14",
      wind=False, night=True))
add(S(47, "luc", None, "lstern", [B("A", "m", 50, 80, 0), B("B", "m", 50, 40, 0)], "A", "13, 21",
      wind=False, night=True))
add(S(48, "luc", None, "lsailpow", [B("A", "m", 50, 78, 0), B("B", "s", 22, 50, 90)], "A", "18, 25",
      wind=False, night=True))
add(S(49, "luc", None, "lfish", [B("A", "s", 25, 50, 90), B("B", "f", 60, 70, 0)], "A", "18, 26",
      night=True))
add(S(50, "luc", None, "lnuc", [B("A", "m", 50, 78, 0), B("B", "n", 50, 45, 0)], "A", "18, 27",
      wind=False, night=True))

T = {  # réponses d'une phrase : fr, en, de, it, es, pt
 "r10": ["Sur des bords opposés, le bateau bâbord amures s'écarte du bateau tribord amures (règle 10).",
  "On opposite tacks, the port-tack boat keeps clear of the starboard-tack boat (rule 10).",
  "Auf verschiedenen Bugs hält das Boot auf Backbordbug Abstand vom Boot auf Steuerbordbug (Regel 10).",
  "Su mure opposte, la barca mure a sinistra lascia strada a quella mure a dritta (regola 10).",
  "En amuras opuestas, el barco amurado a babor se aparta del amurado a estribor (regla 10).",
  "Em amuras opostas, o barco amurado a bombordo afasta-se do amurado a estibordo (regra 10)."],
 "r10b": ["À la bouée au vent, la règle 18 ne s'applique pas entre bords opposés : la règle 10 décide, bâbord s'écarte.",
  "At the windward mark, rule 18 does not apply between boats on opposite tacks: rule 10 decides, port keeps clear.",
  "An der Luvtonne gilt Regel 18 nicht zwischen Booten auf verschiedenen Bugs: Regel 10 entscheidet, Backbord weicht aus.",
  "Alla boa di bolina la regola 18 non vale tra barche su mure opposte: decide la regola 10, la mure a sinistra lascia strada.",
  "En la baliza de barlovento la regla 18 no se aplica entre amuras opuestas: decide la regla 10, babor se aparta.",
  "Na bóia de barlavento a regra 18 não se aplica entre amuras opostas: decide a regra 10, bombordo afasta-se."],
 "r11": ["Sur le même bord et en recouvrement, le bateau au vent s'écarte du bateau sous le vent (règle 11).",
  "On the same tack and overlapped, the windward boat keeps clear of the leeward boat (rule 11).",
  "Auf gleichem Bug und überlappend hält das Luvboot Abstand vom Leeboot (Regel 11).",
  "Sulla stessa mura e in sovrapposizione, la barca sopravento lascia strada a quella sottovento (regola 11).",
  "En la misma amura y con overlap, el barco de barlovento se aparta del de sotavento (regla 11).",
  "Na mesma amura e com sobreposição, o barco de barlavento afasta-se do de sotavento (regra 11)."],
 "r12": ["Sur le même bord sans recouvrement, le bateau derrière s'écarte du bateau devant (règle 12).",
  "On the same tack and not overlapped, the boat clear astern keeps clear of the boat clear ahead (rule 12).",
  "Auf gleichem Bug ohne Überlappung hält das hintere Boot Abstand vom vorderen (Regel 12).",
  "Sulla stessa mura e senza sovrapposizione, la barca dietro lascia strada a quella davanti (regola 12).",
  "En la misma amura y sin overlap, el barco de atrás se aparta del de delante (regla 12).",
  "Na mesma amura e sem sobreposição, o barco de trás afasta-se do da frente (regra 12)."],
 "r13": ["Après avoir passé le vent debout, un bateau qui vire s'écarte des autres jusqu'à ce qu'il soit au près sur son nouveau bord (règle 13).",
  "After passing head to wind, a tacking boat keeps clear of the others until she is on a close-hauled course (rule 13).",
  "Nach dem Durchgang durch den Wind hält das wendende Boot Abstand von allen anderen, bis es am Wind segelt (Regel 13).",
  "Dopo aver passato la prua al vento, la barca che vira lascia strada alle altre finché non è di bolina (regola 13).",
  "Tras pasar por la proa al viento, el barco que vira se aparta de los demás hasta que navega de ceñida (regla 13).",
  "Depois de passar com a proa ao vento, o barco que vira afasta-se dos outros até estar de bolina (regra 13)."],
 "r14": ["Même prioritaire, un bateau doit éviter le contact dès qu'il est clair que l'autre ne s'écarte pas (règle 14).",
  "Even with right of way, a boat must avoid contact once it is clear the other is not keeping clear (rule 14).",
  "Auch mit Wegerecht muss ein Boot einen Zusammenstoß vermeiden, sobald klar ist, dass das andere nicht ausweicht (Regel 14).",
  "Anche con la precedenza, una barca deve evitare il contatto appena è chiaro che l'altra non si scosta (regola 14).",
  "Incluso con derecho de paso, un barco debe evitar el contacto en cuanto está claro que el otro no se aparta (regla 14).",
  "Mesmo com prioridade, um barco deve evitar o contacto assim que é claro que o outro não se afasta (regra 14)."],
 "r15": ["Un bateau qui devient prioritaire en virant ou en empannant doit d'abord laisser à l'autre la place de s'écarter (règle 15).",
  "A boat that gains right of way by tacking or gybing must first give the other boat room to keep clear (rule 15).",
  "Ein Boot, das durch Wende oder Halse Wegerecht erlangt, muss dem anderen zunächst Raum zum Ausweichen geben (Regel 15).",
  "Una barca che ottiene la precedenza virando o strambando deve prima lasciare all'altra lo spazio per scostarsi (regola 15).",
  "Un barco que adquiere derecho de paso virando o trasluchando debe dar primero al otro espacio para apartarse (regla 15).",
  "Um barco que ganha prioridade ao virar ou ao jibar deve primeiro dar ao outro espaço para se afastar (regra 15)."],
 "r16a": ["Un bateau prioritaire qui change de route doit laisser à l'autre la place de s'écarter (règle 16.1).",
  "A right-of-way boat that changes course must give the other boat room to keep clear (rule 16.1).",
  "Ein Boot mit Wegerecht, das den Kurs ändert, muss dem anderen Raum zum Ausweichen lassen (Regel 16.1).",
  "Una barca con la precedenza che cambia rotta deve lasciare all'altra lo spazio per scostarsi (regola 16.1).",
  "Un barco con derecho de paso que cambia de rumbo debe dar al otro espacio para apartarse (regla 16.1).",
  "Um barco com prioridade que muda de rumo deve dar ao outro espaço para se afastar (regra 16.1)."],
 "r16b": ["Le bateau tribord ne doit pas changer de route si le bateau bâbord qui passe derrière devrait alors manœuvrer à nouveau (règle 16.2).",
  "The starboard boat must not change course if the port-tack boat passing astern would then have to alter course again (rule 16.2).",
  "Das Steuerbordboot darf den Kurs nicht ändern, wenn das hinter ihm durchgehende Backbordboot dann erneut ausweichen müsste (Regel 16.2).",
  "La barca mure a dritta non deve cambiare rotta se quella mure a sinistra che passa a poppa dovesse allora manovrare di nuovo (regola 16.2).",
  "El barco de estribor no debe cambiar de rumbo si el de babor que pasa por su popa tuviera que maniobrar de nuevo (regla 16.2).",
  "O barco de estibordo não deve mudar de rumo se o de bombordo que passa por sua popa tivesse de manobrar outra vez (regra 16.2)."],
 "r23": ["Si possible, un bateau doit éviter un bateau chaviré, mouillé ou échoué, même s'il est prioritaire (règle 23.1).",
  "If possible, a boat must avoid a capsized, anchored or aground boat, even with right of way (rule 23.1).",
  "Wenn möglich muss ein Boot ein gekentertes, geankertes oder aufgelaufenes Boot meiden, auch mit Wegerecht (Regel 23.1).",
  "Se possibile, una barca deve evitare una barca scuffiata, all'ancora o incagliata, anche se ha la precedenza (regola 23.1).",
  "Si es posible, un barco debe evitar a otro volcado, fondeado o varado, aunque tenga derecho de paso (regla 23.1).",
  "Se possível, um barco deve evitar outro virado, fundeado ou encalhado, mesmo com prioridade (regra 23.1)."],
 "r18o": ["Si les bateaux sont en recouvrement quand le premier entre dans la zone des trois longueurs, le bateau extérieur donne la place à la bouée au bateau intérieur (règle 18.2).",
  "If boats are overlapped when the first reaches the three-length zone, the outside boat gives the inside boat room at the mark (rule 18.2).",
  "Sind die Boote überlappt, wenn das erste die Drei-Längen-Zone erreicht, gibt das äußere Boot dem inneren Raum an der Marke (Regel 18.2).",
  "Se le barche sono sovrapposte quando la prima entra nella zona delle tre lunghezze, quella esterna dà spazio alla boa a quella interna (regola 18.2).",
  "Si los barcos están con overlap cuando el primero entra en la zona de tres esloras, el exterior da espacio en la baliza al interior (regla 18.2).",
  "Se os barcos estão sobrepostos quando o primeiro entra na zona dos três comprimentos, o exterior dá espaço na bóia ao interior (regra 18.2)."],
 "r18b": ["Sans recouvrement à l'entrée de la zone, le bateau derrière laisse la place à la bouée au bateau devant (règle 18.2).",
  "If not overlapped when the first reaches the zone, the boat astern gives the boat ahead room at the mark (rule 18.2).",
  "Ohne Überlappung beim Erreichen der Zone gibt das hintere Boot dem vorderen Raum an der Marke (Regel 18.2).",
  "Senza sovrapposizione all'ingresso nella zona, la barca dietro dà spazio alla boa a quella davanti (regola 18.2).",
  "Sin overlap a la entrada de la zona, el barco de atrás da espacio en la baliza al de delante (regla 18.2).",
  "Sem sobreposição à entrada da zona, o barco de trás dá espaço na bóia ao da frente (regra 18.2)."],
 "r19": ["En recouvrement près d'un obstacle, le bateau extérieur laisse au bateau intérieur la place de passer entre lui et l'obstacle (règle 19.2).",
  "When overlapped at an obstacle, the outside boat gives the inside boat room to pass between her and the obstacle (rule 19.2).",
  "Überlappt an einem Hindernis gibt das äußere Boot dem inneren Raum zwischen sich und dem Hindernis (Regel 19.2).",
  "In sovrapposizione a un ostacolo, la barca esterna lascia alla interna lo spazio per passare tra sé e l'ostacolo (regola 19.2).",
  "Con overlap en un obstáculo, el barco exterior da al interior espacio para pasar entre él y el obstáculo (regla 19.2).",
  "Com sobreposição num obstáculo, o barco exterior dá ao interior espaço para passar entre ele e o obstáculo (regra 19.2)."],
 "r20": ["Un bateau qui doit virer pour éviter un obstacle peut héler « Place pour virer » ; l'autre doit virer ou répondre « Vire » (règle 20).",
  "A boat that must tack to avoid an obstacle may hail \"Room to tack\"; the other boat must tack or reply \"You tack\" (rule 20).",
  "Ein Boot, das wegen eines Hindernisses wenden muss, darf „Raum zum Wenden“ rufen; das andere muss wenden oder „Du wendest“ antworten (Regel 20).",
  "Una barca che deve virare per evitare un ostacolo può chiamare «Spazio per virare»; l'altra deve virare o rispondere «Vira tu» (regola 20).",
  "Un barco que debe virar para evitar un obstáculo puede gritar «Espacio para virar»; el otro debe virar o responder «Vira tú» (regla 20).",
  "Um barco que tem de virar para evitar um obstáculo pode gritar «Espaço para virar»; o outro deve virar ou responder «Vira tu» (regra 20)."],
 "c12a": ["Deux voiliers avec le vent de côtés différents : celui qui reçoit le vent par bâbord s'écarte (RIPAM règle 12).",
  "Two sailing vessels with the wind on different sides: the one with the wind on the port side keeps out of the way (COLREG rule 12).",
  "Zwei Segelfahrzeuge mit Wind von verschiedenen Seiten: das mit Wind von Backbord weicht aus (KVR Regel 12).",
  "Due barche a vela con il vento da lati diversi: quella con il vento a sinistra si tiene fuori rotta (RIPAM regola 12).",
  "Dos veleros con el viento por bandas distintas: el que lo recibe por babor se aparta (RIPA regla 12).",
  "Dois veleiros com o vento de bordos diferentes: o que o recebe por bombordo afasta-se (RIPEAM regra 12)."],
 "c12b": ["Deux voiliers avec le vent du même côté : celui qui est au vent s'écarte de celui qui est sous le vent (RIPAM règle 12).",
  "Two sailing vessels with the wind on the same side: the windward vessel keeps out of the way of the leeward one (COLREG rule 12).",
  "Zwei Segelfahrzeuge mit Wind von derselben Seite: das Luvfahrzeug weicht dem Leefahrzeug aus (KVR Regel 12).",
  "Due barche a vela con il vento dallo stesso lato: quella sopravento si tiene fuori rotta da quella sottovento (RIPAM regola 12).",
  "Dos veleros con el viento por la misma banda: el de barlovento se aparta del de sotavento (RIPA regla 12).",
  "Dois veleiros com o vento do mesmo bordo: o de barlavento afasta-se do de sotavento (RIPEAM regra 12)."],
 "c13": ["Le bateau qui en rattrape un autre s'écarte, qu'il soit à voile ou à moteur (RIPAM règle 13).",
  "The vessel overtaking another keeps out of the way, whether under sail or power (COLREG rule 13).",
  "Das überholende Fahrzeug weicht aus, ob unter Segel oder Motor (KVR Regel 13).",
  "La barca che raggiunge un'altra si tiene fuori rotta, a vela o a motore (RIPAM regola 13).",
  "El buque que alcanza a otro se aparta, vaya a vela o a motor (RIPA regla 13).",
  "O barco que ultrapassa outro afasta-se, seja à vela ou a motor (RIPEAM regra 13)."],
 "c14": ["Deux bateaux à moteur qui se rencontrent cap à cap changent tous deux de cap sur tribord (RIPAM règle 14).",
  "Two power-driven vessels meeting head-on both alter course to starboard (COLREG rule 14).",
  "Zwei Maschinenfahrzeuge auf entgegengesetzten Kursen weichen beide nach Steuerbord aus (KVR Regel 14).",
  "Due unità a motore che si incontrano prua contro prua accostano entrambe a dritta (RIPAM regola 14).",
  "Dos buques de propulsión mecánica que se encuentran de vuelta encontrada caen ambos a estribor (RIPA regla 14).",
  "Dois barcos a motor que se cruzam de roda a roda guinam ambos para estibordo (RIPEAM regra 14)."],
 "c15": ["Deux bateaux à moteur qui se croisent : celui qui voit l'autre par sa droite (tribord) s'écarte (RIPAM règle 15).",
  "Two power-driven vessels crossing: the one that has the other on her starboard side keeps out of the way (COLREG rule 15).",
  "Zwei kreuzende Maschinenfahrzeuge: das, das das andere an Steuerbord hat, weicht aus (KVR Regel 15).",
  "Due unità a motore che si incrociano: quella che ha l'altra sulla propria dritta si tiene fuori rotta (RIPAM regola 15).",
  "Dos buques de propulsión mecánica que se cruzan: el que ve al otro por su estribor se aparta (RIPA regla 15).",
  "Dois barcos a motor que se cruzam: o que tem o outro por estibordo afasta-se (RIPEAM regra 15)."],
 "c18a": ["Un bateau à moteur s'écarte d'un voilier, quel que soit le bord du voilier ou le côté d'où il arrive (RIPAM règle 18).",
  "A power-driven vessel keeps out of the way of a sailing vessel, whatever the tack or side it comes from (COLREG rule 18).",
  "Ein Maschinenfahrzeug weicht einem Segelfahrzeug aus, egal auf welchem Bug oder von welcher Seite (KVR Regel 18).",
  "Un'unità a motore si tiene fuori rotta da una barca a vela, qualunque sia la mura o il lato da cui arriva (RIPAM regola 18).",
  "Un buque de propulsión mecánica se aparta de un velero, sea cual sea la amura o el lado por el que llegue (RIPA regla 18).",
  "Um barco a motor afasta-se de um veleiro, qualquer que seja a amura ou o lado de onde venha (RIPEAM regra 18)."],
 "c18f": ["Un voilier s'écarte d'un bateau qui pêche (RIPAM règle 18).",
  "A sailing vessel keeps out of the way of a vessel engaged in fishing (COLREG rule 18).",
  "Ein Segelfahrzeug weicht einem fischenden Fahrzeug aus (KVR Regel 18).",
  "Una barca a vela si tiene fuori rotta da un'unità che sta pescando (RIPAM regola 18).",
  "Un velero se aparta de un buque dedicado a la pesca (RIPA regla 18).",
  "Um veleiro afasta-se de um barco que está a pescar (RIPEAM regra 18)."],
 "c9": ["Dans un chenal étroit ou à l'entrée d'un port, un voilier ne doit pas gêner un bateau qui ne peut naviguer qu'à l'intérieur du chenal (RIPAM règle 9).",
  "In a narrow channel or harbour entrance, a sailing vessel must not impede a vessel that can navigate safely only within the channel (COLREG rule 9).",
  "In einem engen Fahrwasser oder einer Hafeneinfahrt darf ein Segelfahrzeug ein Fahrzeug nicht behindern, das nur innerhalb des Fahrwassers sicher fahren kann (KVR Regel 9).",
  "In un canale stretto o all'imboccatura di un porto, una barca a vela non deve ostacolare un'unità che può navigare solo all'interno del canale (RIPAM regola 9).",
  "En un canal estrecho o a la entrada de un puerto, un velero no debe estorbar a un buque que solo puede navegar por dentro del canal (RIPA regla 9).",
  "Num canal estreito ou à entrada de um porto, um veleiro não deve estorvar um barco que só pode navegar dentro do canal (RIPEAM regra 9)."],
 "c9d": ["Dans un chenal étroit, chacun garde sa droite (tribord) et passe bâbord contre bâbord (RIPAM règle 9).",
  "In a narrow channel each vessel keeps to the starboard side and passes port to port (COLREG rule 9).",
  "In einem engen Fahrwasser hält jedes Fahrzeug sich an der Steuerbordseite und passiert Backbord an Backbord (KVR Regel 9).",
  "In un canale stretto ognuno tiene la propria dritta e si incrocia sinistra con sinistra (RIPAM regola 9).",
  "En un canal estrecho cada buque navega por su estribor y se cruza babor con babor (RIPA regla 9).",
  "Num canal estreito cada barco mantém-se a estibordo e cruza-se bombordo com bombordo (RIPEAM regra 9)."],
 "c25": ["Un voilier qui avance au moteur est un bateau à moteur : il s'écarte du voilier qui avance à la voile (RIPAM règles 3 et 18).",
  "A sailboat under engine is a power-driven vessel: it keeps out of the way of one that is under sail (COLREG rules 3 and 18).",
  "Eine Segelyacht unter Motor ist ein Maschinenfahrzeug: Sie weicht dem Segler unter Segeln aus (KVR Regeln 3 und 18).",
  "Una barca a vela che va a motore è un'unità a motore: si tiene fuori rotta da quella che naviga a vela (RIPAM regole 3 e 18).",
  "Un velero que navega a motor es un buque de propulsión mecánica: se aparta del que navega a vela (RIPA reglas 3 y 18).",
  "Um veleiro a motor é um barco a motor: afasta-se do que navega à vela (RIPEAM regras 3 e 18)."],
 "lred": ["Tu vois son feu de bâbord (rouge) : il te croise par ta droite, tu dois t'écarter (RIPAM règles 15 et 21).",
  "You see its red port light: it is crossing from your starboard side, so you give way (COLREG rules 15 and 21).",
  "Du siehst sein rotes Backbordlicht: Es kreuzt von deiner Steuerbordseite, also weichst du aus (KVR Regeln 15 und 21).",
  "Vedi il suo fanale rosso di sinistra: ti incrocia da dritta, quindi devi scostarti tu (RIPAM regole 15 e 21).",
  "Ves su luz roja de babor: te cruza por tu estribor, así que te apartas tú (RIPA reglas 15 y 21).",
  "Vês a sua luz vermelha de bombordo: cruza-te por estibordo, por isso afastas-te tu (RIPEAM regras 15 e 21)."],
 "lgreen": ["Tu vois son feu vert : il vient de ta gauche, c'est lui qui s'écarte et tu maintiens ta route (RIPAM règles 15 et 17).",
  "You see its green starboard light: it is crossing from your port side, so it gives way and you hold your course (COLREG rules 15 and 17).",
  "Du siehst sein grünes Steuerbordlicht: Es kreuzt von deiner Backbordseite, es weicht aus und du behältst den Kurs (KVR Regeln 15 und 17).",
  "Vedi il suo fanale verde: ti incrocia da sinistra, deve scostarsi lui e tu mantieni la rotta (RIPAM regole 15 e 17).",
  "Ves su luz verde de estribor: te cruza por tu babor, se aparta él y tú mantienes el rumbo (RIPA reglas 15 y 17).",
  "Vês a sua luz verde de estibordo: cruza-te por bombordo, ele afasta-se e tu manténs o rumo (RIPEAM regras 15 e 17)."],
 "lhead": ["Rouge, vert et feu de tête de mât en même temps : vous êtes cap à cap, changez tous deux de cap sur tribord (RIPAM règle 14).",
  "Red, green and masthead light together: you are head-on, both alter course to starboard (COLREG rule 14).",
  "Rot, Grün und Topplicht zugleich: ihr seid auf Gegenkurs, beide weichen nach Steuerbord aus (KVR Regel 14).",
  "Rosso, verde e fanale di testa d'albero insieme: siete prua contro prua, accostate entrambi a dritta (RIPAM regola 14).",
  "Rojo, verde y luz de tope a la vez: estáis de vuelta encontrada, caed ambos a estribor (RIPA regla 14).",
  "Vermelho, verde e luz de topo ao mesmo tempo: estão de roda a roda, guinem ambos para estibordo (RIPEAM regra 14)."],
 "lstern": ["Tu ne vois que son feu de poupe blanc : tu le rattrapes, c'est à toi de t'écarter (RIPAM règles 13 et 21).",
  "You see only its white stern light: you are overtaking it, so you keep out of the way (COLREG rules 13 and 21).",
  "Du siehst nur sein weißes Hecklicht: Du überholst, also weichst du aus (KVR Regeln 13 und 21).",
  "Vedi solo il suo fanale bianco di poppa: lo stai raggiungendo, quindi ti scosti tu (RIPAM regole 13 e 21).",
  "Solo ves su luz blanca de alcance: lo estás alcanzando, así que te apartas tú (RIPA reglas 13 y 21).",
  "Só vês a sua luz branca de popa: estás a ultrapassá-lo, por isso afastas-te tu (RIPEAM regras 13 e 21)."],
 "lsailpow": ["Des feux de côté sans feu de tête de mât montrent un voilier : toi, à moteur, tu t'écartes quelle que soit la couleur vue (RIPAM règles 18 et 25).",
  "Sidelights without a masthead light show a sailing vessel: you, under power, keep out of the way whichever colour you see (COLREG rules 18 and 25).",
  "Seitenlichter ohne Topplicht zeigen ein Segelfahrzeug: Du als Maschinenfahrzeug weichst aus, egal welche Farbe du siehst (KVR Regeln 18 und 25).",
  "Fanali di via senza luce di testa d'albero indicano una barca a vela: tu, a motore, ti scosti qualunque colore tu veda (RIPAM regole 18 e 25).",
  "Luces de costado sin luz de tope indican un velero: tú, a motor, te apartas veas el color que veas (RIPA reglas 18 y 25).",
  "Luzes de bordo sem luz de topo indicam um veleiro: tu, a motor, afastas-te seja qual for a cor que vês (RIPEAM regras 18 e 25)."],
 "lfish": ["Rouge au-dessus de blanc = bateau qui pêche : le voilier s'écarte (RIPAM règles 18 et 26).",
  "Red over white means a vessel fishing: the sailing vessel keeps out of the way (COLREG rules 18 and 26).",
  "Rot über Weiß bedeutet ein fischendes Fahrzeug: Das Segelfahrzeug weicht aus (KVR Regeln 18 und 26).",
  "Rosso sopra bianco indica un'unità che pesca: la barca a vela si scosta (RIPAM regole 18 e 26).",
  "Rojo sobre blanco indica un buque pescando: el velero se aparta (RIPA reglas 18 y 26).",
  "Vermelho sobre branco indica um barco a pescar: o veleiro afasta-se (RIPEAM regras 18 e 26)."],
 "lnuc": ["Deux feux rouges superposés = bateau qui n'est pas maître de sa manœuvre : tu t'écartes (RIPAM règles 18 et 27).",
  "Two red lights one above the other mean a vessel not under command: you keep out of the way (COLREG rules 18 and 27).",
  "Zwei rote Lichter übereinander bedeuten ein manövrierunfähiges Fahrzeug: Du weichst aus (KVR Regeln 18 und 27).",
  "Due fanali rossi in verticale indicano una nave non governata: ti scosti tu (RIPAM regole 18 e 27).",
  "Dos luces rojas en vertical indican un buque sin gobierno: te apartas tú (RIPA reglas 18 y 27).",
  "Duas luzes vermelhas na vertical indicam um barco sem governo: afastas-te tu (RIPEAM regras 18 e 27)."],
}

# Interface : une entrée par clé, six langues dans l'ordre fr, en, de, it, es, pt.
UI = {
 "titre": ["Simulateur de priorités", "Right-of-way simulator", "Vorfahrts-Simulator", "Simulatore di precedenze", "Simulador de preferencias", "Simulador de prioridades"],
 "intro": ["50 situations en mer : qui doit s'écarter ? Règles de course, RIPAM de jour et feux de nuit. Vent du haut de l'écran.",
  "50 situations at sea: who must keep clear? Racing rules, COLREG by day and night lights. Wind comes from the top of the screen.",
  "50 Situationen auf See: Wer muss ausweichen? Wettsegelregeln, KVR am Tag und Lichterführung bei Nacht. Der Wind kommt von oben.",
  "50 situazioni in mare: chi deve scostarsi? Regole di regata, RIPAM di giorno e fanali di notte. Il vento arriva dall'alto dello schermo.",
  "50 situaciones en el mar: ¿quién debe apartarse? Reglas de regata, RIPA de día y luces de noche. El viento viene de la parte superior de la pantalla.",
  "50 situações no mar: quem deve afastar-se? Regras de regata, RIPEAM de dia e luzes de noite. O vento vem do topo do ecrã."],
 "retour": ["← Sailing More", "← Sailing More", "← Sailing More", "← Sailing More", "← Sailing More", "← Sailing More"],
 "tous": ["Tous", "All", "Alle", "Tutti", "Todos", "Todos"],
 "f_rrs": ["Règles de course", "Racing rules", "Wettsegelregeln", "Regole di regata", "Reglas de regata", "Regras de regata"],
 "f_col": ["RIPAM de jour", "COLREG by day", "KVR am Tag", "RIPAM di giorno", "RIPA de día", "RIPEAM de dia"],
 "f_luc": ["Feux de nuit", "Night lights", "Lichter bei Nacht", "Fanali di notte", "Luces de noche", "Luzes de noite"],
 "col": ["RIPAM", "COLREG", "KVR", "RIPAM", "RIPA", "RIPEAM"],
 "question": ["Quel bateau doit s'écarter ?", "Which boat must keep clear?", "Welches Boot muss ausweichen?", "Quale barca deve scostarsi?", "¿Qué barco debe apartarse?", "Qual barco deve afastar-se?"],
 "nuit": ["Tu es A. Voici les feux de B vus depuis A.", "You are A. These are B's lights as seen from A.", "Du bist A. Das sind die Lichter von B, von A aus gesehen.", "Tu sei A. Questi sono i fanali di B visti da A.", "Tú eres A. Estas son las luces de B vistas desde A.", "Tu és A. Estas são as luzes de B vistas de A."],
 "repA": ["A s'écarte", "A keeps clear", "A weicht aus", "A si scosta", "A se aparta", "A afasta-se"],
 "repB": ["B s'écarte", "B keeps clear", "B weicht aus", "B si scosta", "B se aparta", "B afasta-se"],
 "repAB": ["Les deux", "Both", "Beide", "Entrambe", "Los dos", "Os dois"],
 "ok": ["Bonne réponse.", "Correct.", "Richtig.", "Risposta esatta.", "Correcto.", "Certo."],
 "ko": ["Pas tout à fait.", "Not quite.", "Nicht ganz.", "Non proprio.", "No exactamente.", "Não exatamente."],
 "reponse": ["Réponse :", "Answer:", "Antwort:", "Risposta:", "Respuesta:", "Resposta:"],
 "rA": ["A s'écarte", "A keeps clear", "A weicht aus", "A si scosta", "A se aparta", "A afasta-se"],
 "rB": ["B s'écarte", "B keeps clear", "B weicht aus", "B si scosta", "B se aparta", "B afasta-se"],
 "rAB": ["les deux s'écartent", "both keep clear", "beide weichen aus", "entrambe si scostano", "los dos se apartan", "ambos se afastam"],
 "regle": ["Voir la règle dans les 113 règles", "See the rule among the 113 rules", "Regel in den 113 Regeln ansehen", "Vedi la regola tra le 113 regole", "Ver la regla entre las 113 reglas", "Ver a regra entre as 113 regras"],
 "prec": ["← Précédent", "← Previous", "← Zurück", "← Precedente", "← Anterior", "← Anterior"],
 "suiv": ["Suivant →", "Next →", "Weiter →", "Successivo →", "Siguiente →", "Seguinte →"],
 "alea": ["Au hasard", "Random", "Zufällig", "A caso", "Al azar", "Ao acaso"],
 "lien": ["Copier le lien", "Copy link", "Link kopieren", "Copia il link", "Copiar enlace", "Copiar ligação"],
 "copie": ["Lien copié", "Link copied", "Link kopiert", "Link copiato", "Enlace copiado", "Ligação copiada"],
 "score": ["Score", "Score", "Punkte", "Punteggio", "Puntuación", "Pontuação"],
 "vent": ["vent", "wind", "Wind", "vento", "viento", "vento"],
 "zone": ["zone 3L", "3L zone", "3L-Zone", "zona 3L", "zona 3L", "zona 3L"],
 "t_tk": ["vire de bord", "tacking", "wendet", "vira", "vira", "vira"],
 "t_ctk": ["vient de virer", "has just tacked", "hat gerade gewendet", "ha appena virato", "acaba de virar", "acabou de virar"],
 "t_gy": ["empanne", "gybing", "halst", "strambando", "trasluchando", "jibando"],
 "t_alt": ["change de route", "alters course", "ändert den Kurs", "cambia rotta", "cambia de rumbo", "muda de rumo"],
 "t_late": ["ne réagit pas", "does not react", "reagiert nicht", "non reagisce", "no reacciona", "não reage"],
 "t_cap": ["chaviré", "capsized", "gekentert", "scuffiata", "volcado", "virado"],
 "t_hail": ["« Place pour virer ! »", "\"Room to tack!\"", "„Raum zum Wenden!“", "«Spazio per virare!»", "«¡Espacio para virar!»", "«Espaço para virar!»"],
 "avert": ["Outil pédagogique : le texte officiel des règles fait foi. Les schémas montrent une situation figée, avec le même gabarit de bateau.",
  "Teaching tool: the official text of the rules prevails. Diagrams show a frozen situation with same-size boats.",
  "Lernhilfe: Maßgeblich ist der amtliche Regeltext. Die Skizzen zeigen eine eingefrorene Situation mit gleich großen Booten.",
  "Strumento didattico: fa fede il testo ufficiale delle regole. Gli schemi mostrano una situazione ferma con barche della stessa taglia.",
  "Herramienta didáctica: manda el texto oficial de las reglas. Los esquemas muestran una situación congelada con barcos del mismo tamaño.",
  "Ferramenta didática: vale o texto oficial das regras. Os esquemas mostram uma situação congelada com barcos do mesmo tamanho."],
 "scn": ["Scénario", "Scenario", "Szenario", "Scenario", "Escenario", "Cenário"],
}


def export():
    ui = {l: {k: v[i] for k, v in UI.items()} for i, l in enumerate(LANGS)}
    re_ = {l: {k: v[i] for k, v in T.items()} for i, l in enumerate(LANGS)}
    return {"ui": ui, "reasons": re_, "sc": SC}
