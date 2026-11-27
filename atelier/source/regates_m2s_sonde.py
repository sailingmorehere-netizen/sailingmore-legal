import re, urllib.request, html as H
UA = {'User-Agent': 'Mozilla/5.0'}
def lit(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode('utf-8', 'ignore')
h = lit('https://www.manage2sail.com/en-US/search?filterYear=2026&page=1')
m = re.search(r'filterYear=\d+&amp;page=(\d+)">Last', h)
print('pages', m and m.group(1))
rows = re.findall(r'(?s)<tr>(.*?)</tr>', h)
print(len(rows))
for tr in rows[:4]:
    print(tr[:900].replace('\n', ' '))
    print('----')
