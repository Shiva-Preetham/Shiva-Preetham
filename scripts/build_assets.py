#!/usr/bin/env python3
"""Builds the animated SVGs used by the profile README.

Edit the data in this file (phrases, highlight tiles, project cards) and run:

    python scripts/build_assets.py

Everything is written to ./assets. No third-party packages needed.
"""
from html import escape
from math import cos, radians, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ---------------------------------------------------------------- palette --
BG0, BG1 = "#0A0E1A", "#141A35"
PANEL = "#0F1424"
INK, MUTED, FAINT, LINE = "#E6EDF3", "#8B98B0", "#5B6B8C", "#1F2A44"
TEAL, VIOLET, PINK, AMBER = "#2DD4BF", "#A78BFA", "#F472B6", "#FBBF24"
SKY, GREEN, RED = "#38BDF8", "#4ADE80", "#F87171"

SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, 'SFMono-Regular', Menlo, monospace"


def css(extra: str = "") -> str:
    return f"""<style>
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.b{{font-weight:700}}
.rise{{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
.flow{{stroke-dasharray:4 8;animation:dash 1.8s linear infinite}}
@keyframes dash{{to{{stroke-dashoffset:-48}}}}
.blink{{animation:blink 1.05s steps(1) infinite}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes draw{{0%{{stroke-dashoffset:var(--len)}}35%,85%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:var(--len)}}}}
{extra}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def card(w, h, rx, glows, blur=60):
    """Dark rounded card with a dot grid and soft colour glows."""
    g = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{o}" filter="url(#blur)"/>'
        for cx, cy, r, c, o in glows
    )
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#24304D"/></pattern>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{blur}"/></filter>
<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
</defs>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect width="{w}" height="{h}" fill="url(#dots)" opacity=".55"/>
{g}
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{rx}" fill="none" stroke="{LINE}" stroke-width="1.5"/>"""


def svg(w, h, body, title, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'
        f"{css(extra_css)}\n{body}\n</svg>\n"
    )


def t(x, y, text, size, fill, cls="sans", anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{escape(text)}</text>'
    )


def keyframes(times, values, total):
    """Collapse duplicate leading times and format SMIL keyTimes/values."""
    pairs = []
    for tm, v in zip(times, values):
        if pairs and abs(pairs[-1][0] - tm) < 1e-9:
            pairs[-1] = (tm, v)
        else:
            pairs.append((tm, v))
    kt = ";".join(f"{tm / total:.4f}" for tm, _ in pairs)
    vs = ";".join(f"{v:.1f}" for _, v in pairs)
    return kt, vs


# ================================================================= header ==
PHRASES = [
    "building explainable ML that tells you why",
    "shipping multimodal LLM pipelines with guardrails",
    "models gather evidence, code makes the call",
    "hackathons: Meta · PayPal · HackerRank · WeMakeDevs",
]


def header():
    W, H = 1200, 400
    body = [card(W, H, 24, [(1060, 40, 200, VIOLET, 0.20), (120, 420, 220, TEAL, 0.13), (720, -40, 140, PINK, 0.10)])]

    # left column -----------------------------------------------------------
    body.append(
        f'<text x="64" y="92" class="mono rise" font-size="17" fill="{TEAL}">~/shiva-preetham'
        f'<tspan fill="{FAINT}"> $ </tspan><tspan fill="{INK}">whoami</tspan></text>'
    )
    body.append(t(60, 172, "Shiva Preetham", 66, INK, "sans b rise", extra='style="animation-delay:.1s"'))
    body.append(t(60, 244, "Chelimila", 66, "url(#accent)", "sans b rise", extra='style="animation-delay:.2s"'))
    body.append(
        t(64, 292, "AI/ML Engineer  ·  B.Tech CSE @ JIIT Noida  ·  Class of 2028", 21, MUTED,
          "sans rise", extra='style="animation-delay:.3s"')
    )

    # typing line -------------------------------------------------------------
    fs, cw, x0, y = 19, 11.4, 92, 348
    period = 4.6
    total = period * len(PHRASES)
    body.append(t(64, y, ">", fs, TEAL, "mono b"))
    clips, texts = [], []
    cur_t, cur_v = [0.0], [x0]
    for i, p in enumerate(PHRASES):
        w = len(p) * cw
        s = i * period
        typed = s + min(2.3, 0.05 * len(p))
        hold = s + period - 0.45
        gone = s + period - 0.15
        kt, vs = keyframes([0, s, typed, hold, gone, total], [0, 0, w, w, 0, 0], total)
        clips.append(
            f'<clipPath id="type{i}"><rect x="{x0}" y="{y - 22}" height="32" width="0">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{vs}"/></rect></clipPath>'
        )
        texts.append(
            f'<text x="{x0}" y="{y}" class="mono" font-size="{fs}" fill="{INK}" textLength="{w:.1f}" '
            f'lengthAdjust="spacing" clip-path="url(#type{i})">{escape(p)}</text>'
        )
        cur_t += [s, typed, hold, gone]
        cur_v += [x0, x0 + w + 3, x0 + w + 3, x0]
    cur_t.append(total)
    cur_v.append(x0)
    kt, vs = keyframes(cur_t, cur_v, total)
    body.append("<defs>" + "".join(clips) + "</defs>")
    body += texts
    body.append(
        f'<rect y="{y - 17}" width="10" height="22" rx="1.5" fill="{TEAL}" class="blink">'
        f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{vs}"/></rect>'
    )

    # right column: how I build ----------------------------------------------
    body.append(t(770, 104, "// how I build", 13, FAINT, "mono"))
    inputs = [("image", 150, TEAL), ("text", 210, VIOLET), ("data", 270, PINK)]
    mx, my, mr = 930, 210, 38
    edges, dots = [], []
    for i, (label, cy, col) in enumerate(inputs):
        d = f"M854 {cy} C 880 {cy}, 866 {my}, {mx - mr} {my}"
        edges.append(f'<path d="{d}" fill="none" stroke="#3B4A6B" stroke-width="1.6" class="flow"/>')
        dots.append(
            f'<circle r="4.5" fill="{col}"><animateMotion dur="3.3s" begin="-{i * 1.1:.1f}s" '
            f'repeatCount="indefinite" path="{d} L 1092 {my}"/></circle>'
        )
    edges.append(f'<path d="M{mx + mr} {my} L1000 {my}" stroke="#3B4A6B" stroke-width="1.6" class="flow"/>')
    edges.append(f'<path d="M1070 {my} L1092 {my}" stroke="#3B4A6B" stroke-width="1.6" class="flow"/>')
    body += edges + dots
    for label, cy, col in inputs:
        body.append(
            f'<rect x="770" y="{cy - 15}" width="84" height="30" rx="15" fill="{PANEL}" stroke="{col}" stroke-opacity=".55"/>'
        )
        body.append(t(812, cy + 4.5, label, 13, INK, "mono", "middle"))
    body.append(
        f'<circle cx="{mx}" cy="{my}" r="{mr + 9}" fill="none" stroke="{VIOLET}" stroke-opacity=".45" '
        f'stroke-dasharray="2 7" style="transform-origin:{mx}px {my}px;animation:spin 14s linear infinite"/>'
    )
    body.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{PANEL}" stroke="url(#accent)" stroke-width="2.2"/>')
    body.append(t(mx, my + 4.5, "model", 13, INK, "mono", "middle"))
    body.append(f'<rect x="1000" y="184" width="70" height="52" rx="12" fill="{PANEL}" stroke="{AMBER}" stroke-opacity=".8" stroke-width="1.6"/>')
    body.append(t(1035, my + 4.5, "rules", 13, INK, "mono", "middle"))
    body.append(f'<circle cx="1120" cy="{my}" r="28" fill="{PANEL}" stroke="{GREEN}" stroke-width="2"/>')
    body.append(
        f'<path d="M1107 {my + 1} l9 9 l15 -17" fill="none" stroke="{GREEN}" stroke-width="3.5" '
        f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="40" '
        f'style="--len:40;animation:draw 3.3s ease-in-out infinite"/>'
    )
    for x, label in [(mx, "describes"), (1035, "decides"), (1120, "ships")]:
        body.append(t(x, 284, label, 12, MUTED, "mono", "middle"))
    return svg(W, H, "\n".join(body), "Shiva Preetham Chelimila: AI/ML engineer building explainable ML and multimodal LLM systems")


# ============================================================= highlights ==
HIGHLIGHTS = [
    ("#1", "Rank in admission", "counselling at JIIT", "JIIT · 2024", TEAL),
    ("Top 13%", "HackerRank Orchestrate", "rank 227 of 1,773", "JUN 2026", VIOLET),
    ("200+", "DSA problems solved", "on LeetCode", "C++", AMBER),
    ("98.3%", "Class XII overall", "with 100% in PCM", "TSBIE", PINK),
]


def highlights():
    W, H, gap = 1200, 190, 20
    tw, th = (W - gap * 3) / 4, 170
    defs = ["<defs>", f'<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>']
    body = []
    for i, (val, l1, l2, tag, col) in enumerate(HIGHLIGHTS):
        x = i * (tw + gap)
        defs.append(f'<clipPath id="tile{i}"><rect x="{x:.1f}" y="10" width="{tw:.1f}" height="{th}" rx="18"/></clipPath>')
        defs.append(
            f'<linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/>'
            f'<stop offset="1" stop-color="{BG1}"/></linearGradient>'
        )
        g = [f'<g class="rise" style="animation-delay:{i * 0.12:.2f}s">']
        g.append(f'<g clip-path="url(#tile{i})"><rect x="{x:.1f}" y="10" width="{tw:.1f}" height="{th}" fill="url(#g{i})"/>')
        g.append(f'<circle cx="{x + tw - 20:.1f}" cy="20" r="80" fill="{col}" opacity=".16" filter="url(#blur)"/></g>')
        g.append(f'<rect x="{x + .75:.1f}" y="10.75" width="{tw - 1.5:.1f}" height="{th - 1.5}" rx="18" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
        g.append(f'<rect x="{x + 26:.1f}" y="38" width="34" height="4" rx="2" fill="{col}"/>')
        g.append(t(f"{x + tw - 24:.1f}", 46, tag, 12, FAINT, "mono", "end"))
        g.append(t(f"{x + 24:.1f}", 104, val, 46, col, "sans b"))
        g.append(t(f"{x + 26:.1f}", 136, l1, 16, INK, "sans"))
        g.append(t(f"{x + 26:.1f}", 158, l2, 16, MUTED, "sans"))
        g.append("</g>")
        body += g
    defs.append("</defs>")
    return svg(W, H, "\n".join(defs + body), "Highlights: rank 1 in JIIT admission counselling, top 13% in HackerRank Orchestrate, 200+ LeetCode problems, 98.3% in Class XII")


# =========================================================== project art ==
def motif_churn():
    base, scale = 252, 170
    out = [f'<line x1="404" y1="{base}" x2="578" y2="{base}" stroke="{LINE}" stroke-width="1.5"/>']
    hi = base - 0.7 * scale
    out.append(f'<line x1="404" y1="{hi:.0f}" x2="578" y2="{hi:.0f}" stroke="{RED}" stroke-opacity=".5" stroke-dasharray="4 5"/>')
    out.append(t(578, hi - 6, "HIGH RISK", 10, RED, "mono", "end", 'fill-opacity=".8"'))
    bars = [(412, 52), (446, 88), (480, 128), (514, 70)]
    for x, h in bars:
        col = GREEN if h < 68 else AMBER if h < 119 else RED
        out.append(f'<rect x="{x}" y="{base - h}" width="22" height="{h}" rx="4" fill="{col}" fill-opacity=".85"/>')
    kt = "0;.25;.45;.85;1"
    out.append(
        f'<rect x="548" width="22" rx="4" fill-opacity=".9" y="{base - 150}" height="150" fill="{RED}">'
        f'<animate attributeName="height" values="150;150;50;50;150" keyTimes="{kt}" dur="5s" repeatCount="indefinite"/>'
        f'<animate attributeName="y" values="{base - 150};{base - 150};{base - 50};{base - 50};{base - 150}" keyTimes="{kt}" dur="5s" repeatCount="indefinite"/>'
        f'<animate attributeName="fill" values="{RED};{RED};{GREEN};{GREEN};{RED}" keyTimes="{kt}" dur="5s" repeatCount="indefinite"/></rect>'
    )
    out.append(t(491, 274, "act → re-score", 11, MUTED, "mono", "middle"))
    return "\n".join(out)


def motif_malaria():
    cx, cy, r = 488, 162, 74
    px, py = 512, 140
    return "\n".join([
        f'<defs><clipPath id="cell"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PINK}" fill-opacity=".08" stroke="{PINK}" stroke-opacity=".6" stroke-width="2"/>',
        f'<circle cx="{cx - 6}" cy="{cy + 6}" r="46" fill="none" stroke="{PINK}" stroke-opacity=".16" stroke-width="10"/>',
        f'<circle cx="{px}" cy="{py}" r="10" fill="#8B5CF6"/>',
        f'<circle cx="{px + 9}" cy="{py - 6}" r="4" fill="#C4B5FD"/>',
        f'<circle cx="{px}" cy="{py}" r="12" fill="none" stroke="{PINK}" stroke-width="2">'
        f'<animate attributeName="r" values="12;32" dur="1.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>',
        f'<path d="M{px - 20} {py - 10} v-10 h10 M{px + 10} {py - 20} h10 v10 M{px + 20} {py + 10} v10 h-10 M{px - 10} {py + 20} h-10 v-10" '
        f'fill="none" stroke="{INK}" stroke-opacity=".8" stroke-width="2"/>',
        f'<g clip-path="url(#cell)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="2.5" fill="{PINK}" opacity=".85">'
        f'<animate attributeName="y" values="{cy - r};{cy + r};{cy - r}" dur="3.6s" repeatCount="indefinite"/></rect></g>',
        t(cx, 264, "parasitized", 11, PINK, "mono", "middle"),
    ])


def motif_claim():
    shield = "M488 96 L538 113 V158 C538 196 517 220 488 234 C459 220 438 196 438 158 V113 Z"
    return "\n".join([
        f'<defs><clipPath id="shield"><path d="{shield}"/></clipPath></defs>',
        f'<rect x="414" y="58" width="58" height="22" rx="11" fill="{VIOLET}" fill-opacity=".1" stroke="{VIOLET}" stroke-opacity=".55"/>',
        t(443, 73, "pass 1", 11, INK, "mono", "middle"),
        f'<path d="M474 69 L502 69" stroke="#3B4A6B" stroke-width="1.6" class="flow"/>',
        f'<rect x="504" y="58" width="58" height="22" rx="11" fill="{VIOLET}" fill-opacity=".1" stroke="{VIOLET}" stroke-opacity=".55"/>',
        t(533, 73, "pass 2", 11, INK, "mono", "middle"),
        f'<path d="{shield}" fill="{VIOLET}" fill-opacity=".09" stroke="{VIOLET}" stroke-width="2.2"/>',
        f'<g clip-path="url(#shield)"><rect x="430" y="96" width="120" height="2.5" fill="{VIOLET}" opacity=".8">'
        f'<animate attributeName="y" values="96;234;96" dur="3.4s" repeatCount="indefinite"/></rect></g>',
        f'<path d="M466 163 l15 15 l30 -32" fill="none" stroke="{GREEN}" stroke-width="5" stroke-linecap="round" '
        f'stroke-linejoin="round" stroke-dasharray="70" style="--len:70;animation:draw 3.4s ease-in-out infinite"/>',
        t(488, 264, "supported", 11, GREEN, "mono", "middle"),
    ])


def motif_market():
    out = [f'<line x1="404" y1="{y}" x2="578" y2="{y}" stroke="{LINE}" stroke-width="1"/>' for y in (96, 136, 176, 216, 256)]
    candles = [(414, 228, 212, 236, 206), (438, 212, 220, 226, 204), (462, 218, 198, 224, 192),
               (486, 196, 180, 204, 172), (510, 182, 188, 194, 170), (534, 186, 150, 192, 142), (558, 152, 124, 158, 114)]
    for x, o, c, lo, hi in candles:
        col = GREEN if c < o else RED
        out.append(f'<line x1="{x}" y1="{hi}" x2="{x}" y2="{lo}" stroke="{col}" stroke-opacity=".7" stroke-width="1.5"/>')
        out.append(f'<rect x="{x - 5}" y="{min(o, c)}" width="10" height="{max(abs(o - c), 3)}" rx="1.5" fill="{col}" fill-opacity=".75"/>')
    pts = [(414, 214), (438, 214), (462, 200), (486, 184), (510, 182), (534, 156), (558, 124)]
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    out.append(
        f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" '
        f'stroke-dasharray="260" style="--len:260;animation:draw 4.5s ease-in-out infinite"/>'
    )
    out.append(f'<circle cx="558" cy="124" r="5" fill="{AMBER}" class="pulse"/>')
    out.append(f'<path d="M572 102 l-6 9 h12 z" fill="{GREEN}"/>')
    out.append(t(491, 278, "45+ features → 5-day call", 11, MUTED, "mono", "middle"))
    return "\n".join(out)


def motif_saveflow():
    cx, cy, r = 488, 160, 66
    circ = 2 * 3.14159 * r
    dash = 300
    a = radians(dash / r * 180 / 3.14159)
    ex, ey = cx + r * cos(a), cy + r * sin(a)
    tx, ty = -sin(a), cos(a)
    nx, ny = cos(a), sin(a)
    tip = (ex + 11 * tx, ey + 11 * ty)
    b1 = (ex + 7 * nx, ey + 7 * ny)
    b2 = (ex - 7 * nx, ey - 7 * ny)
    arrow = f"M{tip[0]:.1f} {tip[1]:.1f} L{b1[0]:.1f} {b1[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f} Z"
    return "\n".join([
        f'<g style="transform-origin:{cx}px {cy}px;animation:spin 7s linear infinite">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SKY}" stroke-width="3.5" stroke-linecap="round" '
        f'stroke-dasharray="{dash} {circ - dash:.1f}"/><path d="{arrow}" fill="{SKY}"/></g>',
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="{SKY}" fill-opacity=".08" stroke="{SKY}" stroke-opacity=".35"/>',
        f'<rect x="{cx - 15}" y="{cy - 18}" width="10" height="36" rx="3" fill="{SKY}"/>',
        f'<rect x="{cx + 5}" y="{cy - 18}" width="10" height="36" rx="3" fill="{SKY}"/>',
        f'<text x="{cx}" y="264" class="mono" font-size="11" text-anchor="middle" fill="{FAINT}">'
        f'<tspan text-decoration="line-through">cancel</tspan><tspan fill="{SKY}"> → saved</tspan></text>',
    ])


def motif_ship():
    nodes = {"sup": (432, 104), "fix": (544, 104), "rev": (488, 188)}
    tri = "M432 104 L544 104 L488 188 Z"
    out = [f'<path d="{tri}" fill="none" stroke="#3B4A6B" stroke-width="1.6" class="flow"/>']
    for i, col in enumerate((GREEN, TEAL)):
        out.append(f'<circle r="4.5" fill="{col}"><animateMotion dur="4.2s" begin="-{i * 2.1:.1f}s" repeatCount="indefinite" path="{tri}"/></circle>')
    for name, (x, y) in nodes.items():
        out.append(f'<circle cx="{x}" cy="{y}" r="23" fill="{PANEL}" stroke="{GREEN}" stroke-width="2"/>')
        out.append(t(x, y + 4, name, 12, INK, "mono", "middle"))
    for gx, label in ((440, "merge"), (536, "reply")):
        out.append(f'<path d="M488 211 L{gx} 236" stroke="{AMBER}" stroke-opacity=".5" stroke-dasharray="3 4"/>')
        out.append(f'<circle cx="{gx}" cy="238" r="5.5" fill="{AMBER}"/>')
        out.append(f'<path d="M{gx - 9} 258 a9 9 0 0 1 18 0" fill="none" stroke="{AMBER}" stroke-width="2.5" stroke-linecap="round"/>')
        out.append(t(gx, 276, f"{label} ok", 10, AMBER, "mono", "middle"))
    return "\n".join(out)


PROJECTS = [
    dict(slug="churnsense", title="ChurnSense", tag="LIVE · AGILE PBL", col=TEAL,
         sub=["Explainable churn prediction that says", "who may leave, why, and what to do next."],
         stats=[("142", "TESTS · TDD · CI"), ("SHAP", "REASON PER SCORE")], motif=motif_churn),
    dict(slug="malariavision", title="MalariaVision", tag="LIVE · IPCV PBL", col=PINK,
         sub=["Spots malaria parasites in blood-smear", "cells: OpenCV pipeline + MobileNetV2."],
         stats=[("96.3%", "ACCURACY"), ("95.1%", "RECALL · 900 UNSEEN")], motif=motif_malaria),
    dict(slug="claim-verifier", title="Claim Verifier", tag="HACKERRANK ORCHESTRATE", col=VIOLET,
         sub=["Two-pass Gemini vision pipeline that", "judges damage claims from photo evidence."],
         stats=[("20/20", "CLAIM STATUS"), ("~$0.02", "45 CLAIMS · <13 MIN")], motif=motif_claim),
    dict(slug="marketlens", title="MarketLens", tag="LIVE · FULL STACK", col=AMBER,
         sub=["NSE/BSE direction forecasts with SHAP", "drivers, news sentiment and portfolios."],
         stats=[("RF+XGB", "ENSEMBLE PER STOCK"), ("45+", "INDICATORS")], motif=motif_market),
    dict(slug="saveflow", title="SaveFlow", tag="PAYPAL AI HACKATHON", col=SKY,
         sub=["Agent that rescues cancelling PayPal", "subscribers, with guardrails in code."],
         stats=[("0", "POLICY VIOLATIONS"), ("10/10", "INJECTIONS CAUGHT")], motif=motif_saveflow),
    dict(slug="support-to-ship", title="Support-to-Ship", tag="FLIP THE SWITCH HACKATHON", col=GREEN,
         sub=["Customer ticket in, reviewed fix merged,", "customer answered. 3 agents, 2 humans."],
         stats=[("3", "AI AGENTS"), ("2", "HUMAN APPROVALS")], motif=motif_ship),
]


def project(p):
    W, H = 600, 300
    col = p["col"]
    body = [card(W, H, 20, [(540, 30, 150, col, 0.22), (80, 330, 120, VIOLET, 0.10)], blur=50)]
    tw = len(p["tag"]) * 7.6 + 26
    body.append(f'<rect x="28" y="26" width="{tw:.0f}" height="26" rx="13" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".5"/>')
    body.append(t(41, 43.5, p["tag"], 12, col, "mono b", extra='letter-spacing=".6"'))
    body.append(t(28, 104, p["title"], 38, INK, "sans b"))
    for i, line in enumerate(p["sub"]):
        body.append(t(29, 138 + i * 24, line, 17.5, MUTED, "sans"))
    for i, (val, label) in enumerate(p["stats"]):
        x = 29 + i * 172
        body.append(t(x, 234, val, 32, col, "sans b"))
        body.append(t(x + 1, 258, label, 12, "#71809E", "mono", extra='letter-spacing=".3"'))
    body.append(p["motif"]())
    return svg(W, H, "\n".join(body), f"{p['title']}: {' '.join(p['sub'])}")


# ================================================================= footer ==
def footer():
    W, H = 1200, 150
    body = [card(W, H, 22, [(600, 200, 260, VIOLET, 0.18)], blur=60)]

    def wave(y, amp, length):
        d = f"M0 {y}"
        for i in range(int(2 * W / length) + 1):
            x = i * length
            d += f" Q {x + length / 4} {y - amp} {x + length / 2} {y} T {x + length} {y}"
        return d + f" V {H} H 0 Z"

    body.append(f'<g clip-path="url(#frame)">')
    body.append(f'<path d="{wave(118, 14, 300)}" fill="url(#accent)" opacity=".22" style="animation:slide 9s linear infinite"/>')
    body.append(f'<path d="{wave(128, 10, 240)}" fill="url(#accent)" opacity=".16" style="animation:slide2 14s linear infinite"/>')
    body.append("</g>")
    body.append(t(600, 64, "Thanks for stopping by!", 26, INK, "sans b", "middle"))
    body.append(t(600, 96, "Let's build AI that shows its work.", 16, MUTED, "mono", "middle"))
    extra = "@keyframes slide{to{transform:translateX(-600px)}}@keyframes slide2{from{transform:translateX(-480px)}to{transform:translateX(0)}}"
    return svg(W, H, "\n".join(body), "Thanks for stopping by. Let's build AI that shows its work.", extra)


def main():
    (OUT / "projects").mkdir(parents=True, exist_ok=True)
    files = {OUT / "header.svg": header(), OUT / "highlights.svg": highlights(), OUT / "footer.svg": footer()}
    for p in PROJECTS:
        files[OUT / "projects" / f"{p['slug']}.svg"] = project(p)
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
