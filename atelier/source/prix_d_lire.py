# © 2026 Sailing More — tous droits réservés. All rights reserved.
import re,sys,urllib.request,subprocess
for ligne in open(sys.argv[1]):
    p=ligne.split(' ')
    i,u=p[0],p[-1].strip()
    if not u.startswith('http'): continue
    try:
        h=subprocess.run(['curl','-sL','--max-time','20','-A','Mozilla/5.0',u],capture_output=True).stdout.decode('utf8','ignore')
    except Exception as e:
        print(i,'ERR',e); continue
    t=re.sub(r'<(script|style)[^>]*>.*?</\1>','',h,flags=re.S)
    t=re.sub(r'<[^>]+>',' ',t); t=re.sub(r'\s+',' ',t)
    m=[t[max(0,x.start()-50):x.end()+20] for x in re.finditer(r'(€\s?\d|\d[\d.,]*\s?(€|EUR|Euro|CHF|Fr\.))',t)][:5]
    print(i,u,len(h)); [print('   ',s) for s in m]
