"""Draw the last year of GitHub contributions as seven Wi-Fi subcarriers (one per weekday).

Usage: GITHUB_TOKEN=... python scripts/signal.py <login>   -> writes assets/signal-{dark,light}.svg
"""
import json, math, os, sys, urllib.request
from datetime import date

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "ahmadshahbazzz"
Q = """{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions
weeks{contributionDays{date contributionCount weekday}}}}}}""" % LOGIN


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": Q}).encode(),
                                 {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return cal["totalContributions"], cal["weeks"], days


def smooth(pts):
    """Catmull-Rom through pts -> cubic Bezier path."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def render(total, weeks, days, theme):
    bg, ink, dim, line, acc = {
        "dark": ("#0d1117", "#e6edf3", "#8b949e", "#e6edf3", "#2f6bff"),
        "light": ("#ffffff", "#1f2328", "#59636e", "#1f2328", "#2440ff"),
    }[theme]
    W, H, L, R, TOP = 1200, 340, 112, 1150, 92
    peak = max(d["contributionCount"] for d in days) or 1
    xs = lambda i: L + (R - L) * i / (len(weeks) - 1)
    rows = []
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for wd in range(7):
        base = TOP + 24 + wd * 30
        pts = []
        for i, w in enumerate(weeks):
            c = next((d["contributionCount"] for d in w["contributionDays"] if d["weekday"] == wd), 0)
            pts.append((xs(i), base - 28 * math.sqrt(c / peak)))
        op = 0.35 + 0.09 * wd
        rows.append(f'<text x="{L-18}" y="{base+4}" text-anchor="end" class="s">{names[wd]}</text>'
                    f'<path d="{smooth(pts)}" fill="none" stroke="{line}" stroke-opacity="{op:.2f}" stroke-width="1.5" stroke-linejoin="round"/>')
    # month ticks
    ticks, seen = [], set()
    for i, w in enumerate(weeks):
        m = w["contributionDays"][0]["date"][:7]
        if m not in seen and w["contributionDays"][0]["date"][8:] <= "07":
            seen.add(m)
            ticks.append(f'<text x="{xs(i):.0f}" y="{H-22}" class="s">{date.fromisoformat(m+"-01").strftime("%b").lower()}</text>')
    best = max(days, key=lambda d: d["contributionCount"])
    active = sum(1 for d in days if d["contributionCount"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} contributions in the last year, drawn as seven signal lines, one per weekday">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{acc}" stop-opacity="0"/><stop offset="1" stop-color="{acc}" stop-opacity=".22"/></linearGradient>
<clipPath id="k"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<style>
.h{{font:600 15px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:1.6px;fill:{ink}}}
.s{{font:400 12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{dim}}}
.b{{font:700 30px ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;letter-spacing:-1px;fill:{ink}}}
@media (prefers-reduced-motion:reduce){{.scan{{display:none}}}}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{bg}"/>
<text x="{L}" y="44" class="h">THE LAST 12 MONTHS, AS SIGNAL</text>
<text x="{L}" y="66" class="s">one line per weekday · amplitude = contributions</text>
<text x="{R}" y="48" text-anchor="end" class="b">{total:,}</text>
<text x="{R}" y="68" text-anchor="end" class="s">contributions · {active} active days · peak {best["contributionCount"]}</text>
{"".join(rows)}
{"".join(ticks)}
<g clip-path="url(#k)" class="scan"><g><rect x="-48" y="{TOP-8}" width="48" height="{7*30+20}" fill="url(#g)"/><rect x="0" y="{TOP-8}" width="1.5" height="{7*30+20}" fill="{acc}" opacity=".8"/>
<animateTransform attributeName="transform" type="translate" from="{L} 0" to="{R} 0" dur="7s" repeatCount="indefinite"/></g></g>
</svg>'''


if __name__ == "__main__":
    total, weeks, days = fetch()
    os.makedirs("assets", exist_ok=True)
    for t in ("dark", "light"):
        open(f"assets/signal-{t}.svg", "w").write(render(total, weeks, days, t))
    print(f"{total} contributions, {len(weeks)} weeks")
