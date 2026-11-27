import re, urllib.request
r = urllib.request.Request('https://uksa.org/courses/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    h = urllib.request.urlopen(r, timeout=30).read().decode('utf-8', 'replace')
except Exception as e:
    print('ERREUR', e)
    raise SystemExit
open('/opt/data/cache/claude-nuit/travail/scripts/_uksa_courses.html', 'w', encoding='utf-8').write(h)
print(len(h))
print(sorted(set(re.findall(r'20\d\d-\d\d-\d\d|\d{1,2}(?:st|nd|rd|th)? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* 20\d\d', h)))[:30])
print(sorted(set(re.findall(r'href="([^"]*uksa\.org/[^"]*)"', h)))[:40])
