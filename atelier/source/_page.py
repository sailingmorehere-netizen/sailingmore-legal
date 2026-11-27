import re,sys,subprocess
h=subprocess.run(['curl','-sL','-m','25',sys.argv[1]],capture_output=True,text=True).stdout
h=re.sub(r'(?s)<(script|style).*?</\1>',' ',h)
t=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',h))
for m in re.finditer(r'(20(26|27)-\d\d-\d\d|\d{1,2}[./]\d{1,2}[./]20(26|27)|\d{1,2}(st|nd|rd|th)? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* 20(26|27))',t):
    print(t[max(0,m.start()-60):m.end()+60]);
print(len(t))
