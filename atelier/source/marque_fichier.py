#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Écrit la marque DANS le fichier image : EXIF (Artist, Copyright) + IPTC (By-line, Credit, CopyrightNotice) pour les
JPEG, tEXt pour les PNG. Sans ré-encoder les pixels (insertion de segments : aucune perte).

Usage : python3 scripts/marque_fichier.py fichier.jpg [fichier2.png ...]
Importable : marque_fichier.marquer(chemin) -> True si le fichier a été modifié. Idempotent.

Une seule source du texte : scripts/bateaux_page.py (LEGENDE). Pas une protection : une preuve et une ligne de crédit.
"""
from __future__ import annotations

import struct
import sys
from datetime import date
from pathlib import Path

CREDIT = "SailingMore.fr — École de voile en ligne"
URL = "https://sailingmore.fr"


def _copyright() -> str:
    return f"© {date.today().year} {CREDIT}"


def _iptc() -> bytes:
    def ds(num: int, val: str) -> bytes:
        b = val.encode("utf-8")
        return b"\x1c\x02" + bytes([num]) + struct.pack(">H", len(b)) + b
    corps = (b"\x1c\x01\x5a\x00\x03\x1b%G"          # 1:90 jeu de caractères UTF-8
             + ds(80, CREDIT)                         # By-line
             + ds(110, CREDIT)                        # Credit
             + ds(115, CREDIT)                        # Source
             + ds(116, _copyright())                  # CopyrightNotice
             + ds(40, "Source : " + URL))             # SpecialInstructions
    bim = b"8BIM\x04\x04\x00\x00" + struct.pack(">I", len(corps)) + corps
    if len(corps) % 2:
        bim += b"\x00"
    return b"Photoshop 3.0\x00" + bim


def _segment(marqueur: int, charge: bytes) -> bytes:
    return b"\xff" + bytes([marqueur]) + struct.pack(">H", len(charge) + 2) + charge


def _jpeg(data: bytes) -> bytes:
    if data[:2] != b"\xff\xd8":
        raise ValueError("pas un JPEG")
    i, tete = 2, []
    reste_debut = 2
    # garde APP0 (JFIF) en tête, retire nos anciens APP1 Exif / APP13
    while i + 4 <= len(data) and data[i] == 0xFF:
        m = data[i + 1]
        if m == 0xDA or m == 0xD9:
            break
        n = struct.unpack(">H", data[i + 2:i + 4])[0]
        seg = data[i:i + 2 + n]
        charge = seg[4:]
        if m == 0xE1 and charge.startswith(b"Exif\x00\x00"):
            pass
        elif m == 0xED and charge.startswith(b"Photoshop 3.0"):
            pass
        else:
            tete.append(seg)
        i += 2 + n
    reste = data[i:]
    jfif = [s for s in tete if s[1] == 0xE0]
    autres = [s for s in tete if s[1] != 0xE0]
    nouveau = (b"\xff\xd8" + b"".join(jfif)
               + _segment(0xE1, b"Exif\x00\x00" + _exif_tiff())
               + _segment(0xED, _iptc()) + b"".join(autres) + reste)
    return nouveau


def _exif_tiff() -> bytes:
    from PIL import Image
    ex = Image.Exif()
    ex[315] = CREDIT
    ex[33432] = _copyright()
    b = ex.tobytes()
    return b[6:] if b.startswith(b"Exif\x00\x00") else b


def _png(data: bytes) -> bytes:
    import zlib
    sig = data[:8]
    i, morceaux = 8, []
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        brut = data[i:i + 12 + n]
        morceaux.append((typ, brut))
        i += 12 + n

    def itxt(cle: str, val: str) -> bytes:
        ch = cle.encode("latin-1") + b"\x00\x00\x00\x00\x00" + val.encode("utf-8")
        return struct.pack(">I", len(ch)) + b"iTXt" + ch + struct.pack(">I", zlib.crc32(b"iTXt" + ch))

    cles = {"Author": CREDIT, "Copyright": _copyright(), "Source": URL, "Credit": CREDIT}
    mon = b"".join(itxt(k, v) for k, v in cles.items())
    sortie, mis = [sig], False
    for typ, brut in morceaux:
        if typ == b"iTXt" and any(brut[8:8 + len(k) + 1] == k.encode() + b"\x00" for k in cles):
            continue
        sortie.append(brut)
        if typ == b"IHDR" and not mis:
            sortie.append(mon)
            mis = True
    return b"".join(sortie)


def _webp(data: bytes) -> bytes:
    """Insère un chunk EXIF dans le conteneur RIFF, sans ré-encoder l'image (aucune perte)."""
    import io
    from PIL import Image
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("pas un WebP")
    with Image.open(io.BytesIO(data)) as im:
        w, h = im.size
        alpha = "A" in im.getbands()
    i, chunks = 12, []
    while i + 8 <= len(data):
        typ = data[i:i + 4]
        n = struct.unpack("<I", data[i + 4:i + 8])[0]
        chunks.append((typ, data[i + 8:i + 8 + n]))
        i += 8 + n + (n & 1)
    chunks = [c for c in chunks if c[0] != b"EXIF"]
    if chunks and chunks[0][0] == b"VP8X":
        fl = bytearray(chunks[0][1])
        fl[0] |= 0x08
        chunks[0] = (b"VP8X", bytes(fl))
    else:
        fl = 0x08 | (0x10 if alpha else 0)
        chunks.insert(0, (b"VP8X", bytes([fl, 0, 0, 0]) + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")))
    chunks.append((b"EXIF", _exif_tiff()))
    corps = b"".join(t + struct.pack("<I", len(c)) + c + (b"\x00" if len(c) & 1 else b"") for t, c in chunks)
    return b"RIFF" + struct.pack("<I", 4 + len(corps)) + b"WEBP" + corps


def marquer(chemin) -> bool:
    p = Path(chemin)
    data = p.read_bytes()
    suf = p.suffix.lower()
    if suf in (".jpg", ".jpeg"):
        neuf = _jpeg(data)
    elif suf == ".png":
        neuf = _png(data)
    elif suf == ".webp":
        neuf = _webp(data)
    else:
        return False
    if neuf == data:
        return False
    p.write_bytes(neuf)
    return True


def images_a_nous() -> list[Path]:
    """Les images que SailingMore produit elle-même. Exclus : stages-img (photos des écoles de voile, pas à nous),
    drapeaux, favicons/icônes, img/vr-inshore.png (logo d'un tiers)."""
    site = Path(__file__).resolve().parent.parent / "projets" / "sailingmore" / "site"
    out = [site / "og-image.jpg", site / "carte-monde.png"]
    out += sorted((site / "stories").rglob("*.jpg")) + sorted((site / "reels").glob("*.jpg"))
    out += sorted((site / "images").rglob("*.webp")) if (site / "images").exists() else []
    return [p for p in out if p.exists()]


if __name__ == "__main__":
    n = 0
    cibles = images_a_nous() if "--site" in sys.argv else sys.argv[1:]
    for a in cibles:
        if str(a).startswith("--"):
            continue
        n += marquer(a)
    print(f"{n} fichier(s) marqué(s)")
