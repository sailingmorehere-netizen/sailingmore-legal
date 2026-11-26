import re, subprocess
U = {
 153: 'https://segelschule-insel-reichenau.de/kurse/',
 154: 'https://segelschule-insel-reichenau.de/kurse/motorbootscheine/bodenseeschifferpatent-kat-a-motor/',
 155: 'https://segelschule-insel-reichenau.de/kurse/segelschein/bodenseeschifferpatent-kat-d-segel/',
 156: 'https://segelschule-insel-reichenau.de/kurse/grundkurs/',
 157: 'https://segelschule-insel-reichenau.de/kurse/motorbootscheine/hochrheinpatent/',
 158: 'https://segelschule-insel-reichenau.de/kurse/motorbootscheine/sportbootfuehrerschein-see/',
 152: 'https://segelschule-rehbach.de/segelkurse/',
 194: 'https://segelschule-schluchsee.de/segel-kurse-scheine/',
 292: 'https://segelschule-ueberlingen.de/ausbildung/theoriekurs-in-stuttgart/',
 380: 'https://www.windzone.es/inicio/campamentos/',
 107: 'https://ecoledecroisiereslowlife.com/stage-voile-hauturier',
 110: 'https://ecoledecroisiereslowlife.com/stage-decouverte',
 354: 'https://ventdularge.org/formation-voilier/sejours-educatifs-jeunes-en-difficultes/',
}
for i, u in U.items():
    try:
        t = subprocess.run(['curl', '-sL', '-m', '20', u], capture_output=True, text=True).stdout
    except Exception as e:
        print(i, 'ERR', e); continue
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\s+', ' ', t)
    m = [t[max(0, x.start() - 50):x.end() + 20] for x in re.finditer(r'(€\s?\d|\d\s?(€|euros?|EUR)\b)', t)][:4]
    print(i, len(t), m)
