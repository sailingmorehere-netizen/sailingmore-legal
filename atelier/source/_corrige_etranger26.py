"""Tâche 26 : recale `etranger` sur `pays` dans regates.json (pays != FRA). Usage : python3 _corrige_etranger26.py"""
import json
import os
from pathlib import Path

ICI = Path(os.environ.get("SAILINGMORE_RACINE", str(Path(__file__).resolve().parent.parent)))
f = ICI / "projets/sailingmore/regates.json"
d = json.loads(f.read_text())
n = 0
for e in d["regates"]:
    if e.get("pays"):
        v = e["pays"] != "FRA"
        if e.get("etranger") != v:
            e["etranger"] = v
            n += 1
f.write_text(json.dumps(d, ensure_ascii=False, indent=1))
print(n, "champs etranger corrigés sur", len(d["regates"]))
