#!/usr/bin/env python3
"""Sonde en lecture seule : état de la mesure de trafic sur sailingmore.fr.
Vérifie : balise google-site-verification, scripts de comptage, robots.txt, sitemap.
Aucune écriture vers l'extérieur (GET uniquement)."""
import re, sys, urllib.request

BASE = "https://sailingmore.fr"

def get(path):
    try:
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "sonde-lecture"})
        r = urllib.request.urlopen(req, timeout=20)
        return r.status, r.read().decode("utf8", "replace")
    except Exception as e:
        return None, "ERREUR " + str(e)

st, html = get("/")
print("accueil", st, len(html), "octets")
print("scripts externes :", re.findall(r'<script[^>]*src="([^"]*)"', html)[:15])
print("meta google-site-verification :", re.findall(r'<meta[^>]*google-site-verification[^>]*>', html))
print("outils de comptage connus :", [k for k in ("googletagmanager", "google-analytics", "gtag(", "matomo", "plausible", "umami", "cloudflareinsights") if k in html])
for p in ("/robots.txt", "/sitemap.xml"):
    st, t = get(p)
    print(p, st, len(t), "octets")
    print("\n".join(t.splitlines()[:8]))
sys.exit(0)
