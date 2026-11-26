import re, subprocess, html
U = {106: 'https://lagoo.ch/collections/segelkurse-zurichsee-vom-grundkurs-bis-segelschein-kat-d',
     155: 'https://segelschule-insel-reichenau.de/kurse/segelschein/bodenseeschifferpatent-kat-d-segel/',
     152: 'https://segelschule-rehbach.de/segelkurse/', 194: 'https://segelschule-schluchsee.de/segel-kurse-scheine/',
     197: 'https://www.scuolavela.com/it/scuola-vela/corsi-cabinati/'}
for i, u in U.items():
    t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    print(i, len(t))
    for x in list(re.finditer(r'(?i)(\d{2,4}\s?(€|eur|chf|fr\b|,-|\.-)|ab\s\d{2,4}|253)', t))[:5]:
        print('    ', t[max(0, x.start() - 60):x.end() + 40])
