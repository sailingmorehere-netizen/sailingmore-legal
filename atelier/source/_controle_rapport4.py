import re, json
D = "/opt/data/cache/claude-nuit/travail/"
for p, ident in (("regles-de-course", "donnees-regles"), ("lexique", "donnees-lexique")):
    for nom, f in (("nouvelle", D + "projets/sailingmore/site/" + p + ".html"), ("ligne", D + "sortie-test/enligne-" + p + ".html")):
        h = open(f, encoding="utf-8").read()
        m = re.search(r'<script[^>]*id="%s"[^>]*>(.*?)</script>' % ident, h, re.S)
        j = json.loads(m.group(1))
        n = len(j["regles"]) if "regles" in j else sum(len(t["termes"]) for t in j["themes"])
        sc = re.findall(r"<script>(.*?)</script>", h, re.S)
        print(p, nom, "octets", len(h.encode()), "h3", len(re.findall(r"<h3", h)), "entrees", n, "json", len(m.group(1)),
              "js", sum(len(s) for s in sc), "css", sum(len(s) for s in re.findall(r"<style>(.*?)</style>", h, re.S)),
              "svg", len(re.findall("<svg", h)), "main", len(re.findall("<main", h)), "/main", len(re.findall("</main", h)))
