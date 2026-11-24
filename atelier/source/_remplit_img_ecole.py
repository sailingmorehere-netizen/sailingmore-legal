import json,collections
F='projets/sailingmore/site/stages-proches.json'
raw=open(F).read()
d=json.loads(raw)
by=collections.defaultdict(collections.Counter)
for o in d['o']:
    if o[11]: by[o[4]][o[11]]+=1
n=0
for o in d['o']:
    if not o[11] and by[o[4]]:
        o[11]=by[o[4]].most_common(1)[0][0]; n+=1
sep=(',',':') if ', ' not in raw[:200] and ': ' not in raw[:200] else None
json.dump(d,open(F,'w'),ensure_ascii=False,separators=sep)
print('remplis',n)
