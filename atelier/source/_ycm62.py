import json, re, html
from datetime import datetime, timezone, timedelta
h = open("cache/moisson62/ycm_events.html", encoding="utf-8", errors="ignore").read()
parts = re.split(r'(?=<div id="event_\d+_\d+" class="eventon_list_event)', h)[1:]
out = []
for p in parts:
    p = p[:6000]
    t = re.search(r'data-time="(\d+)-(\d+)"', p)
    l = re.search(r'evo_event_schema[^>]*><a href="([^"]+)"', p)
    n = re.search(r'evcal_event_title[^>]*>([^<]+)<', p)
    c = re.search(r'event_type[^"]*"[^>]*>([^<]*)', p)
    d0 = datetime.fromtimestamp(int(t.group(1)), timezone(timedelta(hours=1))).date().isoformat() if t else ""
    d1 = datetime.fromtimestamp(int(t.group(2)), timezone(timedelta(hours=1))).date().isoformat() if t else ""
    out.append({"debut": d0, "fin": d1, "lien": l.group(1) if l else "", "nom": html.unescape(n.group(1)).strip() if n else ""})
print(len(out))
for o in out:
    print(o["debut"], o["fin"], o["nom"], "|", o["lien"])
json.dump(out, open("cache/moisson62/ycm_liste.json", "w"), ensure_ascii=False, indent=1)
