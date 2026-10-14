"""Static about-panel SVGs (three cards). Run once: python scripts/cards.py"""
CARDS = [
    ("01", "BUILD", ["AI products,", "end to end"],
     ["LLM workflows, AI video and voice", "pipelines, full-stack web apps.", "Associate SWE @ InfiniteGoose."]),
    ("02", "RESEARCH", ["Machine learning", "&amp; AI systems"],
     ["Computer vision, security and", "sensing. First paper published", "in IEEE Access, 2026."]),
    ("03", "RECORD", ["CGPA 3.90", "1st of 40 teams"],
     ["BS Computer Science, UCP.", "Hackathon winner; 2nd at PMI", "Lahore's student competition."]),
]
THEMES = {
    "dark": dict(bg="#0d1117", card="#161b22", edge="#30363d", ink="#e6edf3", dim="#8b949e", acc="#2f6bff"),
    "light": dict(bg="#ffffff", card="#f6f8fa", edge="#d1d9e0", ink="#1f2328", dim="#59636e", acc="#2440ff"),
}


def svg(t):
    W, H, gap, pad = 1200, 330, 24, 0
    cw = (W - 2 * gap) / 3
    out = []
    for i, (num, tag, head, body) in enumerate(CARDS):
        x = i * (cw + gap)
        d = 0.15 + i * 0.18
        out.append(f'''<g class="card" style="animation-delay:{d:.2f}s">
<rect x="{x+.5}" y=".5" width="{cw-1}" height="{H-1}" rx="16" fill="{t['card']}" stroke="{t['edge']}"/>
<rect x="{x+28}" y="28" width="0" height="3" rx="1.5" fill="{t['acc']}"><animate attributeName="width" from="0" to="44" begin="{d+.3:.2f}s" dur=".8s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></rect>
<text x="{x+28}" y="62" class="tag">{num} · {tag}</text>
<text x="{x+28}" y="118" class="hd">{head[0]}</text>
<text x="{x+28}" y="156" class="hd">{head[1]}</text>
{"".join(f'<text x="{x+28}" y="{226+k*26}" class="bd">{line}</text>' for k, line in enumerate(body))}
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Build: AI products end to end. Research: machine learning and AI systems, published in IEEE Access. Record: CGPA 3.90, hackathon winner.">
<style>
.tag{{font:500 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:2px;fill:{t['dim']}}}
.hd{{font:700 32px ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;letter-spacing:-1.2px;fill:{t['ink']}}}
.bd{{font:400 16.5px ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{t['dim']}}}
.card{{opacity:0;animation:up .9s cubic-bezier(.2,.8,.2,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.card{{animation:none;opacity:1}}}}
</style>
{"".join(out)}
</svg>'''


for name, t in THEMES.items():
    open(f"assets/about-{name}.svg", "w").write(svg(t))
