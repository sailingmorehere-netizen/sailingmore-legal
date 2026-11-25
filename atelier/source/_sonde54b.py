import json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, os.path.join(R, "scripts", "etude_six_langues.py")], stdout=subprocess.DEVNULL)
d = json.load(open(os.path.join(R, "sortie-test", "etude-six-langues.json")))
for p in d["pages"]:
    t = p["tete"]
    print(p["page"], p["octets"], "lang=%s" % t["lang"], "hl=%s" % t["hreflang"], "data-t=%s" % p["data_t_elements"],
          "data-l=%s" % sum(p["data_l"].values()), "tables=%s" % len(p["tables"]), "sansjs=%s" % p["sans_js"]["mots_visibles"],
          "titreJS=%s" % t["script_titre_langue"])
