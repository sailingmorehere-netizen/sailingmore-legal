import json, re
d = json.load(open('projets/sailingmore/site/stages-proches.json', encoding='utf-8'))
pref = ["rya day skipper motor", "rya coastal skipper motor", "rya motor boat coastal skipper",
        "sbt yachtmaster coastal coc prep for motor", "sbt yachtmaster offshore coc prep for motor",
        "rya powerboat instructors course", "powerboat instructor skills", "rya powerboat instructor",
        "rya pwc instructor course"]
seen = {}
for x in d['o']:
    t = x[3] or ''
    if any(t.casefold().startswith(p) for p in pref):
        urls = [v for v in x if isinstance(v, str) and v.startswith('http')]
        seen.setdefault(t, (x[13] if len(x) > 13 else None, urls[:1]))
for t, v in seen.items():
    print(t, '|', v)
