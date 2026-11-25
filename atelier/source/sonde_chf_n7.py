#!/usr/bin/env python3
"""Sonde en lecture seule : pour chaque URL, statut, taille, nombre de « CHF » / « Fr. » et liens internes utiles."""
import re
import sys
import urllib.request

URLS = sys.argv[1:] or ["https://www.ecole-de-voile.ch/"]
for u in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=25)
        t = r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        print(u, "ERREUR", e)
        continue
    chf = re.findall(r".{0,60}(?:CHF|Fr\.)\s?\d.{0,30}", t)
    print(u, r.status, len(t), "CHF:", len(chf))
    for c in chf[:6]:
        print("   ", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)))
    liens = sorted(set(re.findall(r'href="([^"#]+)"', t)))
    print("   liens:", len(liens), [l for l in liens if re.search(r"cours|stage|kurs|tarif|prix|preis|price|segel|voile", l, re.I)][:25])
