import re, urllib.request, html
U = """https://7seassailing.com/all-courses/rya-motor-cruising/rya-day-skipper-motor/
https://7seassailing.com/all-courses/rya-motor-cruising/rya-coastal-skipper-motor/
https://7seassailing.com/all-courses/rya-pwc-jet-ski-courses/rya-pwc-instructor-course/
https://www.solentboattraining.co.uk/rya-powerboat-courses/powerboat-instructor-skills-assessment
https://www.solentboattraining.co.uk/rya-powerboat-courses/rya-powerboat-instructor-course
https://www.solentboattraining.co.uk/rya-cruising-courses/coastal-skipper-practical
https://www.solentboattraining.co.uk/rya-cruising-courses/sbt-yachtmaster-coastal-coc-prep-for-motor
https://www.solentboattraining.co.uk/rya-cruising-courses/sbt-yachtmaster-offshore-coc-prep-for-motor
https://www.uksa.org/course/rya-powerboat-instructor/
https://www.solentboattraining.co.uk/rya-cruising-courses/day-skipper-practical""".split()
KEY = re.compile(r"prerequisite|pre-requisite|requirement|entry|experience|suitable|who is|should (have|hold)|must (have|hold)|minimum|beginner|aimed|level", re.I)
for u in U:
    print("=====", u)
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=25)
        h = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("ERREUR", e)
        continue
    h = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", h)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", h))
    lines = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
    lines = [l for l in lines if len(l) > 25]
    n = 0
    for l in lines:
        if KEY.search(l) and n < 12:
            print("-", l[:400])
            n += 1
