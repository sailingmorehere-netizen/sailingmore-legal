import sys
for p in ('scripts/stages_page.py', 'projets/sailingmore/site/stages.html'):
    s = open(p, encoding='utf-8').read()
    a = "function cmpId(o){return o.lien||o.titre}"
    b = "function cmpId(o){return [o.ecole_slug,o.lien,o.titre,o.debut||''].join('|')}"
    assert s.count(a) == 1, p
    s = s.replace(a, b)
    s = s.replace("= {v:1, ids:[lien de l'offre,…], maj:ms}.\n   On range le lien de l'offre, pas son rang",
                  "= {v:1, ids:[école|lien|titre|début,…], maj:ms}.\n   On range l'identité de l'offre (le lien seul ne suffit pas : 725 offres, 531 liens), pas son rang")
    open(p, 'w', encoding='utf-8').write(s)
print('ok')
