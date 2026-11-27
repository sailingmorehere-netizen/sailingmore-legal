import py_compile, os
for root, d, files in os.walk('.'):
    if '/.' in root or 'node_modules' in root:
        continue
    for n in files:
        if n.endswith('.py'):
            f = os.path.join(root, n)
            try:
                py_compile.compile(f, doraise=True, cfile='/tmp/_x.pyc')
            except Exception as e:
                print(f, str(e)[:300])
print('fini')
