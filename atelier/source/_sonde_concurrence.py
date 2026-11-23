import re, urllib.request
for u in ["https://www.click-and-boat.com/", "https://www.sailogy.com/", "https://www.windy.com/", "https://www.meteoblue.com/", "https://www.navily.com/"]:
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "mesure-site"}), timeout=20) as f:
            b = f.read().decode("utf-8", "replace"); st = f.status; fin = f.geturl()
    except Exception as e:
        print(u, "ERREUR", str(e)[:60]); continue
    hl = re.findall(r'<link[^>]+hreflang="([^"]+)"[^>]*href="([^"]+)"|<link[^>]+href="([^"]+)"[^>]+hreflang="([^"]+)"', b)
    print(u, st, fin, "octets", len(b), "hreflang", len(hl), [(h[0] or h[3], h[1] or h[2]) for h in hl][:8])
