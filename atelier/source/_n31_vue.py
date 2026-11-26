import json, collections
r = json.load(open('scripts/_n31_scan.json'))
seen = collections.Counter()
for k, v in r.items():
    if v and v != 'ERR':
        e = k.split('|')[0]
        seen[e] += 1
        if seen[e] <= 2:
            print(e, '|', k.split('|', 1)[1][:40], '|', len(v), v[:4])
