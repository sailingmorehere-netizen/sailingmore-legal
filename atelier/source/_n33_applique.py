"""Tâche 33 : debut/fin lus sur les pages (cache tmp_n33 = texte des pages, lecture seule), première session à venir
PUBLIÉE (>= 26/11/2026), prise telle quelle sur la page de l'offre ; jamais déduite. `fin` seulement si la page
donne une plage. Écoles à calendrier lisible uniquement."""
import json, re, sys, datetime as dt
AUJ = dt.date(2026, 11, 27)  # la publication se fait le matin : une session d'aujourd'hui sera passée
F = 'projets/sailingmore/stages.json'
MEN = {m: i + 1 for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split())}
MDE = {'januar': 1, 'februar': 2, 'märz': 3, 'april': 4, 'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
       'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12}
MOIS_EN = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
MOIS_DE = r'(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)'


def texte(u):
    return open('tmp_n33/' + re.sub(r'\W+', '_', u)[:120] + '.txt').read()


def dd(y, m, j):
    try:
        return dt.date(int(y), int(m), int(j))
    except ValueError:
        return None


def fin_ok(a, b):
    return b if (a and b and b >= a) else None


def en(t, ancre=None, fen=700):
    """BH Marine / Urban Truant : '4–5 Mar 2027', '30 November 2026 – 4 December 2026', '3 December 2026'."""
    if ancre:
        i = t.lower().find(ancre.lower())
        if i < 0:
            return []
        t = t[i:i + fen]
    p = re.compile(r'(\d{1,2})(?:st|nd|rd|th)? (' + MOIS_EN + r') (\d{4}) ?[–-] ?(\d{1,2})(?:st|nd|rd|th)? (' + MOIS_EN + r') (\d{4})'
                   r'|(\d{1,2}) ?[–-] ?(\d{1,2}) (' + MOIS_EN + r') (\d{4})'
                   r'|(\d{1,2})(?:st|nd|rd|th)? (' + MOIS_EN + r') (\d{4})')
    out = []
    for m in p.finditer(t):
        if m[1]:
            a = dd(m[3], MEN[m[2][:3].lower()], m[1]); b = dd(m[6], MEN[m[5][:3].lower()], m[4])
        elif m[7]:
            mo = MEN[m[9][:3].lower()]
            a = dd(m[10], mo, m[7]); b = dd(m[10], mo, m[8])
        else:
            a = dd(m[13], MEN[m[12][:3].lower()], m[11]); b = None
        out.append((a, fin_ok(a, b)))
    return out


def de_num(t, ancre=None, fen=900):
    """Schluchsee / Grosse Freiheit / Weber : 'Sa, 22.05.2027 – 23.05.', '06./07.02.2027', '12. - 14.02.2027', '26.11.2026'."""
    if ancre:
        i = t.find(ancre)
        if i < 0:
            return []
        t = t[i:i + fen]
    p = re.compile(r'(\d{1,2})\.(\d{1,2})\.(\d{4}) ?[–-] ?(\d{1,2})\.(\d{1,2})\.(?!\d)'
                   r'|(\d{1,2})\.(?:(\d{1,2})\.)? ?[/–-] ?(\d{1,2})\.(?:(\d{1,2})\.)? ?(\d{4})'
                   r'|(\d{1,2})\.(\d{1,2})\.(\d{4})')
    out = []
    for m in p.finditer(t):
        prec = t[max(0, m.start() - 3):m.start()]
        if re.search(r'[–-] ?$|/$', prec):
            continue  # seconde moitié d'une plage que le motif n'a pas su lire
        if m[1]:
            a = dd(m[3], m[2], m[1]); b = dd(m[3], m[5], m[4])
            if a and b and b < a:
                b = dd(int(m[3]) + 1, m[5], m[4])
        elif m[6]:
            y = m[10]; m2 = m[9]; m1 = m[7] or m2
            a = dd(y, m1, m[6]); b = dd(y, m2, m[8])
        else:
            a = dd(m[13], m[12], m[11]); b = None
        out.append((a, fin_ok(a, b)))
    return out


def de_mois(t):
    """Reichenau : 'Sa/So 20./21. März 2027', 'Sa 19. - Mo 21. Juni 2027', 'Sa 31. Juli - Mo 02. August 2027', 'Sonntag 21. März 2027'."""
    p = re.compile(r'(\d{1,2})\.(?: ?/ ?(\d{1,2})\.)? (' + MOIS_DE + r') (\d{4})'
                   r'|(\d{1,2})\. (?:- )?(?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\. (' + MOIS_DE + r') (\d{4})')
    p2 = re.compile(r'(?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\. - (?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\. (' + MOIS_DE + r') (\d{4})')
    p3 = re.compile(r'(?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\. (' + MOIS_DE + r') - (?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\. (' + MOIS_DE + r') (\d{4})')
    out = []
    for m in p3.finditer(t):
        out.append((dd(m[5], MDE[m[2].lower()], m[1]), dd(m[5], MDE[m[4].lower()], m[3])))
    t2 = p3.sub(' ', t)
    for m in p2.finditer(t2):
        mo = MDE[m[3].lower()]
        out.append((dd(m[4], mo, m[1]), dd(m[4], mo, m[2])))
    t2 = p2.sub(' ', t2)
    for m in p.finditer(t2):
        if m[1]:
            mo = MDE[m[3].lower()]
            out.append((dd(m[4], mo, m[1]), dd(m[4], mo, m[2]) if m[2] else None))
    return [(a, fin_ok(a, b)) for a, b in out]


def titre_xp(titre, t):
    m = re.search(r'(\d{1,2})-(\d{1,2}) (' + MOIS_EN + r') (\d{4})', titre)
    if m:
        mo = MEN[m[3][:3].lower()]
        return [(dd(m[4], mo, m[1]), dd(m[4], mo, m[2]))]
    return []


def slash(t, motif):
    out = []
    for m in re.finditer(motif, t):
        g = m.groups()
        a = dd(g[2], g[1], g[0])
        b = dd(g[5], g[4], g[3]) if len(g) >= 6 else None
        if len(g) >= 6 and not (a and b and b >= a):
            continue  # plage incohérente sur la page (ex. « du 02/02/2027 au 15/01/2027 ») : non retenue
        out.append((a, fin_ok(a, b)))
    return out


def lagoo(t):
    out = []
    for m in re.finditer(r'(2026|2027): (\d{1,2})\. - (\d{1,2})\. (' + MOIS_DE + r')', t):
        mo = MDE[m[4].lower()]
        out.append((dd(m[1], mo, m[2]), dd(m[1], mo, m[3])))
    for m in re.finditer(r'(2026|2027): (\d{1,2})\. (' + MOIS_DE + r') - (\d{1,2})\. (' + MOIS_DE + r')', t):
        out.append((dd(m[1], MDE[m[3].lower()], m[2]), dd(m[1], MDE[m[5].lower()], m[4])))
    return [(a, fin_ok(a, b)) for a, b in out]


ECOLES = {
    'Sailway': lambda e, t: slash(t, r'Próxima salida: (\d\d)/(\d\d)/(\d{4})'),
    'Vent du Large': lambda e, t: slash(t, r'Du (\d\d)/(\d\d)/(\d{4}) au (\d\d)/(\d\d)/(\d{4})'),
    'Ultra Sailing': lambda e, t: slash(t, r'From (\d\d)\.(\d\d)\.(\d{4})\. until (\d\d)\.(\d\d)\.(\d{4})'),
    'Lagoo Segelschule Zürich': lambda e, t: lagoo(t),
    'BH Marine': lambda e, t: en(t, 'UPCOMING PRACTICAL COURSE DATES'),
    'Urban Truant': lambda e, t: en(t, 'Upcoming course dates'),
    'Segelschule Schluchsee': lambda e, t: de_num(t, 'Nächste Termine'),
    'Segelschule Grosse Freiheit': lambda e, t: de_num(t, 'Bitte wählen') or de_num(t, 'Kursplan', 3000),
    'Segelschule Weber': lambda e, t: de_num(t, None),
    'Segelschule Insel Reichenau': lambda e, t: de_mois(next((t[t.find(a):] for a in ('Terminblock', 'Termine Hochrhein', 'Termine') if a in t), t)),
    'Sailing Xperience': lambda e, t: titre_xp(e['titre'], t),
}

if __name__ == '__main__':
    ecoles = sys.argv[2:] or list(ECOLES)
    ecrire = sys.argv[1] == 'ecrire'
    d = json.load(open(F, encoding='utf-8'))
    n = 0
    for e in d['offres']:
        if e['ecole'] not in ecoles or e.get('debut') or not e['lien']:
            continue
        try:
            t = texte(e['lien'])
        except OSError:
            continue
        c = [x for x in ECOLES[e['ecole']](e, t) if x[0] and x[0] >= AUJ]
        if not c:
            continue
        a, b = min(c, key=lambda x: x[0])
        print(e['ecole'][:14], a, b, '|', e['titre'][:45])
        if ecrire:
            e['debut'] = a.isoformat()
            if b:
                e['fin'] = b.isoformat()
                e['duree_jours'] = (b - a).days + 1
        n += 1
    print('offres datées', n)
    if ecrire:
        json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
