import re, subprocess, html, sys
U = {153: 'https://segelschule-insel-reichenau.de/kurse/', 156: 'https://segelschule-insel-reichenau.de/kurse/grundkurs/',
     155: 'https://segelschule-insel-reichenau.de/kurse/segelschein/bodenseeschifferpatent-kat-d-segel/',
     106: 'https://lagoo.ch/collections/segelkurse-zurichsee-vom-grundkurs-bis-segelschein-kat-d',
     107: 'https://ecoledecroisiereslowlife.com/stage-voile-hauturier', 110: 'https://ecoledecroisiereslowlife.com/stage-decouverte',
     194: 'https://segelschule-schluchsee.de/segel-kurse-scheine/', 152: 'https://segelschule-rehbach.de/segelkurse/',
     150: 'https://www.rcmarsc.es/escuela-de-vela', 253: 'https://solentsail.com/sailing_trips/', 380: 'https://www.windzone.es/inicio/campamentos/',
     197: 'https://www.scuolavela.com/it/scuola-vela/corsi-cabinati/', 198: 'https://www.scuolavela.com/it/scuola-vela/corsi-derive/'}
for i, u in U.items():
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    print(i, u)
    for x in list(re.finditer(r'(?i)(preis|kosten|prix|tarif|prezzo|precio|price|CHF|Fr\.|\d\s?,-|\d\s?\.-)', t))[:4]:
        print('    ', t[max(0, x.start() - 50):x.end() + 50])
