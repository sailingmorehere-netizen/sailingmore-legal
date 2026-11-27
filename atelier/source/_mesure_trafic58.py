"""Lecture seule : DNS public + page d'accueil de sailingmore.fr (tâche 58)."""
import re, subprocess, urllib.request

for t in ("NS", "TXT", "MX", "A"):
    try:
        r = subprocess.run(["dig", "+short", t, "sailingmore.fr"], capture_output=True, text=True, timeout=15)
        print("==", t, "\n" + (r.stdout.strip() or r.stderr.strip() or "(vide)"))
    except Exception as e:
        print("==", t, "dig indisponible:", e)

req = urllib.request.Request("https://sailingmore.fr/", headers={"User-Agent": "controle-lecture"})
with urllib.request.urlopen(req, timeout=20) as r:
    print("== en-têtes", r.status, {k: v for k, v in r.headers.items() if k.lower() in ("server", "x-powered-by", "content-encoding")})
    h = r.read().decode("utf-8", "replace")
print("scripts externes:", sorted(set(re.findall(r'<script[^>]*src="([^"]*)"', h))))
print("compteurs connus:", [k for k in ("gtag", "googletagmanager", "plausible", "matomo", "google-site-verification") if k in h])
