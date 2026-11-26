import json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chants_outils import get, API

DOSSIER = "claude/livrables/chants-images"
FICHIER = "claude/livrables/chants-images.json"

# id -> (titre Commons, licence, crédit)
LOT = {
 "saucy-arethusa": ("File:Francis Swaine (d. 1782) - The Engagement between\" The Arethusa\" and \"La Belle Poule\", 17 June 1778. - RCIN 405446 - Royal Collection.jpg",
   "Public domain (Wikimedia Commons)",
   "Francis Swaine, « The Engagement between The Arethusa and La Belle Poule, 17 June 1778 » (Royal Collection, RCIN 405446) — le combat que chante « The Saucy Arethusa » — Public domain, via Wikimedia Commons"),
 "la-pique": ("File:HMS Blanche and Pique.jpg",
   "Public domain (Wikimedia Commons)",
   "Robert Dodd, « HMS Blanche et La Pique » — la frégate Blanche prenant la frégate française La Pique (1795), l'action que raconte le chant — Public domain, via Wikimedia Commons"),
 "banks-of-sacramento": ("File:Ships-abandoned-in-Yerba-Buena-Cove-San-Francisco-during-the-California-gold-rush.-1849.jpg",
   "Public domain (Wikimedia Commons)",
   "William Shew, navires abandonnés dans la baie de Yerba Buena, San Francisco, pendant la ruée vers l'or (1849) — image de thème : le chant évoque cette route et cette ruée, il ne décrit pas cette scène — Public domain, via Wikimedia Commons"),
 "bully-boat": ("File:A race on the Mississippi LCCN2001703796.jpg",
   "Public domain (Wikimedia Commons)",
   "« A race on the Mississippi », lithographie américaine du XIXe siècle (Library of Congress, LCCN 2001703796) — image de thème : bateaux à vapeur du Mississippi, pas le « Bully Boat » du chant — Public domain, via Wikimedia Commons"),
 "a-roving": ("File:The 'Pieter and Paul' on the IJ in Amsterdam in 1698 (Abraham Storck).jpg",
   "Public domain (Wikimedia Commons)",
   "Abraham Storck, « Le Pieter and Paul sur l'IJ à Amsterdam en 1698 » — image de thème : le port d'Amsterdam cité par le chant, deux siècles avant sa collecte — Public domain, via Wikimedia Commons"),
 "drunken-sailor": ("File:Sailors Carousing RMG BHC1090.tiff",
   "Public domain (Wikimedia Commons)",
   "Julius Caesar Ibbetson, « Sailors Carousing » — Royal Museums Greenwich (BHC1090) — image de thème : marins en bordée, pas une illustration du chant — Public domain, via Wikimedia Commons"),
 "the-whale": ("File:The Northern Whale Fishery, by William John Huggins 1835.jpg",
   "Public domain (Wikimedia Commons)",
   "William John Huggins, « The Northern Whale Fishery » (1835) — image de thème : pêche à la baleine dans l'Arctique, pas une scène du chant — Public domain, via Wikimedia Commons"),
 "blow-ye-winds-morning": ("File:The 'Northern Whale Fishery'.jpg",
   "Public domain (Wikimedia Commons)",
   "Edward Duncan d'après William John Huggins, « The Northern Whale Fishery » — image de thème : baleinier au travail, pas une scène du chant — Public domain, via Wikimedia Commons"),
 "rolling-home": ("File:Antonio Jacobsen - The American clipper ship Flying Cloud at sea under full sail.jpg",
   "Public domain (Wikimedia Commons)",
   "Antonio Jacobsen, « Le clipper américain Flying Cloud en mer sous toutes voiles » — image de thème : un grand voilier du long cours, pas le navire du chant — Public domain, via Wikimedia Commons"),
 "homeward-bound": ("File:David Crockett (1853 clipper ship) by Jacobsen.jpg",
   "Public domain (Wikimedia Commons)",
   "Antonio Jacobsen, « David Crockett », clipper de 1853 — image de thème : un clipper sous voiles, pas le navire du chant — Public domain, via Wikimedia Commons"),
 "st-helena-soldier": ("File:MELLISS(1875) THE ROOM IN WHICH NAPOLEON DIED AT LONGWOOD.jpg",
   "Public domain (Wikimedia Commons)",
   "John Charles Melliss, « The room in which Napoleon died at Longwood » (1875, St Helena) — image de thème : le lieu de l'exil que garde le soldat du chant — Public domain, via Wikimedia Commons"),
 "fire-down-below": ("File:The Burning of the packet ship Boston in 1830.jpg",
   "Public domain (Wikimedia Commons)",
   "Fitz Henry Lane, « The Burning of the packet ship Boston in 1830 » — image de thème : incendie à bord d'un voilier, pas une scène du chant — Public domain, via Wikimedia Commons"),
}

import io
try:
    from PIL import Image
except Exception:
    Image = None


def largeur(b):
    if Image:
        return Image.open(io.BytesIO(b)).size[0]
    # JPEG SOF
    i = 2
    while i < len(b):
        if b[i] != 0xFF:
            i += 1; continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(b[i + 7:i + 9], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
    return 0


def main():
    liste = json.load(open(FICHIER))
    deja = {e["id"] for e in liste}
    os.makedirs(DOSSIER, exist_ok=True)
    for cid, (titre, lic, credit) in LOT.items():
        if cid in deja:
            print("déjà là", cid); continue
        ok = None
        for w in (1200, 1000, 900, 800):
            p = {"action": "query", "format": "json", "titles": titre, "prop": "imageinfo",
                 "iiprop": "url|size", "iiurlwidth": str(w)}
            j = json.loads(get(API + "?" + urllib.parse.urlencode(p)))
            ii = list(j["query"]["pages"].values())[0]["imageinfo"][0]
            if ii["width"] < 800:
                print("TROP PETIT", cid, ii["width"]); break
            url = ii.get("thumburl") or ii["url"]
            b = get(url, binary=True)
            lg = largeur(b)
            print(cid, w, len(b), lg)
            if len(b) <= 400 * 1024 and lg >= 800 and b[:2] == b"\xff\xd8":
                ok = (b, lg); break
        if not ok:
            print("ECHEC", cid); continue
        fn = cid + ".jpg"
        open(os.path.join(DOSSIER, fn), "wb").write(ok[0])
        liste.append({"id": cid, "fichier": fn,
                      "source": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(titre.replace(" ", "_"), safe="_(),:'"),
                      "licence": lic, "credit": credit, "page_livre": None, "largeur": ok[1]})
        json.dump(liste, open(FICHIER, "w"), ensure_ascii=False, indent=1)
    print("total", len(liste))


main()
