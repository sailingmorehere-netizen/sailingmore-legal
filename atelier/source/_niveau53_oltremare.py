import subprocess, re, html
u = 'https://www.oltremare.it/percorso-didattico-scuola-di-vela-2/'
for args in (['-sL'], ['-sL', '--compressed', '-H', 'Accept: text/html', '-H', 'Accept-Language: it']):
    r = subprocess.run(['curl', *args, '--max-time', '20', '-A', 'Mozilla/5.0 (X11; Linux x86_64)', u], capture_output=True, timeout=30)
    b = r.stdout.decode('utf-8', 'ignore')
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b))))
    print(len(b), len(t), t[300:3300])
    break
