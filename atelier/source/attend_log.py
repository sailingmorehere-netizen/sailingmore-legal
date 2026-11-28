# © 2026 Sailing More — tous droits réservés. All rights reserved.
import time, sys
t = time.time()
while time.time() - t < 570:
    s = open('/tmp/m2s.log').read()
    if 'remplis' in s or 'Traceback' in s:
        break
    time.sleep(15)
print(s[-300:])
