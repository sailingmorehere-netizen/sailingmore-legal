import json, re
L = json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
rx = re.compile(r'(20\d\d-\d\d-\d\d|\d{1,2}(st|nd|rd|th)?[\s\-–]+(\d{1,2}\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+20\d\d|\d{1,2}[./]\d{1,2}[./]20\d\d)', re.I)
n = 0
for o in L:
    if not o[7]:
        m = rx.search(o[3]) or rx.search(o[10])
        if m:
            n += 1; print(o[4], '|', o[3][:80], '|', m.group(0))
print(n)
