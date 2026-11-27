import re, html, urllib.request
for p in ['ado', 'optimist', 'rs-feva', 'adultes', 'parents-enfants']:
    s = urllib.request.urlopen('https://www.cnv.ch/fr/stages-voile/' + p, timeout=20).read().decode('utf-8', 'replace')
    s = re.sub(r'(?s)<(script|style|nav|footer|header).*?</\1>', '', s)
    s = html.unescape(re.sub(r'<[^>]+>', '\n', s))
    l = [x.strip() for x in s.split('\n') if len(x.strip()) > 25]
    print('===', p)
    print('\n'.join(l)[:2000])
