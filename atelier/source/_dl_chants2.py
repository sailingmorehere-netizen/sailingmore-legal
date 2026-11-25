import os, sys, urllib.request
dest = sys.argv[1]
for i in ("the-shanty-book-part-two", "theshantybookpar20774gut"):
    u = f"https://archive.org/download/{i}/{i}_djvu.txt"
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "lecture"}), timeout=60).read()
        open(os.path.join(dest, i + ".txt"), "wb").write(d)
        print(i, len(d))
    except Exception as e:
        print(i, "ERREUR", e)
