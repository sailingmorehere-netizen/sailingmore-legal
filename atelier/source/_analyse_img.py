import json, collections, os, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
o = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
print([x[11] for x in o if x[11]][:3])
ok = {x[4] for x in o if x[11]}
seen = set()
for x in o:
    if not x[11] and x[4] not in ok and x[4] not in seen:
        seen.add(x[4]); print(x[4], x[10])
for x in o[:400]:
    if x[11]:
        u = x[10]
        print(x[11], hashlib.sha256(u.encode()).hexdigest()[:16], hashlib.md5(u.encode()).hexdigest()[:16], hashlib.sha1(u.encode()).hexdigest()[:16]); break
