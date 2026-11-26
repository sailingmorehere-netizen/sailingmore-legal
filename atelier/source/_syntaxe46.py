import ast, sys
for f in ["scripts/stages_page.py", "scripts/regates_page.py", "scripts/_generer_ports.py", "scripts/carte_epreuves.py"]:
    try:
        ast.parse(open(f, encoding="utf-8").read())
        print("ok", f)
    except SyntaxError as e:
        print("ERREUR", f, e)
