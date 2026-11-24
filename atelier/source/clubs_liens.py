"""Lien automatique club -> fiche. UNE seule fonction de détection, à appeler partout (pages, articles, régates, stages).

    from clubs_liens import charger, lier
    idx = charger('projets/clubs-monde/clubs.json')
    html_sortie = lier(texte_html, idx)

Règles : jamais sur un nom de ville seul ; jamais si deux clubs portent la même forme (ambigu) ;
jamais vers un club « moteur » ni « à préciser » ; jamais dans une balise ni dans un lien existant.
"""
import json, re, unicodedata

def pli(s):
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()

def charger(chemin):
    clubs = json.load(open(chemin, encoding='utf-8'))
    formes = {}
    for c in clubs:
        if not c.get('fiche') or c['activite'] not in ('voile', 'les deux'):
            continue
        for f in [c['nom']] + c.get('variantes', []):
            if len(f) < 3:      # variante explicite (sigle) d'au moins 3 caractères
                continue
            formes.setdefault(pli(f), set()).add(c['id'])
    # forme ambiguë (plusieurs clubs) = exclue
    par_id = {c['id']: c for c in clubs}
    sure = {f: next(iter(ids)) for f, ids in formes.items() if len(ids) == 1}
    if not sure:
        return None
    motif = re.compile(r'(?<![\w])(' + '|'.join(re.escape(f) for f in sorted(sure, key=len, reverse=True)) + r')(?![\w])')
    return {'sure': sure, 'motif': motif, 'clubs': par_id}

def lier(texte, idx):
    """Relie les noms de clubs dans un fragment HTML. Une seule occurrence par club et par appel."""
    if not idx:
        return texte
    deja = set()
    sortie = []
    # on découpe en balises / texte ; on ne touche pas au texte dans <a>, <script>, <style>
    profondeur = 0
    for morceau in re.split(r'(<[^>]+>)', texte):
        if morceau.startswith('<'):
            bas = morceau.lower()
            if re.match(r'<(a|script|style)\b', bas): profondeur += 1
            elif re.match(r'</(a|script|style)>', bas): profondeur = max(0, profondeur - 1)
            sortie.append(morceau); continue
        if profondeur:
            sortie.append(morceau); continue
        # la recherche se fait sur le texte sans accents, de même longueur (NFD ascii casse la longueur : on aligne caractère par caractère)
        plat = ''.join(pli(ch) or ch for ch in morceau)
        if len(plat) != len(morceau):
            sortie.append(morceau); continue
        out, pos = [], 0
        for m in idx['motif'].finditer(plat):
            cid = idx['sure'][m.group(1)]
            if cid in deja: continue
            deja.add(cid)
            out.append(morceau[pos:m.start()])
            out.append('<a href="/clubs/%s.html">%s</a>' % (cid, morceau[m.start():m.end()]))
            pos = m.end()
        out.append(morceau[pos:])
        sortie.append(''.join(out))
    return ''.join(sortie)

if __name__ == '__main__':   # auto-test : python3 scripts/clubs_liens.py
    import tempfile, os
    jeu = [
        {'id': 'yacht-club-de-monaco', 'nom': 'Yacht Club de Monaco', 'variantes': ['YCM'], 'activite': 'voile', 'fiche': True},
        {'id': 'moteur-x', 'nom': 'Yacht Club Moteur X', 'variantes': [], 'activite': 'moteur', 'fiche': True},
        {'id': 'cn-1', 'nom': 'Cercle Nautique Rolle', 'variantes': [], 'activite': 'voile', 'fiche': True},
        {'id': 'cn-2', 'nom': 'Cercle Nautique Rolle', 'variantes': [], 'activite': 'voile', 'fiche': True},
    ]
    p = os.path.join(tempfile.mkdtemp(), 'c.json'); json.dump(jeu, open(p, 'w'))
    i = charger(p)
    assert 'href="/clubs/yacht-club-de-monaco.html"' in lier('Régate au Yacht Club de Monaco.', i)
    assert 'href' in lier('Le YCM organise.', i)
    assert 'href' not in lier('Un hiver à Monaco.', i)
    assert 'href' not in lier('Yacht Club Moteur X et voile', i)
    assert 'href' not in lier('Cercle Nautique Rolle', i)
    assert lier('<a href="/x">Yacht Club de Monaco</a>', i).count('<a ') == 1
    print('liens : 6 tests ok')
