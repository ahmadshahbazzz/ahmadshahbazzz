"""Draw the profile's two images, in dark and light.

hero    name, one sentence, and a band of Wi-Fi-like waves that draw in once and drift
signal  the last 12 months of GitHub contributions as seven waves, one per weekday

Usage: GITHUB_TOKEN=... python scripts/signal.py <login>   -> assets/{hero,signal}-{dark,light}.svg
Fonts (Bricolage Grotesque, OFL) are embedded so GitHub renders them exactly.
"""
import base64, json, math, os, sys, urllib.request

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "ahmadshahbazzz"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEMES = {  # matched to GitHub's own canvas so the images have no visible box
    "dark": dict(bg="#0d1117", ink="#e6edf3", mute="#7d8590", line="#e6edf3", sig="#4d8dff"),
    "light": dict(bg="#ffffff", ink="#1f2328", mute="#656d76", line="#1f2328", sig="#2f5bff"),
}


def font(name):
    b = base64.b64encode(open(os.path.join(ROOT, "fonts", name + ".woff2"), "rb").read()).decode()
    return f"@font-face{{font-family:{name};src:url(data:font/woff2;base64,{b}) format('woff2')}}"


FONTS = font("display") + font("text")
SANS = "ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"


def smooth(pts):
    """Catmull-Rom through pts, as cubic Beziers."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        d += (f" C{p1[0] + (p2[0] - p0[0]) / 6:.1f},{p1[1] + (p2[1] - p0[1]) / 6:.1f}"
              f" {p2[0] - (p3[0] - p1[0]) / 6:.1f},{p2[1] - (p3[1] - p1[1]) / 6:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return d


def hero(t):
    W, H, X0 = 1200, 300, 470  # waves start right of the name
    rows = []
    for i in range(9):
        k, amp, ph, y = 0.011 + i * 0.0013, 4 + i * 1.7, i * 0.8, 46 + i * 11
        per = 2 * math.pi / k
        pts = [(X0 + x, math.sin(x * k + ph) * amp + math.sin(x * k * 2.4 + ph * 1.6) * amp * .3)
               for x in range(0, int(W - X0 + per) + 1, 10)]
        accent = i == 6
        col, op, sw = (t["sig"], 1, 2) if accent else (t["line"], .14 + .05 * i, 1.2)
        L = int(sum(math.dist(pts[j], pts[j + 1]) for j in range(len(pts) - 1))) + 10
        rows.append(f'''<g transform="translate(0 {y})"><path d="{smooth(pts)}" fill="none" stroke="{col}" stroke-opacity="{op:.2f}" stroke-width="{sw}" stroke-dasharray="{L}" stroke-dashoffset="{L}" class="w" style="animation-delay:{.05*i:.2f}s">
<animateTransform attributeName="transform" type="translate" from="0 0" to="-{per:.1f} 0" dur="{16 + i * 1.5:.1f}s" repeatCount="indefinite"/></path></g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Ahmad. I build AI products, and I do research across fields. Lahore, Pakistan.">
<defs><linearGradient id="f" x1="{X0}" x2="{X0 + 260}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs>
<style>{FONTS}
.n{{font:150px display,{SANS};letter-spacing:-2px;fill:{t["ink"]}}}
.s{{font:30px text,{SANS};letter-spacing:-.3px;fill:{t["ink"]}}}
.p{{font:22px text,{SANS};fill:{t["mute"]}}}
.w{{animation:draw 2.4s cubic-bezier(.6,0,.2,1) forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@media (prefers-reduced-motion:reduce){{.w{{animation:none;stroke-dasharray:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{t["bg"]}"/>
<g mask="url(#m)">{"".join(rows)}</g>
<text x="-6" y="140" class="n">Ahmad</text>
<text x="0" y="214" class="s">I build AI products, and I do research across fields.</text>
<text x="0" y="262" class="p">Lahore, Pakistan</text>
</svg>'''


def fetch():
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}' % LOGIN
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def signal(total, weeks, t):
    W, H, L, R, TOP, GAP = 1200, 430, 64, 1196, 92, 34
    days = [d for w in weeks for d in w["contributionDays"]]
    ld = max((d["date"] for d in days if d["contributionCount"]), default=None)
    last = "never" if not ld else "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[int(ld[5:7]) - 1] + " " + str(int(ld[8:]))
    peak = max(d["contributionCount"] for d in days) or 1
    xs = lambda i: L + (R - L) * i / (len(weeks) - 1)
    rows = []
    for wd, name in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        base = TOP + 30 + wd * GAP
        pts = [(xs(i), base - 30 * math.sqrt(next((d["contributionCount"] for d in w["contributionDays"] if d["weekday"] == wd), 0) / peak))
               for i, w in enumerate(weeks)]
        rows.append(f'<text x="0" y="{base + 5}" class="m">{name}</text>'
                    f'<path d="{smooth(pts)}" fill="none" stroke="{t["line"]}" stroke-opacity="{.38 + .08 * wd:.2f}" stroke-width="1.4" stroke-linejoin="round"/>')
    ticks, seen = [], set()
    for i, w in enumerate(weeks):
        dt = w["contributionDays"][0]["date"]
        if dt[:7] not in seen and dt[8:] <= "07":
            seen.add(dt[:7])
            ticks.append(f'<text x="{xs(i):.0f}" y="{TOP + 30 + 6 * GAP + 36}" class="m">{"Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[int(dt[5:7]) - 1]}</text>')
    y0, y1 = TOP + 2, TOP + 30 + 6 * GAP + 12
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} GitHub contributions in the past year, drawn as seven waves, one per weekday. Last active {last}. If these lines ever go flat, consider me dead.">
<style>{FONTS}
.h{{font:24px text,{SANS};fill:{t["ink"]}}}
.m{{font:15px text,{SANS};fill:{t["mute"]}}}
.c{{font:20px text,{SANS};fill:{t["mute"]}}}
@media (prefers-reduced-motion:reduce){{.scan{{display:none}}}}
</style>
<rect width="{W}" height="{H}" fill="{t["bg"]}"/>
<text x="0" y="34" class="h">{total:,} contributions in the past year, one line per weekday.</text>
{"".join(rows)}{"".join(ticks)}
<line class="scan" x1="0" x2="0" y1="{y0}" y2="{y1}" stroke="{t["sig"]}" stroke-width="1.5">
<animateTransform attributeName="transform" type="translate" from="{L} 0" to="{R} 0" dur="9s" repeatCount="indefinite"/></line>
<text x="0" y="{H - 12}" class="c">Last active {last}. If these lines ever go flat, consider me dead.</text>
</svg>'''


if __name__ == "__main__":
    os.chdir(ROOT)
    total, weeks = fetch()
    os.makedirs("assets", exist_ok=True)
    for name, t in THEMES.items():
        open(f"assets/intro-{name}.svg", "w").write(hero(t))
        open(f"assets/signal-{name}.svg", "w").write(signal(total, weeks, t))
    print(f"{total} contributions, {len(weeks)} weeks")
