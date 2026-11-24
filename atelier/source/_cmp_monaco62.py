import json, re, unicodedata
def cle(t):
    t = "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", t.lower())
d = json.load(open("projets/sailingmore/regates.json"))["regates"]
print("base", len(d))
for x in d:
    s = " ".join([x["nom"], x["ville"], x["club"]]).lower()
    if x["pays"] == "MON" or "monaco" in s or "montecarlo" in s or "monte-carlo" in s or "monte carlo" in s:
        print(x["debut"], x["fin"], x["pays"], x["nom"], "|", x["ville"], "|", x["club"], "|", x["sources"][:1])
print("--- YCM")
for o in json.load(open("cache/moisson62/ycm_liste.json")):
    print(o["debut"], o["nom"], [x["nom"] for x in d if x["debut"] == o["debut"] and (x["pays"] == "MON" or cle(x["nom"]) == cle(o["nom"]))])
