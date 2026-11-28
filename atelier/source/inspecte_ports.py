# © 2026 Sailing More — tous droits réservés. All rights reserved.
import sqlite3
c = sqlite3.connect('projets/sailingmore/ports.sqlite')
print(c.execute("select * from releves").fetchall())
