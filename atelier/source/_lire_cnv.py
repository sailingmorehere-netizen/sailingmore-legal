import re, subprocess
for p in ['optimist', 'optimist-decouverte', 'parents-enfants', 'rs-feva', 'ado', 'adultes']:
    h = subprocess.run(['curl', '-sL', '-m', '20', 'https://www.cnv.ch/stages-voile/' + p],
                       capture_output=True, text=True).stdout
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))
    i = t.find('Rejoignez le club')
    print('===', p)
    print(t[i + 200:i + 2600])
