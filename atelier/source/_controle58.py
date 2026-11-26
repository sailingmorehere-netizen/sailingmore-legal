import re
from pathlib import Path
S = Path(__file__).resolve().parent.parent / "projets/sailingmore/site"
sm = (S / "sitemap-bateaux.xml").read_text()
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
print("sitemap-bateaux <loc>:", len(locs))
print("sitemap.xml a /bateaux/ :", "<loc>https://sailingmore.fr/bateaux/</loc>" in (S / "sitemap.xml").read_text())
print("robots déclare :", "sitemap-bateaux.xml" in (S / "robots.txt").read_text())
mini = 99
for u in locs:
    p = S / "bateaux" / u.rsplit("/", 1)[1]
    t = p.read_text()
    corps = t.split("</h1>")[1].split("<h2>Cotes</h2>")[0]
    n = len(re.findall(r'<a href="\.\./(?:lexique|cours|regates|regles)[^"]*"', corps))
    mini = min(mini, n)
    if n < 3:
        print("TROP PEU", p.name, n)
print("min liens contextuels par fiche:", mini)
touchees = [p for p in list((S / "lexique").glob("*.html")) + list(S.glob("cours-*.html")) if "<!--fiches-bateaux-->" in p.read_text()]
print("pages avec lien retour:", sorted(p.relative_to(S).as_posix() for p in touchees))
print("liens retour valides:", all((S / m).exists() for p in touchees for m in re.findall(r'href="(?:\.\./)?(bateaux/[^"]+)"', re.search(r"<!--fiches-bateaux-->(.*?)<!--/", p.read_text(), re.S).group(1))))
