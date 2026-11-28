# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 52 : marque hors_offre les pages d'information (hubs, présentation, théorie, entreprise...)
sans prix, sans date de début. Ne supprime rien. Indices = positions dans stages.json."""
import json
R = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
raw = open(R, encoding='utf-8').read()
d = json.loads(raw)
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
IDX = set("""22 27 31 35 42 46 49 50 51 54 55 56 57 59 78 79 84 85 86 87 88 91 92 94 99 102 104
111 113 114 117 119 122 124 128 140 147 148 149 150 151 152 153 155 158 164 166 167 168 174 211
204 205 206 212 213 214 215 216 220 221 222 223 226 272
274 275 276 277 278 279 281 282 283 284 285 286 287 288 295 298 302 306 308 309 310 312 313
315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 335 336 338 339
340 342 356 358 359 375 376 377 380 381 382 383 384 385 399 400 401 403""".split())
n = 0
for i in map(int, IDX):
    x = L[i]
    if x.get('prix_eur') or x.get('debut') or x.get('hors_offre'):
        print('ignoré', i, x.get('titre'))
        continue
    x['hors_offre'] = True
    x['hors_offre_motif'] = "page d'information (pas de prix, pas de date, pas d'inscription)"
    n += 1
json.dump(d, open(R, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('marquées', n)
