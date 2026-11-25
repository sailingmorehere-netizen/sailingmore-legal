#!/usr/bin/env python3
"""Retiré le 25/11/2026 (règle 7) : ce script écrivait sitemap.xml en parallèle de `sitemap_site.py`.
Seul `scripts/sitemap_site.py` écrit le sitemap ; il conserve les blocs `image:image` déjà posés.
Les 10 images (accueil + bateaux) sont déjà dans site/sitemap.xml."""
import sys

print("sitemap_images_accueil.py n'écrit plus rien : voir scripts/sitemap_site.py")
sys.exit(0)
