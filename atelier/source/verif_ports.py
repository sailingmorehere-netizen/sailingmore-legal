# © 2026 Sailing More — tous droits réservés. All rights reserved.
import sqlite3, os, sys
c = sqlite3.connect('projets/sailingmore/ports.sqlite')
n = c.execute('select count(*) from ports').fetchone()[0]
p = c.execute('select count(distinct pays) from ports').fetchone()[0]
f = 'projets/sailingmore/site/ports.html'
h = os.path.getsize(f) if os.path.exists(f) else 0
print(n, p, h)
sys.exit(0 if n >= 500 and p >= 20 and h > 20000 else 1)
