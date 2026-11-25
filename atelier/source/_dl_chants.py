import os, sys, urllib.request
dest = sys.argv[1]
os.makedirs(dest, exist_ok=True)
ids = {
 "shantybooksailor00terr": "Terry I (1921)",
 "seasongsshanties00whal": "Whall (1920)",
 "musicofwaterscol00smituoft": "Smith (1888)",
}
for i in ids:
    u = f"https://archive.org/download/{i}/{i}_djvu.txt"
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "lecture"}), timeout=60).read()
        open(os.path.join(dest, i + ".txt"), "wb").write(d)
        print(i, len(d))
    except Exception as e:
        print(i, "ERREUR", e)
