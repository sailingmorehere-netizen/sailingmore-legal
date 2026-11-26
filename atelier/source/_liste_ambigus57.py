import json, collections
B = '/opt/data/cache/claude-nuit/travail/'
R = json.load(open(B + 'projets/sailingmore/regates.json', encoding='utf-8'))['regates']
sans = [r for r in R if r.get('lien') in (None, '', [])]
cl = collections.Counter(r['club'] for r in sans)
with open(B + 'claude/liens-regates-clubs-a-arbitrer.md', 'w', encoding='utf-8') as f:
    f.write('# Clubs des régates sans lien (tâche 57) — %d régates, %d clubs\n\n' % (len(sans), len(cl)))
    f.write('Aucun n\'est dans regates-clubs.json (qui ne contient que 8 événements du Yacht Club de Monaco). À arbitrer : fournir un annuaire club -> site.\n\n')
    for k, n in cl.most_common():
        f.write('- %s : %d\n' % (k, n))
print(len(sans), len(cl))
