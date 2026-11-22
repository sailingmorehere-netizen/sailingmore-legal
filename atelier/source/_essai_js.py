"""Essai : extrait les <script> des pages de sortie-test/ et les passe à `node --check` si node existe."""
import re, shutil, subprocess, sys
from pathlib import Path
ici = Path(__file__).resolve().parent.parent
node = shutil.which("node")
print("node:", node)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import carte_epreuves as C
print("poids de la brique : JS", len(C.js().encode()), "CSS", len(C.CSS.encode()), "HTML", len(C.html().encode()), "octets")
for n in ("regates", "stages"):
    h = (ici / "sortie-test" / f"{n}.html").read_text(encoding="utf-8")
    for i, m in enumerate(re.finditer(r"<script(?![^>]*json)[^>]*>(.*?)</script>", h, re.S)):
        f = ici / "sortie-test" / f"_{n}{i}.js"
        f.write_text(m.group(1), encoding="utf-8")
        if node:
            r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
            print(n, i, "OK" if r.returncode == 0 else r.stderr[:600])
