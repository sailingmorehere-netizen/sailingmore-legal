# © 2026 Sailing More — tous droits réservés. All rights reserved.
import sqlite3
c=sqlite3.connect('projets/sailingmore/ports.sqlite')
for r in c.execute("select name,sql from sqlite_master"): print(r[0], (r[1] or '')[:300])
print(c.execute("select pays,count(*) from ports group by pays").fetchall())
print(c.execute("select * from ports limit 2").fetchall())
