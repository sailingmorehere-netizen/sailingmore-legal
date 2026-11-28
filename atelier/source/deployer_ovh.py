#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Dépose un dossier de site chez OVHcloud (hébergement Pro, FTP).

Un seul chemin de sortie : ce script est le seul à écrire dans l'hébergement.

    python3 scripts/deployer_ovh.py --source <dossier> --essai     # montre ce qui partirait
    python3 scripts/deployer_ovh.py --source <dossier> --publie    # envoie vraiment
    python3 scripts/deployer_ovh.py --source <dossier> --publie --verifie   # envoie puis relit

Ce qu'il fait, et pourquoi :
- il compare la taille de chaque fichier distant à la locale et saute les identiques,
  donc on peut relancer un envoi interrompu sans tout refaire ;
- chaque fichier envoyé est relu en taille chez OVH ; un écart arrête l'envoi ;
- il n'efface jamais rien sans --supprime (drapeau explicite) ;
- le journal va dans logs/deployer-ovh.log.

Le serveur FTP est ftp.<cluster>.hosting.ovh.net — le nom de cluster seul (cluster130.hosting.ovh.net)
est le serveur web, il ne répond rien sur le port 21. C'est l'erreur qui a coûté une heure le 25/11/2026.
"""
import argparse
import ftplib
import os
import sys
import time
from datetime import datetime, timezone

FICHIER_ACCES = "/opt/data/credentials/ovh-ftp.txt"
JOURNAL = "/opt/data/logs/deployer-ovh.log"
RACINE_DISTANTE_DEFAUT = "/www"


def journal(ligne):
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    with open(JOURNAL, "a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {ligne}\n")


def lire_acces():
    acc = {}
    with open(FICHIER_ACCES) as f:
        for ligne in f:
            ligne = ligne.strip()
            if "=" in ligne:
                k, v = ligne.split("=", 1)
                acc[k] = v
    for cle in ("hote", "utilisateur", "motdepasse"):
        if not acc.get(cle):
            sys.exit(f"{FICHIER_ACCES} : {cle} manquant")
    return acc


def connecte(acc):
    ftp = ftplib.FTP()
    ftp.connect(acc["hote"], 21, timeout=30)
    ftp.login(acc["utilisateur"], acc["motdepasse"])
    ftp.set_pasv(True)
    ftp.voidcmd("TYPE I")
    return ftp


def taille_distante(ftp, chemin):
    try:
        return ftp.size(chemin)
    except Exception:
        return None


def cree_dossier(ftp, chemin):
    parties = [p for p in chemin.strip("/").split("/") if p]
    courant = ""
    for p in parties:
        courant += "/" + p
        try:
            ftp.cwd(courant)
        except ftplib.error_perm:
            ftp.mkd(courant)
            ftp.cwd(courant)


def parcours(source):
    for racine, _dossiers, fichiers in os.walk(source):
        for nom in sorted(fichiers):
            chemin = os.path.join(racine, nom)
            relatif = os.path.relpath(chemin, source).replace(os.sep, "/")
            yield chemin, relatif


def liste_distante(ftp, racine, prefixe=""):
    """Tous les fichiers du serveur sous `racine` (chemins relatifs à `racine`).

    Le 27/11/2026, `--supprime` était déclaré mais jamais appliqué : un `ports.sqlite` vide est
    resté servi à la racine du site pendant deux publications. Une option annoncée dans l'aide et
    qui ne fait rien est pire qu'une option absente.
    """
    trouves = []
    a_voir = [(racine, "")]
    while a_voir:
        chemin, relatif = a_voir.pop()
        try:
            entrees = list(ftp.mlsd(chemin))
        except Exception:
            continue
        for nom, faits in entrees:
            if nom in (".", ".."):
                continue
            r = f"{relatif}/{nom}".lstrip("/")
            if faits.get("type") == "dir":
                a_voir.append((f"{chemin}/{nom}", r))
            elif faits.get("type") == "file" and r.startswith(prefixe):
                trouves.append(r)
    return trouves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--distante", default=RACINE_DISTANTE_DEFAUT)
    ap.add_argument("--essai", action="store_true")
    ap.add_argument("--publie", action="store_true")
    ap.add_argument("--verifie", action="store_true", help="relit le site en HTTP après envoi")
    ap.add_argument("--supprime", action="store_true", help="efface en distant ce qui n'est plus en local")
    ap.add_argument("--prefixe", default="", help="n'envoyer que ce chemin (ex. ports/) : évite de relire 15 000 fichiers à chaque envoi")
    ap.add_argument("--force", action="store_true", help="envoyer même si la taille distante est identique (un fichier retouché à taille égale ne partait jamais)")
    args = ap.parse_args()

    if not (args.essai or args.publie):
        sys.exit("choisir --essai ou --publie")
    source = os.path.abspath(args.source)
    if not os.path.isdir(source):
        sys.exit(f"source introuvable : {source}")

    acc = lire_acces()
    ftp = connecte(acc)
    ftp.cwd(args.distante)

    a_envoyer = []
    deja = 0
    total_octets = 0
    for chemin, relatif in parcours(source):
        if args.prefixe and not relatif.startswith(args.prefixe):
            continue
        local = os.path.getsize(chemin)
        distant = taille_distante(ftp, relatif)
        if distant == local and not getattr(args,'force',False):
            deja += 1
            continue
        a_envoyer.append((chemin, relatif, local))
        total_octets += local

    print(f"source      : {source}")
    print(f"déjà à jour : {deja} fichiers")
    print(f"à envoyer   : {len(a_envoyer)} fichiers, {total_octets/1e6:.1f} Mo")
    if args.essai:
        for _c, relatif, taille in a_envoyer[:25]:
            print(f"  {taille/1024:9.0f} Ko  {relatif}")
        if len(a_envoyer) > 25:
            print(f"  … et {len(a_envoyer)-25} autres")
        ftp.quit()
        return

    debut = time.time()
    envoyes = 0
    echecs = []
    for chemin, relatif, taille in a_envoyer:
        dossier = os.path.dirname(relatif)
        if dossier:
            cree_dossier(ftp, f"/{args.distante.strip('/')}/{dossier}")
            ftp.cwd(f"/{args.distante.strip('/')}/{dossier}")
        else:
            ftp.cwd(args.distante)
        nom = os.path.basename(relatif)
        try:
            with open(chemin, "rb") as f:
                ftp.storbinary(f"STOR {nom}", f, blocksize=262144)
            relu = taille_distante(ftp, nom)
            if relu != taille:
                raise RuntimeError(f"taille relue {relu} != {taille}")
            envoyes += 1
            if envoyes % 25 == 0:
                print(f"  {envoyes}/{len(a_envoyer)} envoyés ({time.time()-debut:.0f} s)", flush=True)
        except Exception as e:
            echecs.append((relatif, str(e)))
            print(f"  ÉCHEC {relatif} : {e}", flush=True)
            try:
                ftp = connecte(acc)
                ftp.cwd(args.distante)
            except Exception:
                pass
    ftp.quit()

    duree = time.time() - debut
    print(f"envoyés {envoyes} / {len(a_envoyer)} en {duree:.0f} s, échecs {len(echecs)}")
    journal(f"source={source} envoyés={envoyes} échecs={len(echecs)} durée={duree:.0f}s")
    for relatif, err in echecs[:20]:
        journal(f"  échec {relatif} : {err}")
    if echecs:
        sys.exit(1)

    if args.verifie:
        import urllib.request
        base = f"http://{acc['utilisateur']}.cluster130.hosting.ovh.net/"
        for page in ("", "index.html"):
            try:
                with urllib.request.urlopen(base + page, timeout=20) as r:
                    print(f"HTTP {r.status} {base}{page} ({len(r.read())} octets)")
            except Exception as e:
                print(f"HTTP KO {base}{page} : {e}")

    if args.supprime:
        locaux = {relatif for _c, relatif in parcours(source)
                  if not args.prefixe or relatif.startswith(args.prefixe)}
        ftp = connecte(acc)
        distants = liste_distante(ftp, args.distante, args.prefixe)
        orphelins = [r for r in distants if r not in locaux and not os.path.basename(r).startswith(".")]
        if not orphelins:
            print("rien à effacer en distant")
        for r in orphelins:
            try:
                ftp.delete(f"{args.distante.rstrip('/')}/{r}")
                print(f"  effacé {r}")
                journal(f"  effacé {r}")
            except Exception as e:
                print(f"  ÉCHEC effacement {r} : {e}")
                journal(f"  échec effacement {r} : {e}")
        ftp.quit()
        print(f"effacés {len(orphelins)} fichier(s) qui n'existent plus en local")
        journal(f"suppression demandée : {len(orphelins)} fichier(s)")


if __name__ == "__main__":
    main()
