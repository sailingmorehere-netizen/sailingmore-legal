import re, sys, urllib.request
for u in sys.argv[1:]:
    t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8', 'replace')
    print('##', u, len(t))
    for h in sorted(set(re.findall(r'href="([^"]*(?:date|calendar|schedule|availab|booking)[^"]*)"', t, re.I)))[:12]:
        print('  ', h)
