import urllib.request, time, sys
UA = {"User-Agent": "Mozilla/5.0 (compatible; SailingMore/1.0; +https://sailingmore.fr)"}
for u in sys.argv[1:]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25)
        b = r.read(3000).decode("utf-8", "ignore")
        print("==", u, r.status, r.geturl(), r.headers.get("content-type"))
        print(b[:500].replace("\n", " "))
    except Exception as e:
        print("==", u, "ERR", e)
    time.sleep(3)
