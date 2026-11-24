"""Lit des URL (3 s entre deux), range le corps dans cache/moisson62/, affiche statut et taille.
python3 scripts/_prend62.py nom=URL [nom=URL ...]"""
import os, sys, time, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (compatible; SailingMore/1.0; +https://sailingmore.fr)"}
os.makedirs("cache/moisson62", exist_ok=True)
for a in sys.argv[1:]:
    nom, u = a.split("=", 1)
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40)
        b = r.read()
        open(f"cache/moisson62/{nom}", "wb").write(b)
        print(nom, r.status, len(b), r.geturl())
    except Exception as e:
        print(nom, "ERR", e)
    time.sleep(3)
