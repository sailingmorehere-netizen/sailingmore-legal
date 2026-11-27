import re,json,subprocess,concurrent.futures as cf
d=json.load(open('projets/sailingmore/stages.json'))
k=[e for e in d['offres'] if not e.get('debut') and not e.get('hors_offre')]
RX=re.compile(r'20(26|27)-\d\d-\d\d|\d{1,2}[./]\d{1,2}[./]20(26|27)|\d{1,2}(?:st|nd|rd|th)? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* 20(?:26|27)|\d{1,2} (?:janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc)\w* 20(?:26|27)')
def f(e):
    h=subprocess.run(['curl','-sL','-m','25',e['lien']],capture_output=True).stdout.decode('utf-8','replace')
    h=re.sub(r'(?s)<(script|style).*?</\1>',' ',h)
    t=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',h))
    return [m.group(0) for m in RX.finditer(t)][:12]
with cf.ThreadPoolExecutor(12) as ex: r=list(ex.map(f,k))
out=[{'lien':e['lien'],'slug':e['ecole_slug'],'titre':e['titre'],'d':x} for e,x in zip(k,r)]
json.dump(out,open('scan.json','w'),ensure_ascii=False)
import collections
c=collections.Counter(o['slug'] for o in out if o['d'])
print(len(out),sum(1 for o in out if o['d']),c.most_common(20))
