import json, re
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
w = [e for e in d['offres'] if not e.get('debut')]
n = 0
for e in w:
    if re.search(r'\d{1,2}[./]\d{1,2}[./]?(20)?\d\d|20(26|27)|\d{1,2} (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', e['titre'], re.I):
        n += 1
        print(e['ecole_slug'], '|', e['titre'][:90])
print(n)
