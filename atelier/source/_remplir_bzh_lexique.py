"""Complète le breton (mot.bzh) des termes qui n'en ont pas. Ne remplace jamais un breton existant.
Traductions de la nuit du 25/11/2026 : à faire relire par un bretonnant avant publication."""
import json, pathlib

BZH = {
 "etai": "stag", "grand-voile": "gwel-veur", "spinnaker": "spinnaker", "voile": "gwel",
 "barre-franche": "stur", "wishbone": "wishbone", "harnais": "harnez", "planche": "plankenn",
 "poulie": "rodell", "aile-avant": "askell a-raok", "mat-de-foil": "gwern foil",
 "aile-de-rappel": "askell", "aile-de-wing": "askell",
 "virer": "treiñ", "affaler": "diskenn", "hisser": "sevel", "border": "stardañ",
 "lofer": "tostaat ouzh an avel", "accoster": "tostaat", "ferler": "plegañ",
 "homme-a-la-mer": "un den er mor", "noeud-plat": "skoulm plat", "noeud-de-huit": "skoulm eizh",
 "attention-a-la-bome": "diwall ouzh ar bom",
 "pres": "tost d'an avel", "travers": "a-dreuz", "vent-arriere": "avel a-dreñv",
 "vent-reel": "avel wir", "au-vent": "a-us d'an avel", "cap": "kab",
 "bascule-du-vent": "tro an avel", "grain": "barrad-avel",
 "noeud-vitesse": "skoulm", "beaufort": "skeulenn Beaufort", "houle": "houl", "maree": "mare",
 "flot": "lanv", "pleine-mer": "mor leun", "basse-mer": "mor izel", "etale": "mor sioul",
 "bulletin-meteo": "keleier an amzer", "anticyclone": "gwask uhel", "brise-de-mer": "avel-vor",
 "brise-de-terre": "avel-douar", "brume": "latar", "visibilite": "gwelusted", "etat-de-la-mer": "stad ar mor",
 "lignes": "linennoù", "porte": "dor", "tour-de-penalite": "tro-kastiz", "protestation": "protestadenn",
 "regles-de-course": "reolennoù ar redadeg", "comite-de-course": "komite ar redadeg",
 "bateau-comite": "bag komite", "manche": "tro",
}
p = pathlib.Path("projets/sailingmore/lexique.json")
d = json.loads(p.read_text(encoding="utf-8"))
n = 0
for t in d["themes"]:
    for x in t.get("termes", []):
        if x["cle"] in BZH and not x["mot"].get("bzh"):
            x["mot"]["bzh"] = BZH[x["cle"]]
            n += 1
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(n, "termes complétés")
