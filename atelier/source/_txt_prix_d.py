import re, subprocess, html, sys
# usage: url motclef longueur
u, k, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
t = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('utf-8', 'replace')
t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t)); t = re.sub(r'\s+', ' ', t)
i = t.find(k)
print(t[i:i + n])
